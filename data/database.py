import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class TradingDatabase:
    """
    Handles SQLite persistence for trades and portfolio snapshots.
    Compatible with Termux and standard Python environments.
    """

    def __init__(self, db_path: str = "data/trading.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_tables()

    def _get_connection(self):
        """ Returns a connection to the SQLite database. """
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """ Initializes the database schema with the requested tables. """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 1. Trades table (extended lifecycle tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    qty INTEGER NOT NULL,
                    entry_date TEXT NOT NULL,
                    exit_date TEXT,
                    pnl REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'OPEN',
                    strategy TEXT,
                    timeframe TEXT
                )
            """)
            
            # 2. Portfolio snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    equity REAL NOT NULL,
                    cash REAL NOT NULL,
                    positions_value REAL NOT NULL
                )
            """)
            
            conn.commit()
        finally:
            conn.close()

    # --- Trade Functions ---

    def insert_trade(self, ticker: str, entry_price: float, qty: int, strategy: str = "Default", timeframe: str = "daily") -> int:
        """ Creates a new OPEN trade record. Returns the trade ID. """
        entry_date = datetime.now().isoformat()
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trades (ticker, entry_price, qty, entry_date, status, strategy, timeframe)
                VALUES (?, ?, ?, ?, 'OPEN', ?, ?)
            """, (ticker, entry_price, qty, entry_date, strategy, timeframe))
            conn.commit()
            trade_id = cursor.lastrowid
            print(f"Database: Trade inserted for {ticker}. Total trades in DB: {self.count_trades()}")
            return trade_id
        except Exception as e:
            print(f"Database Error: Failed to insert trade: {str(e)}")
            raise e
        finally:
            conn.close()

    def update_trade_close(self, trade_id: int, exit_price: float, pnl: float):
        """ Closes an existing trade record with exit data. """
        exit_date = datetime.now().isoformat()
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE trades 
                SET exit_price = ?, exit_date = ?, pnl = ?, status = 'CLOSED'
                WHERE id = ?
            """, (exit_price, exit_date, pnl, trade_id))
            conn.commit()
            print(f"Database: Trade {trade_id} closed. Total trades in DB: {self.count_trades()}")
        except Exception as e:
            print(f"Database Error: Failed to close trade {trade_id}: {str(e)}")
            raise e
        finally:
            conn.close()

    def get_all_trades(self) -> List[Dict[str, Any]]:
        """ Retrieves all trades as a list of dictionaries. """
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades ORDER BY entry_date DESC")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # --- Portfolio Functions ---

    def insert_portfolio_snapshot(self, equity: float, cash: float, positions_value: float):
        """ Persists a granular portfolio snapshot. """
        date = datetime.now().isoformat()
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO portfolio_snapshots (date, equity, cash, positions_value)
                VALUES (?, ?, ?, ?)
            """, (date, equity, cash, positions_value))
            conn.commit()
        finally:
            conn.close()

    def get_portfolio_history(self) -> List[Dict[str, Any]]:
        """ Retrieves portfolio history as a list of dictionaries. """
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM portfolio_snapshots ORDER BY date DESC")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # --- Debug & Utility Functions ---

    def count_trades(self) -> int:
        """ Returns the total number of trades in the database. """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM trades")
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def count_open_positions(self) -> int:
        """ Returns the number of currently OPEN trades. """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'OPEN'")
            return cursor.fetchone()[0]
        finally:
            conn.close()


if __name__ == "__main__":
    # Test initialization
    db = TradingDatabase(db_path="data/test_v2.db")
    tid = db.insert_trade("BBCA.JK", 10000, 100)
    db.update_trade_close(tid, 10500, 50000)
    db.insert_portfolio_snapshot(100050000, 99000000, 1050000)
    
    print("Trades:", db.get_all_trades())
    print("Portfolio:", db.get_portfolio_history())
