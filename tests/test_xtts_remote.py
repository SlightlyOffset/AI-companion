import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the project root to sys.path to import engines
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestXTTSRemote(unittest.TestCase):

    @patch('engines.xtts_remote.requests.post')
    @patch('engines.xtts_remote.get_setting')
    def test_generate_audio_remote_success(self, mock_get_setting, mock_post):
        from engines.xtts_remote import generate_remote_xtts
        mock_get_setting.return_value = "https://mock-bridge.ngrok.app"
        
        # Mock successful response with binary content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake-audio-data"
        mock_post.return_value = mock_response
        
        # We need a dummy reference file for the test
        with open("dummy_ref.wav", "wb") as f: f.write(b"dummy")
        
        result = generate_remote_xtts("Hello", "output.wav", "dummy_ref.wav")
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists("output.wav"))
        
        # Cleanup
        if os.path.exists("output.wav"): os.remove("output.wav")
        if os.path.exists("dummy_ref.wav"): os.remove("dummy_ref.wav")

    @patch('engines.xtts_remote.get_setting')
    def test_generate_remote_fails_without_url(self, mock_get_setting):
        from engines.xtts_remote import generate_remote_xtts
        mock_get_setting.return_value = None
        
        result = generate_remote_xtts("Hello", "output.wav", "ref.wav")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
