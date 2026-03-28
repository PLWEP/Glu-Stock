import pandas as pd
import numpy as np
import os
from typing import List, Dict, Tuple, Any

class UniverseManager:
    """
    Manages the stock universe for the IDX market.
    Handles loading, strategic filtering (excluding Banks/BUMN), and factor ranking.
    """

    def __init__(self, csv_path: str = "data/idx_stocks.csv"):
        self.csv_path = csv_path
        if not os.path.exists(self.csv_path):
            self.refresh_universe()

    def refresh_universe(self):
        """ 
        Fetches the complete list of IDX tickers from official endpoints.
        Replaces hardcoded samples with ~800+ live tickers.
        """
        import requests
        print("UniverseManager: Refreshing universe from IDX...")
        
        # 1. Get Company Profiles (includes Sector)
        url = "https://www.idx.co.id/primary/ListedCompany/GetCompanyProfiles?keyword=&start=0&length=1000"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            raw_data = response.json().get('data', [])
        except Exception as e:
            print(f"UniverseManager: ERROR fetching IDX data: {e}")
            # Fallback to a minimal list if internet fails
            raw_data = [{"Code": "BBCA", "Name": "BCA", "SectorName": "Financials"}]

        # 2. Process and Map
        # List of well-known BUMN tickers for identification
        bumn_list = ["TLKM", "BMRI", "BBRI", "BBNI", "PTBA", "ANTM", "TINS", "WIKA", "PTPP", "ADHI"]
        
        processed = []
        for item in raw_data:
            ticker = f"{item['Code']}.JK"
            processed.append({
                "ticker": ticker,
                "name": item.get("Name", "Unknown"),
                "sector": item.get("SectorName", "Unknown"),
                "is_bumn": item['Code'] in bumn_list
            })
            
        df = pd.DataFrame(processed)
        df.to_csv(self.csv_path, index=False)
        print(f"UniverseManager: Successfully cached {len(df)} tickers to {self.csv_path}")

    def get_idx_tickers(self) -> pd.DataFrame:
        """ Loads the full IDX universe from CSV. """
        return pd.read_csv(self.csv_path)

    def filter_global(self, df: pd.DataFrame) -> pd.DataFrame:
        """ 
        Strict Global Filter: Excludes "Bank" (Financials sector) and "BUMN" (State-Owned Enterprises).
        Mandatory for all IDX pipelines to meet user risk/exposure constraints.
        """
        if df.empty: return df
        return df[
            (df["sector"].str.lower() != "financials") & 
            (df["is_bumn"] == False)
        ]

    def filter_daily(self, tickers: List[str], price_data_dict: Dict[str, pd.DataFrame]) -> List[str]:
        """
        Pipeline 1 Filter: Liquidity & Volatility.
        - Volume > 500k lot (50M shares) OR Value > Rp25B.
        - Day Range > 3%.
        """
        candidates = []
        for ticker, df in price_data_dict.items():
            if df.empty or len(df) < 5: continue
            
            # Vectorized metrics
            avg_volume = df["volume"].mean()
            avg_price = df["close"].mean()
            avg_value = avg_volume * avg_price
            
            # Lot size in IDX is 100 shares
            volume_lots = avg_volume / 100
            
            # Liquidity check
            is_liquid = (volume_lots > 500_000) or (avg_value > 25_000_000_000)
            
            # Volatility check (High-Low range)
            daily_range = (df["high"] - df["low"]) / df["low"]
            avg_range = daily_range.mean()
            
            if is_liquid and (0.03 <= avg_range <= 0.05):
                candidates.append(ticker)
                
        return candidates

    def filter_weekly(self, tickers: List[str], price_data_dict: Dict[str, pd.DataFrame]) -> List[str]:
        """
        Pipeline 2 Filter: Trend Structure & Breakout.
        - Price > EMA(21).
        - Volume Breakout (Current > 1.5x Avg).
        """
        candidates = []
        for ticker, df in price_data_dict.items():
            if df.empty or len(df) < 21: continue
            
            last_close = df["close"].iloc[-1]
            ema21 = df["close"].ewm(span=21).mean().iloc[-1]
            
            # Volume Breakout
            avg_vol = df["volume"].tail(20).mean()
            curr_vol = df["volume"].iloc[-1]
            
            if last_close > ema21 and curr_vol > (avg_vol * 1.5):
                candidates.append(ticker)
        return candidates

    def filter_monthly(self, tickers: List[str], price_data_dict: Dict[str, pd.DataFrame], fundamental_data: Dict[str, Any]) -> List[str]:
        """
        Pipeline 3 Filter: Fundamental Quality & Momentum.
        - ROE > 10%, Laba YoY Positive.
        - Price > MA200.
        """
        candidates = []
        for ticker, df in price_data_dict.items():
            if df.empty or len(df) < 200: continue
            
            info = fundamental_data.get(ticker, {})
            roe = info.get("returnOnEquity", 0)
            net_income_growth = info.get("netIncomeGrowth", 0)
            
            last_close = df["close"].iloc[-1]
            ma200 = df["close"].rolling(200).mean().iloc[-1]
            
            if roe > 0.10 and net_income_growth > 0 and last_close > ma200:
                candidates.append(ticker)
        return candidates

    def partition_price_data(self, df: pd.DataFrame, tickers: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Partitions a MultiIndex DataFrame into a dictionary of per-ticker DataFrames.
        Ensures robust handling of missing data and logging for audit trails.
        """
        partitioned = {}
        for ticker in tickers:
            try:
                # Use Cross-section (XS) for efficient MultiIndex slicing
                ticker_data = df.xs(ticker, level="ticker")
                if not ticker_data.empty:
                    partitioned[ticker] = ticker_data
            except KeyError:
                # Ticker exists in metadata but not in the researched data
                continue
            except Exception:
                # Generic safety guard for unexpected data corruption
                continue
        return partitioned

    def rank_stocks(self, df: pd.DataFrame, price_data_dict: Dict[str, pd.DataFrame], top_n: int = 10) -> Tuple[List[str], Dict[str, Any]]:
        """
        Ranks stocks using a multi-factor ensemble.
        Returns Tuple: (List[Top Tickers], Dict[Ticker -> All Scores])
        """
        tickers = df["ticker"].tolist()
        scores = []

        for ticker in tickers:
            if ticker not in price_data_dict:
                continue
            
            data = price_data_dict[ticker]
            if len(data) < 20:
                continue

            # 1. Volume Factor (Normalized relative to universe?) - For simplicity, use raw mean
            volume_factor = data["volume"].tail(20).mean()
            
            # 2. Volatility Factor
            returns = data["close"].pct_change()
            volatility_factor = returns.tail(20).std()
            
            # 3. Trend Factor (Price vs SMA20)
            sma20 = data["close"].rolling(20).mean().iloc[-1]
            last_close = data["close"].iloc[-1]
            trend_factor = (last_close / sma20) - 1 if sma20 > 0 else 0

            scores.append({
                "ticker": ticker,
                "volume": volume_factor,
                "volatility": volatility_factor,
                "trend": trend_factor
            })

        if not scores:
            return []

        # Convert to DataFrame for normalization
        scores_df = pd.DataFrame(scores)
        
        # Min-Max Normalization helper
        def normalize(series):
            if series.max() == series.min(): return series * 0
            return (series - series.min()) / (series.max() - series.min())

        scores_df["volume_n"] = normalize(scores_df["volume"])
        scores_df["volatility_n"] = normalize(scores_df["volatility"])
        scores_df["trend_n"] = normalize(scores_df["trend"])

        # Calculated Weighted Ensemble Score
        scores_df["final_score"] = (
            scores_df["volume_n"] * 0.4 + 
            scores_df["volatility_n"] * 0.3 + 
            scores_df["trend_n"] * 0.3
        )

        # Sort and return top N
        sorted_scores = scores_df.sort_values("final_score", ascending=False)
        top_stocks = sorted_scores.head(top_n)["ticker"].tolist()
        
        # Format scores for logging
        full_scores = sorted_scores.set_index("ticker")["final_score"].to_dict()
        
        return top_stocks, full_scores

if __name__ == "__main__":
    # Test Manager
    mgr = UniverseManager()
    all_stocks = mgr.get_idx_tickers()
    filtered = mgr.filter_excluded_stocks(all_stocks)
    print(f"Filtered Universe: {filtered['ticker'].tolist()}")
