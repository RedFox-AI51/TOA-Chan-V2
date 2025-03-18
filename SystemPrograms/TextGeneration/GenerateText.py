import requests
import json
import re
import time
from datetime import datetime
from SystemPrograms.SystemSetup.ReadConfigs import ReadConfigs

# WiFi Check Integration
from SystemPrograms.CheckInternet.ManageWIFI import CheckWIFI
manageWiFi = CheckWIFI()
wifi_connected = manageWiFi.get_wifi_status()

app = ReadConfigs()
CONFIG = app.load_config()
FILE_TO_FIND = app.get_file_path(CONFIG, "tokens.json")

def load_api_key():
    try:
        with open(FILE_TO_FIND, "r") as file:
            tokens = json.load(file)
            return tokens.get("TOA-Chan V2", {}).get("gpt-main", None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

class BaseAI:
    def __init__(self, memory_file="SystemFiles/Memory/memory.json"):
        self.api_key = load_api_key()
        if not self.api_key:
            raise ValueError("API key not found in tokens.json")
        self.memory_file = memory_file
        self.memory, self.last_interaction = self.load_memory()

        # Initialize system prompt if memory is empty
        if not self.memory:
            self.memory.append({"role": "system", "content": "Your name is Toa-chan. As far as you know, you're a human and you are very curious about everything."})

    def load_memory(self):
        """Loads chat memory from a file."""
        try:
            with open(self.memory_file, "r") as file:
                data = json.load(file)
                return data.get("messages", []), data.get("last_interaction", None)
        except (FileNotFoundError, json.JSONDecodeError):
            return [], None

    def save_memory(self):
        """Saves chat memory to a file."""
        with open(self.memory_file, "w") as file:
            json.dump({"messages": self.memory, "last_interaction": self.last_interaction}, file, indent=4)

    def get_time_since_last_interaction(self):
        """Calculates the time elapsed since the last interaction."""
        if not self.last_interaction:
            return "This is your first message."

        last_time = datetime.strptime(self.last_interaction, "%Y-%m-%d %H:%M:%S")
        elapsed = (datetime.now() - last_time).total_seconds()
        return f"{int(elapsed // 60)} minutes and {int(elapsed % 60)} seconds ago."

    def chat_with_ai(self, user_input, vision_model=None):
        """Processes user input and generates a response using OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Update last interaction time
        self.last_interaction = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Inject vision data if requested
        if vision_model and "what do you see" in user_input.lower():
            vision_context = vision_model.get_vision_data()
            self.memory.append({"role": "system", "content": f"Visual Input: {vision_context}"})

        # Inject time awareness
        if "what time is it" in user_input.lower():
            self.memory.append({"role": "system", "content": f"The current time is {datetime.now().strftime('%H:%M:%S')}."})

        if "how long since last message" in user_input.lower():
            self.memory.append({"role": "system", "content": f"Your last message was {self.get_time_since_last_interaction()}"})
        
        if not wifi_connected:
            print("No WiFi Connection")
            return
        

        self.memory.append({"role": "user", "content": user_input})

        data = {
            "model": "google/gemma-3-27b-it:free",
            "messages": self.memory
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                ai_response = response_data["choices"][0].get("message", {}).get("content", "No response")
                ai_response = re.sub(r"\\boxed{(.*?)}", r"\1", ai_response)  # Remove \boxed{{}}
                self.memory.append({"role": "assistant", "content": ai_response})

                # Save memory after response
                self.save_memory()

                return ai_response
            else:
                return "No response"
        else:
            return f"API Error: {response.status_code} - {response.text}"

def main():
    try:
        toa_ai = BaseAI()
    except ValueError as e:
        print(e)
        exit()

    while True:
        user_message = input("You: ")
        if user_message.lower() in ["exit", "quit"]:
            break
        response = toa_ai.chat_with_ai(user_message)
        print(f"AI: {response}")

# Example Usage
if __name__ == "__main__":
    print("Starting AI Chat...")