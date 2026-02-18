"""
Main entry point for the Sassy AI Desktop Companion.
Handles the interaction loop, multi-threaded TTS pipeline, and UI rendering.
"""

# Standard library imports
import json
import threading
import random
import queue
import re
import os
import time
import sys

# Third-party imports
from colorama import init, Fore, Style

# Local imports
from engines.actions import execute_command
from engines.utilities import is_command
from engines.utilities import pick_profile, pick_user_profile
from engines.app_commands import app_commands, RestartRequested
from engines.responses import get_respond_stream, apply_mood_decay
from engines.tts_module import generate_audio, play_audio, clean_text_for_tts
from engines.config import update_setting, get_setting
from engines.memory_v2 import memory_manager

# Initialize colorama
init(autoreset=False)

# Clearing the console at startup
if get_setting("clear_at_start", True):
    os.system('cls' if os.name == 'nt' else 'clear')

# Global configuration path
CONFIG_PATH = "settings.json"

def load_profile(profile_path):
    """Loads a character or user profile from a JSON file."""
    with open(profile_path, "r", encoding="UTF-8") as f:
        return json.load(f)

# TTS Queues
tts_text_queue = queue.Queue()
audio_file_queue = queue.Queue()

def tts_generation_worker():
    """Worker thread that converts text to MP3. Expects (text, voice) tuples."""
    while True:
        data = tts_text_queue.get()
        if data is None:
            audio_file_queue.put(None)
            break

        text, voice = data
        temp_dir = os.environ.get("TEMP", "/tmp")
        temp_filename = os.path.join(temp_dir, f"tts_{time.time()}_{random.randint(1000,9999)}.mp3")

        if generate_audio(text, temp_filename, voice=voice):
            audio_file_queue.put(temp_filename)
        tts_text_queue.task_done()

def tts_playback_worker():
    """Worker thread to play audio files in order."""
    while True:
        filename = audio_file_queue.get()
        if filename is None:
            break
        play_audio(filename)
        audio_file_queue.task_done()

def get_smart_split_points(text):
    """
    Finds split points for TTS.
    Splits on asterisks (to switch voices) and punctuation (to keep segments short).
    """
    points = []
    in_asterisks = False
    for i in range(len(text)):
        char = text[i]
        if char == '*':
            in_asterisks = not in_asterisks
            points.append(i + 1)
            continue
        if not in_asterisks:
            if char in ".!?\n":
                if char == '.' and i + 1 < len(text) and text[i+1] == '.':
                    continue
                if char == '.' and i > 0 and text[i-1] == '.':
                    continue
                points.append(i + 1)
    return points

def run_app():
    character_profile_path = pick_profile()
    if not character_profile_path:
        return

    character_profile = load_profile(character_profile_path)
    ch_name = character_profile["name"] # For display
    history_profile_name = os.path.basename(character_profile_path).replace(".json", "") # For history
    update_setting("current_character_profile", os.path.basename(character_profile_path)) # Set active profile

    user_profile_path = pick_user_profile()
    if user_profile_path:
        user_profile = load_profile(user_profile_path)
        user_name = user_profile.get("name", "User")
        update_setting("current_user_profile", os.path.basename(user_profile_path))
    else:
        user_name = "User"

    print(Fore.YELLOW + Style.BRIGHT + f"--- {ch_name} Desktop Companion Loaded ---" + Style.RESET_ALL)
    print(Fore.YELLOW + "Type '//help' for a list of commands.\n" + Style.RESET_ALL)

    # --- Automatic Recap Display ---
    recap_messages = memory_manager.load_history(history_profile_name, limit=5)
    if recap_messages:
        print(Fore.WHITE + Style.DIM + "=== Past Conversation ===" + Style.RESET_ALL)
        for msg in recap_messages:
            role = msg.get("role", "Unknown").capitalize()
            content = msg.get("content", "")
            # Basic styling for recap messages - will be refined in Phase 3
            print(Fore.LIGHTBLACK_EX + f"{role}: {content}" + Style.RESET_ALL)
        print(Fore.WHITE + Style.DIM + "=========================" + Style.RESET_ALL)
    # --- End Automatic Recap Display ---

    while True:
        try:
            with open(CONFIG_PATH, "r", encoding="UTF-8") as f:
                config = json.load(f)

            profile_data = load_profile(character_profile_path)
            char_voice = profile_data.get("preferred_tts_voice", None)
            narrator_voice = get_setting("narration_tts_voice", "en-US-AndrewNeural")

            apply_mood_decay(character_profile_path, history_profile_name)

            gen_thread = threading.Thread(target=tts_generation_worker)
            play_thread = threading.Thread(target=tts_playback_worker)
            gen_thread.daemon = True; play_thread.daemon = True
            gen_thread.start(); play_thread.start()

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
                else:
                    print(Fore.RED + "[SYSTEM] Unknown command. Type '//help' for a list of commands." + Style.RESET_ALL)
                    tts_text_queue.put(None)
                    gen_thread.join(); play_thread.join()
                    continue

            should_obey = None
            if is_command(user_input) and config.get("execute_command", False):
                rel_score = profile_data.get("relationship_score", 0)
                weights = [max(0.1, profile_data.get("good_weight", 5) + (rel_score/10)),
                           max(0.1, profile_data.get("bad_weight", 5) - (rel_score/10))]
                should_obey = (random.choices(["good", "bad"], weights=weights, k=1)[0] == "good")
                if should_obey:
                    _, message = execute_command(user_input)
                    print(Fore.GREEN + f"[SYSTEM] {message}" + Style.RESET_ALL)

            colors = profile_data.get("colors", {})
            char_style = getattr(Fore, colors.get("text", "WHITE").upper(), Fore.WHITE) + \
                         getattr(Style, colors.get("label", "NORMAL").upper(), Style.NORMAL)
            narration_style = Fore.LIGHTBLACK_EX + Style.BRIGHT + "\033[3m"

            print(Fore.WHITE + Style.DIM + "-" * 30 + Style.RESET_ALL)
            sys.stdout.write(Fore.MAGENTA + Style.BRIGHT + f"{ch_name}: " + Style.RESET_ALL)
            sys.stdout.flush()

            full_response = ""
            current_buffer = ""
            is_currently_narrating = False # Tracks state for terminal printing
            tts_in_narration = False      # Tracks state for voice selection

            for chunk in get_respond_stream(user_input, profile_data, should_obey=should_obey, profile_path=character_profile_path):
                for char in chunk:
                    if char == '*':
                        is_currently_narrating = not is_currently_narrating
                        sys.stdout.write(narration_style if is_currently_narrating else char_style)
                        # sys.stdout.write(char) # Optionally print the asterisk if you want a visual toggle in the terminal
                    else:
                        sys.stdout.write((narration_style if is_currently_narrating else char_style) + char)
                sys.stdout.flush()

                full_response += chunk
                current_buffer += chunk

                # Check for split points
                split_points = get_smart_split_points(current_buffer)
                if split_points:
                    last_point = 0
                    for point in split_points:
                        segment = current_buffer[last_point:point]

                        # Detect if this segment contains a toggle
                        contains_asterisk = '*' in segment

                        # Important: Voice selection happens based on state BEFORE the toggle,
                        # UNLESS the segment IS the narration itself.
                        # If a segment is "*", it toggles the state for the NEXT segment.
                        voice = narrator_voice if tts_in_narration or contains_asterisk else char_voice

                        # Update the state for the next segment if we hit an asterisk
                        if contains_asterisk:
                            tts_in_narration = not tts_in_narration

                        cleaned = clean_text_for_tts(segment, speak_narration=True)
                        if cleaned:
                            tts_text_queue.put((cleaned, voice))
                        last_point = point
                    current_buffer = current_buffer[last_point:]

            if current_buffer.strip():
                clean_leftover = re.sub(r'\[REL:\s*[+-]?\d+\]', '', current_buffer).strip()
                voice = narrator_voice if tts_in_narration or '*' in clean_leftover else char_voice
                cleaned = clean_text_for_tts(clean_leftover, speak_narration=True)
                if cleaned:
                    tts_text_queue.put((cleaned, voice))

            sys.stdout.write(Style.RESET_ALL + "\n")
            print(Fore.WHITE + Style.DIM + "-" * 30 + Style.RESET_ALL)
            sys.stdout.flush()

            tts_text_queue.put(None)
            gen_thread.join(); play_thread.join()

        except (KeyboardInterrupt, RestartRequested):
            sys.stdout.write(Style.RESET_ALL); sys.stdout.flush()
            raise
        except Exception as e:
            sys.stdout.write(Style.RESET_ALL)
            print(Fore.RED + f"\n[ERROR] {e}" + Style.RESET_ALL)

def main():
    while True:
        try:
            run_app()
        except RestartRequested:
            os.system('cls' if os.name == 'nt' else 'clear')
            continue
        except KeyboardInterrupt:
            print(Style.RESET_ALL + Fore.YELLOW + "\n[SYSTEM] Shutting down..." + Style.RESET_ALL)
            break
        except Exception as e:
            print(Style.RESET_ALL + Fore.RED + f"\n[CRITICAL ERROR] {e}" + Style.RESET_ALL)
            break

if __name__ == "__main__":
    main()
