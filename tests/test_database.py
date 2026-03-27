import unittest
import os
import sqlite3
from data.database import TradingDatabase

class TestTradingDatabase(unittest.TestCase):
    def setUp(self):
        import uuid
        self.test_db_path = f"tests/trading_test_{uuid.uuid4()}.db"
        self.db = TradingDatabase(db_path=self.test_db_path)

    def tearDown(self):
        import time
        import os
        # Retry deletion for Windows file lock resilience
        for _ in range(5):
            try:
                if os.path.exists(self.test_db_path):
                    os.remove(self.test_db_path)
                return
            except PermissionError:
                time.sleep(0.2)

    def test_schema_initialization(self):
        # Verify tables exist
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
            self.assertIsNotNone(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_history'")
            self.assertIsNotNone(cursor.fetchone())

    def test_trade_persistence(self):
        self.db.record_trade("BBCA.JK", "BUY", 100, 10000.0)
        trades = self.db.get_all_trades()
        
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["ticker"], "BBCA.JK")
        self.assertEqual(trades[0]["side"], "BUY")
        self.assertEqual(trades[0]["quantity"], 100)
        self.assertEqual(trades[0]["price"], 10000.0)
        self.assertEqual(trades[0]["total_value"], 1000000.0)

    def test_portfolio_snapshot_persistence(self):
        self.db.record_portfolio_snapshot(105000000.0, 95000000.0)
        history = self.db.get_portfolio_history()
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["equity"], 105000000.0)
        self.assertEqual(history[0]["cash"], 95000000.0)

    def test_ordering(self):
        # Insert two trades
        self.db.record_trade("A", "BUY", 1, 10)
        import time
        time.sleep(0.1)
        self.db.record_trade("B", "BUY", 1, 20)
        
        trades = self.db.get_all_trades()
        self.assertEqual(len(trades), 2)
        # Should be descending (newest first)
        self.assertEqual(trades[0]["ticker"], "B")
        self.assertEqual(trades[1]["ticker"], "A")

if __name__ == "__main__":
    unittest.main()
