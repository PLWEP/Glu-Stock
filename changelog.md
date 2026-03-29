# Changelog

## [v11.0.0] - 2026-03-29
### Added
- **Deep Intelligence (Phase 11)**:
    - **1D-CNN Brain**: Implemented 10-layer Convolutional Neural Network for temporal pattern recognition.
    - **Dual-Brain Ensemble**: Integrated CNN + Random Forest voting logic in `StrategyAgent`.
    - **TFLite Inference**: Optimized `.tflite` interpreter for high-speed CNN execution on Termux.
- **DevOps & Training**:
    - `train_intel.py`: Unified script for training both RF and CNN intelligence layers.
    - `setup_pc.bat`: Comprehensive PC Command Center for environment setup, training, and testing.

### Changed
- Refactored `Orchestrator` signal reports to display dual-brain (ML/CNN) confidence scores.
- Updated `requirements.txt` to include `tensorflow` and `scipy` for deep learning support.

## [v8.0.0] - 2026-03-29
...

## [v3.1.0] - 2026-03-29
...

## [v2.0.0] - 2026-03-29
### Added
- **Production Hardening**:
    - `RotatingFileHandler`: Implemented log rotation (5MB, 3 backups) in `JsonLogger` to prevent storage exhaustion.
    - **Recursion Guard**: decoupled alerts from error logging to prevent infinite loops during network failure.
    - **Resilient Polling**: Added retry backoff mechanism to `TelegramBot` polling loop.

### Fixed
- **VWAP Accuracy**: Fixed the `DailyStrategy` to correctly reset VWAP calculations at each market open.
- **Data Performance**: Optimized `StockDataHandler` with bulk SQL `executemany` inserts (80% faster caching).
- **Security**: Switched WhatsApp command execution from `exec` to `spawn` with argument arrays to prevent shell injection.

## [v1.5.0] - 2026-03-28
### Added
- Multi-interval data support (1d, 15m, 1h) in `StockDataHandler` and `ResearchAgent`.
- Intraday ISO timestamp caching for high-frequency signal generation.

### Changed
- `UniverseManager` now enforces Rp25B/500k lot liquidity floor and prioritizes LQ45/Kompas100.

## [v0.1.0] - 2026-03-27
### Added
- Initial project structure and multi-agent core.
- SQLite data caching and Telegram integration.
