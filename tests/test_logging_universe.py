import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import json
import os
from agents.agents import UniverseSelectionAgent, ResearchAgent

class TestLoggingUniverse(unittest.TestCase):
    def setUp(self):
        self.log_file = "logs/test_universe_selection.log"
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        
        # Mock ResearchAgent
        self.mock_research_agent = MagicMock(spec=ResearchAgent)
        self.agent = UniverseSelectionAgent(research_agent=self.mock_research_agent)
        # Override logger to use test log
        from utils.logger import JsonLogger
        self.agent.logger = JsonLogger(log_file=self.log_file)

    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_logging_content(self):
        # 1. Setup mocks
        dummy_metadata = pd.DataFrame([
            ["A.JK", "Alpha", "Industrials", False],
            ["D.JK", "Delta", "Energy", False],
        ], columns=["ticker", "name", "sector", "is_bumn"])
        
        self.agent.universe_manager.get_idx_tickers = MagicMock(return_value=dummy_metadata)
        
        dates = pd.date_range("2024-01-01", periods=30)
        data_a = pd.DataFrame({"Close": [100+i for i in range(30)], "Volume": [1000]*30, "ticker": "A.JK"}, index=dates)
        data_d = pd.DataFrame({"Close": [100]*30, "Volume": [100]*30, "ticker": "D.JK"}, index=dates)
        
        researched_df = pd.concat([data_a, data_d])
        researched_df.index.name = "date"
        researched_df = researched_df.reset_index().set_index(["date", "ticker"]).rename(columns={"Close": "Close", "Volume": "Volume"})
        
        self.mock_research_agent.research.return_value = researched_df

        # 2. Execute
        self.agent.select_universe(max_stocks=1, start_date="2024-01-01", end_date="2024-02-01")

        # 3. Verify Log File
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            log_entry = json.loads(f.readline())
            
        self.assertEqual(log_entry["level"], "INFO")
        self.assertIn("UniverseSelectionAgent: Curated watchlist generated", log_entry["message"])
        self.assertIn("A.JK", log_entry["metadata"]["selected"])
        self.assertIn("A.JK", log_entry["metadata"]["scores"])
        self.assertIn("D.JK", log_entry["metadata"]["scores"])
        # A should have higher score than D
        self.assertGreater(log_entry["metadata"]["scores"]["A.JK"], log_entry["metadata"]["scores"]["D.JK"])

if __name__ == "__main__":
    unittest.main()
