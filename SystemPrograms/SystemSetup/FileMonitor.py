import os
import time
import termcolor
import importlib
import sys
import configparser
from pathlib import Path

# Import AuthorizeFiles as a module
try:
    from SystemPrograms.SystemSetup import AuthorizeFiles
except ModuleNotFoundError:
    termcolor.cprint("❌ ERROR: Could not import AuthorizeFiles module!", "red")
    sys.exit(1)

BASE_PATH = Path(__file__).resolve().parents[2]  # Moves up three levels
CONFIG_PATH = os.path.join(BASE_PATH, "SystemFiles", "config.cfg")


class FileMonitor:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.monitored_modules = {}
        self.load_config()

    def load_config(self):
        """Load file status from config.cfg."""
        if os.path.exists(CONFIG_PATH):
            self.config.read(CONFIG_PATH)
        else:
            termcolor.cprint("⚠️ WARNING: config.cfg not found!", "yellow")

    def get_enabled_modules(self):
        """Extract enabled module paths and convert them to importable module names."""
        enabled_modules = {}
        if "SystemFiles" in self.config:
            for filename, status in self.config["SystemFiles"].items():
                if status == "enabled":
                    file_path = self.find_file_path(filename)
                    module_name = self.get_module_name(file_path)
                    if module_name:
                        enabled_modules[module_name] = file_path
        return enabled_modules

    def find_file_path(self, filename):
        """Find the full path of a file in SystemPrograms."""
        for root, _, files in os.walk(os.path.join(BASE_PATH, "SystemPrograms")):
            if filename in files:
                return os.path.join(root, filename)
        return None

    def get_module_name(self, filepath):
        """Convert a file path to a Python module name."""
        if not filepath or not filepath.endswith(".py"):
            return None
        relative_path = os.path.relpath(filepath, BASE_PATH).replace(os.sep, ".")
        return relative_path[:-3]  # Remove .py extension

    def import_or_reload_module(self, module_name):
        """Import or reload a module dynamically."""
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
        """Unload a module from sys.modules."""
        if module_name in sys.modules:
            del sys.modules[module_name]
            termcolor.cprint(f"🚫 Unloaded {module_name}", "yellow")
            self.monitored_modules.pop(module_name, None)

    def run_authorize_files(self):
        """Run AuthorizeFiles as an imported module to update config.cfg."""
        termcolor.cprint("🔄 Running AuthorizeFiles to verify and update files...", "yellow")
        auth_instance = AuthorizeFiles.AuthorizeFiles()
        auth_instance.verify_files()
        auth_instance.verify_json_files()
        auth_instance.verify_program_files_syntax()
        auth_instance.verify_program_files_runtime()
        self.load_config()  # Reload updated statuses
        termcolor.cprint("✅ AuthorizeFiles completed!", "green")

    def start_monitoring(self):
        """Start monitoring enabled modules."""
        termcolor.cprint("📡 FileMonitor started...", "green")
        try:
            while True:
                self.load_config()
                enabled_modules = self.get_enabled_modules()

                for module_name, path in enabled_modules.items():
                    if module_name not in self.monitored_modules or not self.monitored_modules[module_name]:
                        self.import_or_reload_module(module_name)

                for module_name in list(self.monitored_modules.keys()):
                    if module_name not in enabled_modules:
                        self.unload_module(module_name)

                time.sleep(5)  # Check every 5 seconds
        except KeyboardInterrupt:
            termcolor.cprint("\n🛑 FileMonitor stopped by user.", "cyan")


if __name__ == "__main__":
    monitor = FileMonitor()
    monitor.start_monitoring()
