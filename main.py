# Standard library imports
import json
import threading
import random

# Third-party imports
from colorama import init, Fore, Style

# Local imports
from engines.actions import execute_command
from engines.utilities import is_command
from engines.utilities import pick_profile
from engines.utilities import loading_spinner
from engines.utilities import app_commands
from engines.responses import get_respond
from engines.tts_module import speak
# from engines.mood import is_command  ---> # Uncomment if using the mood engine

# Initialize colorama
init(autoreset=True)

# ---------------------------------
# NOTE1: Currently, 'mood' is not very much used.
# Future versions may expand on this.
# Or delete it entirely.
# ---------------------------------
# NOTE2: Command fucntionality is basic. And brittle.
# Future versions may include more robust NLP parsing
# Or a command registry.
# ---------------------------------

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
    print(Fore.YELLOW + "Type '//help' for a list of commands.\n")

    while True:
        try:
            user_input = input(Fore.CYAN + Style.BRIGHT + "You: " + Style.RESET_ALL).strip()
            if not user_input: continue
            if user_input.startswith("//"):
                if app_commands(user_input): continue

            is_cmd = is_command(user_input)

            # Weight lookup
            good_w = profile.get("good_weight", 5)
            bad_w = profile.get("bad_weight", 5)

            mood = random.choices(["good", "bad"],
                                  weights=[good_w, bad_w],
                                  k=1)[0]
            should_obey = (mood == "good")

            # Instant Action: Execute if obedient before AI starts thinking
            ai_input = user_input
            if is_cmd and should_obey:
                success, message = execute_command(user_input)
                print(Fore.GREEN + f"[SYSTEM] {message}")
                # Add a hidden instruction for conciseness
                ai_input += " (IMPORTANT: The task is already done. Keep your response very brief.)"

            # Spinner and LLM Response
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=loading_spinner, args=(stop_event, name))
            spinner_thread.start()

            try:
                response = get_respond(ai_input, profile, should_obey=should_obey, profile_path=profile_path)
            finally:
                stop_event.set()
                spinner_thread.join()

            # Print response
            colors = profile.get("colors", {})
            text_color_name = colors.get("text", "WHITE").upper()
            text_style = getattr(Fore, text_color_name, Fore.WHITE)

            print(Fore.WHITE + Style.DIM + "-" * 30)
            print(Fore.MAGENTA + Style.BRIGHT + f"{name}: " + Style.NORMAL + text_style + response + "\n")

            # Get TTS preference from profile
            tts_pref = profile.get("preferred_tts_voice", None)
            speak(response, pref_tts=tts_pref)

            # System message for refusal
            if is_cmd and not should_obey:
                print(Fore.RED + f"[SYSTEM] {name} refused to help.")

            print(Fore.WHITE + Style.DIM + "-" * 30)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(Fore.RED + f"\n[ERROR] {e}")

if __name__ == "__main__":
    main()
