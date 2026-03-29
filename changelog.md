# Changelog

## [v8.0.0] - 2026-03-29
### Added
- **Strategic Master (Phase 8)**:
    - `StrategyAllocator`: Dynamic inter-strategy capital rebalancing based on Sharpe ratios.
    - **Rolling Matrix**: Implemented rolling 30-day covariance with Ledoit-Wolf shrinkage in `RiskManager`.
    - **Expectancy Safeguard**: Automated safety gate in `Orchestrator` to skip trades with negative expectancy.
- **Quantitative Validation (Phase 7)**:
    - `HistoricalBacktester`: Full-featured engine with OOS support and 0.3% slippage simulation.
    - `MonteCarloSimulator`: 1000-path randomization for Risk of Ruin calculation.
- **Advanced Money Management (Phase 6)**:
    - Multi-tier position sizing: Kelly Criterion and Volatility Targeting (ATR-based).
- **Quant Analytics (Phase 5)**:
    - Real-time calculation of Sharpe, Sortino, and Calmar ratios.
- **Risk & Resilience (Phase 4)**:
    - ATR Trailing stops and Hardware-Aware Throttling (Thermal/Battery guards).

### Changed
- Integrated **Strategic Pulse** metrics into Telegram/WhatsApp reporting.
- Refactored `Orchestrator` to support dynamic capital re-injection between strategy clusters.

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
