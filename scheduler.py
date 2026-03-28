import schedule
import time
import argparse
from datetime import datetime, timedelta
from utils.config import ConfigLoader
from utils.logger import JsonLogger
from orchestrator.orchestrator import PipelineOrchestrator
import gc

class TradingScheduler:
    """
    Automates the trading pipeline using the 'schedule' library.
    Supports fixed weekday execution and immediate manual triggers.
    """

    def __init__(self):
        self.logger = JsonLogger(log_file="logs/scheduler.log")
        self.config_loader = ConfigLoader()
        self.orchestrator = PipelineOrchestrator()

    def run_scan(self, pipeline: str = "daily"):
        """ Executes the heavy scanning/research part of the pipeline. """
        self.logger.info(f"Scheduler: Initializing [{pipeline}] scan at market close...")
        try:
            days_map = {"daily": 60, "weekly": 180, "monthly": 730}
            days = days_map.get(pipeline.lower(), 365)
            
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Run without immediate alert (send_alert=False)
            self.orchestrator.run_full_pipeline(
                tickers=None,
                start_date=start_date,
                end_date=end_date,
                pipeline=pipeline,
                send_alert=False
            )
            self.logger.info(f"Scheduler: [{pipeline}] scan complete. Signals persisted.")
            gc.collect() # Clear memory after heavy scan
        except Exception as e:
            self.logger.error(f"Scheduler: Scan failure for [{pipeline}]", error=str(e))

    def broadcast_report(self, pipeline: str = "daily"):
        """ Sends the previously saved signal report. """
        self.logger.info(f"Scheduler: Sending [{pipeline}] pre-market report...")
        try:
            self.orchestrator.broadcast_saved_signals(pipeline)
            self.logger.info(f"Scheduler: [{pipeline}] report sent successfully.")
        except Exception as e:
            self.logger.error(f"Scheduler: Report failure for [{pipeline}]", error=str(e))

    def broadcast_portfolio(self, pipeline: str = "daily"):
        """ Sends the End-of-Day Portfolio Report. """
        self.logger.info(f"Scheduler: Sending [{pipeline}] EOD Portfolio Report...")
        try:
            self.orchestrator.broadcast_portfolio_status(pipeline)
            self.logger.info(f"Scheduler: [{pipeline}] portfolio report sent successfully.")
        except Exception as e:
            self.logger.error(f"Scheduler: Portfolio report failure for [{pipeline}]", error=str(e))

    def setup_schedule(self):
        """ Registers staggered scan (16:00) and alert (08:30) tasks. """
        self.logger.info("Scheduler: Setting up decoupled scan/alert schedule...")
        
        # --- DAILY (Mon-Fri) ---
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            # A. Morning Alerts (08:30)
            getattr(schedule.every(), day).at("08:30").do(self.broadcast_report, pipeline="daily")
            # B. EOD Portfolio (15:55)
            getattr(schedule.every(), day).at("15:55").do(self.broadcast_portfolio, pipeline="daily")
            # C. Session-Close Scans (16:00)
            getattr(schedule.every(), day).at("16:00").do(self.run_scan, pipeline="daily")
        
        # --- WEEKLY (Friday/Monday) ---
        # A. Friday EOD Portfolio
        schedule.every().friday.at("15:55").do(self.broadcast_portfolio, pipeline="weekly")
        # B. Friday Close Scan
        schedule.every().friday.at("16:15").do(self.run_scan, pipeline="weekly")
        # C. Monday Morning Alert
        schedule.every().monday.at("08:30").do(self.broadcast_report, pipeline="weekly")
        
        # --- MONTHLY ---
        # A. Last Day Check for Portfolio & Scan
        schedule.every().day.at("15:55").do(self._monthly_portfolio_check)
        schedule.every().day.at("16:30").do(self._monthly_scan_check)
        # B. 1st Day Check for Alert
        schedule.every().day.at("08:30").do(self._monthly_alert_check)
        
        self.logger.info("Scheduler: Schedule registration complete.")

    def _monthly_scan_check(self):
        """ Runs scan at end of month. """
        from calendar import monthrange
        now = datetime.now()
        last_day = monthrange(now.year, now.month)[1]
        if now.day == last_day:
            self.run_scan(pipeline="monthly")

    def _monthly_alert_check(self):
        """ Runs alert on 1st of month. """
        if datetime.now().day == 1:
            self.broadcast_report(pipeline="monthly")

    def _monthly_portfolio_check(self):
        """ Runs portfolio report on last day of month. """
        from calendar import monthrange
        now = datetime.now()
        last_day = monthrange(now.year, now.month)[1]
        if now.day == last_day:
            self.broadcast_portfolio(pipeline="monthly")

    def start_loop(self):
        """ Enters the infinite scheduler loop. """
        self.setup_schedule()
        self.logger.info("Scheduler: Heartbeat started. Monitoring tasks...")
        
        try:
            while True:
                try:
                    schedule.run_pending()
                except Exception as e:
                    self.logger.error("Scheduler: Critical loop error, attempting to continue...", error=str(e))
                
                time.sleep(60) # Only check every minute to save resources
        except KeyboardInterrupt:
            self.logger.info("Scheduler: Shutdown requested by user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Glu-Stock Trading Scheduler")
    parser.add_argument("--scan", type=str, help="Manually run scan for: daily, weekly, monthly")
    parser.add_argument("--report", type=str, help="Manually send signal report for: daily, weekly, monthly")
    parser.add_argument("--portfolio", type=str, help="Manually send portfolio report for: daily, weekly, monthly")
    parser.add_argument("--loop", action="store_true", help="Start the background scheduler loop")
    
    args = parser.parse_args()
    
    ts = TradingScheduler()
    
    if args.scan:
        ts.run_scan(pipeline=args.scan)
    elif args.report:
        ts.broadcast_report(pipeline=args.report)
    elif args.portfolio:
        ts.broadcast_portfolio(pipeline=args.portfolio)
    elif args.loop:
        ts.start_loop()
    else:
        parser.print_help()
