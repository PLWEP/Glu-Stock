import unittest
import pandas as pd
import os
from reporting.report import ReportGenerator

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.output_dir = "tests/reporting_exports"
        self.rg = ReportGenerator(output_dir=self.output_dir)
        self.report_path = os.path.join(self.output_dir, "test_report.html")

    def tearDown(self):
        # Cleanup
        if os.path.exists(self.report_path):
            os.remove(self.report_path)
        if os.path.exists(self.output_dir):
            import shutil
            shutil.rmtree(self.output_dir)

    def test_html_report_generation(self):
        dummy_equity = pd.Series([100, 110, 105, 120, 115, 130])
        dummy_metrics = {"Total_Return": "30%", "Sharpe_Ratio": "1.8", "Max_Drawdown": "5%"}
        dummy_trades = pd.DataFrame({
            "timestamp": ["2024-01-01", "2024-01-02"],
            "ticker": ["AAPL", "TSLA"],
            "action": ["BUY", "SELL"],
            "status": ["SUCCESS", "SUCCESS"]
        })
        
        # Act
        self.rg.generate_html_report(dummy_metrics, dummy_trades, dummy_equity, filename="test_report.html")
        
        # Assert
        self.assertTrue(os.path.exists(self.report_path))
        with open(self.report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("GLU-STOCK TRADING REPORT", content)
            self.assertIn("Sharpe Ratio", content)
            self.assertIn("AAPL", content)
            self.assertIn("data:image/png;base64,", content) # Verify plot embedding

if __name__ == "__main__":
    unittest.main()
