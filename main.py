# Standard library imports
import json
import threading
import random
import queue
import re
import os
import time

# Third-party imports
from colorama import init, Fore, Style

# Local imports
from engines.actions import execute_command
from engines.utilities import is_command
from engines.utilities import pick_profile, pick_user_profile
from engines.app_commands import app_commands, RestartRequested
from engines.responses import get_respond_stream, apply_mood_decay
from engines.tts_module import generate_audio, play_audio, clean_text_for_tts
from engines.config import update_setting

# Initialize colorama
init(autoreset=True)

# Clearing the console
os.system('cls' if os.name == 'nt' else 'clear')

# Config path
CONFIG_PATH = "settings.json"

def load_profile(profile_path):
    with open(profile_path, "r", encoding="UTF-8") as f:
        return json.load(f)

# TTS Queues for pipelined streaming
tts_text_queue = queue.Queue()
audio_file_queue = queue.Queue()

def tts_generation_worker(tts_pref):
    """Worker thread to generate MP3s from text segments."""
    while True:
        text = tts_text_queue.get()
        if text is None:
            audio_file_queue.put(None)
            break

        # Unique filename to avoid collisions
        temp_dir = os.environ.get("TEMP", "/tmp")
        temp_filename = os.path.join(temp_dir, f"tts_{time.time()}_{random.randint(1000,9999)}.mp3")

        if generate_audio(text, temp_filename, voice=tts_pref):
            audio_file_queue.put(temp_filename)
        tts_text_queue.task_done()

def tts_playback_worker():
    """Worker thread to play generated MP3s in order."""
    while True:
        filename = audio_file_queue.get()
        if filename is None:
            break

        play_audio(filename)
        audio_file_queue.task_done()

def run_app():
    # Load character
    character_profile_path = pick_profile()
    if not character_profile_path:
        print(Fore.RED + "No profile selected or found. Exiting.")
        return

    character_profile = load_profile(character_profile_path)
    ch_name = character_profile["name"]

    # Load user profile
    user_profile_path = pick_user_profile()
    if user_profile_path:
        user_profile = load_profile(user_profile_path)
        user_name = user_profile.get("name", "User")
        user_filename = os.path.basename(user_profile_path)
        update_setting("current_user_profile", user_filename)
    else:
        user_name = "User"

    print(Fore.YELLOW + Style.BRIGHT + f"--- {ch_name} Desktop Companion Loaded ---")
    print(Fore.YELLOW + "Type '//help' for a list of commands.\n")
    print(Fore.YELLOW + Style.DIM + "[ NOTICE ]: This is an early build. Expect some quirks and crashes. Feedback is appreciated!")
    print(Fore.YELLOW + Style.DIM + "[ NOTICE ]: Take everything the AI says with a grain of salt! It may produce incorrect or nonsensical responses.\n")

    while True:
        try:
            with open(CONFIG_PATH, "r", encoding="UTF-8") as f:
                config = json.load(f)

            profile_data = load_profile(character_profile_path)
            tts_pref = profile_data.get("preferred_tts_voice", None)

            decayed_points, new_score = apply_mood_decay(character_profile_path, ch_name) or (0, 0)
            if decayed_points > 0:
                print(Fore.YELLOW + Style.DIM + f"  (Time has passed... {ch_name}'s feelings have shifted. New Score: {new_score})")

            gen_thread = threading.Thread(target=tts_generation_worker, args=(tts_pref,))
            play_thread = threading.Thread(target=tts_playback_worker)
            gen_thread.daemon = True
            play_thread.daemon = True
            gen_thread.start()
            play_thread.start()

            user_input = input(Fore.CYAN + Style.BRIGHT + f"{user_name}: " + Style.RESET_ALL).strip()
            if not user_input:
                tts_text_queue.put(None)
                gen_thread.join()
                play_thread.join()
                continue

            if user_input.startswith("//"):
                if app_commands(user_input):
                    tts_text_queue.put(None)
                    gen_thread.join()
                    play_thread.join()
                    continue
                else:
                    print(Fore.RED + "[SYSTEM] Unknown command. Type '//help' for a list of commands.")
                    tts_text_queue.put(None)
                    gen_thread.join()
                    play_thread.join()
                    continue

            should_obey = None
            system_extra_info = None
            if is_command(user_input):
                if config.get("execute_command", False):
                    relationship_score = profile_data.get("relationship_score", 0)
                    rel_mod = relationship_score / 10.0
                    good_w = profile_data.get("good_weight", 5)
                    bad_w = profile_data.get("bad_weight", 5)
                    adj_good_w = max(0.1, good_w + rel_mod)
                    adj_bad_w = max(0.1, bad_w - rel_mod)
                    mood = random.choices(["good", "bad"], weights=[adj_good_w, adj_bad_w], k=1)[0]
                    should_obey = (mood == "good")

                    if should_obey:
                        success, message = execute_command(user_input)
                        print(Fore.GREEN + f"[SYSTEM] {message}")
                        system_extra_info = "The task you were asked to do is already complete. Keep your response very brief."
                else:
                    print(Fore.YELLOW + "[SYSTEM] Command execution is disabled in settings.")
                    continue

            colors = profile_data.get("colors", {})
            text_color_name = colors.get("text", "WHITE").upper()
            text_style = getattr(Fore, text_color_name, Fore.WHITE)

            print(Fore.WHITE + Style.DIM + "-" * 30)
            print(Fore.MAGENTA + Style.BRIGHT + f"{ch_name}: " + Style.NORMAL + text_style, end="", flush=True)

            full_response = ""
            current_sentence = ""
            in_narration = False
            narration_style = Fore.BLACK + Style.BRIGHT

            for chunk in get_respond_stream(user_input, profile_data, should_obey=should_obey, profile_path=character_profile_path, system_extra_info=system_extra_info):
                for char in chunk:
                    if char == '*':
                        in_narration = not in_narration
                        print(narration_style + char if in_narration else char + text_style, end="", flush=True)
                    else:
                        print(char, end="", flush=True)

                full_response += chunk
                current_sentence += chunk

                # IMPORTANT: Only split for TTS if all narration blocks are closed (even number of asterisks)
                # and we hit a punctuation/newline OR the buffer is getting very long.
                num_asterisks = current_sentence.count('*')
                is_balanced = (num_asterisks % 2 == 0)

                if (any(punct in chunk for punct in ".!?\n") or len(current_sentence) > 100) and is_balanced:
                    parts = re.split(r'(?<=[.!?\n])', current_sentence)
                    for i in range(len(parts) - 1):
                        segment = parts[i].strip()
                        if segment:
                            cleaned = clean_text_for_tts(segment)
                            if cleaned:
                                tts_text_queue.put(cleaned)
                    current_sentence = parts[-1]

            # Final leftover text
            if current_sentence.strip():
                # Clean out potential metadata tags first
                clean_leftover = re.sub(r'\[REL:\s*[+-]?\d+\]', '', current_sentence).strip()
                cleaned = clean_text_for_tts(clean_leftover)
                if cleaned:
                    tts_text_queue.put(cleaned)

            print("\n")
            if is_command(user_input) and not should_obey:
                print(Fore.RED + f"[SYSTEM] {ch_name} refused to help.")

            print(Fore.WHITE + Style.DIM + "-" * 30)
            tts_text_queue.put(None)
            gen_thread.join()
            play_thread.join()

        except (KeyboardInterrupt, RestartRequested):
            raise
        except Exception as e:
            print(Fore.RED + f"\n[ERROR] {e}")

def main():
    while True:
        try:
            run_app()
        except RestartRequested:
            os.system('cls' if os.name == 'nt' else 'clear')
            continue
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[SYSTEM] Shutting down...")
            break
        except Exception as e:
            print(Fore.RED + f"\n[CRITICAL ERROR] {e}")
            break

if __name__ == "__main__":
    main()
