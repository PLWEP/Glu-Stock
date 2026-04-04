# GLU-STOCK: PROJECT CHECKPOINT (v16.0)

## System Overview
Glu-Stock is a high-performance quantitative trading framework consolidated for PC/Laptop execution. It uses a cloud-synced intelligence layer (Firebase) to manage trading state, history, and audits.

## 🚀 Key Features (PC Consolidated)
- **Deep Intelligence (v11)**: Dual-Brain Ensemble (RF + CNN) agreement for high-conviction trades.
- **Firebase Cloud Sync**: Real-time state synchronization for trades and logs.
- **Institutional Engine**: hardware-aware throttling (PC optimized), high-performance bulk caching (SQLite).
- **Consolidated Unified Workflow**: One Batch menu (`setup_pc.bat`) for environment setup, training, and backtesting.

## 📁 Repository Structure (Core)
- `agents/`: Research, Strategy, and Trading agents.
- `orchestrator/`: Pipeline lifecycle and risk guards.
- `strategies/`: Multi-timeframe strategies (Daily, Weekly, Monthly).
- `utils/`: Cloud handlers, ML/CNN predictors, and system monitors (PC Optimized).
- `data/`: Local OHLCV cache and model storage.

## 🏗️ Technical State
1. **Environment**: `pc_venv` (Python 3.13.5).
2. **Database**: Firebase Realtime DB (Source of Truth) + SQLite (Local Cache).
3. **Hardware Health**: Throttling enabled via `psutil` (85°C Temp Limit).
4. **Execution Mode**: Paper Trading / Strategy Validation.

---
*Consolidation Date*: 2026-04-04
*Status*: Active Development | PC-Focused
 Riverside
 Riverside
 Riverside
