# 🤖 t.ai - Terminal AI Desktop Companion

**Current Status: [Alpha 0.1.0]**

A lightweight, highly immersive, profile-based AI companion that lives in your terminal. Built for roleplayers and AI enthusiasts who want a character that feels alive, remembers the past, and has a distinct personality.

---

## ✨ Key Features

### 🖥️ Modern TUI (Terminal User Interface)

* **Minimalist Bubble Layout**: A clean, distraction-free chat interface with right-aligned user messages and left-aligned companion responses.
* **Sixel/Kitty Image Rendering**: High-fidelity character portraits integrated directly into the terminal for deeper immersion.
* **Real-time Streaming**: Watch your companion "think" and type in real-time within immersive side-bordered bubbles.
* **Immersive Styling**: Automatic italicization and dimming of RP narration (`*actions*`) to separate dialogue from description.
* **Persistent Sidebars**: Real-time tracking of relationship scores, mood labels, and active profiles (Toggle with `Ctrl+B`).

### 🎙️ Advanced Audio & Voice Cloning

* **Multi-Voice TTS**: Automatically switches between a narrator voice for actions (`*...*`) and a character voice for dialogue.
* **Voice Cloning (XTTS v2)**: Clone distinct voices locally or via Colab, giving your companion a truly unique and realistic voice.
* **Hybrid Offloading**: Intelligent switching between local CPU/GPU and remote GPU pools (Colab/Kaggle) for zero-latency TTS playback.
* **Pipelined Streaming**: Uses a multi-threaded queue system to generate and play audio *while* the LLM is still typing. Zero latency.

### 📈 Relationship & Mood Engine

* **Persistence**: A -100 to +100 relationship meter that dictates the AI's tone and obedience.
* **Mood Decay & Sentiment Awareness**: The character remembers how long it's been since you last chatted. The AI self-reports its emotional state based on your interactions, updating its profile in real-time.

### 🎭 Deep Character Immersion & Memory

* **Rolling Summarization & Memory Core**: Automatically condenses long histories (>15 messages) into a "Memory Core" injected into every interaction to preserve long-term narrative recall.
* **Dynamic Lorebook (World Info)**: Efficiently injects relevant world or character facts into the LLM context based on keywords detected in the conversation.
* **Persistent History & Recaps**: Saves chat history persistently per profile and automatically generates a recap of your previous session on startup.

### 🔒 Security & Privacy

* **Privacy-First Design**: Mandatory HTTPS for remote services and secure masking of API tokens/sensitive keys in the UI.
* **Security Hardened**: Recently completed a comprehensive remediation sprint (May 2026) to address prompt injection (VULN-001), path traversal (VULN-003), and privacy leaks (VULN-004).
* **Isolated Data**: All history and settings are scoped to the active profile to prevent cross-character data leakage.

---

## 🚀 Getting Started

### Prerequisites

* **Python 3.10+**
* **Ollama** (Local LLM runner)
* **Terminal with Sixel/Kitty support** (e.g., WezTerm, Alacritty, iTerm2) for image rendering.

### Installation

1. **Clone the repo:**

    ```bash
    git clone https://github.com/SlightlyOffset/t.ai.git
    cd t.ai
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Pull the recommended model:**

    ```bash
    ollama pull fluffy/l3-8b-stheno-v3.2
    ```

### Running the Companion

Simply run the main launcher to start the TUI:

```bash
python main.py
```

---

## 🎮 Commands & Shortcuts

Inside the chat, you can use operational commands or keyboard shortcuts:

* `Ctrl+B`: Toggle sidebar visibility.
* `//help`: Show all commands.
* `//mode`: Toggle between RP and Casual modes.
* `//change_character`: Swap to a different character profile.
* `//change_user_profile`: Swap to a different user profile.
* `//import_card <path>`: Imports a SillyTavern character card.
* `//restart`: Cleanly reboot the application.

---

## 🛠️ Configuration

Edit `settings.json` to customize your experience:

* `remote_llm_url` / `remote_tts_url`: Set these to your Colab/Kaggle tunneling endpoints for cloud offloading.
* `image_protocol`: Choose avatar rendering protocol (`auto`, `kitty`, `sixel`, `blocky`).
* `auto_recap_on_start`: Let the AI summarize the previous chat context upon booting.
* `privacy_mode`: Redact sensitive information from being sent to remote LLMs.

---

## 📜 Roadmap

* [x] **Core Logic**: Mood Engine, Persistent Memory, and Relationships.
* [x] **Cloud & Audio**: Colab Bridge, Streaming TTS, and XTTS v2 Integration.
* [x] **TUI Overhaul**: High-fidelity bubble layout and terminal image rendering.
* [x] **Security Sprint**: Comprehensive vulnerability remediation and hardening.
* [ ] **Agentic Intelligence (v0.2.0)**: Transform t.ai into an autonomous agent (File I/O, Code Execution).
* [ ] **Dedicated Command Mode**: Structured `Ctrl+!` input for complex task handling.
* [ ] **Live2D Integration**: Map mood scores to sprite changes and animations.
