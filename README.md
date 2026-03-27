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

from orchestrator.orchestrator import Orchestrator
orch = Orchestrator()
summary = orch.run_full_pipeline(["AAPL", "TSLA"], "2024-01-01", "2024-03-01")
print(f"Workflow Summary: {summary['tickers_processed']}")

from utils.config import ConfigLoader
print(f"Trading with {config['capital']} capital on {config['tickers']}")

from utils.logger import JsonLogger
logger = JsonLogger()
logger.info("Pipeline started", tickers=["BBCA.JK"])
```

## Project Structure

- `data/`: Data fetching and caching.
- `features/`: Technical indicator engineering.
- `strategies/`: Trading strategies and signal generation.
- `backtesting/`: Vectorized backtesting engine and performance metrics.
- `portfolio/`: Portfolio management and PnL tracking.
- `execution/`: Paper trading engine and trade logging.
- `risk/`: Risk management and position sizing.
- `agents/`: Multi-agent orchestration layer.
- `orchestrator/`: Full-pipeline orchestration and resilience.
- `reporting/`: Performance reporting.
- `utils/`: Miscellaneous utilities (Configuration, etc.).

## [0.9.0] - 2026-03-27

### Added

- `report.py` module for performance visualization.
- Institutional-grade HTML report generation with dark mode.
- Automated equity curve plotting using `matplotlib`.

## [1.0.0] - 2026-03-27

### Added

- `orchestrator.py` module for full-pipeline automation.
- Robust error handling for multi-ticker trading workflows.
- Unified entry point for end-to-end strategy execution.
- Consolidated reporting integration in the orchestrator.
- Final production-ready stabilizing of all core modules.

## [1.1.0] - 2026-03-27

### Added

- Centralized `config.yaml` for trading parameters (IDX focused).
- `ConfigLoader` utility with robust validation and defaults.
- Support for externalized capital and risk management.
- Comprehensive unit tests for the configuration system.

## [1.2.0] - 2026-03-27

### Added

- Structured JSON logging system in `utils/logger.py`.
- Dual output to console and `logs/trading.log`.
- Support for `INFO` and `ERROR` levels with arbitrary metadata.
- Automated log directory creation.
- Standalone report exports with embedded assets.
