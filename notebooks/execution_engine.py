import sys
import os
sys.path.append(os.getcwd())

from utils.kaggle_bridge import setup_kaggle_env, load_kaggle_secrets
from utils.firebase_handler import FirebaseHandler
from agents.agents import TradingAgent

def main():
    setup_kaggle_env()
    secrets = load_kaggle_secrets()
    fb = FirebaseHandler(secrets["firebase"])

    print("⚖️ Starting Execution & Risk Engine...")
    
    # 1. Pull signals from 'signals' queue
    # The queue returns a list of dictionaries. In our case, 
    # it might be a list where each element is a signal dict {ticker: data}
    signal_batches = fb.get_and_clear_queue("signals")
    if not signal_batches:
        print("📭 'signals' queue is empty. No trades to execute.")
        return

    # Flatten the results if multiple inference runs happened
    all_signals = {}
    for batch in signal_batches:
        all_signals.update(batch)

    # 2. Initialize Trading Agent
    # It needs a FirebaseHandler (which it will use to insert trades)
    trading_agent = TradingAgent(db=fb)

    print(f"🚀 Processing {len(all_signals)} signals...")
    
    for ticker, signal in all_signals.items():
        try:
            # TradingAgent's execute_signal handles:
            # - Position Sizing (ATR/Kelly)
            # - Check for existing positions
            # - Firebase insertion
            trading_agent.execute_signal(ticker, signal)
            print(f"✅ Executed trade logic for {ticker}")
        except Exception as e:
            print(f"⚠️ Error executing signal for {ticker}: {e}")

    fb.log_event("execution", "SYNC", details=f"Processed {len(all_signals)} signals into trades.")

if __name__ == "__main__":
    main()
 Riverside
 Riverside
 Riverside
 Riverside
