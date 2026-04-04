# Track Specification: Profile Branching & Scenario Engine

## Overview
This track implements a "Save Slot" or "Multiverse" system for the AI Desktop Companion. It decouples the base character template from the active session state, allowing users to create multiple "Branches" for a single character (e.g., "Astgenne - Cyberpunk AU" vs "Astgenne - High Fantasy").

## Functional Requirements
- **Template/Instance Separation**: Base profiles (e.g., `profiles/Astgenne.json`) remain read-only templates.
- **Branch Profiles**: Create a `branches/` (or `saves/`) directory to store session-specific data:
    - `relationship_score`
    - `scenario_description` (Custom context for the current branch)
    - `last_active_timestamp`
    - `history_file_pointer`
- **Multi-History Support**: Each branch must point to a unique history file (e.g., `history/Astgenne/cyberpunk_history.json`).
- **Scenario Injection**: The `scenario_description` must be dynamically injected into the system prompt to ground the AI in the current setting.
- **CLI Commands**:
    - `//branch_list`: Show all branches for the current character.
    - `//branch_new [name]`: Create a new branch with a custom scenario.
    - `//branch_switch [name]`: Swap to a different branch/timeline.
    - `//scenario_set [text]`: Update the context for the current active branch.
- **Startup Picker Upgrade**: Enhance the initial character selection to allow picking/resuming a specific branch.

## Non-Functional Requirements
- **Data Integrity**: Ensure switching branches safely saves the current state before loading the next.
- **Backward Compatibility**: Existing single-file profiles should be automatically migrated or treated as a "Default" branch.

## Acceptance Criteria
- User can create and name multiple branches for one character.
- Relationship scores and chat histories are completely isolated between branches.
- Changing the `scenario_description` in one branch correctly updates the AI's behavior without affecting other branches.
- The application persists the last active branch per character.
