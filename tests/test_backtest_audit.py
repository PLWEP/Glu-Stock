import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from orchestrator.orchestrator import PipelineOrchestrator

class TestBacktestValidation(unittest.TestCase):
    
    @patch('orchestrator.orchestrator.send_telegram_alert')
    @patch('agents.agents.ResearchAgent.research')
    def test_audit_pass_fail_flow(self, mock_research, mock_alert):
        orch = PipelineOrchestrator()
        
        # 1. MOCK DATA
        dates = pd.date_range("2024-01-01", periods=101)
        
        # GOOD: Steady Upward
        df_a = pd.DataFrame({
            'open': [100.0]*101, 'high': [110.0]*101, 'low': [90.0]*101,
            'close': [100.0 + i for i in range(101)], 
            'volume': [1000]*101
        }, index=pd.MultiIndex.from_tuples([(d, 'GOOD.JK') for d in dates], names=['date', 'ticker']))
        
        # BAD: Steady Downward
        df_b = pd.DataFrame({
            'open': [100.0]*101, 'high': [110.0]*101, 'low': [90.0]*101,
            'close': [100.0 - (i*10) for i in range(101)], # Sharp decline
            'volume': [1000]*101
        }, index=pd.MultiIndex.from_tuples([(d, 'BAD.JK') for d in dates], names=['date', 'ticker']))
        
        mock_research.side_effect = [df_a, df_b]
        
        with patch('strategies.daily.DailyStrategy.generate_signals') as mock_gen:
            def mock_side_effect(df):
                # 1 on even indices, 0 on odd. i=100 is even -> 1.
                df['final_signal'] = [1 if i % 2 == 0 else 0 for i in range(len(df))]
                return df
            mock_gen.side_effect = mock_side_effect
            
            # Run
            orch.run_full_pipeline(tickers=["GOOD.JK", "BAD.JK"], pipeline="daily", send_alert=True)
            
            # Verify
            candidates = [c['ticker'] for c in orch.results["candidates"]]
            print(f"DEBUG: Final Candidates: {candidates}")
            self.assertIn("GOOD.JK", candidates)
            self.assertNotIn("BAD.JK", candidates)
            
            # Verify Alert
            report = mock_alert.call_args[0][0]
            self.assertIn("🛡️ *Audit:* PASS", report)
            self.assertIn("GOOD.JK", report)

if __name__ == '__main__':
    unittest.main()
