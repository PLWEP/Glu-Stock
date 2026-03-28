import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from orchestrator.orchestrator import PipelineOrchestrator

class TestPortfolioReporting(unittest.TestCase):
            
    @patch('orchestrator.orchestrator.send_telegram_alert')
    def test_portfolio_report_format(self, mock_alert):
        orch = PipelineOrchestrator()
        
        # 1. Setup Mock Portfolio with positions
        orch.trading_agent.portfolio.cash = 50000.0
        orch.trading_agent.portfolio.positions = {
            "BBCA.JK": {"shares": 350, "avg_cost": 10000.0},
            "TLKM.JK": {"shares": 1000, "avg_cost": 3800.0}
        }
        
        # 2. Mock Current Prices
        current_prices = {
            "BBCA.JK": 10500.0,
            "TLKM.JK": 3750.0
        }
        
        summary = orch.trading_agent.get_detailed_status(current_prices)
        
        # 3. Generate Report
        report = orch.generate_portfolio_report(summary, "daily")
        
        # 4. Verify Content (Accounting for markdown formatting)
        self.assertIn("PORTFOLIO REKAP (DAILY)", report)
        self.assertIn("BBCA.JK", report)
        self.assertIn("Lot: 3.50", report)
        self.assertIn("Avg: 10000.00 | Last: 10500.00", report)
        self.assertIn("PnL: +175,000.00 (+5.00%)", report)
        self.assertIn("*Cash:* 50,000.00", report)
        self.assertIn("*Equity:* 7,475,000.00", report)

    @patch('orchestrator.orchestrator.send_telegram_alert')
    def test_empty_portfolio_report(self, mock_alert):
        orch = PipelineOrchestrator()
        orch.trading_agent.portfolio.positions = {}
        summary = orch.trading_agent.get_detailed_status({})
        report = orch.generate_portfolio_report(summary, "weekly")
        
        self.assertIn("Tidak ada posisi aktif", report)
        self.assertIn("*Cash:* 100,000.00", report)

if __name__ == '__main__':
    unittest.main()
