import math
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class RiskManager:
    """
    Handles risk management including position sizing, 
    Advanced Markowitz (Rolling Covariance), and safety gates.
    """

    def __init__(self, risk_per_trade: float = 0.01, max_drawdown_limit: float = 0.15):
        self.risk_per_trade = risk_per_trade
        self.max_drawdown_limit = max_drawdown_limit

    def calculate_fixed_fractional_size(self, equity: float, price: float, stop_loss_pct: float) -> int:
        if price <= 0 or stop_loss_pct <= 0: return 0
        return math.floor((equity * self.risk_per_trade) / (price * stop_loss_pct))

    def calculate_volatility_adjusted_size(self, equity: float, price: float, atr: float, multiplier: float = 2.0) -> int:
        if price <= 0 or atr <= 0: return 0
        return math.floor((equity * self.risk_per_trade) / (atr * multiplier))

    def calculate_kelly_size(self, equity: float, price: float, win_rate: float, win_loss_ratio: float, fraction: float = 0.5) -> int:
        if price <= 0 or win_loss_ratio <= 0: return 0
        k_pct = max(0, (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio)
        final_risk = min(k_pct * fraction, 0.20)
        return math.floor((equity * final_risk) / price)

    def calculate_markowitz_weights(self, price_data_dict: Dict[str, pd.DataFrame], 
                                     window: int = 30, shrinkage: float = 0.1) -> Dict[str, float]:
        """
        Advanced Markowitz: Uses Rolling Covariance and Ledoit-Wolf-style Shrinkage.
        """
        if not price_data_dict: return {}
        
        # 1. Align prices
        all_prices = {}
        for t, df in price_data_dict.items():
            if len(df) >= window: all_prices[t] = df['close']
        
        if len(all_prices) < 2:
            return {t: 1.0/len(price_data_dict) for t in price_data_dict.keys()}
            
        price_df = pd.DataFrame(all_prices).tail(window)
        returns = price_df.pct_change().dropna()
        
        # 2. Compute Covariance with Shrinkage
        # Cov = (1-s)*SampleCov + s*Identity
        sample_cov = returns.cov().values
        n = sample_cov.shape[0]
        shrink_matrix = (1 - shrinkage) * sample_cov + shrinkage * np.eye(n) * np.mean(np.diag(sample_cov))
        
        # 3. Inverse-Variance Weighting (Simplified for Stability)
        # Weights normalized proportion to 1/Var
        inv_vars = 1.0 / np.diag(shrink_matrix)
        weights = inv_vars / np.sum(inv_vars)
        
        return dict(zip(price_df.columns, weights))

    def get_atr_trailing_stop(self, current_price: float, atr: float, multiplier: float = 3.0, prev_stop: float = 0) -> float:
        stop_level = current_price - (atr * multiplier)
        return max(stop_level, prev_stop) if prev_stop > 0 else stop_level

    def is_stop_loss_triggered(self, avg_cost: float, current_price: float, stop_loss_pct: float) -> bool:
        if avg_cost <= 0: return False
        return current_price < (avg_cost * (1 - stop_loss_pct))

    def check_drawdown_halt(self, current_equity: float, peak_equity: float) -> bool:
        if peak_equity <= 0: return False
        return ((peak_equity - current_equity) / peak_equity) >= self.max_drawdown_limit
