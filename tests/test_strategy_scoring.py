import unittest
import pandas as pd
import numpy as np
from strategies.strategy import TradingStrategy

class TestStrategyScoring(unittest.TestCase):
    def setUp(self):
        self.strategy = TradingStrategy()
        # Create a sample DataFrame with indicators
        dates = pd.date_range("2024-01-01", periods=100)
        self.df = pd.DataFrame({
            "close": np.linspace(100, 110, 100),
            "rsi": np.linspace(20, 80, 100),
            "macd_h": np.zeros(100),
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
        # Case 1: Oversold (RSI 20) -> Should have high s_rsi
        oversold_df = self.df.iloc[[0]].copy()
        oversold_df['rsi'] = 20
        res1 = self.strategy.generate_signals(oversold_df)
        
        # Case 2: Overbought (RSI 80) -> Should have low s_rsi
        overbought_df = self.df.iloc[[0]].copy()
        overbought_df['rsi'] = 80
        res2 = self.strategy.generate_signals(overbought_df)
        
        self.assertGreater(res1.iloc[0]['final_score'], res2.iloc[0]['final_score'])
        self.assertAlmostEqual(res1.iloc[0]['s_rsi'], 1.0)
        self.assertAlmostEqual(res2.iloc[0]['s_rsi'], 0.0)

    def test_trend_impact(self):
        # Case 1: Strong Uptrend (Price >> SMA20)
        uptrend_df = self.df.iloc[[0]].copy()
        uptrend_df['close'] = 120
        uptrend_df['sma_20'] = 100
        res1 = self.strategy.generate_signals(uptrend_df)
        
        # Case 2: Strong Downtrend (Price << SMA20)
        downtrend_df = self.df.iloc[[0]].copy()
        downtrend_df['close'] = 80
        downtrend_df['sma_20'] = 100
        res2 = self.strategy.generate_signals(downtrend_df)
        
        self.assertGreater(res1.iloc[0]['s_trend'], res2.iloc[0]['s_trend'])

    def test_signal_mapping(self):
        # Force a very high score
        high_score_df = self.df.iloc[[0]].copy()
        high_score_df['rsi'] = 10     # s_rsi = 1
        high_score_df['macd_h'] = 10  # s_macd -> 1
        high_score_df['close'] = 150  # s_trend -> 1
        high_score_df['sma_20'] = 100
        high_score_df['volume'] = 3000 # s_vol -> 1
        
        # We need a history for MACD std and Vol avg
        long_df = pd.concat([self.df] * 3) # ensure 20+ periods
        long_df.iloc[-1] = high_score_df.iloc[0]
        
        res = self.strategy.generate_signals(long_df)
        last_row = res.iloc[-1]
        
        self.assertGreater(last_row['final_score'], 0.7)
        self.assertEqual(last_row['final_signal'], 1)

if __name__ == "__main__":
    unittest.main()
