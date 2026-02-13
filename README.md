# 🤖 Terminal-based AI Desktop Companion

A lightweight, highly immersive, and technically "bratty" AI companion that lives in your terminal. Built for roleplayers and AI enthusiasts who want a character that feels alive, remembers the past, and has a distinct personality.

---

## ✨ Key Features

### 🎙️ Zero-Latency Multi-Voice TTS

* **Narrator & Character**: Automatically switches between a narrator voice for actions (`*...*`) and a character voice for dialogue.
* **Pipelined Workers**: Uses a multi-threaded queue system to generate and play audio *while* the LLM is still typing. No more waiting for the AI to finish thinking before it starts speaking.
* **Edge Neural Support**: Powered by Microsoft's high-fidelity neural voices.

### 📈 Relationship & Mood Engine

* **Persistence**: A -100 to +100 relationship meter that dictates the AI's tone and obedience.
* **Mood Decay**: The character remembers how long it's been since you last chatted. If you disappear for days, their feelings will shift back toward neutral.
* **Sentiment Awareness**: The AI self-reports its emotional state, updating its profile in real-time based on your interaction.

### 🎭 Deep Character Immersion

* **Enriched Profiles**: Characters have backstories, physical appearances, likes/dislikes, and specific mannerisms they weave into their roleplay.
* **Manganese Integration**: Support for detailed User Profiles so the AI knows exactly who it's talking to (down to your ember eyes and your pet fur-ball, Critter).
* **Roleplay Preservation**: Advanced regex and smart-splitting ensure that narration is styled correctly (Italics/Grey) and filtered properly for the voice engine.

### ⚡ Technical Efficiency

* **Ultra-Lightweight**: Minimal CPU/RAM footprint. It leaves almost 100% of your hardware for the LLM.
* **CLI First**: No heavy GUI overhead. Beautiful terminal rendering with dynamic colors and styles.
* **Hybrid LLM Support**: Optimized for **Ollama** (specifically tested with Stheno-v3.2 on 6GB VRAM) but supports remote APIs as well.

---

## 🚀 Getting Started

### Prerequisites

* **Python 3.10+**
* **Ollama** (Local LLM runner)
* **Microsoft Edge** (For neural TTS access)

### Installation

1. **Clone the repo:**

    ```bash
    git clone https://github.com/your-username/Sassy-AI-Companion.git
    cd Sassy-AI-Companion
    ```

2. **Install dependencies:**

    ```bash
    pip install colorama ollama requests edge-tts pyttsx3
    ```

3. **Pull the recommended model:**

    ```bash
    ollama pull fluffy/l3-8b-stheno-v3.2
    ```

### Running the Companion

```bash
python main.py
```

---

## 🎮 Commands

Inside the chat, you can use the following operational commands:

* `//help`: Show all commands.
* `//reset`: Clear the current conversation history.
* `//change_character`: Swap to a different profile (Glitch, Eira, Ria).
* `//show_settings`: View current app configuration.
* `//restart`: Cleanly reboot the application.

---

## 🛠️ Configuration

Edit `settings.json` to customize your experience:

* `tts_enabled`: Toggle voice on/off.
* `speak_narration`: Choose if the Narrator should speak the actions.
* `history_limit`: Control how much memory the AI has.

---

## 📜 Roadmap

* [ ] **Phase 3.5**: Dynamic Scene Memory (Location/Time tracking).
* [ ] **Phase 4**: Voice Cloning (XTTS v2) & Background operation.
* [ ] **STT**: Full voice-to-voice conversation support.

---

## 🤝 Contributing

Feel free to fork, submit PRs, or suggest "bratty" personality traits.

*Disclaimer: This is an early build. Expect some quirks and sass.*
