import unittest
from portfolio.portfolio import Portfolio

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio(initial_cash=10000.0)

    def test_initial_state(self):
        self.assertEqual(self.portfolio.cash, 10000.0)
        self.assertEqual(len(self.portfolio.positions), 0)

    def test_buy_transaction(self):
        # Buy 10 @ 150
        success = self.portfolio.update_position("AAPL", 10, 150, "BUY")
        self.assertTrue(success)
        self.assertEqual(self.portfolio.cash, 8500.0)
        self.assertEqual(self.portfolio.positions["AAPL"]["shares"], 10)
        self.assertEqual(self.portfolio.positions["AAPL"]["avg_cost"], 150)
        
        # Buy more: 10 @ 160
        self.portfolio.update_position("AAPL", 10, 160, "BUY")
        self.assertEqual(self.portfolio.cash, 6900.0)
        self.assertEqual(self.portfolio.positions["AAPL"]["shares"], 20)
        self.assertEqual(self.portfolio.positions["AAPL"]["avg_cost"], 155)

    def test_sell_transaction(self):
        self.portfolio.update_position("AAPL", 20, 155, "BUY") # Spend 3100, Cash 6900
        # Sell 15 @ 170
        success = self.portfolio.update_position("AAPL", 15, 170, "SELL")
        self.assertTrue(success)
        # 6900 + (15 * 170) = 6900 + 2550 = 9450
        self.assertEqual(self.portfolio.cash, 9450.0)
        self.assertEqual(self.portfolio.positions["AAPL"]["shares"], 5)
        # Realized PnL: 15 * (170 - 155) = 225
        self.assertEqual(self.portfolio.realized_pnl, 225.0)

    def test_equity_and_pnl_calculation(self):
        self.portfolio.update_position("AAPL", 10, 150, "BUY") # Cash 8500
        prices = {"AAPL": 160}
        
        # Equity: 8500 + 10 * 160 = 10100
        self.assertEqual(self.portfolio.get_equity(prices), 10100.0)
        
        # Unrealized PnL: 10 * (160 - 150) = 100
        self.assertEqual(self.portfolio.get_unrealized_pnl(prices), 100.0)
        
        # Total PnL: Realized (0) + 100 = 100
        self.assertEqual(self.portfolio.get_total_pnl(prices), 100.0)

    def test_insufficient_cash(self):
        success = self.portfolio.update_position("AAPL", 100, 200, "BUY") # Needs 20000, only has 10000
        self.assertFalse(success)
        self.assertEqual(self.portfolio.cash, 10000.0)

    def test_insufficient_shares(self):
        self.portfolio.update_position("AAPL", 10, 150, "BUY")
        success = self.portfolio.update_position("AAPL", 15, 160, "SELL")
        self.assertFalse(success)
        self.assertEqual(self.portfolio.positions["AAPL"]["shares"], 10)

if __name__ == "__main__":
    unittest.main()
