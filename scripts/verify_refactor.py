import sys
import os
import cv2
import numpy as np

# Add apps to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "apps"))

print("Testing Imports...")
try:
    from utils import detection_engine
    print("✅ detection_engine imported")
except ImportError as e:
    print(f"❌ detection_engine import failed: {e}")
    sys.exit(1)

try:
    import webcam_detect
    print("✅ webcam_detect imported")
except ImportError as e:
    print(f"❌ webcam_detect import failed: {e}")

try:
    import flask_app
    print("✅ flask_app imported")
except ImportError as e:
    print(f"❌ flask_app import failed: {e}")

print("\nTesting Detection Engine...")
# Create a dummy black image
img = np.zeros((480, 640, 3), dtype=np.uint8)

# Mock Model
class MockBox:
    xyxy = [[100, 100, 200, 200]]
    cls = [0] # 0 = 'helmet' usually, or whatever
    conf = [0.95]

class MockResult:
    boxes = [MockBox()]

class MockModel:
    names = {0: 'helmet'}
    def __call__(self, frame, conf=0.5, verbose=False):
        return [MockResult()]

model = MockModel()

try:
    frame, p_cnt, classes, violations = detection_engine.process_frame(img, model, conf_thresh=0.4, draw=True)
    print(f"✅ process_frame ran successfully. Classes found: {classes}")
    
    if 'helmet' in classes:
        print("✅ Detection logic verified")
    else:
        print("❌ Detection logic returned unexpected classes")
        
except Exception as e:
    print(f"❌ process_frame failed: {e}")

print("\nVerification Complete.")
