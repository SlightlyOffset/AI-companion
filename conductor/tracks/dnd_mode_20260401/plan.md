# Implementation Plan: D&D Mode Extension

## Phase 1: Prompt Engineering
- [ ] Task: Update `engines/prompts.py` to include `dnd` mode behavioral rules.
- [ ] Task: Define the structure for `[STORY]`, `[SAY]`, and `[DO]` tags in the system prompt.

## Phase 2: Response Parsing & Styling
- [ ] Task: Update `engines/responses.py` to parse the new tags.
- [ ] Task: Implement color-coding for tags in the terminal using `colorama`.
- [ ] Task: Update the TTS splitting logic to handle `[STORY]` and `[SAY]` tags as voice triggers.

## Phase 3: Integration
- [ ] Task: Update `//mode` command to include `dnd` in the rotation.
- [ ] Task: Final end-to-end verification of D&D roleplay.
