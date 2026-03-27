import pandas as pd
import ta
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands

class FeatureEngineer:
    """
    Computes technical indicators for OHLCV data using the ta library.
    Ensures multi-ticker isolation and no lookahead bias.
    """

    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates indicators (RSI, MACD, SMA, EMA, BBands) for the given DataFrame.
        Expected index: ['date', 'ticker']
        """
        if df.empty:
            return df

        # Group by ticker to ensure isolation
        enriched_df = df.groupby(level='ticker', group_keys=False).apply(self._calculate_ticker_features)
        
        return enriched_df

    def _calculate_ticker_features(self, group: pd.DataFrame) -> pd.DataFrame:
        """Calculates indicators for a single ticker subgroup."""
        # Ensure data is sorted by date
        group = group.sort_index(level='date')
        
        close = group['close']
        high = group['high']
        low = group['low']

        # 1. RSI (Relative Strength Index)
        group['rsi'] = RSIIndicator(close=close, window=14).rsi()

        # 2. MACD (Moving Average Convergence Divergence)
        macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
        group['macd'] = macd.macd()
        group['macd_signal'] = macd.macd_signal()
        group['macd_diff'] = macd.macd_diff()

        # 3. SMA (Simple Moving Average)
        group['sma_20'] = SMAIndicator(close=close, window=20).sma_indicator()

        # 4. EMA (Exponential Moving Average)
        group['ema_20'] = EMAIndicator(close=close, window=20).ema_indicator()

        # 5. Bollinger Bands
        bb = BollingerBands(close=close, window=20, window_dev=2)
        group['bb_mavg'] = bb.bollinger_mavg()
        group['bb_high'] = bb.bollinger_hband()
        group['bb_low'] = bb.bollinger_lband()
        group['bb_width'] = bb.bollinger_wband()

        return group

    def clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handles NaNs created by technical indicator rolling windows."""
        # Typically we drop or fill NaNs. Indicators like SMA(20) create 19 NaNs at start.
        return df.dropna()

if __name__ == "__main__":
    # Example usage / sanity check
    from data.data import StockDataHandler
    
    handler = StockDataHandler()
    raw_data = handler.fetch_data(["AAPL", "MSFT"], "2024-01-01", "2024-02-28")
    
    engineer = FeatureEngineer()
    featured_data = engineer.add_indicators(raw_data)
    
    print(featured_data.tail())
