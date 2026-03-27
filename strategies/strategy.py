import pandas as pd
import numpy as np
from typing import Optional, List

class TradingStrategy:
    """
    Generates trading signals based on technical indicators and optional ML models.
    """

    def generate_signals(self, df: pd.DataFrame, model: Optional[object] = None, features: Optional[List[str]] = None, timeframe: str = "daily") -> pd.DataFrame:
        """
        Generates combined signals based on continuous multi-factor scoring.
        """
        if df.empty:
            return df
        
        # 1. Compute individual factor scores (0-1)
        df = self._compute_factor_scores(df)
        
        # 2. Combine into composite score using requested weights
        # score = 0.3*rsi + 0.3*macd + 0.2*trend + 0.2*volume
        df['final_score'] = (
            0.3 * df['s_rsi'] + 
            0.3 * df['s_macd'] + 
            0.2 * df['s_trend'] + 
            0.2 * df['s_vol']
        )
        
        # 3. Handle ML signals (if model is provided) - Maintain for architecture compatibility
        if model and features:
            df = self._generate_ml_signals(df, model, features)
            df['final_score'] = (df['final_score'] + df['ml_confidence'] * df['ml_signal'].clip(0, 1)) / 2
        
        # 4. Map back to discrete signals
        # SIGNAL: "BUY" if score > 0.5 else "HOLD"
        df['final_signal'] = 0
        df.loc[df['final_score'] > 0.5, 'final_signal'] = 1
        
        # 5. Debug Log
        if not df.empty:
            try:
                ticker = df.index.get_level_values('ticker')[-1]
                score = df['final_score'].iloc[-1]
                signal = "BUY" if score > 0.5 else "HOLD"
                print(f"Strategy: {ticker} score: {score:.4f} | Signal: {signal}")
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

    def _generate_ml_signals(self, df: pd.DataFrame, model: object, features: List[str]) -> pd.DataFrame:
        """ML-based prediction integration."""
        try:
            preds = model.predict(df[features])
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(df[features])
                confidence = np.max(probs, axis=1)
            else:
                confidence = 1.0
            
            df['ml_signal'] = preds
            df['ml_confidence'] = confidence
        except Exception:
            df['ml_signal'] = 0
            df['ml_confidence'] = 0.0
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
