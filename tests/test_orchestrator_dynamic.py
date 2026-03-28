import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from orchestrator.orchestrator import PipelineOrchestrator

class TestPipelineOrchestratorDynamic(unittest.TestCase):
    def setUp(self):
        # We need to mock agents to avoid real IO/Data fetching
        with patch('orchestrator.orchestrator.ResearchAgent'), \
             patch('orchestrator.orchestrator.StrategyAgent'), \
             patch('orchestrator.orchestrator.TradingAgent'), \
             patch('orchestrator.orchestrator.UniverseSelectionAgent'), \
             patch('orchestrator.orchestrator.ReportGenerator'), \
             patch('utils.config.ConfigLoader.get_config') as mock_conf:
            
            mock_conf.return_value = {"debug_mode": False}
            self.orch = PipelineOrchestrator()
            self.orch._generate_final_report = MagicMock()
            self.orch._send_telegram_summary = MagicMock()

    def test_dynamic_selection_triggered(self):
        # Setup: tickers=None
        self.orch.universe_agent.select_universe.return_value = ["DYNAMIC.JK"]
        self.orch.research_agent.research.return_value = pd.DataFrame()
        
        # Test
        self.orch.run_full_pipeline(tickers=None, start_date="2024-01-01", end_date="2024-02-01")
        
        # Verify
        self.orch.universe_agent.select_universe.assert_called_with(5, "2024-01-01", "2024-02-01")

    def test_manual_override_respected(self):
        # Setup: tickers provided
        self.orch.research_agent.research.return_value = pd.DataFrame()
        
        # Test
        self.orch.run_full_pipeline(tickers=["MANUAL.JK"], start_date="2024-01-01", end_date="2024-02-01")
        
        # Verify
        self.orch.universe_agent.select_universe.assert_not_called()
        self.orch.research_agent.research.assert_any_call(["MANUAL.JK"], "2024-01-01", "2024-02-01")

    def test_empty_universe_handling(self):
        # Setup: select_universe returns empty list
        self.orch.universe_agent.select_universe.return_value = []
        
        # Test
        result = self.orch.run_full_pipeline(tickers=None)
        
        # Verify: Instead of error dict, it returns a consolidated summary dict (Institutional Policy)
        self.assertIsInstance(result, dict)
        self.assertIn("tickers_processed", result)
        self.assertEqual(len(result["tickers_processed"]), 0)

if __name__ == "__main__":
    unittest.main()
