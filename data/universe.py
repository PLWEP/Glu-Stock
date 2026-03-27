import pandas as pd
import numpy as np
import os
from typing import List, Dict

class UniverseManager:
    """
    Manages the stock universe for the IDX market.
    Handles loading, strategic filtering (excluding Banks/BUMN), and factor ranking.
    """

    def __init__(self, csv_path: str = "data/idx_stocks.csv"):
        self.csv_path = csv_path
        if not os.path.exists(self.csv_path):
            self._create_sample_csv()

    def _create_sample_csv(self):
        """ Creates a default sample of IDX stocks if none exist. """
        data = [
            ["BBCA.JK", "BCA", "Financials", False],
            ["TLKM.JK", "Telkom", "Communication", True],
            ["ASII.JK", "Astra", "Industrials", False],
            ["BMRI.JK", "Mandiri", "Financials", True],
            ["GOTO.JK", "GoTo", "Technology", False],
        ]
        df = pd.DataFrame(data, columns=["ticker", "name", "sector", "is_bumn"])
        df.to_csv(self.csv_path, index=False)

    def get_idx_tickers(self) -> pd.DataFrame:
        """ Loads the full IDX universe from CSV. """
        return pd.read_csv(self.csv_path)

    def filter_excluded_stocks(self, df: pd.DataFrame) -> pd.DataFrame:
        """ 
        Excludes "Bank" (Financials sector) and "BUMN" (State-Owned Enterprises).
        """
        filtered = df[
            (df["sector"].str.lower() != "financials") & 
            (df["is_bumn"] == False)
        ]
        return filtered

    def rank_stocks(self, df: pd.DataFrame, price_data_dict: Dict[str, pd.DataFrame], top_n: int = 10) -> List[str]:
        """
        Ranks stocks using a multi-factor ensemble:
        - Volume (40%): Avg 20d Volume.
        - Volatility (30%): Std Dev of 20d returns.
        - Trend (30%): Distance from SMA20.
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
            volume_factor = data["Volume"].tail(20).mean()
            
            # 2. Volatility Factor
            returns = data["Close"].pct_change()
            volatility_factor = returns.tail(20).std()
            
            # 3. Trend Factor (Price vs SMA20)
            sma20 = data["Close"].rolling(20).mean().iloc[-1]
            last_close = data["Close"].iloc[-1]
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
        top_stocks = scores_df.sort_values("final_score", ascending=False).head(top_n)
        return top_stocks["ticker"].tolist()

if __name__ == "__main__":
    # Test Manager
    mgr = UniverseManager()
    all_stocks = mgr.get_idx_tickers()
    filtered = mgr.filter_excluded_stocks(all_stocks)
    print(f"Filtered Universe: {filtered['ticker'].tolist()}")
