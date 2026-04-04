import sys
import os
sys.path.append(os.getcwd())

from utils.kaggle_bridge import setup_kaggle_env, load_kaggle_secrets
from utils.firebase_handler import FirebaseHandler
from utils.ml_trainer_pc import MLTrainer
from utils.cnn_trainer import CNNTrainer

def main():
    setup_kaggle_env()
    secrets = load_kaggle_secrets()
    fb = FirebaseHandler(secrets["firebase"])

    print("🧠 Starting Automated Model Retraining...")
    
    # 1. RF Training
    print("Training RF Brain...")
    rf_trainer = MLTrainer()
    rf_trainer.run_all_pipelines()
    
    # 2. CNN Training
    print("Training CNN Brain...")
    cnn_trainer = CNNTrainer()
    cnn_trainer.train_all_horizons()

    print("✅ Retraining Complete. New models saved to /kaggle/working/")
    fb.log_event("training", "RETRAIN", details="RF and CNN models updated via Kaggle.")

if __name__ == "__main__":
    main()
 Riverside
 Riverside
 Riverside
