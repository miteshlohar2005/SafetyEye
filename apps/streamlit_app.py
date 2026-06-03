import streamlit as st
import cv2
from ultralytics import YOLO
import tempfile
from PIL import Image
import numpy as np
import math
import os
import time
import threading
from datetime import datetime
import time
import threading
import winsound
from datetime import datetime
import pandas as pd
try:
    import plotly.express as px
except ImportError:
    px = None

import requests
from streamlit_lottie import st_lottie

# Import Utils
try:
    from utils import db, email_sender, face_rec, detection_engine
except ImportError:
    # Handle running from different context
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from utils import db, email_sender, face_rec, detection_engine

# Initialize DB
db.init_db()

# Set Page Config
st.set_page_config(
    page_title="SafetyEye Pro",
    page_icon="👷",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load Animation
lottie_safety = load_lottieurl("https://lottie.host/962f3b79-5e7e-4091-87e3-085e64032483/9rT6aQyZJ5.json")

# Initialize Session State
if "webcam_active" not in st.session_state:
    st.session_state.webcam_active = False

# Constants
DANGER_CLASSES = ['no-helmet', 'no-vest', 'no-goggles', 'no-gloves', 'no-boots']

# --- SIDEBAR CONFIG ---
st.sidebar.title("Configuration")
if lottie_safety:
    with st.sidebar:
        st_lottie(lottie_safety, height=150, key="safety_anim")
else:
    st.sidebar.image("https://img.icons8.com/color/96/000000/industrial-helmet.png", width=70)

theme = st.sidebar.radio("Theme", ["Dark", "Light"], index=0)

# Custom CSS
if theme == "Dark":
    st.markdown("""
    <style>
        /* Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Inter:wght@300;400;600&display=swap');
        
        /* Global Settings */
        [data-testid="stAppViewContainer"] { 
            background-color: #0e1117; 
            background-image: radial-gradient(#1c1e24 20%, transparent 20%), radial-gradient(#1c1e24 20%, transparent 20%);
            background-position: 0 0, 50px 50px;
            background-size: 100px 100px;
            font-family: 'Inter', sans-serif;
        }
        [data-testid="stSidebar"] { background-color: #000000; border-right: 1px solid #333; }
        
        /* Metric Card / Glassmorphism */
        div[data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            color: #ffffff;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        div[data-testid="metric-container"]:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(100, 200, 255, 0.4);
            box-shadow: 0 0 15px rgba(100, 200, 255, 0.2);
        }
        
        /* Typography */
        h1, h2, h3 { font-family: 'Orbitron', sans-serif; letter-spacing: 1px; color: #fff; text-shadow: 0 0 10px rgba(0,0,0,0.5); }
        p, label, span, div { font-family: 'Inter', sans-serif; color: #e0e0e0 !important; }
        
        /* Buttons */
        .stButton>button { 
            border-radius: 4px; 
            height: 3em; 
            background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%); 
            color: #000 !important; 
            border: none;
            font-weight: 700;
            font-family: 'Orbitron', sans-serif;
            text-transform: uppercase;
            transition: all 0.3s ease;
            letter-spacing: 1px;
        }
        .stButton>button:hover { 
            box-shadow: 0 0 20px rgba(0, 201, 255, 0.6);
            transform: scale(1.02);
            color: #fff !important;
        }
    </style>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background-color: #ffffff; color: #000000; }
        [data-testid="stSidebar"] { background-color: #f0f2f6; color: black; }
        
        /* Smooth Animation for Buttons */
        .stButton>button { 
            width: 100%; 
            border-radius: 8px; 
            height: 3.5em; 
            background: linear-gradient(90deg, #FF4B4B 0%, #FF6B6B 100%); 
            color: white !important; 
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
         .stButton>button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(255, 75, 75, 0.3);
        }
    </style>""", unsafe_allow_html=True)

# Tabs in Sidebar for Settings
settings_tab1, settings_tab2 = st.sidebar.tabs(["⚙️ General", "📧 Email"])

with settings_tab1:
    confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.4, 0.05)
    enable_face_rec = st.checkbox("Enable Face Recognition", value=False)
    enable_audio = st.checkbox("Enable Audio Alerts", value=True)

with settings_tab2:
    enable_email = st.checkbox("Enable Email Alerts", value=False)
    sender_email = st.text_input("Sender Email (Gmail)")
    sender_password = st.text_input("App Password", type="password")
    receiver_email = st.text_input("Receiver Email")
    
    email_config = {
        'email_enabled': enable_email,
        'sender_email': sender_email,
        'sender_password': sender_password,
        'receiver_email': receiver_email
    }

# Load Model
@st.cache_resource
def load_model():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "..", "models", "best.pt")
    if not os.path.exists(model_path):
        return YOLO("yolov8n.pt")
    try:
        return YOLO(model_path)
    except:
        return YOLO("yolov8n.pt")

model = load_model()

# --- HELPER: PROCESS FRAME ---
def process_frame(frame, conf_thresh, draw_pd=True):
    """
    Process a single frame: Detect, Draw.
    Wrapper for detection_engine.
    """
    return detection_engine.process_frame(frame, model, conf_thresh=conf_thresh, draw=draw_pd)

from streamlit_option_menu import option_menu

# ... (Previous code)

# --- MAIN APP LAYOUT ---
# Removing Title as we will put it in specific pages or cleaner header
# st.title("👷 SafetyEye Pro")

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("---")
    selected = option_menu(
        menu_title=None,
        options=["Live Monitoring", "Video Analysis", "Image Analysis", "History & Analytics", "Face Management"],
        icons=["camera-video", "film", "image", "bar-chart-line", "person-badge"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "orange", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#333"},
            "nav-link-selected": {"background-color": "#444"},
        }
    )

# --- PAGE 1: LIVE MONITORING ---
if selected == "Live Monitoring":
    st.title("🔴 Live Mission Control")
    col_video, col_stats = st.columns([3, 1])
    
    with col_stats:
        # Glassmorphic Card 1
        st.markdown('<div data-testid="metric-container">', unsafe_allow_html=True)
        if not st.session_state.webcam_active:
            if st.button("▶️ Start Monitoring"):
                st.session_state.webcam_active = True
                st.rerun()
        else:
            if st.button("🛑 Stop Monitoring"):
                st.session_state.webcam_active = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("") # Spacer
        
        kpi1_ph = st.empty()
        kpi2_ph = st.empty()
        alert_ph = st.empty()
        
    with col_video:
        video_ph = st.empty()

    if st.session_state.webcam_active:
        cap = cv2.VideoCapture(0)
        
        # Determine persistent path for violations
        violations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "violations")
        os.makedirs(violations_dir, exist_ok=True)
        
        # Local variable for cooldown
        last_log_time = 0
        LOG_COOLDOWN = 5 # seconds

        while st.session_state.webcam_active:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to read webcam.")
                break
                
            # Process Frame
            frame, p_count, det_classes, v_list = process_frame(frame, confidence_threshold)

            # Face Rec (Only on Live)
            person_name = "Unknown"
            if enable_face_rec and p_count > 0:
                person_name = face_rec.identify_person(frame)
                if person_name != "Unknown":
                    cv2.putText(frame, f"Person: {person_name}", (10, 30), 0, 1, (0, 255, 255), 2)

            # Violations Logic
            if v_list:
                # 1. Alert UI
                alert_text = f"🚨 {', '.join(v_list).upper()}"
                alert_ph.error(alert_text)
                
                # 2. Audio Alert
                if enable_audio:
                    try:
                        winsound.Beep(1000, 200) # 200ms beep
                    except:
                        pass
                
                # 3. Log DB with Cooldown
                current_time = time.time()
                if current_time - last_log_time > LOG_COOLDOWN:
                    # Create daily subfolder
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    day_dir = os.path.join(violations_dir, today_str)
                    os.makedirs(day_dir, exist_ok=True)
                    
                    snap_path = os.path.join(day_dir, f"violation_{int(current_time)}.jpg")
                    cv2.imwrite(snap_path, frame)
                    
                    db.log_violation(",".join(v_list), 0.9, snap_path, person_name)
                    last_log_time = current_time
                
                    # 4. Send Email
                    if enable_email:
                         email_sender.async_send_email(v_list, snap_path, email_config)
            else:
                alert_ph.empty()

            # Update KPIs
            kpi1_ph.metric("Persons On-Site", p_count)
            
            # Calculate Violations Today
            history_df = db.get_history()
            if not history_df.empty:
                # Ensure timestamp is datetime
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
                today = datetime.now().date()
                today_violations = history_df[history_df['timestamp'].dt.date == today]
                todays_count = len(today_violations)
            else:
                todays_count = 0
            
            kpi2_ph.metric("Violations (Today)", todays_count)

            # Display
            video_ph.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
            
        cap.release()

# --- PAGE 2: VIDEO ANALYSIS ---
elif selected == "Video Analysis":
    st.header("📼 Video Analysis")
    st.markdown("Upload CCTV footage for post-processing.")
    
    # Show storage path
    vid_save_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "violations", "videos"))
    st.info(f"📂 **Violation snapshots will be saved to:** `{vid_save_dir}`")
    
    video_file = st.file_uploader("Choose a video...", type=['mp4', 'avi', 'mov'])
    
    if video_file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        
        cap = cv2.VideoCapture(tfile.name)
        st_video = st.empty()
        
        # Tracking for Video Analysis
        last_log_time_vid = 0
        LOG_COOLDOWN_VID = 2 # 2 seconds cooldown for pre-recorded video
        violations_dir_vid = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "violations", "videos")
        os.makedirs(violations_dir_vid, exist_ok=True)
        violation_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Use same processing logic
            frame, p_cnt, _, v_list = process_frame(frame, confidence_threshold)
            
            # Log Violations
            current_time = time.time()
            if v_list and (current_time - last_log_time_vid > LOG_COOLDOWN_VID):
                snap_path = os.path.join(violations_dir_vid, f"violation_vid_{int(current_time)}.jpg")
                success = cv2.imwrite(snap_path, frame)
                
                if success:
                    db.log_violation(",".join(v_list), 0.9, snap_path, "Unknown", True, "Video Upload")
                    last_log_time_vid = current_time
                    violation_count += 1
                else:
                    st.write(f"Debug: Failed to write to {snap_path}")
            
            st_video.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
            
        cap.release()
        if violation_count > 0:
            st.success(f"Processed video. Logged {violation_count} violation snapshots to database.")
        else:
            st.info("No violations detected in the video.")

# --- PAGE 3: IMAGE ANALYSIS ---
elif selected == "Image Analysis":
    st.header("🖼️ Image Analysis")
    
    # Show storage path
    img_save_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "violations", "images"))
    st.info(f"📂 **Analyzed images will be saved to:** `{img_save_dir}`")
    
    img_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg'])
    
    if img_file:
        image = Image.open(img_file)
        # Convert to CV2 format
        img_array = np.array(image)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        c1, c2 = st.columns(2)
        with c1:
            st.image(image, caption="Original", use_container_width=True)
            
        # Process
        processed_frame, p_cnt, det_classes, v_list = process_frame(img_bgr, confidence_threshold)
        
        processed_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        
        with c2:
            st.image(processed_rgb, caption="Analyzed", use_container_width=True)
            
        # Report
        if v_list:
             st.error(f"🚨 Violations Detected: {', '.join(v_list)}")
             
             # Save to DB
             violations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "violations", "images")
             os.makedirs(violations_dir, exist_ok=True)
             
             timestamp = int(time.time())
             snap_path = os.path.join(violations_dir, f"violation_img_{timestamp}.jpg")
             success = cv2.imwrite(snap_path, processed_frame)
             
             if success:
                 db.log_violation(",".join(v_list), 0.9, snap_path, "Unknown", True, "Image Upload")
                 st.success(f"✅ Violation Logged to Database.\nSaved to: `{snap_path}`")
             else:
                 st.error(f"❌ Failed to save image to `{snap_path}`. Check permissions or path.")
             
        else:
             st.success("✅ No Violations Detected")


# --- PAGE 4: HISTORY ---
elif selected == "History & Analytics":
    st.header("📋 Violation Logs & Analysis")
    df = db.get_history()
    
    if not df.empty:
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Violations", len(df))
        m2.metric("Most Common", df['violation_type'].mode()[0] if not df['violation_type'].empty else "N/A")
        m3.metric("Latest", df.iloc[0]['timestamp'])
        
        st.markdown("---")
        
        # Charts
        if px:
            st.subheader("Analytics Overview")
            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            c1, c2 = st.columns(2)
            with c1:
                fig_type = px.bar(df, x='violation_type', title="Violations by Type", color='violation_type')
                fig_type.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig_type, use_container_width=True)
            with c2:
                # Resample by hour
                df['hour'] = df['timestamp'].dt.hour
                fig_time = px.histogram(df, x='hour', nbins=24, title="Violations by Hour of Day")
                fig_time.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig_time, use_container_width=True)
                
        # Data Table
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No violations recorded yet.")

# --- PAGE 5: FACE MANAGEMENT ---
elif selected == "Face Management":
    st.header("👤 Authorized Personnel")
    st.write("Upload images of workers to identify them.")
    
    uploaded_files = st.file_uploader("Upload Faces", accept_multiple_files=True, type=['jpg', 'png'])
    
    if uploaded_files:
        faces_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "faces")
        os.makedirs(faces_dir, exist_ok=True)
        
        for up_file in uploaded_files:
            with open(os.path.join(faces_dir, up_file.name), "wb") as f:
                f.write(up_file.getbuffer())
        
        st.success(f"Uploaded {len(uploaded_files)} images.")
        
        if st.button("🔄 Retrain Face Model"):
            with st.spinner("Encoding faces..."):
                count = face_rec.encode_faces(faces_dir)
            st.success(f"Model updated! {count} people known.")
