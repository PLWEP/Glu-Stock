import unittest
import pandas as pd
import numpy as np
from strategies.strategy import TradingStrategy

class TestStrategyTimeframes(unittest.TestCase):
    def setUp(self):
        self.strategy = TradingStrategy()
        # Create dummy multi-ticker data
        dates = pd.date_range("2024-01-01", periods=100)
        tickers = ["AAPL"]
        index = pd.MultiIndex.from_product([dates, tickers], names=['date', 'ticker'])
        self.df = pd.DataFrame(index=index)
        self.df['close'] = np.linspace(100, 200, 100)
        self.df['volume'] = 1000
        # Dummy indicators (Mocked from FeatureEngineer)
        self.df['rsi'] = 60
        self.df['macd_h'] = 5
        self.df['sma_20'] = 150

    def test_score_differentiation(self):
        res_daily = self.strategy.generate_signals(self.df.copy(), timeframe="daily")
        res_yearly = self.strategy.generate_signals(self.df.copy(), timeframe="yearly")
        
        # In Yearly, Trend (0.8) should dominate. RSI (0.0) and MACD (0.0) should be ignored.
        # In Daily, RSI (0.3) and MACD (0.3) are included.
        self.assertNotEqual(res_daily['final_score'].iloc[-1], res_yearly['final_score'].iloc[-1])
        self.assertEqual(res_daily['timeframe'].iloc[-1], "daily")
        self.assertEqual(res_yearly['timeframe'].iloc[-1], "yearly")

    def test_no_lookahead_bias(self):
        # 1. Generate signal for 50 rows
        df_short = self.df.iloc[:50].copy()
        res_short = self.strategy.generate_signals(df_short, timeframe="daily")
        score_at_50 = res_short['final_score'].iloc[-1]
        
        # 2. Generate signal for 100 rows
        res_long = self.strategy.generate_signals(self.df.copy(), timeframe="daily")
        score_at_50_long = res_long.loc[res_short.index[-1], 'final_score']
        
        # Historical scores must match exactly
        self.assertAlmostEqual(score_at_50, score_at_50_long)

if __name__ == "__main__":
    unittest.main()
