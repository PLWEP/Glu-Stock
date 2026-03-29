# Glu-Stock 💹

Quantitative Finance Framework for Stock Analysis, optimized for IDX (Indonesia Stock Exchange). Features a multi-agent engine with Intelligence Layer (Fundamentals + ML), and dual-platform bot integration (Telegram & WhatsApp).

## 🧠 Intelligence Layer (Phase 3)

Glu-Stock now features an advanced intelligence layer to filter "junk" stocks and predict confidence:
- **Fundamental Analyst**: Automatically scores stocks based on **P/E, ROE, DER, and Dividend Yield**.
- **ML Price Predictor**: Uses a **Random Forest** classification model to predict price increase probability. 
- **Decoupled Architecture**: Training is performed on a PC/Laptop (heavy lifting) while Termux handles lean, fast inference.

## 📱 Termux Quick Start (Recommended)

1. **Install Termux API App**:
   - Install **Termux:API** from [F-Droid](https://f-droid.org/en/packages/com.termux.api/).
   - Grant necessary hardware permissions in Android Settings.

2. **Run Automated Setup**:
   ```bash
   chmod +x termux_setup.sh
   ./termux_setup.sh
   ```

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

## ⚙️ Configuration (config.yaml)

Key parameters are centralized in `config.yaml`:
- **Initial Cash**: Rp 100M default.
- **Risk**: TP/SL levels, Max Drawdown, and Profit Freeze.
- **Intelligence**: Thresholds for ROE, P/E, and ML Confidence.

## 🤖 Bot Commands

- `/start`: Open Main Menu.
- `/status`: System health (RAM/Bat/Temp) + **Intel Status**.
- `/portfolio`: Performance summary (Daily/Weekly/Monthly).
- `/signals`: Latest recommendations with **Intel Badges (`🧠`, `🤖`)**.
- `/logs`: View rotating system logs.

## 🛠️ Tech Stack
- **Python 3.13**: Quant engine, Scikit-Learn, joblib, yfinance.
- **Node.js 22+**: Baileys (WhatsApp) bridge.
- **SQLite**: High-performance bulk-caching and log audit trail.
- **PM2**: Resilient process management.

---
*Institutional Grade | ML Powered | Secure & Robust*
