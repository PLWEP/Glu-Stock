import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from scanner import MarketScanner

class TestMarketScanner(unittest.TestCase):
    def setUp(self):
        # 1. Mock Agents and Managers
        self.mock_ra = MagicMock()
        self.mock_um = MagicMock()
        
        # 2. Patch UniverseManager to return our mock
        with patch('scanner.UniverseManager', return_value=self.mock_um):
            self.scanner = MarketScanner(research_agent=self.mock_ra)
            
        # 3. Create dummy data
        dates = pd.date_range("2024-01-01", periods=10)
        self.df = pd.DataFrame({
            'close': [150] * 10,
            'rsi': [50] * 10,
            'macd_diff': [0] * 10,
            'sma_20': [150] * 10,
            'volume': [1000] * 10
        }, index=pd.MultiIndex.from_tuples([(d, 'A.JK') for d in dates], names=['date', 'ticker']))

    def test_empty_input(self):
        results = self.scanner.scan([], threshold=0.5)
        self.assertEqual(results, [])

    @patch('scanner.JsonLogger')
    def test_scan_logic_flow(self, mock_logger):
        # 1. Mock Research success
        self.mock_ra.research.return_value = self.df
        
        # 2. Mock Universe partitioning and ranking
        self.mock_um.partition_price_data.return_value = {"A.JK": self.df.xs("A.JK", level="ticker")}
        self.mock_um.rank_stocks.return_value = (["A.JK"], {"A.JK": 0.85})
        
        # 3. Execute
        results = self.scanner.scan(["A.JK"], threshold=0.1)
        
        # 4. Verify
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ticker"], "A.JK")
        self.assertEqual(results[0]["score"], 0.85)

if __name__ == "__main__":
    unittest.main()
