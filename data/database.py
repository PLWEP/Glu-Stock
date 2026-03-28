import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any

class TradingDatabase:
    """
    Manages long-term storage of trading data using SQLite.
    Tracks trades and portfolio snapshots for institutional reporting.
    """
    def __init__(self, db_path: str = "data/trading.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_db()

    def _initialize_db(self):
        """ Creates tables for trades and portfolio snapshots. """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    qty REAL,
                    entry_date TEXT,
                    exit_date TEXT,
                    pnl REAL,
                    status TEXT, -- OPEN, CLOSED
                    strategy TEXT,
                    timeframe TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    equity REAL,
                    cash REAL,
                    positions_value REAL
                )
            """)

    def insert_trade(self, trade_data: Dict[str, Any]):
        """ Inserts a new trade record. """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO trades (ticker, entry_price, qty, entry_date, status, strategy, timeframe)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (trade_data['ticker'], trade_data['entry_price'], trade_data['qty'], 
                  trade_data.get('entry_date', datetime.now().isoformat()), 
                  'OPEN', trade_data.get('strategy'), trade_data.get('timeframe')))

    def update_trade_close(self, ticker: str, exit_price: float, pnl: float):
        """ Closes an open trade and calculates PnL. """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE trades 
                SET exit_price = ?, exit_date = ?, pnl = ?, status = 'CLOSED'
                WHERE ticker = ? AND status = 'OPEN'
            """, (exit_price, datetime.now().isoformat(), pnl, ticker))

    def get_all_trades(self) -> List[Dict[str, Any]]:
        """ Retrieves all trades as a list of dictionaries. """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades ORDER BY entry_date DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_portfolio_history(self) -> List[Dict[str, Any]]:
        """ Retrieves portfolio snapshots. """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM portfolio_snapshots ORDER BY date DESC")
            return [dict(row) for row in cursor.fetchall()]

    def record_portfolio_snapshot(self, equity: float, cash: float, positions_value: float):
        """ Records a daily snapshot of the portfolio state. """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO portfolio_snapshots (date, equity, cash, positions_value)
                VALUES (?, ?, ?, ?)
            """, (datetime.now().isoformat(), equity, cash, positions_value))

    def count_trades(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]

    def count_open_positions(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM trades WHERE status = 'OPEN'").fetchone()[0]
