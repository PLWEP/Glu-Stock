import pandas as pd
import numpy as np
from typing import List, Dict, Any

def calculate_performance_metrics(trades: List[Dict[str, Any]], snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates key performance metrics from a list of trades and portfolio snapshots.
    """
    if not trades:
        return {
            "total_return": 0.0,
            "win_rate": 0.0,
            "max_drawdown": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0
        }

    # 1. Total Return
    initial_equity = snapshots[0]['equity'] if snapshots else 100000.0
    final_equity = snapshots[-1]['equity'] if snapshots else initial_equity
    total_return = (final_equity / initial_equity) - 1 if initial_equity > 0 else 0.0

    # 2. Win Rate
    pnl_list = [t.get('pnl', 0) for t in trades if t.get('pnl') is not None]
    wins = [p for p in pnl_list if p > 0]
    losses = [p for p in pnl_list if p <= 0]
    win_rate = len(wins) / len(pnl_list) if pnl_list else 0.0

    # 3. Max Drawdown
    equity_series = pd.Series([s['equity'] for s in snapshots])
    if not equity_series.empty:
        rolling_max = equity_series.cummax()
        drawdowns = (equity_series - rolling_max) / rolling_max
        max_drawdown = abs(drawdowns.min())
    else:
        max_drawdown = 0.0

    return {
        "total_return": total_return,
        "win_rate": win_rate,
        "max_drawdown": max_drawdown,
        "avg_win": np.mean(wins) if wins else 0.0,
        "avg_loss": np.mean(losses) if losses else 0.0
    }
