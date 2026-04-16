# Glu-Stock 💹

Kaggle-native quantitative trading framework for IDX (Indonesia Stock Exchange). Features an institutional-grade CNN-LLM Dual Core pipeline for strategic signal generation.

## 🧠 Dual-Core Intelligence (v20.0 - Institutional)

The engine leverages a specialized two-stage intelligence flow:

1.  **CNN Visual Brain**: Lightweight Conv1D TFLite model for 30-day OHLCV pattern recognition. Acts as the primary technical gatekeeper.
2.  **LLM Strategic Brain**: 4-bit quantized **Qwen2.5-Coder-7B-Instruct** acting as the high-hierarchy Supreme Auditor. Performs qualitative reasoning with **Enriched Technical Prompting** (RSI, MACD, ATR, BB).

## 🚀 Institutional Features

- **High-Hierarchy Audit**: No trade is executed without strategic confirmation from the LLM Brain.
- **Unified 3-Notebook Hub**: Optimized for Kaggle's 5-notebook scheduling limit.
- **ATR-Based Risk Management**: Automated position sizing and Triple Barrier exits (TP 3% / SL 2%).
- **Firebase Global State**: Cross-notebook signaling and real-time execution monitoring.

## 🕒 Operational Flow (Kaggle Schedule)
The system is designed for high-autonomy execution on Kaggle:
- **Daily Start (12:00 AM)**: `01`, `02`, and `03` are scheduled to start simultaneously.
- **Sequential Guard**: Logic within notebooks enforces the `01 (Scan) -> 02 (Audit) -> 03 (Report)` sequence via polling.
- **Reporting (08:30 AM WIB)**: `03_execution_monitor` waits until the Jakarta morning session to deliver visual trade plans to Telegram.
- **Weekly Retrain**: `00b_model_retraining_cnn` outputs fresh visual models for the `01` engine.

## 🛰️ Project Structure (v18.26)

1.  **`01_inference_engine.ipynb`**: Universe Scan (SMA 50) + CNN Visual Inference.
2.  **`02_strategic_brain.ipynb`**: High-hierarchy LLM Strategic Audit.
3.  **`03_execution_monitor.ipynb`**: Trade execution, risk management, and Telegram reporting.
4.  **`04_performance_lab.ipynb`**: Historical backtesting and performance auditing.

**Model Retraining**:
*   `00b_model_retraining_cnn.ipynb`: Weekly CNN visual logic training.

---
*Institutional Grade | CNN-LLM Dual Core | v20.0*

## 🗺️ Roadmap (Upcoming Features)
Analysis performed on 2026-04-16 identified several key development paths:
- **Fundamental RAG**: Integration of financial news and fundamental metrics into the LLM audit.
- **Sector Concentration Guard**: Automated portfolio diversification across industrial sectors.
- **Dynamic Fee Engine**: High-fidelity PnL simulation including IDX-specific taxes and fees.
- **Strategy Visualizer**: Dashboard for real-time monitoring of LLM analytical logic.

---
*Institutional Grade | CNN-LLM Dual Core | v20.0*

# Changelog

## [v20.0.0] - 2026-04-16
### Added
- **Ticker Checkpoint**: Firebase-based state management to resume audits after kernel restarts.
- **Global Market Guard**: Automated systemic risk monitoring (S&P 500/Nikkei 225) in `03_execution_monitor`.
- **Accuracy Gating**: Validation threshold (>60%) for CNN model deployment in `00b`.
- **Strict Target Parsing**: Automated VETO logic for incomplete LLM signal outputs.

## [v19.0.0] - 2026-04-16
### Added
- **Enriched Prompting**: Integrated RSI, MACD, ATR, and Bollinger Bands into the Strategic Brain prompt for higher precision reasoning.
- **Parallel Inference**: Implemented `ThreadPoolExecutor` for parallel data fetching in the signal audit stage.
- **Dynamic Fees Model**: Added IDX-specific sell tax (0.1%) and broker commission (0.2%) to backtest simulations.
- **Advanced Metrics**: Integrated Sharpe Ratio, Sortino Ratio, and Max Drawdown (MDD) calculations into the Performance Lab.
- **Strategy Visualizer**: Automated generation of 30-day OHLCV charts with target overlays, sent directly to Telegram.

## [v18.26.0] - 2026-04-16

# Task: Implementing v20.0 Robustness & Market Guards

- [x] Create Implementation Plan
- [x] Update Strategic Brain (02) - Checkpoints & Strict Targets
- [x] Update Execution Monitor (03) - Global Market Guard
- [x] Update CNN Retraining (00b) - Accuracy Gating
- [x] Final verification and walkthrough

# Walkthrough: Glu-Stock v20.0 Institutional Upgrade

Berhasil mengimplementasikan v20.0 dengan fokus pada stabilitas operasional dan integrasi sentimen global.

## Perubahan v20.0 (Robustness & Sync)

### 1. Ticker Checkpoint (02_strategic_brain)
- Implementasi sistem checkpoint berbasis Firebase. 
- Jika proses terhenti/crash, sistem akan secara otomatis melewati ticker yang sudah diaudit hari itu.

### 2. Global Market Guard (03_execution_monitor)
- Integrasi data **S&P 500 (^GSPC)** dan **Nikkei 225 (^N225)** via `yfinance` (Free API).
- Memberikan peringatan **[SYSTEMIC RISK WARNING]** pada jam 08:30 WIB jika pasar global drop > 1.5%.

### 3. Accuracy Gating (00b_model_retrain)
- Penambahan filter kualitas: Model baru hanya akan diekspor jika akurasi validasi > 60%. 
- Jika di bawah threshold, sistem mendeteksi kegagalan training dan tetap menggunakan model lama di produksi.

### 4. Strict Target Parsing
- Buy, TP, dan SL kini diparsing secara ketat dari output LLM. Jika data tidak lengkap, sinyal akan di-VETO secara otomatis untuk menghindari "tebakan" harga.

---
*Status: Ready for Production | v20.0 Institutional Grade*
- 2026-04-16
