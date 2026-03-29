import numpy as np
import pandas as pd
from typing import List, Dict, Any

class MonteCarloSimulator:
    """
    Simulates thousands of randomized equity paths based on historical trade outcomes.
    Helps estimate Risk of Ruin and Worst-Case Drawdowns.
    """

    def __init__(self, trades: List[Dict[str, Any]], num_simulations: int = 1000):
        self.pnls = [t.get('pnl', 0) for t in trades if t.get('pnl') is not None]
        self.num_simulations = num_simulations

    def run_simulation(self, initial_equity: float = 100000000.0) -> Dict[str, Any]:
        """
        Runs the simulation and returns statistical summaries.
        """
        if not self.pnls:
            return {"error": "No trade data provided for simulation"}

        all_paths = []
        max_drawdowns = []
        ruin_count = 0
        ruin_threshold = initial_equity * 0.8 # 20% loss

        for _ in range(self.num_simulations):
            # Bootstrap: Randomly sample trades with replacement
            sampled_pnls = np.random.choice(self.pnls, size=len(self.pnls), replace=True)
            
            # Generate equity curve
            equity_path = np.cumsum(sampled_pnls) + initial_equity
            all_paths.append(equity_path)
            
            # Calculate Max Drawdown for this path
            path_series = pd.Series(equity_path)
            rolling_max = path_series.cummax()
            drawdowns = (path_series - rolling_max) / rolling_max
            max_drawdowns.append(abs(drawdowns.min()))
            
            # Check for Ruin
            if any(equity_path < ruin_threshold):
                ruin_count += 1

        return {
            "num_trades_simulated": len(self.pnls),
            "expected_pnl": np.mean([p[-1] - initial_equity for p in all_paths]),
            "median_max_drawdown": np.median(max_drawdowns),
            "worst_case_drawdown": np.max(max_drawdowns),
            "risk_of_ruin_pct": (ruin_count / self.num_simulations) * 100,
            "confidence_interval_95": np.percentile([p[-1] for p in all_paths], [2.5, 97.5]).tolist()
        }
