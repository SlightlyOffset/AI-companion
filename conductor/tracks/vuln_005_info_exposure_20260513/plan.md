# Implementation Plan: VULN-005 Remediation

## Phase 1: Research
- [x] Identify all potentially sensitive keys in `settings.json` (e.g., `HF_TOKEN`, `NGROK_TOKEN`, `remote_llm_url` if it contains a key).

## Phase 2: Implementation
- [x] Create a `SENSITIVE_KEYS` list in `engines/app_commands.py`. f5c1088
- [x] Update `_show_settings` to mask these values (e.g., `********`). f5c1088

## Phase 3: Validation
- [ ] Run `//show_settings` and verify that sensitive values are masked.
