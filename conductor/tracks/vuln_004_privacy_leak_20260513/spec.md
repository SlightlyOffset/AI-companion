# Specification: VULN-004 Remediation

## Problem
The application sends PII (chat history, voice samples) to remote URLs provided in `settings.json` without validation or user warning.

## Requirements
- Implement validation for `remote_llm_url` and `remote_tts_url` (e.g., must be HTTPS).
- Add a user confirmation/warning dialog when a remote URL is first configured or used.
- Provide a clear indicator in the UI when remote services are active.
- Document which data is sent to which remote services.

## Scope
- `engines/config.py`: Add validation for remote URLs.
- `menu.py`: Add UI warnings/indicators.
- `engines/responses.py`, `engines/xtts_remote.py`: Ensure HTTPS and add logging/tracking.
