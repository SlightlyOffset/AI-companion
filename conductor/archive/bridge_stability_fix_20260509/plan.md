# Bridge Stability and Thread-Safety Fix

## Objective
Fix the intermittent `CUDA error: an illegal memory access was encountered` occurring in `standalone_llm_bridge.py` during both streaming and parallel batch generation.

## Implementation Steps
1. **Fix `generate_stream` Lifecycle:** Wrap the streamer iteration in a `try...finally` block. If the client disconnects, ensure `generation_thread.join()` is called before releasing the lock to prevent overlapping CUDA executions.
2. **Remove `empty_cache` Spam:** Remove the `torch.cuda.empty_cache()` calls from the post-generation `finally` blocks in both `generate_stream` and `_worker_generate_once` to prevent global CUDA sync issues on dual-worker setups.
3. **Implement Context Truncation:** Add logic to `_worker_generate_once` to check `inputs.input_ids.shape[1]`. If `length + max_tokens > max_position_embeddings`, cleanly slice the tensors from the left to keep the context within limits before generation.

## Verification
- Start the bridge and simulate a dropped connection mid-stream to ensure the lock remains held until the background thread finishes.
- Send a payload exceeding 8500 tokens to verify that truncation successfully prevents the RoPE out-of-bounds crash.
