# Specification: Standalone Dual-Worker GPU Pool

## Overview
Implement a dual-worker pool architecture in `colab_bridge/standalone_llm_bridge.py`, mirroring the high-throughput design of `LLM_Bridge.ipynb`. This enables parallel candidate generation (`n>1`) across multiple GPUs.

## Functional Requirements
1.  **Multi-GPU Detection:** Detect available GPUs. If >1 GPU is found, initialize a "Dual-Worker Pool". Otherwise, fallback to single-worker mode.
2.  **Worker Initialization:**
    - Worker 0 loads the model on `cuda:0`.
    - Worker 1 loads the model on `cuda:1` (if available).
3.  **Concurrency Model:**
    - Replace the single global `threading.Lock` with per-GPU locks (`gpu0_lock`, `gpu1_lock`).
    - Use a job queue or worker threads to dispatch incoming requests to available workers.
4.  **Parallel Generation (`n>1`):**
    - When a request for multiple candidates arrives, dispatch tasks across both workers simultaneously using threading.
    - Collect results from both workers before returning the JSON response.

## Technical Context
-   Target script: `colab_bridge/standalone_llm_bridge.py`
-   Stack: FastAPI, PyTorch, Transformers, Threading.

## Acceptance Criteria
- Script detects multiple GPUs and loads two model instances.
- Generation tasks (`n>1`) are distributed to both GPUs concurrently.
- Streaming tasks lock one GPU, leaving the other free for parallel requests.