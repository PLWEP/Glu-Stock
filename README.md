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
from features.features import FeatureEngineer

handler = StockDataHandler()
df = handler.fetch_data(['AAPL', 'MSFT'], '2023-01-01', '2023-12-31')

engineer = FeatureEngineer()
featured_df = engineer.add_indicators(df)
featured_df = engineer.clean_features(featured_df)

from strategies.strategy import TradingStrategy
strategy = TradingStrategy()
signals_df = strategy.generate_signals(featured_df)

from backtesting.backtest import VectorizedBacktester
backtester = VectorizedBacktester(transaction_cost=0.001)
results_df = backtester.run_backtest(signals_df)
metrics = backtester.get_metrics()
print(metrics)

from portfolio.portfolio import Portfolio
p = Portfolio(initial_cash=100000)
p.update_position("AAPL", 10, 150, "BUY")
print(p.get_total_pnl({"AAPL": 160}))
```

## Project Structure

- `data/`: Data fetching and caching.
- `features/`: Technical indicator engineering.
- `strategies/`: Trading strategies and signal generation.
- `backtesting/`: Vectorized backtesting engine and performance metrics.
- `portfolio/`: Portfolio management and PnL tracking.
- `execution/`: Order execution.
- `reporting/`: Performance reporting.
