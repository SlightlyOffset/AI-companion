# Specification - XTTS v2 Voice Cloning Implementation

## Overview
Implement high-fidelity local and remote voice cloning using the XTTS v2 model. This feature allows users to provide a short audio sample (reference voice) which the AI will then use to generate all future dialogue and narration, significantly enhancing immersion beyond standard neural voices.

## Functional Requirements
- **Hybrid Execution Model:**
    - **Local Mode:** Support running XTTS v2 directly on local hardware (optimized for NVIDIA GPUs with 6GB+ VRAM).
    - **Remote Mode:** Support offloading XTTS v2 inference to Google Colab via a dedicated bridge (similar to the LLM bridge).
- **Profile-Linked Cloning:**
    - Character profiles (`.json`) will include a new field `voice_clone_ref` specifying the path to a reference `.wav` file.
    - Reference voices will be stored in a dedicated `/voices` directory.
- **Dynamic Engine Selection:**
    - Per-profile setting to choose between `XTTS v2` and `edge-tts`.
    - **Automatic Fallback:** If the primary XTTS engine is unavailable (e.g., bridge disconnected or local error), the system must automatically fallback to `edge-tts` to ensure uninterrupted interaction.
- **Audio Optimization:**
    - **Audio Caching:** Implement a local cache for generated audio files. If the AI generates an identical string, the cached file will be reused to eliminate generation latency.
- **Enhanced Cloning Capabilities:**
    - Support for multi-language cloning (e.g., using a non-English reference voice to speak English).

## Non-Functional Requirements
- **VRAM Management:** Local execution must be optimized to fit within the 6GB limit of an RTX 3050, potentially using quantization or offloading the LLM to Colab.
- **Latency:** Aim for "perceived zero-latency" through audio segment streaming or aggressive caching.

## Acceptance Criteria
- [ ] Users can specify a `.wav` reference in a character profile and hear the cloned voice in the terminal.
- [ ] The system correctly identifies when XTTS is unavailable and switches to Edge-TTS without crashing.
- [ ] Repeated phrases are played instantly from the audio cache.
- [ ] Cloned voices maintain the unique characteristics (pitch, tone) of the reference sample across different responses.

## Out of Scope
- Training or fine-tuning the base XTTS v2 model.
- Real-time "voice-to-voice" conversion (cloning the user's voice in real-time).
- Automatic downloading of the XTTS v2 model weights (user must provide them initially).
