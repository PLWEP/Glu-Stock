# Changelog

## [v20.0.0] - 2026-04-16
### Added
- **Ticker Checkpointing**: Persistent audit state in Firebase to handle kernel restarts and crashes.
- **Global Market Guard**: Automated sentiment analysis of S&P 500 and Nikkei indices at 08:30 WIB.
- **Model Quality Gate**: Validation accuracy threshold (60%) for weekly CNN retraining.
- **Strict Target Enforcement**: Mandatory Buy/TP/SL extraction from LLM reasoning with VETO fallback.

## [v19.0.0] - 2026-04-16
### Added
- **Enriched Prompting**: Integrated RSI, MACD, ATR, and Bollinger Bands into the Strategic Brain prompt for higher precision reasoning.
- **Parallel Inference**: Implemented `ThreadPoolExecutor` for parallel data fetching in the signal audit stage.
- **Dynamic Fees Model**: Added IDX-specific sell tax (0.1%) and broker commission (0.2%) to backtest simulations.
- **Advanced Metrics**: Integrated Sharpe Ratio, Sortino Ratio, and Max Drawdown (MDD) calculations into the Performance Lab.
- **Strategy Visualizer**: Automated generation of 30-day OHLCV charts with target overlays, sent directly to Telegram.

## [v18.26.0] - 2026-04-16
### Added
- **CNN-LLM Dual Core**: Transitioned to a specialized architecture using CNN for visual pattern recognition and Gemma-7B (LLM) for strategic auditing.
- **Expectancy Metrics**: Added Profit Factor and Expectancy calculations to the Performance Lab.
- **Project Audit**: Completed a comprehensive project analysis and generated a future development roadmap.

### Changed
- **Pipeline Consolidation**: Merged Research and Inference into a single stage. Reduced production footprint to 3 core notebooks.
- **Threshold Optimization**: Set CNN trigger to 0.45 to increase candidate flow for LLM analysis.

### Removed
- **LGBM Decommissioning**: Purged LightGBM model (`glu_brain_v1.joblib`) and legacy training notebook (`00a`) to eliminate statistical recall bottlenecks.
- **Debris Purge**: Removed unused CNN variants (weekly, monthly) and .h5 weights.
### Removed
- **Root Cleanup**: Purged all remaining legacy scripts and config files (`config.yaml`, `scheduler.py`, `telegram_bot.py`, `tickers.json`, etc.).
- **Environment Debris**: Deleted `.env`, `package.json`, and older `venv` setup scripts.

## [v18.15.0] - 2026-04-07
### Changed
- **Global Decommissioning**: Completed the mass purge of all legacy module directories (`agents`, `risk`, `utils`, `strategies`, `reporting`, `portfolio`, `orchestrator`, `tests`).
- **Cleanroom Status**: Repository has reached a pristine state, containing only the high-performance v18.x notebooks and essential model assets.

## [v18.1.0] - 2026-04-06
### Added
- **Recursive Model Discovery**: Implemented nested directory walking in `02_signal_inference.ipynb` to automatically locate `.joblib` and `.tflite` artifacts in any Kaggle input path.
- **Wait & Retry (Polling)**: Added `wait_for_queue` logic to FirebaseHandler in notebooks `02`, `03`, and `04`. Notebooks now wait up to 20 minutes for predecessor data, resolving Kaggle scheduling race conditions.
- **Market Regime Guard**: Integrated IHSG (^JKSE) trend detection. System now automatically tightens Meta-Gate to **70% confidence** during **BEAR** market regimes.
- **ATR-Based Risk Management**: 
    - Implemented Position Sizing based on 1% Equity Risk and 2.0x ATR volatility in `03_execution_engine.ipynb`.
    - Added **The Closer**: Automated monitoring of `OPEN` trades for Stop-Loss (2x ATR) and Take-Profit (3x ATR) hits.
- **Portfolio Constraint**: Implemented a hard limit of **10 concurrent positions** to maintain portfolio health and liquidity.

### Changed
- **Emoji-Free Interface**: Performed an aggressive emoji purge across all notebooks to ensure 100% character encoding compatibility in automated Kaggle environments.
- **Enhanced Progress Tracking**: Standardized `flush=True` in all print logs to ensure real-time visibility of autonomous progress in the Kaggle UI.

## [v18.0.0] - 2026-04-06
### Changed
- **Model Upgrade**: Replaced Random Forest with **LightGBM** single model (10x faster training, identical accuracy).
- **Stacking Removed**: Removed XGBoost + CatBoost stacking ensemble (overkill for <1% accuracy gain).
- **CNN Simplified**: Removed LSTM layer, Optuna HPO, and Meta-Labeling dependency from CNN pipeline. Now uses lightweight Conv1D + GlobalAvgPool with native TFLite export.
- **Triple Barrier**: Upgraded from binary (up/down) to 2-class Triple Barrier labeling (BUY vs DONT_BUY, TP=3%, SL=2%, horizon=10 days).
- **Independent Notebooks**: `00a` and `00b` now run fully independently (no Meta-Labeling data dependency).

### Added
- **12-Feature Engineering**: RSI, MACD, BB_High, BB_Low, ATR, ADX, OBV_norm, day_of_week, week_of_month, frac_diff_close, vol_ratio, Returns.
- **Fractional Differentiation**: López de Prado fixed-window (100 days) for stationarity with memory.
- **SMOTE Oversampling**: Balanced BUY/DONT_BUY classes on training set only.
- **Feature Selection**: Mutual Information ranking, top 10 features auto-selected.
- **Optuna HPO**: 50 trials for LightGBM (num_leaves, max_depth, learning_rate, min_child_samples).
- **Walk-Forward CV**: 4-split expanding window temporal validation.
- **Pipeline Diagnostics**: Per-stage counters (OK/Empty/Short/Dropna/Error) for data aggregation.
- **Meta-Label Gate** in `02_signal_inference.ipynb`: Execute only when LightGBM=BUY AND CNN confidence ≥60%.

### Fixed
- **frac_diff overflow**: Changed from threshold-based (1e-5) to fixed window=100. Previous impl produced ~1200 weights for ~1250 data points, causing 95%+ NaN.
- **yfinance MultiIndex**: Added `.squeeze()` + `ndim > 1` fallback for all OHLCV columns.
- **yfinance FutureWarning**: Suppressed with `warnings.filterwarnings('ignore')` + explicit `auto_adjust=True`.
- **LGBMClassifier feature names**: Passed `pd.DataFrame(columns=...)` instead of raw numpy to eliminate sklearn warning.

### Removed
- **35 patch scripts**: Cleaned up all one-shot `patch_*.py`, `fix_*.py`, `dump_*.py`, `test_*.py`, and `debug_*.py` files from project root.

## [v17.0.0] - 2026-04-04
### Changed
- **Cloud Migration**: Migrated entire system from Termux/PC to Kaggle-native architecture.
- **Monolithic Notebooks**: Consolidated system into 6 self-contained `.ipynb` files with embedded infrastructure.
- **Firebase Integration**: Replaced SQLite with Firebase Firestore for cloud state management.
- **Market Universe**: Expanded from LQ45 (45 tickers) to full Papan Utama (259 tickers) with 3-tier fallback.

## [v14.1.0] - 2026-03-31
### Fixed
- **History Module Sync**: Resolved `ImportError: HistoryManager` in `orchestrator.py`.
- **Config Hardening**: Updated `ConfigLoader` for current `config.yaml` schema.
- **Training Stability**: Fixed `UnicodeEncodeError` and `KeyError` in unified training.
- **Backtest Lab**: Implemented `--backtest` CLI logic in `scheduler.py`.

## [v14.0.0] - 2026-03-30
### Removed
- **WhatsApp Integration**: Deleted `wa_bot.js` and Baileys bridge.
- **SaaS Guard**: Suspended Telegram Channel broadcasting.

## [v11.0.0] - 2026-03-29
### Added
- Deep Intelligence (CNN) integration with TFLite.
- Institutional Core (Trend & Risk Parity).
- Telegram Signal SaaS & Admin Automation.

## [v2.0.0] - 2026-03-29
### Added
- Production hardening: log rotation, recursion guard, resilient polling.
- VWAP accuracy fix, bulk SQL inserts, shell injection prevention.

## [v0.1.0] - 2026-03-27
### Added
- Initial project structure and multi-agent core.
