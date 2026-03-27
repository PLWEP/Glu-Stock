import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from orchestrator.orchestrator import PipelineOrchestrator

class TestOrchestratorEnforcement(unittest.TestCase):
    
    def setUp(self):
        self.orch = PipelineOrchestrator()

    @patch('agents.agents.UniverseSelectionAgent.select_universe')
    @patch('orchestrator.orchestrator.PipelineOrchestrator._generate_final_report')
    @patch('orchestrator.orchestrator.PipelineOrchestrator._send_telegram_summary')
    def test_empty_universe_enforcement(self, mock_tel, mock_html, mock_universe):
        # Mock empty universe
        mock_universe.return_value = []
        
        self.orch.run_full_pipeline(tickers=None)
        
        # Verify reporting agents were STILL called
        mock_html.assert_called()
        mock_tel.assert_called()

    @patch('utils.text_report.TextReportGenerator.generate_daily_report')
    @patch('orchestrator.orchestrator.send_telegram_alert')
    def test_report_fallback_logic(self, mock_alert, mock_gen):
        # Case 1: Empty report
        mock_gen.return_value = ""
        self.orch._send_telegram_summary({})
        mock_alert.assert_called_with("⚠️ WARNING: Report empty")
        
        # Case 2: Exception during generation
        mock_gen.side_effect = Exception("Crash")
        self.orch._send_telegram_summary({})
        self.assertIn("Failed to generate report", mock_alert.call_args[0][0])

    @patch('agents.agents.ResearchAgent.research')
    @patch('agents.agents.StrategyAgent.get_recommendations')
    @patch('agents.agents.TradingAgent.trade')
    def test_telemetry_tracking(self, mock_trade, mock_strat, mock_research):
        # Mocking a successful candidate and trade
        dates = [pd.Timestamp("2024-01-01")]
        tickers = ["AAPL"]
        index = pd.MultiIndex.from_product([dates, tickers], names=['date', 'ticker'])
        mock_research.return_value = pd.DataFrame({'close': [100]}, index=index)
        mock_strat.return_value = pd.DataFrame({'final_signal': [1], 'close': [100]}, index=index)
        
        # Capture stdout for telemetry check
        with patch('sys.stdout', new=MagicMock()) as mock_stdout:
            self.orch.run_full_pipeline(tickers=["AAPL"])
            
            # Verify telemetry output structure
            # Join all calls to write() to get the full output
            output_str = "".join([call.args[0] for call in mock_stdout.write.call_args_list])
            self.assertIn("Scanned 1 tickers", output_str)
            self.assertIn("Found 1 candidates", output_str)
            self.assertIn("Processed 1 execution attempts", output_str)

if __name__ == "__main__":
    unittest.main()
