# Glu-Stock

Quantitative Finance Framework for Stock Analysis, optimized for IDX (Indonesia Stock Exchange).

## 📱 Termux Quick Start (Recommended)

To set up the platform on Termux (Android) or any Linux-based environment:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/Glu-Stock.git
   cd Glu-Stock
   ```

2. **Run Automated Setup**:
   ```bash
   chmod +x termux_setup.sh
   ./termux_setup.sh
   ```

3. **Activate & Run**:
   ```bash
   source glustock_venv/bin/activate
   pm2 start ecosystem.config.js
   ```

## ⚙️ Configuration

1. **Telegram Bot**:
   - Create a bot via [@BotFather](https://t.me/BotFather) and get the token.
   - Get your Chat ID via [@userinfobot](https://t.me/userinfobot).
   - Update `config.yaml` or `.env` with your credentials.

2. **Trading Parameters**:
   - Adjust `config.yaml` to set your initial capital, risk thresholds, and debug mode.

## 🛠️ Components

- **Daily Scan**: `python scheduler.py --scan daily` (Market Close)
- **Morning Alert**: `python scheduler.py --report daily` (Market Open)
- **Portfolio Recap**: `python scheduler.py --recap daily` (EOD)
- **Telegram Command Center**: `python telegram_bot.py`

## 📂 Project Structure

- `agents/`: Multi-agent orchestration (Research, Strategy, Trading, Universe).
- `data/`: High-performance caching and IDX metadata management.
- `strategies/`: Pipeline-specific signals (Daily, Weekly, Monthly).
- `utils/`: System telemetry, Telegram alerts, and institutional metrics.
- `logs/`: Structured JSON logging for audit trails.

## ⚖️ Risk Management

Every strategy enforced through the `RiskManager` includes:
- **Stop Loss (SL)** & **Take Profit (TP)** levels.
- **Position Sizing** based on portfolio equity.
- **Profit Freezing**: Prevents over-trading after successful gains.

---
*Institutional Grade | Mobile First | Open Source*
