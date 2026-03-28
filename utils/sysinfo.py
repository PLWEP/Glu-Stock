import os
import psutil
import time
import subprocess
import json
from datetime import datetime
from typing import Dict, Any

class SysInfo:
    """
    Utility for tracking hardware health and process resources on Termux/Android.
    """
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()

    def get_uptime_str(self) -> str:
        """ Returns process uptime in a readable format. """
        uptime_seconds = int(time.time() - self.start_time)
        days, rem = divmod(uptime_seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        
        parts = []
        if days > 0: parts.append(f"{days}d")
        if hours > 0: parts.append(f"{hours}h")
        if minutes > 0: parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)

    def get_memory_stats(self) -> Dict[str, Any]:
        """ Returns process memory and system memory stats. """
        mem = psutil.virtual_memory()
        process_mem = self.process.memory_info().rss / (1024 * 1024) # MB
        
        return {
            "process_mb": round(process_mem, 2),
            "total_gb": round(mem.total / (1024**3), 2),
            "free_gb": round(mem.available / (1024**3), 2),
            "percent": mem.percent
        }

    def get_hardware_status(self) -> Dict[str, Any]:
        """ 
        Attempts to get battery and thermal info. 
        Note: termux-battery-status requires termux-api package. 
        """
        status = {
            "battery_pct": "N/A",
            "battery_status": "N/A",
            "temp": "N/A",
            "cpu_pct": psutil.cpu_percent(interval=None)
        }
        
        # Try Termux API for Battery
        try:
            result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                status["battery_pct"] = f"{data.get('percentage')}%"
                status["battery_status"] = data.get("status")
                status["temp"] = f"{data.get('temperature'):.1f}°C"
        except:
            # Fallback to psutil (might work on some mobile linux environments)
            try:
                battery = psutil.sensors_battery()
                if battery:
                    status["battery_pct"] = f"{battery.percent}%"
                    status["battery_status"] = "Charging" if battery.power_plugged else "Discharging"
            except:
                pass
                
        return status

    def get_full_report(self) -> str:
        """ Formats a full hardware report for Telegram. """
        up = self.get_uptime_str()
        mem = self.get_memory_stats()
        hw = self.get_hardware_status()
        
        report = f"💻 *SYSTEM STATUS (TERMUX)*\n"
        report += f"⏱ *Uptime:* {up}\n"
        report += f"🧠 *App RAM:* {mem['process_mb']} MB\n"
        report += f"📊 *Free RAM:* {mem['free_gb']} / {mem['total_gb']} GB\n"
        report += f"🔥 *CPU:* {hw['cpu_pct']}%\n"
        report += f"🔋 *Battery:* {hw['battery_pct']} ({hw['battery_status']})\n"
        if hw['temp'] != "N/A":
            report += f"🌡 *Temp:* {hw['temp']}\n"
            
        return report
