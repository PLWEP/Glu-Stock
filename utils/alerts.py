import requests
import os
import subprocess
from utils.config import ConfigLoader

def send_telegram_alert(message: str, parse_mode: str = "Markdown"):
    """
    Sends a one-off Telegram notification.
    """
    try:
        config = ConfigLoader().get_config()
        tel_config = config.get("telegram", {})
        
        token = os.environ.get("TELEGRAM_BOT_TOKEN") or tel_config.get("bot_token")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID") or tel_config.get("chat_id")
        
        if not token or not chat_id:
            return
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

def send_whatsapp_alert(message: str):
    """
    Sends a one-off WhatsApp notification via the Baileys bridge (Node.js).
    """
    try:
        # We call the node script with --send argument
        # Use shell=True if needed for environment variables or path resolution
        # But here we try direct execution.
        subprocess.run(["node", "wa_bot.js", "--send", message], 
                       capture_output=True, text=True, timeout=15)
    except Exception:
        pass

def broadcast_alert(message: str, parse_mode: str = "Markdown"):
    """
    Broadcasts the message to all configured platforms (Telegram, WhatsApp, etc).
    """
    # 1. Telegram
    send_telegram_alert(message, parse_mode)
    
    # 2. WhatsApp
    send_whatsapp_alert(message)
