import cv2
import math
from ultralytics import YOLO
import cvzone
import os

# 1. Load your custom model
# Make sure best.pt is in the same folder as this script!
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "..", "models", "best.pt")
model = YOLO(model_path) 

# 2. Start Webcam
# Use 0 for webcam. If you want to test a video, replace 0 with "test_video.mp4"
cap = cv2.VideoCapture(0) 
cap.set(3, 1280) # Width
cap.set(4, 720)  # Height

while True:
    success, img = cap.read()
    if not success:
        break

    # Run detection
    results = model(img, stream=True)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Bounding Box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1

            # Confidence
            conf = math.ceil((box.conf[0] * 100)) / 100
            
            # Class Name
            cls = int(box.cls[0])
            currentClass = model.names[cls] # Automatically gets names from your model

            # --- SMART COLOR LOGIC ---
            # If the class name contains "no-", it means danger (RED)
            if "no-" in currentClass.lower():
                color = (0, 0, 255) # Red
                myText = f"ALERT: {currentClass}"
            else:
                color = (0, 255, 0) # Green
                myText = f"Safe: {currentClass}"

            # Draw the box and text
            cvzone.putTextRect(img, f'{myText} {conf}', 
                               (max(0, x1), max(35, y1)), 
                               scale=1.5, thickness=2, 
                               colorR=color, colorT=(255,255,255))
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)

    cv2.imshow("AI Safety Monitor", img)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()