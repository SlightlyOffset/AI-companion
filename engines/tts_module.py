"""
Text-to-Speech (TTS) engine.
Supports Microsoft Edge Neural TTS (online) and pyttsx3 (offline fallback).
Includes logic to strip or preserve RP narration from spoken audio.
"""

import os
import re
import time
import asyncio
import socket
import subprocess
from colorama import Fore
from engines.config import get_setting

# Attempt to import edge-tts
try:
    import edge_tts
    EDGE_AVAILABLE = True
except ImportError:
    EDGE_AVAILABLE = False

# Fallback offline engine
try:
    import pyttsx3
    OFFLINE_AVAILABLE = True
except ImportError:
    OFFLINE_AVAILABLE = False

_offline_engine = None

def clean_text_for_tts(text: str, speak_narration: bool = True) -> str:
    """
    Cleans text for the TTS engine. 
    Either strips narration (*...*) or just removes the symbols based on settings.

    Args:
        text (str): Raw segment of text from the LLM.
        speak_narration (bool): If True, removes symbols but keeps text. If False, strips text entirely.

    Returns:
        str: Cleaned text suitable for the TTS engine.
    """
    if speak_narration:
        # Just remove formatting symbols but keep the words
        cleaned = text.replace('***', '').replace('**', '').replace('*', '')
        cleaned = cleaned.replace('(', '').replace(')', '').replace('[', '').replace(']', '')
    else:
        # 1. Remove text inside triple or double asterisks first
        cleaned = re.sub(r'\*{2,3}.*?\*{2,3}', '', text, flags=re.DOTALL)
        # 2. Remove text inside single asterisks
        cleaned = re.sub(r'\*.*?\*', '', cleaned, flags=re.DOTALL)
        # 3. Remove text inside parentheses
        cleaned = re.sub(r'\(.*?\)', '', cleaned, flags=re.DOTALL)
        # 4. Remove text inside brackets
        cleaned = re.sub(r'\[.*?\]', '', cleaned, flags=re.DOTALL)

    # Final cleanup of leftover stray symbols and normalization
    cleaned = cleaned.replace('*', '').replace('[', '').replace(']', '')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    if all(char in ".,!?;:- " for char in cleaned):
        return ""

    return cleaned

def is_online(host="8.8.8.8", port=53, timeout=3):
    """Checks for an active internet connection."""
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
        return True
    except (socket.timeout, socket.error):
        return False

def get_offline_engine():
    """Initializes and returns the pyttsx3 engine."""
    global _offline_engine
    if _offline_engine is None and OFFLINE_AVAILABLE:
        try:
            default_rate = get_setting("tts_rate", 170)
            _offline_engine = pyttsx3.init()
            _offline_engine.setProperty('rate', default_rate)
        except:
            pass
    return _offline_engine

async def generate_edge_tts(text, filename, voice="en-GB-SoniaNeural"):
    """Internal async function for Edge TTS."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def play_audio_windows(filename):
    """Plays audio via VBScript on Windows."""
    abspath = os.path.abspath(filename)
    vbs_path = os.path.join(os.environ["TEMP"], "play_sound.vbs")
    vbs_content = f"""
    Set Sound = CreateObject("WMPlayer.OCX")
    Sound.URL = "{abspath.replace('\\', '\\\\')}"
    Sound.Controls.play
    do while Sound.currentmedia.duration = 0
        wscript.sleep 5
    loop
    wscript.sleep (Sound.currentmedia.duration * 1000)
    """
    with open(vbs_path, "w") as f: f.write(vbs_content)
    subprocess.run(["wscript.exe", vbs_path], capture_output=True)
    if os.path.exists(vbs_path): os.remove(vbs_path)

def generate_audio(text, filename, voice=None, engine="edge-tts", clone_ref=None):
    """
    Converts text to an MP3 or WAV file.
    Supports edge-tts (default) and future XTTS.
    """
    if engine == "edge-tts":
        if not EDGE_AVAILABLE or not is_online():
            return False
        try:
            if voice is None:
                voice = get_setting("default_tts_voice", "en-GB-SoniaNeural")
            
            # We perform a generic clean just in case symbols were missed
            cleaned_text = clean_text_for_tts(text, speak_narration=True)
            if not cleaned_text:
                return False

            asyncio.run(generate_edge_tts(cleaned_text, filename, voice=voice))
            return True
        except Exception as e:
            print(Fore.RED + f"\n[TTS GEN ERROR] {e}")
            return False
    elif engine == "xtts":
        return False # Not implemented yet

    return False

def play_audio(filename):
    """Plays and deletes the audio file."""
    if not get_setting("tts_enabled", True):
        return
    try:
        if os.name == "nt":
            play_audio_windows(filename)
        else:
            cmd = "xdg-open" if os.name == "posix" else "open"
            subprocess.run([cmd, filename])
            time.sleep(2)
    except Exception as e:
        print(Fore.RED + f"\n[TTS PLAY ERROR] {e}")
    finally:
        if os.path.exists(filename):
            try: os.remove(filename)
            except: pass

def speak(text, pref_tts: str | None = None, engine="edge-tts", clone_ref=None):
    """High-level synchronous speak function."""
    if not get_setting("tts_enabled", True):
        return
    
    filename = "temp_speak.mp3"
    if generate_audio(text, filename, voice=pref_tts, engine=engine, clone_ref=clone_ref):
        play_audio(filename)
    else:
        # Fallback to pyttsx3 if edge-tts/xtts failed and offline engine available
        if OFFLINE_AVAILABLE:
            cleaned_text = clean_text_for_tts(text, speak_narration=True)
            if cleaned_text:
                py_engine = get_offline_engine()
                py_engine.say(cleaned_text); py_engine.runAndWait()
