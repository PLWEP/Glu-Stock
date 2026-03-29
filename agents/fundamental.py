import yfinance as yf
import pandas as pd
import time
from typing import List, Dict, Any, Optional
from utils.logger import JsonLogger
from utils.config import ConfigLoader

class FundamentalAgent:
    """
    Analyzes stock quality using financial ratios (P/E, ROE, DER, Div Yield).
    Provides a quality score (0-1) for stock filtering.
    """
    def __init__(self):
        self.logger = JsonLogger(log_file="logs/fundamental_agent.log")
        self.config = ConfigLoader().get_config().get("intelligence", {})
        
        # Default Thresholds
        self.max_pe = self.config.get("max_pe", 25.0)
        self.min_roe = self.config.get("min_roe", 0.10) # 10%
        self.max_der = self.config.get("max_der", 2.0)
        self.min_div_yield = self.config.get("min_div_yield", 0.02) # 2%

    def analyze_tickers(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetches and scores multiple tickers. Returns a dict of results.
        """
        results = {}
        self.logger.info(f"FundamentalAgent: Analyzing {len(tickers)} tickers...")
        
        for ticker in tickers:
            try:
                data = self.get_fundamental_data(ticker)
                if data:
                    score = self.calculate_quality_score(data)
                    data['quality_score'] = score
                    data['passed'] = score >= 0.6 # Quality threshold
                    results[ticker] = data
                # Self-throttle to avoid yfinance rate limits
                time.sleep(0.5)
            except Exception as e:
                self.logger.error(f"FundamentalAgent: Error analyzing [{ticker}]", error=str(e))
                
        return results

    def get_fundamental_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetches raw financial data from yfinance.
        """
        try:
            yt = yf.Ticker(ticker)
            info = yt.info
            
            # Extract key ratios
            return {
                "pe_ratio": info.get("trailingPE"),
                "roe": info.get("returnOnEquity"),
                "der": info.get("debtToEquity"), # in percentage (e.g. 150 = 1.5)
                "div_yield": info.get("dividendYield"),
                "market_cap": info.get("marketCap"),
                "sector": info.get("sector")
            }
        except:
            return None

    def calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """
        Calculates a composite quality score (0-1).
        """
        score = 0
        points = 0
        
        # 1. P/E Score (Value)
        pe = data.get("pe_ratio")
        if pe:
            points += 1
            if pe < self.max_pe: score += 1
            if pe < 15: score += 0.5 # Bonus for deep value
            
        # 2. ROE Score (Profitability)
        roe = data.get("roe")
        if roe:
            points += 1
            if roe > self.min_roe: score += 1
            if roe > 0.20: score += 0.5 # Bonus for high quality
            
        # 3. DER Score (Financial Stability)
        der = data.get("der") # Note: yf returns it in units (e.g. 150.0 means 1.5)
        if der:
            points += 1
            real_der = der / 100.0 if der > 10 else der
            if real_der < self.max_der: score += 1
            if real_der < 0.5: score += 0.5 # Bonus for low debt
            
        # 4. Dividend Score (Income)
        div = data.get("div_yield")
        if div:
            points += 1
            if div > self.min_div_yield: score += 1
            
        if points == 0: return 0.5 # Neutral if no data
        return min(1.0, score / points)
