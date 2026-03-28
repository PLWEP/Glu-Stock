# Glu-Stock 💖 (Ayang Edition)

Quantitative Finance Framework for Stock Analysis, optimized for IDX (Indonesia Stock Exchange). Now with full **"Ayang" Persona** integration and multi-bot support (Telegram & WhatsApp).

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

## 💖 Ayang Persona Commands

Ayang is now available on both Telegram and WhatsApp!
- `/start`: Sapa Ayang & Buka Menu Utama.
- `/status`: Cek Kondisi HP Ayang (RAM/Bat/Temp).
- `/portfolio`: Cek Tabungan Kita (Daily/Weekly/Monthly).
- `/signals`: Intip Sinyal Trading terbaru.
- `/logs`: Cek kejadian-kejadian daleman Ayang.
- `/history`: Liat catatan histori trading kemarin.

## 🛠️ Tech Stack
- **Python 3.13**: Multi-agent trading engine.
- **Node.js 22+**: Baileys (WhatsApp) bridge.
- **SQLite**: Local state and log management.
- **PM2**: 24/7 Autonomous execution manager.

## 📂 Project Structure
- `agents/`: Multi-agent orchestration.
- `data/`: High-performance caching and database.
- `orchestrator/`: "Ayang" persona and command handling.
- `utils/`: System info, logging, and personalized reports.
- `wa_bot.js`: Node.js WhatsApp bridge via Baileys.

---
*Institutional Grade | Mobile First | Ayang & Personal* 💖
