import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import json
import os
from orchestrator.orchestrator import PipelineOrchestrator
from scheduler import TradingScheduler

class TestAsynchronousFlow(unittest.TestCase):
    def setUp(self):
        if os.path.exists("data/pending_signals_test.json"):
            os.remove("data/pending_signals_test.json")
            
    @patch('data.data.StockDataHandler.fetch_data')
    @patch('orchestrator.orchestrator.send_telegram_alert')
    def test_decoupled_scan_and_report(self, mock_alert, mock_fetch):
        # 1. Setup Orchestrator with test persistence
        from utils.persistence import SignalPersistence
        test_persistence = SignalPersistence("data/pending_signals_test.json")
        orch = PipelineOrchestrator()
        orch.persistence = test_persistence
        
        # 2. Mock Data for Scan
        dates = pd.date_range("2024-01-01", periods=100)
        index = pd.MultiIndex.from_tuples([(d, 'BBCA.JK') for d in dates], names=['date', 'ticker'])
        df = pd.DataFrame({
            'open': [100.0]*100, 'high': [110.0]*100, 'low': [90.0]*100,
            'close': [100.0]*99 + [108.0], 'volume': [1000]*100
        }, index=index)
        mock_fetch.return_value = df
        
        # 3. PHASE A: 16:00 Scan (Silent, no alert)
        orch.run_full_pipeline(tickers=["BBCA.JK"], pipeline="daily", send_alert=False)
        
        # Verify persistence
        self.assertFalse(mock_alert.called, "Alert should NOT be sent during scan")
        self.assertTrue(os.path.exists("data/pending_signals_test.json"))
        with open("data/pending_signals_test.json", "r") as f:
            saved = json.load(f)
            self.assertIn("daily", saved)
            self.assertEqual(len(saved["daily"]["candidates"]), 1)
            self.assertEqual(saved["daily"]["candidates"][0]["ticker"], "BBCA.JK")

        # 4. PHASE B: 08:30 Report (Broadcast saved signals)
        orch.broadcast_saved_signals("daily")
        
        # Verify alert
        self.assertTrue(mock_alert.called, "Alert should be sent during broadcast")
        report = mock_alert.call_args[0][0]
        self.assertIn("ANALYSIS (DAILY)", report)
        self.assertIn("BBCA.JK", report)
        self.assertIn("Total saham yang lolos filter: 1", report)

    def tearDown(self):
        if os.path.exists("data/pending_signals_test.json"):
            os.remove("data/pending_signals_test.json")

if __name__ == '__main__':
    unittest.main()
