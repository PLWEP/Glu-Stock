import pandas as pd
import numpy as np
from typing import Optional, List
from utils.config import ConfigLoader
from utils.math_core import MathCore

class TradingStrategy:
    """
    Generates trading signals based on technical indicators and optional ML models.
    Now includes Institutional Trend Filtering (Vol-Normalized EMA).
    """

    def generate_signals(self, df: pd.DataFrame, model: Optional[object] = None, features: Optional[List[str]] = None, timeframe: str = "daily") -> pd.DataFrame:
        """
        Generates combined signals based on continuous multi-factor scoring.
        """
        if df.empty:
            return df
        
        # 1. Institutional Trend Conviction (The Grebenkov Layer)
        # Use appropriate scale for each timeframe
        scale = 112 if timeframe == "monthly" else (20 if timeframe == "weekly" else 10)
        norm_ret = MathCore.calculate_volatility_normalized_return(df['close'])
        df['inst_trend_conviction'] = MathCore.calculate_trend_signal(norm_ret, span=scale)
        
        # 2. Compute individual factor scores (0-1)
        df = self._compute_factor_scores(df)
        
        # 3. Combine into composite score using timeframe-aware weights
        # Daily: Short-term (RSI/MACD) | Yearly: Long-term (Trend)
        if timeframe == "daily":
            # Daily uses weighted average of indicators + Inst Trend
            weights = {'rsi': 0.2, 'macd': 0.2, 'trend': 0.2, 'vol': 0.2, 'inst': 0.2}
            inst_score = (df['inst_trend_conviction'] + 1) / 2 # Scale [-1,1] to [0,1]
        else:
            # Monthly/Weekly: Focus heavily on Institutional Trend
            weights = {'rsi': 0.05, 'macd': 0.05, 'trend': 0.1, 'vol': 0.1, 'inst': 0.7}
            inst_score = (df['inst_trend_conviction'] + 1) / 2

        df['final_score'] = (
            weights['rsi'] * df['s_rsi'] + 
            weights['macd'] * df['s_macd'] + 
            weights['trend'] * df['s_trend'] + 
            weights['vol'] * df['s_vol'] +
            weights['inst'] * inst_score
        )
        df['timeframe'] = timeframe
        
        # 4. Map back to discrete signals
        # SIGNAL: "BUY" if score > 0.5 else "HOLD"
        df['final_signal'] = 0
        
        # DEBUG MODE OVERRIDE
        debug_mode = ConfigLoader().get_config().get('debug_mode', True)
        if debug_mode:
            print("Strategy: !! DEBUG MODE ACTIVE !! Bypassing thresholds - Forcing BUY signal.")
            df['final_signal'] = 1
        else:
            df.loc[df['final_score'] > 0.5, 'final_signal'] = 1
        
        # 5. Debug Log
        if not df.empty:
            try:
                ticker = df.index.get_level_values('ticker')[-1]
                score = df['final_score'].iloc[-1]
                final_sig = df['final_signal'].iloc[-1]
                signal_str = "BUY" if final_sig == 1 else "HOLD"
                print(f"Strategy: {ticker} score: {score:.4f} | Signal: {signal_str} (Score Signal: {'BUY' if score > 0.5 else 'HOLD'})")
            except Exception:
                pass

        return df

    def _compute_factor_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Calculates continuous normalized factor components (0-1). """
        # A. RSI Score: (50 - RSI) / 50 clamped [0, 1]
        df['s_rsi'] = np.clip((50 - df['rsi'].fillna(50)) / 50, 0, 1)
        
        # B. MACD Score: Sigmoid normalization of histogram
        df['s_macd'] = 1 / (1 + np.exp(-df['macd_diff'].fillna(0)))
        
        # C. Trend Score: Slope of SMA20 normalized to [0, 1]
        # Normalized slope = Change in SMA / SMA (clamped)
        df['sma_slope'] = df.groupby(level='ticker')['sma_20'].diff() / df['sma_20'].replace(0, 1)
        df['s_trend'] = np.clip(df['sma_slope'] / 0.01 + 0.5, 0, 1) # 1% move creates 1.0 score
        df['s_trend'] = df['s_trend'].fillna(0.5)

        # D. Volume Score: current_volume / avg_volume (normalized)
        df['vol_avg_20'] = df.groupby(level='ticker')['volume'].transform(lambda x: x.rolling(20).mean())
        df['s_vol'] = np.clip(df['volume'] / (df['vol_avg_20'].replace(0, 1) * 2), 0, 1)
        df['s_vol'] = df['s_vol'].fillna(0.5)

        return df


if __name__ == "__main__":
    # Sanity check
    from data.data import StockDataHandler
    from features.features import FeatureEngineer
    
    handler = StockDataHandler()
    df = handler.fetch_data("AAPL", "2024-01-01", "2024-03-01")
    
    engineer = FeatureEngineer()
    df = engineer.add_indicators(df)
    
    strategy = TradingStrategy()
    df = strategy.generate_signals(df)
    
    print("Scoring Sample:")
    print(df[['close', 'final_score', 'final_signal']].tail(10))
