import pandas as pd
import numpy as np
from typing import Optional, List

class TradingStrategy:
    """
    Generates trading signals based on technical indicators and optional ML models.
    """

    def generate_signals(self, df: pd.DataFrame, model: Optional[object] = None, features: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Generates combined signals and confidence scores.
        """
        if df.empty:
            return df
        
        # 1. Rule-based signals
        df = self._generate_rule_signals(df)
        
        # 2. ML signals (if model is provided)
        if model and features:
            df = self._generate_ml_signals(df, model, features)
        else:
            df['ml_signal'] = 0
            df['ml_confidence'] = 0.0
        
        # 3. Aggregate signals
        df = self._aggregate_signals(df)
        
        return df

    def _generate_rule_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rule-based logic: RSI and MACD."""
        # RSI Logic
        df['rsi_signal'] = 0
        df.loc[df['rsi'] < 30, 'rsi_signal'] = 1  # Buy
        df.loc[df['rsi'] > 70, 'rsi_signal'] = -1 # Sell
        
        # MACD Logic: Detect crossover
        # We need to shift to find crossover: (prev_macd < prev_signal) AND (curr_macd > curr_signal) -> BUY
        df['macd_prev'] = df.groupby(level='ticker')['macd'].shift(1)
        df['macd_signal_prev'] = df.groupby(level='ticker')['macd_signal'].shift(1)
        
        df['m_cross_up'] = (df['macd_prev'] < df['macd_signal_prev']) & (df['macd'] > df['macd_signal'])
        df['m_cross_down'] = (df['macd_prev'] > df['macd_signal_prev']) & (df['macd'] < df['macd_signal'])
        
        df['macd_signal_rule'] = 0
        df.loc[df['m_cross_up'], 'macd_signal_rule'] = 1
        df.loc[df['m_cross_down'], 'macd_signal_rule'] = -1
        
        # Cleanup temp columns
        df.drop(columns=['macd_prev', 'macd_signal_prev', 'm_cross_up', 'm_cross_down'], inplace=True)
        
        return df

    def _generate_ml_signals(self, df: pd.DataFrame, model: object, features: List[str]) -> pd.DataFrame:
        """ML-based logic."""
        try:
            # Assume Scikit-Learn like interface
            preds = model.predict(df[features])
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(df[features])
                confidence = np.max(probs, axis=1)
            else:
                confidence = 1.0  # Placeholder if no proba
            
            df['ml_signal'] = preds
            df['ml_confidence'] = confidence
        except Exception as e:
            print(f"ML prediction error: {e}")
            df['ml_signal'] = 0
            df['ml_confidence'] = 0.0
        return df

    def _aggregate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Combine signals and calculate confidence."""
        # Weighted aggregate: RSI (0.3), MACD (0.3), ML (0.4) if ML exists.
        # If no ML, then RSI (0.5), MACD (0.5).
        
        has_ml = (df['ml_confidence'] > 0).any()
        
        if has_ml:
            # simple mean for signal if multiple agree, or prioritize ML
            df['final_signal'] = np.sign(0.3 * df['rsi_signal'] + 0.3 * df['macd_signal_rule'] + 0.4 * df['ml_signal'])
            df['confidence'] = (0.3 * (df['rsi_signal'] != 0).astype(float) + 
                                0.3 * (df['macd_signal_rule'] != 0).astype(float) + 
                                0.4 * df['ml_confidence'])
        else:
            # Rule based only
            df['final_signal'] = np.sign(0.5 * df['rsi_signal'] + 0.5 * df['macd_signal_rule'])
            df['confidence'] = (0.5 * (df['rsi_signal'] != 0).astype(float) + 
                                0.5 * (df['macd_signal_rule'] != 0).astype(float))
        
        # Standardize final_signal to integers
        df['final_signal'] = df['final_signal'].fillna(0).astype(int)
        df['confidence'] = df['confidence'].clip(0, 1.0)
        
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
    
    print(df[df['final_signal'] != 0].tail())
