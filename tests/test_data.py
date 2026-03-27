import unittest
import os
import sqlite3
import pandas as pd
from data.data import StockDataHandler

class TestStockDataHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = "data/test_cache.db"
        cls.handler = StockDataHandler(db_path=cls.db_path)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_single_ticker(self):
        df = self.handler.fetch_data("AAPL", "2024-01-01", "2024-01-05")
        self.assertFalse(df.empty)
        self.assertIn("open", df.columns)
        self.assertIn("close", df.columns)
        # Check if AAPL is in the index levels
        tickers_in_index = df.index.get_level_values('ticker').unique()
        self.assertIn("AAPL", tickers_in_index)

    def test_multi_ticker(self):
        tickers = ["AAPL", "MSFT"]
        df = self.handler.fetch_data(tickers, "2024-01-01", "2024-01-05")
        self.assertFalse(df.empty)
        tickers_in_index = df.index.get_level_values('ticker').unique()
        self.assertIn("AAPL", tickers_in_index)
        self.assertIn("MSFT", tickers_in_index)

    def test_caching(self):
        # First fetch (downloads and caches)
        self.handler.fetch_data("AAPL", "2024-01-02", "2024-01-03")
        
        # Verify db has data
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM ohlcv WHERE ticker = 'AAPL'").fetchone()[0]
            self.assertGreater(count, 0)
            
    def test_missing_data_handling(self):
        # Create a DF with some NaNs and test handler method
        df_with_nans = pd.DataFrame({
            'open': [100, None, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100.5, None, 102.5],
            'volume': [1000, 1100, 1200]
        }, index=pd.MultiIndex.from_tuples([
            (pd.Timestamp('2024-01-01'), 'AAPL'),
            (pd.Timestamp('2024-01-02'), 'AAPL'),
            (pd.Timestamp('2024-01-03'), 'AAPL')
        ], names=['date', 'ticker']))
        
        cleaned_df = self.handler.handle_missing_data(df_with_nans)
        self.assertFalse(cleaned_df.isna().any().any())
        # Check ffill (second row 'open' should be 100)
        # Re-fetching value by index
        val = cleaned_df.loc[(pd.Timestamp('2024-01-02'), 'AAPL'), 'open']
        self.assertEqual(val, 100.0)

if __name__ == "__main__":
    unittest.main()
