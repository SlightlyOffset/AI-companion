import unittest
import os
import json
import shutil
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

if __name__ == "__main__":
    unittest.main()
