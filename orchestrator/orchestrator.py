import os
import pandas as pd
from typing import List, Dict, Any, Optional
from agents.agents import ResearchAgent, StrategyAgent, TradingAgent, UniverseSelectionAgent
from reporting.report import ReportGenerator

class PipelineOrchestrator:
    """
    Coordinates the full lifecycle (Research -> Strategy -> Trading -> Reporting)
    for multiple tickers with robust error handling.
    """

    def __init__(self, initial_cash: float = 100000.0, output_dir: str = "reporting/exports"):
        self.research_agent = ResearchAgent()
        self.strategy_agent = StrategyAgent()
        self.trading_agent = TradingAgent(initial_cash=initial_cash)
        self.universe_agent = UniverseSelectionAgent(research_agent=self.research_agent)
        self.report_generator = ReportGenerator(output_dir=output_dir)
        self.results = {"success": [], "failure": []}

    def run_full_pipeline(self, tickers: Optional[List[str]] = None, max_stocks: int = 5, start_date: str = "2024-01-01", end_date: str = "2024-03-27") -> Dict[str, Any]:
        """ Executes the full pipeline for a list of tickers (dynamic or manual). """
        
        # 1. Dynamic Universe Selection
        if tickers is None:
            print(f"Orchestrator: No tickers provided. Selecting top {max_stocks} dynamically...")
            tickers = self.universe_agent.select_universe(max_stocks, start_date, end_date)
            
        if not tickers:
            print("Orchestrator: No tickers selected. Aborting pipeline.")
            return {"error": "Empty universe"}

        print(f"Orchestrator: Starting full pipeline for {len(tickers)} tickers...")
        
        all_data = []

        for ticker in tickers:
            print(f"---\nOrchestrator: Processing ticker [{ticker}]...")
            try:
                # 2. Research (Fetch & Feature)
                df = self.research_agent.research([ticker], start_date, end_date)
                
                # 2. Strategy (Signals)
                df = self.strategy_agent.get_recommendations(df)
                
                # 3. Execution (Trading & Risk)
                self.trading_agent.trade(df)
                
                # 4. Success Tracking
                self.results["success"].append(ticker)
                all_data.append(df)
                print(f"Orchestrator: [{ticker}] processed successfully.")
                
            except Exception as e:
                print(f"Orchestrator: Error processing ticker [{ticker}]: {str(e)}")
                self.results["failure"].append({"ticker": ticker, "error": str(e)})

        # 5. Reporting
        final_summary = self._consolidate_results(all_data)
        self._generate_final_report(final_summary)
        
        return final_summary

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
        # Load trade log
        log_file = summary["trade_log_path"]
        trade_log = pd.DataFrame()
        if os.path.exists(log_file):
            trade_log = pd.read_csv(log_file)
            
        # Simplified metrics for the report
        metrics = {
            "Total_Equity": f"${summary['final_portfolio']['equity']:.2f}",
            "Cash": f"${summary['final_portfolio']['cash']:.2f}",
            "Realized_PnL": f"${summary['final_portfolio']['realized_pnl']:.2f}",
            "Assets": len(summary['tickers_processed']),
            "Failures": len(summary['failures'])
        }
        
        # We need an equity curve. Since we don't have a time-series equity curve 
        # across all tickers combined here, we'll use a dummy placeholder or 
        # assume StrategyAgent's backtester would provide it.
        # For now, let's just pass a series of total equity if available.
        # In a real scenario, the portfolio should track its history.
        # For this version, let's use a flat curve representing final vs start.
        equity_series = pd.Series([100000, summary['final_portfolio']['equity']])
        
        self.report_generator.generate_html_report(metrics, trade_log, equity_series, filename="orchestrator_report.html")

if __name__ == "__main__":
    import os
    # Integration test
    orch = PipelineOrchestrator(initial_cash=100000)
    # Using real tickers to test resilience
    summary = orch.run_full_pipeline(["AAPL", "TSLA", "NONEXISTENT_TICKER"], "2024-01-01", "2024-02-01")
    print(summary)
