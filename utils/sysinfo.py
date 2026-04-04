import os
import psutil
import time
from datetime import datetime
from typing import Dict, Any, Tuple

class SystemMonitor:
    """
    Utility for tracking hardware health and process resources on PC.
    Includes Hardware-Aware Throttling logic.
    """
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        
        # Hardware Thresholds for Throttling
        self.temp_threshold = 85.0 # Higher for PCs
        self.battery_threshold = 10.0

    def get_memory_stats(self) -> Dict[str, Any]:
        """ Returns process memory and system memory stats. """
        try:
            mem = psutil.virtual_memory()
            total_gb = round(mem.total / (1024**3), 2)
            available_gb = round(mem.available / (1024**3), 2)
            percent = mem.percent
            process_mb = self.process.memory_info().rss / (1024 * 1024)
        except:
            total_gb, available_gb, percent, process_mb = 0, 0, 0, 0
            
        return {
            "process_mb": round(process_mb, 2),
            "total_gb": total_gb,
            "available_gb": available_gb,
            "percent": percent
        }

    def get_hardware_status(self) -> Dict[str, Any]:
        """ Fetches system battery and cpu info via psutil. """
        status = {"battery_pct": 100, "battery_status": "Unknown", "temperature": 0.0, "cpu_percent": 0.0}
        
        try:
            status["cpu_percent"] = psutil.cpu_percent(interval=None)
        except: pass

        try:
            battery = psutil.sensors_battery()
            if battery:
                status["battery_pct"] = battery.percent
                status["battery_status"] = "Charging" if battery.power_plugged else "Discharging"
        except: pass
                
        return status

    def is_safe_to_run(self) -> Tuple[bool, str]:
        """
        Hardware-Aware Throttling check.
        Returns (is_safe, reason).
        """
        hw = self.get_hardware_status()
        
        # 1. Temperature Check (Optional for PC if sensors available)
        if hw["temperature"] > self.temp_threshold and hw["temperature"] > 0:
            return False, f"Temperature too high ({hw['temperature']}°C)"
            
        # 2. Battery Check (if not charging)
        if hw["battery_pct"] < self.battery_threshold and hw["battery_status"] != "Charging":
            return False, f"Battery too low ({hw['battery_pct']}%)"
            
        return True, "Safe"

    def get_status(self) -> Dict[str, Any]:
        """ Aggregates system metrics. """
        hw = self.get_hardware_status()
        mem = self.get_memory_stats()
        return {
            "battery_pct": hw["battery_pct"],
            "battery_status": hw["battery_status"],
            "battery_temp": hw["temperature"],
            "ram_usage": mem["percent"],
            "ram_free_gb": mem["available_gb"],
            "cpu_usage": hw["cpu_percent"],
            "timestamp": datetime.now().isoformat()
        }
