import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from telegram_bot import TelegramBot

class TestTelegramLogic(unittest.TestCase):
    @patch('telegram_bot.ConfigLoader')
    @patch('telegram_bot.TradingDatabase')
    @patch('utils.text_report.TradingDatabase')
    def setUp(self, mock_db_report, mock_db_bot, mock_config):
        # Mock Config
        self.mock_config = mock_config.return_value
        self.mock_config.get_config.return_value = {
            "telegram": {
                "enabled": True,
                "bot_token": "fake_token",
                "chat_id": "12345"
            }
        }
        # Both modules should use the same mock DB instance
        self.mock_db = mock_db_report.return_value
        mock_db_bot.return_value = self.mock_db
        
        self.bot = TelegramBot()
        self.bot.send_message = MagicMock() # Don't actually send

    def test_handle_status_formatting(self):
        with patch('os.path.exists', return_value=False): # No log file
            self.bot.handle_status()
            args, _ = self.bot.send_message.call_args
            msg = args[0]
            self.assertIn("Glu-Stock Engine Status", msg)
            self.assertIn("System: Online", msg)

    def test_handle_portfolio_formatting(self):
        # Setup dummy data with ISO dates
        now = datetime.now().isoformat()
        self.mock_db.get_portfolio_history.return_value = [
            {"date": now, "equity": 1000000.0, "cash": 900000.0, "positions_value": 100000.0}
        ]
        self.mock_db.get_all_trades.return_value = [
            {"entry_date": now, "status": "OPEN", "ticker": "BBCA.JK", "pnl": 0.0}
        ]
        
        self.bot.handle_portfolio()
        args, _ = self.bot.send_message.call_args
        msg = args[0]
        
        self.assertIn("DAILY REPORT", msg)
        self.assertIn("Portfolio Value: IDR 1,000,000.00", msg)
        self.assertIn("BBCA.JK", msg)

    @patch('requests.get')
    def test_polling_command_parsing(self, mock_get):
        # 1. Mock response with /status command
        mock_get.return_value.json.return_value = {
            "ok": True,
            "result": [
                {
                    "update_id": 100,
                    "message": {"text": "/status", "chat": {"id": 12345}}
                }
            ]
        }
        
        # We need a way to break the infinite loop in poll()
        # We'll use side_effect to raise an exception after the first loop iteration
        mock_get.side_effect = [mock_get.return_value, KeyboardInterrupt()]
        
        self.bot.handle_status = MagicMock()
        self.bot.poll()
        
        self.bot.handle_status.assert_called_once()
        self.assertEqual(self.bot.offset, 101)

if __name__ == "__main__":
    unittest.main()
