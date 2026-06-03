import cv2
import math
from ultralytics import YOLO

# Constants
VIOLATION_CLASSES = ['no-helmet', 'no-vest', 'no-goggles', 'no-gloves', 'no-mask']
COMPLIANT_CLASSES = ['helmet', 'vest', 'goggles', 'gloves', 'mask']

def get_center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)

def is_inside(center, container_box):
    cx, cy = center
    px1, py1, px2, py2 = container_box
    return px1 <= cx <= px2 and py1 <= cy <= py2

def process_frame(frame, model, conf_thresh=0.6, draw=True):
    # Detect using aggressive NMS and higher threshold
    results = model(frame, conf=conf_thresh, iou=0.45, agnostic_nms=True, verbose=False)
    
    person_boxes = []
    ppe_boxes = []
    
    # First pass: Separate persons and PPE
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            conf = math.ceil((box.conf[0] * 100)) / 100
            
            box_data = {
                'coords': (x1, y1, x2, y2),
                'cls': cls_name,
                'conf': conf
            }
            
            if cls_name == 'person':
                person_boxes.append(box_data)
            else:
                ppe_boxes.append(box_data)

    detected_classes = set()
    violation_list = []
    final_boxes_to_draw = []
    
    # Always draw persons
    for p in person_boxes:
        final_boxes_to_draw.append(p)

    # Process PPE and assign to persons
    for p in person_boxes:
        person_ppes = []
        # Find PPEs belonging to this person
        for ppe in ppe_boxes:
            if is_inside(get_center(ppe['coords']), p['coords']):
                person_ppes.append(ppe)
        
        # Rule Processing: Filter false positive violations if compliant gear is present
        compliant_set = set([item['cls'] for item in person_ppes if item['cls'] in COMPLIANT_CLASSES])
        
        for ppe in person_ppes:
            cls = ppe['cls']
            # If it's a violation, but the compliant counterpart is present on this person, skip it
            if cls == 'no-helmet' and 'helmet' in compliant_set: continue
            if cls == 'no-vest' and 'vest' in compliant_set: continue
            if cls == 'no-goggles' and 'goggles' in compliant_set: continue
            if cls == 'no-gloves' and 'gloves' in compliant_set: continue
            if cls == 'no-mask' and 'mask' in compliant_set: continue
            
            final_boxes_to_draw.append(ppe)

    # If no persons detected, just show all high-conf PPE anyway (fallback)
    if not person_boxes:
        final_boxes_to_draw = ppe_boxes
        
    person_count = len(person_boxes)

    # Draw and collate results
    for box in final_boxes_to_draw:
        x1, y1, x2, y2 = box['coords']
        cls_name = box['cls']
        conf = box['conf']
        
        detected_classes.add(cls_name)
        
        color = (200, 200, 200) # Gray for person or unknown
        if cls_name in VIOLATION_CLASSES or "no-" in cls_name.lower() or cls_name == "unauthorized":
            color = (0, 0, 255) # Red for Violation
            violation_list.append(cls_name)
        elif cls_name in COMPLIANT_CLASSES:
            color = (0, 255, 0) # Green for Compliant
            
        if draw:
            # Draw Box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw Professional Label
            label = f"{cls_name.replace('-', ' ').title()} - {int(conf*100)}%"
            t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, thickness=1)[0]
            
            # Background for text
            cv2.rectangle(frame, (x1, y1 - t_size[1] - 8), (x1 + t_size[0] + 8, y1), color, -1)
            # Text
            cv2.putText(frame, label, (x1 + 4, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
            
    return frame, person_count, detected_classes, violation_list
