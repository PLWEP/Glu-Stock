import time
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from agents.agents import ResearchAgent, StrategyAgent, TradingAgent, UniverseSelectionAgent
from utils.persistence import SignalPersistence
from utils.firebase_handler import FirebaseHandler
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
        self.history = FirebaseHandler(ConfigLoader().get_firebase_config())

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
        target_exposures = {}
        price_data_dict = {}

        for ticker in tickers:
            try:
                df = self.research_agent.research([ticker], start_date, end_date, interval="15m" if pipeline=="daily" else "1d")
                recommendations = self.strategy_agent.get_recommendations(df, pipeline=pipeline)
                
                if not recommendations.empty:
                    last_row = recommendations.iloc[-1]
                    # Institutional Conviction is encoded in inst_trend_conviction (-1.0 to 1.0)
                    conviction = last_row.get('inst_trend_conviction', 0)
                    target_exposures[ticker] = conviction
                    price_data_dict[ticker] = df

                    signal_data = {
                        "ticker": ticker,
                        "timestamp": str(last_row.name),
                        "close": last_row['close'],
                        "signal": last_row['recommendation'],
                        "ml_conf": last_row.get('ml_conf', 0.5),
                        "cnn_conf": last_row.get('cnn_conf', 0.5),
                        "ens_conf": last_row.get('ens_conf', 0.5),
                        "conviction": conviction,
                        "tp1": last_row['tp1'],
                        "tp2": last_row['tp2'],
                        "sl": last_row['sl_level'],
                    }
                    all_signals.append(signal_data)
            except Exception as e:
                self.logger.error(f"Orchestrator: Error [{ticker}]", error=str(e))

        # 5. Institutional Rebalancing (The ARP Layer)
        if target_exposures:
            self.trading_agent.rebalance(target_exposures, price_data_dict, pipeline=pipeline)

        self.persistence.save_signals(all_signals, pipeline)
        
        if all_signals:
            report = self.generate_signal_report(pipeline)
            # SaaS Broadcasting disabled as per user request
            # channel_id = os.environ.get("TELEGRAM_CHANNEL_ID")
            # if channel_id and self.bot:
            #     self.bot.send_message(report, target_chat_id=channel_id)
            
            # Add Market Context to report
            market_note = "\n📉 *Kondisi Pasar*: Bearish (Risiko dikurangi 50%)" if regime_res['regime'] == "BEAR" else "\n📈 *Kondisi Pasar*: Bullish (Tancap Gas)"
            # broadcast_alert(report + market_note) # Disable all broadcast alerts for now
            return report
        return None

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
            conv = s.get('conviction', 0)
            conv_icon = "🔥" if abs(conv) > 0.8 else "🔹"
            
            report += f"{icon} *{s['ticker']}* {intel} {conv_icon}\n"
            report += f"Price: `{s['close']:,.0f}` | Conv: `{conv:+.2f}`\n"
            report += f"Ens: `{s.get('ens_conf', 0):.0%}` | CNN: `{s.get('cnn_conf', 0):.0%}`\n"
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
        # 1. Parse filter from command
        parts = cmd_text.split()
        filter_val = parts[1].lower() if len(parts) > 1 else None
        
        # 2. Get events from Strategic History (Checking both strategy and ticker)
        if filter_val:
            # Try as strategy first
            logs = self.history.query_history(strategy=filter_val, limit=10)
            # If nothing, try as ticker
            if not logs:
                logs = self.history.query_history(ticker=filter_val, limit=10)
        else:
            logs = self.history.query_history(limit=5)
        
        if not logs: 
            return f"🌸 Belum ada catatan untuk `{filter_val or 'semua'}` nih sayang."
        
        header = f"📜 *CATATAN TRADING ({filter_val.upper() if filter_val else 'TERAKHIR'})*\n\n"
        msg = header
        for log in logs:
            phase = log.get('phase', 'INFO')
            icon = "🎯" if phase == 'TRADE' else ("🔍" if phase == 'SCAN' else "📊")
            msg += f"{icon} *{log['ticker']}* | {log['phase']}\n"
            msg += f"   Status: `{log['status']}` | `{log['details']}`\n"
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
