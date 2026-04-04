# Implementation Plan: Profile Branching & Scenario Engine

## Phase 1: Architecture & Data Structure
- [ ] Task: Create `branches/` directory structure.
- [ ] Task: Refactor `engines/config.py` to track `current_branch` in addition to `current_character`.
- [ ] Task: Develop a migration script/logic to move `relationship_score` from base profiles into a "Default" branch file.

## Phase 2: Memory & History Refactor
- [ ] Task: Update `engines/memory_v2.py` to support nested history paths (e.g., `history/{character}/{branch}.json`).
- [ ] Task: Ensure the `memory_manager` correctly loads/saves history based on the active branch ID.

## Phase 3: Prompt Engineering (Scenarios)
- [ ] Task: Update `engines/prompts.py` to accept `branch_data` (specifically `scenario_description`).
- [ ] Task: Inject the scenario context into the master system prompt under a new `[CURRENT SCENARIO]` header.

## Phase 4: Integration & Command Logic
- [ ] Task: Implement the `//branch_...` suite of commands in `engines/app_commands.py`.
- [ ] Task: Update the startup flow in `main.py` and `engines/utilities.py` to handle branch selection after character selection.
- [ ] Task: Final verification of "multiverse" switching.
