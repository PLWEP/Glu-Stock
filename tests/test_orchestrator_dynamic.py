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
             patch('orchestrator.orchestrator.ReportGenerator'):
            self.orch = PipelineOrchestrator()
            self.orch._generate_final_report = MagicMock()

    def test_dynamic_selection_triggered(self):
        # Setup: tickers=None
        self.orch.universe_agent.select_universe.return_value = ["DYNAMIC.JK"]
        self.orch.research_agent.research.return_value = pd.DataFrame()
        
        # Test
        self.orch.run_full_pipeline(tickers=None, start_date="2024-01-01", end_date="2024-02-01")
        
        # Verify
        self.orch.universe_agent.select_universe.assert_called_once()
        self.orch.research_agent.research.assert_called_with(["DYNAMIC.JK"], "2024-01-01", "2024-02-01")

    def test_manual_override_respected(self):
        # Setup: tickers provided
        self.orch.research_agent.research.return_value = pd.DataFrame()
        
        # Test
        self.orch.run_full_pipeline(tickers=["MANUAL.JK"], start_date="2024-01-01", end_date="2024-02-01")
        
        # Verify
        self.orch.universe_agent.select_universe.assert_not_called()
        self.orch.research_agent.research.assert_called_with(["MANUAL.JK"], "2024-01-01", "2024-02-01")

    def test_empty_universe_handling(self):
        # Setup: select_universe returns empty list
        self.orch.universe_agent.select_universe.return_value = []
        
        # Test
        result = self.orch.run_full_pipeline(tickers=None)
        
        # Verify
        self.assertEqual(result, {"error": "Empty universe"})

if __name__ == "__main__":
    unittest.main()
