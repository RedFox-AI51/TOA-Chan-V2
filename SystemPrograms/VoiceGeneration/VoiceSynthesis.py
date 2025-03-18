import requests
import os
import json
from pydub import AudioSegment
from pydub.playback import play
from SystemPrograms.SystemSetup.ReadConfigs import ReadConfigs

# WiFi Check Integration
from SystemPrograms.CheckInternet.ManageWIFI import CheckWIFI
manageWiFi = CheckWIFI()
wifi_connected = manageWiFi.get_wifi_status()

class Voice:
    def __init__(self, output_path="SystemFiles/temp/output.mp3", chunk_size=1024):
        # Load API key and voice ID from tokens.json using ReadConfigs
        self.config_reader = ReadConfigs()
        tokens_path = self.config_reader.get_file_path(self.config_reader.load_config(), "tokens.json")
        
        self.api_key, self.voice_id = self._load_api_details(tokens_path)
        self.output_path = output_path
        self.wav_path = "SystemFiles/temp/output.wav"  # Path for the converted wav file
        self.chunk_size = chunk_size
        self.tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
        self.headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key
        }

    def _load_api_details(self, tokens_path):
        """Load API key and VoiceID from the specified JSON config file."""
        try:
            with open(tokens_path, "r") as file:
                data = json.load(file)
                api_key = data["TOA-Chan V2"]["TOA-Chan Voice"]["elevenlabs"]
                voice_id = data["TOA-Chan V2"]["TOA-Chan Voice"]["VoiceID"]
                return api_key, voice_id
        except (FileNotFoundError, KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error loading API details: {str(e)}")
            return None, None

    def generate_audio(self, text, model_id="eleven_multilingual_v2", stability=1.0, similarity_boost=0.8, style=0.0, use_speaker_boost=True):
        """
        Generate audio from text using ElevenLabs API.
        """
        if not self.api_key or not self.voice_id:
            print("API key or VoiceID missing. Please check your configuration.")
            return
        
        if not wifi_connected:
            print("No WiFi Connection")
            return
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost
            }
        }

        try:
            response = requests.post(self.tts_url, headers=self.headers, json=data, stream=True)
            if response.ok:
                self._save_audio_stream(response)
                print("Audio stream saved successfully.")
            else:
                print(f"Failed to generate audio: {response.status_code}, {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while making the request: {str(e)}")

    def _save_audio_stream(self, response):
        """Save the audio stream to the specified output path."""
        with open(self.output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    f.write(chunk)

    def play_audio(self):
        """Play the generated audio file as a .wav file and delete the .mp3 afterward."""
        if os.path.exists(self.output_path):
            try:
                # Convert mp3 to wav
                audio = AudioSegment.from_mp3(self.output_path)
                audio.export(self.wav_path, format="wav")  # Save as .wav file
                print(f"Playing audio: {self.wav_path}")
                play(audio)

                # Delete the .mp3 file after conversion
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)
                    print(f"Deleted the .mp3 file: {self.output_path}")
            except Exception as e:
                print(f"Failed to play the audio: {str(e)}")
        else:
            print(f"Audio file {self.output_path} not found. Please generate it first.")

# Example usage
if __name__ == "__main__":
    TEXT_TO_SPEAK = "Hi, I'm Toa chan"

    # Initialize the Voice class
    tts = Voice()

    # Generate audio with the specified text
    tts.generate_audio(text=TEXT_TO_SPEAK)

    # Play the generated audio
    tts.play_audio()