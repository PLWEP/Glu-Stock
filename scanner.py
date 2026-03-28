import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from utils.logger import JsonLogger
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
        self.logger = JsonLogger(log_file="logs/scanner.log")

    def scan(self, tickers: List[str], threshold: float = 0.5, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scans a list of tickers and returns the top 5 candidates by score.
        If dates are not provided, defaults to 1-year lookback.
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

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
            self.logger.error("MarketScanner: Research phase failed", error=str(e))
            return []
        
        # 3. Partition data for ranking (DRY Refactored)
        price_data_dict = self.universe_manager.partition_price_data(df_researched, tickers)

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
        
        self.logger.info("MarketScanner: Scan complete", 
                         tickers_scanned=len(tickers), 
                         top_candidates=[c['ticker'] for c in candidates])
        return candidates

if __name__ == "__main__":
    # Mini integration test
    scanner = MarketScanner()
    results = scanner.scan(["AAPL", "TSLA", "MSFT"], threshold=0.1)
    print(f"Scan Results: {results}")
