import pandas as pd
from typing import List, Dict, Any, Optional
from data.data import StockDataHandler
from features.features import FeatureEngineer
from backtesting.backtest import VectorizedBacktester
from portfolio.portfolio import Portfolio
from execution.execution import ExecutionEngine
from risk.risk import RiskManager
from data.universe import UniverseManager
from strategies.daily import DailyStrategy
from strategies.weekly import WeeklyStrategy
from strategies.monthly import MonthlyStrategy
from utils.logger import JsonLogger
from utils.config import ConfigLoader

class ResearchAgent:
    """ Handles data collection and feature engineering. """
    def __init__(self):
        self.data_handler = StockDataHandler()
        self.feature_engineer = FeatureEngineer()

    def research(self, tickers: List[str], start_date: str, end_date: str, interval: str = "1d") -> pd.DataFrame:
        df = self.data_handler.fetch_data(tickers, start_date, end_date, interval=interval)
        df = self.feature_engineer.add_indicators(df)
        df = self.feature_engineer.clean_features(df)
        return df

class StrategyAgent:
    """ Manages signal generation across Daily, Weekly, and Monthly pipelines. """
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.pipelines = {
            "daily": DailyStrategy(),
            "weekly": WeeklyStrategy(),
            "monthly": MonthlyStrategy()
        }

    def get_recommendations(self, df: pd.DataFrame, pipeline: str = "daily") -> pd.DataFrame:
        strategy = self.pipelines[pipeline]
        result_df = strategy.generate_signals(df)
        
        if result_df.empty: return result_df

        # Strategy Parameters from Config
        strat_config = self.config.get("strategies", {}).get(pipeline.lower(), {})
        tp1 = strat_config.get("tp1_pct", 0.01)
        tp2 = strat_config.get("tp2_pct", 0.02)
        sl = strat_config.get("sl_pct", 0.01)
        duration = strat_config.get("duration", "N/A")
        
        # Vectorized Level Calculation
        result_df['buy_level'] = result_df['close']
        result_df['tp1'] = result_df['close'] * (1 + tp1)
        result_df['tp2'] = result_df['close'] * (1 + tp2)
        result_df['sl_level'] = result_df['close'] * (1 - sl)
        result_df['signal_duration'] = duration
        result_df['recommendation'] = result_df['final_signal'].map({1: "BUY", -1: "SELL", 0: "HOLD"})

        return result_df

class UniverseSelectionAgent:
    """ Autonomous agent for dynamic universe curation and ranking. """
    def __init__(self, research_agent: Optional[ResearchAgent] = None):
        self.research_agent = research_agent or ResearchAgent()
        self.universe_manager = UniverseManager()
        self.logger = JsonLogger(log_file="logs/universe_selection.log")

    def select_universe(self, max_stocks: int, start_date: str, end_date: str, pipeline: str = "daily") -> List[str]:
        all_metadata = self.universe_manager.get_idx_tickers()
        global_pool = self.universe_manager.filter_global(all_metadata)
        tickers = global_pool["ticker"].tolist()

        # Partitioned Research (Prevent yfinance timeouts)
        price_df = self.research_agent.research(tickers, start_date, end_date, interval="1d")
        price_data_dict = self.universe_manager.partition_price_data(price_df, tickers)

        if pipeline == "daily": candidates = self.universe_manager.filter_daily(tickers, price_data_dict)
        elif pipeline == "weekly": candidates = self.universe_manager.filter_weekly(tickers, price_data_dict)
        elif pipeline == "monthly":
            tech_candidates = [t for t, df in price_data_dict.items() if len(df) >= 200 and df["close"].iloc[-1] > df["close"].rolling(200).mean().iloc[-1]]
            candidates = tech_candidates[:max_stocks*2] # Simplified monthly
        else: candidates = tickers

        top_tickers, _ = self.universe_manager.rank_stocks(global_pool[global_pool["ticker"].isin(candidates)], price_data_dict, top_n=max_stocks)
        return top_tickers

class TradingAgent:
    """ Coordinates execution and risk-aware portfolio management. """
    def __init__(self, initial_cash: float = None):
        config = ConfigLoader().get_config()
        self.cash = initial_cash or config.get("initial_cash", 100000000.0)
        self.execution_engine = ExecutionEngine()
        self.risk_manager = RiskManager()
        
        self.portfolios: Dict[str, Portfolio] = {}
        strat_settings = config.get("strategies", {})
        
        for name, settings in strat_settings.items():
            cap = self.cash * settings.get("allocation_pct", 0.33)
            p = Portfolio(name=name, initial_cash=cap)
            if not p.load_state(): p.save_state()
            self.portfolios[name] = p

    def trade(self, df: pd.DataFrame, pipeline: str = "daily"):
        portfolio = self.portfolios.get(pipeline.lower())
        if not portfolio or df.empty: return

        ticker = df.index.get_level_values('ticker')[0] if isinstance(df.index, pd.MultiIndex) else "UNKNOWN"
        last_row = df.iloc[-1]
        action = "BUY" if last_row['final_signal'] == 1 else ("SELL" if last_row['final_signal'] == -1 else "HOLD")
        
        if action == "HOLD": return

        if action == "BUY":
            # 10% of INITIAL capacity per trade
            allocation = portfolio.initial_capital * 0.1
            shares = self.risk_manager.calculate_position_size(allocation, last_row['close'])
            # Profit Freeze Check
            max_shares = int(portfolio.available_to_trade / last_row['close'])
            shares = min(shares, max_shares)
        else:
            shares = portfolio.positions.get(ticker, {}).get("shares", 0)

        if shares <= 0: return

        if self.execution_engine.execute(ticker, action, shares, last_row['close']):
            portfolio.update_position(ticker, shares, last_row['close'], action)
            portfolio.save_state()
            
    def get_status(self, current_prices: Dict[str, float], pipeline: Optional[str] = None) -> Any:
        if pipeline:
            p = self.portfolios.get(pipeline.lower())
            return {"cash": p.cash, "equity": p.get_equity(current_prices), "realized_pnl": p.realized_pnl} if p else {}
        return {n: {"cash": p.cash, "equity": p.get_equity(current_prices)} for n, p in self.portfolios.items()}

    def get_detailed_status(self, current_prices: Dict[str, float], pipeline: str = "daily") -> Dict[str, Any]:
        portfolio = self.portfolios.get(pipeline.lower())
        if not portfolio: return {}
        summary = {"name": pipeline.upper(), "cash": portfolio.cash, "equity": portfolio.get_equity(current_prices), 
                   "realized_pnl": portfolio.realized_pnl, "unrealized_pnl": portfolio.get_unrealized_pnl(current_prices), "holdings": []}
        for ticker, pos in portfolio.positions.items():
            lp = current_prices.get(ticker, pos["avg_cost"])
            sh = pos["shares"]; ap = pos["avg_cost"]
            pnl = sh * (lp - ap); pp = (pnl / (sh * ap)) * 100 if ap > 0 else 0
            summary["holdings"].append({"ticker": ticker, "lots": sh / 100, "shares": sh, "avg_price": ap, "last_price": lp, "pnl": pnl, "pnl_pct": pp})
        return summary
