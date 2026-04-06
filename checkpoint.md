# GLU-STOCK: PROJECT CHECKPOINT (v18.1)

## System Overview
Institutional-grade quantitative trading engine for IDX. Replaced complex ensembles with a high-performance **LightGBM** (63% OOS) + **CNN TFLite** (62% OOS) meta-label gate. High-precision risk management with **ATR-based sizing** and **Market Regime Guards**.

## 📁 Active Notebook Pipeline

| Notebook | Function | Schedule | Engine Features |
|----------|----------|----------|-----------------|
| `00a_retrain_rf` | LightGBM training (SMOTE + Optuna) | Weekly | 12 features, FracDiff |
| `00b_retrain_cnn` | CNN TFLite training (OHLCV Visual) | Weekly | 5-channel, 30d window |
| `01_research` | Universe scanning & Liquidity filter | Daily | MA200 Trend Guard |
| `02_inference` | Dual-brain Gate + Recursive Search | Daily | **BEAR/BULL Regime Guard** |
| `03_execution` | ATR Sizing & Automated SL/TP | Daily | **Wait & Retry (Polling)** |
| `04_monitor` | Portfolio telemetry & Telegram | Daily | No-Emoji Clean UI |

## 🏗️ v18.1 Hardening Features
1. **Recursive Model Search**: Automatically finds `.joblib` and `.tflite` in deeply nested Kaggle paths.
2. **Self-Sequencing (Wait Logic)**: Downstream notebooks (02, 03, 04) wait up to 20 min for upstream data to hit Firebase.
3. **Institutional Risk Manager**: 
   - **Position Sizing**: Calculated based on 1% Equity Risk / 2x ATR distance.
   - **The Closer**: Automated monitoring of Stop-Loss and Take-Profit.
   - **Regime-Aware Filter**: Gate tightens to 70% confidence during BEAR markets.

## 🏗️ Infrastructure
- **Compute**: Kaggle Kernels (Python 3.12+, fully self-contained)
- **State**: Firebase Firestore (Queue + Trades + History)
- **Secrets**: Kaggle Secrets (`FIREBASE_KEY_JSON`, `TELEGRAM_TOKEN`)

## ⚠️ Critical Rules
1. **Zero Placeholder**: No hardcoded equity/shares; use ATR and Firebase state.
2. **Feature Persistence**: Never delete features from training notebooks.
3. **No emojis in logs**: Use plain text markers `[OK]`, `[SIGNAL]`, `[WAIT]`.

---
*Last Updated*: 2026-04-06
*Status*: **ACTIVE PRODUCTION (v18.1)** | Kaggle Cloud Autonomous
