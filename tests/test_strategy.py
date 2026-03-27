import unittest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from strategies.strategy import TradingStrategy

class TestTradingStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = TradingStrategy()
        # Sample data with RSI and MACD
        self.df = pd.DataFrame({
            'rsi': [25, 35, 75, 65, 30, 70],
            'macd': [1.0, 1.1, 1.2, 1.1, 0.9, 0.8],
            'macd_signal': [1.05, 1.05, 1.15, 1.15, 0.95, 0.95]
        }, index=pd.MultiIndex.from_tuples([
            (pd.Timestamp('2024-01-01'), 'AAPL'),
            (pd.Timestamp('2024-01-02'), 'AAPL'),
            (pd.Timestamp('2024-01-03'), 'AAPL'),
            (pd.Timestamp('2024-01-04'), 'AAPL'),
            (pd.Timestamp('2024-01-05'), 'AAPL'),
            (pd.Timestamp('2024-01-06'), 'AAPL')
        ], names=['date', 'ticker']))

    def test_rsi_signals(self):
        df_sig = self.strategy.generate_signals(self.df)
        # RSI 25 (< 30) -> BUY (1)
        self.assertEqual(df_sig.loc[(pd.Timestamp('2024-01-01'), 'AAPL'), 'rsi_signal'], 1)
        # RSI 75 (> 70) -> SELL (-1)
        self.assertEqual(df_sig.loc[(pd.Timestamp('2024-01-03'), 'AAPL'), 'rsi_signal'], -1)
        # RSI 35 -> Hold (0)
        self.assertEqual(df_sig.loc[(pd.Timestamp('2024-01-02'), 'AAPL'), 'rsi_signal'], 0)

    def test_macd_crossover_signals(self):
        df_sig = self.strategy.generate_signals(self.df)
        # Prev MACD 1.0 < 1.05, Current MACD 1.1 > 1.05 -> BUY
        self.assertEqual(df_sig.loc[(pd.Timestamp('2024-01-02'), 'AAPL'), 'macd_signal_rule'], 1)
        # Prev MACD 1.2 > 1.15, Current MACD 1.1 < 1.15 -> SELL
        self.assertEqual(df_sig.loc[(pd.Timestamp('2024-01-04'), 'AAPL'), 'macd_signal_rule'], -1)

    def test_ml_integration(self):
        # Mock model
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([1, -1, 0, 1, -1, 0])
        mock_model.predict_proba.return_value = np.array([[0.1, 0.9], [0.8, 0.2], [0.5, 0.5], [0.2, 0.8], [0.9, 0.1], [0.5, 0.5]])
        
        df_sig = self.strategy.generate_signals(self.df, model=mock_model, features=['rsi', 'macd'])
        
        self.assertIn('ml_signal', df_sig.columns)
        self.assertIn('ml_confidence', df_sig.columns)
        self.assertEqual(df_sig.loc[(pd.Timestamp('2024-01-01'), 'AAPL'), 'ml_signal'], 1)
        self.assertGreater(df_sig.loc[(pd.Timestamp('2024-01-01'), 'AAPL'), 'ml_confidence'], 0)

    def test_confidence_range(self):
        df_sig = self.strategy.generate_signals(self.df)
        self.assertTrue((df_sig['confidence'] >= 0).all())
        self.assertTrue((df_sig['confidence'] <= 1.0).all())

if __name__ == "__main__":
    unittest.main()
