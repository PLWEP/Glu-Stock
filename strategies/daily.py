import pandas as pd
import numpy as np

class DailyStrategy:
    """
    Day Trading / Scalping Strategy.
    Pivot Support/Resistance + VWAP (Daily Reset).
    """
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        
        # Ensure dates are datetime for grouping
        dates = pd.to_datetime(df.index.get_level_values('date'))
        df['date_only'] = dates.date
        
        # 1. VWAP Calculation (RESET DAILY)
        # Standard VWAP = cumulative (price * volume) / cumulative volume (resetting each day)
        def calc_vwap(group):
            cum_pv = (group['close'] * group['volume']).cumsum()
            cum_v = group['volume'].cumsum()
            group['vwap'] = cum_pv / cum_v
            return group

        df = df.groupby('date_only', group_keys=False).apply(calc_vwap)
        
        # 2. Pivot Points (Using previous TRADING DAY)
        daily_ohlc = df.groupby('date_only').agg({
            'high': 'max', 'low': 'min', 'close': 'last'
        }).shift(1) 
        
        df['pivot'] = df['date_only'].map(daily_ohlc.apply(lambda r: (r['high'] + r['low'] + r['close'])/3 if not pd.isna(r['high']) else np.nan, axis=1))
        df['r_res'] = df['date_only'].map(daily_ohlc.apply(lambda r: (2 * ((r['high'] + r['low'] + r['close'])/3)) - r['low'] if not pd.isna(r['high']) else np.nan, axis=1))
        df['s_sup'] = df['date_only'].map(daily_ohlc.apply(lambda r: (2 * ((r['high'] + r['low'] + r['close'])/3)) - r['high'] if not pd.isna(r['high']) else np.nan, axis=1))
        
        # 3. Donchian Channel (20 periods)
        df['donchian_up'] = df['high'].rolling(window=20).max()
        df['donchian_down'] = df['low'].rolling(window=20).min()
        
        # 4. Signal Logic
        df['final_signal'] = 0
        df['final_score'] = 0.5
        
        # LONG: P > Pivot AND P > VWAP.
        long_entry = (df['close'] > df['pivot']) & (df['close'] > df['vwap'])
        df.loc[long_entry, 'final_signal'] = 1
        
        # SHORT (Paper Only): P < Pivot AND P < VWAP.
        short_entry = (df['close'] < df['pivot']) & (df['close'] < df['vwap'])
        df.loc[short_entry, 'final_signal'] = -1
        
        # Take Profit / Exit (R1/S1 levels)
        df.loc[df['close'] >= df['r_res'], 'final_signal'] = 0
        df.loc[df['close'] <= df['s_sup'], 'final_signal'] = 0
        
        return df
