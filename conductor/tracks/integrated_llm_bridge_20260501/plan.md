# Implementation Plan: Integrated Transformers LLM Bridge

## Phase 1: Environment & Engine Setup
- [x] **Task: Update Dependencies**
    - [x] Add `transformers`, `accelerate`, `bitsandbytes`, `torch`, `torchvision`, `torchaudio` to `colab_bridge/requirements.txt`.
- [x] **Task: Implement LLM Engine Class**
    - [x] Create `LLMEngine` class in `colab_bridge/standalone_llm_bridge.py`.
    - [x] Implement 4-bit loading logic with `BitsAndBytesConfig`.
    - [x] Implement `generate_stream` and `generate_batch` methods.
- [x] **Task: Add CLI Arguments**
    - [x] Update `main()` to accept `--model` and `--hf_token` arguments.

## Phase 2: Endpoint Integration
- [x] **Task: Integrate Engine into FastAPI**
    - [x] Initialize `LLMEngine` globally in the bridge.
    - [x] Update `/chat` endpoint to use the engine.
- [x] **Task: Implement Concurrency Control**
    - [x] Add a `threading.Lock` to the `LLMEngine` to protect inference.
- [x] **Task: Unified RAG Injection**
    - [x] Ensure `LoreManager` results are prepended to the system prompt before tokenization.

## Phase 3: Reliability & Validation
- [x] **Task: Implement Error Fallbacks**
    - [x] Add try-except blocks around generation to return a "System busy/unavailable" message on OOM.
- [x] **Task: Local End-to-End Test**
    - [x] Mock GPU and verify streaming/batch JSON formats.
- [ ] **Task: Remote Validation (Kaggle)**
    - [ ] Run on Kaggle T4 and verify connection from `t.ai`.
- [ ] **Task: Conductor - User Manual Verification 'Integrated Transformers LLM Bridge' (Protocol in workflow.md)**
