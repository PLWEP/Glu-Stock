import unittest
import pandas as pd
from agents.agents import ResearchAgent, StrategyAgent, TradingAgent
from portfolio.portfolio import Portfolio

class TestAgents(unittest.TestCase):
    def setUp(self):
        self.ra = ResearchAgent()
        self.sa = StrategyAgent()
        self.ta = TradingAgent(initial_cash=10000.0)

    def test_end_to_end_workflow(self):
        # 1. Research (Mocking network call by passing direct ticker if needed, but here we test the class orchestration)
        # Note: Testing with a real ticker might fail if no internet, but StockDataHandler uses yfinance.
        # We'll use a mocked scenario or assume integration works if data/ is tested.
        # For agent-level test, let's verify method presence and basic data flow.
        
        # Create dummy data that looks like ResearchAgent output
        dates = pd.date_range("2024-01-01", periods=10)
        df = pd.DataFrame({
            'close': [150 + i for i in range(10)],
            'rsi': [30 + i for i in range(10)],
            'macd_diff': [0.1] * 10,
            'macd_signal': [0.05] * 10,
            'sma_20': [145 + i for i in range(10)],
            'volume': [1000] * 10
        }, index=pd.MultiIndex.from_tuples([(d, 'AAPL') for d in dates], names=['date', 'ticker']))
        
        # 2. Strategy Agent
        signals = self.sa.get_recommendations(df)
        self.assertIn('final_signal', signals.columns)
        
        # 3. Strategy Validation
        metrics = self.sa.validate_strategy(signals)
        self.assertIn('sharpe_ratio', metrics)
        
        # 4. Trading Agent
        # Mock signal to trigger a buy
        signals.loc[(dates[0], 'AAPL'), 'final_signal'] = 1
        self.ta.trade(signals.iloc[:1], shares_per_trade=10)
        
        status = self.ta.get_status({"AAPL": 150})
        self.assertEqual(status["cash"], 8500.0)
        self.assertEqual(status["positions"]["AAPL"]["shares"], 10)

if __name__ == "__main__":
    unittest.main()
