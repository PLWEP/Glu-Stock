import unittest
import pandas as pd
import os
import csv
from portfolio.portfolio import Portfolio
from execution.execution import ExecutionEngine

class TestExecutionEngine(unittest.TestCase):
    def setUp(self):
        self.log_file = "tests/test_trade_log.csv"
        self.engine = ExecutionEngine(log_file=self.log_file)
        self.portfolio = Portfolio(initial_cash=10000.0)
        
        # Sample data
        dates = pd.date_range("2024-01-01", periods=3)
        self.df = pd.DataFrame({
            'close': [150, 160, 170],
            'final_signal': [1, 1, 0] # Buy, Hold, Sell
        }, index=pd.MultiIndex.from_tuples([
            (dates[0], 'AAPL'), (dates[1], 'AAPL'), (dates[2], 'AAPL')
        ], names=['date', 'ticker']))

    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_execution_and_logging(self):
        # Execute signals
        self.engine.execute_signals(self.df, self.portfolio, shares_per_trade=10)
        
        # Verify Portfolio
        # BUY 10 @ 150 -> 8500 cash.
        # SELL 10 @ 170 -> 8500 + 1700 = 10200 cash.
        self.assertEqual(self.portfolio.cash, 10200.0)
        self.assertEqual(len(self.portfolio.positions), 0)
        self.assertEqual(self.portfolio.realized_pnl, 200.0)
        
        # Verify Log File
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, mode='r') as f:
            lines = list(csv.reader(f))
            # Header + 2 trades (BUY and SELL)
            self.assertEqual(len(lines), 3) 
            self.assertEqual(lines[1][2], "BUY")
            self.assertEqual(lines[1][5], "SUCCESS")
            self.assertEqual(lines[2][2], "SELL")

    def test_no_double_buy(self):
        # Even if signal stays 1, should only buy once if shares > 0
        df_same = self.df.iloc[:2] # Two '1' signals
        self.engine.execute_signals(df_same, self.portfolio, shares_per_trade=10)
        
        self.assertEqual(self.portfolio.positions["AAPL"]["shares"], 10)
        self.assertEqual(self.portfolio.cash, 8500.0)

if __name__ == "__main__":
    unittest.main()
