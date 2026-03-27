import unittest
import os
import yaml
from utils.config import ConfigLoader

class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        self.test_config_path = "tests/test_config.yaml"

    def tearDown(self):
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

    def test_load_valid_config(self):
        test_data = {
            "trading": {
                "capital": 50000000.0,
                "risk_per_trade": 0.01,
                "tickers": ["BBCA.JK"]
            }
        }
        with open(self.test_config_path, 'w') as f:
            yaml.dump(test_data, f)
            
        loader = ConfigLoader(config_path=self.test_config_path)
        params = loader.get_trading_params()
        self.assertEqual(params["capital"], 50000000.0)
        self.assertEqual(params["risk_per_trade"], 0.01)

    def test_validation_errors(self):
        # Invalid capital
        with open(self.test_config_path, 'w') as f:
            yaml.dump({"trading": {"capital": -1, "risk_per_trade": 0.02, "tickers": ["A"]}}, f)
        with self.assertRaises(ValueError):
            ConfigLoader(config_path=self.test_config_path)
            
        # Invalid risk
        with open(self.test_config_path, 'w') as f:
            yaml.dump({"trading": {"capital": 100, "risk_per_trade": 1.5, "tickers": ["A"]}}, f)
        with self.assertRaises(ValueError):
            ConfigLoader(config_path=self.test_config_path)

    def test_default_fallback(self):
        # File doesn't exist
        loader = ConfigLoader(config_path="non_existent_file.yaml")
        params = loader.get_trading_params()
        self.assertEqual(params["capital"], 100000000.0)

if __name__ == "__main__":
    unittest.main()
