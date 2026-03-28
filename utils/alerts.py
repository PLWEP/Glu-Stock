import requests
from utils.config import ConfigLoader

def send_telegram_alert(message: str, parse_mode: str = "Markdown"):
    """
    Sends a one-off Telegram notification using configurations from config.yaml.
    """
    try:
        config = ConfigLoader().get_config()
        tel_config = config.get("telegram", {})
        
        if not tel_config.get("enabled"):
            return
            
        import os
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
        # Prevent alerting failures from crashing the main engine
        pass
