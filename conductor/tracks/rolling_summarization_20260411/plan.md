# Implementation Plan - Rolling Summarization

## Phase 1: Memory Manager & State Storage
- [x] Update `engines/memory_v2.py` to support `memory_core` and `last_summarized_index` within the `metadata` structure. (bc618b6)
- [x] Add getter and setter methods for the Memory Core in `HistoryManager`. (21728c8)

## Phase 2: Rolling Summarizer Logic
- [ ] In `engines/responses.py`, create a `update_rolling_summary` helper function.
- [ ] This function should accept the current Memory Core, the new messages to summarize, and the model configuration.
- [ ] Draft a specific prompt for consolidating an existing summary with new events.

## Phase 3: Background Worker Integration
- [ ] In `menu.py` (or the appropriate controller), trigger a background check after every few user interactions.
- [ ] If the difference between the total history length and the `last_summarized_index` exceeds the active `memory_limit` + buffer (e.g., 5 messages), launch the summarization task.
- [ ] Save the updated Memory Core and new index back to disk upon completion.

## Phase 4: Context Injection
- [ ] Modify `get_respond_stream` in `engines/responses.py` to fetch the current Memory Core.
- [ ] Inject the summary string (if present) into the `system_extra_info` parameter or directly into the system prompt compilation.
- [ ] Validate that the AI references the injected memory correctly during chat.
