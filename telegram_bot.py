import time
import requests
import json
import os
from typing import Dict, Any, Optional
from utils.config import ConfigLoader
from data.database import TradingDatabase
from utils.logger import JsonLogger
from utils.text_report import TextReportGenerator

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
        self.reporter = TextReportGenerator()
        self.offset = 0

    def send_message(self, text: str):
        """ Sends a message to the configured chat_id with strict debug logging. """
        if not self.tel_config.get("enabled"):
            return
        
        url = f"{self.api_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"}
        
        print(f"Telegram: Sending message to Telegram...")
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("Telegram: Message sent successfully")
            else:
                print(f"Telegram: Failed with status {response.status_code}")
                print(f"Telegram: Response: {response.text}")
                self.logger.error("Telegram: API Error", status=response.status_code, body=response.text)
        except Exception as e:
            print(f"Telegram: CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            self.logger.error("Telegram: Failed to send message", error=str(e))

    def test_telegram(self):
        """ Standalone connectivity test. """
        print("Telegram: Running connectivity test...")
        self.send_message("✅ *TELEGRAM TEST SUCCESS*\nSystem: Glu-Stock Engine")

    def handle_status(self):
        """ Handles /status command. """
        # Static status check (uptime simplified)
        status_msg = "*Glu-Stock Engine Status*\n"
        status_msg += "✅ System: Online\n"
        status_msg += f"📅 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # Check last scheduler run
        log_path = "logs/trading.log" # Updated to main trading log
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                lines = f.readlines()
                if lines:
                    last_log = json.loads(lines[-1])
                    status_msg += f"📊 Last Activity: {last_log.get('timestamp')}\n"
                    status_msg += f"✅ Message: {last_log.get('message')}"
        
        self.send_message(status_msg)

    def handle_portfolio(self):
        """ Handles /portfolio command - Provides a detailed performance summary. """
        report = self.reporter.generate_daily_report()
        self.send_message(report)

    def handle_report(self, command_text: str):
        """ Handles /report [daily|weekly] commands. """
        parts = command_text.split()
        if len(parts) < 2:
            self.send_message("❌ Usage: `/report [daily|weekly|monthly]`")
            return
        
        subcommand = parts[1].lower()
        if subcommand == "daily":
            self.send_message(self.reporter.generate_daily_report())
        elif subcommand == "weekly":
            self.send_message(self.reporter.generate_weekly_report())
        elif subcommand == "monthly":
            self.send_message(self.reporter.generate_monthly_report())
        else:
            self.send_message(f"❌ Unknown report type: `{subcommand}`")

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
                        elif text.startswith("/report"):
                            self.handle_report(text)
                
            except KeyboardInterrupt:
                print("Telegram: Shutting down...")
                break
            except Exception as e:
                self.logger.error("Telegram: Polling error", error=str(e))
                time.sleep(5)

if __name__ == "__main__":
    import sys
    bot = TelegramBot()
    if "--test" in sys.argv:
        bot.test_telegram()
    else:
        bot.poll()
