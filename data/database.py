import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any

class TradingDatabase:
    """
    Handles SQLite persistence for trades and portfolio history.
    Ensures thread-safe (or at least centralized) access to the trading database.
    """

    def __init__(self, db_path: str = "data/trading.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_tables()

    def _get_connection(self):
        """ Returns a connection to the SQLite database. """
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """ Initializes the database schema. """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # 1. Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    total_value REAL NOT NULL
                )
            """)
            # 2. Portfolio history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    equity REAL NOT NULL,
                    cash REAL NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def record_trade(self, ticker: str, side: str, quantity: float, price: float):
        """ Persists a trade record to the database. """
        timestamp = datetime.now().isoformat()
        total_value = quantity * price
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trades (timestamp, ticker, side, quantity, price, total_value)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, ticker, side, quantity, price, total_value))
            conn.commit()
        finally:
            conn.close()

    def record_portfolio_snapshot(self, equity: float, cash: float):
        """ Persists a portfolio snapshot to the database. """
        timestamp = datetime.now().isoformat()
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO portfolio_history (timestamp, equity, cash)
                VALUES (?, ?, ?)
            """, (timestamp, equity, cash))
            conn.commit()
        finally:
            conn.close()

    def get_all_trades(self) -> List[Dict[str, Any]]:
        """ Retrieves all trades as a list of dictionaries. """
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_portfolio_history(self) -> List[Dict[str, Any]]:
        """ Retrieves portfolio history as a list of dictionaries. """
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM portfolio_history ORDER BY timestamp DESC")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

if __name__ == "__main__":
    # Test initialization
    db = TradingDatabase(db_path="data/test_trading.db")
    db.record_trade("BBCA.JK", "BUY", 100, 10000)
    db.record_portfolio_snapshot(100000000, 99000000)
    print(db.get_all_trades())
    print(db.get_portfolio_history())
