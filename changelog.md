# Changelog

## [v3.1.0] - 2026-03-28

### Added
- `termux_setup.sh`: Automated environment setup for Android/Termux environments.
- `requirements.txt`: Consolidated production dependency list.

### Fixed
- Fixed `rank_stocks` unpack error when universe is empty.
- Restored missing `data/database.py` and `utils/performance.py` modules.
- Standardized portfolio status keys across the engine.

### Removed
- Legacy HTML reporting module (`reporting/report.py`) in favor of pure Telegram monitoring.
- `matplotlib` dependency for reduced footprint in mobile environments.

## [v1.5.0] - 2026-03-28

### Added

- Multi-interval data support (1d, 15m, 1h) in `StockDataHandler` and `ResearchAgent`.
- Intraday ISO timestamp caching for high-frequency signal generation.
- Institutional Daily Pipeline: 15m Pivot Points ($R=2C-P_L$, $S=2C-P_H$), Donchian, and VWAP guards.
- Institutional Weekly Pipeline: 3-EMA (3, 10, 21) trend alignment and MA20/50 confirmation.
- Institutional Monthly Pipeline: 12m Momentum (skip 1m), Low-Volatility anomaly, and ROE/Laba tiered filtering.

### Changed

- `UniverseManager` now enforces Rp25B/500k lot liquidity floor and prioritizes LQ45/Kompas100.
- `Orchestrator` dynamically dispatches intervals based on pipeline selection.

## [v1.4.0] - 2026-03-28

### Added

- Dynamic Universe Discovery: `UniverseManager.refresh_universe()` fetches ~800+ tickers from IDX official endpoints.
- Sector metadata and BUMN identification automated during discovery.
- Local cache policy for `idx_stocks.csv` to minimize network latency.

### Removed

- Hardcoded ticker list in `UniverseManager`.

## [v1.3.0] - 2026-03-28

### Added

- 3 distinct trading pipelines: `Daily`, `Weekly`, and `Monthly`.
- `DailyStrategy`: Pivot Points, Donchian Channel, VWAP logic.
- `WeeklyStrategy`: 3 EMA T-Alignment, RSI (50-60), MACD, Pairs Trading Z-score.
- `MonthlyStrategy`: Price-Momentum, Low-Vol Anomaly, Value Rotation (B/P).
- Pipeline-specific filtering in `UniverseManager` (Liquidity, Fundamental ROE/Laba YoY).

### Changed

- `UniverseManager` now enforces a Strict Global Filter (Excludes BUMN & Banks).
- `StrategyAgent` refactored as a strategy dispatcher for multiple timeframes.
- `PipelineOrchestrator` updated with `pipeline` and `paper_trading` parameters.

### Fixed

- Standardized institutional guardrails: Long-Only for Live, Short visibility for Paper.
- Removed legacy `record_trade` and `record_portfolio_snapshot` functions from `TradingDatabase`.
- Consolidated and modernized the database test suite.

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
