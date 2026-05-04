# Specification: Integrated Transformers LLM Bridge

## Overview
Connect the `standalone_llm_bridge.py` server to a real LLM using the HuggingFace `transformers` stack. This replaces placeholder responses with actual inference on GPU-enabled environments (Colab/Kaggle).

## Functional Requirements
1.  **Model Loading**:
    -   Support loading any HuggingFace CausalLM model (default: `Sao10K/L3-8B-Stheno-v3.2`).
    -   Load models in 4-bit precision using `bitsandbytes` to fit on T4 GPUs.
    -   Model ID must be configurable via a `--model` command-line argument.
2.  **Inference Endpoints**:
    -   **`/chat` (Streaming)**: Stream tokens using `TextIteratorStreamer` for single-candidate requests (`n=1`).
    -   **`/chat` (Batch)**: Return a JSON payload `{"candidates": [str, ...]}` for multi-candidate requests (`n>1`).
3.  **Context Management**:
    -   Apply existing Semantic RAG context injection (Lorebook retrieval) *before* the generation phase.
    -   Use the appropriate chat template for the loaded model.
4.  **Concurrency & Reliability**:
    -   Implement a global thread lock to ensure only one inference task is active at a time to prevent VRAM over-allocation.
    -   On GPU failure or OOM, return a graceful text fallback message instead of a raw 500 error.

## Technical Context
-   **Host**: Google Colab / Kaggle T4 GPU.
-   **Stack**: FastAPI, Uvicorn, Transformers, BitsAndBytes, Torch.
-   **Security**: Open access (no API key required), but requires `HF_TOKEN` for model downloads.

## Acceptance Criteria
-   Bridge successfully loads `L3-8B-Stheno-v3.2` on a T4 GPU.
-   Local `t.ai` client receives a streaming response from the remote tunnel.
-   Parallel candidate generation (`n=4`) returns the correct JSON format.
-   RAG-injected context is reflected in the AI's response.
