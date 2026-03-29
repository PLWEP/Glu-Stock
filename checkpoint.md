# Glu-Stock Project Grounding

## Project Overview

Glu-Stock is an institutional-grade, multi-agent quantitative trading engine optimized for the IDX (Indonesia Stock Exchange). It features a 24/7 autonomous lifecycle, ensemble intelligence (RF + CNN), and an Institutional Core based on Trend-Following and Risk Parity.

## 🏛️ Module Logic: Institutional Core (v12.0)

The foundational risk and strategy layer, transforming the bot into a Target-Exposure Fund Manager.

- **Trend-Following Backbone**: Uses EMA of volatility-normalized returns (Return / EWMA_Vol) to filter noise.
- **Linear Conviction**: Signals range from -1.0 to +1.0, defining target exposure levels rather than binary choices.
- **Agnostic Risk Parity (ARP)**: Portfolio weights are derived from the inverse of the correlation matrix square root ($\Sigma^{-1/2}$), distributing risk uniformly across assets.
- **Basket Trading**: Optimized for High-N portfolios (especially in Daily pipeline) to leverage statistical mean-reversion and cross-asset stability.

## 🧠 Module Logic: Deep Intelligence (v11.0)

- **Dual-Brain Ensemble**: 
    - **Brain 1 (RF)**: Scikit-learn Random Forest for tabular analysis.
    - **Brain 2 (CNN)**: 10-layer 1D-CNN for temporal pattern recognition.
- **TFLite Conversion**: Models converted to `.tflite` for low-latency Termux execution.

## 📊 Module Logic: Strategic Master (v8.0.0)

- **Inter-Strategy Allocation**: Dynamic rebalancing between Daily, Weekly, and Monthly clusters based on Sharpe ratios.
- **Expectancy Safeguard**: Automated gatekeeper that pauses strategies with negative statistical edge.

## 🔬 Module Logic: Quantitative Validation (v7.0.0)

- **OOS Testing**: 80/20 train-test split for parameter validation.
- **Monte Carlo Simulation**: 1000 randomized scenarios to determine Risk of Ruin.
- **Market Regime Guard**: Automatic size scaling (50%) during Bearish IHSG regimes.

## 🛡️ Module Logic: Resilience & Monitoring

- **Hardware Throttling**: Battery/Thermal protection.
- **ATR Trailing Stop**: Dynamic profit protection.
- **Dual-Platform Bot**: Telegram (Ayang persona) and WhatsApp (Mirroring).

## Core Execution Rules

1. **Python Path**: `c:/Users/MP2NE93D/miniconda3/python.exe`.
2. **Environment**: `pc_venv` (Windows) / `glustock_venv` (Termux).
3. **Commit Policy**: Conventional Commits.
4. **Documentation Sync**: Always update `README.md`, `changelog.md`, and `checkpoint.md`.
