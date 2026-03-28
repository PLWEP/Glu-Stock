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
- **Scoring Engine:** Composite multi-factor score (0-1) combining RSI (30%), MACD (30%), Trend (20%), and Volume (20%).
- **Aggregation:** Maps composite score to discrete signals (>0.7 for BUY, <0.3 for SELL).
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

- **Pipeline:** Coordinates selection -> Research -> Strategy -> Trading -> Reporting.
- **Dynamic Selection:** Integrates `UniverseSelectionAgent` for automatic ticker curation if none are provided.
- **Resilience:** Per-ticker isolation and error handling.
- **Reporting:** Automatic generation of consolidated performance dashboards.
- **Status:** Production-ready.

## Module Logic: Configuration Module

The Configuration Module manages externalized trading parameters using YAML.

- **File:** `config.yaml` for capital, risk, and IDX## Architecture Snapshot (v1.5.0)
- **Data Layer**: `StockDataHandler` supports multi-interval (1d, 15m, 1h) caching with intraday granularity.
- **Curation Layer**: `UniverseManager` enforces institutional liquidity floors (>Rp25B/day) and LQ45/Kompas100 priority.
- **Strategy Layer**: Institutional dispatcher for 15m Daily (Pivot/VWAP), 1d Weekly (3-EMA), and Position Monthly (Momentum/Fundamental).
- **Execution Engine**: Implements trailing stop-loss (MA20) and strict Long-Only compliance for IDX.
  d risk percentage (0-1).
- **Status:** Hardened.

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
- **Tables:**
    - `trades`: tracks id, ticker, entry/exit prices, qty, dates, pnl, status (OPEN/CLOSED), strategy, and timeframe.
    - `portfolio_snapshots`: tracks date, equity, cash, and positions_value.
- **Resilience:** Explicit connection management for Windows and Termux compatibility.
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
- **UniverseSelectionAgent:** Orchestrates metadata filtering and data-driven ranking to curate the daily trading universe.
- **Status:** Production-ready.

## Module Logic: Deployment Module

The Deployment Module provides institutional process management using PM2.

- **Entry Point:** `main.py` (One-shot execution of the full pipeline).
- **Process Manager:** `ecosystem.config.js`.
- **Scheduling:** Automated weekday 09:00 AM start via PM2 cron.
- **Resource Limits:** 500MB memory limit with automated restart.
- **Status:** Production-ready.

## Module Logic: Market Scanner Module

The Market Scanner Module provides lightweight candidate evaluation against scoring thresholds.

- **Logic:** Fetches data -> Computes factors -> Filters by threshold.
- **Scoring:** Reuses `UniverseManager` multi-factor ensemble (Volume, Volatility, Trend).
- **Return:** Sorted list of tickers exceeding the `threshold`.
- **Status:** Production-ready.

## Module Logic: Performance Module

The Performance Module calculates institutional-grade trading metrics from realized trades and portfolio snapshots.

- **Metrics:** Win Rate, Total Return, Average Win/Loss, Max Drawdown.
- **Resilience:** Built-in guards for empty data and zero-capital scenarios.
- **Efficiency:** Vectorized calculations for speed across all environments.
- **Status:** Production-ready.

## Module Logic: Text Report Module

The Text Report Module generates human-readable Markdown summaries for Telegram.

- **Periods:** Daily, Weekly, Monthly.
- **Metrics:** Equity, Total Return, Win Rate, Max Drawdown, and recent trades list.
- **Formatting:** Optimized for mobile display with clean emojis and Markdown.
- **Status:** Production-ready.

## Module Logic: Telegram Integration Module

The Telegram Integration Module provides real-time monitoring and control of the trading engine.

- **Bot Commands:** `/status` (health), `/portfolio` (detailed performance), `/report [daily|weekly|monthly]` (periodic summaries).
- **Alert Triggers:** Real-time `BUY` icons, errors, and automated end-of-session reports.
- **Efficiency:** Optimized `handle_status` with `os.seek()` for O(1) log tailing.
- **Diagnostics:** Strict debug logging in `send_message` and standalone `--test` connectivity mode.
- **Provider:** Integrated bot listener and proactive orchestrator alerts.
- **Data Source:** Direct consumption of `TradingDatabase` and `TextReportGenerator`.
- **Status:** Hardened.

## Core Execution Rules

1. Python: `c:/Users/MP2NE93D/miniconda3/python.exe`.
2. Environment Isolation: Mandatory clean environments for tests.
3. Documentation: Keep `README.md`, `changelog.md`, and `checkpoint.md` in sync.
4. Linting: Strict `ruff` enforcement.
