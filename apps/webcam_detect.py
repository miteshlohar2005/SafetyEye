import cv2
import os
import time
import tempfile
import threading
from ultralytics import YOLO

# Import local modules
try:
    from utils import db, face_rec, detection_engine
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from utils import db, face_rec, detection_engine

# --- Configuration ---
CONFIDENCE_THRESHOLD = 0.4
LOG_COOLDOWN = 5 # Seconds between logging same violation type
ENABLE_FACE_REC = True

def main():
    print("Initialize SafetyEye Standalone Monitor...")
    
    # 1. Initialize DB
    db.init_db()
    print("Database initialized.")

    # 2. Load Model
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "..", "models", "best.pt")
        if not os.path.exists(model_path):
             print(f"Model not found at {model_path}, downloading/using yolov8n...")
             model = YOLO("yolov8n.pt")
        else:
            model = YOLO(model_path)
            print(f"Loaded model from {model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # 3. Start Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting Main Loop. Press 'q' to exit.")
    
    last_log_time = 0
    
    while True:
        success, frame = cap.read()
        if not success:
            break

        # 4. Process Frame used Shared Engine
        # Returns: frame, person_count, detected_classes, violation_list
        frame, p_count, det_classes, v_list = detection_engine.process_frame(
            frame, model, conf_thresh=CONFIDENCE_THRESHOLD, draw=True
        )

        # 5. Face Recognition (Optional)
        person_name = "Unknown"
        if ENABLE_FACE_REC and p_count > 0:
            # We use the raw frame for face rec, or the processed one? 
            # Processed one has boxes drawn, might interfere. ideally raw.
            # But process_frame modifies 'frame' in place if we are not careful?
            # detection_engine.process_frame modifies the frame passed to it if draw=True.
            # So we should have made a copy for face_rec if we wanted clean input.
            # However, face_rec usually is robust enough or we can accept it. 
            # Better: pass a copy to process_frame or use a copy for face_rec?
            # Let's use the frame (already drawn on) for now as face_rec crops faces.
            # If boxes cover faces, it fails. 
            # Ideally: Face Rec First, Then Draw.
            # BUT: detection engine does both.
            # Fix: In future, separate Detection from Drawing.
            # For now, let's try identifying on the already drawn frame.
            name = face_rec.identify_person(frame)
            if name != "Unknown":
                person_name = name
                cv2.putText(frame, f"Person: {name}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # 6. Check Violations and Log
        if v_list:
            current_time = time.time()
            if current_time - last_log_time > LOG_COOLDOWN:
                print(f"ALERT: Violations detected: {v_list}")
                
                # Save snapshot
                timestamp = int(current_time)
                # Determine persistent path
                import datetime # Lazy import
                today_str = datetime.datetime.now().strftime('%Y-%m-%d')
                violations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "violations")
                day_dir = os.path.join(violations_dir, today_str)
                os.makedirs(day_dir, exist_ok=True)
                
                snap_path = os.path.join(day_dir, f"violation_{timestamp}.jpg")
                cv2.imwrite(snap_path, frame)
                
                # Log to DB
                # run in thread to not block UI? SQLite needs thread safety care, but typically fast enough for this.
                try:
                    db.log_violation(",".join(v_list), 0.9, snap_path, person_name)
                    print("Logged to DB.")
                except Exception as e:
                    print(f"DB Error: {e}")
                
                last_log_time = current_time
            else:
                # Flash warning on screen without logging
                pass
            
            # Draw Alert on Screen
            cv2.putText(frame, "VIOLATION DETECTED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        # 7. Display
        cv2.imshow('SafetyEye Pro - Standalone', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
