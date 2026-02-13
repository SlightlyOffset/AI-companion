import subprocess


# This is your "App Dictionary"
APPS = {
    "browser": "chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "discord": "discord.exe",
}

def execute_command(command: str):
    """
    Attempts to find and launch an app based on the user's command.
    """

    command = command.lower()

    for trigger, exe in APPS.items():
        if trigger in command:
            try:
                # Start the process without blocking our script
                subprocess.Popen(exe, shell=True)
                return True, f"Launching {trigger}..."
            except Exception as e:
                return False, f"I tried to open {trigger}, but I failed. Typical. (Error: {e})"

    return False, "I have no idea what you want me to open. Try being more specific?"
