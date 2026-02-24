"""
Remote XTTS v2 client.
Handles communication with the Google Colab bridge for remote voice cloning.
"""

import requests
import os
from colorama import Fore
from engines.config import get_setting

def generate_remote_xtts(text, output_path, speaker_wav, language="en"):
    """
    Sends a generation request to the remote Google Colab bridge.
    """
    bridge_url = get_setting("remote_tts_url")
    if not bridge_url:
        print(Fore.RED + "[XTTS REMOTE] Error: 'remote_tts_url' not set in settings.json." + Fore.RESET)
        return False

    if not os.path.exists(speaker_wav):
        print(Fore.RED + f"[XTTS REMOTE] Error: Speaker reference '{speaker_wav}' not found." + Fore.RESET)
        return False

    try:
        endpoint = f"{bridge_url.rstrip('/')}/generate_tts"
        
        with open(speaker_wav, "rb") as f:
            files = {"speaker_file": f}
            data = {
                "text": text,
                "language": language
            }
            
            if get_setting("debug_mode", False):
                print(Fore.MAGENTA + f"[DEBUG] Sending text to XTTS: {text}" + Fore.RESET)

            print(Fore.CYAN + f"[XTTS REMOTE] Requesting audio from Colab bridge..." + Fore.RESET)
            response = requests.post(endpoint, data=data, files=files, timeout=60)
            
        if response.status_code == 200:
            with open(output_path, "wb") as out:
                out.write(response.content)
            return True
        else:
            print(Fore.RED + f"[XTTS REMOTE ERROR] Server returned {response.status_code}: {response.text}" + Fore.RESET)
            return False

    except Exception as e:
        print(Fore.RED + f"[XTTS REMOTE ERROR] Failed to connect to bridge: {e}" + Fore.RESET)
        return False
