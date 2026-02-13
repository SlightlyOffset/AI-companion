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
from engines.utilities import pick_profile
from engines.app_commands import app_commands
from engines.responses import get_respond_stream, apply_mood_decay
from engines.tts_module import generate_audio, play_audio, clean_text_for_tts

# Initialize colorama
init(autoreset=True)

# Congig path
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
    print(Fore.YELLOW + Style.DIM + "[ NOTICE ]: This is an early build. Expect some quirks and crashes. Feedback is appreciated!")
    print(Fore.YELLOW + Style.DIM + "[ NOTICE ]: Take everything the AI says with a grain of salt! It may produce incorrect or nonsensical responses.\n")

    while True:
        try:
            # Load config
            with open(CONFIG_PATH, "r", encoding="UTF-8") as f:
                config = json.load(f)

            # Refresh profile each loop to get updates
            profile = load_profile(profile_path)
            tts_pref = profile.get("preferred_tts_voice", None)

            # Check and apply mood decay dynamically
            decayed_points, new_score = apply_mood_decay(profile_path, name) or (0, 0)
            if decayed_points > 0:
                print(Fore.YELLOW + Style.DIM + f"  (Time has passed... {name}'s feelings have shifted. New Score: {new_score})")

            # Start TTS pipeline workers
            gen_thread = threading.Thread(target=tts_generation_worker, args=(tts_pref,))
            play_thread = threading.Thread(target=tts_playback_worker)
            gen_thread.daemon = True
            play_thread.daemon = True
            gen_thread.start()
            play_thread.start()

            user_input = input(Fore.CYAN + Style.BRIGHT + "You: " + Style.RESET_ALL).strip()
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

            # Determine if the AI should obey based on relationship score
            should_obey = None
            system_extra_info = None
            if is_command(user_input):
                if config.get("execute_command", False):
                    # --- Relationship-Based Decision Logic ---
                    relationship_score = profile.get("relationship_score", 0)
                    rel_mod = relationship_score / 10.0

                    good_w = profile.get("good_weight", 5)
                    bad_w = profile.get("bad_weight", 5)

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

            # Colors for AI response
            colors = profile.get("colors", {})
            text_color_name = colors.get("text", "WHITE").upper()
            text_style = getattr(Fore, text_color_name, Fore.WHITE)

            print(Fore.WHITE + Style.DIM + "-" * 30)
            print(Fore.MAGENTA + Style.BRIGHT + f"{name}: " + Style.NORMAL + text_style, end="", flush=True)

            # Streaming LLM Response
            full_response = ""
            current_sentence = ""

            for chunk in get_respond_stream(user_input, profile, should_obey=should_obey, profile_path=profile_path, system_extra_info=system_extra_info):
                print(text_style + chunk, end="", flush=True)
                full_response += chunk
                current_sentence += chunk

                # Check for sentence completion or buffer length
                if any(punct in chunk for punct in ".!?\n") or len(current_sentence) > 60:
                    parts = re.split(r'(?<=[.!?\n])', current_sentence)

                    if len(parts) == 1 and len(current_sentence) > 160:
                        last_space = current_sentence.rfind(' ')
                        if last_space != -1 and last_space > 30:
                            parts = [current_sentence[:last_space+1], current_sentence[last_space+1:]]
                        else:
                            parts = [current_sentence]

                    for i in range(len(parts) - 1):
                        segment = parts[i].strip()
                        if segment:
                            # Pre-clean check to avoid speaking roleplay actions
                            if clean_text_for_tts(segment):
                                tts_text_queue.put(segment)
                    current_sentence = parts[-1]

            if current_sentence.strip():
                clean_sentence = re.sub(r'\[REL:\s*[+-]?\d+\]', '', current_sentence).strip()
                if clean_sentence and clean_text_for_tts(clean_sentence):
                    tts_text_queue.put(clean_sentence)

            print("\n")

            if is_command(user_input) and not should_obey:
                print(Fore.RED + f"[SYSTEM] {name} refused to help.")

            print(Fore.WHITE + Style.DIM + "-" * 30)

            # Stop the pipeline
            tts_text_queue.put(None)
            gen_thread.join()
            play_thread.join()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(Fore.RED + f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()