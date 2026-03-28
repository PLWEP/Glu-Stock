import time
import requests
import json
import os
from typing import Dict, Any, Optional
from utils.config import ConfigLoader
from utils.logger import JsonLogger
from utils.text_report import TextReportGenerator
from orchestrator.orchestrator import PipelineOrchestrator
from dotenv import load_dotenv

# Explicitly load .env from the same directory as this script
load_dotenv()

class TelegramBot:
    """
    Standalone Telegram Bot for real-time engine monitoring.
    Uses lightweight requests for long-polling.
    """
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.tel_config = self.config.get("telegram", {})
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        
        if not self.token:
            print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in environment!")
        if not self.chat_id:
            print("⚠️ WARNING: TELEGRAM_CHAT_ID not found in environment!")
            
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.logger = JsonLogger(log_file="logs/telegram_bot.log")
        self.orchestrator = PipelineOrchestrator()
        self.reporter = TextReportGenerator()
        self.offset = 0
        
        # Register commands on startup
        self.set_bot_commands()

    def set_bot_commands(self):
        """ Registers command hints in the Telegram menu. """
        url = f"{self.api_url}/setMyCommands"
        commands = [
            {"command": "start", "description": "🚀 Buka Command Center"},
            {"command": "status", "description": "🔋 Cek Kondisi Termux (RAM/Bat)"},
            {"command": "signals", "description": "🎯 Cek Sinyal Trading (Daily/Weekly)"},
            {"command": "portfolio", "description": "📊 Cek Rekap Portofolio"},
            {"command": "history", "description": "📜 Cek Histori Audit Strategis"},
            {"command": "log_system", "description": "📂 Cek Log Internal Aplikasi"},
            {"command": "logs", "description": "📋 Tampilkan 10 Log terakhir"}
        ]
        try:
            requests.post(url, json={"commands": commands}, timeout=10)
            self.logger.info("Telegram: Commands registered successfully")
        except: pass

    def send_message(self, text: str, reply_markup: Optional[Dict] = None, target_chat_id: Optional[str] = None):
        """ Sends a message with optional inline keyboard. """
        if not self.tel_config.get("enabled"):
            return
        
        url = f"{self.api_url}/sendMessage"
        cid = target_chat_id or self.chat_id
        
        if not cid:
            self.logger.error("Telegram: No chat_id provided and TELEGRAM_CHAT_ID is missing")
            return
            
        payload = {
            "chat_id": cid, 
            "text": text, 
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
            
        try:
            r = requests.post(url, json=payload, timeout=10)
            if not r.json().get("ok"):
                self.logger.error(f"Telegram: API error: {r.text}")
        except Exception as e:
            self.logger.error("Telegram: Failed to send", error=str(e))

    def handle_start(self):
        """ Sends the interactive Command Center. """
        text = "🎮 *GLU-STOCK COMMAND CENTER*\n_Pilih aksi cepat di bawah ini atau ketik / untuk menu lengkap._"
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🔋 Status", "callback_data": "/status"},
                    {"text": "📊 Portfolio", "callback_data": "/portfolio daily"}
                ],
                [
                    {"text": "🚀 Daily Signals", "callback_data": "/signals daily"},
                    {"text": "🚀 Weekly Signals", "callback_data": "/signals weekly"}
                ],
                [
                    {"text": "📜 Recent History", "callback_data": "/history"},
                    {"text": "📂 Errors", "callback_data": "/log_system error"}
                ]
            ]
        }
        self.send_message(text, reply_markup=keyboard)

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
        log_path = "logs/trading.log"
        if os.path.exists(log_path):
            try:
                with open(log_path, "rb") as f:
                    # Efficiently seek to end and find last line
                    f.seek(0, os.SEEK_END)
                    pos = f.tell()
                    buffer = []
                    while pos > 0:
                        pos -= 1
                        f.seek(pos)
                        char = f.read(1)
                        if char == b"\n" and buffer:
                            break
                        buffer.append(char)
                    
                    last_line = b"".join(reversed(buffer)).decode("utf-8").strip()
                    if last_line:
                        last_log = json.loads(last_line)
                        status_msg += f"📊 Last Activity: {last_log.get('timestamp')}\n"
                        status_msg += f"✅ Message: {last_log.get('message')}"
            except Exception as e:
                self.logger.error("Telegram: Failed to read last log line", error=str(e))
        
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
                        callback_query = update.get("callback_query", {})
                        
                        inc_chat_id = None
                        if message:
                            inc_chat_id = message.get("chat", {}).get("id")
                            text = message.get("text", "")
                        elif callback_query:
                            inc_chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
                            text = callback_query.get("data", "")
                            # Answer callback
                            requests.post(f"{self.api_url}/answerCallbackQuery", json={"callback_query_id": callback_query["id"]})
                        
                        if not text: continue
                        
                        cmd = text.split()[0].lower()
                        
                        # Helper to send response back to the sender
                        def reply(msg, markup=None):
                            self.send_message(msg, markup, target_chat_id=inc_chat_id)

                        if cmd == "/start":
                            text_start = "🎮 *GLU-STOCK COMMAND CENTER*\n_Pilih aksi di bawah ini._"
                            keyboard = {
                                "inline_keyboard": [
                                    [{"text": "🔋 Status", "callback_data": "/status"}, {"text": "📊 Portfolio", "callback_data": "/portfolio daily"}],
                                    [{"text": "🚀 Signals", "callback_data": "/signals daily"}, {"text": "📜 History", "callback_data": "/history"}],
                                    [{"text": "📂 Logs", "callback_data": "/logs"}]
                                ]
                            }
                            reply(text_start, keyboard)
                        elif cmd == "/status":
                            reply(self.orchestrator.handle_status_command())
                        elif cmd == "/logs":
                            reply(self.orchestrator.handle_log_system_command("/log_system info 10"))
                        elif cmd in ["/portfolio", "/recap"]:
                            # Note: broadcast functions might still use self.chat_id, but here we can at least handle direct requests
                            pipeline = text.split()[1] if len(text.split()) > 1 else "daily"
                            report = self.reporter.generate_report(1 if pipeline=="daily" else (7 if pipeline=="weekly" else 30), pipeline.capitalize())
                            reply(report)
                        elif cmd in ["/signals", "/alert"]:
                            pipeline = text.split()[1] if len(text.split()) > 1 else "daily"
                            signals = self.orchestrator.persistence.load_signals(pipeline)
                            report = self.orchestrator.generate_signal_report(pipeline)
                            reply(report)
                        elif cmd == "/history":
                            reply(self.orchestrator.handle_history_command(text))
                        elif cmd in ["/log_system", "/log-system"]:
                            reply(self.orchestrator.handle_log_system_command(text))
                        elif cmd.startswith("/report"):
                            self.handle_report(text)
                else:
                    self.logger.error(f"Telegram: Poll Failed: {res.get('description', 'Unknown Error')}")
                
            except KeyboardInterrupt:
                print("Telegram: Shutting down...")
                break
            except Exception as e:
                import traceback
                error_msg = f"Telegram: Polling error: {str(e)}\n{traceback.format_exc()}"
                self.logger.error("Telegram: Polling error", error=error_msg)
                time.sleep(5)

if __name__ == "__main__":
    import sys
    bot = TelegramBot()
    if "--test" in sys.argv:
        bot.test_telegram()
    else:
        bot.poll()
