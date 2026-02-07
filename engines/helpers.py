import re
import os
import sys
import time
import socket
from colorama import Fore, Style
from engines.actions import APPS    # Import the APPS dictionary

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

def is_online(host="8.8.8.8", port=53, timeout=3):
    """
    Check internet connectivity by attempting to connect to a DNS server.

    Args:
        host (str): Host to connect to (default: Google's DNS 8.8.8.8)
        port (int): Port number (default: 53 for DNS)
        timeout (int): Timeout in seconds

    Returns:
        bool: True if connected, False otherwise
    """
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
        return True
    except (socket.timeout, socket.error):
        return False

def clean_text_for_tts(text: str) -> str:
    """
    Removes text between asterisks (usually actions/narration in RP)
    so they aren't spoken out loud.
    """
    # Remove text inside *asterisks*
    cleaned = re.sub(r'\*.*?\*', '', text)
    # Remove double spaces left behind
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned




