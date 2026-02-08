import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    """Loads all settings from the JSON file."""
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def get_setting(key, default=None):
    """Retrieves a specific setting by key."""
    settings = load_settings()
    return settings.get(key, default)

def update_setting(key, value):
    """Updates a specific setting and saves it back to the file."""
    settings = load_settings()
    settings[key] = value
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False
