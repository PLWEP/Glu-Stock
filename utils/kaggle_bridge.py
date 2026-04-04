import json
import os
from typing import Dict, Any

def load_kaggle_secrets() -> Dict[str, Any]:
    """
    Loads Firebase and Telegram credentials from Kaggle User Secrets.
    Requires 'FIREBASE_URL', 'FIREBASE_KEY_JSON', and 'TELEGRAM_TOKEN' to be set in Kaggle.
    """
    try:
        from kaggle_secrets import UserSecretsClient
        user_secrets = UserSecretsClient()
        
        firebase_url = user_secrets.get_secret("FIREBASE_URL")
        firebase_key_raw = user_secrets.get_secret("FIREBASE_KEY_JSON")
        telegram_token = user_secrets.get_secret("TELEGRAM_TOKEN")
        
        # Parse the raw JSON string from secrets
        firebase_key = json.loads(firebase_key_raw)
        
        return {
            "firebase": {
                "enabled": True,
                "database_url": firebase_url,
                "service_account_json": firebase_key
            },
            "telegram": {
                "enabled": True,
                "token": telegram_token
            }
        }
    except Exception as e:
        print(f"[ERROR] Failed to load Kaggle Secrets: {e}")
        # Return empty or placeholder for local development
        return {"firebase": {"enabled": False}, "telegram": {"enabled": False}}

def setup_kaggle_env():
    """Installs necessary libraries for the Kaggle environment."""
    print("📥 Installing dependencies...")
    os.system("pip install -q yfinance firebase-admin pandas scikit-learn tensorflow joblib")
    print("✅ Dependencies installed.")
 Riverside
