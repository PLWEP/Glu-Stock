# Glu-Stock 💹

Quantitative Finance Framework for Stock Analysis, optimized for IDX (Indonesia Stock Exchange). Features a multi-agent engine with Intelligence Layer (Fundamentals + ML), and dual-platform bot integration (Telegram & WhatsApp).

## 🧠 Intelligence Layer (Phase 3)

Glu-Stock now features an advanced intelligence layer to filter "junk" stocks and predict confidence:
- **Fundamental Analyst**: Automatically scores stocks based on **P/E, ROE, DER, and Dividend Yield**.
- **ML Price Predictor**: Uses a **Random Forest** classification model to predict price increase probability. 
- **Decoupled Architecture**: Training is performed on a PC/Laptop (heavy lifting) while Termux handles lean, fast inference.

## 🛡️ Risk & Resilience (Phase 4-5)

Glu-Stock is built for 24/7 stability on mobile/Termux:
- **ATR Trailing Stop**: Dynamic stop-loss that follows price action to lock in profits.
- **Hardware-Aware Throttling**: Automatically pauses scans if phone temperature >45°C or battery <15%.
- **Panic Exit**: Instant liquidation of all positions via `/panic` command.
- **Quant Metrics**: real-time calculation of **Sharpe, Sortino, and Calmar Ratios**.

## 🏦 Strategic Master (Phase 6-8)

Professional-grade capital management and validation:
- **Multi-Tier Sizing**: Choose between **Fixed Fractional, Volatility Targeting (ATR), or Kelly Criterion**.
- **Strategy Rebalancer**: Automatically shifts capital between Daily, Weekly, and Monthly pipelines based on relative performance.
- **OOS Backtester**: Validates strategies on unseen historical data with 0.3% slippage.
- **Monte Carlo Simulator**: Calculates **Risk of Ruin** and worst-case drawdowns across 1000 randomized scenarios.
- **Expectancy Gate**: Prevents trading if the strategy's statistical edge (Expectancy) falls below zero.

## 📱 Termux Quick Start (Recommended)

1. **Install Termux API App**:
   - Install **Termux:API** from [F-Droid](https://f-droid.org/en/packages/com.termux.api/).
   - Grant necessary hardware permissions in Android Settings.

2. **Run Automated Setup**:
   - **Termux**: `./termux_setup.sh`
   - **Laptop/PC (Windows)**: Run `setup_pc.bat`

3. **WhatsApp Authentication**:
   ```bash
   pm2 start wa_bot.js
   pm2 logs glu-stock-wa
   # Scan the QR code with your phone. 
   ```

4. **Activate All**:
   ```bash
   pm2 start ecosystem.config.js
   pm2 save
   ```

## 💻 Decoupled ML Training (PC Trainer)

Training on Termux is restricted. Perform training on your PC/Laptop and export the brain:

1. **Train Model (on PC)**:
   ```bash
   python utils/ml_trainer_pc.py
   ```
2. **Transfer Brain**:
   Copy `data/models/glu_brain_v1.joblib` from PC to `~/Glu-Stock/data/models/` on Termux.

## 🤖 Bot Commands

- `/start`: Open Main Menu.
- `/status`: System health (RAM/Bat/Temp) + **Portfolio Recap**.
- `/signals`: Latest recommendations with **Intel Badges (`🧠`, `🤖`)**.
- `/panic`: Liquidate all positions immediately.
- `/history`: View last 5-10 closed trades.
- `/logs`: View rotating system logs.

## 🛠️ Tech Stack
- **Python 3.13**: Quant engine, Scikit-Learn, joblib, yfinance.
- **Node.js 22+**: Baileys (WhatsApp) bridge.
- **SQLite**: High-performance bulk-caching and long-term trade audit trail.

---
*Institutional Grade | ML Powered | Strategically Optimized*
