import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from data.database import TradingDatabase

class HistoryManager:
    def __init__(self, db_path: str = "data/strategic_history.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_db()
        self.db = TradingDatabase()

    def _initialize_db(self):
        """ Creates the history table if it doesn't exist. """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                strategy TEXT,
                phase TEXT,
                ticker TEXT,
                metric_value REAL,
                status TEXT,
                details TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log_event(self, strategy: str, phase: str, ticker: str = "SYSTEM", 
                  metric: float = 0.0, status: str = "INFO", details: str = ""):
        """ Logs a structured event to the database. """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO history (strategy, phase, ticker, metric_value, status, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (strategy.lower(), phase.upper(), ticker, metric, status.upper(), details))
        conn.commit()
        conn.close()

    def query_history(self, strategy: Optional[str] = None, 
                      ticker: Optional[str] = None, 
                      limit: int = 10) -> List[Dict[str, Any]]:
        """ Queries history with optional filters. """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM history WHERE 1=1"
        params = []
        
        if strategy:
            query += " AND strategy = ?"
            params.append(strategy.lower())
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker.upper())
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = [dict(row) for row in rows]
        conn.close()
        return results

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """ Alias for query_history to support orchestrator CLI. """
        return self.query_history(limit=limit)

    def get_daily_summary(self, date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """ Gets all events for a specific date (YYYY-MM-DD). """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
            
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM history 
            WHERE date(timestamp) = ? 
            ORDER BY timestamp ASC
        """, (date_str,))
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        conn.close()
        return results
