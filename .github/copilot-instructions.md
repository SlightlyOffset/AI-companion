# AI Companion – Copilot Instructions

## Running the App

```bash
python main.py
```

Requires Ollama running locally with a loaded model (default: `fluffy/l3-8b-stheno-v3.2`).

## Tests

Run the full test suite (from the project root):

```bash
python -m pytest tests/
```

Run a single test file:

```bash
python -m pytest tests/test_memory_v2.py
```

Run a single test case:

```bash
python -m pytest tests/test_memory_v2.py::TestHistoryManager::test_save_and_load
```

## Architecture Overview

The app is a terminal-based AI roleplay companion with a pipelined multi-threaded TTS system.

**Core data flow:**

1. `main.py` — Entry point and interaction loop. Spins up two background threads per turn:
   - `tts_generation_worker`: reads from `tts_text_queue`, calls `generate_audio()`, pushes temp MP3 paths to `audio_file_queue`
   - `tts_playback_worker`: reads from `audio_file_queue`, calls `play_audio()` in order

2. `engines/responses.py` — Streams LLM output (Ollama local or HTTP remote). Parses and strips `[REL: ±N]` sentiment tags in real-time; persists score changes and saves history after each turn.

3. `engines/prompts.py` — Assembles the full system prompt from: character profile fields + user profile fields + relationship label + behavioral rules. The `[REL: ±N]` tag is instructed here (rule #4).

4. `engines/tts_module.py` — TTS engine dispatch: edge-tts (primary) → XTTS local → XTTS remote → pyttsx3 (offline fallback). Results are cached by MD5 hash of `text|voice|engine`.

5. `engines/memory_v2.py` — `HistoryManager` (singleton `memory_manager`) stores per-profile history as `{metadata, history}` JSON in `history/`. Handles old list-format migration.

6. `engines/config.py` — All settings read/write live-reload from `settings.json`. **There is no in-memory config cache** — `get_setting()` opens the file every call.

## Key Conventions

### Character & User Profiles
- Character profiles: `profiles/<Name>.json` — use `profiles/profile_template.json` as the schema reference.
- User profiles: `user_profiles/<Name>.json` — same shape but describes the human user.
- The `relationship_score` field in the character profile JSON is mutated directly at runtime by `update_profile_score()` and `apply_mood_decay()`.
- History files are stored as `history/<ProfileName>_history.json`. The filename key is derived from the profile filename without extension (not the `name` field).

### Narration vs. Dialogue
- Text wrapped in `*...*` is treated as narration (actions). Everything outside is spoken dialogue.
- In the terminal: narration renders in italic dim grey; dialogue renders in the character's profile color.
- In TTS: `get_smart_split_points()` splits on `*` boundaries and sentence-ending punctuation, toggling between narrator voice and character voice per segment.
- `clean_text_for_tts()` either strips narration symbols (keeping text) or strips narration text entirely based on the `speak_narration` setting.

### Sentiment Tag Protocol
- The LLM is instructed (via `build_system_prompt`) to end every reply with `[REL: +N]`, `[REL: -N]`, or `[REL: 0]` (range −5 to +5).
- This tag is filtered from both the terminal stream and saved history; only the numeric delta is applied to `relationship_score`.

### In-app Commands
- All runtime commands are prefixed with `//` (e.g., `//help`, `//reset`, `//toggle_speak`).
- Commands are dispatched in `engines/app_commands.py`. `RestartRequested` is a sentinel exception caught by `main()` to re-run `run_app()`.

### TTS Engine Selection per Profile
- Each character profile can specify `tts_engine` (`"edge-tts"` or `"xtts"`), `preferred_tts_voice`, `voice_clone_ref`, and `tts_language`.
- Narrator voice is always edge-tts (`narration_tts_voice` setting); only character dialogue uses XTTS.

### Settings
- `settings.json` is the single source of truth for runtime config. `update_setting()` writes it immediately on every call (including on each profile/character switch).
- `debug_mode: true` prints the final cleaned TTS text to the terminal before generation.

### Colab Bridge (Remote GPU)
Two Jupyter notebooks in `colab_bridge/` offload compute to a Google Colab T4 GPU when local hardware is insufficient:

| Notebook | Purpose | `settings.json` key |
|---|---|---|
| `LLM_Bridge.ipynb` | Runs `Sao10K/L3-8B-Stheno-v3.2` via HuggingFace + streams responses over a FastAPI `/chat` endpoint | `remote_llm_url` |
| `XTTS_Bridge.ipynb` | Runs XTTS v2 for voice cloning over a FastAPI `/generate_tts` endpoint | `remote_tts_url` |

Both tunnels are exposed via **Ngrok**. Setup requires `HF_TOKEN` (LLM only) and `NGROK_TOKEN` stored as Colab Secrets.

**Connecting a bridge:**
1. Run all cells in the notebook — wait for the `BRIDGE ONLINE!` message and copy the Ngrok URL.
2. Paste the URL into `settings.json` under the appropriate key.
3. Restart `main.py` — the local app automatically routes to the remote endpoint when the key is set (non-null).

**API contract:**
- LLM bridge: `POST /chat` — body: `{messages, temperature, max_tokens}`, response: streaming plain text.
- XTTS bridge: `POST /generate_tts` — multipart form with `text`, `language`, and `speaker_file` (WAV); returns a WAV file. The local client is in `engines/xtts_remote.py`; the `speaker_file` path comes from `voice_clone_ref` in the character profile.

**Important:** `XTTS_Bridge.ipynb` pins `torch==2.5.1` (not latest) to avoid a PyTorch 2.6 `weights_only` security error with XTTS v2.

### Platform Note
- Primary target is **Windows**. Audio playback uses VBScript (`WMPlayer.OCX`) with `os.startfile` as fallback. Unix path is present but minimally tested.
