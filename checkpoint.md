# GLU-STOCK: PROJECT CHECKPOINT (v18.0)

## System Overview
Glu-Stock is a **Kaggle-native** quantitative trading framework for IDX. All compute runs on free Kaggle kernels with Firebase Firestore as the cloud state bridge. The ML pipeline uses **LightGBM** (tabular) + **CNN** (temporal patterns) with a Meta-Label gate for signal execution.

## 📁 Active Notebook Pipeline

| Notebook | Function | Schedule | Runtime |
|----------|----------|----------|---------|
| `00a_model_retraining_rf.ipynb` | LightGBM training (259 tickers, 12 features, SMOTE, Optuna) | Weekly | ~8 min |
| `00b_model_retraining_cnn.ipynb` | CNN training (OHLCV patterns, 30-day sequences) | Weekly | ~15 min |
| `01_research_scan.ipynb` | Universe scanning & candidate filtering | Daily | ~5 min |
| `02_signal_inference.ipynb` | Dual-model inference + Meta-Label gate (60% threshold) | Daily | ~3 min |
| `03_execution_engine.ipynb` | Trade execution & position management | Daily | ~2 min |
| `04_monitor_alert.ipynb` | Portfolio monitoring & Telegram alerts | Daily | ~1 min |

## 🧠 ML Pipeline Details

### LightGBM (00a)
- **Features (12)**: Returns, RSI, MACD, BB_High, BB_Low, ATR, ADX, OBV_norm, day_of_week, week_of_month, frac_diff_close, vol_ratio
- **Feature Selection**: Mutual Information → top 10
- **Target**: 2-class Triple Barrier (BUY/DONT_BUY, TP=3%, SL=2%, horizon=10 days)
- **Class Balance**: SMOTE oversampling (training set only)
- **HPO**: Optuna 50 trials (max_depth, num_leaves, lr, min_child_samples)
- **Validation**: Walk-Forward expanding window (4 splits)
- **Output**: `glu_brain_v1.joblib` + `rf_oos_meta.json`

### CNN (00b)
- **Input**: 5-channel OHLCV, 30-day rolling window, MinMax normalized
- **Architecture**: Conv1D(64) → BN → MaxPool → Conv1D(128) → GlobalAvgPool → Dense(64) → Dropout(0.3) → Softmax(2)
- **Training**: 20 epochs, batch_size=256, EarlyStopping(patience=3)
- **Output**: `cnn_daily_t2.tflite` (native TFLite, no SELECT_TF_OPS)

### Inference Gate (02)
- Signal fires ONLY when: `LightGBM == BUY` AND `CNN confidence >= 60%`
- Blocked signals logged with reason to Firebase

## 🏗️ Infrastructure
- **Compute**: Kaggle Kernels (Python 3.12+, GPU optional)
- **State**: Firebase Firestore (task queues, trade history, telemetry)
- **Models**: Kaggle Datasets (`glustock-brains`)
- **Universe**: 259 Papan Utama (3-tier fallback: IDX API → GitHub → Hardcoded)
- **Secrets**: Kaggle Secrets (`FIREBASE_KEY_JSON`, `TELEGRAM_TOKEN`)

## ⚠️ Critical Rules
1. **Feature Persistence**: Never delete existing notebook features without explicit request.
2. **Temporal Integrity**: All validation must use `shuffle=False` (time-series).
3. **SMOTE on train only**: Never apply oversampling to test/validation set.
4. **frac_diff window**: Must use fixed window=100 (NOT threshold-based).
5. **Notebooks are independent**: `00a` and `00b` can run in parallel.

---
*Last Updated*: 2026-04-06
*Status*: Active Production | Kaggle Cloud Native | v18.0
