# Glu-Stock 💹

Kaggle-native quantitative trading framework for IDX (Indonesia Stock Exchange). Features an institutional-grade CNN-LLM Dual Core pipeline for strategic signal generation.

## 🧠 Dual-Core Intelligence (v19.0 - Institutional)

The engine leverages a specialized two-stage intelligence flow:

1.  **CNN Visual Brain**: Lightweight Conv1D TFLite model for 30-day OHLCV pattern recognition. Acts as the primary technical gatekeeper.
2.  **LLM Strategic Brain**: 4-bit quantized **Qwen2.5-Coder-7B-Instruct** acting as the high-hierarchy Supreme Auditor. Performs qualitative reasoning with **Enriched Technical Prompting** (RSI, MACD, ATR, BB).

## 🚀 Institutional Features

- **High-Hierarchy Audit**: No trade is executed without strategic confirmation from the LLM Brain.
- **Unified 3-Notebook Hub**: Optimized for Kaggle's 5-notebook scheduling limit.
- **ATR-Based Risk Management**: Automated position sizing and Triple Barrier exits (TP 3% / SL 2%).
- **Firebase Global State**: Cross-notebook signaling and real-time execution monitoring.

## 🛰️ Project Structure (v18.26)

1.  **`01_inference_engine.ipynb`**: Universe Scan (SMA 50) + CNN Visual Inference.
2.  **`02_strategic_brain.ipynb`**: High-hierarchy LLM Strategic Audit.
3.  **`03_execution_monitor.ipynb`**: Trade execution, risk management, and Telegram reporting.
4.  **`04_performance_lab.ipynb`**: Historical backtesting and performance auditing.

**Model Retraining**:
*   `00b_model_retraining_cnn.ipynb`: Weekly CNN visual logic training.

---
*Institutional Grade | CNN-LLM Dual Core | v19.0*

## 🗺️ Roadmap (Upcoming Features)
Analysis performed on 2026-04-16 identified several key development paths:
- **Fundamental RAG**: Integration of financial news and fundamental metrics into the LLM audit.
- **Sector Concentration Guard**: Automated portfolio diversification across industrial sectors.

# Changelog

## [v19.0.0] - 2026-04-16
### Added
- **Enriched Prompting**: Integrated RSI, MACD, ATR, and Bollinger Bands into the Strategic Brain prompt for higher precision reasoning.
- **Parallel Inference**: Implemented `ThreadPoolExecutor` for parallel data fetching in the signal audit stage.
- **Dynamic Fees Model**: Added IDX-specific sell tax (0.1%) and broker commission (0.2%) to backtest simulations.
- **Advanced Metrics**: Integrated Sharpe Ratio, Sortino Ratio, and Max Drawdown (MDD) calculations into the Performance Lab.
- **Strategy Visualizer**: Automated generation of 30-day OHLCV charts with target overlays, sent directly to Telegram.

## [v18.26.0] - 2026-04-16
