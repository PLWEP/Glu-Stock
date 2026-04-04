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
from utils.firebase_handler import FirebaseHandler
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

        # For Daily Basket Trading, we increase max_stocks proportionally
        actual_max = max_stocks * 3 if pipeline == "daily" else max_stocks
        top_tickers, _ = self.universe_manager.rank_stocks(global_pool[global_pool["ticker"].isin(candidates)], price_data_dict, top_n=actual_max)
        return top_tickers

class TradingAgent:
    """ Handles execution with multi-level position sizing (Fixed, Volatility, Kelly). """
    def __init__(self, initial_cash: float = None):
        self.config = ConfigLoader().get_config()
        self.cash = initial_cash or self.config.get("initial_cash", 100000000.0)
        self.execution_engine = ExecutionEngine()
        self.risk_manager = RiskManager()
        self.db = FirebaseHandler(ConfigLoader().get_firebase_config())
        
        self.portfolios: Dict[str, Portfolio] = {}
        strat_settings = self.config.get("strategies", {})
        
        for name, settings in strat_settings.items():
            cap = self.cash * settings.get("allocation_pct", 0.33)
            p = Portfolio(name=name, initial_cash=cap)
            if not p.load_state(): p.save_state()
            self.portfolios[name] = p

    def rebalance(self, target_exposures: Dict[str, float], price_data_dict: Dict[str, pd.DataFrame], pipeline: str = "daily"):
        """
        Institutional Rebalancing: Applies ARP and conviction-based sizing.
        target_exposures: Dict {ticker: conviction_level [-1, 1]}
        """
        portfolio = self.portfolios.get(pipeline.lower())
        if not portfolio or not target_exposures: return

        # 1. Calculate ARP Weights for the active basket
        arp_weights = self.risk_manager.calculate_arp_weights(price_data_dict)
        
        # 2. Iterate and Adjust Positions
        for ticker, conviction in target_exposures.items():
            last_price = price_data_dict[ticker]['close'].iloc[-1]
            arp_weight = arp_weights.get(ticker, 0)
            
            # Target IDR = Total Equity * ARP_Weight * Conviction_Strength
            # (Conviction determines how much of the allocated risk weight to use)
            target_value = portfolio.total_equity * arp_weight * abs(conviction)
            current_value = portfolio.positions.get(ticker, {}).get("shares", 0) * last_price
            
            diff_value = target_value - current_value
            action = "BUY" if diff_value > 0 else "SELL"
            
            # Conviction direction matters
            if conviction < 0 and current_value > 0:
                action = "SELL"
                diff_value = -current_value # Exit current bullish position
                
            shares_diff = abs(int(diff_value / last_price))
            if shares_diff <= 0: continue

            if self.execution_engine.execute(ticker, action, shares_diff, last_price):
                portfolio.update_position(ticker, shares_diff, last_price, action)
        
        portfolio.save_state()
