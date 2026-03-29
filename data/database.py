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

    def get_performance_stats(self) -> Dict[str, float]:
        """ Returns win rate and payoff ratio for Kelly Criterion. """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pnl FROM trades WHERE status = 'CLOSED'")
            pnls = [row[0] for row in cursor.fetchall() if row[0] is not None]
            
            if not pnls:
                return {"win_rate": 0.5, "win_loss_ratio": 1.5, "total_trades": 0}
                
            wins = [p for p in pnls if p > 0]
            losses = [abs(p) for p in pnls if p < 0]
            
            win_rate = len(wins) / len(pnls)
            avg_win = sum(wins) / len(wins) if wins else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            
            # Payoff Ratio (b in Kelly)
            win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1.5
            
            return {
                "win_rate": win_rate,
                "win_loss_ratio": win_loss_ratio,
                "total_trades": len(pnls)
            }

    def count_trades(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]

    def count_open_positions(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM trades WHERE status = 'OPEN'").fetchone()[0]
