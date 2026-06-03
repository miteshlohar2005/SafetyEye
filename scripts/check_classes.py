from ultralytics import YOLO
import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "..", "models", "best.pt")
output_path = os.path.join(current_dir, "..", "data", "classes.txt")

model = YOLO(model_path)
with open(output_path, "w") as f:
    f.write(str(model.names))
