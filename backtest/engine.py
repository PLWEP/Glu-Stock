import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from data.data import StockDataHandler
from features.features import FeatureEngineer
from strategies.daily import DailyStrategy
from strategies.weekly import WeeklyStrategy
from strategies.monthly import MonthlyStrategy
from utils.performance import calculate_performance_metrics
from data.backtest_db import BacktestRegistry

class HistoricalBacktester:
    """
    Simulates trading strategies on historical data with OOS support.
    Includes realistic 0.3% transaction cost.
    """

    def __init__(self, initial_cash: float = 100000000.0, fee_pct: float = 0.003):
        self.initial_cash = initial_cash
        self.fee_pct = fee_pct
        self.data_handler = StockDataHandler()
        self.feature_engineer = FeatureEngineer()
        self.registry = BacktestRegistry()
        self.strategies = {
            "daily": DailyStrategy(),
            "weekly": WeeklyStrategy(),
            "monthly": MonthlyStrategy()
        }

    def run_backtest(self, ticker: str, start_date: str, end_date: str, 
                     pipeline: str = "daily", oos_split: float = 0.8) -> Dict[str, Any]:
        """
        Runs a backtest for a single ticker.
        oos_split: Fraction of data used for In-Sample (IS) training/fitting.
        """
        # 1. Fetch & Engineer Data
        interval = "1d" # Default
        if pipeline == "daily":
            # Yahoo limits 15m to 60 days. Switch to 1h if range is longer.
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            days_diff = (end_dt - start_dt).days
            
            if days_diff <= 59:
                interval = "15m"
            elif days_diff <= 729:
                interval = "1h"
                print(f"[INFO] Backtester: Range {days_diff}d > 59d. Switching to 1h interval for {ticker}.")
            else:
                interval = "1d"
                print(f"[WARNING] Backtester: Range {days_diff}d > 720d! Switching to 1d interval for {ticker}.")
        
        df = self.data_handler.fetch_data([ticker], start_date, end_date, interval=interval)
        
        if df.empty: 
            return {"error": f"No data found for {ticker} ({interval} {start_date} to {end_date})"}

        df = self.feature_engineer.add_indicators(df)
        df = self.feature_engineer.clean_features(df)
        
        if df.empty: 
            return {"error": f"Calculated features resulted in empty dataset for {ticker}. Need more warm-up data?"}

        # 2. OOS Split
        split_idx = int(len(df) * oos_split)
        is_df = df.iloc[:split_idx]
        oos_df = df.iloc[split_idx:]
        
        # 3. Generate Signals
        strategy = self.strategies[pipeline]
        signals_df = strategy.generate_signals(df) # Full run then split for clarity
        
        # 4. Simulation Engine
        results = {
            "is": self._simulate(signals_df.iloc[:split_idx]),
            "oos": self._simulate(signals_df.iloc[split_idx:])
        }
        
        # 5. Log to Registry
        self.registry.log_backtest(pipeline, ticker, results)
        
        return results

    def _simulate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """ Core simulation loop for signals. """
        cash = self.initial_cash
        equity = cash
        positions = 0
        trades = []
        equity_history = []
        
        for i in range(len(df)):
            row = df.iloc[i]
            signal = row.get('final_signal', 0)
            price = row['close']
            
            # Exit Logic
            if positions > 0 and signal == -1:
                # Sell everything
                val = positions * price * (1 - self.fee_pct)
                trades.append({
                    "ticker": "BTEST", "entry_date": "N/A", "exit_date": str(row.name),
                    "pnl": val - (positions * entry_price),
                    "status": "CLOSED"
                })
                cash += val
                positions = 0
                
            # Entry Logic
            elif positions == 0 and signal == 1:
                # Buy Max
                entry_price = price * (1 + self.fee_pct)
                positions = cash // entry_price
                cash -= positions * entry_price
                
            equity = cash + (positions * price)
            equity_history.append({"date": str(row.name), "equity": equity})
            
        metrics = calculate_performance_metrics(trades, equity_history)
        return {
            "metrics": metrics,
            "equity_history": equity_history,
            "trade_count": len(trades)
        }
