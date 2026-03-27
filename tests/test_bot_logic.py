import unittest
from unittest.mock import patch, MagicMock
from telegram_bot import TelegramBot
from orchestrator.orchestrator import PipelineOrchestrator

class TestBotLogic(unittest.TestCase):
    
    def setUp(self):
        # Mocking config to bypass real bot token/chat_id
        with patch('utils.config.ConfigLoader.get_config') as mock_conf:
            mock_conf.return_value = {
                "telegram": {"enabled": True, "bot_token": "test", "chat_id": "123"}
            }
            self.bot = TelegramBot()

    @patch('utils.text_report.TextReportGenerator.generate_daily_report')
    @patch('telegram_bot.TelegramBot.send_message')
    def test_report_daily_command(self, mock_send, mock_gen):
        mock_gen.return_value = "Daily Mock Report"
        self.bot.handle_report("/report daily")
        mock_send.assert_called_with("Daily Mock Report")

    @patch('utils.text_report.TextReportGenerator.generate_weekly_report')
    @patch('telegram_bot.TelegramBot.send_message')
    def test_report_weekly_command(self, mock_send, mock_gen):
        mock_gen.return_value = "Weekly Mock Report"
        self.bot.handle_report("/report weekly")
        mock_send.assert_called_with("Weekly Mock Report")

    @patch('utils.text_report.TextReportGenerator.generate_daily_report')
    @patch('telegram_bot.TelegramBot.send_message')
    def test_portfolio_command(self, mock_send, mock_gen):
        mock_gen.return_value = "Portfolio Mock Report"
        self.bot.handle_portfolio()
        mock_send.assert_called_with("Portfolio Mock Report")

    @patch('utils.text_report.TextReportGenerator.generate_daily_report')
    @patch('orchestrator.orchestrator.send_telegram_alert')
    def test_orchestrator_auto_report(self, mock_alert, mock_gen):
        mock_gen.return_value = "Auto EOD Report"
        orch = PipelineOrchestrator()
        orch._send_telegram_summary({"dummy": "data"}) # Internal call test
        mock_alert.assert_called_with("Auto EOD Report")

if __name__ == "__main__":
    unittest.main()
