import subprocess
import threading
import time
import os
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[2]  # Moves up three levels

class TerminalManager:
    def __init__(self):
        self.terminal_threads = []  # List to keep track of running terminals
    
    def open_terminal(self):
        """
        Opens a new terminal at the specified path and runs it in a new thread.
        """
        path = BASE_PATH
        if not os.path.exists(path):
            print(f"Error: Path '{path}' does not exist.")
            return
        
        thread = threading.Thread(target=self._start_terminal, args=(path,), daemon=True)
        thread.start()
        self.terminal_threads.append(thread)
        print(f"Terminal started at {path}")
    
    def _start_terminal(self, path):
        """
        Runs the terminal process at the given path.
        """
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'start cmd.exe /K "cd /d {path} && python -c "import time; from SystemPrograms import SystemSetup; SystemSetup.InitializeSystem()""', shell=True)
        else:  # Linux/macOS
            subprocess.Popen(['x-terminal-emulator', '--working-directory', path])
    
    def list_active_terminals(self):
        """
        Lists the number of active terminal threads.
        """
        return len(self.terminal_threads)

# Example usage
if __name__ == "__main__":
    manager = TerminalManager()
    print(f"Active terminals: {manager.list_active_terminals()}")
