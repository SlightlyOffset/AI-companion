# Implementation Plan: Standalone Dual-Worker Pool

## Phase 1: Engine Refactor
- [x] **Task: Modify LLMEngine for Multi-Worker Support**
  - [x] Update `LLMEngine.__init__` to detect `torch.cuda.device_count()`.
  - [x] Implement `_load_worker(device_id)` to load independent model/tokenizer pairs.
  - [x] Initialize `self.workers = {0: (model, tokenizer, lock), ...}`.
- [x] **Task: Update Initialization Logic**
  - [x] Ensure `standalone_llm_bridge.py` main loop initializes the engine with worker support.

## Phase 2: Parallel Dispatch
- [x] **Task: Implement Parallel generate_batch**
  - [x] Update `generate_batch` to use `threading.Thread` for distributing `n` candidates across available workers.
  - [x] Implement result collection and error handling for parallel threads.
- [x] **Task: Implement Async-Safe generate_stream**
  - [x] Update `generate_stream` to acquire the first available worker lock.

## Phase 3: Validation
- [x] **Task: Verification & Testing**
  - [x] Create test script to simulate multi-GPU environment (if possible) or verify single-GPU fallback.
  - [x] Verify parallel generation speedup and JSON response format.
- [x] **Task: Conductor Checkpoint - Verification**

