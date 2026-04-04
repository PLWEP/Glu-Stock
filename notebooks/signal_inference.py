import sys
import os
sys.path.append(os.getcwd())

from utils.kaggle_bridge import setup_kaggle_env, load_kaggle_secrets
from utils.firebase_handler import FirebaseHandler
from agents.agents import StrategyAgent

def main():
    setup_kaggle_env()
    secrets = load_kaggle_secrets()
    fb = FirebaseHandler(secrets["firebase"])

    # --- Kaggle Environment Detection ---
    # Assuming models are either in /kaggle/input/glustock-brains/ 
    # or /kaggle/input/model-retrain/ if using notebook output
    model_dir = "/kaggle/input/glustock-brains"
    if not os.path.exists(model_dir):
        # Fallback to local data/models if running elsewhere
        model_dir = "data/models"

    print(f"🧠 Starting Signal Inference (Model Dir: {model_dir})")
    
    # 1. Pull tickers from 'research' queue
    candidates = fb.get_and_clear_queue("research")
    if not candidates:
        print("📭 'research' queue is empty. Nothing to analyze.")
        return

    # 2. Initialize Strategy Agent with custom model path
    strategy_agent = StrategyAgent(model_dir=model_dir)

    signals = {}
    print(f"🔬 Analyzing {len(candidates)} candidates...")
    
    for ticker in candidates:
        try:
            # Note: StrategyAgent internally fetches data and runs RF/CNN ensemble
            signal = strategy_agent.analyze_ticker(ticker)
            
            # Filter for high conviction (Ensemble > Threshold)
            if signal.get("ens_conviction", 0) >= 0.7:
                signals[ticker] = signal
                print(f"🔥 BULLISH SIGNAL: {ticker} (Conv: {signal['ens_conviction']:.2f})")
        except Exception as e:
            print(f"⚠️ Error analyzing {ticker}: {e}")

    # 3. Push to 'signals' queue
    if signals:
        fb.push_task("signals", signals)
        fb.log_event("inference", "SIGNALS", details=f"Generated {len(signals)} signals.")
        print(f"✅ Pushed {len(signals)} signals to Firebase.")
    else:
        print("💤 No high-conviction signals generated today.")

if __name__ == "__main__":
    main()
 Riverside
 Riverside
 Riverside
