# Specification: Bridge Stability & Thread-Safety Fix

## Problem
The `standalone_llm_bridge.py` experiences intermittent `CUDA error: an illegal memory access was encountered` during multi-worker operation or streaming.

## Root Causes
1. **Dangling Threads:** When `t.ai` times out (60s), the bridge lock is released but the generation thread continues, causing collisions.
2. **Global Syncs:** `torch.cuda.empty_cache()` forces global synchronizations that break parallel batch generation.
3. **Context Overflow:** Lack of prompt truncation leads to RoPE kernel out-of-bounds access on long conversations.

## Requirements
- Ensure generation threads are joined before worker locks are released.
- Remove redundant global CUDA cache clearing.
- Implement server-side context window enforcement (8k tokens).
