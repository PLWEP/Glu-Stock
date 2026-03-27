# Glu-Stock Project Grounding

## Project Overview

Glu-Stock is a Python-based quantitative finance framework for stock analysis and backtesting.

## Module Logic: Data Module

The Data Module is responsible for fetching and caching OHLCV data.

- **Provider:** Yahoo Finance via `yfinance`.
- **Caching:** Local SQLite database (`data/cache.db`).
- **Data Integrity:** Fully verified with tests (NaN checks, multi-ticker support).
- **Status:** Production-ready.

## Core Execution Rules

1. Python: `c:/Users/MP2NE93D/miniconda3/python.exe`.
2. Environment Isolation: Mandatory clean environments for tests.
3. Documentation: Keep `README.md`, `changelog.md`, and `checkpoint.md` in sync.
4. Linting: Strict `ruff` enforcement.
