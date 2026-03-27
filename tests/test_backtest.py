import unittest
import pandas as pd
import numpy as np
from backtesting.backtest import VectorizedBacktester

class TestVectorizedBacktester(unittest.TestCase):
    def setUp(self):
        # Create a simple trend dataset
        dates = pd.date_range("2024-01-01", periods=10)
        self.df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109], # ~1% daily return
            'final_signal': [1] * 10
        }, index=pd.MultiIndex.from_tuples([(d, 'AAPL') for d in dates], names=['date', 'ticker']))
        
        self.backtester = VectorizedBacktester(transaction_cost=0.0)

    def test_total_return(self):
        self.backtester.run_backtest(self.df)
        metrics = self.backtester.get_metrics()
        # Initial 100, Final 109. Signal shift means we capture returns from D2 to D10.
        # Cumulative return = (101/100) * (102/101) * ... * (109/108) = 109/100 = 1.09
        # Total return = 0.09 (9%)
        self.assertAlmostEqual(metrics['total_return'], 0.09, places=4)

    def test_transaction_cost_impact(self):
        # Strategy with flipping signals to generate trades
        df_flip = self.df.copy()
        df_flip['final_signal'] = [1, -1, 1, -1, 1, -1, 1, -1, 1, -1]
        
        # Backtest with NO cost
        bt_no_cost = VectorizedBacktester(transaction_cost=0.0)
        bt_no_cost.run_backtest(df_flip)
        res_no_cost = bt_no_cost.get_metrics()['total_return']
        
        # Backtest WITH cost
        bt_with_cost = VectorizedBacktester(transaction_cost=0.01) # 1% cost
        bt_with_cost.run_backtest(df_flip)
        res_with_cost = bt_with_cost.get_metrics()['total_return']
        
        self.assertLess(res_with_cost, res_no_cost)

    def test_max_drawdown(self):
        # Create a drawdown scenario: 100 -> 110 -> 90 -> 100
        df_drawdown = pd.DataFrame({
            'close': [100, 110, 90, 100],
            'final_signal': [1, 1, 1, 1]
        }, index=pd.MultiIndex.from_tuples([(pd.Timestamp(f'2024-01-0{i+1}'), 'AAPL') for i in range(4)], names=['date', 'ticker']))
        
        self.backtester.run_backtest(df_drawdown)
        metrics = self.backtester.get_metrics()
        # Equity: 100,000 -> 110,000 -> 90,000 -> 100,000
        # Peak: 110,000. Trout: 90,000. DD = (90-110)/110 = -18.18%
        self.assertAlmostEqual(metrics['max_drawdown'], -0.1818, places=4)

    def test_sharpe_ratio_positive(self):
        self.backtester.run_backtest(self.df)
        metrics = self.backtester.get_metrics()
        # Upward trend should have positive Sharpe
        self.assertGreater(metrics['sharpe_ratio'], 0)

if __name__ == "__main__":
    unittest.main()
