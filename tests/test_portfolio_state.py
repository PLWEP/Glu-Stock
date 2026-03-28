import unittest
import os
import json
import pandas as pd
from agents.agents import TradingAgent
from portfolio.portfolio import Portfolio

class TestPortfolioState(unittest.TestCase):
    
    def setUp(self):
        # Cleanup potential old state
        for p in ["daily", "weekly", "monthly", "test"]:
            path = f"data/portfolio_{p}.json"
            if os.path.exists(path):
                os.remove(path)
                
    def test_continuity_persistence(self):
        """ Verify that portfolio state survives TradingAgent restart. """
        allocations = {"daily": 1000.0}
        ta = TradingAgent(initial_cash=1000.0, allocations=allocations)
        
        # 1. Simulate a trade
        df = pd.DataFrame({
            'close': [100.0], 'final_signal': [1]
        }, index=pd.MultiIndex.from_tuples([('2024-01-01', 'BBCA.JK')], names=['date', 'ticker']))
        
        ta.trade(df, pipeline="daily", shares_per_trade=5)
        
        # Verify in-memory
        p = ta.portfolios["daily"]
        self.assertEqual(p.positions["BBCA.JK"]["shares"], 5)
        self.assertEqual(p.cash, 500.0) # 1000 - (5 * 100)
        
        # 2. Kill and Restart Agent
        del ta
        ta2 = TradingAgent(initial_cash=1000.0, allocations=allocations)
        p2 = ta2.portfolios["daily"]
        
        # Verify restored from JSON
        self.assertEqual(p2.positions["BBCA.JK"]["shares"], 5)
        self.assertEqual(p2.cash, 500.0)
        
    def test_profit_freezing(self):
        """ Verify that profit is NOT available for new trades. """
        p = Portfolio(name="test", initial_cash=1000.0)
        
        # 1. Buy 5 shares at 100 (Cost 500)
        p.update_position("AAPL", 5, 100.0, "BUY")
        self.assertEqual(p.cash, 500.0)
        self.assertEqual(p.available_to_trade, 500.0)
        
        # 2. Sell 5 shares at 200 (Gain 500, Cash 1500)
        p.update_position("AAPL", 5, 200.0, "SELL")
        self.assertEqual(p.cash, 1500.0)
        self.assertEqual(p.realized_pnl, 500.0)
        
        # 3. VERIFY PROFIT FREEZE: Available to trade should be capped at initial 1000
        # However, since cash is 1500, and initial is 1000...
        # Wait, if cash is 1500, and initial is 1000, then available_to_trade is 1000. Correct.
        self.assertEqual(p.available_to_trade, 1000.0)
        
        # If I had LOST money (Cash 400), available should be 400
        p.cash = 400.0
        self.assertEqual(p.available_to_trade, 400.0)

if __name__ == '__main__':
    unittest.main()
