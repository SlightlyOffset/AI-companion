"""
Helper utilities for terminal UI and file selection.
Provides selection menus for profiles and history files.
"""

import os
import re
from colorama import Fore, Style
from engines.actions import APPS

def is_command(user_input: str) -> bool:
    """
    Checks if the user input contains keywords that suggest a system command request.

    Args:
        user_input (str): The raw user input.

    Returns:
        bool: True if it looks like a command, False otherwise.
    """
    user_input = user_input.lower()
    return any(trigger in user_input for trigger in APPS.keys()) or "open" in user_input

def pick_profile() -> str:
    """
    Displays a terminal-based menu for picking a character profile.

    Returns:
        str: The path to the selected .json profile, or None.
    """
    profiles_dir = "profiles"
    if not os.path.exists(profiles_dir):
        print(Fore.RED + f"[ERROR] Profiles directory '{profiles_dir}' not found.")
        return None

    profiles = [f for f in os.listdir(profiles_dir) if f.endswith(".json")]
    if not profiles:
        print(Fore.RED + f"[ERROR] No .json profiles found in '{profiles_dir}'.")
        return None

    print(Fore.YELLOW + Style.BRIGHT + "\n--- Select Your Companion Profile ---")
    for i, p in enumerate(profiles, 1):
        display_name = p.replace(".json", "").replace("_", " ").title()
        print(Fore.CYAN + f"  [{i}] {display_name}")

    while True:
        try:
            choice = input(Fore.YELLOW + "\nEnter profile number: " + Style.RESET_ALL).strip()
            if not choice: continue
            idx = int(choice) - 1
            if 0 <= idx < len(profiles):
                selected = os.path.join(profiles_dir, profiles[idx])
                print(Fore.GREEN + f"Loading {profiles[idx]}...\n")
                return selected
            else:
                print(Fore.RED + "Invalid selection.")
        except ValueError:
            print(Fore.RED + "Please enter a valid number.")
        except KeyboardInterrupt:
            return None

def pick_user_profile() -> str:
    """
    Displays a terminal-based menu for picking a user profile.

    Returns:
        str: The path to the selected user .json profile, or None.
    """
    user_profiles_dir = "user_profiles"
    if not os.path.exists(user_profiles_dir):
        return None

    user_profiles = [f for f in os.listdir(user_profiles_dir) if f.endswith(".json")]
    if not user_profiles:
        return None

    print(Fore.YELLOW + Style.BRIGHT + "\n--- Select Your User Profile ---")
    for i, p in enumerate(user_profiles, 1):
        display_name = p.replace(".json", "").replace("_", " ").title()
        print(Fore.CYAN + f"  [{i}] {display_name}")

    while True:
        try:
            choice = input(Fore.YELLOW + "\nEnter user profile number: " + Style.RESET_ALL).strip()
            if not choice: continue
            idx = int(choice) - 1
            if 0 <= idx < len(user_profiles):
                return os.path.join(user_profiles_dir, user_profiles[idx])
            else:
                print(Fore.RED + "Invalid selection.")
        except ValueError:
            print(Fore.RED + "Please enter a valid number.")
        except KeyboardInterrupt:
            return None

def pick_history() -> str:
    """
    Displays a terminal-based menu for picking a conversation history file.

    Returns:
        str: The path to the selected history .json file, or None.
    """
    history_dir = "history"
    if not os.path.exists(history_dir):
        return None

    history_files = [f for f in os.listdir(history_dir) if f.endswith(".json")]
    if not history_files:
        return None

    print(Fore.YELLOW + Style.BRIGHT + "\n--- Select Conversation History ---")
    for i, h in enumerate(history_files, 1):
        display_name = h.replace(".json", "").replace("_", " ").title()
        print(Fore.CYAN + f"  [{i}] {display_name}")

    while True:
        try:
            choice = input(Fore.YELLOW + "\nEnter history number: " + Style.RESET_ALL).strip()
            if not choice: continue
            idx = int(choice) - 1
            if 0 <= idx < len(history_files):
                return os.path.join(history_dir, history_files[idx])
            else:
                print(Fore.RED + "Invalid selection.")
        except ValueError:
            print(Fore.RED + "Please enter a valid number.")
        except KeyboardInterrupt:
            return None

