import unittest
from risk.risk import RiskManager

class TestRiskManager(unittest.TestCase):
    def setUp(self):
        self.rm = RiskManager(risk_per_trade=0.02, max_drawdown_limit=0.10)

    def test_position_sizing(self):
        # Equity: 100,000, Price: 200, SL: 5%
        # Risk Amount: 2,000
        # Risk per Share: 200 * 0.05 = 10
        # Shares: 2,000 / 10 = 200
        shares = self.rm.calculate_position_size(100000, 200, 0.05)
        self.assertEqual(shares, 200)

    def test_stop_loss_trigger(self):
        # Avg Cost: 200, SL: 5% (SL Price is 190)
        self.assertTrue(self.rm.is_stop_loss_triggered(200, 189, 0.05))
        self.assertFalse(self.rm.is_stop_loss_triggered(200, 191, 0.05))
        # Boundary
        self.assertFalse(self.rm.is_stop_loss_triggered(200, 190, 0.05))

    def test_drawdown_halt(self):
        # Peak: 100,000. Current: 89,000. DD: 11%. Threshold: 10%.
        self.assertTrue(self.rm.check_drawdown_halt(89000, 100000))
        # Current: 91,000. DD: 9%. Threshold: 10%.
        self.assertFalse(self.rm.check_drawdown_halt(91000, 100000))

if __name__ == "__main__":
    unittest.main()
