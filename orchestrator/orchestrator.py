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
from utils.performance import calculate_performance_metrics
from risk.allocator import StrategyAllocator

class PipelineOrchestrator:
    """
    Orchestrates the multi-agent trading lifecycle.
    Includes Hardware Throttling, Panic Exit, and Dynamic Strategy Rebalancing.
    """

    def __init__(self, initial_cash: float = None):
        self.config = ConfigLoader().get_config()
        self.logger = JsonLogger(log_file="logs/orchestrator.log")
        self.sys_monitor = SystemMonitor()
        
        # Agents & Tools
        self.research_agent = ResearchAgent()
        self.strategy_agent = StrategyAgent()
        self.trading_agent = TradingAgent(initial_cash=initial_cash)
        self.universe_agent = UniverseSelectionAgent(research_agent=self.research_agent)
        self.allocator = StrategyAllocator(total_capital=self.config.get('initial_cash', 100000000.0))
        
        # Utils
        self.persistence = SignalPersistence()
        self.history = HistoryManager()

    def run_full_pipeline(self, pipeline: str = "daily"):
        """ Runs the full scan and trade loop with advanced guards. """
        
        # 1. Hardware Safety Check
        is_safe, reason = self.sys_monitor.is_safe_to_run()
        if not is_safe:
            broadcast_alert(f"⚠️ *OTOT BOT AYANG LAGI LEMAS*\nScan ditunda... {reason}. Biarin bot istirahat ya! 🍵")
            return

        # 2. Dynamic Capital Rebalancing (Inter-Strategy)
        if self.config.get("risk", {}).get("dynamic_strategy_allocation"):
            self.logger.info("Orchestrator: Recalculating strategy weights...")
            allocations = self.allocator.get_allocation_map()
            for p_name, cap in allocations.items():
                if p_name in self.trading_agent.portfolios:
                    self.trading_agent.portfolios[p_name].initial_capital = cap
                    self.trading_agent.portfolios[p_name].save_state()

        # 3. Expectancy Safeguard
        all_trades = self.history.db.get_all_trades()
        p_trades = [t for t in all_trades if t.get('strategy', '').lower() == pipeline]
        if len(p_trades) >= 10:
            metrics = calculate_performance_metrics(p_trades, [])
            if metrics.get('expectancy', 0) < 0:
                self.logger.warning(f"Orchestrator: Expectancy gate engaged for {pipeline}. Ex: {metrics['expectancy']}")
                broadcast_alert(f"🌸 *INFO AYANG*\nSayang, strategi `{pipeline.upper()}` lagi gak punya hoki (Expectancy < 0). Ayang istirahatin dulu ya buat jaga tabungan kita! 🍵")
                return

        self.logger.info(f"Orchestrator: Starting {pipeline.upper()} pipeline...")
        # ... rest of the pipeline remains the same ...
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
                        "timestamp": str(last_row.name),
                        "close": last_row['close'],
                        "signal": last_row['recommendation'],
                        "confidence": last_row.get('ml_confidence', 0.5),
                        "tp1": last_row['tp1'],
                        "tp2": last_row['tp2'],
                        "sl": last_row['sl_level'],
                    }
                    all_signals.append(signal_data)
                    self.trading_agent.trade(recommendations, pipeline=pipeline)
            except Exception as e:
                self.logger.error(f"Orchestrator: Error processing ticker [{ticker}]", error=str(e))

        self.persistence.save_signals(all_signals, pipeline)
        self.logger.info(f"Orchestrator: {pipeline.upper()} pipeline complete in {time.time() - start_time:.2f}s")
        
        if all_signals:
            broadcast_alert(self.generate_signal_report(pipeline))

    def handle_panic_exit(self) -> str:
        self.logger.critical("Orchestrator: PANIC EXIT TRIGGERED!")
        results = []
        for name, portfolio in self.trading_agent.portfolios.items():
            tickers = list(portfolio.positions.keys())
            for ticker in tickers:
                portfolio.update_position(ticker, portfolio.positions[ticker]["shares"], 0, "SELL")
                results.append(f"• {ticker} Sold")
            portfolio.save_state()
        return "🚨 *PANIC EXIT EXECUTED!*\nSemua posisi dicairkan sayang. 🛡️" if results else "🌸 Portofolio sudah kosong sayang."

    def generate_signal_report(self, pipeline: str) -> str:
        signals = self.persistence.load_signals(pipeline)
        if not signals: return f"🌸 *Ayang Glu-Stock ({pipeline.upper()})*\n_Lagi sepi sinyal nih sayang..._"
        
        brain_info = self.strategy_agent.ml_predictor.get_info()
        report = f"🎯 *SINYAL TRADING ({pipeline.upper()})*\n📅 `{datetime.now().strftime('%Y-%m-%d %H:%M')}`\n\n"
        for s in signals:
            icon = "🚀" if s['signal'] == "BUY" else "🔻"
            intel = "🧠" if s.get('confidence', 0) > 0.7 else ""
            report += f"{icon} *{s['ticker']}* {intel}\nPrice: `{s['close']:,.0f}` | Conf: `{s.get('confidence', 0):.0%}`\n🎯 TP: `{s['tp1']:,.0f}` | 🧱 SL: `{s['sl']:,.0f}`\n\n"
        return report

    def handle_status_command(self) -> str:
        stats = self.sys_monitor.get_status()
        msg = "🔋 *KONDISI HP AYANG*\n"
        msg += f"⚡ Bat: `{stats['battery_pct']}%` | 🌡 `{stats['battery_temp']}°C` | 🧠 RAM: `{stats['ram_usage']}%`\n\n"
        
        port_stats = self.trading_agent.get_status({})
        msg += "📊 *Portfolio Recap:*\n"
        for name, p in port_stats.items():
            msg += f"• `{name.upper()}`: `Rp {p['cash']:,.0f}`\n"
        return msg

    def handle_history_command(self, cmd_text: str) -> str:
        logs = self.history.get_history(limit=5)
        if not logs: return "🌸 Belum ada riwayat nih sayang..."
        msg = f"📜 *CATATAN TRADING (5 Terakhir)*\n\n"
        for log in logs:
            msg += f"{'✅' if log['action']=='BUY' else '❌'} *{log['ticker']}* @ `{log['price']:,.0f}`\n"
        return msg

    def handle_log_system_command(self, cmd_text: str) -> str:
        logs = self.logger.query_logs(limit=10)
        msg = f"📂 *SYSTEM LOGS*\n\n"
        for log in logs:
            msg += f"🕒 `{log['timestamp'][:19]}`: `{log['message']}`\n"
        return msg
