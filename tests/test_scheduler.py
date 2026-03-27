import unittest
from unittest.mock import patch, MagicMock
import schedule
from scheduler import TradingScheduler

class TestTradingScheduler(unittest.TestCase):
    def setUp(self):
        # We mock dependencies to avoid real pipeline execution
        with patch('scheduler.JsonLogger'), patch('scheduler.ConfigLoader'), patch('scheduler.PipelineOrchestrator'):
            self.ts = TradingScheduler()

    def test_schedule_registration(self):
        # Clear existing jobs
        schedule.clear()
        
        self.ts.setup_schedule()
        
        # Check if 5 weekday jobs are registered
        jobs = schedule.get_jobs()
        self.assertEqual(len(jobs), 5)
        
        # Verify they are all scheduled for 09:00
        for job in jobs:
            self.assertEqual(job.at_time.strftime("%H:%M"), "09:00")

    def test_run_pipeline_orchestration(self):
        # Configure the mock config loader to return valid params
        self.ts.config_loader.get_trading_params.return_value = {"tickers": ["AAPL"]}
        
        # Verify that run_pipeline calls the orchestrator
        with patch.object(self.ts.orchestrator, 'run_full_pipeline', return_value={"success": ["AAPL"]}) as mock_run:
            self.ts.run_pipeline()
            mock_run.assert_called_once()

if __name__ == "__main__":
    unittest.main()
