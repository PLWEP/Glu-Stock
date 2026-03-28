import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from agents.agents import ResearchAgent, StrategyAgent, TradingAgent, UniverseSelectionAgent

class TestAgentsPipelines(unittest.TestCase):
    def setUp(self):
        self.ra = ResearchAgent()
        self.sa = StrategyAgent()
        self.usa = UniverseSelectionAgent(research_agent=self.ra)

    def test_strategy_agent_pipeline_dispatch(self):
        # Create dummy data (100 periods to satisfy Daily/Weekly/Monthly lookbacks)
        dates = pd.date_range("2024-01-01", periods=100)
        df = pd.DataFrame({
            'close': [100 + i for i in range(100)],
            'high': [105 + i for i in range(100)],
            'low': [95 + i for i in range(100)],
            'volume': [1000] * 100
        }, index=pd.MultiIndex.from_tuples([(d, 'AAPL') for d in dates], names=['date', 'ticker']))
        
        # Test Daily
        res_daily = self.sa.get_recommendations(df, pipeline="daily")
        self.assertIn('vwap', res_daily.columns)
        
        # Test Weekly
        res_weekly = self.sa.get_recommendations(df, pipeline="weekly")
        self.assertIn('ema21', res_weekly.columns)

if __name__ == "__main__":
    unittest.main()
