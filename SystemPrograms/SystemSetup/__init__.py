from SystemPrograms.SystemSetup.AuthorizeFiles import AuthorizeFiles
from SystemPrograms.SystemSetup.FileMonitor import FileMonitor
from SystemPrograms.SystemSetup.ReadConfigs import ReadConfigs
import threading
import termcolor


def InitializeSystem():
    """Initialize system by verifying files and starting monitoring."""
    app = AuthorizeFiles()

    try:
        app.verify_files()
        app.verify_json_files()
        app.verify_program_files_syntax()
        app.verify_program_files_runtime()
    except Exception as e:
        termcolor.cprint(f"❌ ERROR during system verification: {e}", "red")

    # Start FileMonitor in a separate thread to prevent blocking
    monitor = FileMonitor()
    monitor_thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
    monitor_thread.start()

    termcolor.cprint("✅ System Initialization Complete!", "green")
