import unittest
from utils.performance import calculate_performance_metrics

class TestPerformance(unittest.TestCase):
    def test_empty_data_handling(self):
        metrics = calculate_performance_metrics([], [])
        self.assertEqual(metrics["total_trades"], 0)
        self.assertEqual(metrics["win_rate"], 0.0)
        self.assertEqual(metrics["max_drawdown"], 0.0)

    def test_win_rate_and_averages(self):
        trades = [
            {"pnl": 100, "status": "CLOSED"},
            {"pnl": 200, "status": "CLOSED"},
            {"pnl": -150, "status": "CLOSED"}
        ]
        metrics = calculate_performance_metrics(trades, [])
        self.assertEqual(metrics["total_trades"], 3)
        self.assertAlmostEqual(metrics["win_rate"], 2/3)
        self.assertEqual(metrics["average_win"], 150.0)
        self.assertEqual(metrics["average_loss"], -150.0)

    def test_drawdown_calculation(self):
        # Peak: 1500, Low after peak: 1200 -> DD: 300/1500 = 0.2
        snapshots = [
            {"date": "2024-01-01", "equity": 1000},
            {"date": "2024-01-02", "equity": 1500},
            {"date": "2024-01-03", "equity": 1200}, # Drawdown starts
            {"date": "2024-01-04", "equity": 1800}  # Recovers and hits new peak
        ]
        metrics = calculate_performance_metrics([], snapshots)
        self.assertAlmostEqual(metrics["max_drawdown"], 0.2)
        self.assertAlmostEqual(metrics["total_return"], 0.8) # (1800-1000)/1000

    def test_zero_capital_guard(self):
        # Should not crash with initial equity 0
        snapshots = [{"date": "2024-01-01", "equity": 0}, {"date": "2024-01-02", "equity": 1000}]
        metrics = calculate_performance_metrics([], snapshots)
        self.assertEqual(metrics["total_return"], 0.0)
        self.assertEqual(metrics["max_drawdown"], 0.0)

if __name__ == "__main__":
    unittest.main()
