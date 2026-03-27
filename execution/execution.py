import os
import csv
import pandas as pd
from typing import Dict, Any
from portfolio.portfolio import Portfolio
from utils.alerts import send_telegram_alert

class ExecutionEngine:
    """
    Simulates paper trading execution by translating signals into portfolio updates.
    Maintains a CSV log of all trades.
    """

    def __init__(self, log_file: str = "execution/trade_log.csv"):
        self.log_file = log_file
        self._initialize_log()

    def _initialize_log(self):
        """ Ensure the log file exists and has headers. """
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "ticker", "action", "shares", "price", "status"])

    def _log_trade(self, timestamp: Any, ticker: str, action: str, shares: float, price: float, status: str):
        """ Standard logging for trade actions. """
        with open(self.log_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, ticker, action, shares, price, status])

    def execute_signals(self, df: pd.DataFrame, portfolio: Portfolio, shares_per_trade: float = 100):
        """
        Processes signals in the DataFrame and executes trades against the Portfolio.
        Expects index: ['date', 'ticker'] and column: 'final_signal'
        """
        if df.empty or 'final_signal' not in df.columns:
            return

        # Sort by date for proper chronological execution
        df = df.sort_index(level='date')

        for (timestamp, ticker), row in df.iterrows():
            signal = row['final_signal']
            current_shares = portfolio.positions.get(ticker, {}).get("shares", 0.0)
            price = row['close']

            # Execution Logic
            # 1. Open Long (Buy)
            if signal == 1 and current_shares == 0:
                success = portfolio.update_position(ticker, shares_per_trade, price, "BUY")
                status = "SUCCESS" if success else "FAILED"
                self._log_trade(timestamp, ticker, "BUY", shares_per_trade, price, status)
                
                # Telegram Alert on successful BUY
                if success:
                    alert_msg = f"📈 *BUY ORDER EXECUTED*\n*Ticker:* {ticker}\n*Shares:* {shares_per_trade}\n*Price:* {price:,.2f}"
                    send_telegram_alert(alert_msg)

            # 2. Close Long (Sell)
            elif (signal == 0 or signal == -1) and current_shares > 0:
                success = portfolio.update_position(ticker, current_shares, price, "SELL")
                status = "SUCCESS" if success else "FAILED"
                self._log_trade(timestamp, ticker, "SELL", current_shares, price, status)

if __name__ == "__main__":
    # Quick sanity check
    from portfolio.portfolio import Portfolio
    
    p = Portfolio(10000)
    engine = ExecutionEngine("tmp_trade_log.csv")
    
    dates = pd.date_range("2024-01-01", periods=2)
    df = pd.DataFrame({
        'close': [150, 160],
        'final_signal': [1, 0]
    }, index=pd.MultiIndex.from_tuples([(dates[0], 'AAPL'), (dates[1], 'AAPL')], names=['date', 'ticker']))
    
    engine.execute_signals(df, p, shares_per_trade=10)
    print(f"Portfolio cash: {p.cash}")
