# Sassy AI Desktop Companion - TODO

## Phase 1: Foundation
- [x] Initialize Python environment and core dependencies (`colorama`, `ollama`, `edge-tts`)
- [x] Implement **TTS Module** with Edge Neural voices and `pyttsx3` fallback
- [x] Create Terminal-based **Profile Picker**
- [x] Build core `main.py` loop with character loading
- [ ] Implement Speech-to-Text (STT) for full voice control

## Phase 2: Personality & Logic
- [x] Build the **Mood Engine** (Weight-based obedience logic)
- [x] Create `engines/actions.py` with app dictionary (Browser, Notepad, etc.)
- [x] Integrate Ollama (Llama3) for actual AI intelligence
- [x] Implement **RP Screening** (Stripping `*narration*` from TTS)
- [x] Synchronize LLM responses with Mood Engine decisions (Hard-enforced obedience/refusal)

## Phase 3: Persistent Memory & Relationships (Next)
- [ ] **Persistent Chat History**: Save/Load conversations to JSON per profile
- [ ] **Context Window Management**: Feed last 10-15 messages back to the AI for short-term memory
- [ ] **Dynamic Mood Score**: Replace random rolls with a -100 to +100 relationship meter
- [ ] **Sentiment Analysis**: Update mood based on user being "Nice" or "Mean"
- [ ] **Mood Decay**: Implement logic for the AI to "calm down" over time

## Phase 4: Features & Polishing
- [ ] Add more complex triggers (time, weather, or custom jokes)
- [ ] Implement background operation / system tray support
- [ ] Source or record custom voice for **Voice Cloning (XTTS v2)**
- [ ] Finalize error handling for offline/online transitions