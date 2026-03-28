import unittest
import os
import sqlite3
from orchestrator.orchestrator import PipelineOrchestrator
from utils.history import StrategicHistoryManager

class TestStrategicHistory(unittest.TestCase):
    
    def setUp(self):
        self.db_path = "data/test_history.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.hm = StrategicHistoryManager(db_path=self.db_path)
        
    def test_logging_and_query(self):
        """ Verify that events are logged to SQLite and retrievable via command. """
        # 1. Log mixed events
        self.hm.log_event("daily", "SCAN_START", details="Tickers: 10")
        self.hm.log_event("daily", "AUDIT", "BBCA.JK", 55.5, "PASS", "PF: 1.50")
        self.hm.log_event("daily", "TRADE", "BBCA.JK", status="SUCCESS")
        self.hm.log_event("daily", "RECAP", "BBCA.JK", 2.5, "PROFIT", "Lots: 10, PnL: 2M")
        
        # 2. Inject this HM into a mock orchestrator
        orch = PipelineOrchestrator()
        orch.history_manager = self.hm
        
        # 3. Test Command Parser
        # a) Recent History
        report = orch.handle_history_command("/history")
        self.assertIn("RECENT", report.upper())
        self.assertIn("RECAP", report.upper())
        self.assertIn("PROFIT", report.upper())
        
        # b) Strategy Filter
        report_daily = orch.handle_history_command("/history daily")
        self.assertIn("DAILY", report_daily.upper())
        
        # c) Ticker Filter
        report_ticker = orch.handle_history_command("/history BBCA.JK")
        self.assertIn("BBCA.JK", report_ticker.upper())
        self.assertIn("PF: 1.50", report_ticker.upper())

if __name__ == '__main__':
    unittest.main()
