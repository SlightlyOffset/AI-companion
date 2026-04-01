# Implementation Plan: Mode Switch (RP vs. Casual)

## Phase 1: Configuration and State Management
Objective: Update the configuration system to support and persist the interaction mode.

- [x] Task: Update `settings.json` and `engines/config.py`
    - [x] Add `interaction_mode` with default value `"rp"` to `settings.json`.
    - [x] Update `engines/config.py` to ensure the new setting is loaded and updatable.
- [x] Task: Write Tests for Configuration
    - [x] Create `tests/test_mode_config.py`.
    - [x] Write tests to verify that `interaction_mode` can be retrieved and updated correctly via `engines/config.py`.

## Phase 2: Prompt Engineering
Objective: Implement the dynamic prompt selection logic based on the active mode.

- [x] Task: Modify `engines/prompts.py`
    - [x] Update `build_system_prompt` to accept the `mode` parameter.
    - [x] Define separate `rule` sets for:
        - **"rp"**: Standard roleplay with narration in `*...*`.
        - **"casual"**: Concise, no narration, conversational.
    - [x] Implement conditional logic to return the appropriate rules.
- [x] Task: Write Tests for Prompt Construction
    - [x] Update `tests/test_prompts.py` or create `tests/test_mode_prompts.py`.
    - [x] Write tests to verify that `build_system_prompt` returns the correct behavioral rules for both modes.

## Phase 3: Integration and Command Logic
Objective: Connect the mode setting to the interaction loop and provide a user command to toggle it.

- [x] Task: Update `engines/responses.py`
    - [x] Update `get_respond_stream` to fetch the current `interaction_mode` from settings and pass it to `build_system_prompt`.
- [x] Task: Implement `//mode` command in `engines/app_commands.py`
    - [x] Implement `_toggle_mode` function to switch between `rp` and `casual`.
    - [x] Register the `//mode` command in the `cmds` mapping.
    - [x] Ensure user feedback is printed to the terminal upon switching.
- [x] Task: Write Tests for Command Integration
    - [x] Update `tests/test_app_commands.py`.
    - [x] Write tests to verify the `//mode` command correctly updates the configuration.

## Phase 4: Final Verification
Objective: Ensure the feature works as expected in a live session.

- [x] Task: End-to-End Verification
    - [x] Start the application and verify that it defaults to RP mode.
    - [x] Use `//mode` to switch to Casual mode and confirm the change.
    - [x] Send messages in Casual mode and verify the response follows the "No Narration" and "Concise" rules.
    - [x] Restart the application and verify that it persists the last used mode.
