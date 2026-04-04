import sys
import os
sys.path.append(os.getcwd())

from utils.kaggle_bridge import setup_kaggle_env, load_kaggle_secrets
from utils.firebase_handler import FirebaseHandler
import telebot # python-telebot

def main():
    setup_kaggle_env()
    secrets = load_kaggle_secrets()
    fb = FirebaseHandler(secrets["firebase"])
    
    if not secrets["telegram"]["enabled"]:
        print("❌ Telegram not enabled.")
        return

    bot = telebot.TeleBot(secrets["telegram"]["token"])
    # Note: We need a CHAT_ID. Usually stored in config or secrets.
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") # Or passed via secrets

    print("📊 Generating Cloud Performance Report...")
    
    # 1. Fetch latest state
    history = fb.get_history(limit=5)
    trades = fb.get_all_trades()
    open_positions = [t for t in trades if t.get('status') == 'OPEN']
    
    # 2. Format Message
    msg = "🛡️ **GLU-STOCK CLOUD STATUS** 🛡️\n\n"
    msg += f"✅ **Sync**: Firebase Connected\n"
    msg += f"📦 **Open Positions**: {len(open_positions)}\n"
    msg += "\n📜 **Latest Events**:\n"
    for event in history:
        msg += f"- [{event['phase']}] {event['details'][:50]}...\n"

    if chat_id:
        bot.send_message(chat_id, msg, parse_mode="Markdown")
        print("✅ Report sent to Telegram.")
    else:
        print("⚠️ No CHAT_ID found. Report printed to console only.")
        print(msg)

if __name__ == "__main__":
    main()
 Riverside
 Riverside
 Riverside
 Riverside
