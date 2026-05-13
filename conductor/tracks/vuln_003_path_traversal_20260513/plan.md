# Implementation Plan: VULN-003 Remediation

## Phase 1: Research & Reproduction
- [ ] Create a unit test that attempts to import a character with a traversal name (e.g., `../../malicious`).

## Phase 2: Implementation
- [ ] Implement `sanitize_profile_name` or use the existing one from `utilities.py` in `character_importer.py`.
- [ ] Add explicit checks to ensure the `target_path` is relative to the `profiles/` root.

## Phase 3: Validation
- [ ] Verify that the unit test now saves the file safely within the `profiles/` directory (or fails gracefully).
