from datetime import datetime
import json
import os

HISTORY_DIR = "history"

def ensure_history_dir():
    """ Ensure the history directory exists. """
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

def get_history_filename(profile_name: str) -> str:
    """Get the filename for storing conversation history for a given profile."""
    ensure_history_dir()
    safe_name = "".join(c for c in profile_name if c.isalnum() or c in (' ', '_')).rstrip()
    return os.path.join(HISTORY_DIR, f"{safe_name}_history.json")

def save_conversation(profile_name: str, conversation: list):
    """Save the conversation history to a JSON file."""
    filename = get_history_filename(profile_name)
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d | %H:%M:%S")
    
    # Create a copy to avoid polluting the active conversation list with multiple timestamps
    data_to_save = list(conversation)
    data_to_save.append({
        "role": "system",
        "content": f"Timestamp: {current_time}"
    })
    
    with open(filename, "w", encoding="UTF-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

def get_last_timestamp(profile_name: str) -> datetime | None:
    """Extracts the last timestamp from the history file."""
    conversation = load_conversation(profile_name)
    # Search backwards for the last timestamp message
    for msg in reversed(conversation):
        if msg.get("role") == "system" and "Timestamp: " in msg.get("content", ""):
            time_str = msg["content"].replace("Timestamp: ", "").strip()
            try:
                return datetime.strptime(time_str, "%Y-%m-%d | %H:%M:%S")
            except ValueError:
                return None
    return None

def load_conversation(profile_name: str, filter_system: bool = False) -> list:

    """Load the conversation history from a JSON file."""

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
