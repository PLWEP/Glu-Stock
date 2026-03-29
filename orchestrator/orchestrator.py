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
from utils.regime import RegimeDetector
from risk.allocator import StrategyAllocator

class PipelineOrchestrator:
    """
    Orchestrates the multi-agent trading lifecycle.
    Includes Hardware Throttling, Panic Exit, and Market Regime Guards.
    """

    def __init__(self, initial_cash: float = None):
        self.config = ConfigLoader().get_config()
        self.logger = JsonLogger(log_file="logs/orchestrator.log")
        self.sys_monitor = SystemMonitor()
        self.regime_detector = RegimeDetector()
        
        # Agents & Tools
        self.research_agent = ResearchAgent()
        self.strategy_agent = StrategyAgent()
        self.trading_agent = TradingAgent(initial_cash=initial_cash)
        self.universe_agent = UniverseSelectionAgent(research_agent=self.research_agent)
        self.allocator = StrategyAllocator(total_capital=self.config.get('initial_cash', 100000000.0))
        
        self.persistence = SignalPersistence()
        self.history = HistoryManager()

    def run_full_pipeline(self, pipeline: str = "daily"):
        # 1. Hardware Safety Check
        is_safe, reason = self.sys_monitor.is_safe_to_run()
        if not is_safe:
            broadcast_alert(f"⚠️ *OTOT BOT AYANG LAGI LEMAS*\nScan ditunda... {reason}. Biarin bot istirahat ya! 🍵")
            return

        # 2. Market Regime Check (Global Risk Throttling)
        regime_res = self.regime_detector.get_market_regime()
        regime_label = f"📈 Market: {regime_res['regime']}"
        risk_multiplier = regime_res.get('multiplier', 1.0)
        
        # 3. Dynamic Strategy Rebalancing 
        if self.config.get("risk", {}).get("dynamic_strategy_allocation"):
            allocations = self.allocator.get_allocation_map()
            for p_name, cap in allocations.items():
                if p_name in self.trading_agent.portfolios:
                    # Apply Regime Multiplier to the allocated capital
                    final_cap = cap * risk_multiplier
                    self.trading_agent.portfolios[p_name].initial_capital = final_cap
                    self.trading_agent.portfolios[p_name].save_state()

        # 4. Expectancy Safeguard
        all_trades = self.history.db.get_all_trades()
        p_trades = [t for t in all_trades if t.get('strategy', '').lower() == pipeline]
        if len(p_trades) >= 10:
            metrics = calculate_performance_metrics(p_trades, [])
            if metrics.get('expectancy', 0) < 0:
                msg = f"🌸 *INFO AYANG*\nSayang, strategi `{pipeline.upper()}` lagi gak punya hoki (Ex < 0). Ayang istirahatin dulu ya! 🍵"
                broadcast_alert(msg)
                return

        self.logger.info(f"Orchestrator: Starting {pipeline.upper()} pipeline ({regime_label})...")
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
                        "ml_conf": last_row.get('ml_confidence', 0.5),
                        "cnn_conf": last_row.get('cnn_confidence', 0.5),
                        "ens_conf": last_row.get('ensemble_confidence', 0.5),
                        "tp1": last_row['tp1'],
                        "tp2": last_row['tp2'],
                        "sl": last_row['sl_level'],
                    }
                    all_signals.append(signal_data)
                    self.trading_agent.trade(recommendations, pipeline=pipeline)
            except Exception as e:
                self.logger.error(f"Orchestrator: Error [{ticker}]", error=str(e))

        self.persistence.save_signals(all_signals, pipeline)
        
        if all_signals:
            report = self.generate_signal_report(pipeline)
            # Add Market Context to report
            market_note = "\n📉 *Kondisi Pasar*: Bearish (Risiko dikurangi 50%)" if regime_res['regime'] == "BEAR" else "\n📈 *Kondisi Pasar*: Bullish (Tancap Gas)"
            broadcast_alert(report + market_note)

    def handle_panic_exit(self) -> str:
        results = []
        for name, portfolio in self.trading_agent.portfolios.items():
            tickers = list(portfolio.positions.keys())
            for ticker in tickers:
                portfolio.update_position(ticker, portfolio.positions[ticker]["shares"], 0, "SELL")
                results.append(f"• {ticker} Sold")
            portfolio.save_state()
        return "🚨 *PANIC EXIT!* Semua posisi dicairkan sayang. 🛡️" if results else "🌸 Kosong sayang."

    def generate_signal_report(self, pipeline: str) -> str:
        signals = self.persistence.load_signals(pipeline)
        if not signals: return f"🌸 *Ayang Glu-Stock ({pipeline.upper()})*\n_Lagi sepi sinyal..._"
        report = f"🎯 *SINYAL TRADING ({pipeline.upper()})*\n📅 `{datetime.now().strftime('%Y-%m-%d %H:%M')}`\n\n"
        for s in signals:
            icon = "🚀" if s['signal'] == "BUY" else "🔻"
            # Badge if Ensemble confidence is high
            intel = "🧠" if s.get('ens_conf', 0) > 0.7 else ""
            report += f"{icon} *{s['ticker']}* {intel}\n"
            report += f"Price: `{s['close']:,.0f}` | Ens: `{s.get('ens_conf', 0):.0%}`\n"
            report += f"CNN: `{s.get('cnn_conf', 0):.0%}` | ML: `{s.get('ml_conf', 0):.0%}`\n"
            report += f"🎯 TP: `{s['tp1']:,.0f}` | 🧱 SL: `{s['sl']:,.0f}`\n\n"
        return report

    def handle_status_command(self) -> str:
        stats = self.sys_monitor.get_status()
        regime = self.regime_detector.get_market_regime()
        msg = "🔋 *KONDISI HP AYANG*\n"
        msg += f"⚡ Bat: `{stats['battery_pct']}%` | 🌡 `{stats['battery_temp']}°C` | 📈 Market: `{regime['regime']}`\n\n"
        port_stats = self.trading_agent.get_status({})
        msg += "📊 *Portfolio Recap:*\n"
        for name, p in port_stats.items():
            msg += f"• `{name.upper()}`: `Rp {p['cash']:,.0f}`\n"
        return msg

    def handle_history_command(self, cmd_text: str) -> str:
        logs = self.history.get_history(limit=5)
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

    def handle_registry_command(self) -> str:
        """ Shows top experiments from the Backtest Registry. """
        from data.backtest_db import BacktestRegistry
        registry = BacktestRegistry()
        experiments = registry.get_top_experiments(limit=5)
        
        if not experiments:
            return "🌸 *Info Lab Ayang*\nBelum ada catatan simulasi nih sayang. Coba jalankan backtest dulu ya! 🧪"
            
        msg = "🧪 *REGISTRY EKSPERIMEN (Top 5)*\n\n"
        for i, exp in enumerate(experiments, 1):
            msg += f"{i}. *{exp['pipeline'].upper()}* ({exp['ticker']})\n"
            msg += f"   📊 Sharpe: `{exp['sharpe']:.2f}` | OOS: `{exp['oos_sharpe']:.2f}`\n"
            msg += f"   📅 `{exp['date'][:10]}`\n\n"
        return msg
