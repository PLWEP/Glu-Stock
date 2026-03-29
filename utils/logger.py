import sqlite3
import os
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from utils.alerts import broadcast_alert

class JsonLogger:
    """
    Structured logger that writes to console, Rotating JSON file, and SQLite database.
    Supports DEBUG, INFO, WARNING, ERROR, CRITICAL levels.
    """

    def __init__(self, log_file: str = "logs/trading.log", db_file: str = "logs/system_logs.db"):
        self.log_file = log_file
        self.db_file = db_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Guard to prevent infinite alert recursion during network/API failures
        self._is_alerting = False
        
        # Setup Rotating File Handler (Standard logging for file)
        self.file_logger = logging.getLogger(log_file)
        self.file_logger.setLevel(logging.DEBUG)
        if not self.file_logger.handlers:
            handler = RotatingFileHandler(self.log_file, maxBytes=5*1024*1024, backupCount=3)
            self.file_logger.addHandler(handler)
            
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

    def _log(self, level: str, message: str, silent_alert: bool = False, **kwargs):
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
        
        # 2. Log to File (Rotating)
        self.file_logger.info(json_log)
            
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
            # Fallback console print if DB fails
            print(f"FAILED TO LOG TO DB: {e}")

        # 4. Proactive Alerting (Conditional)
        if level in ["ERROR", "CRITICAL"] and not silent_alert and not self._is_alerting:
            self._is_alerting = True
            try:
                alert_prefix = "⚠️ *Error*" if level == "ERROR" else "‼️ *Critical*"
                alert_msg = f"{alert_prefix}: {message}"
                if kwargs:
                    alert_msg += f"\n*Detail:* `{json.dumps(kwargs)}`"
                broadcast_alert(alert_msg)
            except:
                pass # Prevent loop if alerting fails
            finally:
                self._is_alerting = False

    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, silent_alert: bool = False, **kwargs):
        self._log("ERROR", message, silent_alert=silent_alert, **kwargs)

    def critical(self, message: str, silent_alert: bool = False, **kwargs):
        self._log("CRITICAL", message, silent_alert=silent_alert, **kwargs)

    def query_logs(self, level: str = None, limit: int = 10):
        """ Queries logs from the DB. """
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
