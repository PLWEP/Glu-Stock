import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from utils.text_report import TextReportGenerator

class TestTextReport(unittest.TestCase):
    
    @patch('data.database.TradingDatabase.get_all_trades')
    @patch('data.database.TradingDatabase.get_portfolio_history')
    def test_daily_report_filtering(self, mock_history, mock_trades):
        # Mocking data from different days
        now_str = datetime.now().isoformat()
        old_str = (datetime.now() - timedelta(days=5)).isoformat()
        
        mock_trades.return_value = [
            {"ticker": "BBCA.JK", "entry_date": now_str, "status": "CLOSED", "pnl": 1000},
            {"ticker": "TLKM.JK", "entry_date": old_str, "status": "CLOSED", "pnl": 500}
        ]
        mock_history.return_value = [
            {"date": now_str, "equity": 100000},
            {"date": old_str, "equity": 90000}
        ]
        
        gen = TextReportGenerator()
        report = gen.generate_daily_report()
        
        # Verify Daily report only includes BBCA
        self.assertIn("DAILY REPORT", report)
        self.assertIn("BBCA.JK", report)
        self.assertNotIn("TLKM.JK", report)
        self.assertIn("Portfolio Value: IDR 100,000.00", report)

    @patch('data.database.TradingDatabase.get_all_trades')
    @patch('data.database.TradingDatabase.get_portfolio_history')
    def test_weekly_report_filtering(self, mock_history, mock_trades):
        now_str = datetime.now().isoformat()
        old_str = (datetime.now() - timedelta(days=5)).isoformat()
        very_old_str = (datetime.now() - timedelta(days=20)).isoformat()
        
        mock_trades.return_value = [
            {"ticker": "BBCA.JK", "entry_date": now_str, "status": "CLOSED", "pnl": 1000},
            {"ticker": "TLKM.JK", "entry_date": old_str, "status": "CLOSED", "pnl": 500},
            {"ticker": "GOTO.JK", "entry_date": very_old_str, "status": "CLOSED", "pnl": 100}
        ]
        mock_history.return_value = [
            {"date": now_str, "equity": 100000},
            {"date": old_str, "equity": 95000}
        ]
        
        gen = TextReportGenerator()
        report = gen.generate_weekly_report()
        
        # Weekly should include BBCA and TLKM, but not GOTO
        self.assertIn("WEEKLY REPORT", report)
        self.assertIn("BBCA.JK", report)
        self.assertIn("TLKM.JK", report)
        self.assertNotIn("GOTO.JK", report)

    @patch('data.database.TradingDatabase.get_all_trades')
    @patch('data.database.TradingDatabase.get_portfolio_history')
    def test_no_trades_fallback(self, mock_history, mock_trades):
        # Case: History exists but no trades in period
        mock_trades.return_value = []
        mock_history.return_value = [{"date": "2024-03-27", "equity": 150000}]
        
        gen = TextReportGenerator()
        report = gen.generate_daily_report()
        
        self.assertIn("DAILY REPORT", report)
        self.assertIn("Portfolio Value: IDR 150,000.00", report)
        self.assertIn("No trades executed today", report)
        self.assertIn("System is running normally", report)
        self.assertIn("Generated:", report)

    @patch('data.database.TradingDatabase.get_all_trades')
    @patch('data.database.TradingDatabase.get_portfolio_history')
    def test_complete_empty_case(self, mock_history, mock_trades):
        # Case: No history and no trades
        mock_trades.return_value = []
        mock_history.return_value = []
        
        gen = TextReportGenerator()
        report = gen.generate_daily_report()
        
        self.assertIn("DAILY REPORT", report)
        self.assertIn("Generated:", report)
        self.assertIn("No trades executed today", report)

    @patch('data.database.TradingDatabase.get_all_trades')
    def test_error_handling(self, mock_trades):
        # Case: Database crash
        mock_trades.side_effect = Exception("DB Connection Lost")
        
        gen = TextReportGenerator()
        report = gen.generate_daily_report()
        
        self.assertIn("ERROR: DB Connection Lost", report)
        self.assertIn("DAILY REPORT", report)

if __name__ == "__main__":
    unittest.main()
