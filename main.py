# Standard library imports
import json
import threading
import time
import sys
import random

# Third-party imports
from colorama import init, Fore, Style

# Local imports
from engines.actions import execute_command
from engines.helpers import is_command, pick_profile
from engines.helpers import loading_spinner
from responses.responses import get_respond
from engines.tts_module import speak
# from engines.mood import is_command  ---> # Uncomment if using the mood engine

# Initialize colorama
init(autoreset=True)

def load_profile(profile_path):
    with open(profile_path, "r", encoding="UTF-8") as f:
        return json.load(f)

def main():
    # Load character
    profile_path = pick_profile()
    if not profile_path:
        print(Fore.RED + "No profile selected or found. Exiting.")
        return

    profile = load_profile(profile_path)
    name = profile["name"]

    print(Fore.YELLOW + Style.BRIGHT + f"--- {name} Desktop Companion Loaded ---")
    print(Fore.YELLOW + "Commands: 'open browser', 'open notepad', etc. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input(Fore.CYAN + Style.BRIGHT + "You: " + Style.RESET_ALL).strip()

            if not user_input: continue
            if user_input.lower() in ["exit", "quit"]: break

            is_cmd = is_command(user_input)
            
            # Robust weight lookup
            good_w = profile.get("good_weight") or profile.get("obedient_weight") or 5
            bad_w = profile.get("bad_weight") or profile.get("sass_weight") or 5
            
            mood = random.choices(["good", "bad"],
                                  weights=[good_w, bad_w],
                                  k=1)[0]
            should_obey = (mood == "good")

            # Spinner and LLM Response
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=loading_spinner, args=(stop_event, name))
            spinner_thread.start()

            try:
                response = get_respond(mood, user_input, profile, should_obey=should_obey)
            finally:
                stop_event.set()
                spinner_thread.join()

            # Print response
            colors = profile.get("colors", {})
            text_color_name = colors.get("text", "WHITE").upper()
            text_style = getattr(Fore, text_color_name, Fore.WHITE)

            print(Fore.WHITE + Style.DIM + "-" * 30)
            print(Fore.MAGENTA + Style.BRIGHT + f"{name}: " + Style.NORMAL + text_style + response + "\n")

            # Play TTS
            speak(response)

            if is_cmd:
                if should_obey:
                    success, message = execute_command(user_input)
                    print(Fore.GREEN + f"[SYSTEM] {message}")
                else:
                    print(Fore.RED + f"[SYSTEM] {name} refused to help.")

            print(Fore.WHITE + Style.DIM + "-" * 30)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(Fore.RED + f"\n[ERROR] {e}")

if __name__ == "__main__":
    main()
