# 🎙️ High-Performance Voice Cloning (StyleTTS 2)

## 📋 Overview
To achieve the lowest possible latency and best VRAM efficiency on an **RTX 3050 (6GB VRAM)**, we are transitioning from XTTS v2 to **StyleTTS 2**. This allows for high-fidelity, zero-shot voice cloning with significantly lower resource overhead.

### **Why StyleTTS 2?**
- **VRAM Usage**: ~2GB (XTTS v2 is ~4GB+).
- **Speed**: 40x-80x real-time (XTTS v2 is ~1-2x).
- **Quality**: Better prosody and natural flow for roleplay.

---

## 🛠️ Step 1: Environment Setup
*   **System Dependency**: Install `espeak-ng`.
    *   **Windows**: Download and install from [espeak-ng releases](https://github.com/espeak-ng/espeak-ng/releases). Add to System PATH.
*   **Python Dependencies**:
    *   `pip install styletts2`
*   **Model Storage**: Checkpoints (~400MB) will be automatically managed or stored in `models/tts/`.

## 🎤 Step 2: Voice Sampling
*   **Reference Audio**: Requires a 5-10 second `.wav` file.
*   **Quality**: Must be clean (no background noise), mono, 24kHz or 44.1kHz.
*   **Storage**: Store in `voices/{character}/reference.wav`.

## 💻 Step 3: Code Integration (`engines/tts_module.py`)
*   **Implementation**: 
    *   Initialize `StyleTTS2` as a singleton worker.
    *   Use `inference(text, target_voice_path=...)` for generation.
*   **Fallback**: Maintain `edge-tts` as a zero-resource fallback if the GPU is unavailable.

## ⚙️ Step 4: Configuration (`settings.json` / `.env`)
*   `"tts_engine": "styletts2"`
*   `"use_local_cloning": true`
*   `"cloning_reference_file": "voices/Astgenne/reference.wav"`

---

## 🔄 Workflow
1.  **App** detects `tts_engine: "styletts2"` and loads the model into VRAM (~2GB).
2.  **LLM** generates response chunks.
3.  **StyleTTS 2** performs instant inference using the character's reference `.wav`.
4.  **Audio** plays with near-zero latency, even while running a local 4-bit LLM.
