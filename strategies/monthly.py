import pandas as pd
import numpy as np

class MonthlyStrategy:
    """
    Position Trading Strategy.
    Price Momentum (12m - 1m) + Low-Volatility Anomaly + Value (B/P).
    """
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 252: return df
        
        # 1. Price-Momentum (12m - 1m skip latest month)
        df['mom_12m_1m'] = df['close'].shift(21) / df['close'].shift(252) - 1
        
        # 2. Low-Volatility (126d - 252d stdev)
        df['volatility_252d'] = df['close'].pct_change().rolling(252).std()
        
        # 3. Value Metric (Simplified: Price vs 52w Avg as proxy if B/P not ready)
        # In production, this would use Fundamental Data (ROE/Laba) passed from Universe.
        df['ma200'] = df['close'].rolling(200).mean()
        df['ma20_trail'] = df['close'].rolling(20).mean() # Trailing stop
        
        # 4. Signal Logic
        df['final_signal'] = 0
        
        # LONG: Price > MA200 AND Momentum > 10% AND Low Volatility
        low_vol = df['volatility_252d'] < df['volatility_252d'].rolling(252).mean()
        long_condition = (df['close'] > df['ma200']) & (df['mom_12m_1m'] > 0.10) & low_vol
        
        df.loc[long_condition, 'final_signal'] = 1
        
        # Exit (Trailing)
        df.loc[df['close'] < df['ma20_trail'], 'final_signal'] = 0
        
        return df
