import pandas as pd
import numpy as np

class VectorizedBacktester:
    """
    A vectorized backtesting engine for simulating trading strategies.
    Supports multi-ticker DataFrames and accounts for transaction costs.
    """

    def __init__(self, initial_capital: float = 100000, transaction_cost: float = 0.001):
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost

    def run_backtest(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Runs the backtest simulation based on the 'final_signal' column.
        Expects index: ['date', 'ticker']
        """
        if df.empty or 'final_signal' not in df.columns:
            return df

        # Ensure index is sorted
        df = df.sort_index(level=['ticker', 'date'])

        # 1. Calculate historical returns
        df['returns'] = df.groupby(level='ticker')['close'].pct_change()

        # 2. Shift signals to represent execution at next day's open/close
        # We assume the signal is generated at the close and executed at the next bar's return.
        df['strategy_signal'] = df.groupby(level='ticker')['final_signal'].shift(1)

        # 3. Calculate raw strategy returns
        df['strategy_returns'] = df['strategy_signal'] * df['returns']

        # 4. Apply transaction costs
        # Trades are detected by signal changes. 
        # Abs difference: 1 to 0 (sell/close) = 1 trade, 0 to 1 (buy) = 1 trade, 1 to -1 (flip) = 2 trades.
        df['trades'] = df.groupby(level='ticker')['final_signal'].diff().abs()
        df['cost'] = df['trades'] * self.transaction_cost
        df['strategy_returns'] = df['strategy_returns'] - df['cost']

        # 5. Calculate cumulative performance and equity curve
        # Combined across all tickers (portfolio level)
        # For simplicity, we calculate per-ticker first then average or sum.
        # Here we'll average returns assuming equal-weight allocation to active signals.
        portfolio_returns = df.groupby(level='date')['strategy_returns'].mean().fillna(0)
        
        # Equity Curve
        df_portfolio = pd.DataFrame(index=portfolio_returns.index)
        df_portfolio['returns'] = portfolio_returns
        df_portfolio['cumulative_returns'] = (1 + df_portfolio['returns']).cumprod()
        df_portfolio['equity_curve'] = df_portfolio['cumulative_returns'] * self.initial_capital
        
        self.portfolio_results = df_portfolio
        return df

    def get_metrics(self) -> dict:
        """ Calculates key performance metrics for the portfolio. """
        if not hasattr(self, 'portfolio_results'):
            return {}

        results = self.portfolio_results
        total_return = (results['equity_curve'].iloc[-1] / self.initial_capital) - 1
        
        # Annualized Sharpe Ratio (Assumes daily data, 252 days/year)
        returns = results['returns']
        if returns.std() == 0:
            sharpe = 0
        else:
            sharpe = np.sqrt(252) * returns.mean() / returns.std()

        # Max Drawdown
        equity = results['equity_curve']
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        max_drawdown = drawdown.min()

        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "final_value": equity.iloc[-1]
        }

    def get_ticker_metrics(self, df: pd.DataFrame, ticker: str) -> dict:
        """ Calculates metrics for a specific ticker from the backtest result. """
        if df.empty or ticker not in df.index.get_level_values('ticker'):
            return {"win_rate": 0, "profit_factor": 0, "trades": 0}
            
        ticker_df = df.xs(ticker, level='ticker')
        # We audit based on all bars where we have an active signal
        active_df = ticker_df[ticker_df['strategy_signal'] != 0].copy()
        
        # We still count trades to ensure some activity happened
        num_trades = ticker_df[ticker_df['trades'] != 0]['trades'].sum() / 2  # Approx total trades (entry+exit)
        
        if active_df.empty:
            return {"win_rate": 0, "profit_factor": 0, "trades": 0}
            
        # 1. Win Rate: Percentage of positive return bars while signal is active
        wins = active_df[active_df['strategy_returns'] > 0]
        win_rate = len(wins) / len(active_df)
        
        # 2. Profit Factor: Gross Profit / Gross Loss across active bars
        gross_profit = active_df[active_df['strategy_returns'] > 0]['strategy_returns'].sum()
        gross_loss = abs(active_df[active_df['strategy_returns'] < 0]['strategy_returns'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (100.0 if gross_profit > 0 else 0)
        
        return {
            "win_rate": win_rate * 100,
            "profit_factor": profit_factor,
            "trades": int(num_trades)
        }

if __name__ == "__main__":
    # Sanity check with dummy data
    dates = pd.date_range("2024-01-01", periods=10)
    df = pd.DataFrame({
        'close': [100, 101, 102, 101, 103, 104, 105, 104, 102, 101],
        'final_signal': [0, 1, 1, 1, 1, -1, -1, -1, 0, 0]
    }, index=pd.MultiIndex.from_tuples([(d, 'AAPL') for d in dates], names=['date', 'ticker']))
    
    backtester = VectorizedBacktester()
    backtester.run_backtest(df)
    print(backtester.get_metrics())
