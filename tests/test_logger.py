import unittest
import os
import json
from utils.logger import JsonLogger

class TestJsonLogger(unittest.TestCase):
    def setUp(self):
        self.test_log_file = "tests/trading_test.log"
        self.logger = JsonLogger(log_file=self.test_log_file)

    def tearDown(self):
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)
        if os.path.exists("tests/logs"):
            import shutil
            shutil.rmtree("tests/logs")

    def test_json_structure(self):
        self.logger.info("Test message", ticker="AAPL")
        
        with open(self.test_log_file, "r", encoding="utf-8") as f:
            line = f.readline().strip()
            log_data = json.loads(line)
            
            self.assertEqual(log_data["level"], "INFO")
            self.assertEqual(log_data["message"], "Test message")
            self.assertEqual(log_data["metadata"]["ticker"], "AAPL")
            self.assertIn("timestamp", log_data)

    def test_error_level(self):
        self.logger.error("Error occurred")
        
        with open(self.test_log_file, "r", encoding="utf-8") as f:
            line = f.readline().strip()
            log_data = json.loads(line)
            self.assertEqual(log_data["level"], "ERROR")

    def test_persistence_append(self):
        self.logger.info("First")
        self.logger.info("Second")
        
        with open(self.test_log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertIn("First", lines[0])
            self.assertIn("Second", lines[1])

if __name__ == "__main__":
    unittest.main()
