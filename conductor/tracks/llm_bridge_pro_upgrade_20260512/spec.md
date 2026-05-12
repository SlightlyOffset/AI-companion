# Specification: LLM Bridge "Pro" Upgrade

## Overview
Upgrade the `LLM_Bridge.ipynb` notebook to include the advanced logic found in `standalone_llm_bridge.py`. This ensures parity between the interactive notebook and the standalone script, providing better stability, safety, and features for users offloading to Colab/Kaggle.

## Objectives
- **Context Truncation:** Implement logic to surgically trim conversation history to prevent RoPE kernel crashes when exceeding the model's context window.
- **OOM Resilience:** Port the automatic retry mechanism that re-packs VRAM if an Out-of-Memory error occurs.
- **Semantic RAG:** Integrate the `LoreManager` to support server-side Lorebook indexing and retrieval.
- **Feature Parity:** Support `repetition_penalty` and `n` (candidates) parameters in the `/chat` endpoint.
- **Stability:** Standardize on `float32` compute type for better cross-hardware compatibility on T4 GPUs.

## Scope
- `colab_bridge/LLM_Bridge.ipynb`

## Technical Details
- **FastAPI Integration:** Use `create_app` pattern for modularity.
- **Dual-Worker Pool:** Maintain support for multi-GPU setups (Kaggle T4 x2).
- **Notebook UX:** Keep the instructions and setup cells clear and easy to follow.
