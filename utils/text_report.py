import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from data.database import TradingDatabase
from utils.performance import calculate_performance_metrics
from utils.monte_carlo import MonteCarloSimulator

class TextReportGenerator:
    """
    Generates clean Markdown reports specifically for Telegram notifications.
    Supports periodic summaries with Statistical Pulse metrics.
    """
    
    def __init__(self):
        self.db = TradingDatabase()

    def generate_report(self, days: int, interval_name: str, candidates: List[Dict[str, Any]] = None) -> str:
        """
        Generic generator for periodic reports with Statistical Pulse.
        """
        now = datetime.now()
        start_period = now - timedelta(days=days)
        timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # 1. Fetch and Filter Data
            all_trades = self.db.get_all_trades()
            all_snaps = self.db.get_portfolio_history()
            
            period_trades = [
                t for t in all_trades 
                if datetime.fromisoformat(t['entry_date']) >= start_period
            ]
            
            period_snaps = [
                s for s in all_snaps 
                if datetime.fromisoformat(s['date']) >= start_period
            ]

            # 2. Base Header
            msg = f"🌸 *Laporan {interval_name} buat Kamu*\n"
            msg += f"🕒 Dicatat pada: {timestamp_str}\n"

            # 3. Portfolio Value Logic
            latest_equity = 0.0
            if all_snaps:
                latest_equity = all_snaps[0]['equity']
                msg += f"💰 Tabungan Kita: IDR {latest_equity:,.2f}\n"

            # 4. Handle Empty Trades Case
            if not period_trades:
                msg += "\n🌸 Hari ini Ayang belum lihat ada transaksi nih...\n"
                if candidates:
                    msg += "Tapi Ayang lagi pantau ini buat kamu:\n"
                    for c in candidates[:5]:
                        score = c.get('score', 0)
                        msg += f"- {c['ticker']} (Skor {score:.2f})\n"
                else:
                    msg += "\nSemua aman kok, jangan khawatir ya! ✨"
                return msg

            # 5. Full Report Logic (If Trades Exist)
            metrics = calculate_performance_metrics(period_trades, period_snaps if period_snaps else all_snaps[:1])
            
            msg += f"📈 Profit Kita: {metrics['total_return']*100:.2f}%\n"
            msg += f"🎯 Win Rate: {metrics['win_rate']*100:.1f}%\n"
            msg += f"📉 Penurunan (DD): {metrics['max_drawdown']*100:.1f}%\n"
            
            # 6. Statistical Pulse (Expectancy & Confidence)
            msg += f"📊 *Risk Score*: `S:{metrics['sharpe_ratio']:.2f}` | `T:{metrics['sortino_ratio']:.2f}` | `C:{metrics['calmar_ratio']:.2f}`\n"
            msg += f"🧠 *Stats Pulse*: 💰 `Ex: {metrics['expectancy']:+,.0f}` | ⚡ `Conf: {metrics['confidence']}`\n"
            
            # 7. Stress Test (Monte Carlo) - Only if enough data
            if len(period_trades) >= 10:
                mc = MonteCarloSimulator(period_trades, num_simulations=500)
                mc_res = mc.run_simulation(initial_equity=latest_equity)
                if "error" not in mc_res:
                    msg += f"🛡️ *Stress Test*: Prob. Bangkrut: `{mc_res['risk_of_ruin_pct']:.1f}%`\n"

            msg += f"\n✅ *Transaksi Kita ({len(period_trades)})*:\n"
            limit = 5 if days <= 1 else 10
            for t in period_trades[:limit]:
                status_icon = "🟢" if t['status'] == 'CLOSED' else "⚪"
                pnl_icon = "💰" if (t.get('pnl') or 0) > 0 else "📉"
                msg += f"{status_icon} {t['ticker']} | Untung: {t['pnl']:,.0f} {pnl_icon}\n"
            
            if len(period_trades) > limit:
                msg += f"_...dan {len(period_trades)-limit} lainnya ya sayang_"

            msg += "\n\n_Bot tetap waspada buat jagain tabungan kita!_ 💖"
            return msg

        except Exception as e:
            return f"📊 *{interval_name.upper()} REPORT*\n🕒 {timestamp_str}\n❌ ERROR: {str(e)}"

    def generate_daily_report(self, candidates: List[Dict[str, Any]] = None) -> str:
        return self.generate_report(1, "Daily", candidates=candidates)

    def generate_weekly_report(self, candidates: List[Dict[str, Any]] = None) -> str:
        return self.generate_report(7, "Weekly", candidates=candidates)

    def generate_monthly_report(self, candidates: List[Dict[str, Any]] = None) -> str:
        return self.generate_report(30, "Monthly", candidates=candidates)
