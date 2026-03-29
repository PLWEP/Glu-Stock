# Glu-Stock Project Grounding

## Project Overview

Glu-Stock is an institutional-grade, multi-agent quantitative trading engine optimized for the IDX (Indonesia Stock Exchange). It features a 24/7 autonomous lifecycle, intelligent signal confirmation (Fundamentals + ML), and dual-platform monitoring via Telegram and WhatsApp.

## 🧠 Module Logic: Intelligence Layer (v3.1.0)

The Intelligence Layer adds a "brain" to the system to filter quality and predict confidence.

- **Fundamental Analyst Agent**: 
    - **Logic**: Evaluates stocks based on P/E, ROE, DER, and Dividend Yield.
    - **Scoring**: Composite score (0-1). Signals are only approved if score >= 0.6.
    - **Integration**: Filters the universe for long-term (Weekly/Monthly) pipelines.
- **ML Price Predictor (Decoupled)**:
    - **Strategy**: Offloads training to high-power PC/Laptop. Termux performs lean inference.
    - **Model**: Random Forest Classifier trained on 5+ years of historical data.
    - **Features**: RSI, MACD_diff, SMA, EMA, and Volatility.
    - **Confidence**: Every trade signal is assigned a probability (0-100%).
- **Status:** Production-ready & Decoupled.

## 🛡️ Module Logic: Hardening & Stability (v2.0.0)

System stability is enforced via aggressive log and error management.

- **Logging**: `JsonLogger` with `RotatingFileHandler` (5MB limit, 3 backups) and SQLite audit trail.
- **Alert Resilience**: Alert recursion guard prevents infinite loops during API or network failures.
- **Security**: WhatsApp command execution uses `child_process.spawn` with argument arrays to prevent shell injection.
- **Data Performance**: `StockDataHandler` uses bulk SQL `executemany` for 10x faster caching.
- **Strategic Accuracy**: VWAP calculation resets daily to ensure accurate intraday signals.

## ⚙️ Module Logic: Configuration (v1.5.0)

All technical and risk parameters are externalized in `config.yaml`.

- **Risk Management**: Mandatory Stop-Loss (SL), Take-Profit (TP), and Drawdown limits.
- **Profit Freeze**: Optional mechanism to lock capital when profit thresholds are met.
- **Strategy Specs**: Per-pipeline TP/SL, allocation percentage, and ML confidence thresholds.

## 🤖 Module Logic: Bots & Monitoring

- **Telegram Bot**: Interactive "Ayang" persona with button-based command center. Resilient polling with backoff.
- **WhatsApp Bot**: Baileys-based bridge for 24/7 alerts and dual-platform notifications.
- **Telemetry**: Real-time monitoring of RAM, Battery, and Temperature via Termux:API.

## 📂 Module Logic: Core Components

- **Universe Selection Agent**: Dynamic curation based on Rp25B/500k lot liquidity and LQ45 priority.
- **Research Agent**: Multi-interval data fetching (15m, 1h, 1d) with zero lookahead bias.
- **Execution Engine**: Paper trading with Long-Only enforcement and automated trade logging.

## Core Execution Rules

1. **Python Path**: `c:/Users/MP2NE93D/miniconda3/python.exe`.
2. **Commit Policy**: Conventional Commits (feat, fix, refactor).
3. **Environment Isolation**: Mandatory clean venv for test runs.
4. **Documentation Sync**: `README.md`, `changelog.md`, and `checkpoint.md` must be updated on every feature change.
