import pytest
from engines.config import get_setting, update_setting
import os
import json

from engines.utilities import redact_pii

def test_remote_url_validation(capsys):
    # Setup: Create a temporary settings file
    temp_settings = "settings_test.json"
    if os.path.exists(temp_settings):
        os.remove(temp_settings)
        
    with open(temp_settings, "w") as f:
        json.dump({
            "remote_llm_url": "http://insecure.com",
            "remote_tts_url": "https://secure.com"
        }, f)
        
    # Patch SETTINGS_FILE in engines.config
    import engines.config
    original_settings_file = engines.config.SETTINGS_FILE
    engines.config.SETTINGS_FILE = temp_settings
    
    try:
        # Insecure URL should return None and print a warning
        assert get_setting("remote_llm_url") is None
        captured = capsys.readouterr()
        assert "[SECURITY WARNING]" in captured.out
        
        # Secure URL should be returned
        assert get_setting("remote_tts_url") == "https://secure.com"
        
    finally:
        engines.config.SETTINGS_FILE = original_settings_file
        if os.path.exists(temp_settings):
            os.remove(temp_settings)

def test_pii_redaction():
    text = "Contact me at user@example.com or 192.168.1.1. My name is Alice."
    sanitized = redact_pii(text, user_name="Alice")
    
    assert "user@example.com" not in sanitized
    assert "[EMAIL]" in sanitized
    assert "192.168.1.1" not in sanitized
    assert "[IP_ADDR]" in sanitized
    assert "Alice" not in sanitized
    assert "[USER]" in sanitized
    assert "Contact me at" in sanitized
