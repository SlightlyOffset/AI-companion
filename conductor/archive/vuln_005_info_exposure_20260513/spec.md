# Specification: VULN-005 Remediation

## Problem
The `//show_settings` command displays all values from `settings.json` in plain text. This may include API tokens or other secrets.

## Requirements
- Define a list of "sensitive" configuration keys.
- Redact or mask values for sensitive keys in the `//show_settings` output.
- Add an option to "reveal" secrets if absolutely necessary, with a confirmation prompt.

## Scope
- `engines/app_commands.py`: Modify `_show_settings` output logic.
