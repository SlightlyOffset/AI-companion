import importlib.util
from pathlib import Path
import unittest

try:
    from fastapi.testclient import TestClient
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


if FASTAPI_AVAILABLE:
    MODULE_PATH = Path(__file__).resolve().parents[1] / "colab_bridge" / "standalone_llm_bridge.py"
    SPEC = importlib.util.spec_from_file_location("standalone_llm_bridge", MODULE_PATH)
    BRIDGE = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(BRIDGE)


class FakeLoreManager:
    def __init__(self):
        self.model = object()
        self.lore_entries = []

    def retrieve_top_k(self, _query, k=3):
        return ["[LORE: test]\nMoonlight means caution."]


class FakeLLMEngine:
    def __init__(self):
        self.ready = True
        self.model_id = "fake/model"
        self.last_stream_messages = None
        self.last_batch_messages = None

    def generate_stream(self, messages, max_tokens=1024, temperature=0.8):
        self.last_stream_messages = messages
        yield "Hello"
        yield " world"

    def generate_batch(self, messages, max_tokens=1024, temperature=0.8, n=1):
        self.last_batch_messages = messages
        return [f"candidate-{i}" for i in range(1, n + 1)]


@unittest.skipUnless(FASTAPI_AVAILABLE, "fastapi is required for bridge endpoint tests")
class TestStandaloneLLMBridge(unittest.TestCase):
    def test_chat_stream_uses_engine_and_rag(self):
        lore_manager = FakeLoreManager()
        engine = FakeLLMEngine()
        app = BRIDGE.create_app(lore_manager=lore_manager, llm_engine=engine)
        client = TestClient(app)

        payload = {
            "messages": [
                {"role": "system", "content": "Stay in character."},
                {"role": "user", "content": "What should we do now?"},
            ],
            "use_rag": True,
            "n": 1,
        }
        response = client.post("/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "Hello world")
        self.assertIsNotNone(engine.last_stream_messages)
        self.assertIn("Moonlight means caution.", engine.last_stream_messages[0]["content"])
        self.assertIn("Stay in character.", engine.last_stream_messages[0]["content"])

    def test_chat_batch_returns_candidates_json(self):
        lore_manager = FakeLoreManager()
        engine = FakeLLMEngine()
        app = BRIDGE.create_app(lore_manager=lore_manager, llm_engine=engine)
        client = TestClient(app)

        payload = {
            "messages": [{"role": "user", "content": "Give options"}],
            "n": 3,
            "use_rag": False,
        }
        response = client.post("/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"candidates": ["candidate-1", "candidate-2", "candidate-3"]})
        self.assertIsNotNone(engine.last_batch_messages)

    def test_chat_fallback_when_no_engine(self):
        lore_manager = FakeLoreManager()
        app = BRIDGE.create_app(lore_manager=lore_manager, llm_engine=None)
        client = TestClient(app)

        batch_response = client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": "x"}], "n": 2},
        )
        self.assertEqual(batch_response.status_code, 200)
        self.assertEqual(
            batch_response.json(),
            {"candidates": [BRIDGE.FALLBACK_UNAVAILABLE_MESSAGE, BRIDGE.FALLBACK_UNAVAILABLE_MESSAGE]},
        )

        stream_response = client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": "x"}], "n": 1},
        )
        self.assertEqual(stream_response.status_code, 200)
        self.assertEqual(stream_response.text, BRIDGE.FALLBACK_UNAVAILABLE_MESSAGE)


if __name__ == "__main__":
    unittest.main()
