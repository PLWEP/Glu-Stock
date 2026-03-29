# Glu-Stock Project Grounding

## Project Overview

Glu-Stock is an institutional-grade, multi-agent quantitative trading engine optimized for the IDX (Indonesia Stock Exchange). It features a 24/7 autonomous lifecycle, ensemble intelligence (RF + CNN), and dual-platform monitoring.

## 🧠 Module Logic: Deep Intelligence (v11.0)

The pinnacle of the engine's cognitive ability, combining multiple ML paradigms.

- **Dual-Brain Ensemble**: 
    - **Brain 1 (RF)**: Scikit-learn Random Forest for tabular/technical indicators.
    - **Brain 2 (CNN)**: 10-layer 1D-Convolutional Neural Network for temporal/visual price patterns.
    - **Logic**: Symmetrical voting system requiring high-confidence agreement for `🧠` signals.
- **TFLite Conversion**: Models are trained on PC (Keras) and converted to `.tflite` for low-latency inference on Termux.
- **10-Channel Input**: Ingests raw OHLCV and Adjusted OHLCV for maximum pattern transparency.

## 📊 Module Logic: Strategic Master (v8.0.0)

- **Inter-Strategy Allocation**: Dynamic rebalancing between Daily, Weekly, and Monthly pipelines based on Sharpe ratios.
- **Expectancy Safeguard**: Automated "Gatekeeper" that pauses underperforming strategies (Ex < 0).
- **Rolling Matrix**: Rolling 30-day covariance with Ledoit-Wolf shrinkage for IDX stability.

## 🔬 Module Logic: Quantitative Validation (v7.0.0)

- **OOS Testing**: 80/20 train-test split to identify overfitting.
- **Monte Carlo Simulation**: 1000 randomized timelines to calculate Risk of Ruin.
- **Market Regime Guard**: Monitors IHSG (`^JKSE`) vs EMA 200. Automatically scales down size (50%) during Bear regimes.

## 🛡️ Module Logic: Resilience & Monitoring (v4.0.0)

- **Hardware Throttling**: Pauses if Temp > 45°C or Battery < 15%.
- **ATR Trailing Stop**: Dynamic protective floor for unrealized gains.
- **Panic Exit**: Instant `/panic` command to liquidate all clusters.

## 🤖 Module Logic: Bots & Configuration

- **Telegram Bot**: Interactive "Ayang" persona.
- **WhatsApp Bot**: Baileys-based bridge for 24/7 mirroring.
- **PC Command Center**: Menu-driven `setup_pc.bat` for training, testing, and monitoring.

## Core Execution Rules

1. **Python Path**: `c:/Users/MP2NE93D/miniconda3/python.exe`.
2. **Environment**: Use `pc_venv` on Windows and `glustock_venv` on Termux.
3. **Commit Policy**: Conventional Commits (feat, fix, refactor).
4. **Documentation Sync**: Every feature update must reflect in `README.md`, `changelog.md`, and `checkpoint.md`.
