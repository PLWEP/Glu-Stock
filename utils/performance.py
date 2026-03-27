import pandas as pd
from typing import List, Dict, Any

def calculate_performance_metrics(trades: List[Dict[str, Any]], snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates institutional-grade performance metrics from raw list of trades and portfolio snapshots.
    Handles empty data safely and avoids division by zero.
    """
    
    # Initialize zeroed metrics
    metrics = {
        "total_trades": 0,
        "win_rate": 0.0,
        "total_return": 0.0,
        "average_win": 0.0,
        "average_loss": 0.0,
        "max_drawdown": 0.0
    }

    # 1. Total return from snapshots
    if snapshots:
        df_snap = pd.DataFrame(snapshots)
        if not df_snap.empty and 'equity' in df_snap.columns:
            # Sort by date
            df_snap = df_snap.sort_values(by='date')
            initial_equity = df_snap.iloc[0]['equity']
            final_equity = df_snap.iloc[-1]['equity']
            
            if initial_equity > 0:
                metrics["total_return"] = (final_equity - initial_equity) / initial_equity
            
            # Max Drawdown
            equity_curve = df_snap['equity']
            running_peak = equity_curve.cummax()
            drawdowns = (running_peak - equity_curve) / running_peak
            metrics["max_drawdown"] = drawdowns.max()

    # 2. Trade statistics from trades (only closed trades with status 'CLOSED' or having 'pnl')
    if trades:
        # Filter for realized PnL (either status='CLOSED' or has a 'pnl' key > 0 | < 0)
        realized_trades = [t for t in trades if t.get('status') == 'CLOSED' or t.get('pnl', 0) != 0]
        
        metrics["total_trades"] = len(realized_trades)
        
        if metrics["total_trades"] > 0:
            winners = [t['pnl'] for t in realized_trades if t['pnl'] > 0]
            losers = [t['pnl'] for t in realized_trades if t['pnl'] < 0]
            
            metrics["win_rate"] = len(winners) / metrics["total_trades"]
            
            if len(winners) > 0:
                metrics["average_win"] = sum(winners) / len(winners)
                
            if len(losers) > 0:
                metrics["average_loss"] = sum(losers) / len(losers)

    return metrics

if __name__ == "__main__":
    # Test cases
    dummy_trades = [
        {"pnl": 1000, "status": "CLOSED"},
        {"pnl": -500, "status": "CLOSED"},
        {"pnl": 2000, "status": "CLOSED"}
    ]
    dummy_snaps = [
        {"date": "2024-01-01", "equity": 1000},
        {"date": "2024-01-02", "equity": 1200},
        {"date": "2024-01-03", "equity": 1100},
        {"date": "2024-01-04", "equity": 1500}
    ]
    print(calculate_performance_metrics(dummy_trades, dummy_snaps))
