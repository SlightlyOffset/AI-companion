# Specification: VULN-002 Remediation

## Problem
The `play_audio_windows` function in `engines/tts_module.py` generates a temporary VBScript and embeds an absolute file path into it without proper escaping. This can lead to arbitrary VBScript execution if the path is manipulated.

## Requirements
- Escape the file path for VBScript string literals.
- Alternatively, use a safer playback method (e.g., calling a player directly with arguments, avoiding script generation).
- Strictly validate the audio file path before use.

## Scope
- `engines/tts_module.py`: Modify `play_audio_windows`.
