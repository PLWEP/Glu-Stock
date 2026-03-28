# Changelog

## [v1.2.0] - 2026-03-28

### Added

- `UniverseManager.partition_price_data`: Centralized MultiIndex slicing logic (DRY).
- Dynamic lookback logic in `Scheduler` and `Orchestrator` (replacing hardcoded dates).
- Standardized `JsonLogger` telemetry across Scanner and Orchestrator.

### Changed

- `TradingStrategy` transitioned to 4-factor continuous scoring model (RSI, MACD, Trend, Volume).
- `Orchestrator` error handling improved with specific exception blocks and reporting enforcement.

### Removed

- Dead ML code stub `_generate_ml_signals` from `TradingStrategy`.
- Hardcoded date references in `scanner.py` and `scheduler.py`.
- Removed legacy `record_trade` and `record_portfolio_snapshot` functions from `TradingDatabase`.
- Consolidated and modernized the database test suite.

## [0.1.0] - 2026-03-27

### Added

- Initial project structure.
- `data.py` module with `yfinance` integration and SQLite caching.
- Core documentation: `README.md`, `changelog.md`, `checkpoint.md`.
