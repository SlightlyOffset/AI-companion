# Implementation Plan: AI Repetition Fix

## Objective
Implement a repetition penalty across both local and remote generation pipelines to prevent AI echoing and loops.

## Steps
1. **Bridge Update:**
   - Update `ChatRequest` in `colab_bridge/standalone_llm_bridge.py` to include `repetition_penalty: float = 1.15`.
   - Pass `repetition_penalty` to `_generation_kwargs`.
   - Use the parameter in `model.generate`.

2. **Client Update:**
   - Add `repetition_penalty` to `settings.json` defaults in `engines/config.py`.
   - Update `engines/responses.py` to send `repetition_penalty` to the remote bridge.
   - Update `engines/responses.py` to include `repeat_penalty` in Ollama `options`.

## Verification
- Start local bridge and send a prompt that previously caused echoing.
- Verify through logs that the penalty is being applied.
