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

def clean_text_for_tts(text: str) -> str:
    """
    Removes text used for actions/narration in RP so they aren't spoken out loud.
    Handles *actions*, **bold actions**, (parenthetical actions), and [brackets].
    """
    # 1. Remove text inside triple or double asterisks first (longest matches)
    cleaned = re.sub(r'\*{2,3}.*?\*{2,3}', '', text, flags=re.DOTALL)
    
    # 2. Remove text inside single asterisks
    cleaned = re.sub(r'\*.*?\*', '', cleaned, flags=re.DOTALL)
    
    # 3. Remove text inside parentheses (often used for OOC or meta-narration)
    cleaned = re.sub(r'\(.*?\)', '', cleaned, flags=re.DOTALL)

    # 4. Remove text inside brackets
    cleaned = re.sub(r'\[.*?\]', '', cleaned, flags=re.DOTALL)

    # 5. Clean up any leftover stray asterisks or brackets
    cleaned = cleaned.replace('*', '').replace('[', '').replace(']', '')

    # 6. Remove double spaces and strip
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # If the segment is just punctuation now, it should be empty
    if all(char in ".,!?;:- " for char in cleaned):
        return ""

    return cleaned

def is_online(host="8.8.8.8", port=53, timeout=3):
    """
    Check internet connectivity by attempting to connect to a DNS server.

    Args:
        host (str): Host to connect to (default: Google's DNS 8.8.8.8)
        port (int): Port number (default: 53 for DNS)
        timeout (int): Timeout in seconds

    Returns:
        bool: True if connected, False otherwise
    """
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
        return True
    except (socket.timeout, socket.error):
        return False

def get_offline_engine():
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
    """
    Uses Microsoft Edge Neural TTS.
    """
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def play_audio_windows(filename):
    """
    Plays audio using a temporary VBScript.
    This is extremely reliable on Windows and runs in the background.
    """
    abspath = os.path.abspath(filename)
    vbs_path = os.path.join(os.environ["TEMP"], "play_sound.vbs")

    # Create a small VBScript to play the sound
    vbs_content = f"""
    Set Sound = CreateObject("WMPlayer.OCX")
    Sound.URL = "{abspath.replace('\\', '\\\\')}"
    Sound.Controls.play
    do while Sound.currentmedia.duration = 0
        wscript.sleep 5
    loop
    wscript.sleep (Sound.currentmedia.duration * 1000)
    """

    with open(vbs_path, "w") as f:
        f.write(vbs_content)

    # Run the VBScript and wait for it to finish
    subprocess.run(["wscript.exe", vbs_path], capture_output=True)

    # Clean up VBScript
    if os.path.exists(vbs_path):
        os.remove(vbs_path)

def generate_audio(text, filename, voice=None):
    """Generates audio file from text without playing it."""
    if not EDGE_AVAILABLE or not is_online():
        return False
    try:
        if voice is None:
            voice = get_setting("default_tts_voice", "en-GB-SoniaNeural")
        cleaned_text = clean_text_for_tts(text)
        if not cleaned_text:
            return False
        asyncio.run(generate_edge_tts(cleaned_text, filename, voice=voice))
        return True
    except Exception as e:
        print(Fore.RED + f"\n[TTS GEN ERROR] {e}")
        return False

def play_audio(filename):
    """Plays the audio file and removes it."""
    # Check for tts enabled
    if not get_setting("tts_enabled", True):
        return

    try:
        if os.name == "nt":
            play_audio_windows(filename)
        else:
            cmd = "xdg-open" if os.name == "posix" else "open"
            subprocess.run([cmd, filename])
            # rough estimate for non-windows
            time.sleep(2)
    except Exception as e:
        print(Fore.RED + f"\n[TTS PLAY ERROR] {e}")
    finally:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

def tts_edge(text, filename="output_tts.mp3", voice=None):
    """Synchronous wrapper for edge-tts generation and playback."""

    if not EDGE_AVAILABLE:
        return tts_offline(text)
    try:
        asyncio.run(generate_edge_tts(text, filename, voice=voice))

        if os.name == "nt":
            play_audio_windows(filename)
        else:
            # Unix playback
            cmd = "xdg-open" if os.name == "posix" else "open"
            subprocess.run([cmd, filename])
            time.sleep(len(text) * 0.1)

    except Exception as e:
        print(Fore.RED + f"\n[TTS ERROR] {e}")
        tts_offline(text)
    finally:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

def tts_offline(text):
    engine = get_offline_engine()
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except:
            pass

def speak(text, pref_tts: str | None = None):
    """
    High-level speak function using Edge Neural TTS.
    Cleans the text of RP actions (asterisks) before speaking.
    """
    # Check if TTS is enabled
    if not get_setting("tts_enabled", True):
        return

    cleaned_text = clean_text_for_tts(text)

    # If the text was ONLY actions, don't try to speak
    if not cleaned_text:
        return

    if EDGE_AVAILABLE and is_online():
        if pref_tts is None:
            pref_tts = get_setting("default_tts_voice", "en-GB-SoniaNeural")
        tts_edge(cleaned_text, voice=pref_tts)
    else:
        tts_offline(cleaned_text)
