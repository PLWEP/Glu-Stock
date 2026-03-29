import time
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from agents.agents import ResearchAgent, StrategyAgent, TradingAgent, UniverseSelectionAgent
from utils.persistence import SignalPersistence
from utils.history import HistoryManager
from utils.logger import JsonLogger
from utils.sysinfo import SystemMonitor
from utils.alerts import broadcast_alert
from utils.config import ConfigLoader

class PipelineOrchestrator:
    """
    Orchestrates the multi-agent trading lifecycle.
    """

    def __init__(self, initial_cash: float = None):
        self.config = ConfigLoader().get_config()
        self.logger = JsonLogger(log_file="logs/orchestrator.log")
        self.sys_monitor = SystemMonitor()
        
        # Agents
        self.research_agent = ResearchAgent()
        self.strategy_agent = StrategyAgent()
        self.trading_agent = TradingAgent(initial_cash=initial_cash)
        self.universe_agent = UniverseSelectionAgent(research_agent=self.research_agent)
        
        # Utils
        self.persistence = SignalPersistence()
        self.history = HistoryManager()

    def run_full_pipeline(self, pipeline: str = "daily"):
        """ Runs the full scan and trade loop. """
        self.logger.info(f"Orchestrator: Starting {pipeline.upper()} pipeline...")
        
        start_time = time.time()
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=60 if pipeline=="daily" else 365)).strftime('%Y-%m-%d')
        max_stocks = self.config.get("max_stocks_to_scan", 10)
        
        tickers = self.universe_agent.select_universe(max_stocks, start_date, end_date, pipeline=pipeline)
        
        all_signals = []
        for ticker in tickers:
            try:
                df = self.research_agent.research([ticker], start_date, end_date, interval="15m" if pipeline=="daily" else "1d")
                recommendations = self.strategy_agent.get_recommendations(df, pipeline=pipeline)
                
                if not recommendations.empty:
                    last_row = recommendations.iloc[-1]
                    signal_data = {
                        "ticker": ticker,
                        "timestamp": last_row.name[0].isoformat() if isinstance(last_row.name, tuple) else str(last_row.name),
                        "close": last_row['close'],
                        "signal": last_row['recommendation'],
                        "confidence": last_row.get('ml_confidence', 0.5),
                        "tp1": last_row['tp1'],
                        "tp2": last_row['tp2'],
                        "sl": last_row['sl_level'],
                    }
                    all_signals.append(signal_data)
                    self.trading_agent.trade(recommendations, pipeline=pipeline)
                    self.history.log_trade(ticker, signal_data['signal'], signal_data['close'], 0, signal_data['tp1'], signal_data['sl'])
            except Exception as e:
                self.logger.error(f"Orchestrator: Error processing ticker [{ticker}]", error=str(e))

        self.persistence.save_signals(all_signals, pipeline)
        
        elapsed = time.time() - start_time
        self.logger.info(f"Orchestrator: {pipeline.upper()} pipeline complete in {elapsed:.2f}s")
        
        if all_signals:
            summary = self.generate_signal_report(pipeline)
            broadcast_alert(summary)

    def generate_signal_report(self, pipeline: str) -> str:
        signals = self.persistence.load_signals(pipeline)
        if not signals: return f"🌸 *Ayang Glu-Stock ({pipeline.upper()})*\n_Belum ada sinyal yang muncul nih sayang..._"
        
        # Brain Status Info
        brain_info = self.strategy_agent.ml_predictor.get_info()
        brain_status = f"✅ `Brain: {brain_info['accuracy']:.0%}`" if brain_info['status']=="Online" else "⚠️ `Brain: Offline`"
        
        report = f"🎯 *SINYAL TRADING ({pipeline.upper()})*\n"
        report += f"📅 `{datetime.now().strftime('%Y-%m-%d %H:%M')}` | {brain_status}\n\n"
        
        for s in signals:
            icon = "🚀" if s['signal'] == "BUY" else "🔻"
            intel_icon = "🧠" if s.get('confidence', 0) > 0.7 else ("🤖" if s.get('confidence', 0) > 0.6 else "")
            
            report += f"{icon} *{s['ticker']}* {intel_icon}\n"
            report += f"Price: `{s['close']:,.0f}` | Conf: `{s.get('confidence', 0):.0%}`\n"
            report += f"🎯 TP: `{s['tp1']:,.0f}` | 🧱 SL: `{s['sl']:,.0f}`\n\n"
            
        report += "_Ingat ya sayang, tetap gunakan manajemen risiko!_ 💖"
        return report

    def handle_status_command(self) -> str:
        stats = self.sys_monitor.get_status()
        brain_info = self.strategy_agent.ml_predictor.get_info()
        
        msg = "🔋 *KONDISI HP AYANG*\n"
        msg += f"⚡ Bat: `{stats['battery_pct']}%` | 🌡 `{stats['battery_temp']}°C`\n"
        msg += f"🧠 RAM: `{stats['ram_usage']}%` (`{stats['ram_free_gb']}GB`)\n"
        msg += f"🤖 Intel: `{brain_info['status']}` ({brain_info['accuracy']:.0%})\n\n"
        
        current_prices = {} 
        port_stats = self.trading_agent.get_status(current_prices)
        msg += "📊 *Portfolio Recap:*\n"
        for name, p in port_stats.items():
            msg += f"• `{name.upper()}`: `Rp {p['cash']:,.0f}`\n"
            
        return msg

    def handle_history_command(self, cmd_text: str) -> str:
        parts = cmd_text.split()
        limit = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
        logs = self.history.get_history(limit=limit)
        if not logs: return "🌸 Ayang belum punya catatan trading nih sayang..."
        
        msg = f"📜 *CATATAN TRADING ({limit} Terakhir)*\n\n"
        for log in logs:
            icon = "✅" if log['action'] == "BUY" else "❌"
            msg += f"{icon} *{log['ticker']}* @ `{log['price']:,.0f}`\n"
            msg += f"📅 `{log['timestamp']}`\n\n"
        return msg

    def handle_log_system_command(self, cmd_text: str) -> str:
        parts = cmd_text.split()
        level = parts[1].upper() if len(parts) > 1 else "INFO"
        limit = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 10
        
        logs = self.logger.query_logs(level=level, limit=limit)
        if not logs: return f"🌸 Gak ada log dengan level {level} nih sayang..."
        
        msg = f"📂 *SYSTEM LOGS ({level})*\n\n"
        for log in logs:
            time_str = log['timestamp'].split('.')[0].replace('T', ' ')
            msg += f"🕒 `{time_str}`\n"
            msg += f"💬 `{log['message']}`\n\n"
        return msg
