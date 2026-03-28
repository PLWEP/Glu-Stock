#!/bin/bash

# Glu-Stock 💖 Termux Automated Setup Script (Ayang Edition)
# This script installs all necessary system, python, and node dependencies.

echo "🌸 Halo Sayang! Ayang siap bantu setup sistem trading kita di HP kamu..."
echo "🚀 Memulai Setup Glu-Stock untuk Termux..."

# 1. Update and Upgrade System
echo "🔄 Memperbarui sistem sebentar ya sayang..."
pkg update -y && pkg upgrade -y

# 2. Install Core Packages & Repositories
echo "📦 Memasang paket inti dan akses gudang aplikasi (TUR)..."
pkg install -y python git nodejs-lts termux-api
pkg install -y tur-repo  # Activate community user repository

# 3. Update repositories again to include TUR
pkg update -y

# 4. Install Heavy Pre-Compiled Packages (Saves hours of compilation)
echo "⚡ Memasang Pandas, Numpy, dan Psutil via PKG (biar HP kamu nggak capek)..."
pkg install -y python-pandas python-numpy python-psutil

# 5. Setup Python Virtual Environment with System Access
echo "🐍 Menyiapkan Lingkungan Python (Venv) buat Ayang..."
rm -rf glustock_venv
python -m venv --system-site-packages glustock_venv
source glustock_venv/bin/activate

# 6. Install Lightweight Python Dependencies
echo "📥 Mengunduh sisa buku panduan Ayang (Requirements.txt)..."
pip install --upgrade pip
# Force uninstall problematic yfinance if exists
pip uninstall yfinance -y
pip install yfinance==0.2.52
pip install -r requirements.txt

# 7. Install Node Dependencies for WhatsApp Bot
echo "📱 Menyiapkan jembatan WhatsApp (Baileys)..."
npm install --no-audit --no-fund

# 8. Install PM2 via NPM
echo "⚡ Memasang PM2 (Biar Ayang tetap jaga 24 jam buat kamu)..."
npm install -g pm2

# 9. Initialize Configuration
if [ ! -f .env ]; then
    echo "🔑 Membuat catatan rahasia kita (.env)..."
    echo "TELEGRAM_BOT_TOKEN=isi_token_bot_kamu_di_sini" > .env
    echo "TELEGRAM_CHAT_ID=isi_id_telegram_kamu_di_sini" >> .env
    echo "" >> .env
    echo "# Nomor WhatsApp Kamu (Hanya angka, tanpa @s.whatsapp.net)" >> .env
    echo "WHATSAPP_AUTHORIZED_NUMBERS=628xxxxxxxxx" >> .env
    echo "" >> .env
    echo "# Jalur akses Python buat Ayang" >> .env
    echo "PYTHON_PATH=./glustock_venv/bin/python" >> .env
fi

echo "✅ Setup Selesai Sayang! ✨"
echo "--------------------------------------------------"
echo "Untuk mulai melihat kerja Ayang lewat PM2:"
echo "1. Aktifkan venv: source glustock_venv/bin/activate"
echo "2. Jalankan system: pm2 start ecosystem.config.js"
echo ""
echo "Jangan lupa scan QR Code buat WhatsApp ya sayang lewat:"
echo "pm2 logs glu-stock-wa"
echo "--------------------------------------------------"
echo "Semangat Tradingnya ya Sayang! Ayang selalu dukung! 💖"
