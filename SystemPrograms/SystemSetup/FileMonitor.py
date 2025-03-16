# File: FileMonitor.py
import os
import json
import time
import termcolor
import importlib
import sys

# Import AuthorizeFiles as a module
try:
    from SystemPrograms.SystemSetup import AuthorizeFiles
except ModuleNotFoundError:
    termcolor.cprint("❌ ERROR: Could not import AuthorizeFiles module!", "red")
    sys.exit(1)

from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[2]  # Moves up three levels
STATUS_FILE_PATH = os.path.join(BASE_PATH, "SystemFiles\\file_status.json")


class FileMonitor:
    def __init__(self):
        self.file_status = self.load_status_file()
        self.monitored_modules = {}

    def load_status_file(self):
        """Load file status from JSON if available"""
        if os.path.exists(STATUS_FILE_PATH):
            with open(STATUS_FILE_PATH, "r") as f:
                return json.load(f)
        return {}

    def get_enabled_modules(self):
        """Extract enabled module paths and convert them to importable module names"""
        enabled_modules = {}
        for path, status in self.file_status.items():
            if status == "enabled":
                module_name = self.get_module_name(path)
                if module_name:
                    enabled_modules[module_name] = path
        return enabled_modules

    def get_module_name(self, filepath):
        """Convert a file path to a Python module name"""
        if not filepath.endswith(".py"):
            return None

        relative_path = os.path.relpath(filepath, BASE_PATH).replace("\\", ".")
        module_name = relative_path[:-3]  # Remove .py extension

        return module_name if module_name.count(".") > 0 else None  # Ensure it's inside a package

    def import_or_reload_module(self, module_name):
        """Import or reload a module dynamically"""
        try:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                termcolor.cprint(f"🔄 Reloaded {module_name}", "cyan")
            else:
                sys.modules[module_name] = importlib.import_module(module_name)
                termcolor.cprint(f"✅ Imported {module_name}", "green")

            self.monitored_modules[module_name] = True
        except ModuleNotFoundError:
            termcolor.cprint(f"❌ ERROR importing {module_name}: Module not found!", "red")
            self.monitored_modules[module_name] = False
            self.run_authorize_files()
        except Exception as e:
            termcolor.cprint(f"❌ ERROR importing {module_name}: {e}", "red")
            self.monitored_modules[module_name] = False

    def unload_module(self, module_name):
        """Unload a module from sys.modules"""
        if module_name in sys.modules:
            del sys.modules[module_name]
            termcolor.cprint(f"🚫 Unloaded {module_name}", "yellow")
            self.monitored_modules.pop(module_name, None)

    def run_authorize_files(self):
        """Run AuthorizeFiles as an imported module to update file_status.json"""
        termcolor.cprint("🔄 Running AuthorizeFiles to verify and update files...", "yellow")

        # Instantiate and run AuthorizeFiles' validation
        auth_instance = AuthorizeFiles.AuthorizeFiles()
        auth_instance.verify_files()  # Ensure this updates file_status.json correctly
        auth_instance.verify_json_files()
        auth_instance.verify_program_files_syntax()
        auth_instance.verify_program_files_runtime()

        self.file_status = self.load_status_file()  # Reload updated statuses
        termcolor.cprint("✅ AuthorizeFiles completed!", "green")

    def start_monitoring(self):
        """Start monitoring enabled modules"""
        termcolor.cprint("📡 FileMonitor started...", "green")

        try:
            while True:
                self.file_status = self.load_status_file()
                enabled_modules = self.get_enabled_modules()

                # Handle new or re-enabled modules
                for module_name, path in enabled_modules.items():
                    if module_name not in self.monitored_modules or not self.monitored_modules[module_name]:
                        self.import_or_reload_module(module_name)

                # Handle disabled modules
                for module_name in list(self.monitored_modules.keys()):
                    if module_name not in enabled_modules:
                        self.unload_module(module_name)

                time.sleep(5)  # Check every 5 seconds
        except KeyboardInterrupt:
            termcolor.cprint("\n🛑 FileMonitor stopped by user.", "cyan")


if __name__ == "__main__":
    monitor = FileMonitor()
    monitor.start_monitoring()