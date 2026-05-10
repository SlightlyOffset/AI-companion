# Specification: Initial Scene Extraction

## Problem
When starting a new conversation with a starter message, the `current_scene` metadata in the history is initialized as `"Unknown Location"`. This lacks narrative context for the pipeline.

## Requirements
- When a starter message is printed on a fresh history, extract the scene automatically.
- Use a lightweight local LLM prompt (via `ollama.chat`) to determine the scene from the starter message text.
- Save this extracted scene into the persistent memory metadata.
- Perform this in the background so it does not block the UI from rendering.
