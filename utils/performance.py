import pandas as pd
import numpy as np
from typing import List, Dict, Any

def calculate_performance_metrics(trades: List[Dict[str, Any]], snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates key performance metrics including risk-adjusted ratios (Sharpe, Sortino, Calmar).
    """
    metrics = {
        "total_return": 0.0,
        "win_rate": 0.0,
        "max_drawdown": 0.0,
        "avg_win": 0.0,
        "avg_loss": 0.0,
        "sharpe_ratio": 0.0,
        "sortino_ratio": 0.0,
        "calmar_ratio": 0.0
    }

    if not snapshots:
        return metrics

    # 1. Basic Equity Metrics
    equity_series = pd.Series([s['equity'] for s in snapshots])
    if equity_series.empty or len(equity_series) < 2:
        return metrics
        
    initial_equity = equity_series.iloc[0]
    final_equity = equity_series.iloc[-1]
    metrics["total_return"] = (final_equity / initial_equity) - 1 if initial_equity > 0 else 0.0

    # 2. Trade-based Metrics
    if trades:
        pnl_list = [t.get('pnl', 0) for t in trades if t.get('pnl') is not None]
        wins = [p for p in pnl_list if p > 0]
        losses = [p for p in pnl_list if p <= 0]
        metrics["win_rate"] = len(wins) / len(pnl_list) if pnl_list else 0.0
        metrics["avg_win"] = np.mean(wins) if wins else 0.0
        metrics["avg_loss"] = np.mean(losses) if losses else 0.0

    # 3. Max Drawdown
    rolling_max = equity_series.cummax()
    drawdowns = (equity_series - rolling_max) / rolling_max
    metrics["max_drawdown"] = abs(drawdowns.min())

    # 4. Risk-Adjusted Ratios (Requires Daily Returns)
    returns = equity_series.pct_change().dropna()
    if not returns.empty:
        # Annualized values (Assuming 252 trading days)
        avg_ret = returns.mean()
        std_dev = returns.std()
        
        # 4.1 Sharpe Ratio
        if std_dev > 0:
            metrics["sharpe_ratio"] = (avg_ret / std_dev) * np.sqrt(252)
            
        # 4.2 Sortino Ratio (Penalizes only downside volatility)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std()
        if downside_std > 0:
            metrics["sortino_ratio"] = (avg_ret / downside_std) * np.sqrt(252)
        else:
            metrics["sortino_ratio"] = metrics["sharpe_ratio"] # Fallback if no downside

        # 4.3 Calmar Ratio
        if metrics["max_drawdown"] > 0:
            # Simple annualized return assumption for Calmar
            metrics["calmar_ratio"] = metrics["total_return"] / metrics["max_drawdown"]

    return metrics
