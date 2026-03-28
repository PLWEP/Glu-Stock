import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from orchestrator.orchestrator import PipelineOrchestrator

class TestOrchestratorEnforcement(unittest.TestCase):
    
    def setUp(self):
        # Patch Config to avoid real yaml loading
        with patch('utils.config.ConfigLoader.get_config') as mock_conf:
            mock_conf.return_value = {"debug_mode": False}
            self.orch = PipelineOrchestrator()

    @patch('agents.agents.UniverseSelectionAgent.select_universe')
    @patch('orchestrator.orchestrator.PipelineOrchestrator._generate_final_report')
    @patch('orchestrator.orchestrator.PipelineOrchestrator._send_telegram_summary')
    def test_empty_universe_enforcement(self, mock_tel, mock_html, mock_universe):
        # Mock empty universe
        mock_universe.return_value = []
        
        self.orch.run_full_pipeline(tickers=None)
        
        # Verify reporting agents were STILL called (Institutional Enforcement)
        mock_html.assert_called()
        mock_tel.assert_called()

    @patch('orchestrator.orchestrator.JsonLogger')
    @patch('agents.agents.ResearchAgent.research')
    @patch('agents.agents.StrategyAgent.get_recommendations')
    @patch('agents.agents.TradingAgent.trade')
    def test_telemetry_tracking_via_logger(self, mock_trade, mock_strat, mock_research, mock_logger_class):
        # Setup mock logger instance
        mock_logger = mock_logger_class.return_value
        
        # Mocking a successful candidate and trade
        dates = [pd.Timestamp("2024-01-01")]
        tickers = ["AAPL"]
        index = pd.MultiIndex.from_product([dates, tickers], names=['date', 'ticker'])
        mock_research.return_value = pd.DataFrame({'close': [150]}, index=index)
        mock_strat.return_value = pd.DataFrame({'final_signal': [1], 'close': [100]}, index=index)
        
        # Inject the mock logger into the orch instance
        self.orch.logger = mock_logger
        
        self.orch.run_full_pipeline(tickers=["AAPL"])
        
        # Verify logger.info was called with correct telemetry segments
        # Instead of searching sys.stdout, we verify structured logs
        calls = [c.args[0] for c in mock_logger.info.call_args_list]
        self.assertTrue(any("Scanned 1 tickers" in s for s in calls))
        self.assertTrue(any("Found 1 candidates" in s for s in calls))
        self.assertTrue(any("Processed 1 execution attempts" in s for s in calls))

if __name__ == "__main__":
    unittest.main()
