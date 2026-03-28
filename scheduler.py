import schedule
import time
import argparse
from datetime import datetime, timedelta
from utils.config import ConfigLoader
from utils.logger import JsonLogger
from orchestrator.orchestrator import PipelineOrchestrator

class TradingScheduler:
    """
    Automates the trading pipeline using the 'schedule' library.
    Supports fixed weekday execution and immediate manual triggers.
    """

    def __init__(self):
        self.logger = JsonLogger(log_file="logs/scheduler.log")
        self.config_loader = ConfigLoader()
        self.orchestrator = PipelineOrchestrator()

    def run_pipeline(self, pipeline: str = "daily"):
        """ Executes the specific trading pipeline. """
        self.logger.info(f"Scheduler: Initializing [{pipeline}] pipeline execution...")
        try:
            # Reload config
            self.config_loader = ConfigLoader()
            
            # Use appropriate history duration based on pipeline
            days_map = {"daily": 60, "weekly": 180, "monthly": 730}
            days = days_map.get(pipeline.lower(), 365)
            
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            self.orchestrator.run_full_pipeline(
                tickers=None, # Use dynamic universe selection
                start_date=start_date,
                end_date=end_date,
                pipeline=pipeline
            )
            
            self.logger.info(f"Scheduler: [{pipeline}] pipeline executed successfully.")
            
        except Exception as e:
            self.logger.error(f"Scheduler: Critical failure during [{pipeline}] pipeline", error=str(e))

    def setup_schedule(self):
        """ Registers 08:30 staggered tasks for each pipeline. """
        self.logger.info("Scheduler: Setting up 08:30 multi-pipeline schedule...")
        
        # 1. DAILY: Every Trading Day (Mon-Fri) at 08:30
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            getattr(schedule.every(), day).at("08:30").do(self.run_pipeline, pipeline="daily")
        
        # 2. WEEKLY: Every Monday at 08:30
        schedule.every().monday.at("08:30").do(self.run_pipeline, pipeline="weekly")
        
        # 3. MONTHLY: Check on 08:30 daily if it's the 1st of the month
        schedule.every().day.at("08:30").do(self._monthly_check)
        
        self.logger.info("Scheduler: Schedule registration complete.")

    def _monthly_check(self):
        """ Helper to run Monthly pipeline only on the 1st. """
        if datetime.now().day == 1:
            self.run_pipeline(pipeline="monthly")

    def start_loop(self):
        """ Enters the infinite scheduler loop. """
        self.setup_schedule()
        self.logger.info("Scheduler: Heartbeat started. Monitoring tasks...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60) # Only check every minute to save resources
        except KeyboardInterrupt:
            self.logger.info("Scheduler: Shutdown requested by user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Glu-Stock Trading Scheduler")
    parser.add_argument("--now", action="store_true", help="Execute the pipeline immediately")
    parser.add_argument("--loop", action="store_true", help="Start the background scheduler loop")
    
    args = parser.parse_args()
    
    ts = TradingScheduler()
    
    if args.now:
        # Allow specifying pipeline in CLI
        pipeline = "daily"
        ts.run_pipeline(pipeline=pipeline)
    elif args.loop:
        ts.start_loop()
    else:
        parser.print_help()
