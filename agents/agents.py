import pandas as pd
from typing import List, Dict, Any, Optional
from data.data import StockDataHandler
from features.features import FeatureEngineer
from strategies.strategy import TradingStrategy
from backtesting.backtest import VectorizedBacktester
from portfolio.portfolio import Portfolio
from execution.execution import ExecutionEngine
from risk.risk import RiskManager
from data.universe import UniverseManager
from strategies.daily import DailyStrategy
from strategies.weekly import WeeklyStrategy
from strategies.monthly import MonthlyStrategy
from utils.logger import JsonLogger

class ResearchAgent:
    """ Handles data collection and feature engineering. """
    def __init__(self):
        self.data_handler = StockDataHandler()
        self.feature_engineer = FeatureEngineer()

    def research(self, tickers: List[str], start_date: str, end_date: str, interval: str = "1d") -> pd.DataFrame:
        """ Fetches and preprocesses stock data with multi-interval support. """
        print(f"ResearchAgent: Fetching data for {tickers} (interval={interval})...")
        df = self.data_handler.fetch_data(tickers, start_date, end_date, interval=interval)
        
        print("ResearchAgent: Adding technical indicators...")
        df = self.feature_engineer.add_indicators(df)
        df = self.feature_engineer.clean_features(df)
        return df

class StrategyAgent:
    """ Manages signal generation across Daily, Weekly, and Monthly pipelines. """
    def __init__(self):
        self.pipelines = {
            "daily": DailyStrategy(),
            "weekly": WeeklyStrategy(),
            "monthly": MonthlyStrategy()
        }
        self.backtester = VectorizedBacktester()

    def get_recommendations(self, df: pd.DataFrame, pipeline: str = "daily", return_full: bool = True) -> pd.DataFrame:
        """
        Generates signals and enriches with Institutional TP/SL levels (Vectorized).
        """
        strategy = self.pipelines[pipeline]
        result_df = strategy.generate_signals(df)
        
        if result_df.empty: return result_df

        # Risk Parameter Mapping
        risk_params = {
            "daily": {"tp1": 0.01, "tp2": 0.02, "sl": 0.01, "duration": "1 Day"},
            "weekly": {"tp1": 0.03, "tp2": 0.05, "sl": 0.03, "duration": "1 Week"},
            "monthly": {"tp1": 0.10, "tp2": 0.20, "sl": 0.07, "duration": "1-3 Months"}
        }
        
        params = risk_params.get(pipeline.lower(), risk_params["daily"])
        
        # Vectorized Level Calculation
        result_df['buy_level'] = result_df['close']
        result_df['tp1'] = result_df['close'] * (1 + params["tp1"])
        result_df['tp2'] = result_df['close'] * (1 + params["tp2"])
        result_df['sl_level'] = result_df['close'] * (1 - params["sl"])
        result_df['signal_duration'] = params["duration"]
        
        # Standardize for Orchestrator report naming
        result_df['recommendation'] = result_df['final_signal'].map({1: "BUY", -1: "SELL", 0: "HOLD"})

        return result_df

    def validate_strategy(self, df: pd.DataFrame) -> Dict[str, Any]:
        print("StrategyAgent: Validating strategy with backtest...")
        # Assume df already has signals
        self.backtester.run_backtest(df)
        return self.backtester.get_metrics()

class UniverseSelectionAgent:
    """ 
    Autonomous agent for dynamic universe curation and ranking.
    Orchestrates filtering and data-driven scoring.
    """
    def __init__(self, research_agent: Optional[ResearchAgent] = None):
        self.research_agent = research_agent or ResearchAgent()
        self.universe_manager = UniverseManager()
        self.logger = JsonLogger(log_file="logs/universe_selection.log")

    def select_universe(self, max_stocks: int, start_date: str, end_date: str, pipeline: str = "daily") -> List[str]:
        """ Specialized selection flow with pipeline-specific filtering. """
        # 1. Global Filter (Metadata Level)
        all_metadata = self.universe_manager.get_idx_tickers()
        global_pool = self.universe_manager.filter_global(all_metadata)
        tickers = global_pool["ticker"].tolist()

        # 2. Research (Technical Data)
        print(f"UniverseSelectionAgent: Initial technical scan for {len(tickers)} stocks...")
        price_df = self.research_agent.research(tickers, start_date, end_date, interval="1d")
        price_data_dict = self.universe_manager.partition_price_data(price_df, tickers)

        # 3. Pipeline Filter
        if pipeline == "daily":
            candidates = self.universe_manager.filter_daily(tickers, price_data_dict)
        elif pipeline == "weekly":
            candidates = self.universe_manager.filter_weekly(tickers, price_data_dict)
        elif pipeline == "monthly":
            # Tiered Monthly: Trend Filter -> Fundamental Fetch -> Final Selection
            # First pass: Technicals (MA200)
            tech_candidates = [t for t, df in price_data_dict.items() if len(df) >= 200 and df["close"].iloc[-1] > df["close"].rolling(200).mean().iloc[-1]]
            
            print(f"UniverseSelectionAgent: Fetching fundamentals for {len(tech_candidates)} momentum candidates...")
            fundamentals = {}
            import yfinance as yf
            for t in tech_candidates[:50]: # Limit to top 50 to avoid timeout
                try:
                    info = yf.Ticker(t).info
                    fundamentals[t] = {
                        "returnOnEquity": info.get("returnOnEquity", 0),
                        "netIncomeGrowth": info.get("netIncomeToCommon", 0) # Proxy for laba
                    }
                except: continue
                
            candidates = self.universe_manager.filter_monthly(tech_candidates, price_data_dict, fundamentals)
        else:
            candidates = tickers

        # 4. Rank and Select
        print(f"UniverseSelectionAgent: Ranking {len(candidates)} candidates...")
        top_tickers, _ = self.universe_manager.rank_stocks(global_pool[global_pool["ticker"].isin(candidates)], price_data_dict, top_n=max_stocks)
        
        self.logger.info("UniverseSelectionAgent: Selection complete", selected=top_tickers)
        return top_tickers

class TradingAgent:
    """ Coordinates execution and risk-aware portfolio management for multiple strategies. """
    def __init__(self, initial_cash: float = 100000.0, allocations: Optional[Dict[str, float]] = None):
        self.execution_engine = ExecutionEngine()
        self.risk_manager = RiskManager()
        
        # Default allocations if none provided: 40% Daily, 30% Weekly, 30% Monthly
        if allocations is None:
            allocations = {
                "daily": initial_cash * 0.4, 
                "weekly": initial_cash * 0.3, 
                "monthly": initial_cash * 0.3
            }
            
        self.portfolios: Dict[str, Portfolio] = {}
        for name, cap in allocations.items():
            p = Portfolio(name=name, initial_cash=cap)
            # Try to load existing state for continuity
            if not p.load_state():
                print(f"TradingAgent: Initializing new portfolio for [{name}] with {cap}")
                p.save_state()
            else:
                print(f"TradingAgent: Loaded existing {name} portfolio state.")
            self.portfolios[name] = p

    def trade(self, df: pd.DataFrame, pipeline: str = "daily", shares_per_trade: Optional[int] = None):
        """ Executes trades using the strategy-specific isolated portfolio. """
        portfolio = self.portfolios.get(pipeline.lower())
        if not portfolio:
            print(f"TradingAgent: No portfolio found for pipeline [{pipeline}]")
            return

        ticker = df.index.get_level_values('ticker')[0] if isinstance(df.index, pd.MultiIndex) else "UNKNOWN"
        last_row = df.iloc[-1]
        action = "BUY" if last_row['final_signal'] == 1 else ("SELL" if last_row['final_signal'] == -1 else "HOLD")
        
        if action == "HOLD":
            return

        # Profit Freezing Enforcement
        if action == "BUY":
            # Dynamic sizing: 10% of INITIAL capacity per trade, or user provided shares
            if shares_per_trade is None:
                allocation_per_trade = portfolio.initial_capital * 0.1
                shares = self.risk_manager.calculate_position_size(allocation_per_trade, last_row['close'])
            else:
                shares = shares_per_trade
                
            # Final check against available cash (Profit Freeze aware)
            # We only allow buying with cash up to the initial_capital limit
            max_buy_shares = int(portfolio.available_to_trade / last_row['close'])
            shares = min(shares, max_buy_shares)
        else:
            # SELL logic uses current holdings
            shares = portfolio.positions.get(ticker, {}).get("shares", 0)

        if shares <= 0: return

        # Execute via Engine
        success = self.execution_engine.execute(ticker, action, shares, last_row['close'])
        if success:
            # Update Portfolio state
            portfolio.update_position(ticker, shares, last_row['close'], action)
            # Persist state immediately
            portfolio.save_state()
            
    def get_status(self, current_prices: Dict[str, float], pipeline: Optional[str] = None) -> Any:
        """ Gets status for one or all portfolios. """
        if pipeline:
            p = self.portfolios.get(pipeline.lower())
            return {"cash": p.cash, "equity": p.get_equity(current_prices), "pnl": p.realized_pnl} if p else {}
            
        return {name: {"cash": p.cash, "equity": p.get_equity(current_prices)} for name, p in self.portfolios.items()}

    def get_detailed_status(self, current_prices: Dict[str, float], pipeline: str = "daily") -> Dict[str, Any]:
        """ Generates a 'Security Firm' style portfolio summary for a specific pipeline. """
        portfolio = self.portfolios.get(pipeline.lower())
        if not portfolio: return {}

        summary = {
            "name": pipeline.upper(),
            "cash": portfolio.cash,
            "equity": portfolio.get_equity(current_prices),
            "realized_pnl": portfolio.realized_pnl,
            "unrealized_pnl": portfolio.get_unrealized_pnl(current_prices),
            "holdings": []
        }
        
        for ticker, pos in portfolio.positions.items():
            last_p = current_prices.get(ticker, pos["avg_cost"])
            shares = pos["shares"]
            avg_p = pos["avg_cost"]
            
            pnl = shares * (last_p - avg_p)
            pnl_pct = (pnl / (shares * avg_p)) * 100 if avg_p > 0 else 0
            
            summary["holdings"].append({
                "ticker": ticker,
                "lots": shares / 100,
                "shares": shares,
                "avg_price": avg_p,
                "last_price": last_p,
                "value": shares * last_p,
                "pnl": pnl,
                "pnl_pct": pnl_pct
            })
            
        return summary

if __name__ == "__main__":
    # Mini integration test
    ra = ResearchAgent()
    sa = StrategyAgent()
    ta = TradingAgent()
    
    # Simple flow
    data = ra.research(["AAPL"], "2024-01-01", "2024-02-01")
    signals = sa.get_recommendations(data)
    ta.trade(signals, shares_per_trade=10)
    
    last_price = data.iloc[-1]['close']
    print(ta.get_status({"AAPL": last_price}))
