# Implementation Plan: LLM Bridge "Pro" Upgrade

## Phase 1: Preparation
- [x] Review `standalone_llm_bridge.py` to extract core logic.
- [~] Prepare the Markdown instructions for the new notebook.

## Phase 2: Implementation
- [ ] **Step 1: Dependency Update.** Update Cell 1 to install `sentence-transformers` and `scikit-learn`.
- [ ] **Step 2: Logic Integration.** Create a new "Pro Bridge Server" cell that contains:
    - `LoreManager` class.
    - `LLMEngine` class (with OOM retry and context truncation).
    - `TunnelManager` class.
    - `create_app` function.
    - Colab/Kaggle secret retrieval logic.
    - `uvicorn` runner with `nest_asyncio`.
- [ ] **Step 3: Cleanup.** Remove legacy cells and consolidate the notebook structure.

## Phase 3: Verification
- [ ] Run a JSON validator on the final `.ipynb` file.
- [ ] Verify that all required classes and methods are present.
