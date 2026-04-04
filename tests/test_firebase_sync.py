import sys
import os
sys.path.append(os.getcwd())

from utils.firebase_handler import FirebaseHandler
from utils.config import ConfigLoader

def test_firebase():
    loader = ConfigLoader()
    fb_config = loader.get_firebase_config()
    
    if not fb_config.get("enabled"):
        print("❌ Firebase is not enabled in config.yaml")
        return

    print(f"Connecting to: {fb_config.get('database_url')}")
    try:
        handler = FirebaseHandler(fb_config)
        
        # Test Event Log
        print("Logging test event...")
        handler.log_event("test_strat", "VERIFY", details="Firebase Migration Test")
        
        # Test Trade
        print("Inserting test trade...")
        handler.insert_trade({
            'ticker': 'TEST.JK',
            'entry_price': 1000,
            'qty': 100,
            'strategy': 'TEST'
        })
        
        # Query
        history = handler.get_history(limit=1)
        if history:
            print(f"✅ Success! Last event: {history[0].get('details')}")
        else:
            print("❌ Log failed or history empty.")
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")

if __name__ == "__main__":
    test_firebase()
