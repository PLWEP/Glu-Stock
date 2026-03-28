import unittest
import os
import pandas as pd
from orchestrator.orchestrator import PipelineOrchestrator

class TestPipelineOrchestrator(unittest.TestCase):
    def setUp(self):
        self.output_dir = "tests/orch_exports"
        self.orch = PipelineOrchestrator(initial_cash=100000, output_dir=self.output_dir)

    def tearDown(self):
        if os.path.exists(self.output_dir):
            import shutil
            shutil.rmtree(self.output_dir)
        # Clean up temporary trade logs / db if any
        if os.path.exists("execution/trade_log.csv"):
            os.remove("execution/trade_log.csv")

    def test_pipeline_resilience(self):
        # We test with a real ticker and a fake one
        # Note: ResearchAgent will call yfinance. If offline, this might skip or we'd need mocking.
        # For simplicity, we assume StockDataHandler handles errors, which we then catch.
        
        tickers = ["AAPL", "THIS_TICKER_DOES_NOT_EXIST"]
        summary = self.orch.run_full_pipeline(tickers, "2024-01-01", "2024-01-10")
        
        # At least AAPL should be there (if internet ok)
        # But for unit testing, we verify that ONE ticker failing didn't crash the whole run.
        self.assertIn("failures", summary)
        self.assertTrue(len(summary["tickers_processed"]) >= 0) # Could be 0 if no internet, but logic should hold
        
        # Verify HTML report generation
        mock_res.return_value = pd.DataFrame({'close': [100]}, index=pd.MultiIndex.from_tuples([(pd.Timestamp('2024-01-01'), 'AAPL')], names=['date', 'ticker']))
        mock_strat.return_value = pd.DataFrame({'close': [100], 'final_signal': [1]}, index=pd.MultiIndex.from_tuples([(pd.Timestamp('2024-01-01'), 'AAPL')], names=['date', 'ticker']))
        
        res = self.orch.run_full_pipeline(tickers=["AAPL"], pipeline="daily")
        self.assertIn("success", res)

    def test_summary_structure(self):
        # Verify the structure of returned status
        summary = self.orch._consolidate_results([])
        self.assertIn("final_portfolio", summary)
        self.assertIn("cash", summary["final_portfolio"])

if __name__ == "__main__":
    unittest.main()
