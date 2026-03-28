import pandas as pd
import numpy as np
import ta

class WeeklyStrategy:
    """
    Swing Trading Strategy.
    3 EMA T-Alignment (3, 10, 21) + RSI + MACD.
    """
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 50: return df
        
        # 1. 3 EMA Alignment (MA3 > MA10 > MA21)
        df['ema3'] = df['close'].ewm(span=3).mean()
        df['ema10'] = df['close'].ewm(span=10).mean()
        df['ema21'] = df['close'].ewm(span=21).mean()
        
        # 2. RSI (50-60 zone focus)
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        
        # 3. MACD
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        
        # 4. Signal Logic
        df['final_signal'] = 0
        
        # LONG: EMA Alignment + RSI in 50-60 zone + MACD > Signal
        trend_up = (df['ema3'] > df['ema10']) & (df['ema10'] > df['ema21'])
        rsi_zone = (df['rsi'] >= 50) & (df['rsi'] <= 60)
        macd_up = (df['macd'] > df['macd_signal']) & (df['macd'] > 0)
        
        df.loc[trend_up & rsi_zone & macd_up, 'final_signal'] = 1
        
        # Exit (Liquidasi) if EMA trend closes
        exit_condition = (df['ema3'] <= df['ema10'])
        df.loc[exit_condition, 'final_signal'] = 0
        
        return df
