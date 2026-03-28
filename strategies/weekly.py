import pandas as pd
import numpy as np
import ta

class WeeklyStrategy:
    """
    Swing Trading Strategy.
    3 EMA T-Alignment + RSI + MACD + Pairs Trading Logic.
    """
    def generate_signals(self, df: pd.DataFrame, paper_trading: bool = False) -> pd.DataFrame:
        if df.empty: return df
        
        # 1. 3 EMA (3, 10, 21)
        df['ema3'] = df['close'].ewm(span=3).mean()
        df['ema10'] = df['close'].ewm(span=10).mean()
        df['ema21'] = df['close'].ewm(span=21).mean()
        
        # 2. RSI (50-60 zone)
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        
        # 3. MACD
        macd = ta.trend.MACD(df['close'])
        df['macd_diff'] = macd.macd_diff()
        df['macd'] = macd.macd()
        
        # 4. Standard Swing Signal (Long-Only for Live)
        df['final_signal'] = 0
        df['final_score'] = 0.5
        
        trend_up = (df['ema3'] > df['ema10']) & (df['ema10'] > df['ema21'])
        rsi_zone = (df['rsi'] >= 50) & (df['rsi'] <= 60)
        macd_cross = (df['macd_diff'] > 0) & (df['macd'] > 0)
        
        long_condition = trend_up & rsi_zone & macd_cross
        df.loc[long_condition, 'final_signal'] = 1
        df.loc[long_condition, 'final_score'] = 0.9
        
        # 5. Pairs Trading Logic (Demeaned Return) - Placeholder for multi-ticker logic
        # For a single ticker, we'll store signal for audit if paper_trading
        if paper_trading:
            # Simulated Short for mispricing (Z-score > 2)
            # This would normally require a second ticker, but we'll mark it as potential Short canddiate
            df['short_porsi'] = 0
            df.loc[df['rsi'] > 75, 'short_porsi'] = -1
            
        # Stop Loss (Liquidasi saat MA1 <= MA2)
        exit_condition = (df['ema3'] <= df['ema10'])
        df.loc[exit_condition, 'final_signal'] = 0
        
        return df
