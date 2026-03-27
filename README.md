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

from execution.execution import ExecutionEngine
engine = ExecutionEngine()
engine.execute_signals(signals_df, p)

from risk.risk import RiskManager
rm = RiskManager()
shares = rm.calculate_position_size(p.get_equity({"AAPL": 160}), 160, 0.05)
print(f"Risk-adjusted shares: {shares}")
print(p.get_total_pnl({"AAPL": 160}))

from agents.agents import ResearchAgent, StrategyAgent, TradingAgent
ra = ResearchAgent()
sa = StrategyAgent()
ta = TradingAgent()

data = ra.research(["AAPL"], "2024-01-01", "2024-03-01")
signals = sa.get_recommendations(data)
ta.trade(signals)

from reporting.report import ReportGenerator
rg = ReportGenerator()
rg.generate_html_report(
    {"Return": "15%"},
    pd.read_csv("execution/trade_log.csv"),
    pd.Series([100, 115])
)
```

## Project Structure

- `data/`: Data fetching and caching.
- `features/`: Technical indicator engineering.
- `strategies/`: Trading- `StrategyAgent` for signal generation and validation.
- `TradingAgent` for risk-aware portfolio execution.

## [0.9.0] - 2026-03-27

### Added

- `report.py` module for performance visualization.
- Institutional-grade HTML report generation with dark mode.
- Automated equity curve plotting using `matplotlib`.
- Standalone report exports with embedded assets.
  esting engine and performance metrics.
- `portfolio/`: Portfolio management and PnL tracking.
- `execution/`: Paper trading engine and trade logging.
- `risk/`: Risk management and position sizing.
- `agents/`: Multi-agent orchestration layer.
- `reporting/`: Performance reporting.
