from SystemPrograms.VoiceGeneration.VoiceSynthesis import Voice
from SystemPrograms.VoiceRecognition.VoiceDetection import SpeechRecognizer

from SubprocessTerminal import TerminalManager

import threading
import datetime
import time

setup = TerminalManager()
setup.open_terminal

recognizer = SpeechRecognizer()
recognizer.recognize_speech()

TEXT_TO_SPEAK = "Hi, I'm Toa chan"
tts = Voice()
tts.generate_audio(text=TEXT_TO_SPEAK)
tts.play_audio()