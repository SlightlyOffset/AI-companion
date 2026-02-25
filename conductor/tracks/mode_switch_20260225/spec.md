# Track Specification: Mode Switch (RP vs. Casual)

## Overview
This track implements a "Mode Switch" for the AI Desktop Companion, allowing users to switch between the traditional immersive Roleplay (RP) mode and a more direct, narrative-free Casual mode. This switch will be managed via a CLI command and will persist in the application's configuration.

## Functional Requirements
- **Mode Toggle Command**: Implement a CLI command (e.g., `//mode` or `//toggle_mode`) to switch between 'rp' and 'casual' modes.
- **Persistent Configuration**: Store the current mode in `settings.json` so it persists across sessions.
- **Dynamic Prompt Crafting**:
    - **RP Mode (Default)**: Maintains existing behavior with narration/actions (`*...*`) on separate lines and immersive character rules.
    - **Casual Mode**: Modifies the system prompt to explicitly forbid narration/asterisks and encourage concise, direct responses while maintaining character identity.
- **Mood Engine Integration**: Casual mode interactions must still influence the Relationship & Mood engine, allowing the character's sentiment to evolve regardless of the interaction style.
- **Visual Feedback**: Inform the user in the CLI when the mode has been changed.

## Non-Functional Requirements
- **Minimal Latency**: Prompt modification should not introduce noticeable delay in response generation.
- **Consistency**: Ensure the character's core personality remains consistent even when the interaction style changes.

## Acceptance Criteria
- User can toggle between RP and Casual modes using a CLI command.
- The selected mode is saved to `settings.json`.
- In Casual mode, the LLM does not generate narrative text within asterisks.
- In Casual mode, the LLM provides concise responses.
- Changes in relationship score are still calculated and applied in Casual mode.
- On restart, the application loads the last used mode from `settings.json`.

## Out of Scope
- Implementation of additional modes beyond RP and Casual.
- Per-character mode settings (initially, it will be a global application setting).
