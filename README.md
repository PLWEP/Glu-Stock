# Glu-Stock 💹

Kaggle-native quantitative trading framework for IDX (Indonesia Stock Exchange). Features autonomous ML retraining, cloud-native signal inference, and Firebase-based state management — all running on free Kaggle compute.

## 🧠 ML Intelligence (v18.0)

Dual-model ensemble for institutional-grade signal generation:

- **LightGBM Brain**: Gradient boosting with 12-feature engineering (RSI, MACD, ATR, ADX, OBV, Fractional Differentiation, Time-Based). Trained with Optuna HPO, SMOTE oversampling, and Walk-Forward validation.
- **CNN Brain**: Lightweight 1D-Convolutional Neural Network for 30-day OHLCV pattern recognition. Native TFLite export for fast inference.
- **Meta-Label Gate**: Signals execute ONLY when LightGBM says "BUY" AND CNN confidence exceeds 60% threshold.

### Key ML Strategies
- **Triple Barrier Labeling**: Risk-aware 2-class target (BUY vs DONT_BUY) with TP=3%, SL=2%, Horizon=10 days
- **Feature Selection**: Mutual Information ranking, top 10 features selected
- **SMOTE**: Synthetic oversampling for class balance
- **Walk-Forward CV**: Expanding window temporal validation (no shuffle)

## 📁 Repository Structure

```
notebooks/
├── 00a_model_retraining_rf.ipynb   # LightGBM retraining (weekly scheduled)
├── 00b_model_retraining_cnn.ipynb  # CNN retraining (weekly scheduled)
├── 01_research_scan.ipynb          # Universe scanning & candidate selection
├── 02_signal_inference.ipynb       # Dual-model inference + Meta-Label gate
├── 03_execution_engine.ipynb       # Trade execution & position management
└── 04_monitor_alert.ipynb          # Portfolio monitoring & Telegram alerts
```

## 🏗️ Architecture

- **Compute**: Kaggle Kernels (scheduled runs, 12h rotation)
- **State Bridge**: Firebase Firestore (task queues, trade history, telemetry)
- **Model Storage**: Kaggle Datasets (`glustock-brains`)
- **Market Universe**: 259 Papan Utama tickers (3-tier fallback: IDX API → GitHub → Hardcoded)
- **Secrets**: Kaggle Secrets / `.env` for local development

## 🛠️ Tech Stack
- **Python 3.12+**: LightGBM, TensorFlow, Scikit-Learn, yfinance, ta
- **Firebase**: Firestore for cloud state synchronization
- **TFLite**: Lightweight CNN inference binary

---
*Institutional Grade | ML Powered | Cloud Native | v18.0*
