import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys

# Add the project root to sys.path to import engines
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engines.tts_module import generate_audio

class TestMultiLanguage(unittest.TestCase):

    @patch('engines.tts_module.get_cache_path')
    @patch('engines.tts_module.is_xtts_supported')
    @patch('engines.tts_module.XTTSWorker')
    @patch('engines.tts_module.os.path.exists')
    @patch('engines.tts_module.save_to_cache')
    def test_generate_audio_passes_language_to_xtts(self, mock_save, mock_exists, mock_xtts_worker, mock_is_xtts_supported, mock_get_cache_path):
        mock_is_xtts_supported.return_value = True
        mock_get_cache_path.return_value = "cache/hashed_file.wav"
        
        # 1st call (cache check): False, 2nd call (generated file check in Edge fallback, but we want XTTS success): 
        # Actually, if XTTS succeeds, it tries to open the file.
        mock_exists.side_effect = [False, True] 
        
        mock_worker_instance = mock_xtts_worker.return_value
        mock_worker_instance.generate.return_value = True
        
        # Mock open for reading the generated file to save to cache
        with patch("builtins.open", mock_open(read_data=b"audio data")):
            # Call generate_audio with language="es"
            result = generate_audio("Hola", "test.wav", engine="xtts", clone_ref="voices/ref.wav", language="es")
            
            self.assertTrue(result)
            # Verify language was passed to worker
            mock_worker_instance.generate.assert_called_with("Hola", "test.wav", "voices/ref.wav", language="es")

if __name__ == '__main__':
    unittest.main()
