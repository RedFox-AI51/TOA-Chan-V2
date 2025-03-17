import cv2
import face_recognition
import pickle
import os

DATA_FILE = "SystemFiles/Memory/faces.pkl"

class FaceRecognizer:
    def __init__(self):
        self.load_known_faces()

    def load_known_faces(self):
        """Loads known faces from a file or initializes an empty database."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "rb") as f:
                self.known_faces = pickle.load(f)
        else:
            self.known_faces = {"encodings": [], "names": []}

    def save_known_faces(self):
        """Saves updated face data."""
        with open(DATA_FILE, "wb") as f:
            pickle.dump(self.known_faces, f)

    def recognize_faces(self, frame):
        """Detects and recognizes faces in a given frame."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        recognized_faces = []
        
        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(self.known_faces["encodings"], face_encoding)
            name = "Unknown"

            if True in matches:
                matched_idx = matches.index(True)
                name = self.known_faces["names"][matched_idx]
            else:
                print("New face detected! Please enter a name: ")
                name = input()
                self.known_faces["encodings"].append(face_encoding)
                self.known_faces["names"].append(name)
                self.save_known_faces()

            recognized_faces.append(name)

            # Draw bounding box
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return recognized_faces
