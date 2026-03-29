import os
from utils.ml_trainer_pc import PCTrainer
from utils.cnn_trainer import CNNTrainer

def run_unified_training():
    print("🚀 GLU-STOCK: Unified Intelligence Training (v11.0)")
    print("---------------------------------------------------")
    
    # 1. Tickers for training (LQ45 focus)
    tickers = [
        "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", 
        "GOTO.JK", "UNVR.JK", "ADRO.JK", "AMRT.JK", "BBNI.JK",
        "ICBP.JK", "KLBF.JK", "PGAS.JK", "PTBA.JK", "UNTR.JK", "CPIN.JK", "BRIS.JK", "INKP.JK"
    ]
    
    # 2. Random Forest Training (Brain v1)
    print("\n🧠 [STAGE 1] Training Random Forest (Ensemble Brain v1)...")
    rf_trainer = PCTrainer()
    data = rf_trainer.fetch_training_pool(tickers, years=5)
    X, y = rf_trainer.prepare_labeled_data(data, target_horizon=5)
    rf_trainer.train_and_export(X, y, model_name="glu_brain_v1.joblib")
    
    # 3. CNN Training (Deep Intelligence Brain v2)
    print("\n🖼️ [STAGE 2] Training CNN (Deep Intelligence Brain v2)...")
    cnn_trainer = CNNTrainer(window_size=30)
    
    # Horizons
    tasks = [
        ("daily_t2", 2),
        ("weekly_t5", 5),
        ("monthly_t30", 30)
    ]
    
    for name, horizon in tasks:
        print(f"\n--- Training CNN for {name.upper()} (T+{horizon}) ---")
        X_cnn, y_cnn = cnn_trainer.prepare_data(data, target_shift=horizon)
        if len(X_cnn) > 100:
            cnn_trainer.train_and_export(X_cnn, y_cnn, model_name=f"cnn_{name}")
        else:
            print(f"Skipping {name}: Not enough data samples for CNN.")

    print("\n✅ UNIFIED TRAINING COMPLETE!")
    print("Transfer all files from data/models/ to Termux before running the bot.")

if __name__ == "__main__":
    run_unified_training()
