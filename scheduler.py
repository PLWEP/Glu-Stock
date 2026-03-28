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

    def run_pipeline(self):
        """ Executes the full trading pipeline for configured tickers. """
        self.logger.info("Scheduler: Initializing pipeline execution...")
        try:
            # Reload config to ensure we have latest tickers/capital
            self.config_loader = ConfigLoader()
            params = self.config_loader.get_trading_params()
            
            # Run orchestrator with dynamic 1-year lookback
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            
            summary = self.orchestrator.run_full_pipeline(
                tickers=params["tickers"],
                start_date=start_date,
                end_date=end_date
            )
            
            self.logger.info("Scheduler: Pipeline executed successfully", 
                             tickers_processed=len(summary.get("tickers_processed", [])),
                             failures=len(summary.get("failures", [])))
            
        except Exception as e:
            self.logger.error("Scheduler: Critical failure during pipeline execution", error=str(e))

    def setup_schedule(self):
        """ Registers 09:00 weekday tasks. """
        self.logger.info("Scheduler: Setting up weekday 09:00 schedule...")
        
        schedule.every().monday.at("09:00").do(self.run_pipeline)
        schedule.every().tuesday.at("09:00").do(self.run_pipeline)
        schedule.every().wednesday.at("09:00").do(self.run_pipeline)
        schedule.every().thursday.at("09:00").do(self.run_pipeline)
        schedule.every().friday.at("09:00").do(self.run_pipeline)
        
        self.logger.info("Scheduler: Schedule registration complete.")

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
        ts.run_pipeline()
    elif args.loop:
        ts.start_loop()
    else:
        parser.print_help()
