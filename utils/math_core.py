import numpy as np
import pandas as pd
from typing import Dict, List, Optional

class MathCore:
    """
    Core mathematical engine for institutional trend filtering and risk parity.
    Based on the Grebenkov/CTA framework.
    """

    @staticmethod
    def calculate_volatility_normalized_return(series: pd.Series, span: int = 30) -> pd.Series:
        """
        Calculates r_t / sigma_t where sigma_t is an EWMA of absolute returns.
        """
        returns = series.pct_change()
        # EWMA Volatility (Absolute Returns)
        vol = returns.abs().ewm(span=span, adjust=False).mean()
        # Normalization (add epsilon to avoid div by zero)
        normalized = returns / (vol + 1e-8)
        return normalized.fillna(0)

    @staticmethod
    def calculate_trend_signal(normalized_returns: pd.Series, span: int = 120) -> pd.Series:
        """
        Calculates the exponential moving average of normalized returns.
        Output represents conviction (-1.0 to 1.0).
        """
        signal = normalized_returns.ewm(span=span, adjust=False).mean()
        # Scale to [-1, 1] range (rough approximation for conviction)
        # Typically trend-following signals are clipped at +/- 1
        return signal.clip(-1, 1)

    @staticmethod
    def calculate_arp_weights(corr_matrix: pd.DataFrame) -> pd.Series:
        """
        Agnostic Risk Parity (ARP): w proportional to Sigma^-1/2 * 1.
        Distributes risk uniformly across correlated assets.
        """
        try:
            # 1. Eigen-decomposition of correlation matrix
            eigenvalues, eigenvectors = np.linalg.eigh(corr_matrix.values)
            
            # 2. Square root of inverse eigenvalues
            # Protect against zero/negative eigenvalues
            ev_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(eigenvalues, 1e-8)))
            
            # 3. Covariance Matrix ^ -1/2
            sigma_inv_half = eigenvectors @ ev_inv_sqrt @ eigenvectors.T
            
            # 4. Weights = Sum of rows of Sigma^-1/2
            weights = np.sum(sigma_inv_half, axis=1)
            
            # 5. Normalize
            weights = weights / np.sum(np.abs(weights))
            return pd.Series(weights, index=corr_matrix.index)
        except Exception:
            # Fallback to 1/N
            n = len(corr_matrix)
            return pd.Series([1.0/n] * n, index=corr_matrix.index)

def calculate_linear_exposure(conviction: float, target_vol: float, current_vol: float) -> float:
    """
    Linear Trading Rule: Leverage = (Conviction * TargetVol) / CurrentVol
    """
    if current_vol <= 0: return 0.0
    exposure = (conviction * target_vol) / current_vol
    return np.clip(exposure, -1.0, 1.0) # Limit to 100% unleveraged for safety
