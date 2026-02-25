# Implementation Plan: Mode Switch (RP vs. Casual)

## Phase 1: Configuration and State Management
Objective: Update the configuration system to support and persist the interaction mode.

- [ ] Task: Update `settings.json` and `engines/config.py`
    - [ ] Add `interaction_mode` with default value `"rp"` to `settings.json`.
    - [ ] Update `engines/config.py` to ensure the new setting is loaded and updatable.
- [ ] Task: Write Tests for Configuration
    - [ ] Create `tests/test_mode_config.py`.
    - [ ] Write tests to verify that `interaction_mode` can be retrieved and updated correctly via `engines/config.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Configuration and State Management' (Protocol in workflow.md)

## Phase 2: Prompt Engineering
Objective: Implement the dynamic prompt selection logic based on the active mode.

- [ ] Task: Modify `engines/prompts.py`
    - [ ] Update `build_system_prompt` to accept the `mode` parameter.
    - [ ] Define separate `rule` sets for "rp" and "casual" modes.
    - [ ] Implement conditional logic to return the appropriate rules.
- [ ] Task: Write Tests for Prompt Construction
    - [ ] Update `tests/test_prompts.py` or create `tests/test_mode_prompts.py`.
    - [ ] Write tests to verify that `build_system_prompt` returns the correct behavioral rules for both "rp" and "casual" modes.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Prompt Engineering' (Protocol in workflow.md)

## Phase 3: Integration and Command Logic
Objective: Connect the mode setting to the interaction loop and provide a user command to toggle it.

- [ ] Task: Update `engines/responses.py`
    - [ ] Update `get_respond_stream` to fetch the current `interaction_mode` from settings and pass it to `build_system_prompt`.
- [ ] Task: Implement `//mode` command in `engines/app_commands.py`
    - [ ] Add a `_toggle_mode` function to handle switching between modes.
    - [ ] Register the `//mode` (or `//toggle_mode`) command in the `cmds` mapping.
    - [ ] Ensure user feedback is printed to the terminal upon switching.
- [ ] Task: Write Tests for Command Integration
    - [ ] Update `tests/test_app_commands.py`.
    - [ ] Write tests to verify the `//mode` command correctly updates the configuration and provides expected output.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration and Command Logic' (Protocol in workflow.md)

## Phase 4: Final Verification
Objective: Ensure the feature works as expected in a live session.

- [ ] Task: End-to-End Verification
    - [ ] Start the application and verify that it defaults to RP mode.
    - [ ] Use `//mode` to switch to Casual mode and confirm the change.
    - [ ] Send messages in Casual mode and verify the response follows the "No Narration" and "Concise" rules.
    - [ ] Verify that Relationship Score still updates in Casual mode.
    - [ ] Restart the application and verify that it persists the last used mode.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Verification' (Protocol in workflow.md)
