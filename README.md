# Glu-Stock 💹

Quantitative Finance Framework for Stock Analysis, optimized for IDX (Indonesia Stock Exchange). Features a multi-agent engine with Intelligence Layer (Fundamentals + ML), and dual-platform bot integration (Telegram & WhatsApp).

## 🧠 Deep Intelligence (v11.0)

Glu-Stock now uses a **Dual-Brain Ensemble** for decision making:
- **RF Brain (v1)**: Scikit-learn Random Forest for tabular/technical analysis.
- **CNN Brain (v2)**: 10-layer Convolutional Neural Network for temporal/visual price patterns.
- **Decision Engine**: High-confidence trades (`🧠`) now require agreement from both intelligence layers.

## 💻 PC Command Center (Recommended)

Managing the bot is now easier with the unified Windows Batch menu:

1. **Run Setup**:
   ```cmd
   setup_pc.bat
   # Choose [1] to initialize the environment and dependencies.
   ```
2. **Train AI (The Brains)**:
   ```cmd
   setup_pc.bat
   # Choose [2] to run unified training (RF + CNN) for all time horizons.
   ```
3. **Run Backtests**:
   ```cmd
   setup_pc.bat
   # Choose [3] to validate your strategy in the Laboratory.
   ```

## 📱 Termux Quick Start

1. **Install Termux API App**:
   - Install **Termux:API** from [F-Droid](https://f-droid.org/en/packages/com.termux.api/).
   - Grant necessary hardware permissions in Android Settings.

2. **Run Automated Setup**:
   - **Termux**: `./termux_setup.sh`

3. **Transfer Brains**:
   Copy everything from `data/models/*.joblib` and `data/models/*.tflite` (from PC) to `~/Glu-Stock/data/models/` on Termux.

4. **Activate All**:
   ```bash
   pm2 start ecosystem.config.js
   pm2 save
   ```

## 🤖 Bot Commands

- `/start`: Open Main Menu.
- `/status`: System health + Portfolio + **Market Regime (`📈`/`📉`)**.
- `/signals`: Recommendations with **Ensemble Confidence (`Ens`)**.
- `/registry`: View top 5 backtest experiments from the Lab.
- `/panic`: Liquidate all clusters immediately.

## 🛠️ Tech Stack
- **Python 3.13**: Quant engine, Scikit-Learn, joblib, yfinance.
- **Node.js 22+**: Baileys (WhatsApp) bridge.
- **SQLite**: High-performance bulk-caching and long-term trade audit trail.

---
*Institutional Grade | ML Powered | Strategically Optimized*
