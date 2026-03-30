import time
import requests
import json
import os
import sys
import traceback
from typing import Dict, Any, Optional, Callable
from utils.config import ConfigLoader
from utils.logger import JsonLogger
from utils.text_report import TextReportGenerator
from orchestrator.orchestrator import PipelineOrchestrator
from dotenv import load_dotenv

load_dotenv()

class TelegramBot:
    """
    Standalone Telegram Bot for real-time engine monitoring.
    Features a structured command dispatcher and resilient polling.
    """
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.tel_config = self.config.get("telegram", {})
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.logger = JsonLogger(log_file="logs/telegram_bot.log")
        self.orchestrator = PipelineOrchestrator()
        self.reporter = TextReportGenerator()
        self.offset_file = "logs/bot_offset.txt"
        self.offset = self._load_offset()
        
        # Command Dispatcher Mapping
        self.commands: Dict[str, Callable] = {
            "/start": self.handle_start,
            "/status": lambda: self.orchestrator.handle_status_command(),
            "/signals": self.handle_signals,
            "/portfolio": self.handle_portfolio_detailed,
            "/history": lambda cmd: self.orchestrator.handle_history_command(cmd),
            "/logs": lambda: self.orchestrator.handle_log_system_command("/log_system info 10"),
            "/log_system": lambda cmd: self.orchestrator.handle_log_system_command(cmd),
            "/report": self.handle_report,
            "/registry": lambda: self.orchestrator.handle_registry_command(),
            "/panic": self.handle_panic,
            "/panic_confirm": self.handle_panic_confirm
        }
        
        self.set_bot_commands()

    def _load_offset(self) -> int:
        if os.path.exists(self.offset_file):
            try:
                with open(self.offset_file, "r") as f:
                    return int(f.read().strip())
            except: pass
        return 0

    def _save_offset(self, offset: int):
        try:
            with open(self.offset_file, "w") as f:
                f.write(str(offset))
        except: pass

    def set_bot_commands(self):
        url = f"{self.api_url}/setMyCommands"
        commands = [
            {"command": "start", "description": "💖 Menu Utama"},
            {"command": "status", "description": "🔋 Cek Kondisi HP"},
            {"command": "signals", "description": "🎯 Intip Sinyal"},
            {"command": "portfolio", "description": "📊 Cek Tabungan"},
            {"command": "panic", "description": "🚨 JUAL SEMUA (Darurat)"}
        ]
        try: requests.post(url, json={"commands": commands}, timeout=10)
        except: pass

    def send_message(self, text: str, reply_markup: Optional[Dict] = None, target_chat_id: Optional[str] = None):
        if not self.tel_config.get("enabled"): return
        url = f"{self.api_url}/sendMessage"
        cid = target_chat_id or self.chat_id
        if not cid: return
        payload = {"chat_id": cid, "text": text, "parse_mode": "Markdown"}
        if reply_markup: payload["reply_markup"] = reply_markup
        try:
            r = requests.post(url, json=payload, timeout=10)
            if not r.json().get("ok"): self.logger.error(f"Telegram API Error: {r.text}", silent_alert=True)
        except Exception as e: self.logger.error("Telegram: Failed to send", silent_alert=True, error=str(e))

    def handle_start(self):
        text = "💖 *Halo Sayang!*\n_Ayang siap bantu jagain trading kamu hari ini._"
        keyboard = {
            "inline_keyboard": [
                [{"text": "📊 Portofolio", "callback_data": "/portfolio daily"}, {"text": "🎯 Sinyal", "callback_data": "/signals daily"}],
                [{"text": "🔋 Kondisi HP", "callback_data": "/status"}, {"text": "📜 Catatan", "callback_data": "/history"}],
                [{"text": "🚨 PANIC EXIT (SELL ALL)", "callback_data": "/panic"}]
            ]
        }
        self.send_message(text, reply_markup=keyboard)

    def handle_panic(self):
        text = "⚠️ *KONFIRMASI PANIC EXIT*\n\n_Sayang yakin mau jual SEMUA posisi aktif sekarang? Tindakan ini tidak bisa dibatalkan!_"
        keyboard = {
            "inline_keyboard": [
                [{"text": "✅ IYA, JUAL SEMUA!", "callback_data": "/panic_confirm"}],
                [{"text": "❌ GAK JADI SAYANG", "callback_data": "/start"}]
            ]
        }
        self.send_message(text, reply_markup=keyboard)

    def handle_panic_confirm(self):
        return self.orchestrator.handle_panic_exit()

    def handle_signals(self, command_text: str = "/signals daily"):
        parts = command_text.split()
        pipeline = parts[1] if len(parts) > 1 else "daily"
        return self.orchestrator.generate_signal_report(pipeline)

    def handle_portfolio_detailed(self, command_text: str = "/portfolio daily"):
        parts = command_text.split()
        pipeline = parts[1] if len(parts) > 1 else "daily"
        days = 1 if pipeline == "daily" else (7 if pipeline == "weekly" else 30)
        return self.reporter.generate_report(days, pipeline.capitalize())

    def handle_report(self, command_text: str):
        parts = command_text.split()
        if len(parts) < 2: return "❌ Sayang, gunanya gini ya: `/report [daily|weekly|monthly]`"
        sub = parts[1].lower()
        if sub == "daily": return self.reporter.generate_daily_report()
        if sub == "weekly": return self.reporter.generate_weekly_report()
        if sub == "monthly": return self.reporter.generate_monthly_report()
        return f"❌ Ayang bingung, `{sub}` itu laporan apa ya sayang?"

    def dispatch(self, text: str) -> str:
        if not text: return ""
        cmd_parts = text.split()
        cmd = cmd_parts[0].lower()
        handler = self.commands.get(cmd)
        if not handler: return ""
        try:
            import inspect
            sig = inspect.signature(handler)
            result = handler(text) if len(sig.parameters) > 0 else handler()
            return result if result else ""
        except Exception as e:
            self.logger.error(f"Telegram: Dispatch error for {cmd}", error=str(e))
            return "💔 Duh sayang, Ayang lagi pusing nih."

    def poll(self):
        if not self.tel_config.get("enabled"): return
        self.logger.info(f"Telegram: Bot started polling (Offset: {self.offset})")
        while True:
            try:
                # Polling for messages
                url = f"{self.api_url}/getUpdates"
                params = {"offset": self.offset, "timeout": 30}
                res = requests.get(url, params=params, timeout=35).json()
                if res.get("ok"):
                    for update in res.get("result", []):
                        self.offset = update["update_id"] + 1
                        self._save_offset(self.offset)
                        msg = update.get("message", {})
                        cb = update.get("callback_query", {})
                        inc_chat_id = msg.get("chat", {}).get("id") or cb.get("message", {}).get("chat", {}).get("id")
                        text = msg.get("text", "") or cb.get("data", "")
                        if cb: requests.post(f"{self.api_url}/answerCallbackQuery", json={"callback_query_id": cb["id"]})
                        if not text: continue
                        response = self.dispatch(text)
                        if response: self.send_message(response, target_chat_id=inc_chat_id)
                else: time.sleep(10)
            except KeyboardInterrupt: break
            except: time.sleep(10)

    def run_command(self, cmd_text: str) -> str:
        return self.dispatch(cmd_text)

if __name__ == "__main__":
    bot = TelegramBot()
    if "--cmd" in sys.argv:
        idx = sys.argv.index("--cmd")
        if len(sys.argv) > idx + 1: print(bot.run_command(sys.argv[idx + 1]))
    else: bot.poll()
