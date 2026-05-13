# Specification: VULN-001 Remediation

## Problem
The `get_sentiment_score` function in `engines/responses.py` directly concatenates user input into an LLM prompt. An attacker can use this to manipulate the sentiment score, affecting the relationship engine.

## Requirements
- Sanitize user input before passing it to the sentiment LLM.
- Use a more robust prompt structure (e.g., XML-like tags or clear separation).
- Implement defensive instructions in the system prompt to ignore user-supplied instructions.

## Scope
- `engines/responses.py`: Modify `get_sentiment_score`.
