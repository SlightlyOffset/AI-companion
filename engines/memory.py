"""
Persistent memory management for conversation history.
Handles per-profile history storage and timestamp extraction for mood decay.
"""

from datetime import datetime
import json
import os

# Directory where conversation histories are stored
HISTORY_DIR = "history"

def ensure_history_dir():
    """Ensures the history directory exists on the filesystem."""
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

def get_history_filename(profile_name: str) -> str:
    """
    Generates a safe filename for storing conversation history.
    
    Args:
        profile_name (str): The name of the character profile.
        
    Returns:
        str: The full path to the history .json file.
    """
    ensure_history_dir()
    # Sanitize name to prevent invalid filesystem characters
    safe_name = "".join(c for c in profile_name if c.isalnum() or c in (' ', '_')).rstrip()
    return os.path.join(HISTORY_DIR, f"{safe_name}_history.json")

def save_conversation(profile_name: str, conversation: list):
    """
    Saves the full conversation history to a JSON file.
    Appends a system timestamp to the end of the history for mood decay tracking.
    
    Args:
        profile_name (str): The name of the character.
        conversation (list): List of message dictionaries.
    """
    filename = get_history_filename(profile_name)
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d | %H:%M:%S")
    
    # Create a copy to avoid polluting the active context with system timestamps
    data_to_save = list(conversation)
    data_to_save.append({
        "role": "system",
        "content": f"Timestamp: {current_time}"
    })
    
    with open(filename, "w", encoding="UTF-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

def get_last_timestamp(profile_name: str) -> datetime | None:
    """
    Searches history for the most recent system timestamp.
    Used to calculate time passed between sessions for mood decay.
    
    Args:
        profile_name (str): The name of the character.
        
    Returns:
        datetime: The last recorded interaction time, or None if not found.
    """
    conversation = load_conversation(profile_name)
    # Search backwards for the last system timestamp message
    for msg in reversed(conversation):
        if msg.get("role") == "system" and "Timestamp: " in msg.get("content", ""):
            time_str = msg["content"].replace("Timestamp: ", "").strip()
            try:
                return datetime.strptime(time_str, "%Y-%m-%d | %H:%M:%S")
            except ValueError:
                return None
    return None

def load_conversation(profile_name: str, filter_system: bool = False) -> list:
    """
    Loads conversation history from a JSON file.
    
    Args:
        profile_name (str): The name of the character.
        filter_system (bool): If True, removes internal system messages (like timestamps).
        
    Returns:
        list: List of loaded messages.
    """
    filename = get_history_filename(profile_name)

    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="UTF-8") as f:
                history = json.load(f)
                if filter_system:
                    return [m for m in history if m.get("role") != "system"]
                return history
        except Exception:
            return []
    return []
