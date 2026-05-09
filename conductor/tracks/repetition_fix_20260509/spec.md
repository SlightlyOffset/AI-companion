# Specification: AI Repetition & Echoing Fix

## Problem
The AI companion occasionally enters infinite loops (repeating past replies) or echoes the user's input/prompts. This is caused by a lack of repetition penalty during the token generation phase.

## Requirements
- Support `repetition_penalty` in the remote bridge (`ChatRequest` and Transformers `generate`).
- Support `repeat_penalty` in the local Ollama client (`options`).
- Default the penalty to `1.15`, which is the industry standard for Llama 3 models.
- Expose the parameter in `engines/config.py` via `settings.json`.
