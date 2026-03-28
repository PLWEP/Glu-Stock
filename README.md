# Glu-Stock 💹

Quantitative Finance Framework for Stock Analysis, optimized for IDX (Indonesia Stock Exchange). Features a multi-agent engine with Telegram and WhatsApp bot integration.

## 📱 Termux Quick Start (Recommended)

To set up the platform on Termux (Android):

1. **Install Termux API App**:
   - Install **Termux:API** from [F-Droid](https://f-droid.org/en/packages/com.termux.api/).
   - Grant necessary hardware permissions in Android Settings.

2. **Run Automated Setup**:
   ```bash
   git clone https://github.com/your-repo/Glu-Stock.git
   cd Glu-Stock
   chmod +x termux_setup.sh
   ./termux_setup.sh
   ```

3. **WhatsApp Authentication**:
   ```bash
   pm2 start wa_bot.js
   pm2 logs glu-stock-wa
   # Scan the QR code with your phone. 
   # Stop with Ctrl+C (PM2 keeps it running in background).
   ```

4. **Activate & Run All**:
   ```bash
   pm2 start ecosystem.config.js
   pm2 save
   ```

## ⚙️ Configuration (.env)

Update your `.env` file with the following:
- `TELEGRAM_BOT_TOKEN`: From @BotFather.
- `TELEGRAM_CHAT_ID`: Your Personal ID.
- `WHATSAPP_AUTHORIZED_NUMBERS`: Your WA number (comma separated, e.g., `628123456789`).
- `PYTHON_PATH`: `./glustock_venv/bin/python` (Default for Termux).

## 🤖 Bot Commands

The system features an interactive "Ayang" persona for the chatbot interface:
- `/start`: Open Main Menu.
- `/status`: System health report (RAM/Battery/Temp).
- `/portfolio`: Performance summary (Daily/Weekly/Monthly).
- `/signals`: Latest trading recommendations.
- `/logs`: View system internal logs.
- `/history`: Audit trail of strategy executions.

## 🛠️ Tech Stack
- **Python 3.13**: Multi-agent trading engine.
- **Node.js 22+**: Baileys (WhatsApp) bridge.
- **SQLite**: Local state and log management.
- **PM2**: Process manager for 24/7 autonomous execution.

## 📂 Project Structure
- `agents/`: Multi-agent orchestration logic.
- `data/`: Database and caching layer.
- `orchestrator/`: Command processing and persona management.
- `utils/`: Telemetry, reporting, and alert utilities.
- `wa_bot.js`: WhatsApp bridge implementation.

---
*Institutional Grade | Mobile First | Robust Architecture*
