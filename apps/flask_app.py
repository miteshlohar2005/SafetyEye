from flask import Flask, render_template, Response, jsonify, request
import cv2
import os
import sys
import time
from datetime import datetime

# Import shared detection engine
try:
    from utils import detection_engine
except ImportError:
    # Handle path if run from apps/ or root
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from utils import detection_engine

from ultralytics import YOLO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the model
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "..", "models", "best.pt")
    if not os.path.exists(model_path):
        model = YOLO("yolov8n.pt")
    else:
        model = YOLO(model_path)
except Exception as e:
    print(f"Error loading model: {e}")
    model = YOLO("yolov8n.pt")

# Global State Variables
app_state = {
    "is_monitoring": False,
    "session_start_time": None,
    "total_detections": 0,
    "active_violations": 0,
    "violation_count": 0
}

def generate_frames():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    while app_state["is_monitoring"]:
        success, frame = cap.read()
        if not success:
            break

        # Process Frame
        frame, p_cnt, det_classes, v_list = detection_engine.process_frame(
            frame, model, conf_thresh=0.6, draw=True
        )

        # Update stats
        app_state["total_detections"] += p_cnt
        app_state["active_violations"] = len(v_list)
        if v_list:
            app_state["violation_count"] += len(v_list)

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
        # Small sleep to prevent CPU hogging
        time.sleep(0.03)

    # Clean up when monitoring stops
    cap.release()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    if not app_state["is_monitoring"]:
        return Response(status=204)
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    app_state["is_monitoring"] = True
    app_state["session_start_time"] = datetime.now()
    app_state["total_detections"] = 0
    app_state["violation_count"] = 0
    app_state["active_violations"] = 0
    return jsonify({"status": "success", "message": "Monitoring started"})

@app.route('/stop_monitoring', methods=['POST'])
def stop_monitoring():
    app_state["is_monitoring"] = False
    app_state["active_violations"] = 0
    return jsonify({"status": "success", "message": "Monitoring stopped"})

@app.route('/stats')
def stats():
    duration = 0
    if app_state["is_monitoring"] and app_state["session_start_time"]:
        delta = datetime.now() - app_state["session_start_time"]
        duration = int(delta.total_seconds())

    return jsonify({
        'is_monitoring': app_state["is_monitoring"],
        'violation_count': app_state["violation_count"],
        'total_detections': app_state["total_detections"],
        'active_violations': app_state["active_violations"],
        'session_duration_seconds': duration
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
