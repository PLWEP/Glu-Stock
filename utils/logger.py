from utils.alerts import send_telegram_alert
import sqlite3
import os
import json
from datetime import datetime

class JsonLogger:
    """
    Structured logger that writes to console, JSON file, and SQLite database.
    Supports DEBUG, INFO, WARNING, ERROR, CRITICAL levels.
    """

    def __init__(self, log_file: str = "logs/trading.log", db_file: str = "logs/system_logs.db"):
        self.log_file = log_file
        self.db_file = db_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self._initialize_db()

    def _initialize_db(self):
        """ Creates the logging table if it doesn't exist. """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                level TEXT,
                message TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _log(self, level: str, message: str, **kwargs):
        """ Internal method to format and write the log entry. """
        now = datetime.now()
        timestamp = now.isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "metadata": kwargs
        }
        
        json_log = json.dumps(log_entry)
        
        # 1. Print to console
        print(f"[{level}] {message} {json.dumps(kwargs) if kwargs else ''}")
        
        # 2. Append to JSON file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json_log + "\n")
            
        # 3. Log to SQLite
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO logs (timestamp, level, message, metadata)
                VALUES (?, ?, ?, ?)
            """, (timestamp, level, message, json.dumps(kwargs)))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"FAILED TO LOG TO DB: {e}")

    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        """ Log an error and send a Telegram alert. """
        self._log("ERROR", message, **kwargs)
        alert_msg = f"🚨 *ERROR ALERT*\n*Msg:* {message}"
        if kwargs:
            alert_msg += f"\n*Meta:* `{json.dumps(kwargs)}`"
        send_telegram_alert(alert_msg)

    def critical(self, message: str, **kwargs):
        """ Log a critical failure and send a Telegram alert. """
        self._log("CRITICAL", message, **kwargs)
        alert_msg = f"💀 *CRITICAL FAILURE*\n*Msg:* {message}"
        if kwargs:
            alert_msg += f"\n*Meta:* `{json.dumps(kwargs)}`"
        send_telegram_alert(alert_msg)

    def query_logs(self, level: str = None, limit: int = 10):
        """ Static-like method to query logs from the DB. """
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM logs WHERE 1=1"
        params = []
        if level:
            query += " AND level = ?"
            params.append(level.upper())
            
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        res = [dict(row) for row in rows]
        conn.close()
        return res

if __name__ == "__main__":
    logger = JsonLogger(log_file="logs/test.log", db_file="logs/test_logs.db")
    logger.info("Test Info")
    logger.error("Test Error", reason="Simulated")
    print(logger.query_logs(level="INFO"))
