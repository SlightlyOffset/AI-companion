# Specification - Rolling Summarization & Memory Core Injection

## Overview
Implement a rolling summarization system that consolidates older messages into a concise "Memory Core" and continuously injects it into the active LLM context. This prevents the AI from suffering "amnesia" when messages fall outside the configured `memory_limit`, without sacrificing performance or VRAM.

## Functional Requirements
- **Rolling Updates**: A background worker should periodically evaluate the conversation history. If the unsummarized history exceeds a certain threshold beyond the active window, it should generate a new summary.
- **Consolidated Summary**: The new summary must incorporate both the *existing* Memory Core (if any) and the newly "aged out" messages to maintain a continuous narrative.
- **Prompt Injection**: The active Memory Core must be fetched and injected into the AI's system prompt (e.g., via `system_extra_info` or directly appended to the system instructions).
- **Metadata Storage**: The Memory Core summary must be persisted in the character's `history.json` metadata to survive application restarts.

## Technical Requirements
- **Model Usage**: Use the configured `summarizer_model` (defaulting to Gemma 2 2B) for the summarization tasks.
- **Concurrency**: Summarization must happen asynchronously (via `@work(thread=True)` or native `threading`) to avoid blocking the main TUI or the active chat stream.
- **Threshold Logic**: Add logic to track the index of the last summarized message to prevent re-summarizing the entire history every time.

## Acceptance Criteria
- [ ] The `memory_v2.py` manager accurately stores and retrieves the `memory_core` and `last_summarized_index` in the `metadata` block.
- [ ] A background task successfully identifies unsummarized old messages and updates the Memory Core.
- [ ] The active LLM context seamlessly receives the Memory Core data via the system prompt.
- [ ] Long conversations demonstrate retained knowledge of early events without performance degradation.
