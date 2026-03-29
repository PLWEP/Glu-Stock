import yfinance as yf
import pandas as pd
import time
import numpy as np
from typing import List, Dict, Any, Optional
from utils.logger import JsonLogger
from utils.config import ConfigLoader

class FundamentalAgent:
    """
    Analyzes stock quality using financial ratios (P/E, ROE, DER, Div Yield) 
    and multi-year growth metrics (Net Income CAGR).
    """
    def __init__(self):
        self.logger = JsonLogger(log_file="logs/fundamental_agent.log")
        self.config = ConfigLoader().get_config().get("intelligence", {})
        
        self.max_pe = self.config.get("max_pe", 25.0)
        self.min_roe = self.config.get("min_roe", 0.10)
        self.max_der = self.config.get("max_der", 2.0)
        self.min_div_yield = self.config.get("min_div_yield", 0.02)

    def analyze_tickers(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        results = {}
        for ticker in tickers:
            try:
                data = self.get_fundamental_data(ticker)
                if data:
                    score = self.calculate_quality_score(data)
                    data['quality_score'] = score
                    data['passed'] = score >= 0.6
                    results[ticker] = data
                time.sleep(0.5)
            except Exception as e:
                self.logger.error(f"FundamentalAgent: Error analyzing [{ticker}]", error=str(e))
        return results

    def get_fundamental_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        try:
            yt = yf.Ticker(ticker)
            info = yt.info
            
            # 1. Growth Calculation (Net Income CAGR)
            growth_score = 0.5 # Default neutral
            try:
                fin = yt.financials
                if not fin.empty and "Net Income" in fin.index:
                    income = fin.loc["Net Income"].dropna()
                    if len(income) >= 3:
                        # CAGR = (Final/Initial)^(1/N) - 1
                        latest = income.iloc[0]
                        earliest = income.iloc[2]
                        if earliest > 0:
                            cagr = (latest / earliest) ** (1/3) - 1
                            growth_score = 1.0 if cagr > 0.15 else (0.6 if cagr > 0 else 0.2)
            except: pass

            return {
                "pe_ratio": info.get("trailingPE"),
                "roe": info.get("returnOnEquity"),
                "der": info.get("debtToEquity"),
                "div_yield": info.get("dividendYield"),
                "growth_score": growth_score,
                "sector": info.get("sector")
            }
        except:
            return None

    def calculate_quality_score(self, data: Dict[str, Any]) -> float:
        score = 0
        points = 0
        
        # Ratios
        params = [
            ("pe_ratio", lambda x: 1.0 if x < self.max_pe else 0.0),
            ("roe", lambda x: 1.0 if x > self.min_roe else 0.0),
            ("der", lambda x: 1.0 if (x / 100.0 if x > 10 else x) < self.max_der else 0.0),
            ("div_yield", lambda x: 1.0 if x > self.min_div_yield else 0.0),
            ("growth_score", lambda x: x) # Use growth score directly
        ]
        
        for key, func in params:
            val = data.get(key)
            if val is not None:
                points += 1
                score += func(val)
                
        if points == 0: return 0.5
        return min(1.0, score / points)
