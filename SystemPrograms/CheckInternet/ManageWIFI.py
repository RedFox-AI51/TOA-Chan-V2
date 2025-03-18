from pathlib import Path
from datetime import datetime

import socket
import threading
import pickle
import os
import speedtest
import psutil
import platform
import subprocess
import re

# Define base paths
BASE_PATH = Path(__file__).resolve().parents[2]  # Moves up three levels
SYSTEM_FILES_PATH = os.path.join(BASE_PATH, "SystemFiles")


class CheckWIFI:
    def __init__(self):
        self.log_message_format = "| Date: {} | Time: {} | Message: {}"
        self.log_path = os.path.join(SYSTEM_FILES_PATH, "wifi_log.pkl")
        self.__load_wifi_log__()

    def __load_wifi_log__(self):
        """Load existing WiFi logs or create a new log file."""
        if not os.path.exists(self.log_path):
            with open(self.log_path, "wb") as f:
                pickle.dump([], f)  # Initialize empty log
        with open(self.log_path, "rb") as f:
            try:
                self.wifi_log = pickle.load(f)
            except EOFError:
                self.wifi_log = []  # Handle empty file case

    def __save_to_log__(self, log_message):
        """Append a log entry to the log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = self.log_message_format.format(
            timestamp.split()[0], timestamp.split()[1], log_message
        )
        self.wifi_log.append(formatted_message)
        with open(self.log_path, "wb") as f:
            pickle.dump(self.wifi_log, f)

    def get_wifi_status(self):
        """Check if the system is connected to WiFi."""
        interfaces = psutil.net_if_addrs()
        for interface in interfaces:
            if "wlan" in interface.lower() or "wi-fi" in interface.lower():
                return True
        return False

    def get_wifi_strength(self):
        """Get WiFi signal strength (percentage for Windows, dBm for Linux)."""
        os_name = platform.system()

        if os_name == "Linux":
            try:
                output = subprocess.check_output("iwconfig 2>/dev/null", shell=True).decode()
                match = re.search(r"Signal level=(-?\d+) dBm", output)
                if match:
                    return f"{match.group(1)} dBm"
            except Exception:
                return "Unknown"

        elif os_name == "Windows":
            try:
                output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
                match = re.search(r"Signal\s*:\s*(\d+)", output)
                if match:
                    return f"{match.group(1)} %"
            except Exception:
                return "Unknown"

        return "Unknown"


if __name__ == "__main__":
    wifi_manager = CheckWIFI()
    
    wifi_connected = wifi_manager.get_wifi_status()
    wifi_strength = wifi_manager.get_wifi_strength() if wifi_connected else "N/A"

    print(f"WiFi Connected: {'Yes' if wifi_connected else 'No'}")
    print(f"WiFi Signal Strength: {wifi_strength}")

    # Log WiFi data
    log_msg = f"WiFi Status: {'Connected' if wifi_connected else 'Disconnected'}, Strength: {wifi_strength}"
    wifi_manager.__save_to_log__(log_msg)
