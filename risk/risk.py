import math
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class RiskManager:
    """
    Handles risk management including position sizing (Fixed, Volatility, Kelly), 
    stop losses, and portfolio optimization.
    """

    def __init__(self, risk_per_trade: float = 0.01, max_drawdown_limit: float = 0.15):
        self.risk_per_trade = risk_per_trade # Default 1%
        self.max_drawdown_limit = max_drawdown_limit

    def calculate_fixed_fractional_size(self, equity: float, price: float, stop_loss_pct: float) -> int:
        """ Level 1: Fixed Percentage Risk. """
        if price <= 0 or stop_loss_pct <= 0: return 0
        risk_amount = equity * self.risk_per_trade
        risk_per_share = price * stop_loss_pct
        return math.floor(risk_amount / risk_per_share)

    def calculate_volatility_adjusted_size(self, equity: float, price: float, atr: float, multiplier: float = 2.0) -> int:
        """ 
        Level 2: Volatility Targeting. 
        Sizes position so that a 1-ATR move equals the target risk amount.
        """
        if price <= 0 or atr <= 0: return 0
        risk_amount = equity * self.risk_per_trade
        # Risk per share is defined by ATR
        risk_per_share = atr * multiplier
        return math.floor(risk_amount / risk_per_share)

    def calculate_kelly_size(self, equity: float, price: float, win_rate: float, win_loss_ratio: float, fraction: float = 0.5) -> int:
        """
        Level 3: Kelly Criterion.
        Fractional Kelly (default 0.5 for Half-Kelly) to maximize long-term growth.
        """
        if price <= 0 or win_loss_ratio <= 0: return 0
        
        # Kelly % = (p*b - q) / b
        # p: win rate, b: win/loss ratio, q: loss rate (1-p)
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Guard against negative expectancy
        kelly_pct = max(0, kelly_pct)
        
        # Apply fractional scaling for safety
        final_risk_pct = kelly_pct * fraction
        
        # Max cap at 20% per trade to avoid over-concentration
        final_risk_pct = min(final_risk_pct, 0.20)
        
        risk_amount = equity * final_risk_pct
        return math.floor(risk_amount / price)

    def calculate_markowitz_weights(self, price_data_dict: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """ Inverse Volatility weighting strategy. """
        volatilities = {}
        for ticker, df in price_data_dict.items():
            if len(df) < 20: continue
            returns = df['close'].pct_change().dropna()
            vol = returns.std()
            if vol > 0: volatilities[ticker] = vol
        
        if not volatilities:
            return {t: 1.0/len(price_data_dict) for t in price_data_dict.keys()}
            
        inv_vols = {t: 1.0/v for t, v in volatilities.items()}
        sum_inv_vol = sum(inv_vols.values())
        return {t: iv / sum_inv_vol for t, iv in inv_vols.items()}

    def get_atr_trailing_stop(self, current_price: float, atr: float, multiplier: float = 3.0, prev_stop: float = 0) -> float:
        """ ATR-based trailing stop. Moving only UP. """
        stop_level = current_price - (atr * multiplier)
        return max(stop_level, prev_stop) if prev_stop > 0 else stop_level

    def is_stop_loss_triggered(self, avg_cost: float, current_price: float, stop_loss_pct: float) -> bool:
        if avg_cost <= 0: return False
        return current_price < (avg_cost * (1 - stop_loss_pct))

    def check_drawdown_halt(self, current_equity: float, peak_equity: float) -> bool:
        if peak_equity <= 0: return False
        drawdown = (peak_equity - current_equity) / peak_equity
        return drawdown >= self.max_drawdown_limit
