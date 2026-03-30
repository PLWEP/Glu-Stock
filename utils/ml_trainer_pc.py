import pandas as pd
import numpy as np
import os
import joblib
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
from features.features import FeatureEngineer
from data.data import StockDataHandler

class PCTrainer:
    """
    High-power trainer for PC/Laptop environment.
    Handles large-scale data ingestion and model optimization.
    """
    def __init__(self, model_dir: str = "data/models"):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.feature_engineer = FeatureEngineer()
        self.data_handler = StockDataHandler()
        
        # Consistent features between Trainer and Predictor
        self.feature_cols = ['rsi', 'macd_diff', 'sma_20', 'ema_20', 'bb_width']

    def fetch_training_pool(self, tickers: list, years: int = 5):
        """ Downloads a large historical dataset for training. """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365 * years)).strftime('%Y-%m-%d')
        
        print(f"Trainer: Fetching {years} years of data for {len(tickers)} tickers...")
        df = self.data_handler.fetch_data(tickers, start_date, end_date, interval="1d")
        
        print("Trainer: Engineering features...")
        df = self.feature_engineer.add_indicators(df)
        df = self.feature_engineer.clean_features(df)
        return df

    def prepare_labeled_data(self, df: pd.DataFrame, target_horizon: int = 5):
        """ Labels data for binary classification (Price Up vs Not Up). """
        print(f"Trainer: Labeling data with horizon={target_horizon}...")
        
        df_copy = df.copy().sort_index(level='date')
        
        def create_labels(group):
            group['target'] = (group['close'].shift(-target_horizon) > group['close']).astype(int)
            return group

        df_labeled = df_copy.groupby(level='ticker', group_keys=False).apply(create_labels)
        df_labeled = df_labeled.dropna(subset=['target'] + self.feature_cols)
        
        X = df_labeled[self.feature_cols]
        y = df_labeled['target']
        return X, y

    def train_and_export(self, X, y, model_name: str = "glu_brain_v1.joblib"):
        """ Trains a robust RandomForest with GridSearch and exports the result. """
        print("Trainer: Starting model optimization (GridSearch)...")
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5]
        }
        
        rf = RandomForestClassifier(random_state=42)
        grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, n_jobs=-1, verbose=1)
        grid_search.fit(X_train, y_train)
        
        best_model = grid_search.best_estimator_
        
        # Evaluate
        print("\n--- Model Evaluation ---")
        y_pred = best_model.predict(X_test)
        print(classification_report(y_test, y_pred))
        
        # Save Model + Metadata
        model_path = os.path.join(self.model_dir, model_name)
        metadata = {
            "model": best_model,
            "features": self.feature_cols,
            "trained_at": datetime.now().isoformat(),
            "accuracy": best_model.score(X_test, y_test)
        }
        
        joblib.dump(metadata, model_path)
        print(f"\nSUCCESS: Model exported to {model_path}")
        print(f"Best Params: {grid_search.best_params_}")
        return model_path

if __name__ == "__main__":
    # Example training pool: Top IDX Stocks
    lq45_tickers = [
        "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", 
        "GOTO.JK", "UNVR.JK", "ADRO.JK", "AMRT.JK", "BBNI.JK",
        "ICBP.JK", "KLBF.JK", "PGAS.JK", "PTBA.JK", "UNTR.JK"
    ]
    
    trainer = PCTrainer()
    data = trainer.fetch_training_pool(lq45_tickers, years=5)
    X, y = trainer.prepare_labeled_data(data, target_horizon=5) # 5 days lookahead
    trainer.train_and_export(X, y)
