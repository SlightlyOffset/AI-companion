import os
import sys
import time
from colorama import Fore, Style
from engines.actions import APPS    # Import the APPS dictionary
from engines.config import update_setting

def loading_spinner(stop_event, name):
    """Displays a loading spinner in the terminal."""
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(Fore.YELLOW + f"\r  {chars[i % len(chars)]} {name} is thinking..." + Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()

def is_command(user_input: str) -> bool:
    """Checks if the user is asking to open an app."""
    user_input = user_input.lower()
    return any(trigger in user_input for trigger in APPS.keys()) or "open" in user_input

def pick_profile() -> str:
    """Terminal-based profile picker."""
    profiles_dir = "profiles"
    if not os.path.exists(profiles_dir):
        print(Fore.RED + f"[ERROR] Profiles directory '{profiles_dir}' not found.")
        return None

    profiles = [f for f in os.listdir(profiles_dir) if f.endswith(".json")]

    if not profiles:
        print(Fore.RED + f"[ERROR] No .json profiles found in '{profiles_dir}'.")
        return None

    # If only one profile, just return it
    if len(profiles) == 1:
        return os.path.join(profiles_dir, profiles[0])

    print(Fore.YELLOW + Style.BRIGHT + "\n--- Select Your Companion Profile ---")
    for i, p in enumerate(profiles, 1):
        # Strip .json for display
        display_name = p.replace(".json", "").replace("_", " ").title()
        print(Fore.CYAN + f"  [{i}] {display_name}")

    while True:
        try:
            choice = input(Fore.YELLOW + "\nEnter the number of your choice: " + Style.RESET_ALL).strip()
            if not choice:
                continue

            idx = int(choice) - 1
            if 0 <= idx < len(profiles):
                selected = os.path.join(profiles_dir, profiles[idx])
                print(Fore.GREEN + f"Loading {profiles[idx]}...\n")
                return selected
            else:
                print(Fore.RED + "Invalid selection. Please try again.")
        except ValueError:
            print(Fore.RED + "Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n")
            return None

def app_commands(ops: str):
    """
    Execute operational commands like 'shutdown' or 'restart'.
    """

    def _help():
        for cmd in cmds.keys():
            print(Fore.CYAN + f"  {cmd}")

    def _enable_speak():
        print(Fore.GREEN + "[SYSTEM] Text-to-Speech enabled.")
        update_setting("tts_enabled", True)

    def _disable_speak():
        print(Fore.RED + "[SYSTEM] Text-to-Speech disabled.")
        update_setting("tts_enabled", False)

    cmds = {
        "//exit": sys.exit,
        "//quit": sys.exit,
        "//help": lambda: _help(),
        "//enable_speak": lambda: _enable_speak(),
        "//disable_speak": lambda: _disable_speak(),
    }

    action = cmds.get(ops.lower())
    if action:
        action()
        return True
    return False