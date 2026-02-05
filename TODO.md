# Sassy AI Desktop Companion - TODO

## Phase 1: Foundation

- [x] Initialize Python virtual environment and install dependencies (`SpeechRecognition`, `pyttsx3`, `pyaudio`)
- [ ] Implement `src/voice.py` for Text-to-Speech (TTS) and Speech-to-Text (STT)
- [ ] Create basic `main.py` listener loop

## Phase 2: Personality & Logic

- [ ] Build the **Mood Engine** in `src/mood.py` (Randomized sass/obedience logic)
- [ ] Create `src/actions.py` with an initial app dictionary (e.g., Browser, Notepad)
- [ ] Integrate Mood Engine into the main loop (AI might refuse to open apps)

## Phase 3: Features & Polishing

- [ ] Train AI actual LLM model
- [ ] Add actual AI
- [ ] Add more complex triggers (time, weather, or jokes)
- [ ] Refine sassy response library
- [ ] Implement background operation / system tray support
- [ ] Finalize error handling for voice recognition failures
