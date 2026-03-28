import unittest
import os
import sqlite3
import uuid
from data.database import TradingDatabase

class TestTradingDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = f"tests/test_{uuid.uuid4()}.db"
        self.db = TradingDatabase(db_path=self.test_db_path)

    def tearDown(self):
        import time
        for _ in range(5):
            try:
                if os.path.exists(self.test_db_path):
                    os.remove(self.test_db_path)
                return
            except PermissionError:
                time.sleep(0.2)

    def test_schema_initialization(self):
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
            self.assertIsNotNone(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_snapshots'")
            self.assertIsNotNone(cursor.fetchone())

    def test_trade_lifecycle(self):
        # 1. Insert Trade
        trade_id = self.db.insert_trade(
            ticker="BBCA.JK", 
            entry_price=10000.0, 
            qty=100, 
            strategy="RSI_MACD", 
            timeframe="daily"
        )
        self.assertIsNotNone(trade_id)
        
        trades = self.db.get_all_trades()
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]['status'], 'OPEN')
        self.assertEqual(trades[0]['ticker'], 'BBCA.JK')
        self.assertEqual(trades[0]['entry_price'], 10000.0)

        # 2. Update Close
        self.db.update_trade_close(trade_id, exit_price=10500.0, pnl=50000.0)
        
        trades = self.db.get_all_trades()
        self.assertEqual(trades[0]['status'], 'CLOSED')
        self.assertEqual(trades[0]['exit_price'], 10500.0)
        self.assertEqual(trades[0]['pnl'], 50000.0)

    def test_portfolio_snapshots(self):
        self.db.insert_portfolio_snapshot(
            equity=100050000.0, 
            cash=99000000.0, 
            positions_value=1050000.0
        )
        
        history = self.db.get_portfolio_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['equity'], 100050000.0)
        self.assertEqual(history[0]['cash'], 99000000.0)
        self.assertEqual(history[0]['positions_value'], 1050000.0)

    def test_ordering(self):
        self.db.insert_trade("TICKER_A", 10, 1)
        import time
        time.sleep(0.1)
        self.db.insert_trade("TICKER_B", 20, 1)
        
        trades = self.db.get_all_trades()
        self.assertEqual(len(trades), 2)
        # Should be descending (newest first)
        self.assertEqual(trades[0]["ticker"], "TICKER_B")
        self.assertEqual(trades[1]["ticker"], "TICKER_A")

if __name__ == "__main__":
    unittest.main()
