import cv2
import base64
import requests
import json
import time
import threading
import os
from SystemPrograms.Vision.FacialRecognition import FaceRecognizer
from SystemPrograms.SystemSetup.ReadConfigs import ReadConfigs

# WiFi Check Integration
from SystemPrograms.CheckInternet.ManageWIFI import CheckWIFI
manageWiFi = CheckWIFI()
wifi_connected = manageWiFi.get_wifi_status()

# Load API key from tokens.json
app = ReadConfigs()
CONFIG = app.load_config()
FILE_TO_FIND = "tokens.json"

def load_api_key():
    try:
        with open(FILE_TO_FIND, "r") as file:
            tokens = json.load(file)
            return tokens.get("TOA-Chan V2", {}).get("gpt-main", None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

API_KEY = load_api_key()
if not API_KEY:
    print("[ERROR] Missing API key. Ensure 'tokens.json' is configured.")

class VisionModel:
    def __init__(self, api_key, vision_file="SystemFiles/Memory/vision_memory.txt", capture_interval=5, camera_index=1):
        if not api_key:
            raise ValueError("Missing API key.")
        
        self.api_key = api_key
        self.vision_file = vision_file
        self.capture_interval = capture_interval
        self.camera_index = camera_index
        self.running = True
        self.face_recognizer = FaceRecognizer()

    def encode_image_to_base64(self, image):
        """Converts an image to base64 format."""
        _, buffer = cv2.imencode(".jpg", image)
        return base64.b64encode(buffer).decode("utf-8")

    def analyze_image(self, image):
        """Sends an image to OpenRouter AI for object recognition."""
        image_base64 = self.encode_image_to_base64(image)
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        if not wifi_connected:
            print("No WiFi Connection")
            return

        data = {
            "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe what is in this image as if looking through your own eyes."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                vision_description = response_data["choices"][0]["message"]["content"]
                self.save_vision_data(vision_description)
                return vision_description
            else:
                return "No description received."
        else:
            return f"Error: {response.status_code} - {response.text}"

    def save_vision_data(self, vision_description):
        """Saves the latest vision description to a file."""
        with open(self.vision_file, "w") as file:
            file.write(vision_description)

    def get_vision_data(self):
        """Retrieves the latest vision data from the file."""
        try:
            with open(self.vision_file, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            return "No recent visual data."

    def vision_loop(self):
        """Captures frames, processes face recognition, and AI analysis."""
        cap = cv2.VideoCapture(self.camera_index)

        while self.running:
            ret, frame = cap.read()
            if ret:
                recognized_faces = self.face_recognizer.recognize_faces(frame)
                vision_data = self.analyze_image(frame)
                
                print(f"AI Vision: {vision_data}")
                print(f"Recognized Faces: {recognized_faces}")

                cv2.imshow("AI Vision & Face Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            time.sleep(self.capture_interval)

        cap.release()
        cv2.destroyAllWindows()

    def start_vision_processing(self):
        """Starts vision processing in a background thread."""
        threading.Thread(target=self.vision_loop, daemon=True).start()

    def stop_vision_processing(self):
        """Stops vision processing loop."""
        self.running = False

def main():
    if API_KEY:
        vision = VisionModel(API_KEY, capture_interval=5)
        vision.start_vision_processing()

        while True:
            cmd = input("Enter 'see' to get vision data, 'faces' to list known faces, or 'quit' to exit: ")
            if cmd.lower() == "see":
                print("AI sees:", vision.get_vision_data())
            elif cmd.lower() == "faces":
                print("Known Faces:", vision.face_recognizer.known_faces["names"])
            elif cmd.lower() == "quit":
                vision.stop_vision_processing()
                break
    else:
        print("[ERROR] Could not initialize AI Vision due to missing API key.")

if __name__ == "__main__":
    print("Starting AI Vision with Face Recognition...")
    main()