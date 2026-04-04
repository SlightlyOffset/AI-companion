# Track Specification: D&D Mode Extension

## Overview
This track extends the "Mode Switch" system to include a "D&D Mode," which uses structured tags (`[STORY]`, `[SAY]`, `[DO]`) to distinguish between environmental narration, character dialogue, and mechanical outcomes.

## Functional Requirements
- **Tag-Based Output**: Force the LLM to use `[STORY]`, `[SAY]`, and `[DO]` tags for all responses.
- **Terminal Styling**: Color-code the tags in the CLI for better readability (e.g., `[STORY]` in Cyan, `[DO]` in Yellow).
- **TTS Integration**: Ensure the TTS engine correctly maps `[SAY]` to character voices and `[STORY]` to narrator voices.
- **Mechanical Logic**: Allow the LLM to suggest dice rolls or stat checks within the `[DO]` tag.

## Acceptance Criteria
- User can select `dnd` mode via the `//mode` command.
- All LLM output in D&D mode is wrapped in the specified tags.
- The terminal displays tags in distinct colors.
- TTS follows the tag-to-voice mapping.
