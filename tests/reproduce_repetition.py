
import unittest
from unittest.mock import MagicMock, patch
from engines.responses import _call_llm_once

class TestRepetitionFix(unittest.TestCase):
    """
    Empirical verification of the repetition penalty integration.
    This test ensures that the penalty is correctly passed to the backends.
    """

    @patch("engines.responses.get_setting")
    @patch("engines.responses.requests.post")
    def test_remote_bridge_receives_penalty(self, mock_post, mock_get_setting):
        # Setup: Mock setting to a high penalty to ensure it's distinct
        mock_get_setting.side_effect = lambda key, default=None: {
            "repetition_penalty": 1.5,
            "remote_llm_url": "http://mock-bridge"
        }.get(key, default)

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Test"}}, {"message": {"content": "Test"}}]}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        _call_llm_once(
            messages=[{"role": "user", "content": "repeat after me: hello"}],
            model="test-model",
            remote_url="http://mock-bridge"
        )

        # Verify: Check if the payload sent to the bridge contains the penalty
        payload = mock_post.call_args.kwargs["json"]
        print(f"\n[DEBUG] Remote Payload repetition_penalty: {payload.get('repetition_penalty')}")
        self.assertEqual(payload.get("repetition_penalty"), 1.5)

    @patch("engines.responses.get_setting")
    @patch("engines.responses.ollama.chat")
    def test_local_ollama_receives_penalty(self, mock_ollama_chat, mock_get_setting):
        # Setup
        mock_get_setting.side_effect = lambda key, default=None: {
            "repetition_penalty": 1.3
        }.get(key, default)

        mock_ollama_chat.return_value = {"message": {"content": "Test"}}

        _call_llm_once(
            messages=[{"role": "user", "content": "repeat after me: hello"}],
            model="test-model",
            remote_url=None
        )

        # Verify: Ollama uses 'repeat_penalty' in its 'options' dictionary
        options = mock_ollama_chat.call_args.kwargs.get("options", {})
        print(f"[DEBUG] Ollama Options repeat_penalty: {options.get('repeat_penalty')}")
        self.assertEqual(options.get("repeat_penalty"), 1.3)

if __name__ == "__main__":
    unittest.main()
