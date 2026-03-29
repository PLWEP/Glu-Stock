import numpy as np
from typing import Dict, List, Any
from data.database import TradingDatabase
from utils.performance import calculate_performance_metrics

class StrategyAllocator:
    """
    Dynamically rebalances capital between Daily, Weekly, and Monthly pipelines.
    Based on risk-adjusted performance (Inverse Variance / Sharpe).
    """

    def __init__(self, total_capital: float = 100000000.0):
        self.total_capital = total_capital
        self.db = TradingDatabase()

    def calculate_strategy_weights(self) -> Dict[str, float]:
        """
        Calculates optimal capital weights for each strategy cluster.
        Returns a mapping of {pipeline: weight_fraction}.
        """
        pipelines = ["daily", "weekly", "monthly"]
        all_trades = self.db.get_all_trades()
        all_snaps = self.db.get_portfolio_history()
        
        performances = {}
        for p in pipelines:
            p_trades = [t for t in all_trades if t.get('strategy', '').lower() == p]
            # Calculate metrics for this specific pipeline
            metrics = calculate_performance_metrics(p_trades, all_snaps)
            
            # Use Sharpe + Sortino as weight (must be > 0)
            score = max(0.1, metrics.get('sharpe_ratio', 0) + metrics.get('sortino_ratio', 0))
            performances[p] = score

        total_score = sum(performances.values())
        if total_score == 0:
            return {p: 1.0/len(pipelines) for p in pipelines}

        # Apply weights with min/max bounds (20% - 50%)
        weights = {}
        for p, score in performances.items():
            raw_w = score / total_score
            bounded_w = max(0.20, min(0.50, raw_w))
            weights[p] = bounded_w

        # Normalize back to 1.0
        final_sum = sum(weights.values())
        return {p: w / final_sum for p, w in weights.items()}

    def get_allocation_map(self) -> Dict[str, float]:
        """ Returns the actual IDR allocation for each cluster. """
        weights = self.calculate_strategy_weights()
        return {p: w * self.total_capital for p, w in weights.items()}
