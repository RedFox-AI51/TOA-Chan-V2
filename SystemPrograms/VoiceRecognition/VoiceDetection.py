import speech_recognition as sr

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def recognize_speech(self):
        with self.microphone as source:
            print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=5)
                print("Recognizing...")
                
                text = self.recognizer.recognize_sphinx(audio)
                
                print("Recognized Speech:", text)
                return text
            except sr.WaitTimeoutError:
                print("No speech detected. Try again.")
            except sr.UnknownValueError:
                print("Could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
        return None

if __name__ == "__main__":
    try:
        recognizer = SpeechRecognizer()
        recognizer.recognize_speech()
    except Exception as e:
        print(e)