import unittest
import pandas as pd
import numpy as np
from features.features import FeatureEngineer

class TestFeatureEngineer(unittest.TestCase):
    def setUp(self):
        self.engineer = FeatureEngineer()
        # Create a sample multi-index DataFrame for two tickers
        dates = pd.date_range(start="2024-01-01", periods=100)
        self.tickers = ["AAPL", "MSFT"]
        
        data = []
        for ticker in self.tickers:
            # Generate some random stock-like data
            np.random.seed(42 if ticker == "AAPL" else 43)
            prices = 100 + np.cumsum(np.random.randn(100))
            for i, date in enumerate(dates):
                data.append({
                    'date': date,
                    'ticker': ticker,
                    'open': prices[i],
                    'high': prices[i] + 1,
                    'low': prices[i] - 1,
                    'close': prices[i] + 0.5,
                    'volume': 1000000
                })
        
        self.df = pd.DataFrame(data).set_index(['date', 'ticker'])

    def test_indicator_presence(self):
        featured_df = self.engineer.add_indicators(self.df)
        expected_columns = ['rsi', 'macd', 'macd_signal', 'sma_20', 'ema_20', 'bb_high', 'bb_low']
        for col in expected_columns:
            self.assertIn(col, featured_df.columns)

    def test_multi_ticker_isolation(self):
        # Isolation test: changing AAPL data should NOT change MSFT RSI
        featured_df_orig = self.engineer.add_indicators(self.df.copy())
        
        df_mod = self.df.copy()
        # Modify AAPL close at a specific date (date 30)
        date_30 = self.df.index.get_level_values('date').unique()[30]
        df_mod.loc[(date_30, 'AAPL'), 'close'] *= 1.5
        featured_df_mod = self.engineer.add_indicators(df_mod)
        
        # MSFT RSI at the same date should be identical
        orig_msft_rsi = featured_df_orig.loc[(date_30, 'MSFT'), 'rsi']
        mod_msft_rsi = featured_df_mod.loc[(date_30, 'MSFT'), 'rsi']
        # Use np.isclose to handle floating point and potential NaNs safely
        self.assertTrue(np.isclose(orig_msft_rsi, mod_msft_rsi, equal_nan=True))
        
        # AAPL RSI should be different
        orig_aapl_rsi = featured_df_orig.loc[(date_30, 'AAPL'), 'rsi']
        mod_aapl_rsi = featured_df_mod.loc[(date_30, 'AAPL'), 'rsi']
        self.assertNotEqual(orig_aapl_rsi, mod_aapl_rsi)

    def test_no_lookahead_bias(self):
        # Changing a FUTURE value should NOT change CURRENT indicator value
        df_orig = self.df.copy()
        featured_orig = self.engineer.add_indicators(df_orig)
        
        df_future_mod = self.df.copy()
        # Modify AAPL close at date 50
        dates = self.df.index.get_level_values('date').unique()
        df_future_mod.loc[(dates[50], 'AAPL'), 'close'] *= 2.0
        featured_mod = self.engineer.add_indicators(df_future_mod)
        
        # Check indicator at date 30 (earlier than date 50)
        date_30 = dates[30]
        orig_val = featured_orig.loc[(date_30, 'AAPL'), 'rsi']
        mod_val = featured_mod.loc[(date_30, 'AAPL'), 'rsi']
        
        self.assertTrue(np.isclose(orig_val, mod_val, equal_nan=True))
        # Also ensure it is NOT NaN at date 30
        self.assertFalse(np.isnan(orig_val))

    def test_clean_features(self):
        featured_df = self.engineer.add_indicators(self.df)
        cleaned_df = self.engineer.clean_features(featured_df)
        # First 19 rows of SMA(20) should be NaN, so cleaned DF should have fewer rows than indicators DF
        self.assertLess(len(cleaned_df), len(featured_df))
        self.assertFalse(cleaned_df.isna().any().any())

if __name__ == "__main__":
    unittest.main()
