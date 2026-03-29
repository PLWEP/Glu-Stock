import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any

class RegimeDetector:
    """
    Monitors global market conditions using the IHSG (^JKSE) index. 
    Determines Bull/Bear regime based on price relative to EMA 200.
    """

    def __init__(self, ticker: str = "^JKSE"):
        self.ticker = ticker

    def get_market_regime(self) -> Dict[str, Any]:
        """
        Calculates the current market regime.
        Returns: {regime: 'BULL'/'BEAR', factor: 0.5-1.0}
        """
        try:
            # Fetch last 300 days to calculate EMA 200
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')
            
            df = yf.download(self.ticker, start=start_date, end=end_date, interval="1d", progress=False)
            if df.empty:
                return {"regime": "NEUTRAL", "multiplier": 1.0, "reason": "No data"}

            # Standard Institutional Indicator: EMA 200
            df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
            last_price = df['Close'].iloc[-1]
            last_ema = df['ema200'].iloc[-1]
            
            # Simple Logic: 
            # Above EMA 200 = BULL (Full Steam)
            # Below EMA 200 = BEAR (Half Steam)
            if last_price > last_ema:
                return {
                    "regime": "BULL",
                    "multiplier": 1.0,
                    "price": float(last_price),
                    "ema200": float(last_ema)
                }
            else:
                return {
                    "regime": "BEAR",
                    "multiplier": 0.5, # Reduce risk by 50%
                    "price": float(last_price),
                    "ema200": float(last_ema)
                }
        except Exception:
            return {"regime": "NEUTRAL", "multiplier": 1.0, "reason": "Error fetching index"}
