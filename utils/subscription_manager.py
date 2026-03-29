import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class SubscriptionManager:
    """
    Handles subscriber white-listing, expiry tracking, and database operations.
    Supports administrative automation for the Telegram SaaS model.
    """

    def __init__(self, db_path: str = "data/subscribers.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    join_date DATETIME,
                    expiry_date DATETIME,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            conn.commit()

    def add_subscriber(self, user_id: int, username: str, days: int = 30) -> str:
        """ Adds or renews a subscriber. """
        expiry = datetime.now() + timedelta(days=days)
        expiry_str = expiry.isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO subscribers (user_id, username, join_date, expiry_date, is_active)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                    expiry_date = ?,
                    is_active = 1
            """, (user_id, username, datetime.now().isoformat(), expiry_str, expiry_str))
            conn.commit()
        return f"✅ User {user_id} (@{username}) aktif sampai {expiry_str[:10]}"

    def list_active_subscribers(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM subscribers WHERE is_active = 1")
            return [dict(row) for row in cursor.fetchall()]

    def get_expired_subscribers(self) -> List[int]:
        """ Returns list of user_ids whose subscription has passed expiry_date. """
        now = datetime.now().isoformat()
        expired_ids = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT user_id FROM subscribers WHERE expiry_date < ? AND is_active = 1", (now,))
            expired_ids = [row[0] for row in cursor.fetchall()]
        return expired_ids

    def deactivate_subscribers(self, user_ids: List[int]):
        if not user_ids: return
        with sqlite3.connect(self.db_path) as conn:
            placeholders = ",".join(["?"] * len(user_ids))
            conn.execute(f"UPDATE subscribers SET is_active = 0 WHERE user_id IN ({placeholders})", user_ids)
            conn.commit()

    def is_authorized(self, user_id: int) -> bool:
        """ Checks if a user is currently an active subscriber. """
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM subscribers WHERE user_id = ? AND expiry_date > ? AND is_active = 1", (user_id, now))
            return cursor.fetchone() is not None
