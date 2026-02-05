import json
import threading
import time
import sys
from actions import execute_command
from colorama import init, Fore, Style
from responses.responses import get_respond

# Initialize colorama
init(autoreset=True)

def load_profile(profile_name):
    with open(f"profiles/{profile_name}.json", "r") as f:
        return json.load(f)

def loading_spinner(stop_event):
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(Fore.YELLOW + f"\r  {chars[i % len(chars)]} Glitch is thinking..." + Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()

def main():
    # Load character
    profile = load_profile("sassy_companion")
    name = profile["name"]

    print(Fore.YELLOW + Style.BRIGHT + f"--- {name} Desktop Companion Loaded ---")
    print(Fore.YELLOW + "Commands: 'open browser', 'open notepad', etc. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input(Fore.CYAN + Style.BRIGHT + "You: " + Style.RESET_ALL).strip()

            if not user_input: continue
            if user_input.lower() in ["exit", "quit"]: break

            # Mood logic
            from engines.mood import is_command
            import random

            is_cmd = is_command(user_input)
            mood = random.choices(["sass", "obedient"],
                                  weights=[profile["sass_weight"],
                                  profile["obedient_weight"]], k=1)[0]
            should_obey = (mood == "obedient")

            # Spinner and LLM Response
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=loading_spinner, args=(stop_event,))
            spinner_thread.start()

            try:
                response = get_respond(mood, user_input, profile)
            finally:
                stop_event.set()
                spinner_thread.join()

            print(Fore.MAGENTA + Style.BRIGHT + f"{name}: " + Style.NORMAL + response + "\n")

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
