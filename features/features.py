import pandas as pd
import ta
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands

class FeatureEngineer:
    """
    Computes technical indicators for OHLCV data.
    Ensures multi-ticker isolation and handles data 'warm-up'.
    """

    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        # Group by ticker to ensure isolation
        enriched_df = df.groupby(level='ticker', group_keys=False).apply(self._calculate_ticker_features)
        return enriched_df

    def _calculate_ticker_features(self, group: pd.DataFrame) -> pd.DataFrame:
        group = group.sort_index(level='date')
        
        close = group['close']
        high = group['high']
        low = group['low']

        # 1. RSI (14)
        group['rsi'] = RSIIndicator(close=close, window=14).rsi()

        # 2. MACD (12, 26, 9)
        macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
        group['macd_diff'] = macd.macd_diff()

        # 3. SMA & EMA (20)
        group['sma_20'] = SMAIndicator(close=close, window=20).sma_indicator()
        group['ema_20'] = EMAIndicator(close=close, window=20).ema_indicator()

        # 4. Bollinger Bands (20, 2)
        bb = BollingerBands(close=close, window=20, window_dev=2)
        group['bb_mavg'] = bb.bollinger_mavg()
        group['bb_high'] = bb.bollinger_hband()
        group['bb_low'] = bb.bollinger_lband()
        group['bb_width'] = (group['bb_high'] - group['bb_low']) / group['bb_mavg']

        return group

    def clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Only removes rows that are entirely NaN or critical missing values.
        Ensures columns exist before attempting to dropna to prevent KeyErrors.
        """
        if df.empty: return df
        
        # Critical columns that MUST have data for strategy logic
        critical_cols = ['rsi', 'macd_diff', 'ema_20']
        
        # Filter only existing columns to avoid KeyError
        existing_cols = [col for col in critical_cols if col in df.columns]
        
        if not existing_cols:
            return df
            
        return df.dropna(subset=existing_cols)
