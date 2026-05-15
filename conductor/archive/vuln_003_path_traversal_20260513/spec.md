# Specification: VULN-003 Remediation

## Problem
The character importer uses the character name from the metadata to construct the save path for the profile JSON. If the name contains `../`, it can write files outside the `profiles/` directory.

## Requirements
- Sanitize the character name to remove path traversal sequences.
- Use `os.path.basename()` on the generated filename.
- Ensure the final save path is within the expected `profiles/` directory.

## Scope
- `engines/character_importer.py`: Modify profile saving logic.
