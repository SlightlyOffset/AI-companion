# Tech Stack - AI Desktop Companion

## Programming Languages
- **Python 3.10+**: Core application logic.
- **Jupyter Notebook (.ipynb)**: Used for the Colab-based remote inference bridge.

## AI and LLM (Inference)
- **Ollama**: Primary local LLM execution engine.
- **Google Colab (Remote)**: Supported for offloading LLM inference via the `LLM_Bridge.ipynb`, enabling usage on low-end hardware with limited VRAM.
- **ollama (library)**: Python bindings for Ollama API.

## Text-to-Speech (TTS)
- **edge-tts**: Primary engine using Microsoft Edge's high-fidelity neural voices.
- **pyttsx3**: Fallback engine for local, offline TTS.

## User Interface
- **Terminal (CLI)**: Primary interaction layer.
- **colorama**: Terminal styling and ANSI color support.

## Data and Persistence
- **JSON**: Storage format for character profiles, user profiles, chat history, and application settings.

## Network and Communication
- **requests**: HTTP library for communication with local/remote LLM APIs.

## Target Platform
- **Windows (win32)**: Primary development and execution environment.
