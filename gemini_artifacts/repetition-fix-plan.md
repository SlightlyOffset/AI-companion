# Plan: AI Repetition & Echoing Fix

## Objective
Implement a repetition penalty across the entire inference pipeline (both remote bridge and local Ollama) to eliminate AI loops and echoing.

## Background
The AI sometimes repeats its previous sentence or echoes the user's prompt structure. This is a common issue with small Llama 3 models when generation parameters are too loose. A repetition penalty of `1.15` is widely considered the "sweet spot" for Llama 3.

## Technical Details

### 1. Remote Bridge (`colab_bridge/standalone_llm_bridge.py`)
- **ChatRequest Model:** Add `repetition_penalty: float = 1.15`.
- **_generation_kwargs:** Add `repetition_penalty` to the returned dictionary.
- **_worker_generate_once / generate_stream:** Ensure `kwargs` contains the penalty and pass it to `model.generate`.

### 2. Local Client (`engines/responses.py` & `engines/config.py`)
- **Global Settings:** Add `repetition_penalty` to the default settings (default `1.15`).
- **Remote Payload:** Update `get_respond_stream`, `_call_llm_once`, and `_generate_candidate_replies` to send the `repetition_penalty` to the bridge.
- **Local Ollama:** Update `ollama.chat` calls to include `repeat_penalty` in the `options` dictionary.

## Implementation Steps

### Phase 1: Bridge Updates
1.  Modify `ChatRequest` class.
2.  Update `_generation_kwargs` method.
3.  Ensure `model.generate` receives the parameter.

### Phase 2: Client Updates
1.  Add default to `settings.json` via `engines/config.py`.
2.  Update `requests.post` payloads in `engines/responses.py`.
3.  Update `ollama.chat` calls in `engines/responses.py`.

## Verification
1.  Launch the bridge with a Llama 3 model.
2.  Interact through the TUI.
3.  Observe the bridge logs to confirm `repetition_penalty=1.15` is being received.
4.  Run a local Ollama test to confirm `repeat_penalty` is active.
