import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from scanner import MarketScanner

class TestMarketScanner(unittest.TestCase):
    def setUp(self):
        # Mock ResearchAgent
        self.mock_research_agent = MagicMock()
        self.scanner = MarketScanner(research_agent=self.mock_research_agent)

    def test_scan_threshold_and_sorting(self):
        # 1. Setup research mock output for 3 stocks
        # A: Strong uptrend (will be high score)
        # B: Moderate uptrend (will be medium score)
        # C: Flat (will be low score)
        tickers = ["A.JK", "B.JK", "C.JK"]
        dates = pd.date_range("2024-01-01", periods=30)
        
        data_a = pd.DataFrame({"Close": [100 + i for i in range(30)], "Volume": [1000] * 30, "ticker": "A.JK"}, index=dates)
        data_b = pd.DataFrame({"Close": [100 + i*0.5 for i in range(30)], "Volume": [1000] * 30, "ticker": "B.JK"}, index=dates)
        data_c = pd.DataFrame({"Close": [100] * 30, "Volume": [1000] * 30, "ticker": "C.JK"}, index=dates)
        
        researched_df = pd.concat([data_a, data_b, data_c])
        researched_df.index.name = "date"
        # Adjust for MultiIndex format and uppercase columns
        researched_df = researched_df.reset_index().set_index(["date", "ticker"]).rename(columns={"Close": "Close", "Volume": "Volume"})
        
        self.mock_research_agent.research.return_value = researched_df

        # 2. Test threshold (should return A and B, but not C)
        # With trend weight 0.3, even top stock might be around 0.3-0.6 if other factors are flat.
        results_mid = self.scanner.scan(tickers, threshold=0.1)
        self.assertEqual(len(results_mid), 2)
        self.assertEqual(results_mid[0]["ticker"], "A.JK")
        self.assertEqual(results_mid[1]["ticker"], "B.JK")
        
        # 3. Test low threshold (should return all 3, sorted)
        results_low = self.scanner.scan(tickers, threshold=-1.0)
        self.assertEqual(len(results_low), 3)
        self.assertEqual(results_low[0]["ticker"], "A.JK")
        self.assertEqual(results_low[1]["ticker"], "B.JK")
        self.assertEqual(results_low[2]["ticker"], "C.JK")
        self.assertTrue(results_low[0]["score"] > results_low[1]["score"] > results_low[2]["score"])

    def test_empty_input(self):
        results = self.scanner.scan([], threshold=0.5)
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()
