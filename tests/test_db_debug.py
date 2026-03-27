import unittest
import os
import io
import sys
from data.database import TradingDatabase

class TestDatabaseDebug(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "data/test_debug.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = TradingDatabase(db_path=self.test_db)

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_trade_counters(self):
        # 1. Initial counts
        self.assertEqual(self.db.count_trades(), 0)
        self.assertEqual(self.db.count_open_positions(), 0)
        
        # 2. Add trades
        tid1 = self.db.insert_trade("AAPL", 150.0, 10)
        self.db.insert_trade("TSLA", 200.0, 5)
        
        self.assertEqual(self.db.count_trades(), 2)
        self.assertEqual(self.db.count_open_positions(), 2)
        
        # 3. Close a trade
        self.db.update_trade_close(tid1, 160.0, 100.0)
        
        self.assertEqual(self.db.count_trades(), 2)
        self.assertEqual(self.db.count_open_positions(), 1)

    def test_runtime_logging(self):
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            self.db.insert_trade("AAPL", 150.0, 10)
            output = captured_output.getvalue()
            
            self.assertIn("Total trades in DB: 1", output)
            self.assertIn("Trade inserted for AAPL", output)
            
            # Reset buffer
            captured_output.truncate(0)
            captured_output.seek(0)
            
            self.db.update_trade_close(1, 160.0, 100.0)
            output_close = captured_output.getvalue()
            self.assertIn("Total trades in DB: 1", output_close)
            self.assertIn("Trade 1 closed", output_close)
            
        finally:
            sys.stdout = sys.__stdout__

if __name__ == "__main__":
    unittest.main()
