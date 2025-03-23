# File: AuthorizeFiles.py
import termcolor
import json
import os
import py_compile
import subprocess
import configparser
from datetime import datetime
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[2]  # Moves up three levels
SYSTEM_FILES_PATH = os.path.join(BASE_PATH, "SystemFiles")
SYSTEM_PROGRAMS_PATH = os.path.join(BASE_PATH, "SystemPrograms")
CONFIG_PATH = os.path.join(BASE_PATH, "SystemFiles", "config.cfg")  # Config file
TEMP_CONFIG_PATH = os.path.join(BASE_PATH, "SystemFiles", "temp", "config.cfg")

SKIP_FILES = {"AuthorizeFiles.py", "FileMonitor.py"}  # Skip these files
SKIP_DIR = {os.path.join(BASE_PATH, "SystemPrograms", "SystemSetup")}

class AuthorizeFiles:
    def __init__(self, sys_files=SYSTEM_FILES_PATH, program_files=SYSTEM_PROGRAMS_PATH):
        self.sys_files = sys_files
        self.program_files = program_files
        self.verified_sys_files = []
        self.passed_files = []  # Track files that pass syntax
        self.config = configparser.ConfigParser()
        self.load_config()
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)

    def load_config(self, path=TEMP_CONFIG_PATH):
        """Load configuration from the cfg file."""
        if os.path.exists(path):
            self.config.read(path)
        else:
            self.config = configparser.ConfigParser()

    def save_config(self, path=TEMP_CONFIG_PATH):
        """Save updated file statuses back to config.cfg."""
        with open(path, "w") as configfile:
            self.config.write(configfile)

    def set_file_status(self, section, filename, status):
        """Set file status in the config file."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][filename] = status
        self.save_config()

    def verify_files(self):
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
        termcolor.cprint("DEBUG: Checking System Files", "red")
        for dirpath, _, filenames in os.walk(self.sys_files):
            section = os.path.relpath(dirpath, BASE_PATH).replace(os.sep, ".")
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                termcolor.cprint(f"Verified [ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} ]: {filename} @ {filepath}", "green")
                self.verified_sys_files.append(filepath)
                self.set_file_status("SystemFiles", filename, "enabled")

    def verify_json_files(self):
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
        """Check JSON file formatting"""
        termcolor.cprint("\nDEBUG: Checking JSON Files", "red")
        for filepath in self.verified_sys_files:
            if filepath.endswith(".json"):
                termcolor.cprint(f"Checking JSON -> {filepath}", "yellow")
                filename = os.path.basename(filepath)
                try:
                    with open(filepath, "r") as f:
                        json.load(f)  # Ensure it's valid JSON
                    termcolor.cprint(f"Valid JSON: {filepath}", "green")
                    self.set_file_status("SystemFiles", filename, "enabled")
                except json.JSONDecodeError:
                    termcolor.cprint(f"Invalid JSON: {filepath}", "red")
                    self.set_file_status("SystemFiles", filename, "disabled")

    def verify_program_files_syntax(self):
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
        termcolor.cprint("\nDEBUG: Checking System Program Syntax", "red")
        for dirpath, _, filenames in os.walk(self.program_files):
            section = os.path.relpath(dirpath, BASE_PATH).replace(os.sep, ".")
            for filename in filenames:
                if dirpath in SKIP_DIR or filename in SKIP_FILES:
                    termcolor.cprint(f"⚠️ Skipping {filename} (manual exclusion)", "yellow")
                    self.set_file_status(section, filename, "not implemented")
                    continue
                if filename.endswith(".py"):
                    filepath = os.path.join(dirpath, filename)
                    termcolor.cprint(f"[{datetime.now().strftime(r'%m/%d/%Y %H:%M:%S')}] Checking syntax -> {filepath}", "yellow")
                    try:
                        py_compile.compile(filepath, doraise=True)
                        termcolor.cprint(f"Syntax OK: {filename}", "green")
                        self.passed_files.append(filepath)
                        self.set_file_status(section, filename, "enabled")
                    except py_compile.PyCompileError:
                        termcolor.cprint(f"Syntax ERROR: {filename}", "red")
                        self.set_file_status(section, filename, "disabled")

    def verify_program_files_runtime(self):
        termcolor.cprint("\nDEBUG: Checking System Program Runtime", "red")
        for filepath in self.passed_files:
            if os.path.exists(CONFIG_PATH):
                os.remove(CONFIG_PATH)
            filename = os.path.basename(filepath)
            section = os.path.relpath(os.path.dirname(filepath), BASE_PATH).replace(os.sep, ".")

            # Convert file path to module name
            module_name = os.path.relpath(filepath, BASE_PATH).replace(os.sep, ".").replace(".py", "")

            termcolor.cprint(f"Running -> {filename} as {module_name}", "yellow")
            try:
                result = subprocess.run(["python", "-m", module_name], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    termcolor.cprint(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] Runtime OK: {filename}", "green")
                    self.set_file_status(section, filename, "enabled")
                else:
                    termcolor.cprint(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] Runtime ERROR: {filename} | ERROR: {result.stderr}", "red")
                    self.set_file_status(section, filename, "disabled")
            except subprocess.TimeoutExpired:
                termcolor.cprint(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] Timeout ERROR: {filename}", "red")
                self.set_file_status(section, filename, "disabled")
            except Exception as e:
                termcolor.cprint(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] Unexpected ERROR: {e}", "red")
                self.set_file_status(section, filename, "disabled")
        self.certify_the_config_file()

    def certify_the_config_file(self):
        with open(TEMP_CONFIG_PATH, "r") as temp:
            data = temp.read()
            temp.close()
        
        os.remove(TEMP_CONFIG_PATH)

        with open(CONFIG_PATH, "w") as config:
            config.write(data)
            config.close()
        

if __name__ == "__main__":
    app = AuthorizeFiles()
    app.verify_files()
    app.verify_json_files()
    app.verify_program_files_syntax()
    app.verify_program_files_runtime()
