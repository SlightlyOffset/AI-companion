import sys
import os
import json
from colorama import Fore, init
from engines.config import update_setting
from engines.utilities import pick_history
from engines.utilities import pick_profile
from engines.utilities import pick_user_profile

# Initialize colorama
init(autoreset=True)


# Chat history path
HISTORY_PATH = "history/"

class RestartRequested(Exception):
    pass

def app_commands(ops: str):
    """
    Execute operational commands like 'reset' or 'restart'.
    """

    def _help():
        for cmd in cmds.keys():
            print(Fore.CYAN + f"  {cmd}")

    def _show_settings():
        from engines.config import load_settings
        settings = load_settings()
        print(Fore.YELLOW + "[CURRENT SETTINGS]")
        for key, value in settings.items():
            print(Fore.CYAN + f"  {key}" + ": " + (Fore.GREEN + str(value)\
                if isinstance(value, bool) and value else Fore.RED + str(value)\
                if isinstance(value, bool) else Fore.WHITE + str(value)))

    def _enable_speak():
        print(Fore.GREEN + "[SYSTEM] Text-to-Speech enabled.")
        update_setting("tts_enabled", True)

    def _disable_speak():
        print(Fore.RED + "[SYSTEM] Text-to-Speech disabled.")
        update_setting("tts_enabled", False)

    def _enable_command():
        print(Fore.GREEN + "[SYSTEM] Command execution enabled.")
        update_setting("execute_command", True)

    def _disable_command():
        print(Fore.RED + "[SYSTEM] Command execution disabled.")
        update_setting("execute_command", False)

    def _reset():
        print(Fore.YELLOW + "[SYSTEM] Conversation history reset.")
        history_path = pick_history()
        if history_path:
            with open(history_path, "w", encoding="UTF-8") as f:
                json.dump([], f)
            print(Fore.GREEN + "[SYSTEM] History cleared.")
        else:
            print(Fore.RED + "[SYSTEM] No history selected.")

    def _reset_all():
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
        print(Fore.YELLOW + "[SYSTEM] Restarting application...")
        raise RestartRequested()

    def _clear():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.YELLOW + "[SYSTEM] Screen cleared.")

    def _change_character():
        print(Fore.YELLOW + "[SYSTEM] Changing character...")
        raise RestartRequested()

    def _change_user_profile():
        print(Fore.YELLOW + "[SYSTEM] Changing user profile.")
        new_profile_path = pick_user_profile()
        if new_profile_path:
            new_profile_name = os.path.basename(new_profile_path)
            update_setting("current_user_profile", new_profile_name)
            print(Fore.GREEN + f"[SYSTEM] User profile changed to {new_profile_name}. Restarting...")
            raise RestartRequested()
        else:
            print(Fore.RED + "[SYSTEM] No user profile selected.")

    cmds = {
        "//exit": sys.exit,
        "//quit": sys.exit,
        "//help": lambda: _help(),
        "//clear": lambda: _clear(),
        "//change_character": lambda: _change_character(),
        "//change_user_profile": lambda: _change_user_profile(),
        "//reset": lambda: _reset(),
        "//reset_all": lambda: _reset_all(),
        "//reset_rel": lambda: _reset_rel(),
        "//restart": lambda: _restart(),
        "//enable_speak": lambda: _enable_speak(),
        "//disable_speak": lambda: _disable_speak(),
        "//enable_command": lambda: _enable_command(),
        "//disable_command": lambda: _disable_command(),
        "//show_settings": lambda: _show_settings(),
    }

    action = cmds.get(ops.lower())
    if action:
        action()
        return True
    return False