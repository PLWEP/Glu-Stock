# Glu-Stock Project Grounding

## Project Overview

Glu-Stock is an institutional-grade, multi-agent quantitative trading engine optimized for the IDX (Indonesia Stock Exchange). It features a 24/7 autonomous lifecycle, ensemble intelligence (RF + CNN), and a math-driven Institutional Core (ARP + Linear Trend).

## 🤖 Platform Consolidation (v14.1.0)

The system is now fully hardened and focused exclusively on the **Telegram Bot** for personal professional use.

- **Unified Training Fixed**: Resolved all execution errors (Unicode, Missing Features) for the RF and CNN brains.
- **Backtest Lab Restored**: Menu option [3] in `setup_pc.bat` is now fully operational with the `HistoricalBacktester` correctly integrated.
- **History Module Sync**: Consistently logs all scan and trade events with comprehensive Telegram Command Support.
- **Telegram Interface**: All commands, reports, and alerts are delivered directly to the user's private Telegram chat.

## 🏛️ Module Logic: Institutional Core (v12.0)

The foundational risk and strategy layer, transforming the bot into a Target-Exposure Fund Manager.

- **Trend-Following Backbone**: Uses EMA of volatility-normalized returns (Return / EWMA_Vol).
- **Linear Conviction**: Signals range from -1.0 to +1.0, defining target exposure levels.
- **Agnostic Risk Parity (ARP)**: Portfolio weights derived from Sigma^-1/2.
- **Basket Trading**: Optimized for High-N portfolios (Daily pipeline).

## 🧠 Module Logic: Deep Intelligence (v11.0)

- **Dual-Brain Ensemble**: 
    - **Brain 1 (RF)**: Scikit-learn Random Forest.
    - **Brain 2 (CNN)**: 10-layer 1D-CNN.
- **TFLite Conversion**: Models optimized for low-latency Termux execution.

## 📊 Module Logic: Strategic Master (v8.0.0)

- **Inter-Strategy Allocation**: Dynamic rebalancing based on Sharpe ratios.
- **Expectancy Safeguard**: Gatekeeper pausing underperforming strategies.

## 🛡️ Module Logic: Resilience & Monitoring

- **Hardware Throttling**: Battery/Thermal protection.
- **ATR Trailing Stop**: Dynamic protective floor.
- **Telegram Bot**: Ayang persona for real-time monitoring and control.

## Core Execution Rules

1. **Python Path**: `c:/Users/MP2NE93D/miniconda3/python.exe`.
2. **Environment**: `pc_venv` (Windows) / `glustock_venv` (Termux).
3. **Commit Policy**: Conventional Commits.
4. **Documentation Sync**: Always update `README.md`, `changelog.md`, and `checkpoint.md`.
