# Changelog

## [v14.0.0] - 2026-03-30
### Removed
- **WhatsApp Integration**: Deleted `wa_bot.js` and removed all Baileys bridge logic from `alerts.py` and `orchestrator.py`.
- **PM2 Consolidation**: Removed `glu-stock-wa` from `ecosystem.config.js`.

### Changed
- **SaaS Guard Disabled**: Temporary suspension of Telegram Channel broadcasting and subscriber auto-kick logic.
- **Platform Focus**: System consolidated to focus exclusively on Telegram for personal professional use.

## [v11.0.0] - 2026-03-29
...

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
