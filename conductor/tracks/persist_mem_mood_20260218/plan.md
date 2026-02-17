# Implementation Plan - Persistent Chat History and Mood Adjustment System

This plan outlines the steps to implement persistent chat history and the dynamic mood adjustment system.

## Phase 1: Persistent Chat History

- [ ] Task: Create `engines/memory_v2.py` with history persistence logic
    - [ ] Write tests for loading/saving history to profile-specific JSON files
    - [ ] Implement `HistoryManager` class to handle per-profile JSON I/O
    - [ ] Implement history truncation logic (keep last 15 messages)
- [ ] Task: Integrate `HistoryManager` into `main.py`
    - [ ] Write tests for `main.py` interaction with `HistoryManager`
    - [ ] Replace existing in-memory history with `HistoryManager`
- [ ] Task: Conductor - User Manual Verification 'Persistent Chat History' (Protocol in workflow.md)

## Phase 2: Mood Adjustment System

- [ ] Task: Implement Mood Engine in `engines/mood.py`
    - [ ] Write tests for mood score calculation and persistence
    - [ ] Implement `MoodEngine` with relationship meter (-100 to +100)
    - [ ] Implement sentiment analysis triggers (nice/mean words)
    - [ ] Implement mood decay logic based on time difference
- [ ] Task: Integrate Mood Engine with Prompts
    - [ ] Write tests for dynamic system prompt generation based on mood
    - [ ] Update `engines/prompts.py` to inject mood-specific instructions
- [ ] Task: Conductor - User Manual Verification 'Mood Adjustment System' (Protocol in workflow.md)

## Phase 3: Final Integration and UI Updates

- [ ] Task: Update Terminal UI for Mood Display
    - [ ] Write tests for mood status rendering
    - [ ] Add a small indicator in the CLI to show current relationship/mood state
- [ ] Task: Conductor - User Manual Verification 'Final Integration and UI Updates' (Protocol in workflow.md)
