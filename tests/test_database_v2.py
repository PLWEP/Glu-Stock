import unittest
import os
from data.database import TradingDatabase

class TestDatabaseV2(unittest.TestCase):
    def setUp(self):
        self.db_path = "data/test_v2_unit.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.db = TradingDatabase(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

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

        # 2. Update Close
        self.db.update_trade_close(trade_id, exit_price=10500.0, pnl=50000.0)
        
        trades = self.db.get_all_trades()
        self.assertEqual(trades[0]['status'], 'CLOSED')
        self.assertEqual(trades[0]['exit_price'], 10500.0)
        self.assertEqual(trades[0]['pnl'], 50000.0)

    def test_portfolio_snapshots(self):
        # 1. Insert Snapshot
        self.db.insert_portfolio_snapshot(
            equity=100050000.0, 
            cash=99000000.0, 
            positions_value=1050000.0
        )
        
        history = self.db.get_portfolio_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['equity'], 100050000.0)
        self.assertEqual(history[0]['positions_value'], 1050000.0)

    def test_backward_compatibility(self):
        # Test record_trade wrapper
        self.db.record_trade("TLKM.JK", "BUY", 100, 4000)
        trades = self.db.get_all_trades()
        self.assertEqual(trades[0]['ticker'], "TLKM.JK")
        self.assertEqual(trades[0]['status'], "OPEN")

if __name__ == "__main__":
    unittest.main()
