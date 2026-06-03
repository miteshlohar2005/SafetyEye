import os
import cv2
import pickle

# Gracious fallback if face_recognition is not installed
try:
    import face_recognition
    FACE_REC_AVAILABLE = True
except ImportError:
    FACE_REC_AVAILABLE = False
    print("Warning: face_recognition not installed. Feature disabled.")

ENCODINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "encodings.pkl")

def load_encodings():
    if not os.path.exists(ENCODINGS_PATH):
        return [], []
    with open(ENCODINGS_PATH, 'rb') as f:
        known_encodings, known_names = pickle.load(f)
    return known_encodings, known_names

def save_encodings(known_encodings, known_names):
    os.makedirs(os.path.dirname(ENCODINGS_PATH), exist_ok=True)
    with open(ENCODINGS_PATH, 'wb') as f:
        pickle.dump((known_encodings, known_names), f)

def encode_faces(image_folder):
    """Encodes all faces in a folder."""
    if not FACE_REC_AVAILABLE:
        return 0
        
    known_encodings = []
    known_names = []
    
    for filename in os.listdir(image_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            name = os.path.splitext(filename)[0]
            filepath = os.path.join(image_folder, filename)
            
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(name)
    
    save_encodings(known_encodings, known_names)
    return len(known_names)

def identify_person(frame, face_msg_locs=None):
    """
    Identifies person in the frame. 
    Optimization: Only run if 'person' detected by YOLO to save compute? 
    Actually, usually we run face rec independently or crop YOLO person box.
    For simplicity, we'll run it on the whole frame but user can enable/disable.
    """
    if not FACE_REC_AVAILABLE:
        return "Unknown"
        
    # Resize for speed
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    known_encodings, known_names = load_encodings()
    if not known_encodings:
        return "Unknown"

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    name = "Unknown"
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]
            # Just return the first found for now
            return name
            
    return name
