# Bridge Stability and Thread-Safety Fix

## Objective
Fix the intermittent `CUDA error: an illegal memory access was encountered` occurring in `standalone_llm_bridge.py` during both streaming and parallel batch generation.

## Background & Motivation
The bridge is experiencing catastrophic CUDA crashes due to three overlapping issues:
1. **Implicit Disconnects:** `t.ai` has an internal `timeout=60` for remote requests. If the Colab/Kaggle bridge takes longer than 60s to finish, `t.ai` drops the connection. This raises a `GeneratorExit` in FastAPI, causing the `generate_stream` lock to release *while the background generation thread is still running*. Subsequent requests then collide on the same GPU.
2. **Global CUDA Syncs:** `torch.cuda.empty_cache()` is called in the `finally` block of every generation. This PyTorch function causes a global synchronization across *all* devices. When Worker 0 and Worker 1 run concurrently in batch mode, this synchronization stalls the pipeline and causes `bitsandbytes` allocator collisions.
3. **Context Length Overflow:** The bridge does not currently truncate incoming messages. If a long RP session exceeds the 8192 token limit of Llama 3 models, the RoPE (Rotary Position Embedding) kernel attempts to access out-of-bounds memory, resulting in an immediate illegal memory access error.

## Scope & Impact
- `colab_bridge/standalone_llm_bridge.py` will be modified.
- No changes to the `t.ai` client are necessary, as the bridge must be resilient to dropped connections and large payloads.

## Implementation Steps
1. **Fix `generate_stream` Lifecycle:** Wrap the streamer iteration in a `try...finally` block. If the client disconnects, ensure `generation_thread.join()` is called before releasing the lock to prevent overlapping CUDA executions.
2. **Remove `empty_cache` Spam:** Remove the `torch.cuda.empty_cache()` calls from the post-generation `finally` blocks in both `generate_stream` and `_worker_generate_once` to prevent global CUDA sync issues on dual-worker setups.
3. **Implement Context Truncation:** Add logic to `_worker_generate_once` to check `inputs.input_ids.shape[1]`. If `length + max_tokens > max_position_embeddings`, cleanly slice the tensors from the left to keep the context within limits before generation.

## Verification
- Start the bridge and simulate a dropped connection mid-stream to ensure the lock remains held until the background thread finishes.
- Send a payload exceeding 8500 tokens to verify that truncation successfully prevents the RoPE out-of-bounds crash.
