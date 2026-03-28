import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from strategies.strategy import TradingStrategy

class TestStrategyScoring(unittest.TestCase):
    def setUp(self):
        self.strategy = TradingStrategy()
        # Create a sample DataFrame with indicators (Correct columns: close, rsi, macd_diff, sma_20, volume)
        dates = pd.date_range("2024-01-01", periods=100)
        self.df = pd.DataFrame({
            "close": np.linspace(100, 110, 100),
            "rsi": np.linspace(20, 80, 100),
            "macd_diff": np.zeros(100),
            "sma_20": np.full(100, 105),
            "volume": np.full(100, 1000),
            "ticker": "TEST.JK"
        }, index=dates)
        self.df.index.name = "date"
        self.df = self.df.reset_index().set_index(["date", "ticker"])

    def test_score_range(self):
        results = self.strategy.generate_signals(self.df)
        self.assertTrue(results['final_score'].min() >= 0.0)
        self.assertTrue(results['final_score'].max() <= 1.0)
        self.assertIn('final_signal', results.columns)

    def test_rsi_sensitivity(self):
        # Case 1: Oversold (RSI 20) -> s_rsi = (50-20)/50 = 0.6. Clamped [0,1]. Wait, 50-20 = 30. 30/50 = 0.6.
        # RSI 0 -> (50-0)/50 = 1.0
        # RSI 100 -> (50-100)/50 = -1.0 -> 0.0
        oversold_df = self.df.iloc[[0]].copy()
        oversold_df['rsi'] = 10
        res1 = self.strategy.generate_signals(oversold_df)
        
        # Case 2: Overbought (RSI 90) -> Should have low s_rsi
        overbought_df = self.df.iloc[[0]].copy()
        overbought_df['rsi'] = 90
        res2 = self.strategy.generate_signals(overbought_df)
        
        self.assertGreater(res1.iloc[0]['s_rsi'], res2.iloc[0]['s_rsi'])
        self.assertGreater(res1.iloc[0]['final_score'], res2.iloc[0]['final_score'])

    def test_trend_impact(self):
        # Case 1: Strong Uptrend (SMA Slope > 0)
        # Note: sma_20 difference is used in s_trend
        uptrend_df = self.df.iloc[:2].copy()
        uptrend_df['sma_20'] = [100, 110] # Big jump
        res1 = self.strategy.generate_signals(uptrend_df)
        
        # Case 2: Downtrend
        downtrend_df = self.df.iloc[:2].copy()
        downtrend_df['sma_20'] = [110, 100] # Big drop
        res2 = self.strategy.generate_signals(downtrend_df)
        
        self.assertGreater(res1.iloc[-1]['s_trend'], res2.iloc[-1]['s_trend'])

if __name__ == "__main__":
    unittest.main()
