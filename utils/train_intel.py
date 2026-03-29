from orchestrator.orchestrator import PipelineOrchestrator
import sys

def train():
    """ Runs the initial training for Glu-Stock ML Brain. """
    print("🧠 GLU-STOCK: Intelligence Training Started...")
    
    orchestrator = PipelineOrchestrator()
    
    # Indonesian Blue-Chip Stocks for Training (LQ45 Base)
    training_tickers = [
        "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", 
        "GOTO.JK", "UNVR.JK", "ADRO.JK", "AMRT.JK", "BBNI.JK"
    ]
    
    try:
        orchestrator.train_intelligence(tickers=training_tickers)
        print("✅ Training Complete! ML Model is now ready for production. 💹")
    except Exception as e:
        print(f"❌ Training Failed: {e}")

if __name__ == "__main__":
    train()
