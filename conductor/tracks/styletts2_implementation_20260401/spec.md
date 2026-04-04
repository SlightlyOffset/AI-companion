# Track Specification: StyleTTS 2 Voice Cloning

## Overview
This track implements a high-performance, low-latency voice cloning system using StyleTTS 2. It replaces the previous XTTS v2 plan to ensure compatibility and performance on 6GB VRAM GPUs (RTX 3050).

## Functional Requirements
- **Inference Engine**: Integrate the `styletts2` Python library.
- **Zero-Shot Cloning**: Support live voice cloning from a short reference `.wav` file.
- **VRAM Management**: Maintain a footprint under 2.5GB for the TTS engine.
- **Edge Fallback**: Automatically switch to `edge-tts` if GPU inference fails or is disabled.
- **Streaming Support**: Ensure audio segments are generated and played with minimal delay.

## Acceptance Criteria
- Voice cloning works with a 5-10 second reference sample.
- Total system latency (Text -> Audio) is under 500ms for short sentences.
- The TTS engine successfully runs alongside a local 4-bit LLM without VRAM crashes.
- User can toggle between `styletts2` and `edge-tts` in settings.
