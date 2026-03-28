#!/bin/bash

# Glu-Stock Termux Automated Setup Script (Optimized for Speed)
# This script installs all necessary system and python dependencies.

echo "🚀 Starting Glu-Stock Setup for Termux..."

# 1. Update and Upgrade System
echo "🔄 Updating system packages..."
pkg update -y && pkg upgrade -y

# 2. Install Core Packages & Repositories
echo "📦 Installing core packages and community repositories (TUR)..."
pkg install -y python git nodejs-lts termux-api
pkg install -y tur-repo  # Activate community user repository

# 3. Update repositories again to include TUR
pkg update -y

# 4. Install Heavy Pre-Compiled Packages (Saves hours of compilation)
echo "⚡ Installing heavy packages (Pandas, Numpy, Psutil) via PKG..."
pkg install -y python-pandas python-numpy python-psutil

# 5. Setup Python Virtual Environment with System Access
echo "🐍 Setting up Python Virtual Environment (with System Site-Packages)..."
rm -rf glustock_venv
python -m venv --system-site-packages glustock_venv
source glustock_venv/bin/activate

# 6. Install Lightweight Python Dependencies
echo "📥 Installing remaining dependencies from requirements.txt..."
pip install --upgrade pip
# This will skip pandas/numpy if they are already handled by system packages
pip install -r requirements.txt

# 7. Install PM2 via NPM
echo "⚡ Installing PM2 for process management..."
npm install -g pm2

# 8. Initialize Configuration
if [ ! -f .env ]; then
    echo "🔑 Creating template .env file..."
    echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env
    echo "TELEGRAM_CHAT_ID=your_chat_id_here" >> .env
fi

echo "✅ Setup Complete!"
echo "--------------------------------------------------"
echo "To start the trading engine with PM2, run:"
echo "source glustock_venv/bin/activate"
echo "pm2 start ecosystem.config.js"
echo "--------------------------------------------------"
echo "Check logs with: pm2 logs"
