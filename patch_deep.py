import json, glob

rf_logic = """# 🧠 SECTION 3: CORE LOGIC (Panel Training Pipeline)
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import ta

def build_panel_data(universe, period="5y"):
    all_X, all_y = [], []
    print(f"📉 Fetching {period} of data for {len(universe)} tickers...")
    feature_names = ['Returns', 'RSI', 'MACD', 'BB_High', 'BB_Low']
    
    for ticker in universe:
        df = yf.download(ticker, period=period, progress=False)
        if len(df) > 100:
            # 1. Price Action
            df['Returns'] = df['Close'].pct_change()
            
            # 2. Momentum (RSI)
            df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
            
            # 3. Trend (MACD)
            macd = ta.trend.MACD(close=df['Close'])
            df['MACD'] = macd.macd_diff()
            
            # 4. Volatility (Bollinger Bands)
            bollinger = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
            df['BB_High'] = bollinger.bollinger_hband_indicator()
            df['BB_Low'] = bollinger.bollinger_lband_indicator()
            
            df = df.dropna()
            
            X = df[feature_names].values
            y = (df['Close'].shift(-1) > df['Close']).iloc[:-1].values.astype(int)
            all_X.append(X[:len(y)])
            all_y.append(y)
    
    print(f"✅ Successfully aggregated market data.")
    if len(all_X) == 0:
        return None, None, feature_names
    return np.vstack(all_X), np.concatenate(all_y), feature_names

def train_rf(X_train, y_train):
    print(f"🧠 Training Institutional RF Brain on {len(y_train)} samples...")
    model = RandomForestClassifier(n_estimators=300, max_depth=10, min_samples_leaf=5, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)
    return model
"""

rf_main = """# 🚀 SECTION 4: MAIN EXECUTION
def run_retrain():
    secrets = KaggleInfra.load_secrets()
    fb = FirebaseHandler(secrets)
    output_dir = "/kaggle/working/"
    
    universe = get_full_idx_universe()
    
    # 1. Build Panel & Train RF
    X, y, feature_names = build_panel_data(universe)
    if X is None:
        print('⚠️ Retraining aborted due to data fetch failure.')
        return
        
    # 🛑 CRITICAL FIX: shuffle=False to prevent Time-Leakage!
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, shuffle=False)
    
    rf_model = train_rf(X_train, y_train)
    train_acc = rf_model.score(X_train, y_train)
    val_acc = rf_model.score(X_test, y_test)
    
    brain_data = {
        "model": rf_model, 
        "features": feature_names, 
        "train_accuracy": train_acc,
        "val_accuracy": val_acc,
        "trained_at": datetime.now().isoformat()
    }
    joblib.dump(brain_data, os.path.join(output_dir, "glu_brain_v1.joblib"))
    
    rich_log = f"RF Training Complete.\\n🎓 Training Acc: {train_acc:.2%}\\n🛡️ OOS Validation Acc: {val_acc:.2%}\\n📊 Target Universe: {len(universe)} symbols\\n🧠 Features: {len(feature_names)}"
    fb.log_event("RETRAINING_RF", rich_log)
    print(f"✅ RF Model updated successfully: Train Acc {train_acc:.3f} | OOS Val Acc {val_acc:.3f}")

run_retrain()
"""

cnn_logic = """# 🧠 SECTION 3: CORE LOGIC (Panel Training Pipeline)
def build_cnn_panel_data(universe, seq_len=30, period="5y"):
    all_X, all_y = [], []
    print(f"📉 Fetching {period} of data for {len(universe)} tickers...")
    for ticker in universe:
        df = yf.download(ticker, period=period, progress=False)
        if len(df) > seq_len:
            data = df[['Open', 'High', 'Low', 'Close', 'Volume']].values
            
            for i in range(len(data) - seq_len - 1):
                # 🛑 CRITICAL FIX: Rolling Window Normalization to prevent Lookahead Bias!
                seq = data[i:i+seq_len]
                seq_min = seq.min(axis=0)
                seq_max = seq.max(axis=0)
                norm_seq = (seq - seq_min) / (seq_max - seq_min + 1e-7)
                
                all_X.append(norm_seq)
                
                # Target: 1 if tomorrow's close > today's close
                y_val = 1 if data[i+seq_len+1, 3] > data[i+seq_len, 3] else 0
                all_y.append(y_val)
                
    print("✅ Successfully aggregated market sequences.")
    if len(all_X) == 0:
        return None, None
    return np.array(all_X), np.array(all_y)

def train_cnn(X, y):
    print(f"🧠 Training Deep L-CNN Super Brain on {len(y)} target sequences...")
    model = tf.keras.Sequential([
        # Spatial Feature Extraction
        tf.keras.layers.Conv1D(64, 3, activation='relu', padding='same', input_shape=(30, 5)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(128, 3, activation='relu', padding='same'),
        tf.keras.layers.BatchNormalization(),
        
        # Temporal Dependency (NEW!)
        tf.keras.layers.LSTM(64, return_sequences=False),
        
        # Classification Head
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(2, activation='softmax')
    ])
    
    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(initial_learning_rate=1e-3, decay_steps=10000, decay_rate=0.9)
    optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)
    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    
    # 🛑 CRITICAL FIX: shuffle=False during split to prevent Time-Leakage!
    split_idx = int(len(X) * 0.85)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    history = model.fit(X_train, y_train, epochs=40, batch_size=128, validation_data=(X_test, y_test), verbose=1)
    
    final_train_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]
    return model, final_train_acc, final_val_acc
"""

cnn_main = """# 🚀 SECTION 4: MAIN EXECUTION
def run_retrain():
    secrets = KaggleInfra.load_secrets()
    fb = FirebaseHandler(secrets)
    output_dir = "/kaggle/working/"
    
    universe = get_full_idx_universe()
    
    X_all, y_all = build_cnn_panel_data(universe)
    if X_all is None:
        print('⚠️ Retraining aborted due to data fetch failure.')
        return
        
    cnn_model, t_acc, v_acc = train_cnn(X_all, y_all)
    
    print("⚙️ Converting to TFLite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(cnn_model)
    tflite_model = converter.convert()
    with open(os.path.join(output_dir, "cnn_daily_t2.tflite"), "wb") as f:
        f.write(tflite_model)
        
    rich_log = f"L-CNN Deep Training Complete.\\n🎓 Training Acc: {t_acc:.2%}\\n🛡️ OOS Validation Acc: {v_acc:.2%}\\n📊 Target Universe: {len(universe)} symbols\\n🧠 Sequences: {len(y_all)}"
    fb.log_event("RETRAINING_CNN", rich_log)
    print(f"✅ CNN Model updated successfully: Train Acc {t_acc:.3f} | OOS Val Acc {v_acc:.3f}")

run_retrain()
"""

for f in glob.glob("notebooks/*.ipynb"):
    if "00a" in f:
        data = json.load(open(f, encoding='utf-8'))
        for c in data['cells']:
            if c['cell_type'] == 'code':
                src = "".join(c['source'])
                if "def build_panel_data" in src:
                    c['source'] = [line + '\n' for line in rf_logic.split('\n')]
                    c['source'][-1] = c['source'][-1].strip()
                elif "def run_retrain" in src:
                    c['source'] = [line + '\n' for line in rf_main.split('\n')]
                    c['source'][-1] = c['source'][-1].strip()
                # Also inject ta into pip install
                if "!pip install" in src and "ta" not in src:
                    c['source'] = [src.replace("scikit-learn joblib", "scikit-learn joblib ta")]
        json.dump(data, open(f, 'w', encoding='utf-8'), indent=1)
        
    if "00b" in f:
        data = json.load(open(f, encoding='utf-8'))
        for c in data['cells']:
            if c['cell_type'] == 'code':
                src = "".join(c['source'])
                if "def build_cnn_panel_data" in src:
                    c['source'] = [line + '\n' for line in cnn_logic.split('\n')]
                    c['source'][-1] = c['source'][-1].strip()
                elif "def run_retrain" in src:
                    c['source'] = [line + '\n' for line in cnn_main.split('\n')]
                    c['source'][-1] = c['source'][-1].strip()
        json.dump(data, open(f, 'w', encoding='utf-8'), indent=1)
        
print("Perfect Deep Analysis Patches injected!")
