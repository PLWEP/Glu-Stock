import json
import os
from datetime import datetime
from typing import Any
from utils.alerts import send_telegram_alert

class JsonLogger:
    """
    A lightweight logger that outputs structured JSON logs to both 
    the console and a persistent file. Support INFO and ERROR levels.
    """

    def __init__(self, log_file: str = "logs/trading.log"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def _log(self, level: str, message: str, **kwargs):
        """ Internal method to format and write the log entry. """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "metadata": kwargs
        }
        
        json_log = json.dumps(log_entry)
        
        # 1. Print to console
        print(json_log)
        
        # 2. Append to file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json_log + "\n")

    def info(self, message: str, **kwargs):
        """ Log an informational message. """
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """ Log a warning message. """
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        """ Log an error message and send a Telegram alert. """
        self._log("ERROR", message, **kwargs)
        # Trigger Telegram alert for errors
        alert_msg = f"🚨 *ERROR ALERT*\n*Msg:* {message}"
        if kwargs:
            alert_msg += f"\n*Meta:* `{json.dumps(kwargs)}`"
        send_telegram_alert(alert_msg)

if __name__ == "__main__":
    # Quick sanity check
    logger = JsonLogger(log_file="logs/test.log")
    logger.info("System initialized", version="1.1.0")
    logger.error("Order failed", ticker="BBCA.JK", reason="Insufficient funds")
