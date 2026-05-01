# Implementation Plan: Integrated Transformers LLM Bridge

## Phase 1: Environment & Engine Setup
- [ ] **Task: Update Dependencies**
    - [ ] Add `transformers`, `accelerate`, `bitsandbytes`, `torch`, `torchvision`, `torchaudio` to `colab_bridge/requirements.txt`.
- [ ] **Task: Implement LLM Engine Class**
    - [ ] Create `LLMEngine` class in `colab_bridge/standalone_llm_bridge.py`.
    - [ ] Implement 4-bit loading logic with `BitsAndBytesConfig`.
    - [ ] Implement `generate_stream` and `generate_batch` methods.
- [ ] **Task: Add CLI Arguments**
    - [ ] Update `main()` to accept `--model` and `--hf_token` arguments.

## Phase 2: Endpoint Integration
- [ ] **Task: Integrate Engine into FastAPI**
    - [ ] Initialize `LLMEngine` globally in the bridge.
    - [ ] Update `/chat` endpoint to use the engine.
- [ ] **Task: Implement Concurrency Control**
    - [ ] Add a `threading.Lock` to the `LLMEngine` to protect inference.
- [ ] **Task: Unified RAG Injection**
    - [ ] Ensure `LoreManager` results are prepended to the system prompt before tokenization.

## Phase 3: Reliability & Validation
- [ ] **Task: Implement Error Fallbacks**
    - [ ] Add try-except blocks around generation to return a "System busy/unavailable" message on OOM.
- [ ] **Task: Local End-to-End Test**
    - [ ] Mock GPU and verify streaming/batch JSON formats.
- [ ] **Task: Remote Validation (Kaggle)**
    - [ ] Run on Kaggle T4 and verify connection from `t.ai`.
- [ ] **Task: Conductor - User Manual Verification 'Integrated Transformers LLM Bridge' (Protocol in workflow.md)**
