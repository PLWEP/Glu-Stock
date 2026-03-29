import pandas as pd
from typing import List, Dict, Any, Optional
from data.data import StockDataHandler
from features.features import FeatureEngineer
from portfolio.portfolio import Portfolio
from execution.execution import ExecutionEngine
from risk.risk import RiskManager
from data.universe import UniverseManager
from strategies.daily import DailyStrategy
from strategies.weekly import WeeklyStrategy
from strategies.monthly import MonthlyStrategy
from utils.logger import JsonLogger
from utils.config import ConfigLoader
from utils.ml_predictor import MLPredictor
from agents.fundamental import FundamentalAgent
from utils.cnn_predictor import CNNPredictor

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
    """ Manages signal generation with ML and ATR logic. """
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.ml_predictor = MLPredictor()
        self.cnn_predictor = CNNPredictor()
        self.risk_manager = RiskManager()
        self.pipelines = {
            "daily": DailyStrategy(),
            "weekly": WeeklyStrategy(),
            "monthly": MonthlyStrategy()
        }

    def get_recommendations(self, df: pd.DataFrame, pipeline: str = "daily") -> pd.DataFrame:
        strategy = self.pipelines[pipeline]
        result_df = strategy.generate_signals(df)
        
        if result_df.empty: return result_df

        strat_config = self.config.get("strategies", {}).get(pipeline.lower(), {})
        min_ml_conf = strat_config.get("min_ml_confidence", 0.5)
        
        # 1. ENSEMBLE INTELLIGENCE CHECK
        result_df['ml_confidence'] = self.ml_predictor.predict_proba(result_df)
        
        # Mapping for CNN horizon
        cnn_horizon = "daily_t2" if pipeline == "daily" else ("weekly_t5" if pipeline == "weekly" else "monthly_t30")
        result_df['cnn_confidence'] = self.cnn_predictor.predict(result_df, horizon=cnn_horizon)
        
        # 2. ATR Trailing Stop
        result_df['atr_stop'] = result_df.apply(lambda x: self.risk_manager.get_atr_trailing_stop(x['close'], x.get('atr', 0), multiplier=strat_config.get('atr_multiplier', 3.0)), axis=1)
        
        # 3. Vectorized Recommendation
        result_df['buy_level'] = result_df['close']
        result_df['tp1'] = result_df['close'] * (1 + strat_config.get("tp1_pct", 0.01))
        result_df['sl_level'] = result_df['close'] * (1 - strat_config.get("sl_pct", 0.01))
        result_df['recommendation'] = result_df['final_signal'].map({1: "BUY", -1: "SELL", 0: "HOLD"})

        # 4. Intelligence Filter (Dual Brain Ensemble)
        intel_enabled = self.config.get("intelligence", {}).get("enabled", False)
        if intel_enabled:
            # Signal MUST have support from either RF or CNN, or a weighted ensemble
            # For now, we use a conservative 'AND' logic for the 🧠 badge, but 'OR' with high threshold for execution
            is_buy = (result_df['recommendation'] == "BUY")
            
            # Require at least one brain to be high confidence, or both to be decent
            # Weighted average logic (60% CNN / 40% RF as CNN is SOTA)
            ensemble_score = (result_df['cnn_confidence'] * 0.6) + (result_df['ml_confidence'] * 0.4)
            result_df['ensemble_confidence'] = ensemble_score
            
            low_conf_mask = is_buy & (ensemble_score < min_ml_conf)
            result_df.loc[low_conf_mask, 'recommendation'] = "HOLD"
            result_df.loc[low_conf_mask, 'final_signal'] = 0

        return result_df

class UniverseSelectionAgent:
    """ Autonomous agent with Fundamental filtering. """
    def __init__(self, research_agent: Optional[ResearchAgent] = None):
        self.config = ConfigLoader().get_config()
        self.research_agent = research_agent or ResearchAgent()
        self.fundamental_agent = FundamentalAgent()
        self.universe_manager = UniverseManager()
        self.logger = JsonLogger(log_file="logs/universe_selection.log")

    def select_universe(self, max_stocks: int, start_date: str, end_date: str, pipeline: str = "daily") -> List[str]:
        all_metadata = self.universe_manager.get_idx_tickers()
        global_pool = self.universe_manager.filter_global(all_metadata)
        tickers = global_pool["ticker"].tolist()

        intel_enabled = self.config.get("intelligence", {}).get("enabled", False)
        if intel_enabled and pipeline in ["weekly", "monthly"]:
            intel_data = self.fundamental_agent.analyze_tickers(tickers[:50])
            tickers = [t for t, data in intel_data.items() if data.get("passed", False)]
            if not tickers: tickers = global_pool["ticker"].tolist()

        price_df = self.research_agent.research(tickers, start_date, end_date, interval="1d")
        price_data_dict = self.universe_manager.partition_price_data(price_df, tickers)

        if pipeline == "daily": candidates = self.universe_manager.filter_daily(tickers, price_data_dict)
        elif pipeline == "weekly": candidates = self.universe_manager.filter_weekly(tickers, price_data_dict)
        else: candidates = tickers

        top_tickers, _ = self.universe_manager.rank_stocks(global_pool[global_pool["ticker"].isin(candidates)], price_data_dict, top_n=max_stocks)
        return top_tickers

class TradingAgent:
    """ Handles execution with multi-level position sizing (Fixed, Volatility, Kelly). """
    def __init__(self, initial_cash: float = None):
        self.config = ConfigLoader().get_config()
        self.cash = initial_cash or self.config.get("initial_cash", 100000000.0)
        self.execution_engine = ExecutionEngine()
        self.risk_manager = RiskManager()
        self.db = TradingDatabase()
        
        self.portfolios: Dict[str, Portfolio] = {}
        strat_settings = self.config.get("strategies", {})
        
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
        action = last_row.get('recommendation', 'HOLD')
        
        # 1. Trailing Stop Exit Check (Safety First)
        if ticker in portfolio.positions:
            if last_row['close'] < last_row.get('atr_stop', 0):
                action = "SELL"

        if action == "HOLD": return

        if action == "BUY":
            # 2. ADVANCED POSITION SIZING
            risk_cfg = self.config.get("risk", {})
            mode = risk_cfg.get("position_sizing_mode", "FIXED").upper()
            risk_pct = risk_cfg.get("risk_per_trade_pct", 0.01)
            
            # Re-sync RiskManager with local config
            self.risk_manager.risk_per_trade = risk_pct
            
            if mode == "VOLATILITY":
                shares = self.risk_manager.calculate_volatility_adjusted_size(
                    portfolio.total_equity, last_row['close'], 
                    last_row.get('atr', 0), multiplier=risk_cfg.get('atr_multiplier', 2.0)
                )
            elif mode == "KELLY":
                stats = self.db.get_performance_stats()
                shares = self.risk_manager.calculate_kelly_size(
                    portfolio.total_equity, last_row['close'],
                    stats['win_rate'], stats['win_loss_ratio'], 
                    fraction=risk_cfg.get('kelly_fraction', 0.5)
                )
            else: # FIXED FRACTIONAL
                shares = self.risk_manager.calculate_fixed_fractional_size(
                    portfolio.total_equity, last_row['close'], 
                    self.config['strategies'][pipeline.lower()]['sl_pct']
                )

            # Safeguard: Never trade more than available cash
            max_shares = int(portfolio.available_to_trade / last_row['close'])
            shares = min(shares, max_shares)
        else:
            shares = portfolio.positions.get(ticker, {}).get("shares", 0)

        if shares <= 0: return

        if self.execution_engine.execute(ticker, action, shares, last_row['close']):
            portfolio.update_position(ticker, shares, last_row['close'], action)
            portfolio.save_state()
