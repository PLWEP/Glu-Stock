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
        Scans a list of tickers and returns the top 5 candidates by score.
        """
        if not tickers:
            return []

        print(f"MarketScanner: Scanning {len(tickers)} candidates...")
        
        # 1. Prepare Data for UniverseManager
        metadata = pd.DataFrame([{"ticker": t, "sector": "Unknown", "is_bumn": False} for t in tickers])
        
        # 2. Fetch and compute features
        try:
            df_researched = self.research_agent.research(tickers, start_date, end_date)
            if df_researched.empty:
                return []
        except Exception as e:
            print(f"MarketScanner Error: Research failed: {e}")
            return []
        
        # 3. Partition data for ranking
        price_data_dict = {}
        for ticker in tickers:
            try:
                # If ticker is missing from index or fails, continue to next
                ticker_data = df_researched.xs(ticker, level="ticker")
                if not ticker_data.empty:
                    price_data_dict[ticker] = ticker_data
            except (KeyError, Exception):
                continue

        # 4. Execute Multi-Factor Ranking
        _, all_scores = self.universe_manager.rank_stocks(
            metadata, 
            price_data_dict, 
            top_n=len(tickers)
        )
        
        # 5. Collection and Formatting (No threshold filtering)
        candidates = []
        for ticker, score in all_scores.items():
            candidates.append({
                "ticker": ticker,
                "score": round(score, 4)
            })
        
        # Sort by score descending and take top 5
        candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:5]
        
        print(f"Top candidates: {candidates}")
        return candidates

if __name__ == "__main__":
    # Mini integration test
    scanner = MarketScanner()
    results = scanner.scan(["AAPL", "TSLA", "MSFT"], threshold=0.1)
    print(f"Scan Results: {results}")
