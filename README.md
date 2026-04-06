# Glu-Stock 💹

Kaggle-native quantitative trading framework for IDX (Indonesia Stock Exchange). Features an institutional-grade ML pipeline, recursive model discovery, and an autonomous self-sequencing execution engine.

## 🧠 ML Intelligence (v18.1)

Dual-model ensemble for high-precision signal generation:

- **LightGBM Brain**: Tabular Alpha (**63% OOS**) with 12-feature engineering (Fractional Differentiation, Time-Based). 
- **CNN Brain**: Lightweight Conv1D (**62% OOS**) for 30-day OHLCV pattern recognition.
- **Meta-Label Gate**: Signals execute ONLY when LightGBM says "BUY" AND CNN confidence hits threshold.
- **Market Regime Guard**: Automatically tightens Meta-Gate to **70%** during **BEAR** markets (IHSG < SMA200).

## 🚀 Institutional Features (v18.1 Hardening)

- **Recursive Discovery**: Automagically finds model files (`.joblib`, `.tflite`) in deeply nested Kaggle input paths.
- **Self-Sequencing (Wait & Retry)**: Downstream notebooks wait up to 20 mins for predecessors to complete, resolving Kaggle's simultaneous scheduling race conditions.
- **Risk Manager (v18.1)**: 
    - **ATR-Based Sizing**: Positions sized based on 1% Equity Risk and actual market volatility.
    - **The Closer**: Automated monitoring and closure of trades hitting Stop-Loss or Take-Profit.
- **No-Emoji UI**: Standardized plain-text markers for 100% character encoding compatibility in automated logs.

## 📁 Repository Structure

```
notebooks/
├── 00a_model_retraining_rf.ipynb   # LightGBM Alpha training (Weekly)
├── 00b_model_retraining_cnn.ipynb  # CNN Pattern training (Weekly)
├── 01_research_scan.ipynb          # Universe scanning & Liquidity filter
├── 02_signal_inference.ipynb       # Dual-brain Gate + Market Regime
├── 03_execution_engine.ipynb       # ATR Sizing & SL/TP Management
└── 04_monitor_alert.ipynb          # Status alerts & Clean UI
```

---
*Institutional Grade | ML Powered | Cloud Native | v18.1*
