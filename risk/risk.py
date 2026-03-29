import math
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class RiskManager:
    """
    Handles risk management including position sizing, stop losses, 
    Markowitz portfolio optimization, and ATR trailing stops.
    """

    def __init__(self, risk_per_trade: float = 0.02, max_drawdown_limit: float = 0.15):
        self.risk_per_trade = risk_per_trade
        self.max_drawdown_limit = max_drawdown_limit

    def calculate_position_size(self, equity: float, price: float, stop_loss_pct: float) -> int:
        """ Calculates number of shares using fixed percentage risk. """
        if price <= 0 or stop_loss_pct <= 0:
            return 0
        risk_amount = equity * self.risk_per_trade
        risk_per_share = price * stop_loss_pct
        return math.floor(risk_amount / risk_per_share)

    def calculate_markowitz_weights(self, price_data_dict: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """
        Implements a Risk-Parity (Inverse Volatility) weighting strategy.
        Assigns more capital to stocks with lower historical volatility.
        """
        volatilities = {}
        for ticker, df in price_data_dict.items():
            if len(df) < 20: continue
            # Daily returns volatility (Standard Deviation)
            returns = df['close'].pct_change().dropna()
            vol = returns.std()
            if vol > 0:
                volatilities[ticker] = vol
        
        if not volatilities:
            return {t: 1.0/len(price_data_dict) for t in price_data_dict.keys()}
            
        # Inverse Volatility: W = (1/vol) / Sum(1/vol)
        inv_vols = {t: 1.0/v for t, v in volatilities.items()}
        sum_inv_vol = sum(inv_vols.values())
        weights = {t: iv / sum_inv_vol for t, iv in inv_vols.items()}
        
        return weights

    def get_atr_trailing_stop(self, current_price: float, atr: float, multiplier: float = 3.0, prev_stop: float = 0) -> float:
        """
        Calculates ATR-based trailing stop level.
        The stop level can only move UP (for long positions).
        """
        stop_level = current_price - (atr * multiplier)
        # Ensure the stop level doesn't decrease
        return max(stop_level, prev_stop) if prev_stop > 0 else stop_level

    def is_stop_loss_triggered(self, avg_cost: float, current_price: float, stop_loss_pct: float) -> bool:
        """ Checks if price dropped below static SL. """
        if avg_cost <= 0: return False
        return current_price < (avg_cost * (1 - stop_loss_pct))

    def check_drawdown_halt(self, current_equity: float, peak_equity: float) -> bool:
        """ Checks if trading should halt due to excessive drawdown. """
        if peak_equity <= 0: return False
        drawdown = (peak_equity - current_equity) / peak_equity
        return drawdown >= self.max_drawdown_limit
