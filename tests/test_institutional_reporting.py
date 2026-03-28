import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime
from orchestrator.orchestrator import PipelineOrchestrator

class TestInstitutionalReporting(unittest.TestCase):
    @patch('data.data.StockDataHandler.fetch_data')
    @patch('orchestrator.orchestrator.send_telegram_alert')
    def test_daily_report_format(self, mock_alert, mock_fetch):
        orch = PipelineOrchestrator()
        dates = pd.date_range("2024-01-01", periods=100)
        index = pd.MultiIndex.from_tuples([(d, 'BBCA.JK') for d in dates], names=['date', 'ticker'])
        df = pd.DataFrame({
            'open': [100.0]*100, 'high': [110.0]*100, 'low': [90.0]*100,
            'close': [100.0]*99 + [108.0], 'volume': [1000]*100
        }, index=index)
        mock_fetch.return_value = df
        
        orch.run_full_pipeline(tickers=["BBCA.JK"], pipeline="daily")
        
        self.assertTrue(mock_alert.called)
        report = mock_alert.call_args[0][0]
        self.assertIn("GLU-STOCK PRE-MARKET ANALYSIS (DAILY)", report)
        self.assertIn("Total saham yang lolos filter: 1", report)

    @patch('data.data.StockDataHandler.fetch_data')
    @patch('orchestrator.orchestrator.send_telegram_alert')
    def test_weekly_report_format(self, mock_alert, mock_fetch):
        # 1. Create Orchestrator
        orch = PipelineOrchestrator()
        
        # 2. Mock Data (Complete OHLCV for indicators)
        dates = pd.date_range("2024-01-01", periods=100)
        index = pd.MultiIndex.from_tuples([(d, 'ASII.JK') for d in dates], names=['date', 'ticker'])
        df = pd.DataFrame({
            'open': [100.0]*100, 'high': [105.0]*100, 'low': [95.0]*100,
            'close': [102.0]*100, 'volume': [1000]*100
        }, index=index)
        mock_fetch.return_value = df
        
        # 3. Direct instance mock for strategy to ensure success
        signal_df = df.copy()
        signal_df['final_signal'] = 0
        signal_df.iloc[-1, signal_df.columns.get_loc('final_signal')] = 1
        signal_df['buy_price'] = 100.0
        signal_df['tp1'] = 103.0
        signal_df['tp2'] = 105.0
        signal_df['sl_level'] = 97.0
        signal_df['signal_duration'] = "1 Week"
        orch.strategy_agent.get_recommendations = MagicMock(return_value=signal_df)
        
        # 4. Run
        orch.run_full_pipeline(tickers=["ASII.JK"], pipeline="weekly")
        
        # 5. Verify
        self.assertTrue(mock_alert.called, "Weekly Telegram alert was not sent")
        report = mock_alert.call_args[0][0]
        self.assertIn("ANALYSIS (WEEKLY)", report)
        self.assertIn("Total saham yang lolos filter: 1", report)
        self.assertIn("Validity: 1 Week", report)

if __name__ == '__main__':
    unittest.main()
