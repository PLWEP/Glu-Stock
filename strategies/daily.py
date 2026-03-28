import pandas as pd
import numpy as np

class DailyStrategy:
    """
    Day Trading / Scalping Strategy.
    Pivot Support/Resistance + Donchian Channel + VWAP.
    """
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        
        # 1. VWAP Calculation
        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
        
        # 2. Pivot Points (Using previous day/period)
        # Assuming df is sorted by date
        df['prev_high'] = df['high'].shift(1)
        df['prev_low'] = df['low'].shift(1)
        df['prev_close'] = df['close'].shift(1)
        
        df['pivot'] = (df['prev_high'] + df['prev_low'] + df['prev_close']) / 3
        df['r1'] = (2 * df['pivot']) - df['prev_low']
        df['s1'] = (2 * df['pivot']) - df['prev_high']
        
        # 3. Donchian Channel
        df['donchian_up'] = df['high'].rolling(window=20).max()
        df['donchian_down'] = df['low'].rolling(window=20).min()
        
        # 4. Signal Logic
        df['final_signal'] = 0
        df['final_score'] = 0.5 # Default neutral
        
        # Long if Price > Pivot AND Price > VWAP
        long_condition = (df['close'] > df['pivot']) & (df['close'] > df['vwap'])
        df.loc[long_condition, 'final_signal'] = 1
        df.loc[long_condition, 'final_score'] = 0.8
        
        # Exit (Sell) if price hits Resistance R1
        exit_condition = (df['close'] >= df['r1'])
        df.loc[exit_condition, 'final_signal'] = 0 # Close position
        
        return df
