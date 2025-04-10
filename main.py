from SystemPrograms.TextGeneration.GenerateText import BaseAI
from SystemPrograms.Vision.AI_Vision import VisionModel

from SubprocessTerminal import TerminalManager

import threading
import datetime
import time

# setup = TerminalManager()
# setup.open_terminal()

# Facial Recognition and AI
toa_v = VisionModel()
toa_b = BaseAI()

# Start the vision processing in a separate thread
toa_v.start_vision_processing()

# Start the BaseAI
while True:
    user_message = input("You: ")
    if user_message.lower() in ["exit", "quit"]:
        break
    response = toa_b.chat_with_ai(user_message)
    print(f"Toa: {response}")