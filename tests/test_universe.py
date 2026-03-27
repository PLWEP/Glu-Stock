import unittest
import pandas as pd
import numpy as np
import os
from data.universe import UniverseManager

class TestUniverseManager(unittest.TestCase):
    def setUp(self):
        self.test_csv = "tests/test_idx_stocks.csv"
        # Setup dummy metadata
        data = [
            ["A.JK", "Alpha", "Industrials", False],
            ["B.JK", "Beta", "Financials", False], # Bank
            ["C.JK", "Gamma", "Technology", True],   # BUMN
            ["D.JK", "Delta", "Energy", False],
        ]
        df = pd.DataFrame(data, columns=["ticker", "name", "sector", "is_bumn"])
        df.to_csv(self.test_csv, index=False)
        self.mgr = UniverseManager(csv_path=self.test_csv)

    def tearDown(self):
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def test_filtering(self):
        df = self.mgr.get_idx_tickers()
        filtered = self.mgr.filter_excluded_stocks(df)
        tickers = filtered["ticker"].tolist()
        
        # B and C should be excluded
        self.assertIn("A.JK", tickers)
        self.assertIn("D.JK", tickers)
        self.assertNotIn("B.JK", tickers)
        self.assertNotIn("C.JK", tickers)

    def test_ranking(self):
        # Create dummy price data for A and D
        # A: High volume, high trend
        # D: Low volume, low trend
        dates = pd.date_range("2024-01-01", periods=30)
        
        data_a = pd.DataFrame({
            "Close": [100 + i for i in range(30)], 
            "Volume": [1000] * 30
        }, index=dates)
        
        data_d = pd.DataFrame({
            "Close": [100] * 30,
            "Volume": [100] * 30
        }, index=dates)
        
        price_dict = {"A.JK": data_a, "D.JK": data_d}
        
        df_filtered = pd.DataFrame([["A.JK"], ["D.JK"]], columns=["ticker"])
        top_stocks = self.mgr.rank_stocks(df_filtered, price_dict, top_n=1)
        
        self.assertEqual(len(top_stocks), 1)
        self.assertEqual(top_stocks[0], "A.JK")

if __name__ == "__main__":
    unittest.main()
