# Glu-Stock Project Grounding

## Project Overview

Glu-Stock is an institutional-grade, multi-agent quantitative trading engine optimized for the IDX (Indonesia Stock Exchange). It features a 24/7 autonomous lifecycle, intelligent signal confirmation, and dual-platform monitoring.

## 📊 Module Logic: Strategic Master (v8.0.0)

Final layer of quant-governance to avoid fixed-parameter traps.

- **Inter-Strategy Allocation**: 
    - **Logic**: Dynamically rebalances capital between Daily, Weekly, and Monthly pipelines.
    - **Weighting**: Uses Sharpe/Sortino-based Inverse Variance weighting.
- **Expectancy Safeguard**:
    - **Gatekeeper**: Automated check before every scan. If a strategy's 30-day Expectancy is < 0, the scan is skipped and alerted.
- **Rolling Matrix**:
    - **Method**: Rolling 30-day Covariance with Ledoit-Wolf Shrinkage for high stability in volatile IDX market shifts.

## 🔬 Module Logic: Quantitative Validation (v7.0.0)

Scientific verification before capital exposure.

- **Out-of-Sample (OOS) Testing**: Splits historical data into train/test sets. Validates signals on unseen data with 0.3% slippage.
- **Monte Carlo Simulation**: Shuffles historical trades 1000 times to calculate **Risk of Ruin** and worst-case drawdowns.
- **Statistical Pulse**: Every report includes **Expectancy (Value per trade)** and **Confidence Score** (based on sample size N).

## 🏦 Module Logic: Money Management (v6.0.0)

Professional position sizing beyond fixed percentages.

- **Volatility Targeting**: Uses ATR to size positions so each trade has an equal impact on the portfolio.
- **Kelly Criterion**: Mathematically maximizes growth using real win rates and reward-to-risk ratios.

## 🛡️ Module Logic: Resilience & Monitoring (v4.0.0)

- **Hardware-Aware Throttling**: PSUtil-based monitoring. Pauses if Temp > 45°C or Battery < 15%.
- **ATR Trailing Stop**: Only moves UP to protect unrealized gains during vertical price action.
- **Panic Exit**: Instant `/panic` command to liquidate all clusters immediately.

## 🧠 Module Logic: Intelligence Layer (v3.1.0)

The Intelligence Layer adds a "brain" to the system to filter quality and predict confidence.

- **Fundamental Analyst Agent**: Evaluates stocks based on P/E, ROE, DER, and Dividend Yield.
- **ML Price Predictor (Decoupled)**: Offloads training to high-power PC/Laptop. Termux performs lean inference.

## 🛡️ Module Logic: Hardening & Stability (v2.0.0)

- **Logging**: `JsonLogger` with `RotatingFileHandler` (5MB limit) and SQLite audit trail.
- **Alert Resilience**: Alert recursion guard prevents infinite loops.
- **Data Performance**: `StockDataHandler` uses bulk SQL `executemany` for 10x faster caching.

## 🤖 Module Logic: Bots & Configuration

- **Telegram Bot**: Interactive "Ayang" persona.
- **WhatsApp Bot**: Baileys-based bridge for 24/7 mirroring.
- **Strategy Specs**: Parameters centralized in `config.yaml`.

## Core Execution Rules

1. **Python Path**: `c:/Users/MP2NE93D/miniconda3/python.exe`.
2. **Commit Policy**: Conventional Commits (feat, fix, refactor).
3. **Environment Isolation**: Mandatory clean venv for test runs.
4. **Documentation Sync**: `README.md`, `changelog.md`, and `checkpoint.md` must be updated on every feature change.
