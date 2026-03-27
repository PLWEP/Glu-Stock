import os
import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

class StockDataHandler:
    """
    Handles fetching and caching of stock OHLCV data using yfinance and SQLite.
    """

    def __init__(self, db_path: str = "data/cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite database and table."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ohlcv (
                    ticker TEXT,
                    date TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    PRIMARY KEY (ticker, date)
                )
            """)

    def fetch_data(self, tickers, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches OHLCV data for multiple tickers, using cache when available.
        """
        if isinstance(tickers, str):
            tickers = [tickers]

        all_data = []

        for ticker in tickers:
            data = self._get_ticker_data(ticker, start_date, end_date)
            all_data.append(data)

        if not all_data:
            return pd.DataFrame()

        # Combine all tickers into a single DataFrame
        final_df = pd.concat(all_data)
        
        # Handle missing data
        final_df = self.handle_missing_data(final_df)
        
        return final_df

    def _get_ticker_data(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """Fetches data for a single ticker, checking cache first."""
        # 1. Check cache
        cached_df = self._read_from_cache(ticker, start, end)
        
        # Determine missing ranges (simplified: if cache is empty or incomplete, re-download)
        # For simplicity in this version, if cache doesn't cover the full range, we download and upsert.
        # A more robust version would check gaps.
        
        # 2. Download from yfinance
        try:
            downloaded_df = yf.download(ticker, start=start, end=end, progress=False)
            if not downloaded_df.empty:
                # Format for SQLite
                downloaded_df.reset_index(inplace=True)
                downloaded_df['ticker'] = ticker
                # Rename columns if necessary (yfinance columns can be multi-index)
                if isinstance(downloaded_df.columns, pd.MultiIndex):
                    downloaded_df.columns = downloaded_df.columns.get_level_values(0)
                
                # Standardize column names to lowercase
                downloaded_df.columns = [c.lower() for c in downloaded_df.columns]
                
                # 3. Save to cache
                self._write_to_cache(downloaded_df)
                
                # Re-read from cache to be consistent
                return self._read_from_cache(ticker, start, end)
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
        
        return cached_df

    def _read_from_cache(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """Reads data from the SQLite cache."""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT * FROM ohlcv 
                WHERE ticker = ? AND date BETWEEN ? AND ?
                ORDER BY date ASC
            """
            df = pd.read_sql_query(query, conn, params=(ticker, start, end))
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index(['date', 'ticker'], inplace=True)
            return df

    def _write_to_cache(self, df: pd.DataFrame):
        """Writes data to the SQLite cache."""
        with sqlite3.connect(self.db_path) as conn:
            # Prepare for upsert
            for _, row in df.iterrows():
                conn.execute("""
                    INSERT OR REPLACE INTO ohlcv (ticker, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (row['ticker'], row['date'].strftime('%Y-%m-%d'), 
                      row['open'], row['high'], row['low'], row['close'], row['volume']))

    def handle_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handles missing data by forward filling and then backward filling.
        """
        if df.empty:
            return df
        
        # Sort by index (Date, Ticker)
        df.sort_index(inplace=True)
        
        # Forward fill then backward fill within each ticker group
        df = df.groupby(level='ticker', group_keys=False).apply(lambda x: x.ffill().bfill())
        
        # Drop any remaining NaNs (if entire ticker had No data)
        df.dropna(inplace=True)
        
        return df

if __name__ == "__main__":
    # Quick sanity check
    handler = StockDataHandler()
    data = handler.fetch_data(["AAPL", "MSFT"], "2024-01-01", "2024-01-10")
    print(data.head())
