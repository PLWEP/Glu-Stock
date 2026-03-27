from scheduler import TradingScheduler

if __name__ == "__main__":
    """ 
    Institutional Entry Point:
    Executes a single iteration of the curated trading universe cycle.
    Designed for PM2 cron-based orchestration.
    """
    ts = TradingScheduler()
    ts.run_pipeline()
