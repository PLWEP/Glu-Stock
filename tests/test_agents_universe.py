import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from agents.agents import UniverseSelectionAgent, ResearchAgent

class TestUniverseSelectionAgent(unittest.TestCase):
    def setUp(self):
        # Mock ResearchAgent
        self.mock_research_agent = MagicMock(spec=ResearchAgent)
        self.agent = UniverseSelectionAgent(research_agent=self.mock_research_agent)

    def test_select_universe_orchestration(self):
        # 1. Setup metadata mock
        dummy_metadata = pd.DataFrame([
            ["A.JK", "Alpha", "Industrials", False],
            ["B.JK", "Beta", "Financials", False], # Bank
            ["C.JK", "Gamma", "Technology", True],   # BUMN
            ["D.JK", "Delta", "Energy", False],
        ], columns=["ticker", "name", "sector", "is_bumn"])
        
        self.agent.universe_manager.get_idx_tickers = MagicMock(return_value=dummy_metadata)
        
        # 2. Setup research mock output
        # Filtered should be A and D
        dates = pd.date_range("2024-01-01", periods=30)
        
        # A: Strong uptrend
        data_a = pd.DataFrame({
            "Close": [100 + i for i in range(30)], 
            "Volume": [1000] * 30,
            "ticker": "A.JK"
        }, index=dates)
        
        # D: Flat
        data_d = pd.DataFrame({
            "Close": [100] * 30,
            "Volume": [100] * 30,
            "ticker": "D.JK"
        }, index=dates)
        
        researched_df = pd.concat([data_a, data_d])
        researched_df.index.name = "date"
        researched_df = researched_df.reset_index().set_index(["date", "ticker"]).rename(columns={"Close": "close", "Volume": "Volume"}) # Matching data schema
        
        # Actually ResearchAgent research() returns 'close' (lowercase) usually, 
        # but UniverseManager looks for 'Volume' and 'Close' (Uppercase) based on implementation?
        # Let's check universe.py again. It uses data["Volume"] and data["Close"].
        researched_df = researched_df.rename(columns={"close": "Close"})
        
        self.mock_research_agent.research.return_value = researched_df

        # 3. Execute
        selected = self.agent.select_universe(max_stocks=1, start_date="2024-01-01", end_date="2024-02-01")

        # 4. Assertions
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0], "A.JK")
        
        # Verify research was called only with A and D
        args = self.mock_research_agent.research.call_args[0][0]
        self.assertIn("A.JK", args)
        self.assertIn("D.JK", args)
        self.assertNotIn("B.JK", args)
        self.assertNotIn("C.JK", args)

if __name__ == "__main__":
    unittest.main()
