import pandas as pd
from typing import List, Dict, Any, Optional
from agents.agents import ResearchAgent
from data.universe import UniverseManager

class MarketScanner:
    """
    Evaluates a specific list of tickers against scoring thresholds.
    Provides immediate identification of high-potential assets.
    """
    def __init__(self, research_agent: Optional[ResearchAgent] = None):
        self.research_agent = research_agent or ResearchAgent()
        self.universe_manager = UniverseManager()

    def scan(self, tickers: List[str], threshold: float = 0.5, start_date: str = "2024-01-01", end_date: str = "2024-03-27") -> List[Dict[str, Any]]:
        """
        Scans a list of tickers and returns those satisfying the score threshold.
        """
        if not tickers:
            return []

        print(f"MarketScanner: Scanning {len(tickers)} candidates with threshold {threshold}...")
        
        # 1. Prepare Data for UniverseManager
        # We need a dummy metadata DataFrame for rank_stocks to work natively.
        metadata = pd.DataFrame([{"ticker": t, "sector": "Unknown", "is_bumn": False} for t in tickers])
        
        # 2. Fetch and compute features
        df_researched = self.research_agent.research(tickers, start_date, end_date)
        
        # 3. Partition data for ranking
        price_data_dict = {}
        for ticker in tickers:
            try:
                ticker_data = df_researched.xs(ticker, level="ticker")
                if not ticker_data.empty:
                    price_data_dict[ticker] = ticker_data
            except KeyError:
                continue

        # 4. Execute Multi-Factor Ranking
        # Note: UniverseManager.rank_stocks returns (Top Tickers, All Scores Dictionary)
        _, all_scores = self.universe_manager.rank_stocks(
            metadata, 
            price_data_dict, 
            top_n=len(tickers) # Get all candidate scores
        )
        
        # 5. Threshold Filtering and Formatting
        candidates = []
        for ticker, score in all_scores.items():
            if score >= threshold:
                candidates.append({
                    "ticker": ticker,
                    "score": round(score, 4)
                })
        
        # Sort by score descending
        candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
        
        print(f"MarketScanner: Found {len(candidates)} candidates above threshold.")
        return candidates

if __name__ == "__main__":
    # Mini integration test
    scanner = MarketScanner()
    results = scanner.scan(["AAPL", "TSLA", "MSFT"], threshold=0.1)
    print(f"Scan Results: {results}")
