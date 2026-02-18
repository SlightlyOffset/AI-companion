import unittest
import os
import shutil
import sys

# Add the project root to sys.path to import engines
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engines.audio_cache import get_cache_path, save_to_cache

class TestAudioCache(unittest.TestCase):
    def setUp(self):
        self.cache_dir = "test_cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
    def tearDown(self):
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)

    def test_cache_hit_miss(self):
        text = "Hello world"
        voice = "en-GB-SoniaNeural"
        engine = "edge-tts"
        
        # Miss
        path = get_cache_path(text, voice, engine, cache_dir=self.cache_dir)
        self.assertFalse(os.path.exists(path))
        
        # Save
        dummy_data = b"fake audio"
        save_to_cache(text, voice, engine, dummy_data, cache_dir=self.cache_dir)
        
        # Hit
        path = get_cache_path(text, voice, engine, cache_dir=self.cache_dir)
        self.assertTrue(os.path.exists(path))
        with open(path, "rb") as f:
            self.assertEqual(f.read(), dummy_data)

if __name__ == '__main__':
    unittest.main()
