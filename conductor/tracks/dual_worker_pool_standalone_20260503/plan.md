# Implementation Plan: Standalone Dual-Worker Pool

## Phase 1: Engine Refactor
- [ ] **Task: Modify LLMEngine for Multi-Worker Support**
  - [ ] Update `LLMEngine.__init__` to detect `torch.cuda.device_count()`.
  - [ ] Implement `_load_worker(device_id)` to load independent model/tokenizer pairs.
  - [ ] Initialize `self.workers = {0: (model, tokenizer, lock), ...}`.
- [ ] **Task: Update Initialization Logic**
  - [ ] Ensure `standalone_llm_bridge.py` main loop initializes the engine with worker support.

## Phase 2: Parallel Dispatch
- [ ] **Task: Implement Parallel generate_batch**
  - [ ] Update `generate_batch` to use `threading.Thread` for distributing `n` candidates across available workers.
  - [ ] Implement result collection and error handling for parallel threads.
- [ ] **Task: Implement Async-Safe generate_stream**
  - [ ] Update `generate_stream` to acquire the first available worker lock.

## Phase 3: Validation
- [ ] **Task: Verification & Testing**
  - [ ] Create test script to simulate multi-GPU environment (if possible) or verify single-GPU fallback.
  - [ ] Verify parallel generation speedup and JSON response format.
- [ ] **Task: Conductor Checkpoint - Verification**