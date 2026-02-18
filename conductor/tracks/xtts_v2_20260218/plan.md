# Implementation Plan - XTTS v2 Voice Cloning Implementation

This plan outlines the steps to implement high-fidelity voice cloning using XTTS v2, supporting both local GPU acceleration and remote offloading to Google Colab.

## Phase 1: Foundation & Project Structure [checkpoint: ab79ae2]

- [x] Task: Setup environment and project structure
    - [x] Create `/voices` directory for reference audio samples
    - [x] Update `.gitignore` to exclude large model files and cached audio outputs
    - [x] Create initial test suite for new TTS modules
- [x] Task: Update character profile schema and loading logic
    - [x] Write tests for profile validation including `voice_clone_ref` and `tts_engine` fields
    - [x] Update profile loading logic in `main.py` and `engines/utilities.py` to handle new XTTS configuration
- [x] Task: Conductor - User Manual Verification 'Foundation & Project Structure' (Protocol in workflow.md)

## Phase 2: Local XTTS Implementation

- [ ] Task: Implement local XTTS inference module
    - [ ] Write tests for local audio generation using XTTS v2 library
    - [ ] Create `engines/xtts_local.py` with GPU acceleration support
    - [ ] Implement VRAM-conscious model loading (optimized for RTX 3050 6GB)
- [ ] Task: Implement engine switching and fallback logic in `engines/tts_module.py`
    - [ ] Write tests for engine prioritization (XTTS -> Edge-TTS)
    - [ ] Update `generate_audio` to dynamically select the engine based on profile settings and availability
- [ ] Task: Conductor - User Manual Verification 'Local XTTS Implementation' (Protocol in workflow.md)

## Phase 3: Remote XTTS Bridge (Google Colab)

- [ ] Task: Develop XTTS Remote Bridge (Jupyter Notebook)
    - [ ] Create `XTTS_Bridge.ipynb` for deployment on Google Colab
    - [ ] Implement a lightweight API within the notebook to process generation requests
- [ ] Task: Implement remote XTTS client
    - [ ] Write tests for remote connectivity and binary audio data handling
    - [ ] Create `engines/xtts_remote.py` to handle communication with the Colab bridge
- [ ] Task: Conductor - User Manual Verification 'Remote XTTS Bridge (Google Colab)' (Protocol in workflow.md)

## Phase 4: Optimization (Caching) & Integration

- [ ] Task: Implement persistent audio caching
    - [ ] Write tests for content-hash based cache lookup
    - [ ] Implement `engines/audio_cache.py` to manage stored audio clips
- [ ] Task: Integrate caching into the primary TTS pipeline
    - [ ] Write tests for end-to-end cache hits during interaction
    - [ ] Update `engines/tts_module.py` to prioritize cache retrieval over generation
- [ ] Task: Conductor - User Manual Verification 'Optimization (Caching) & Integration' (Protocol in workflow.md)

## Phase 5: Refinement & UI Updates

- [ ] Task: Support Multi-Language Cloning
    - [ ] Write tests for language-specific generation using non-English references
    - [ ] Implement language parameter support in XTTS modules
- [ ] Task: Final UI updates and status indicators
    - [ ] Add terminal indicators to show generation status and the active TTS engine
- [ ] Task: Conductor - User Manual Verification 'Refinement & UI Updates' (Protocol in workflow.md)
