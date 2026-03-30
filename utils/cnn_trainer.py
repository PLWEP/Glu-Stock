import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
from typing import Tuple, List

class CNNTrainer:
    """
    Builds and trains a 10-layer 1D-CNN for stock price classification.
    Optimized for multi-channel input (OHLCV + Adj).
    """

    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.num_channels = 10 # O,H,L,C,V + Adj(O,H,L,C,V)

    def build_model(self) -> models.Model:
        """
        Creates the 10-layer 1D-CNN architecture based on the SOTA paper.
        8 Conv1D layers + 2 Fully Connected layers.
        """
        model = models.Sequential([
            # 8 Convolutional Layers
            layers.Input(shape=(self.window_size, self.num_channels)),
            layers.Conv1D(64, kernel_size=3, padding='same', activation='relu'),
            layers.Conv1D(64, kernel_size=3, padding='same', activation='relu'),
            layers.MaxPooling1D(pool_size=2),
            
            layers.Conv1D(128, kernel_size=3, padding='same', activation='relu'),
            layers.Conv1D(128, kernel_size=3, padding='same', activation='relu'),
            layers.MaxPooling1D(pool_size=2),
            
            layers.Conv1D(256, kernel_size=3, padding='same', activation='relu'),
            layers.Conv1D(256, kernel_size=3, padding='same', activation='leaky_relu'),
            layers.Conv1D(256, kernel_size=3, padding='same', activation='leaky_relu'),
            layers.Conv1D(256, kernel_size=3, padding='same', activation='leaky_relu'),
            layers.GlobalAveragePooling1D(),
            
            # 2 Fully Connected Layers
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(2, activation='softmax') # [Bearish, Bullish]
        ])
        
        model.compile(optimizer='adam', 
                      loss='sparse_categorical_crossentropy', 
                      metrics=['accuracy'])
        return model

    def prepare_data(self, df: pd.DataFrame, target_shift: int = 2) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepares 10-channel 'images' using z-score normalization.
        """
        # Ensure 10 channels: open, high, low, close, volume, 
        # adj_open, adj_high, adj_low, adj_close, adj_volume
        cols = ['open', 'high', 'low', 'close', 'volume']
        if 'adj_open' not in df.columns:
            # Create dummy adj columns if missing
            for c in cols: df[f'adj_{c}'] = df[c] * 0.99 
        
        feature_cols = cols + [f'adj_{c}' for c in cols]
        data = df[feature_cols].values
        
        # Normalization: (x - min) / (max - min)
        data = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0) + 1e-7)
        
        X, y = [], []
        for i in range(len(data) - self.window_size - target_shift):
            window = data[i : i + self.window_size]
            # Target: 1 if future price > current close else 0
            future_close = df['close'].iloc[i + self.window_size + target_shift]
            current_close = df['close'].iloc[i + self.window_size - 1]
            label = 1 if future_close > current_close else 0
            
            X.append(window)
            y.append(label)
            
        return np.array(X), np.array(y)

    def train_and_export(self, X: np.ndarray, y: np.ndarray, model_name: str):
        model = self.build_model()
        model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2, verbose=1)
        
        h5_path = f"data/models/{model_name}.h5"
        tflite_path = f"data/models/{model_name}.tflite"
        os.makedirs("data/models", exist_ok=True)
        
        # Save H5
        model.save(h5_path)
        
        # Convert to TFLite
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
            
        print(f"Model exported to {tflite_path}")

if __name__ == "__main__":
    # Example Usage (Placeholder for actual training trigger)
    trainer = CNNTrainer()
    print("CNN Trainer Ready. Use prepare_data() and train_and_export() locally.")
