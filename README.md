# 👷 SafetyEye Pro: AI-Powered Workplace Safety Monitoring System

## 🌟 Project Overview
**SafetyEye Pro** is an advanced Computer Vision application designed to enhance workplace safety by automatically detecting Personal Protective Equipment (PPE) violations in real-time. 

Built with **YOLOv8** and **Streamlit**, this system monitors video feeds to ensure workers are wearing required safety gear (Helmets, Vests, Goggles, etc.). It goes beyond simple detection by integrating **Zone-Based Monitoring**, **Face Recognition** for accountability, and **Automated Email Alerts** for immediate intervention.

---

## 🚀 Key Features

### 1. 🎥 Real-Time PPE Detection
- **AI Model**: Uses a custom-trained YOLOv8 model to detect:
  - `NO-Hardhat`, `NO-Safety Vest`, `NO-Mask` (Violations)
  - `Hardhat`, `Safety Vest`, `Mask` (Compliant)
- **Visual Feedback**: Draws **RED** boxes for violations and **GREEN** boxes for compliance.

### 2. 👤 Face Recognition Integration
- **Accountability**: Identifies workers who are violating safety rules.
- **Face Management**: Easily upload employee photos to train the system.

### 3. 📧 Automated Alert System
- **Instant Notifications**: Sends an email to supervisors with a **snapshot** of the violation immediately upon detection.
- **Smart Throttling**: Prevents spam by limiting alerts to once per minute per violation type.

### 4. 📊 Analytics Dashboard
- **Digital Logbook**: All violations are recorded in a local database.
- **Data Visualization**: View trends such as "Violations by Hour" or "Most Common Violations" to identify training needs.

---

## 🛠️ Technology Stack
- **Core AI**: Ultralytics YOLOv8 (Deep Learning Object Detection)
- **Interface**: Streamlit (Python Web Framework)
- **Computer Vision**: OpenCV
- **Database**: SQLite (Lightweight, serverless storage)
- **Data Analysis**: Pandas & Plotly
- **Face Recognition**: dlib & face_recognition

---

## 📂 Project Structure

```
SafetyAI_3/
│
├── apps/                   # Application Source Code
│   ├── streamlit_app.py    # MAIN DASHBOARD ENTRY POINT
│   ├── flask_app.py        # Alternative Flask Web App
│   ├── cv_monitor.py       # Standalone OpenCV Monitor
│   ├── webcam_detect.py    # Basic Detection Script
│   └── utils/              # Utility Modules
│       ├── db.py           # Database Handler
│       ├── email_sender.py # Email Alert System
│       └── face_rec.py     # Face Recognition Logic
│
├── models/                 # AI Models
│   └── best.pt             # Trained YOLOv8 Weights
│
├── data/                   # Data Storage
│   ├── safety_logs.db      # SQLite Database
│   ├── faces/              # Known Faces Images
│   └── classes.txt         # Class Names
│
└── requirements.txt        # Dependencies
```

---

## ⚙️ Installation & Setup

1.  **Clone/Download the Repository**
2.  **Install Dependencies**:
    ```bash
    pip install ultralytics streamlit opencv-python-headless pandas plotly face-recognition
    ```
3.  **Run the Dashboard**:
    ```bash
    streamlit run apps/streamlit_app.py
    ```

---

## 📖 User Guide

### **Tab 1: 🎥 Live Monitoring**
- Click **Start Monitoring** to open the webcam.
- View real-time detections.
- **Violations** trigger audio alerts and red boxes.

### **Tab 2: 📼 Video Analysis**
- Upload a pre-recorded CCTV video (MP4/AVI).
- The AI processes the video frame-by-frame for violations.

### **Tab 3: 🖼️ Image Analysis**
- Upload a static image to check for compliance.

### **Tab 4: 📊 History & Analytics**
- Review the log of all past violations.
- Analyze charts to see when most accidents happen.

### **Tab 5: 👤 Face Management**
- Upload photos of authorized personnel.
- Click **Retrain Model** to let the AI learn their faces.

---

## 🔮 Future Scope
- Integration with IP Cameras (RTSP).
- Cloud Dashboard for multi-site monitoring.
- SMS/WhatsApp Alert Integration.

---
**Developed for Safety Compliance Project**
