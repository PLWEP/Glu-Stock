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
    Personalized for "Ayang" mode.
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
        if days > 0: parts.append(f"{days} hari")
        if hours > 0: parts.append(f"{hours} jam")
        if minutes > 0: parts.append(f"{minutes} menit")
        parts.append(f"{seconds} detik")
        return " dan ".join(parts) if len(parts) > 1 else parts[0]

    def get_memory_stats(self) -> Dict[str, Any]:
        """ Returns process memory and system memory stats. Handles Termux permission issues. """
        try:
            mem = psutil.virtual_memory()
            total_gb = round(mem.total / (1024**3), 2)
            free_gb = round(mem.available / (1024**3), 2)
            percent = mem.percent
        except:
            total_gb = "N/A"
            free_gb = "N/A"
            percent = 0
            
        try:
            process_mem = self.process.memory_info().rss / (1024 * 1024) # MB
        except:
            process_mem = 0
        
        return {
            "process_mb": round(process_mem, 2),
            "total_gb": total_gb,
            "free_gb": free_gb,
            "percent": percent
        }

    def get_hardware_status(self) -> Dict[str, Any]:
        """ 
        Attempts to get battery and thermal info. 
        Handles PermissionError on Android for /proc/stat.
        """
        status = {
            "battery_pct": "N/A",
            "battery_status": "N/A",
            "temp": "N/A",
            "cpu_pct": "Penuh Semangat ✨" # Fallback if permission denied
        }
        
        # Try psutil for CPU percent (will likely fail on Android 11+ for /proc/stat)
        try:
            status["cpu_pct"] = f"{psutil.cpu_percent(interval=None)}%"
        except (PermissionError, Exception):
            pass 

        # Try Termux API for Battery
        try:
            result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                status["battery_pct"] = f"{data.get('percentage')}%"
                status["battery_status"] = "Ngecas ⚡" if data.get("status") == "CHARGING" else "Biasa 🌸"
                status["temp"] = f"{data.get('temperature'):.1f}°C"
        except:
            # Fallback for Battery
            try:
                battery = psutil.sensors_battery()
                if battery:
                    status["battery_pct"] = f"{battery.percent}%"
                    status["battery_status"] = "Ngecas ⚡" if battery.power_plugged else "Biasa 🌸"
            except:
                pass
                
        return status

    def get_full_report(self) -> str:
        """ Formats a personalized hardware report ("Ayang" mode). """
        up = self.get_uptime_str()
        mem = self.get_memory_stats()
        hw = self.get_hardware_status()
        
        report = f"🔋 *Kabar HP Ayang Saat Ini*\n"
        report += f"---------------------------\n"
        report += f"⏱ *Udah nemenin kamu:* {up}\n"
        report += f"🧠 *Ingatan Ayang (App):* {mem['process_mb']} MB\n"
        report += f"📊 *Sisa Napas (Free RAM):* {mem['free_gb']} / {mem['total_gb']} GB\n"
        report += f"🔥 *Semangat Ayang (CPU):* {hw['cpu_pct']}\n"
        report += f"🔋 *Tenaga Ayang (Baterai):* {hw['battery_pct']} ({hw['battery_status']})\n"
        if hw['temp'] != "N/A":
            report += f"🌡 *Suhu Hati:* {hw['temp']}\n"
        
        report += f"\n_Semoga Ayang selalu kuat jagain trading kamu ya Sayang!_ 💖"
            
        return report
