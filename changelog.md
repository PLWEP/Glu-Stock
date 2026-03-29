# Changelog

## [v3.1.0] - 2026-03-29
### Added
- **Intelligence Layer (Phase 3)**:
    - `FundamentalAgent`: Financial ratio scoring (ROE, P/E, DER, Div Yield).
    - `MLPredictor`: Decoupled Machine Learning inference engine using Random Forest.
    - `ml_trainer_pc.py`: High-power training utility for PC/Laptop environment.
    - `train_intel.py`: Orchestrated training trigger.
- **Reporting**: Intelligence badges (`🧠`, `🤖`) for high-confidence trades in Telegram/WhatsApp.

### Changed
- Refactored `agents.py` to integrate Intelligence analysis into the trading pipeline.
- Centralized all strategy and risk parameters in `config.yaml`.
- Optimized `MLPredictor` for lean inference on Termux using pre-trained `.joblib` models.

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
