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

# Run Automation
# python scheduler.py --loop
# OR Manual Trigger
# python scheduler.py --now

# Market Scanner execution
# python scanner.py --tickers AAPL,TSLA,MSFT --threshold 0.5
from scanner import MarketScanner
scanner = MarketScanner()
results = scanner.scan(["BBCA.JK", "ASII.JK", "TLKM.JK"], threshold=0.3)

# Telegram Bot execution
python telegram_bot.py

# Deployment with PM2
pm2 start ecosystem.config.js
```

## Telegram Integration

To enable the Telegram bot:

1. Create a bot via [@BotFather](https://t.me/BotFather) and get the token.
2. Get your Chat ID via [@userinfobot](https://t.me/userinfobot).
3. Update `config.yaml` with your credentials and set `enabled: true`.

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

## [1.3.0] - 2026-03-27

### Added

- Automated trading scheduler in `scheduler.py`.
- Support for weekday execution at 09:00 AM using the `schedule` library.
- CLI interface with `--now` (manual trigger) and `--loop` (daemon mode).
- Integration with `PipelineOrchestrator` for end-to-end automation.

## [1.4.0] - 2026-03-27

### Added

- Persistent SQLite storage layer in `data/database.py`.
- Automated schema creation for `trades` and `portfolio_history`.
- High-integrity transaction management for cross-platform reliability.
- Support for historical execution and performance auditing.

## [1.5.0] - 2026-03-27

### Added

- Universe selection engine in `data/universe.py`.
- Metadata-driven IDX universe management via `data/idx_stocks.csv`.
- Strategic filtering logic (Bank/BUMN exclusion).
- Multi-factor ranking system (Volume, Volatility, Trend).

## [1.6.0] - 2026-03-27

### Added

- `UniverseSelectionAgent` in `agents/agents.py`.
- Autonomous orchestration of metadata filtering and market research.
- Data-driven ranking and Top N selection for trading pipelines.
- Integrated `UniverseManager` and `ResearchAgent` into a unified agent workflow.

## [1.7.0] - 2026-03-27

### Added

- Integrated `UniverseSelectionAgent` into `PipelineOrchestrator`.
- Support for dynamic, data-driven universe curation in the main pipeline.
- Automatic fallback to autonomous selection when no tickers are provided.

## [1.8.0] - 2026-03-27

### Added

- PM2 deployment configuration in `ecosystem.config.js`.
- One-shot entry point `main.py` for scheduled execution.
- Automated weekday 09:00 AM cron orchestration.
- Memory limiting (500MB) and resource guarding.

## [1.9.0] - 2026-03-27

### Added

- Enhanced score logging in `agents/agents.py`.
- Audit trail for multi-factor ranking in `logs/universe_selection.log`.
- Structured JSON output of candidate scores (Volume, Volatility, Trend).
- Detailed selection reporting for daily session transparency.

## [1.10.0] - 2026-03-27

### Added

- New `MarketScanner` module in `scanner.py`.
- Threshold-based candidate filtering for targeted watchlists.
- Integration with `ResearchAgent` for real-time indicator computation.
- Automated score sorting for immediate prioritization.

## [1.11.0] - 2026-03-27

### Added

- Multi-factor strategy scoring engine in `strategies/strategy.py`.
- Continuous composite score (0-1) replacing discrete rule-based signals.
- Weighted ensemble: RSI (30%), MACD (30%), Trend (20%), and Volume (20%).
- Signal thresholding (>0.7 BUY, <0.3 SELL) for execution compatibility.

## [1.12.0] - 2026-03-27

### Added

- Standalone Telegram Bot in `telegram_bot.py`.
- Support for `/status` and `/portfolio` commands via Telegram Bot API.
- Real-time monitoring of engine health and portfolio snapshots.
- Lightweight polling architecture using the `requests` library.

## [1.13.0] - 2026-03-27

### Added

- Integrated Telegram alerts for trade executions (BUY).
- Automated error notifications hooked into `JsonLogger`.
- Daily session summary reports sent via Telegram upon pipeline completion.
- Centralized `utils/alerts.py` utility for one-off notifications.

## [1.14.0] - 2026-03-27

### Changed

- Upgraded `data/database.py` with granular trade and portfolio tracking.
- Implemented `trades` table with entry/exit, qty, pnl, status, strategy, and timeframe.
- Implemented `portfolio_snapshots` table with `positions_value` support.
- Added institutional-grade trade lifecycle functions: `insert_trade`, `update_trade_close`.

## [1.15.0] - 2026-03-27

### Added

- Centralized `utils/performance.py` for advanced metrics calculation.
- Support for Win Rate, Total Return, and Max Drawdown analysis.
- Robust handling of empty data and zero-capital edge cases.

## [1.16.0] - 2026-03-27

### Added

- Centralized `utils/text_report.py` for Telegram-friendly reporting.
- Automated generation of Daily, Weekly, and Monthly performance summaries.
- Enhanced reporting with emojis and formatted trade logs.

## [1.17.0] - 2026-03-27

### Added

- Advanced Telegram bot commands: `/report daily`, `/report weekly`, `/report monthly`.
- Automated session-end reporting integrated into `PipelineOrchestrator`.
- Enhanced `/portfolio` command with comprehensive performance metrics.

## [1.18.0] - 2026-03-27

### Added

- Multi-timeframe strategy support for `daily`, `weekly`, `monthly`, and `yearly` intervals.
- Specialized factor weighting logic tailored for different investment horizons.
- Strict "no lookahead bias" enforcement across all timeframes.

## [1.19.0] - 2026-03-27

### Added

- Strict telemetry logging in `PipelineOrchestrator` (Scanned, Candidates, Executed).
- Forced reporting protocol ensuring daily reports are sent regardless of activity levels.
- Robust fallback and error handling for Telegram report generation.

## [1.20.0] - 2026-03-27

### Added

- Strict debug logging in `telegram_bot.py` for API interaction traceability.
- Standalone connectivity test mode (`python telegram_bot.py --test`).
- Full error reporting for failed Telegram messaging attempts.

## [1.21.0] - 2026-03-27

### Fixed

- Strict reporting logic in `TextReportGenerator` to ensure messages are never empty.
- Added mandatory timestamps and portfolio valuation to all periodic reports.
- Implemented explicit "No trades executed" fallback message for zero-activity periods.

## [1.22.0] - 2026-03-27

### Added

- Debug functions `count_trades()` and `count_open_positions()` to `TradingDatabase`.
- Real-time transaction logging with total trade counters in `insert_trade` and `update_trade_close`.
- Enhanced exception handling in database operations to prevent silent failures.

## [1.23.0] - 2026-03-27

### Changed (DEBUG MODE)

- Temporarily lowered bullish strategy threshold to `0.5` (from 0.7) to ensure trade execution during testing.
- Added real-time per-ticker score logging in `TradingStrategy`.

## [1.24.0] - 2026-03-27

### Refactored

- Transitioned `TradingStrategy` to a continuous scoring system.
- Implemented normalized RSI (`(50-RSI)/50`), MACD Sigmoid, and SMA Slope Trend logic.
- Standardized ensemble weighting: 30% RSI, 30% MACD, 20% Trend, 20% Volume.
- Updated signal mapping to continuous BUY (>0.5) / HOLD logic with high-fidelity logging.

## [1.25.0] - 2026-03-27

### Changed

- Refactored `MarketScanner` to a competitive Top-N selection model (top 5 candidates).
- Removed binary threshold filtering to ensure system output visibility on every scan.
- Hardened scanner loop with resilient try-except blocks for per-ticker data gaps.
- Standardized `UniverseManager` to lowercase column schema for pipeline consistency.
- Log-integrated selection process for auditability.
- Standalone report exports with embedded assets.
