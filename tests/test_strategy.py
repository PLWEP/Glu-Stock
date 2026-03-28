import unittest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from strategies.strategy import TradingStrategy

class TestTradingStrategy(unittest.TestCase):
    def setUp(self):
        # Mock config to avoid DEBUG mode side effects
        self.patcher = patch('utils.config.ConfigLoader.get_config')
        self.mock_config = self.patcher.start()
        self.mock_config.return_value = {"debug_mode": False}
        
        self.strategy = TradingStrategy()
        # Sample data with RSI and MACD
        self.df = pd.DataFrame({
            'rsi': [20, 35, 80, 65, 30, 70],
            'macd_diff': [1.0, 1.1, 1.2, 1.1, 0.9, 0.8],
            'macd_signal': [1.05, 1.05, 1.15, 1.15, 0.95, 0.95],
            'sma_20': [100, 101, 102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1100, 1000, 900]
        }, index=pd.MultiIndex.from_tuples([
            (pd.Timestamp('2024-01-01'), 'AAPL'),
            (pd.Timestamp('2024-01-02'), 'AAPL'),
            (pd.Timestamp('2024-01-03'), 'AAPL'),
            (pd.Timestamp('2024-01-04'), 'AAPL'),
            (pd.Timestamp('2024-01-05'), 'AAPL'),
            (pd.Timestamp('2024-01-06'), 'AAPL')
        ], names=['date', 'ticker']))

    def tearDown(self):
        self.patcher.stop()

    def test_rsi_signals(self):
        df_sig = self.strategy.generate_signals(self.df)
        # RSI 20 -> (50-20)/50 = 0.6. High score.
        self.assertGreater(df_sig.loc[(pd.Timestamp('2024-01-01'), 'AAPL'), 's_rsi'], 0.5)
        # RSI 80 -> (50-80)/50 = -0.6 -> 0.0. Low score.
        self.assertLess(df_sig.loc[(pd.Timestamp('2024-01-03'), 'AAPL'), 's_rsi'], 0.5)

    def test_macd_crossover_signals(self):
        df_sig = self.strategy.generate_signals(self.df)
        self.assertIn('s_macd', df_sig.columns)
        # All test data has non-zero macd_diff
        self.assertTrue((df_sig['s_macd'] > 0).all())

    def test_score_range_and_signals(self):
        df_sig = self.strategy.generate_signals(self.df)
        self.assertTrue((df_sig['final_score'] >= 0).all())
        self.assertTrue((df_sig['final_score'] <= 1.0).all())
        self.assertIn('final_signal', df_sig.columns)

if __name__ == "__main__":
    unittest.main()
