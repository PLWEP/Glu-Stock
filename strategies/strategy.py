import pandas as pd
import numpy as np
from typing import Optional, List

class TradingStrategy:
    """
    Generates trading signals based on technical indicators and optional ML models.
    """

    def generate_signals(self, df: pd.DataFrame, model: Optional[object] = None, features: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Generates combined signals based on composite multi-factor scoring.
        Returns 'final_score' (0-1) and 'final_signal' (-1, 0, 1).
        """
        if df.empty:
            return df
        
        # 1. Compute individual factor scores (0-1)
        df = self._compute_factor_scores(df)
        
        # 2. Combine into composite score
        df = self._compute_composite_score(df)
        
        # 3. Handle ML signals (if model is provided)
        if model and features:
            df = self._generate_ml_signals(df, model, features)
            # 50/50 blend between technical composite and ML confidence
            df['final_score'] = (df['comp_score'] + df['ml_confidence'] * df['ml_signal'].clip(0, 1)) / 2
        else:
            df['final_score'] = df['comp_score']
        
        # 4. Map back to discrete signals for legacy execution engines
        # BULLISH: score > 0.7 | BEARISH: score < 0.3
        df['final_signal'] = 0
        df.loc[df['final_score'] > 0.7, 'final_signal'] = 1
        df.loc[df['final_score'] < 0.3, 'final_signal'] = -1
        
        return df

    def _compute_factor_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Calculates normalized factor components (0-1). """
        # A. RSI Score: 30 (1.0) -> 70 (0.0)
        df['s_rsi'] = np.clip((70 - df['rsi']) / 40, 0, 1)
        
        # B. MACD Score: Based on histogram vs its rolling volatility
        # Using macd_h (histogram) from FeatureEngineer
        df['macd_h_std'] = df.groupby(level='ticker')['macd_h'].transform(lambda x: x.rolling(20).std())
        # Map +/- 2 Std Dev to [0, 1]
        df['s_macd'] = np.clip((df['macd_h'] / (2 * df['macd_h_std'].replace(0, 1e-6)) + 1) / 2, 0, 1)
        df['s_macd'] = df['s_macd'].fillna(0.5)

        # C. Trend Score: Price distance from SMA20 (+/- 10% range)
        df['s_trend'] = np.clip(((df['close'] / df['sma_20']) - 1) / 0.2 + 0.5, 0, 1)
        df['s_trend'] = df['s_trend'].fillna(0.5)

        # D. Volume Score: Ratio of current volume to 20-day average
        df['vol_avg_20'] = df.groupby(level='ticker')['volume'].transform(lambda x: x.rolling(20).mean())
        # Map 0x (0.0) -> 2x (1.0)
        df['s_vol'] = np.clip(df['volume'] / (2 * df['vol_avg_20'].replace(0, 1)), 0, 1)
        df['s_vol'] = df['s_vol'].fillna(0.5)

        return df

    def _compute_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Weighted ensemble of technical factors. """
        # Weights: RSI (30%), MACD (30%), Trend (20%), Volume (20%)
        df['comp_score'] = (
            df['s_rsi'] * 0.3 + 
            df['s_macd'] * 0.3 + 
            df['s_trend'] * 0.2 + 
            df['s_vol'] * 0.2
        )
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
