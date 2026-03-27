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
from utils.logger import JsonLogger

class ResearchAgent:
    """ Handles data collection and feature engineering. """
    def __init__(self):
        self.data_handler = StockDataHandler()
        self.feature_engineer = FeatureEngineer()

    def research(self, tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        print(f"ResearchAgent: Fetching data for {tickers}...")
        df = self.data_handler.fetch_data(tickers, start_date, end_date)
        
        print("ResearchAgent: Adding technical indicators...")
        df = self.feature_engineer.add_indicators(df)
        df = self.feature_engineer.clean_features(df)
        return df

class StrategyAgent:
    """ Manages signal generation and strategy validation. """
    def __init__(self):
        self.strategy = TradingStrategy()
        self.backtester = VectorizedBacktester()

    def get_recommendations(self, df: pd.DataFrame, model: Optional[Any] = None) -> pd.DataFrame:
        print("StrategyAgent: Generating trading signals...")
        return self.strategy.generate_signals(df, model=model)

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

    def select_universe(self, max_stocks: int, start_date: str, end_date: str) -> List[str]:
        """
        Executes the selection pipeline:
        Metadata -> Strategic Filter -> Research -> Factor Ranking -> Selection.
        """
        print(f"UniverseSelectionAgent: Curating top {max_stocks} stocks...")
        
        # 1. Load Metadata
        all_metadata = self.universe_manager.get_idx_tickers()
        
        # 2. Strategic Filtering (Exclude Bank/BUMN)
        filtered_metadata = self.universe_manager.filter_excluded_stocks(all_metadata)
        tickers = filtered_metadata["ticker"].tolist()
        
        # 3. Orchestrate Research (Collect market data)
        # Note: We need per-ticker dataframes to pass to UniverseManager.rank_stocks
        # ResearchAgent returns a concatenated MultiIndex DataFrame.
        df_researched = self.research_agent.research(tickers, start_date, end_date)
        
        # 4. Partition data for ranking
        price_data_dict = {}
        for ticker in tickers:
            try:
                ticker_data = df_researched.xs(ticker, level="ticker")
                if not ticker_data.empty:
                    price_data_dict[ticker] = ticker_data
            except KeyError:
                continue

        # 5. Execute Multi-Factor Ranking
        top_tickers, all_scores = self.universe_manager.rank_stocks(
            filtered_metadata, 
            price_data_dict, 
            top_n=max_stocks
        )
        
        # 6. Structured Logging
        self.logger.info(
            "UniverseSelectionAgent: Curated watchlist generated",
            selected=top_tickers,
            scores=all_scores
        )
        
        print(f"UniverseSelectionAgent: Selected {top_tickers}")
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
