import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from data.database import TradingDatabase
from utils.performance import calculate_performance_metrics

class TextReportGenerator:
    """
    Generates clean Markdown reports specifically for Telegram notifications.
    Supports daily, weekly, and monthly timeframes.
    """
    
    def __init__(self):
        self.db = TradingDatabase()

    def generate_report(self, days: int, interval_name: str) -> str:
        """
        Generic generator for periodic reports.
        """
        now = datetime.now()
        start_period = now - timedelta(days=days)
        
        # 1. Fetch and Filter Data
        all_trades = self.db.get_all_trades()
        all_snaps = self.db.get_portfolio_history()
        
        # Filter trades by entry_date (ISO format)
        period_trades = [
            t for t in all_trades 
            if datetime.fromisoformat(t['entry_date']) >= start_period
        ]
        
        # Filter snapshots by date (ISO format)
        period_snaps = [
            s for s in all_snaps 
            if datetime.fromisoformat(s['date']) >= start_period
        ]

        if not period_snaps:
            return f"📊 *Glu-Stock {interval_name} Report* 📊\n❌ No data found for the last {days} days."

        # 2. Calculate Metrics
        metrics = calculate_performance_metrics(period_trades, period_snaps)
        
        # 3. Format Message
        latest_snap = period_snaps[0] # History is DESC, so first is latest
        msg = f"📊 *Glu-Stock {interval_name} Report* 📊\n"
        msg += f"📅 Period: {start_period.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}\n"
        msg += f"💰 Equity: IDR {latest_snap['equity']:,.2f}\n"
        msg += f"📈 Return: {metrics['total_return']*100:.2f}%\n"
        msg += f"🎯 Win Rate: {metrics['win_rate']*100:.1f}%\n"
        msg += f"📉 Max Drawdown: {metrics['max_drawdown']*100:.1f}%\n"
        
        # Recent trades list
        if period_trades:
            msg += f"\n✅ *Trades ({len(period_trades)})*:\n"
            # Show top 5 for daily, top 10 for weekly/monthly
            limit = 5 if days <= 1 else 10
            for t in period_trades[:limit]:
                status_icon = "🟢" if t['status'] == 'CLOSED' else "⚪"
                pnl_icon = "💰" if (t.get('pnl') or 0) > 0 else "📉"
                msg += f"{status_icon} {t['ticker']} | PnL: {t['pnl']:,.0f} {pnl_icon}\n"
            
            if len(period_trades) > limit:
                msg += f"_...and {len(period_trades)-limit} more_"
        else:
            msg += "\n⚪ *No execution signals detected this period.*"

        return msg

    def generate_daily_report(self) -> str:
        return self.generate_report(1, "Daily")

    def generate_weekly_report(self) -> str:
        return self.generate_report(7, "Weekly")

    def generate_monthly_report(self) -> str:
        return self.generate_report(30, "Monthly")

if __name__ == "__main__":
    # Quick test if data exists
    gen = TextReportGenerator()
    print(gen.generate_daily_report())
