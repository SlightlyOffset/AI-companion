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
    with open(filename, "w", encoding="UTF-8") as f:
        json.dump(conversation, f, ensure_ascii=False, indent=4)

def load_conversation(profile_name: str) -> list:
    """Load the conversation history from a JSON file."""
    filename = get_history_filename(profile_name)
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="UTF-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []