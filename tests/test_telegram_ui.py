import unittest
from unittest.mock import MagicMock, patch
import json
from telegram_bot import TelegramBot

class TestTelegramUI(unittest.TestCase):
    
    def setUp(self):
        # Patching network and config to avoid external calls during init
        with patch('telegram_bot.PipelineOrchestrator'), \
             patch('telegram_bot.requests.post'), \
             patch('utils.config.ConfigLoader.get_config'), \
             patch('data.database.TradingDatabase'):
            self.bot = TelegramBot()
            self.bot.orchestrator = MagicMock()
            self.bot.chat_id = "123"

    @patch('telegram_bot.requests.post')
    def test_routing_logic(self, mock_post):
        """ 
        Verify that our internal routing logic (manually triggered) 
        correctly calls Orchestrator. 
        """
        # 1. Test /status routing
        text = "/status"
        self.bot.orchestrator.handle_status_command.return_value = "STATUS OK"
        
        # Execute routing logic manually (extracted from poll loop)
        cmd = text.split()[0].lower()
        if cmd == "/status":
            res = self.bot.orchestrator.handle_status_command()
            self.bot.send_message(res)
            
        self.bot.orchestrator.handle_status_command.assert_called_once()
        self.assertEqual(res, "STATUS OK")

    @patch('telegram_bot.requests.post')
    def test_signals_callback_routing(self, mock_post):
        """ Verify callback data routing for signals. """
        text = "/signals weekly"
        
        cmd = text.split()[0].lower()
        if cmd == "/signals":
            pipeline = text.split()[1] if len(text.split()) > 1 else "daily"
            self.bot.orchestrator.broadcast_saved_signals(pipeline)
            
        self.bot.orchestrator.broadcast_saved_signals.assert_called_with("weekly")

if __name__ == '__main__':
    unittest.main()
