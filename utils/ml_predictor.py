import pandas as pd
import numpy as np
import os
import joblib
import json
from typing import List, Tuple, Optional, Any, Dict
from utils.logger import JsonLogger

class MLPredictor:
    """
    Inference engine for PC/Cloud kernels.
    Loads pre-trained models and provides high-speed predictions.
    """
    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or "data/models"
        self.logger = JsonLogger(log_file="logs/ml_predictor.log")
        
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)
        
        self.model_path = os.path.join(self.model_dir, "glu_brain_v1.joblib")
        
        # Internal state
        self.model = None
        self.features = []
        self.metadata = {}
        
        # Load the brain
        self._load_brain()

    def _load_brain(self):
        """ Loads the model and metadata. """
        if os.path.exists(self.model_path):
            try:
                brain = joblib.load(self.model_path)
                
                if isinstance(brain, dict):
                    self.model = brain.get("model")
                    self.features = brain.get("features", [])
                    self.metadata = {
                        "accuracy": brain.get("accuracy", 0),
                        "trained_at": brain.get("trained_at", "Unknown")
                    }
                    self.logger.info(f"MLPredictor: Brain loaded! (Acc: {self.metadata['accuracy']:.2%}, Trained: {self.metadata['trained_at']})")
                else:
                    self.model = brain
                    self.logger.info("MLPredictor: Basic model loaded (No metadata).")
                    
            except Exception as e:
                self.logger.error("MLPredictor: Failed to load brain", error=str(e))
        else:
            self.logger.warning(f"MLPredictor: No brain found at {self.model_path}.")

    def predict_proba(self, latest_features: pd.DataFrame) -> float:
        """ Fast inference using the pre-trained brain. """
        if self.model is None:
            return 0.5 # Neutral if no model
            
        try:
            X = latest_features[self.features].tail(1)
            prob = self.model.predict_proba(X)[0][1]
            return float(prob)
        except Exception as e:
            return 0.5

    def get_info(self) -> Dict[str, Any]:
        """ Returns metadata about the current model. """
        return {
            "status": "Online" if self.model else "Model Missing",
            "accuracy": self.metadata.get("accuracy", 0),
            "trained_at": self.metadata.get("trained_at", "N/A"),
            "features": self.features
        }
 Riverside
 Riverside
 Riverside
