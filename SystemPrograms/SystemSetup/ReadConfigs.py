# File: ReadConfigs.py
import configparser
import os
from pathlib import Path

class ReadConfigs:
    def __init__(self):
        self.BASE_PATH = Path(__file__).resolve().parents[2]  # Moves up three levels
        self.CONFIG_PATH = os.path.join(self.BASE_PATH, "SystemFiles", "config.cfg")

        # Ensure config file exists
        if not os.path.exists(self.CONFIG_PATH):
            with open(self.CONFIG_PATH, "w") as f:
                f.write("")  # Create an empty config file

    def load_config(self):
        """Loads configuration from config.cfg"""
        config = configparser.ConfigParser()
        config.read(self.CONFIG_PATH)
        return config

    def get_file_path(self, config, file_name):
        """Finds the file path based on config sections"""
        for section in config.sections():
            if file_name in config[section]:
                # Get the status (enabled/disabled/etc.)
                status = config[section][file_name]
                if status.lower() in {"enabled", "not implemented", "disabled"}:
                    base_path = self.BASE_PATH
                    sub_path = section.replace("SystemPrograms.", "SystemPrograms/")  # Fix paths
                    sub_path = sub_path.replace("SystemFiles", "SystemFiles")  # Keep SystemFiles unchanged
                    return os.path.join(base_path, sub_path, file_name)
        return None

if __name__ == "__main__":
    app = ReadConfigs()
    config = app.load_config()

    file_to_find = "tokens.json"  # Change this to the file you want to find
    file_path = app.get_file_path(config, file_to_find)

    if file_path:
        print(f"File found: {file_path}")
    else:
        print("File not found in the configuration.")