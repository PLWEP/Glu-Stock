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
    Provides raw data for system monitoring.
    """
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()

    def get_uptime_seconds(self) -> int:
        """ Returns process uptime in seconds. """
        return int(time.time() - self.start_time)

    def get_memory_stats(self) -> Dict[str, Any]:
        """ Returns process memory and system memory stats. Handles Termux permission issues. """
        try:
            mem = psutil.virtual_memory()
            total_gb = round(mem.total / (1024**3), 2)
            available_gb = round(mem.available / (1024**3), 2)
            percent = mem.percent
        except:
            total_gb = 0
            available_gb = 0
            percent = 0
            
        try:
            process_mb = self.process.memory_info().rss / (1024 * 1024) # MB
        except:
            process_mb = 0
        
        return {
            "process_mb": round(process_mb, 2),
            "total_gb": total_gb,
            "available_gb": available_gb,
            "percent": percent
        }

    def get_hardware_status(self) -> Dict[str, Any]:
        """ 
        Attempts to get battery and thermal info via Termux API or psutil. 
        """
        status = {
            "battery_pct": 0,
            "battery_status": "Unknown",
            "temperature": None,
            "cpu_percent": 0
        }
        
        # CPU Usage (Handles /proc/stat permission errors on Android)
        try:
            status["cpu_percent"] = psutil.cpu_percent(interval=None)
        except:
            pass 

        # Battery & Temp via Termux API
        try:
            result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                status["battery_pct"] = data.get('percentage', 0)
                status["battery_status"] = data.get("status", "Unknown")
                status["temperature"] = data.get('temperature')
        except:
            # Fallback for Battery
            try:
                battery = psutil.sensors_battery()
                if battery:
                    status["battery_pct"] = battery.percent
                    status["battery_status"] = "Charging" if battery.power_plugged else "Discharging"
            except:
                pass
                
        return status

    def get_raw_data(self) -> Dict[str, Any]:
        """ Returns a consolidated dictionary of all system metrics. """
        return {
            "uptime_seconds": self.get_uptime_seconds(),
            "memory": self.get_memory_stats(),
            "hardware": self.get_hardware_status(),
            "timestamp": datetime.now().isoformat()
        }
