"""Module to autonomously build the LLM Bridge Pro notebook from standalone logic."""

import json
import os


def build_notebook():
    """Builds the LLM_Bridge.ipynb notebook using standalone bridge logic."""
    # Read standalone code
    with open('colab_bridge/standalone_llm_bridge.py', 'r', encoding='utf-8') as f:
        standalone_code = f.read()

    # Find the main function index to strip CLI argument parsing
    main_idx = standalone_code.find('def main():')
    if main_idx == -1:
        raise ValueError("Could not find 'def main():' in standalone_llm_bridge.py")

    core_code = standalone_code[:main_idx]

    # Define the runner code for the notebook environment
    runner_code = '''
import nest_asyncio
nest_asyncio.apply()

# Detect Environment and Setup Universal Secret Retrieval
try:
    from google.colab import userdata
    ENV_TYPE = "colab"
except ImportError:
    try:
        from kaggle_secrets import UserSecretsClient
        user_secrets = UserSecretsClient()
        ENV_TYPE = "kaggle"
    except ImportError:
        ENV_TYPE = "local"

def get_secret(name):
    import os
    val = os.environ.get(name)
    if val: return val.strip()
    if ENV_TYPE == "colab":
        try: 
            s = userdata.get(name)
            return s.strip() if s else None
        except: pass
    elif ENV_TYPE == "kaggle":
        try: 
            s = user_secrets.get_secret(name)
            return s.strip() if s else None
        except: pass
    return None

# Configuration
MODEL_ID = "Sao10K/L3-8B-Stheno-v3.2"
HF_TOKEN = get_secret("HF_TOKEN")

print(f"Detected Environment: {ENV_TYPE}")
print(f"Loading Model: {MODEL_ID}")

# Initialize Managers
tunnel_manager = TunnelManager(tunnel_type="cloudflare", local_port=8000)
lore_manager = LoreManager()
llm_engine = LLMEngine(model_id=MODEL_ID, hf_token=HF_TOKEN)

# Start Tunnel and Server
public_url = tunnel_manager.start()
app = create_app(tunnel_manager, lore_manager, llm_engine)

if not public_url:
    print(f"[*] Tunnel unavailable. Local bridge: http://localhost:8000")
else:
    print(f"[🚀] BRIDGE ONLINE: {public_url}")

import uvicorn
config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
server = uvicorn.Server(config)

try:
    # Jupyter environments support top-level await
    await server.serve()
except KeyboardInterrupt:
    print("\\n[!] Server stopped by user.")
finally:
    tunnel_manager._cleanup()
'''


    # Construct the full code for the main execution cell
    cell_2_code = "# @title 2. Start Pro Bridge Server\n" + core_code + "\n" + runner_code

    # Define the notebook JSON structure
    notebook = {
      "cells": [
        {
          "cell_type": "markdown",
          "metadata": {},
          "source": [
            "# 🎭 AI Companion: Universal Roleplay Bridge (Pro)\n\n",
            "This notebook acts as a remote 'brain' for your AI Companion. It features the exact same logic as `standalone_llm_bridge.py`, including **Context Truncation**, **OOM Retries**, and **Semantic RAG** support.\n\n",
            "### 🛠️ Setup Instructions:\n",
            "1. **GPU Acceleration**: Go to `Runtime` > `Change runtime type` and ensure **T4 GPU** (or **T4 x2** on Kaggle) is selected.\n",
            "2. **Secrets (IMPORTANT)**: \n",
            "   - **Colab**: Click the **Key icon** (Secrets) on the left sidebar.\n",
            "   - **Kaggle**: Go to **Add-ons** > **Secrets**.\n",
            "   - Add `HF_TOKEN` with your [HuggingFace Token](https://huggingface.co/settings/tokens).\n",
            "   - No token required for Cloudflare Quick Tunnels! They are created on-demand.\n",
            "   - Enable access for the notebook.\n",
            "3. **Run All**: Press `Ctrl + F9` or go to `Runtime` > `Run all`.\n\n",
            "### 🔗 Connecting to the Local App:\n",
            "1. Wait for the final cell to display the **🚀 BRIDGE ONLINE!** message.\n",
            "2. Copy the **URL** (it will look like `https://xxxx.trycloudflare.com`).\n",
            "3. Open your local `settings.json` and paste the URL into `remote_llm_url`.\n",
            "4. Restart your local `main.py` script."
          ]
        },
        {
          "cell_type": "code",
          "execution_count": None,
          "metadata": {},
          "outputs": [],
          "source": [
            "# @title 1. Install Dependencies\n",
            "!pip install -q -U fastapi uvicorn pyngrok nest_asyncio requests python-dotenv\n",
            "!pip install -q -U transformers accelerate sentence-transformers scikit-learn\n",
            "!pip install -q -U torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121\n",
            "!pip install -q -U bitsandbytes nvidia-cuda-runtime-cu12 nvidia-nvjitlink-cu12"
          ]
        },
        {
          "cell_type": "code",
          "execution_count": None,
          "metadata": {},
          "outputs": [],
          "source": [cell_2_code]
        }
      ],
      "metadata": {
        "accelerator": "GPU",
        "colab": {
          "gpuType": "T4",
          "provenance": []
        },
        "kernelspec": {
          "display_name": "Python 3",
          "language": "python",
          "name": "python3"
        }
      },
      "nbformat": 4,
      "nbformat_minor": 5
    }

    # Write the notebook to disk
    target_path = 'colab_bridge/LLM_Bridge.ipynb'
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)

    print(f"Successfully rebuilt {target_path}")


def main():
    """Main entry point for building the notebook."""
    build_notebook()


if __name__ == "__main__":
    main()
