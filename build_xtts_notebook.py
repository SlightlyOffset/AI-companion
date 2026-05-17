import json
import os

def build_xtts_notebook():
    """Builds the XTTS_Bridge.ipynb notebook using isolated Python 3.10 logic."""
    
    # 1. Environment Setup Cell (Python 3.10 Isolation)
    setup_code = [
        "# @title 1. Prepare Environment (Python 3.10 Isolation)\n",
        "import os\n",
        "import sys\n",
        "\n",
        "print(f\"Current System Python: {sys.version}\")\n",
        "print(\"Installing Python 3.10 and build essentials...\")\n",
        "!apt-get update -qq\n",
        "!apt-get install -y python3.10 python3.10-venv python3.10-dev libsndfile1 build-essential -qq\n",
        "\n",
        "print(\"Creating isolated virtual environment (Python 3.10)...\")\n",
        "!python3.10 -m venv /content/venv\n",
        "\n",
        "print(\"Installing dependencies inside virtual environment...\")\n",
        "!/content/venv/bin/pip install --upgrade pip -q\n",
        "!/content/venv/bin/pip install -q fastapi uvicorn python-multipart\n",
        "\n",
        "print(\"Installing ML binaries (Pinned for CUDA 12.1 compatibility)...\")\n",
        "# Pining to 2.4.0 + cu121 satisfies newer transformers while avoiding CUDA 13 errors\n",
        "!/content/venv/bin/pip install -q torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu121\n",
        "\n",
        "print(\"Installing compatible Transformers...\")\n",
        "!/content/venv/bin/pip install -q transformers==4.38.2\n",
        "\n",
        "print(\"Installing TTS (Coqui) inside venv...\")\n",
        "# 0.22.0 is the most stable version for XTTS v2 on 3.10\n",
        "!/content/venv/bin/pip install -q TTS==0.22.0\n",
        "\n",
        "print(\"\\n✅ Environment Ready (Isolated in /content/venv)!\")"
    ]

    # 2. Bridge Server Cell
    with open('colab_bridge/xtts_bridge_source.py', 'r', encoding='utf-8') as f:
        source_code = f.read()

    server_cell_code = [
        "# @title 2. Create Bridge Script\n",
        "with open(\"bridge_server.py\", \"w\") as f:\n",
        "    f.write(\"\"\"" + source_code.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$') + "\"\"\")\n",
        "print(\"✅ Bridge script created.\")"
    ]

    # 3. Tunnel and Run Cell
    run_code = [
        "# @title 3. Start XTTS Bridge\n",
        "import subprocess, time, re, os\n",
        "\n",
        "# Download cloudflared if not present\n",
        "cf_path = os.path.expanduser(\"~/.cloudflared/cloudflared\")\n",
        "if not os.path.exists(cf_path):\n",
        "    os.makedirs(os.path.dirname(cf_path), exist_ok=True)\n",
        "    print(\"Downloading cloudflared...\")\n",
        "    !curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o {cf_path}\n",
        "    !chmod +x {cf_path}\n",
        "\n",
        "# Start cloudflared tunnel\n",
        "print(\"Starting Cloudflare Quick Tunnel...\")\n",
        "proc = subprocess.Popen([cf_path, \"tunnel\", \"--url\", \"http://localhost:8001\"], stderr=subprocess.PIPE, text=True)\n",
        "\n",
        "public_url = None\n",
        "for _ in range(15):\n",
        "    line = proc.stderr.readline()\n",
        "    if '.trycloudflare.com' in line:\n",
        "        match = re.search(r'https://[a-z0-9\\-]+\\.trycloudflare\\.com', line)\n",
        "        if match:\n",
        "            public_url = match.group(0)\n",
        "            break\n",
        "    time.sleep(1)\n",
        "\n",
        "if public_url:\n",
        "    print(\"=\"*50)\n",
        "    print(f\"\\n🚀 XTTS BRIDGE ONLINE!\\n\")\n",
        "    print(f\"URL: {public_url}\\n\")\n",
        "    print(\"=\"*50)\n",
        "    !source /content/venv/bin/activate && /content/venv/bin/python -m uvicorn bridge_server:app --host 0.0.0.0 --port 8001 --log-level info\n",
        "else:\n",
        "    print(\"❌ Failed to start tunnel.\")"
    ]

    # Define the notebook JSON structure
    notebook = {
      "cells": [
        {
          "cell_type": "markdown",
          "metadata": {},
          "source": [
            "# 🎙️ AI Companion: XTTS v2 Remote Voice Bridge\n\n",
            "### 🛠️ Setup Instructions\n",
            "1. **GPU**: `Runtime` > `Change runtime type` > **T4 GPU**.\n",
            "2. **Run All**: `Ctrl + F9`.\n\n",
            "**Note**: This version uses a Python 3.10 virtual environment for stability."
          ]
        },
        {
          "cell_type": "code",
          "execution_count": None,
          "metadata": {},
          "outputs": [],
          "source": setup_code
        },
        {
          "cell_type": "code",
          "execution_count": None,
          "metadata": {},
          "outputs": [],
          "source": server_cell_code
        },
        {
          "cell_type": "code",
          "execution_count": None,
          "metadata": {},
          "outputs": [],
          "source": run_code
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

    target_path = 'colab_bridge/XTTS_Bridge.ipynb'
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)

    print(f"Successfully rebuilt {target_path}")

if __name__ == "__main__":
    build_xtts_notebook()
