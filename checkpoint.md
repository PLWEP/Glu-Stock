# Glu-Stock Project Grounding

## Project Overview

Glu-Stock is a Python-based quantitative finance framework for stock analysis and backtesting.

## Module Logic: Data Module

The Data Module is responsible for fetching and caching OHLCV data.

- **Provider:** Yahoo Finance via `yfinance`.
- **Caching:** Local SQLite database (`data/cache.db`).
- **Data Integrity:** Fully verified with tests (NaN checks, multi-ticker support).
- **Status:** Production-ready.

## Module Logic: Strategy Module

The Strategy Module generates trading signals using rule-based (RSI, MACD) and optional ML-based logic.

- **Rule-based:** RSI < 30 (BUY), RSI > 70 (SELL), and MACD crossovers.
- **Aggregation:** Combined signal (-1, 0, 1) and confidence (0-1).
- **Status:** Production-ready.

## Module Logic: Backtest Module

The Backtest Module simulates trading strategies using vectorized execution for performance.

- **Engine:** Vectorized backtesting (Group-by ticker).
- **Costs:** Configurable transaction costs (slippage/commission).
- **Metrics:** Sharpe Ratio, Max Drawdown, Total Return.
- **Status:** Production-ready.

## Module Logic: Portfolio Module

The Portfolio Module tracks active positions, cash balances, and calculates performance metrics like PnL and Equity.

- **Tracking:** Real-time cash and asset positions (shares, average cost).
- **PnL:** Supports realized and unrealized PnL calculation.
- **Status:** Production-ready.

## Module Logic: Execution Module

The Execution Engine translates strategy signals into portfolio actions and maintains a trade log.

- **Paper Trading:** Long-only execution of BUY/SELL signals.
- **Logging:** Detailed CSV logging in `execution/trade_log.csv`.
- **Integration:** Directly updates the `Portfolio` instance.
- **Status:** Production-ready.

## Module Logic: Feature Module

The Feature Module computes technical indicators while ensuring zero lookahead bias and multi-ticker isolation.

- **Library:** `ta` (Technical Analysis Library in Python).
- **Supported Indicators:** RSI, MACD, SMA, EMA, Bollinger Bands.
- **Data Integrity:** Group-by-ticker processing to prevent data leakage.
- **Status:** Production-ready.

## Module Logic: Orchestrator Module

The Orchestrator provides a high-level entry point for multi-ticker trading workflows.

- **Pipeline:** Coordinates Research -> Strategy -> Trading -> Reporting.
- **Resilience:** Per-ticker isolation and error handling.
- **Reporting:** Automatic generation of consolidated performance dashboards.
- **Status:** Production-ready.

## Module Logic: Configuration Module

The Configuration Module manages externalized trading parameters using YAML.

- **File:** `config.yaml` for capital, risk, and IDX tickers.
- **Loader:** `ConfigLoader` handles parsing, validation, and defaults.
- **Safety:** Enforces positive capital and valid risk percentage (0-1).
- **Status:** Production-ready.

## Module Logic: Logging Module

The Logging Module provides structured JSON logging for auditability.

- **Format:** JSON strings containing timestamp, level, message, and metadata.
- **Output:** Dual output to console and `logs/trading.log`.
- **Levels:** Support for `INFO` and `ERROR`.
- **Status:** Production-ready.

## Module Logic: Scheduler Module

The Scheduler Module automates the execution of the trading pipeline.

- **Timing:** Every weekday Monday-Friday at 09:00 AM.
- **Triggers:** Supports both background loop (`--loop`) and immediate manual trigger (`--now`).
- **Integration:** Coordinates `ConfigLoader`, `PipelineOrchestrator`, and `JsonLogger`.
- **Status:** Production-ready.

## Module Logic: Persistence Module

The Persistence Module manages long-term storage of trading data using SQLite.

- **Database:** `data/trading.db`.
- **Tables:** `trades` for execution history, `portfolio_history` for equity tracking.
- **Resilience:** Explicit connection management for Windows compatibility.
- **Status:** Production-ready.

## Module Logic: Universe Selection Module

The Universe Selection Module manages the dynamic pool of tradable stocks for the IDX market.

- **Data Source:** `data/idx_stocks.csv` (Ticker, Sector, BUMN status).
- **Filtering:** Automatically excludes Financials and BUMN stocks.
- **Ranking:** Weighted ensemble scoring (Volume 40%, Volatility 30%, Trend 30%).
- **Selection:** Returns the Top N stocks for the trading pipeline.
- **Status:** Production-ready.

## Module Logic: Agents Module

The Agents Module provides an orchestration layer using a multi-agent system.

- **ResearchAgent:** Orchestrates data fetching and feature engineering.
- **StrategyAgent:** Handles signal generation and backtesting.
- **TradingAgent:** Coordinates risk-managed execution and portfolio state.
- **Status:** Production-ready.

## Core Execution Rules

1. Python: `c:/Users/MP2NE93D/miniconda3/python.exe`.
2. Environment Isolation: Mandatory clean environments for tests.
3. Documentation: Keep `README.md`, `changelog.md`, and `checkpoint.md` in sync.
4. Linting: Strict `ruff` enforcement.
