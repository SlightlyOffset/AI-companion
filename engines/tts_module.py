import os
import time
import asyncio
import subprocess
from colorama import Fore, Style
from engines.helpers import is_online

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

def get_offline_engine():
    global _offline_engine
    if _offline_engine is None and OFFLINE_AVAILABLE:
        try:
            _offline_engine = pyttsx3.init()
            _offline_engine.setProperty('rate', 170)
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
        wscript.sleep 100
    loop
    wscript.sleep (int(Sound.currentmedia.duration) + 1) * 1000
    """

    with open(vbs_path, "w") as f:
        f.write(vbs_content)

    # Run the VBScript and wait for it to finish
    subprocess.run(["wscript.exe", vbs_path], capture_output=True)

    # Clean up VBScript
    if os.path.exists(vbs_path):
        os.remove(vbs_path)

def tts_edge(text, filename="output_tts.mp3"):
    """Synchronous wrapper for edge-tts generation and playback."""
    if not EDGE_AVAILABLE:
        return tts_offline(text)

    try:
        # Generation
        asyncio.run(generate_edge_tts(text, filename))

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

def speak(text):
    """
    High-level speak function using Edge Neural TTS.
    """
    if EDGE_AVAILABLE and is_online():
        tts_edge(text)
    else:
        tts_offline(text)
