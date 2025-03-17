from SystemPrograms.VoiceGeneration.VoiceSynthesis import Voice

from SystemPrograms import SystemSetup

import threading
import datetime
import time

SystemSetup.InitializeSystem()

TEXT_TO_SPEAK = "Hi, I'm Toa chan"
tts = Voice()
tts.generate_audio(text=TEXT_TO_SPEAK)
tts.play_audio()