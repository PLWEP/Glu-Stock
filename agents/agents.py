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

    def get_recommendations(self, df: pd.DataFrame, pipeline: str = "daily") -> pd.DataFrame:
        """
        Generates signals and enriches with Institutional TP/SL levels.
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
        
        # Calculate levels for Active Signals (final_signal == 1)
        last_close = result_df['close'].iloc[-1]
        result_df['buy_price'] = last_close
        result_df['tp1'] = last_close * (1 + params["tp1"])
        result_df['tp2'] = last_close * (1 + params["tp2"])
        result_df['sl_level'] = last_close * (1 - params["sl"])
        result_df['signal_duration'] = params["duration"]
        
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
    """ Coordinates execution and risk-aware portfolio management. """
    def __init__(self, initial_cash: float = 100000.0):
        self.portfolio = Portfolio(initial_cash=initial_cash)
        self.execution_engine = ExecutionEngine()
        self.risk_manager = RiskManager()

    def trade(self, df: pd.DataFrame, shares_per_trade: Optional[int] = None):
        """
        Executes trades based on signals in df. 
        If shares_per_trade is None, uses 2% risk rule.
        """
        print("TradingAgent: Starting execution cycle...")
        
        # Chronological execution for paper trading
        df = df.sort_index(level='date')
        
        for (timestamp, ticker), row in df.iterrows():
            current_equity = self.portfolio.get_equity({ticker: row['close']})
            
            # Simple wrapper to integrate RiskManager sizing into ExecutionEngine call
            # We'll calculate sizing here if needed.
            size = shares_per_trade
            if size is None:
                size = self.risk_manager.calculate_position_size(
                    current_equity, row['close'], 0.05 # Fixed 5% SL for simplicity
                )
            
            # Use ExecutionEngine to update portfolio
            # Wrapping for a single row
            single_row_df = pd.DataFrame([row], index=pd.MultiIndex.from_tuples([(timestamp, ticker)], names=['date', 'ticker']))
            self.execution_engine.execute_signals(single_row_df, self.portfolio, shares_per_trade=size)

    def get_status(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        return {
            "cash": self.portfolio.cash,
            "equity": self.portfolio.get_equity(current_prices),
            "realized_pnl": self.portfolio.realized_pnl,
            "positions": self.portfolio.positions
        }

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
