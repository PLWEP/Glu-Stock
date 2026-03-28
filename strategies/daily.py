9import pandas as pd
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
        
        # 2. Pivot Points (Using previous TRADING DAY if data is intraday)
        dates = pd.to_datetime(df.index.get_level_values('date'))
        df['date_only'] = dates.date
        
        daily_ohlc = df.groupby('date_only').agg({
            'high': 'max', 'low': 'min', 'close': 'last'
        }).shift(1) # Shift to get previous day
        
        # Map daily pivots back to intraday candles
        df['pivot'] = df['date_only'].map(daily_ohlc.apply(lambda r: (r['high'] + r['low'] + r['close'])/3 if not pd.isna(r['high']) else np.nan, axis=1))
        df['r_res'] = df['date_only'].map(daily_ohlc.apply(lambda r: (2 * ((r['high'] + r['low'] + r['close'])/3)) - r['low'] if not pd.isna(r['high']) else np.nan, axis=1))
        df['s_sup'] = df['date_only'].map(daily_ohlc.apply(lambda r: (2 * ((r['high'] + r['low'] + r['close'])/3)) - r['high'] if not pd.isna(r['high']) else np.nan, axis=1))
        
        # 3. Donchian Channel (20 periods)
        df['donchian_up'] = df['high'].rolling(window=20).max()
        df['donchian_down'] = df['low'].rolling(window=20).min()
        
        # 4. Signal Logic
        df['final_signal'] = 0
        df['final_score'] = 0.5
        
        # LONG: P > C AND P > VWAP. Close if P >= R
        long_entry = (df['close'] > df['pivot']) & (df['close'] > df['vwap'])
        df.loc[long_entry, 'final_signal'] = 1
        
        # DEBUG: Print last row signal status
        # print(f"DEBUG: Ticker={df.index.get_level_values('ticker')[0]} Close={df['close'].iloc[-1]} Pivot={df['pivot'].iloc[-1]} VWAP={df['vwap'].iloc[-1]} Signal={df['final_signal'].iloc[-1]}")
        
        # SHORT (Paper Only): P < C AND P < VWAP. Close if P <= S
        short_entry = (df['close'] < df['pivot']) & (df['close'] < df['vwap'])
        df.loc[short_entry, 'final_signal'] = -1
        
        # Exit (Liquidasi)
        df.loc[df['close'] >= df['r_res'], 'final_signal'] = 0
        df.loc[df['close'] <= df['s_sup'], 'final_signal'] = 0
        
        return df
