import sys
import json
from colorama import Fore, init
from engines.config import update_setting
from engines.utilities import pick_history

# Chat history path
HISTORY_PATH = "history/"

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
                f.write("")
            print(Fore.GREEN + "[SYSTEM] History cleared.")
        else:
            print(Fore.RED + "[SYSTEM] No history selected.")

    cmds = {
        "//exit": sys.exit,
        "//quit": sys.exit,
        "//help": lambda: _help(),
        "//reset": lambda: _reset(),
        "//enable_speak": lambda: _enable_speak(),
        "//disable_speak": lambda: _disable_speak(),
        "//enable_command": lambda: _enable_command(),
        "//disable_command": lambda: _disable_command(),
    }

    action = cmds.get(ops.lower())
    if action:
        action()
        return True
    return False