"""
Handles the execution of system-level commands triggered by the AI.
Maps user intent (e.g., 'open browser') to local executable paths.
"""

import subprocess

# App Dictionary: Maps keywords to local executable paths or commands
# Add your own apps here following the same format
APPS = {
    "browser": "chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "discord": "discord.exe",
}

def execute_command(command: str):
    """
    Scans the user input for keywords and attempts to launch the corresponding application.
    
    Args:
        command (str): The raw user input string.
        
    Returns:
        tuple: (bool success, str message)
    """
    command = command.lower()

    for trigger, exe in APPS.items():
        if trigger in command:
            try:
                # Start the process without blocking the main script
                subprocess.Popen(exe, shell=True)
                return True, f"Launching {trigger}..."
            except Exception as e:
                # Failed to launch (e.g., executable not found in PATH)
                return False, f"I tried to open {trigger}, but I failed. (Error: {e})"

    return False, "I have no idea what you want me to open. Try being more specific?"
