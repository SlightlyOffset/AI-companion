# 🎭 AI Companion: Universal Roleplay Bridge (Pro)

This notebook acts as a remote 'brain' for your AI Companion. It features the exact same logic as `standalone_llm_bridge.py`, including **Context Truncation**, **OOM Retries**, and **Semantic RAG** support.

### 🛠️ Setup Instructions:
1. **GPU Acceleration**: Go to `Runtime` > `Change runtime type` and ensure **T4 GPU** (or **T4 x2** on Kaggle) is selected.
2. **Secrets (IMPORTANT)**: 
   - **Colab**: Click the **Key icon** (Secrets) on the left sidebar.
   - **Kaggle**: Go to **Add-ons** > **Secrets**.
   - Add `HF_TOKEN` with your [HuggingFace Token](https://huggingface.co/settings/tokens).
   - No token required for Cloudflare Quick Tunnels! They are created on-demand.
   - Enable access for the notebook.
3. **Run All**: Press `Ctrl + F9` or go to `Runtime` > `Run all`.

### 🔗 Connecting to the Local App:
1. Wait for the final cell to display the **🚀 BRIDGE ONLINE!** message.
2. Copy the **URL** (it will look like `https://xxxx.trycloudflare.com`).
3. Open your local `settings.json` and paste the URL into `remote_llm_url`.
4. Restart your local `main.py` script.
