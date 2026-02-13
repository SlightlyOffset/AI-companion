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

def get_smart_split_points(text):
    """
    Finds punctuation points to split text, but ONLY if they are 
    not inside asterisks (*...*) or part of an ellipsis (...).
    """
    points = []
    in_asterisks = False
    
    for i in range(len(text)):
        char = text[i]
        
        # Toggle narration state
        if char == '*':
            in_asterisks = not in_asterisks
            continue
            
        # If we aren't in an action block, look for punctuation
        if not in_asterisks:
            if char in ".!?\n":
                # Check for ellipsis (don't split if the next char is also a dot)
                if char == '.' and i + 1 < len(text) and text[i+1] == '.':
                    continue
                # Check if we are in the middle of an ellipsis (previous char was a dot)
                if char == '.' and i > 0 and text[i-1] == '.':
                    continue
                    
                points.append(i + 1)
    return points

def run_app():
    character_profile_path = pick_profile()
    if not character_profile_path:
        return

    character_profile = load_profile(character_profile_path)
    ch_name = character_profile["name"]

    user_profile_path = pick_user_profile()
    if user_profile_path:
        user_profile = load_profile(user_profile_path)
        user_name = user_profile.get("name", "User")
        update_setting("current_user_profile", os.path.basename(user_profile_path))
    else:
        user_name = "User"

    print(Fore.YELLOW + Style.BRIGHT + f"--- {ch_name} Desktop Companion Loaded ---")
    print(Fore.YELLOW + "Type '//help' for a list of commands.\n")

    while True:
        try:
            with open(CONFIG_PATH, "r", encoding="UTF-8") as f:
                config = json.load(f)

            profile_data = load_profile(character_profile_path)
            tts_pref = profile_data.get("preferred_tts_voice", None)

            apply_mood_decay(character_profile_path, ch_name)

            gen_thread = threading.Thread(target=tts_generation_worker, args=(tts_pref,))
            play_thread = threading.Thread(target=tts_playback_worker)
            gen_thread.daemon = True
            play_thread.daemon = True
            gen_thread.start()
            play_thread.start()

            user_input = input(Fore.CYAN + Style.BRIGHT + f"{user_name}: " + Style.RESET_ALL).strip()
            if not user_input:
                tts_text_queue.put(None)
                gen_thread.join(); play_thread.join()
                continue

            if user_input.startswith("//"):
                if app_commands(user_input):
                    tts_text_queue.put(None)
                    gen_thread.join(); play_thread.join()
                    continue

            should_obey = None
            system_extra_info = None
            if is_command(user_input):
                if config.get("execute_command", False):
                    rel_score = profile_data.get("relationship_score", 0)
                    weights = [max(0.1, profile_data.get("good_weight", 5) + (rel_score/10)), 
                               max(0.1, profile_data.get("bad_weight", 5) - (rel_score/10))]
                    should_obey = (random.choices(["good", "bad"], weights=weights, k=1)[0] == "good")
                    if should_obey:
                        _, message = execute_command(user_input)
                        print(Fore.GREEN + f"[SYSTEM] {message}")
                        system_extra_info = "Task complete. Keep response brief."
                else:
                    print(Fore.YELLOW + "[SYSTEM] Command execution disabled.")
                    continue

            colors = profile_data.get("colors", {})
            text_style = getattr(Fore, colors.get("text", "WHITE").upper(), Fore.WHITE)

            print(Fore.WHITE + Style.DIM + "-" * 30)
            print(Fore.MAGENTA + Style.BRIGHT + f"{ch_name}: " + Style.NORMAL + text_style, end="", flush=True)

            full_response = ""
            current_buffer = ""
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
                current_buffer += chunk

                # Check for safe split points
                split_points = get_smart_split_points(current_buffer)
                if split_points:
                    last_point = 0
                    for point in split_points:
                        segment = current_buffer[last_point:point].strip()
                        if segment:
                            cleaned = clean_text_for_tts(segment)
                            if cleaned:
                                tts_text_queue.put(cleaned)
                        last_point = point
                    current_buffer = current_buffer[last_point:]

            # Final Cleanup
            if current_buffer.strip():
                clean_leftover = re.sub(r'\[REL:\s*[+-]?\d+\]', '', current_buffer).strip()
                cleaned = clean_text_for_tts(clean_leftover)
                if cleaned:
                    tts_text_queue.put(cleaned)

            print("\n" + Fore.WHITE + Style.DIM + "-" * 30)
            tts_text_queue.put(None)
            gen_thread.join(); play_thread.join()

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
