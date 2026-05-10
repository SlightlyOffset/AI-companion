# Implementation Plan: Initial Scene Extraction

## Objective
Extract the starting scene from a character's starter message using a lightweight LLM call to populate history metadata accurately.

## Steps
1. **Engine Update (`engines/responses.py`):**
   - Create a helper function `extract_scene_from_starter(starter_message: str) -> str`.
   - Use `ollama.chat` with the `local_utility_model` (default `llama3.2`) and `temperature=0.1` to ask the model to identify the physical setting from the message.

2. **Memory Update (`engines/memory_v2.py`):**
   - Provide a helper `update_current_scene(profile_name: str, new_scene: str)` to easily patch the metadata in the background.

3. **UI Integration (`menu.py`):**
   - In `print_starter_message`, after saving the initial history, dispatch a `@work(thread=True)` background task.
   - The task will call `extract_scene_from_starter` and then `memory_manager.update_current_scene`.

## Verification
- Start a new session with a profile that has a starter message (e.g., "Welcome to my spaceship").
- Check `history/ProfileName.json` after a few seconds to verify the `current_scene` is updated from `"Unknown Location"` to `"Spaceship"` or similar.
