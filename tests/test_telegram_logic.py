import unittest
from unittest.mock import MagicMock, patch
from telegram_bot import TelegramBot

class TestTelegramLogic(unittest.TestCase):
    @patch('telegram_bot.ConfigLoader')
    @patch('telegram_bot.TradingDatabase')
    def setUp(self, mock_db, mock_config):
        # Mock Config
        self.mock_config = mock_config.return_value
        self.mock_config.get_config.return_value = {
            "telegram": {
                "enabled": True,
                "bot_token": "fake_token",
                "chat_id": "12345"
            }
        }
        # Mock DB
        self.mock_db = mock_db.return_value
        
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
        # Setup dummy data
        self.mock_db.get_portfolio_history.return_value = [
            {"cash": 1000000.0, "equity": 1000000.0}
        ]
        self.mock_db.get_all_trades.return_value = [
            {"side": "BUY", "ticker": "BBCA.JK", "price": 10000.0}
        ]
        
        self.bot.handle_portfolio()
        args, _ = self.bot.send_message.call_args
        msg = args[0]
        
        self.assertIn("Current Portfolio Summary", msg)
        self.assertIn("Cash: IDR 1,000,000.00", msg)
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
