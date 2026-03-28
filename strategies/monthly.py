import pandas as pd
import numpy as np

class MonthlyStrategy:
    """
    Position Trading Strategy.
    Price Momentum + Low-Vol Anomaly + Value Rotation.
    """
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 252: return df
        
        # 1. Price-Momentum (12m - 1m)
        # 252 days ~ 12 months, 21 days ~ 1 month
        df['mom_12m'] = df['close'].shift(21) / df['close'].shift(252) - 1
        
        # 2. Low-Volatility (126d std)
        df['volatility_126d'] = df['close'].pct_change().rolling(126).std()
        
        # 3. Trailing Stop (MA20)
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        
        # 4. Signal Logic
        df['final_signal'] = 0
        df['final_score'] = 0.5
        
        # Momentum + Above MA200 + Not extremely volatile
        mom_rank = df['mom_12m'].rolling(20).mean() # Smoothing
        low_vol = df['volatility_126d'] < df['volatility_126d'].rolling(252).mean() # Below avg vol
        
        long_condition = (df['close'] > df['ma200']) & (mom_rank > 0.1) & low_vol
        df.loc[long_condition, 'final_signal'] = 1
        df.loc[long_condition, 'final_score'] = 0.85
        
        # Trailing Stop exit
        exit_condition = (df['close'] < df['ma20'])
        df.loc[exit_condition, 'final_signal'] = 0
        
        return df
