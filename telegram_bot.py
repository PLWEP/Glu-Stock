import time
import requests
import json
import os
from typing import Dict, Any, Optional
from utils.config import ConfigLoader
from data.database import TradingDatabase
from utils.logger import JsonLogger

class TelegramBot:
    """
    Standalone Telegram Bot for real-time engine monitoring.
    Uses lightweight requests for long-polling.
    """
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.tel_config = self.config.get("telegram", {})
        self.token = self.tel_config.get("bot_token")
        self.chat_id = self.tel_config.get("chat_id")
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.db = TradingDatabase()
        self.logger = JsonLogger(log_file="logs/telegram_bot.log")
        self.offset = 0

    def send_message(self, text: str):
        """ Sends a message to the configured chat_id. """
        if not self.tel_config.get("enabled"):
            return
        
        url = f"{self.api_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            self.logger.error("Telegram: Failed to send message", error=str(e))

    def handle_status(self):
        """ Handles /status command. """
        # Static status check (uptime simplified)
        status_msg = "*Glu-Stock Engine Status*\n"
        status_msg += "✅ System: Online\n"
        status_msg += f"📅 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # Check last scheduler run
        log_path = "logs/scheduler.log"
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                lines = f.readlines()
                if lines:
                    last_log = json.loads(lines[-1])
                    status_msg += f"📊 Last Run: {last_log.get('timestamp')}\n"
                    status_msg += f"✅ Result: {last_log.get('message')}"
        
        self.send_message(status_msg)

    def handle_portfolio(self):
        """ Handles /portfolio command. """
        history = self.db.get_portfolio_history()
        if not history:
            self.send_message("❌ No portfolio history found.")
            return
        
        latest = history[0]
        msg = "*Current Portfolio Summary*\n"
        msg += f"💰 Cash: IDR {latest['cash']:,.2f}\n"
        msg += f"📈 Equity: IDR {latest['equity']:,.2f}\n"
        
        trades = self.db.get_all_trades()
        if trades:
            msg += "\n*Recent Positions & Trades:*\n"
            for t in trades[:5]: # Last 5 trades
                msg += f"• {t['side']} {t['ticker']} @ {t['price']:,.0f}\n"
        
        self.send_message(msg)

    def poll(self):
        """ Polling loop for Telegram updates. """
        if not self.tel_config.get("enabled"):
            print("Telegram: Bot is disabled in config. To enable, set 'enabled: true'.")
            return

        print(f"Telegram: Bot started polling (Offset: {self.offset})...")
        while True:
            try:
                url = f"{self.api_url}/getUpdates"
                params = {"offset": self.offset, "timeout": 30}
                res = requests.get(url, params=params, timeout=35).json()
                
                if res.get("ok"):
                    for update in res.get("result", []):
                        self.offset = update["update_id"] + 1
                        message = update.get("message", {})
                        text = message.get("text", "")
                        
                        if text == "/status":
                            self.handle_status()
                        elif text == "/portfolio":
                            self.handle_portfolio()
                
            except KeyboardInterrupt:
                print("Telegram: Shutting down...")
                break
            except Exception as e:
                self.logger.error("Telegram: Polling error", error=str(e))
                time.sleep(5)

if __name__ == "__main__":
    bot = TelegramBot()
    bot.poll()
