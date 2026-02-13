"""
Configuration management for global application settings.
Handles reading and writing to settings.json.
"""

import json
import os

# Path to the global settings file
SETTINGS_FILE = "settings.json"

def load_settings():
    """
    Loads all settings from the JSON file.
    
    Returns:
        dict: The loaded settings, or an empty dict if the file is missing/invalid.
    """
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def get_setting(key, default=None):
    """
    Retrieves a specific setting by key.
    
    Args:
        key (str): The setting key to find.
        default: The value to return if the key doesn't exist.
        
    Returns:
        The value of the setting or the default.
    """
    settings = load_settings()
    return settings.get(key, default)

def update_setting(key, value):
    """
    Updates a specific setting and saves it back to the file.
    
    Args:
        key (str): The setting key to update.
        value: The new value for the setting.
        
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    settings = load_settings()
    settings[key] = value
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False
