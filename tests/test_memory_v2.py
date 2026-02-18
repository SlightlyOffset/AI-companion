import unittest
import os
import sys
import json
import shutil

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engines.memory_v2 import HistoryManager

class TestHistoryManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_history"
        self.manager = HistoryManager(history_dir=self.test_dir)
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_and_load(self):
        profile = "TestProfile"
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        self.manager.save_history(profile, history, mood_score=10)
        
        loaded = self.manager.load_history(profile)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["content"], "Hello")
        
        # Check that we can also get the metadata
        data = self.manager.get_full_data(profile)
        self.assertIn("metadata", data)
        self.assertEqual(data["metadata"]["mood_score"], 10)
        self.assertIn("last_interaction", data["metadata"])

    def test_truncation(self):
        profile = "TruncateProfile"
        # 20 messages
        history = [{"role": "user", "content": f"msg {i}"} for i in range(20)]
        self.manager.save_history(profile, history)
        
        # Should only load the last 15
        loaded = self.manager.load_history(profile, limit=15)
        self.assertEqual(len(loaded), 15)
        self.assertEqual(loaded[0]["content"], "msg 5")
        self.assertEqual(loaded[-1]["content"], "msg 19")

    def test_per_profile_files(self):
        self.manager.save_history("ProfileA", [{"role": "user", "content": "A"}])
        self.manager.save_history("ProfileB", [{"role": "user", "content": "B"}])
        
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "ProfileA_history.json")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "ProfileB_history.json")))

    def test_special_characters_in_filename(self):
        profile = "Ria(polite)-Variant_1"
        self.manager.save_history(profile, [{"role": "user", "content": "test"}])
        
        expected_path = os.path.join(self.test_dir, "Ria(polite)-Variant_1_history.json")
        self.assertTrue(os.path.exists(expected_path))
        
        loaded = self.manager.load_history(profile)
        self.assertEqual(len(loaded), 1)

    def test_is_recent_interaction(self):
        profile = "RecentProfile"
        # Save history (sets timestamp to now)
        self.manager.save_history(profile, [{"role": "user", "content": "hello"}])
        
        # Should be recent (within 24 hours)
        self.assertTrue(self.manager.is_recent_interaction(profile, hours=24))
        
        # Mocking an old timestamp (this is a bit tricky without patching, 
        # but I can manually overwrite the file for the test)
        filename = self.manager._get_filename(profile)
        with open(filename, "r", encoding="UTF-8") as f:
            data = json.load(f)
        
        # Set to 25 hours ago
        from datetime import datetime, timedelta
        old_time = (datetime.now() - timedelta(hours=25)).strftime("%Y-%m-%d | %H:%M:%S")
        data["metadata"]["last_interaction"] = old_time
        
        with open(filename, "w", encoding="UTF-8") as f:
            json.dump(data, f)
            
        # Should NOT be recent anymore
        self.assertFalse(self.manager.is_recent_interaction(profile, hours=24))

if __name__ == "__main__":
    unittest.main()

