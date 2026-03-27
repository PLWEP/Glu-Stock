# Glu-Stock

Quantitative Finance Framework for Stock Analysis.

## Installation

```bash
pip install yfinance pandas ruff
```

## Usage

### Data Module

```python
from data.data import StockDataHandler
handler = StockDataHandler()
df = handler.fetch_data(['AAPL', 'MSFT'], '2023-01-01', '2023-12-31')
```

## Project Structure

- `data/`: Data fetching and caching.
- `strategies/`: Trading strategies.
- `backtesting/`: Backtesting engine.
- `execution/`: Order execution.
- `reporting/`: Performance reporting.
