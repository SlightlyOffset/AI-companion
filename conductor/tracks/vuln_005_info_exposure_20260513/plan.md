# Implementation Plan: VULN-005 Remediation

## Phase 1: Research
- [ ] Identify all potentially sensitive keys in `settings.json` (e.g., `HF_TOKEN`, `NGROK_TOKEN`, `remote_llm_url` if it contains a key).

## Phase 2: Implementation
- [ ] Create a `SENSITIVE_KEYS` list in `engines/app_commands.py`.
- [ ] Update `_show_settings` to mask these values (e.g., `********`).

## Phase 3: Validation
- [ ] Run `//show_settings` and verify that sensitive values are masked.
