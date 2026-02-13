"""
Internal CLI command handler for the application.
Processes commands starting with '//' to manage settings, history, and app state.
"""

import sys
import os
import json
from colorama import Fore, init
from engines.config import update_setting, get_setting
from engines.utilities import pick_history
from engines.utilities import pick_profile
from engines.utilities import pick_user_profile

# Initialize colorama
init(autoreset=True)

# Path to conversation history files
HISTORY_PATH = "history/"

class RestartRequested(Exception):
    """Exception raised to signal the main loop to restart the application."""
    pass

def app_commands(ops: str):
    """
    Dispatcher for internal operational commands.

    Args:
        ops (str): The raw command input (e.g., '//help').

    Returns:
        bool: True if the command was recognized and handled, False otherwise.
    """

    def _help():
        """Lists all available commands."""
        print(Fore.YELLOW + "[AVAILABLE COMMANDS]")
        for cmd in cmds.keys():
            print(Fore.CYAN + f"  {cmd}")

    def _show_settings():
        """Displays current system settings from settings.json."""
        from engines.config import load_settings
        settings = load_settings()
        print(Fore.YELLOW + "[CURRENT SETTINGS]")
        for key, value in settings.items():
            # Color-code booleans for readability
            val_str = Fore.GREEN + str(value) if isinstance(value, bool) and value else \
                      Fore.RED + str(value) if isinstance(value, bool) else \
                      Fore.WHITE + str(value)
            print(Fore.CYAN + f"  {key}: " + val_str)

    def _toggle_narration():
        is_enabled = get_setting("speak_narration", False)
        print(Fore.GREEN + "[SYSTEM] Narration enabled." if not is_enabled else Fore.RED + "[SYSTEM] Narration disabled.")
        update_setting("speak_narration", not is_enabled)

    def _toggle_speak():
        is_enabled = get_setting("tts_enabled", True)
        print(Fore.GREEN + "[SYSTEM] Text-to-Speech enabled." if not is_enabled else Fore.RED + "[SYSTEM] Text-to-Speech disabled.")
        update_setting("tts_enabled", not is_enabled)

    def _toggle_command():
        is_enabled = get_setting("execute_command", False)
        print(Fore.GREEN + "[SYSTEM] Command execution enabled." if not is_enabled else Fore.RED + "[SYSTEM] Command execution disabled.")
        update_setting("execute_command", not is_enabled)

    def _reset():
        """Wipes a specific history file chosen by the user."""
        print(Fore.YELLOW + "[SYSTEM] Conversation history reset.")
        history_path = pick_history()
        if history_path:
            with open(history_path, "w", encoding="UTF-8") as f:
                json.dump([], f)
            print(Fore.GREEN + "[SYSTEM] History cleared.")
        else:
            print(Fore.RED + "[SYSTEM] No history selected.")

    def _reset_all():
        """Wipes ALL history files in the history directory."""
        confirm = input(Fore.RED + "Are you sure you want to reset ALL history files? (y/n): ").strip().lower()
        if confirm == 'y':
            for filename in os.listdir(HISTORY_PATH):
                if filename.endswith(".json"):
                    file_path = os.path.join(HISTORY_PATH, filename)
                    with open(file_path, "w", encoding="UTF-8") as f:
                        json.dump([], f)
            print(Fore.GREEN + "[SYSTEM] All history files have been wiped.")
        else:
            print(Fore.YELLOW + "[SYSTEM] Reset cancelled.")

    def _reset_rel():
        """Resets the relationship score of a chosen profile to zero."""
        profile_path = pick_profile()
        if profile_path:
            with open(profile_path, "r+", encoding="UTF-8") as f:
                profile_data = json.load(f)
                profile_data["relationship_score"] = 0
                f.seek(0)
                json.dump(profile_data, f, indent=4)
                f.truncate()
            print(Fore.GREEN + "[SYSTEM] Relationship score reset to 0.")
        else:
            print(Fore.RED + "[SYSTEM] No profile selected.")

    def _restart():
        """Signals the main loop to restart."""
        print(Fore.YELLOW + "[SYSTEM] Restarting application...")
        raise RestartRequested()

    def _clear():
        """Clears the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.YELLOW + "[SYSTEM] Screen cleared.")

    def _change_character():
        """Restarts the app to allow picking a new character."""
        print(Fore.YELLOW + "[SYSTEM] Changing character...")
        raise RestartRequested()

    def _change_user_profile():
        """Prompts for a new user profile and restarts."""
        print(Fore.YELLOW + "[SYSTEM] Changing user profile.")
        new_profile_path = pick_user_profile()
        if new_profile_path:
            new_profile_name = os.path.basename(new_profile_path)
            update_setting("current_user_profile", new_profile_name)
            print(Fore.GREEN + f"[SYSTEM] User profile changed to {new_profile_name}. Restarting...")
            raise RestartRequested()
        else:
            print(Fore.RED + "[SYSTEM] No user profile selected.")

    def _toggle_clear_at_start():
        is_enabled = get_setting("clear_at_start", True)
        print(Fore.GREEN + "[SYSTEM] Console will now clear at startup." if not is_enabled else Fore.RED + "[SYSTEM] Console will no longer clear at startup.")
        update_setting("clear_at_start", not is_enabled)

    # Mapping of command strings to their respective functions
    cmds = {
        "//exit": sys.exit,
        "//quit": sys.exit,
        "//help": _help,
        "//clear": _clear,
        "//change_character": _change_character,
        "//change_user_profile": _change_user_profile,
        "//reset": _reset,
        "//reset_all": _reset_all,
        "//reset_rel": _reset_rel,
        "//restart": _restart,
        "//toggle_speak": _toggle_speak,
        "//toggle_narration": _toggle_narration,
        "//toggle_command": _toggle_command,
        "//toggle_clear_at_start": _toggle_clear_at_start,
        "//show_settings": _show_settings,
    }

    action = cmds.get(ops.lower())
    if action:
        action()
        return True
    return False
