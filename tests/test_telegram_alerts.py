import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
from utils.logger import JsonLogger
from execution.execution import ExecutionEngine
from portfolio.portfolio import Portfolio
from orchestrator.orchestrator import PipelineOrchestrator

class TestTelegramAlerts(unittest.TestCase):
    def setUp(self):
        # Ensure enabled in mock config
        self.patcher_config = patch('utils.config.ConfigLoader.get_config')
        self.mock_get_config = self.patcher_config.start()
        self.mock_get_config.return_value = {
            "telegram": {
                "enabled": True,
                "bot_token": "fake_token",
                "chat_id": "12345"
            },
            "debug_mode": False
        }
        
        # Patch requests.post in utils.alerts
        self.patcher_post = patch('utils.alerts.requests.post')
        self.mock_post = self.patcher_post.start()

    def tearDown(self):
        self.patcher_config.stop()
        self.patcher_post.stop()

    def test_logger_error_triggers_telegram(self):
        logger = JsonLogger(log_file="logs/test_alert.log")
        logger.error("Simulation failure", code=500)
        
        # Verify requests.post was called
        self.assertTrue(self.mock_post.called)
        args, kwargs = self.mock_post.call_args
        msg = kwargs['json']['text']
        self.assertIn("ERROR ALERT", msg)
        self.assertIn("Simulation failure", msg)

    @patch('orchestrator.orchestrator.PipelineOrchestrator._generate_final_report')
    @patch('orchestrator.orchestrator.UniverseSelectionAgent.select_universe')
    @patch('orchestrator.orchestrator.ResearchAgent.research')
    @patch('orchestrator.orchestrator.StrategyAgent.get_recommendations')
    @patch('orchestrator.orchestrator.TradingAgent.trade')
    def test_orchestrator_summary_triggers_telegram(self, mock_trade, mock_strat, mock_res, mock_univ, mock_rep):
        orch = PipelineOrchestrator(initial_cash=1000000)
        
        # Mock successful run
        mock_univ.return_value = ["BBCA.JK"]
        # Use ISO dates and MultiIndex
        dates = pd.date_range("2024-03-27", periods=1)
        df_dummy = pd.DataFrame({"close": [10000]}, index=pd.MultiIndex.from_tuples([(dates[0], "BBCA.JK")], names=["date", "ticker"]))
        mock_res.return_value = df_dummy
        mock_strat.return_value = df_dummy
        
        orch.run_full_pipeline(["BBCA.JK"])
        
        # Verify Session Complete alert (TextReportGenerator output check)
        summary_call = False
        for call in self.mock_post.call_args_list:
            # Check for keyword in report output
            text = call[1]['json']['text']
            if "REPORT" in text.upper():
                summary_call = True
                break
        self.assertTrue(summary_call)

if __name__ == "__main__":
    unittest.main()
