"""
Lorebook (World Info) management and scanning.
Efficiently injects world/character facts based on keywords in recent history.
"""

import json
import os
import re
import requests

def load_lorebook(filepath: str) -> dict:
    """
    Safely reads and parses the lorebook JSON file.
    """
    if not os.path.exists(filepath):
        return {"entries": []}
    
    try:
        with open(filepath, "r", encoding="UTF-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error loading lorebook: {e}")
        return {"entries": []}

def sync_lore_to_remote(lorebook_data: dict, remote_url: str) -> bool:
    """
    Sync the lorebook to the remote bridge for semantic indexing.
    
    Args:
        lorebook_data (dict): The lorebook with entries
        remote_url (str): The base URL of the remote bridge
        
    Returns:
        bool: True if sync succeeded, False otherwise
    """
    if not remote_url or not lorebook_data:
        return False
    
    try:
        sync_url = f"{remote_url.rstrip('/')}/sync_lore"
        payload = lorebook_data
        
        response = requests.post(sync_url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success":
            print(f"✓ Lore synced to remote bridge: {data.get('message', 'OK')}")
            return True
        else:
            print(f"✗ Failed to sync lore: {data.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error syncing lore to remote bridge: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during lore sync: {e}")
        return False

def scan_for_lore(recent_messages: list, lorebook_data: dict) -> str:
    """
    Scans the most recent conversation history for keywords defined in the lorebook.
    Returns a formatted string of matched entries.
    """
    if not lorebook_data or not lorebook_data.get("entries"):
        return ""

    # Consolidate text from recent messages to scan
    text_to_scan = " ".join([msg.get("content", "").lower() for msg in recent_messages])
    active_lore = []

    for entry in lorebook_data.get("entries", []):
        if not entry.get("enabled", True):
            continue
            
        # Check if any of the keys are in the recent text using whole-word matching
        for key in entry.get("keys", []):
            # Use regex for whole word matching (\bkey\b) to avoid partial matches
            if re.search(fr'\b{re.escape(key.lower())}\b', text_to_scan):
                active_lore.append(entry)
                break 

    if not active_lore:
        return ""

    # Sort by insertion_order (allows you to control which info appears first)
    active_lore.sort(key=lambda x: x.get("insertion_order", 100))
    
    # Format the activated lore into a string block
    lore_text = "[WORLD INFO / LORE]\n"
    for entry in active_lore:
        content = entry.get("content", "").strip()
        if content:
            lore_text += f"- {content}\n"
    
    return lore_text.strip()

