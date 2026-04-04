import numpy as np
import pandas as pd
import json
import os
from typing import Dict, Any, Optional

try:
    import tensorflow.lite as tflite
except ImportError:
    try:
        import tflite_runtime.interpreter as tflite
    except ImportError:
        tflite = None

class CNNPredictor:
    """
    CNN inference engine for PC/Cloud kernels using TFLite.
    Handles T+2, T+5, and T+30 prediction horizons.
    """
    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or "data/models"
        self.interpreters = {}
        self.window_size = 30
        self._load_models()

    def _load_models(self):
        horizons = ["daily_t2", "weekly_t5", "monthly_t30"]
        if tflite is None:
            return

        for h in horizons:
            path = os.path.join(self.model_dir, f"cnn_{h}.tflite")
            if os.path.exists(path):
                try:
                    interpreter = tflite.Interpreter(model_path=path)
                    interpreter.allocate_tensors()
                    self.interpreters[h] = interpreter
                except: pass

    def predict(self, df: pd.DataFrame, horizon: str = "daily_t2") -> float:
        """ Predicts bullish probability (0-1). """
        if horizon not in self.interpreters or len(df) < self.window_size:
            return 0.5 # Neutral fallback

        try:
            cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            # Ensure 'Adj' columns exist
            for c in cols:
                if f'Adj_{c}' not in df.columns:
                    df[f'Adj_{c}'] = df[c]

            feature_cols = cols + [f'Adj_{c}' for c in cols]
            data = df[feature_cols].tail(self.window_size).values
            
            data = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0) + 1e-7)
            
            interpreter = self.interpreters[horizon]
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            input_data = np.expand_dims(data.astype(np.float32), axis=0)
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            
            output_data = interpreter.get_tensor(output_details[0]['index'])[0]
            bullish_prob = float(output_data[1])
            
            return bullish_prob
        except Exception:
            return 0.5
 Riverside
 Riverside
 Riverside
