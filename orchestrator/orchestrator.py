import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from agents.agents import ResearchAgent, StrategyAgent, TradingAgent, UniverseSelectionAgent
from reporting.report import ReportGenerator
from utils.alerts import send_telegram_alert
from utils.history import StrategicHistoryManager
from utils.text_report import TextReportGenerator
from backtesting.backtest import VectorizedBacktester
from portfolio.portfolio import Portfolio
from utils.config import ConfigLoader
from utils.logger import JsonLogger
from utils.persistence import SignalPersistence

class PipelineOrchestrator:
    """
    Coordinates the full lifecycle (Research -> Strategy -> Trading -> Reporting)
    for multiple tickers with robust error handling.
    """

    def __init__(self, initial_cash: float = 100000.0, output_dir: str = "reporting/exports"):
        self.logger = JsonLogger(log_file="logs/orchestrator.log")
        self.persistence = SignalPersistence()
        self.history_manager = StrategicHistoryManager()
        self.results = {"candidates": [], "success": [], "errors": []}
        self.research_agent = ResearchAgent()
        self.strategy_agent = StrategyAgent()
        self.backtester = VectorizedBacktester(initial_capital=initial_cash)
        self.trading_agent = TradingAgent(initial_cash=initial_cash)
        self.universe_agent = UniverseSelectionAgent(research_agent=self.research_agent)
        self.report_generator = ReportGenerator(output_dir=output_dir)

    def run_full_pipeline(self, tickers: Optional[List[str]] = None, max_stocks: int = 5, start_date: Optional[str] = None, end_date: Optional[str] = None, pipeline: str = "daily", send_alert: bool = False) -> Dict[str, Any]:
        """
        Coordinates the institutional trading lifecycle.
        If send_alert=True, it will trigger Telegram immediately.
        Otherwise, it only saves signals to persistence for later broadcast.
        """
        config = ConfigLoader().get_config()
        paper_trading = config.get("paper_trading", True)
        
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            
        self.logger.info(f"Orchestrator: Starting pipeline for {tickers}, max_stocks={max_stocks}")
        
        # 1. Initialization and Universe Selection
        scanned_count = 0
        candidate_count = 0
        trade_count = 0
        
        if tickers is None:
            self.logger.info(f"Orchestrator: Selecting top {max_stocks} dynamically via [{pipeline}] pipeline...")
            tickers = self.universe_agent.select_universe(max_stocks, start_date, end_date, pipeline=pipeline)
            
        tickers = tickers or []
        
        # DEBUG MODE OVERRIDE
        debug_mode = ConfigLoader().get_config().get('debug_mode', True)
        if debug_mode:
            self.logger.info("Orchestrator: !! DEBUG MODE ACTIVE !! Forcing Top 3 selection.")
            selected_stocks = tickers[:3]
        else:
            # Ensure we only process the top 5 (selected_stocks)
            selected_stocks = tickers[:5]

        scanned_count = len(tickers)
        self.logger.info(f"Orchestrator: [STEP 1/3] Scanned {scanned_count} tickers. Selecting Top {len(selected_stocks)}.")
        
        # Determine Interval based on pipeline
        # Daily: 15m for intraday signals (Need to fetch enough history for indicators)
        interval = "15m" if pipeline == "daily" else "1d"
        # Adjusted start_date for intraday to stay within yfinance limits (60 days for 15m)
        if interval == "15m":
            start_date = (datetime.now() - timedelta(days=59)).strftime("%Y-%m-%d")

        # Prepare results for this clear run
        self.results["candidates"] = []
        self.results["success"] = []
        self.results["failure"] = []

        # 2. Sequential Processing (Ensuring execution regardless of signal strength)
        self.logger.info(f"Orchestrator: [STEP 1/3] Researching {len(tickers)} stocks...")
        self.history_manager.log_event(pipeline, "SCAN_START", details=f"Tickers to research: {len(tickers)}")
        all_data = {}
        for ticker in selected_stocks:
            self.logger.info(f"Orchestrator: Processing [{ticker}]...")
            try:
                # A. Research
                df = self.research_agent.research([ticker], start_date, end_date, interval=interval)
                if df.empty:
                    continue
                all_data[ticker] = df
            except Exception as e:
                self.logger.error(f"Orchestrator: Error processing [{ticker}]: {str(e)}")
                self.results["failure"].append({"ticker": ticker, "error": str(e)})

        # 3. Strategy Analysis
        self.logger.info(f"Orchestrator: Generating signals for {len(all_data)} tickers...")
        for ticker, df in all_data.items():
            signals = self.strategy_agent.get_recommendations(df, pipeline=pipeline)
            if not signals.empty and signals['final_signal'].iloc[-1] != 0:
                # Mandatory Backtest Audit
                audit_result = self._audit_with_backtest(ticker, df, pipeline)
                if audit_result["pass"]:
                    rec = signals.iloc[-1].to_dict()
                    rec['ticker'] = ticker
                    rec['audit'] = audit_result
                    self.results["candidates"].append(rec)
                    self.logger.info(f"Orchestrator: Signal for {ticker} PASSED audit (WR: {audit_result['win_rate']:.1f}%)")
                    
                    self.history_manager.log_event(
                        pipeline, "AUDIT", ticker, audit_result['win_rate'], "PASS", 
                        f"PF: {audit_result['profit_factor']:.2f}"
                    )
                    
                    # D. Execution
                    self.trading_agent.trade(signals, pipeline=pipeline)
                    self.history_manager.log_event(pipeline, "TRADE", ticker, status="SUCCESS")
                    
                    trade_count += 1
                    candidate_count += 1
                    self.results["success"].append(ticker)
                else:
                    self.logger.warning(f"Orchestrator: Signal for {ticker} FAILED audit (WR: {audit_result['win_rate']:.1f}%) - skipping.")
                    self.history_manager.log_event(
                        pipeline, "AUDIT", ticker, audit_result['win_rate'], "FAIL", 
                        f"PF: {audit_result['profit_factor']:.2f}"
                    )

        self.logger.info(f"Orchestrator: [STEP 2/3] Found {candidate_count} candidates for execution.")
        self.logger.info(f"Orchestrator: [STEP 3/3] Processed {trade_count} execution attempts.")
        self.history_manager.log_event(pipeline, "SCAN_END", details=f"Candidates found: {candidate_count}")

        # 3. Forced Reporting (Always Runs)
        self.logger.info("Orchestrator: Finalizing session and forced reporting...")
        final_summary = self._consolidate_results(list(all_data.values()))
        
        # Institutional Signal Report
        self.persistence.save_signals(pipeline, self.results["candidates"])
        
        if send_alert:
            signal_report = self.generate_signal_report(pipeline)
            send_telegram_alert(signal_report)
        
        self._generate_final_report(final_summary)
        
        self.logger.info(f"Orchestrator: Aggregation complete, tickers_processed={len(final_summary['tickers_processed'])}")
        return final_summary

    def broadcast_saved_signals(self, pipeline: str):
        """ Instantly sends the Telegram report using saved persistence data. """
        self.logger.info(f"Orchestrator: Broadcasting saved signals for [{pipeline}]...")
        saved_candidates = self.persistence.load_signals(pipeline)
        
        # Temporarily fill results for report generation
        self.results["candidates"] = saved_candidates
        
        report = self.generate_signal_report(pipeline)
        send_telegram_alert(report)
        self.logger.info(f"Orchestrator: Broadcast complete for [{pipeline}].")

    def _audit_with_backtest(self, ticker: str, df: pd.DataFrame, pipeline: str) -> Dict[str, Any]:
        """ Performs a vectorized backtest on the ticker to validate indicator edge. """
        # Ensure signals are generated for the entire history
        full_signals = self.strategy_agent.get_recommendations(df, pipeline=pipeline, return_full=True)
        
        # Run Backtest
        bt_df = self.backtester.run_backtest(full_signals)
        metrics = self.backtester.get_ticker_metrics(bt_df, ticker)
        
        # Define Thresholds
        thresholds = {
            "daily": {"win_rate": 50.0, "profit_factor": 1.2},
            "weekly": {"win_rate": 45.0, "profit_factor": 1.5},
            "monthly": {"win_rate": 40.0, "profit_factor": 2.0}
        }
        
        t = thresholds.get(pipeline.lower(), thresholds["daily"])
        passed = (metrics["win_rate"] >= t["win_rate"]) and (metrics["profit_factor"] >= t["profit_factor"])
        
        metrics["pass"] = passed
        return metrics

    def broadcast_portfolio_status(self, pipeline: str):
        """ Fetches current prices and sends a detailed EOD Portfolio report. """
        self.logger.info(f"Orchestrator: Generating EOD Portfolio Report for [{pipeline}]...")
        
        # 1. Get Tickers
        tickers = list(self.trading_agent.portfolio.positions.keys())
        current_prices = {}
        
        if tickers:
            # Fetch latest prices
            df = self.research_agent.research(tickers, 
                                            start_date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                                            end_date=datetime.now().strftime("%Y-%m-%d"),
                                            interval="1h")
            for ticker in tickers:
                if ticker in df.index.get_level_values('ticker'):
                    current_prices[ticker] = df.xs(ticker, level='ticker')['close'].iloc[-1]

        # 2. Get Summary
        summary = self.trading_agent.get_detailed_status(current_prices, pipeline=pipeline)
        
        # 3. Log Outcomes to History
        for h in summary.get("holdings", []):
            status = "PROFIT" if h["pnl"] >= 0 else "LOSS"
            self.history_manager.log_event(
                pipeline, "RECAP", h["ticker"], h["pnl_pct"], status, 
                f"Lots: {h['lots']}, PnL: Rp{h['pnl']:,.0f}"
            )

        # 4. Format & Send
        report = self.generate_portfolio_report(summary, pipeline)
        send_telegram_alert(report)
        self.logger.info(f"Orchestrator: Portfolio report sent for [{pipeline}].")

    def generate_portfolio_report(self, summary: Dict[str, Any], pipeline: str) -> str:
        """ Formats the portfolio summary like a security firm report. """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        header = f"📊 *GLU-STOCK PORTFOLIO REKAP ({pipeline.upper()})*\n"
        header += f"📅 {now_str}\n\n"
        
        body = ""
        for h in summary["holdings"]:
            emoji = "🟢" if h["pnl"] >= 0 else "🔴"
            body += f"{emoji} *{h['ticker']}*\n"
            body += f"   - Lot: {h['lots']:.2f} ({h['shares']} shrs)\n"
            body += f"   - Avg: {h['avg_price']:.2f} | Last: {h['last_price']:.2f}\n"
            body += f"   - PnL: {h['pnl']:+,.2f} ({h['pnl_pct']:+2.2f}%)\n\n"
        
        if not summary["holdings"]:
            body = "_Tidak ada posisi aktif saat ini._\n\n"
            
        footer = "==============================\n"
        footer += f"💰 *Cash:* {summary['cash']:,.2f}\n"
        footer += f"📈 *Equity:* {summary['equity']:,.2f}\n"
        footer += f"🏆 *Total PnL:* {summary['realized_pnl'] + summary['unrealized_pnl']:+,.2f}\n"
        
        return header + body + footer

    def generate_signal_report(self, pipeline: str) -> str:
        """ Formats the signal report for Telegram based on user request. """
        p_name = pipeline.upper()
        candidates = self.results["candidates"]
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        header = f"🚀 *GLU-STOCK PRE-MARKET ANALYSIS ({p_name})*\n"
        header += f"📅 {now_str}\n\n"
        header += f"Total saham yang lolos filter: {len(candidates)}\n"
        header += "==============================\n\n"
        
        body = ""
        for c in candidates:
            # We check if it's the detailed Dict or the old List format
            if isinstance(c, dict) and "buy_level" in c:
                body += f"🔹 *{c['ticker']}*\n"
                if "audit" in c:
                    a = c["audit"]
                    body += f"🛡️ *Audit:* PASS (WR: {a['win_rate']:.1f}% | PF: {a['profit_factor']:.2f})\n"
                body += f"   - BUY: {c['buy_level']:,.2f}\n"
                body += f"   - TP1: {c['tp1']:,.2f} | TP2: {c['tp2']:,.2f}\n"
                body += f"   - SL: {c['sl_level']:,.2f}\n"
                body += f"   - Validity: {c['signal_duration']}\n\n"
            else:
                ticker = c.get('ticker') if isinstance(c, dict) else c
                body += f"🔹 *{ticker}* (No precise signal detail)\n\n"
            
        if not candidates:
            body = "Tidak ada saham yang memenuhi kriteria hari ini.\n"
            
        footer = "⚠️ _Setiap keputusan trading berisiko. Gunakan MM yang ketat._"
        return header + body + footer

    def _send_telegram_summary(self, summary: Dict[str, Any], candidates: List[Dict[str, Any]] = None):
        """ Sends high-impact session summary to Telegram with robust fallback. """
        try:
            report = TextReportGenerator().generate_daily_report(candidates=candidates)
            if not report or "Report" not in report: # Crude check for empty/missing components
                report = "⚠️ WARNING: Report empty"
        except Exception as e:
            report = f"❌ ERROR: Failed to generate report: {str(e)}"
        
        send_telegram_alert(report)

    def _consolidate_results(self, all_dfs: List[pd.DataFrame]) -> Dict[str, Any]:
        """ Consolidates metrics from all successful ticker runs. """
        # We'll use the portfolio status as ground truth
        # For simplicity, we'll combine all DFs to get a global equity curve if needed
        # But here we focus on the TradingAgent status.
        tickers_success = [ticker for ticker in self.results["success"]]
        
        # Approximate current prices from last available 'close'
        prices = {}
        for df in all_dfs:
            if not df.empty:
                last_row = df.iloc[-1]
                # Ticker is in MultiIndex
                ticker = df.index.get_level_values('ticker')[0]
                prices[ticker] = last_row['close']
        
        status = self.trading_agent.get_status(prices)
        
        return {
            "tickers_processed": self.results["success"],
            "failures": self.results["failure"],
            "final_portfolio": status,
            "trade_log_path": self.trading_agent.execution_engine.log_file
        }

    def _generate_final_report(self, summary: Dict[str, Any]):
        """ Triggers the HTML report generation. """
        print("Orchestrator: Generating final HTML report...")
        log_file = summary.get("trade_log_path", "execution/trade_log.csv")
        trade_log = pd.DataFrame()
        if os.path.exists(log_file):
            trade_log = pd.read_csv(log_file)
            
        metrics = {
            "Total_Equity": f"${summary['final_portfolio']['equity']:.2f}",
            "Cash": f"${summary['final_portfolio']['cash']:.2f}",
            "Realized_PnL": f"${summary['final_portfolio']['realized_pnl']:.2f}",
            "Assets": len(summary.get('tickers_processed', [])),
            "Failures": len(summary.get('failures', []))
        }
        equity_series = pd.Series([100000, summary['final_portfolio']['equity']])
        self.report_generator.generate_html_report(metrics, trade_log, equity_series, filename="orchestrator_report.html")

    def handle_history_command(self, command_str: str) -> str:
        """ 
        Parses and handles /history [strategy/date/ticker] command.
        Example: /history daily, /history 2024-03-28, /history BBCA.JK
        """
        parts = command_str.strip().split()
        filter_val = parts[1] if len(parts) > 1 else None
        
        strategy = None
        ticker = None
        date_val = None
        
        if filter_val:
            val = filter_val.lower()
            if val in ["daily", "weekly", "monthly"]:
                strategy = val
            elif "-" in val and len(val) == 10:
                date_val = val
            else:
                ticker = filter_val.upper()
        
        if date_val:
            events = self.history_manager.get_daily_summary(date_val)
            title = f"📅 History for {date_val}"
        else:
            events = self.history_manager.query_history(strategy=strategy, ticker=ticker, limit=15)
            title = f"📜 History: {filter_val or 'Recent'}"
            
        return self._format_history_report(events, title)

    def _format_history_report(self, events: List[Dict[str, Any]], title: str) -> str:
        """ Formats history events into a Telegram-friendly Markdown table. """
        if not events:
            return f"❌ *{title}*\n_No logs found for this query._"
            
        report = f"📋 *{title.upper()}*\n"
        report += "`TIME  | TYPE   | TICKER   | STATUS`\n"
        report += "`----------------------------------`\n"
        
        for e in events:
            # Shorten timestamp to HH:MM
            t = e['timestamp'].split()[1][:5] if ' ' in e['timestamp'] else e['timestamp'][-5:]
            phase = e['phase'][:6].ljust(6)
            ticker = e['ticker'][:8].ljust(8)
            status = e['status'][:6]
            
            report += f"`{t} | {phase} | {ticker} | {status}`\n"
            if e['phase'] in ["TRADE", "RECAP", "AUDIT"]:
                 report += f"   _{e['details']}_\n"
                 
        return report

if __name__ == "__main__":
    import os
    # Integration test
    orch = PipelineOrchestrator(initial_cash=100000)
    # Using real tickers to test resilience
    summary = orch.run_full_pipeline(["AAPL", "TSLA", "NONEXISTENT_TICKER"], "2024-01-01", "2024-02-01")
    print(summary)
