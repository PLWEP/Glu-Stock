#!/bin/bash

# Glu-Stock Termux Automated Setup Script
# This script installs all necessary system and python dependencies.

echo "🚀 Starting Glu-Stock Setup for Termux..."

# 1. Update and Upgrade System
echo "🔄 Updating system packages..."
pkg update -y && pkg upgrade -y

# 2. Install Core Packages
echo "📦 Installing core packages (Python, Git, Node.js, etc.)..."
pkg install -y python git nodejs-lts termux-api

# 3. Setup Python Virtual Environment
echo "🐍 Setting up Python Virtual Environment..."
python -m venv glustock_venv
source glustock_venv/bin/activate

# 4. Install Python Dependencies
echo "📥 Installing Python dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Install PM2 via NPM
echo "⚡ Installing PM2 for process management..."
npm install -g pm2

# 6. Initialize Configuration
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
