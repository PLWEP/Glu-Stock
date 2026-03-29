import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List

class BacktestRegistry:
    """
    Manages a database of all historical backtest experiments.
    Allows for tracking strategy iterations and comparing results.
    """

    def __init__(self, db_path: str = "data/backtests.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    pipeline TEXT,
                    ticker TEXT,
                    sharpe REAL,
                    expectancy REAL,
                    win_rate REAL,
                    total_trades INTEGER,
                    oos_sharpe REAL,
                    risk_of_ruin REAL,
                    params_json TEXT
                )
            """)

    def log_backtest(self, pipeline: str, ticker: str, results: Dict[str, Any], params: Dict[str, Any] = None):
        """ Logs a full backtest result summary. """
        is_metrics = results.get('is', {}).get('metrics', {})
        oos_metrics = results.get('oos', {}).get('metrics', {})
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO experiments (
                    date, pipeline, ticker, sharpe, expectancy, win_rate, 
                    total_trades, oos_sharpe, params_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                pipeline,
                ticker,
                is_metrics.get('sharpe_ratio', 0),
                is_metrics.get('expectancy', 0),
                is_metrics.get('win_rate', 0),
                results.get('total_trades', 0),
                oos_metrics.get('sharpe_ratio', 0),
                str(params)
            ))

    def get_top_experiments(self, limit: int = 10) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM experiments ORDER BY oos_sharpe DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
