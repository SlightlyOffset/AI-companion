#!/usr/bin/env python3
"""
Standalone LLM Bridge for Colab/Kaggle with optional Cloudflare Quick Tunnel support.

This script can run as a standalone HTTP server that bridges local requests to
a remote LLM endpoint. It supports both Ngrok and Cloudflare Quick Tunnels for
exposing the bridge to the internet.

Usage:
    python standalone_llm_bridge.py --tunnel cloudflare
    python standalone_llm_bridge.py --tunnel ngrok
    python standalone_llm_bridge.py  # No tunnel, local only
"""

import argparse
import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Silence noisy third-party libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.ERROR)

# Disable TQDM progress bars (HF downloads)
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"


class LoreManager:
    """Manages vector embeddings and semantic retrieval of lore entries."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        global SENTENCE_TRANSFORMERS_AVAILABLE
        self.model_name = model_name
        self.model = None
        self.lore_entries = []
        self.embeddings = None

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Still show this one as it's the main progress indicator
                print(f"[*] Initializing Lore Engine ({model_name})...")
                self.model = SentenceTransformer(model_name)
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                SENTENCE_TRANSFORMERS_AVAILABLE = False

    def embed_and_index(self, lorebook: dict) -> bool:
        """
        Embed all lore entries and store them in memory.

        Args:
            lorebook: Dictionary with 'entries' list containing lore items

        Returns:
            bool: True if indexing succeeded, False otherwise
        """
        if not self.model:
            logger.warning("Embedding model not available; RAG disabled")
            return False

        try:
            entries = lorebook.get("entries", [])
            if not entries:
                self.lore_entries = []
                self.embeddings = np.array([])
                return True

            # Filter and prepare entries
            self.lore_entries = [
                entry for entry in entries
                if entry.get("enabled", True)
            ]

            if not self.lore_entries:
                self.embeddings = np.array([])
                return True

            # Extract text content to embed
            texts_to_embed = [
                f"{entry.get('title', '')} {entry.get('content', '')}"
                for entry in self.lore_entries
            ]

            self.embeddings = self.model.encode(texts_to_embed, convert_to_numpy=True)
            print(f"[+] Successfully indexed {len(self.lore_entries)} lore entries")
            return True

        except Exception as e:
            logger.error(f"Failed to embed and index lorebook: {e}")
            return False

    def retrieve_top_k(self, query: str, k: int = 3) -> list[str]:
        """
        Retrieve top K most similar lore entries using cosine similarity.

        Args:
            query: User's message to search for
            k: Number of top entries to retrieve

        Returns:
            list[str]: Formatted lore entries, or empty list if retrieval failed
        """
        if not self.model or not self.lore_entries or len(self.lore_entries) == 0:
            return []

        try:
            # Embed the query
            query_embedding = self.model.encode(query, convert_to_numpy=True)

            # Compute cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity([query_embedding], self.embeddings)[0]

            # Get top K indices
            top_k_indices = np.argsort(similarities)[::-1][:k]

            # Filter by threshold (only return if similarity > 0.3)
            relevant_entries = []
            for idx in top_k_indices:
                if similarities[idx] > 0.3:
                    entry = self.lore_entries[idx]
                    relevant_entries.append(
                        f"[LORE: {entry.get('title', 'Unknown')}]\n{entry.get('content', '')}"
                    )

            return relevant_entries

        except Exception as e:
            logger.error(f"Error retrieving lore: {e}")
            return []


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    max_tokens: int = 1024
    temperature: float = 0.8
    model: str = "default"
    use_rag: bool = False


class SyncLoreRequest(BaseModel):
    entries: list = []



class TunnelManager:
    """Manager for Cloudflare and Ngrok tunnels."""

    def __init__(self, tunnel_type: str = "none", local_port: int = 8000):
        self.tunnel_type = tunnel_type
        self.local_port = local_port
        self.public_url: Optional[str] = None
        self.process = None

    def start(self) -> Optional[str]:
        """Start the tunnel and return the public URL."""
        if self.tunnel_type == "cloudflare":
            return self._start_cloudflare()
        elif self.tunnel_type == "ngrok":
            return self._start_ngrok()
        else:
            print(f"[*] Local mode: http://localhost:{self.local_port}")
            return None

    def _start_cloudflare(self) -> Optional[str]:
        """Start Cloudflare Quick Tunnel."""
        cf_path = self._get_cloudflared_path()
        if not os.path.exists(cf_path):
            print("[*] Downloading cloudflared...")
            self._download_cloudflared(cf_path)

        try:
            # Start cloudflared tunnel
            self.process = subprocess.Popen(
                [cf_path, "tunnel", "--url", f"http://localhost:{self.local_port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Read output to extract URL
            self.public_url = self._extract_cloudflare_url()

            if self.public_url:
                print(f"\n[🚀] BRIDGE ONLINE: {self.public_url}\n")
                return self.public_url
            else:
                logger.error("Failed to extract Cloudflare URL")
                self._cleanup()
                return None

        except Exception as e:
            logger.error(f"Failed to start Cloudflare tunnel: {e}")
            self._cleanup()
            return None

    def _start_ngrok(self) -> Optional[str]:
        """Start Ngrok tunnel (requires pyngrok and NGROK_TOKEN env var)."""
        try:
            from pyngrok import ngrok
        except ImportError:
            logger.error("pyngrok not installed. Install with: pip install pyngrok")
            return None

        try:
            ngrok_token = os.getenv("NGROK_TOKEN")
            if ngrok_token:
                ngrok.set_auth_token(ngrok_token)

            self.public_url = ngrok.connect(self.local_port).public_url
            print(f"\n[🚀] BRIDGE ONLINE: {self.public_url}\n")
            return self.public_url

        except Exception as e:
            logger.error(f"Failed to start Ngrok tunnel: {e}")
            return None

    def _get_cloudflared_path(self) -> str:
        """Get path to cloudflared binary."""
        home = os.path.expanduser("~")
        cf_dir = os.path.join(home, ".cloudflared")
        os.makedirs(cf_dir, exist_ok=True)
        return os.path.join(cf_dir, "cloudflared")

    def _download_cloudflared(self, cf_path: str):
        """Download cloudflared binary for Linux amd64."""
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

        try:
            subprocess.run(
                ["curl", "-L", "-s", "-o", cf_path, url],
                check=True
            )
            os.chmod(cf_path, 0o755)
        except Exception as e:
            logger.error(f"Failed to download cloudflared: {e}")
            raise

    def _extract_cloudflare_url(self) -> Optional[str]:
        """Extract Cloudflare URL from process output (reads stderr and stdout)."""
        if not self.process:
            return None

        try:
            output_lines = []
            for attempt in range(20):  # Wait up to 20s
                if self.process.poll() is not None:
                    break

                # Try to read from stderr (non-blocking)
                try:
                    if self.process.stderr:
                        line = self.process.stderr.readline()
                        if line:
                            output_lines.append(line)
                except Exception:
                    pass

                # Check accumulated output for URL
                combined = ''.join(output_lines)
                match = re.search(r'(https://[a-z0-9\-]+\.trycloudflare\.com)', combined)
                if match:
                    return match.group(1)

                time.sleep(1)

        except Exception as e:
            logger.error(f"Error extracting Cloudflare URL: {e}")

        return None

    def _cleanup(self):
        """Clean up tunnel process."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass


def create_app(tunnel_manager: Optional[TunnelManager] = None, lore_manager: Optional[LoreManager] = None) -> FastAPI:
    """Create FastAPI app for the bridge."""
    app = FastAPI(title="LLM Bridge", version="1.0.0")

    if lore_manager is None:
        lore_manager = LoreManager()

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "tunnel_type": tunnel_manager.tunnel_type if tunnel_manager else "none",
            "public_url": tunnel_manager.public_url if tunnel_manager else None,
            "rag_enabled": bool(lore_manager.model),
            "lore_entries_indexed": len(lore_manager.lore_entries)
        }

    @app.post("/sync_lore")
    async def sync_lore(request: dict):
        """Sync and index lorebook entries for semantic retrieval."""
        try:
            if not lore_manager.model:
                return {
                    "status": "error",
                    "message": "Embedding model not available; RAG disabled"
                }

            lorebook = {"entries": request.get("entries", [])}
            success = lore_manager.embed_and_index(lorebook)

            if success:
                return {
                    "status": "success",
                    "message": f"Indexed {len(lore_manager.lore_entries)} lore entries",
                    "entries_count": len(lore_manager.lore_entries)
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to index lorebook"
                }
        except Exception as e:
            logger.error(f"Error in /sync_lore: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    @app.post("/chat")
    async def chat(request: ChatRequest):
        """Chat endpoint that streams responses, with optional server-side RAG."""
        # Prepare messages for LLM
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

        # Server-side RAG: retrieve lore and inject into system prompt
        if request.use_rag and lore_manager.model and len(messages) > 0:
            # Get the user's latest message for RAG query
            user_message = None
            for msg in reversed(messages):
                if msg["role"] == "user":
                    user_message = msg["content"]
                    break

            if user_message:
                retrieved_lore = lore_manager.retrieve_top_k(user_message, k=3)
                if retrieved_lore:
                    lore_text = "\n\n".join(retrieved_lore)
                    # Inject into system prompt
                    for i, msg in enumerate(messages):
                        if msg["role"] == "system":
                            messages[i]["content"] = f"{lore_text}\n\n{msg['content']}"
                            break

        # This is a placeholder implementation
        # In a real scenario, this would connect to an LLM (Ollama, vLLM, etc.)
        async def generate():
            yield "This is a placeholder response from the LLM Bridge. "
            yield "In a production setup, this would connect to your actual LLM endpoint."

        return StreamingResponse(generate(), media_type="text/plain")

    return app



def main():
    parser = argparse.ArgumentParser(
        description="Standalone LLM Bridge with optional tunneling and semantic RAG"
    )
    parser.add_argument(
        "--tunnel",
        choices=["none", "cloudflare", "ngrok"],
        default="none",
        help="Tunnel type to use for exposing the bridge"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Local port to run the server on"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to"
    )

    args = parser.parse_args()

    # Create tunnel manager
    tunnel_manager = TunnelManager(tunnel_type=args.tunnel, local_port=args.port)

    # Create LoreManager for semantic RAG
    lore_manager = LoreManager()

    # Start tunnel if enabled
    if args.tunnel != "none":
        public_url = tunnel_manager.start()
        if not public_url:
            logger.error(f"Failed to start {args.tunnel} tunnel")
            sys.exit(1)

    # Create FastAPI app
    app = create_app(tunnel_manager, lore_manager)

    # Run server
    try:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="warning"
        )
    except KeyboardInterrupt:
        pass
    finally:
        if tunnel_manager:
            tunnel_manager._cleanup()



if __name__ == "__main__":
    main()
