# Implementation Plan - Recap Viewport Implementation

This plan outlines the steps to implement a "recap" feature that loads past conversation history into the terminal viewport.

## Phase 1: History Retrieval Enhancements

- [x] Task: Update `HistoryManager` in `engines/memory_v2.py` for flexible retrieval 7d04da7
    - [x] Write tests in `tests/test_memory_v2.py` for retrieving a specific number of recent messages
    - [x] Ensure `load_history(limit)` correctly returns the last `limit` messages from the history file
- [x] Task: Implement 24-hour priority check in `HistoryManager` 8494ca5
    - [x] Write tests for a method that checks if the last interaction was within 24 hours
    - [x] Implement `is_recent_interaction(profile_name, hours=24)` method
- [~] Task: Conductor - User Manual Verification 'History Retrieval Enhancements' (Protocol in workflow.md)

## Phase 2: Terminal Recap Integration

- [ ] Task: Integrate automatic recap into `main.py` startup
    - [ ] Write tests for displaying 3-5 messages on startup (mocking `print`)
    - [ ] Modify `main.py` to fetch the last 5 messages using `memory_manager.load_history(ch_name, limit=5)` before the input loop
    - [ ] Implement a visual separator `=== Past Conversation ===` and header for the recap
- [ ] Task: Implement `//history` command in `engines/app_commands.py`
    - [ ] Write tests for the `//history` command execution and output
    - [ ] Add `//history` and `//recap` to the `cmds` dictionary in `engines/app_commands.py`
    - [ ] The command should fetch the last 15 messages and display them with the same styling as the automatic recap
- [ ] Task: Conductor - User Manual Verification 'Terminal Recap Integration' (Protocol in workflow.md)

## Phase 3: UI/UX Refinement

- [ ] Task: Style the recap output for better readability
    - [ ] Write tests for the recap styling (e.g., color usage)
    - [ ] Use `Fore.LIGHTBLACK_EX` (dimmed) to display historical messages in the terminal
    - [ ] Ensure the format clearly shows `Role: Message` (e.g., `Glitch: ...`)
- [ ] Task: Conductor - User Manual Verification 'UI/UX Refinement' (Protocol in workflow.md)
