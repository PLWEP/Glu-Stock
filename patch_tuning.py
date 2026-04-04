import json, glob

rf_logic = """# 🧠 SECTION 3: CORE LOGIC (Panel Training Pipeline)
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np

def build_panel_data(universe, period="5y"):
    all_X, all_y = [], []
    print(f"📉 Fetching {period} of data for {len(universe)} tickers...")
    for ticker in universe:
        df = yf.download(ticker, period=period, progress=False)
        if len(df) > 100:
            df['Returns'] = df['Close'].pct_change()
            df['SMA_10'] = df['Close'].rolling(window=10).mean() / df['Close'] - 1
            df['SMA_50'] = df['Close'].rolling(window=50).mean() / df['Close'] - 1
            df = df.dropna()
            
            X = df[['Returns', 'SMA_10', 'SMA_50']].values
            y = (df['Close'].shift(-1) > df['Close']).iloc[:-1].values.astype(int)
            all_X.append(X[:len(y)])
            all_y.append(y)
    print(f"✅ Successfully aggregated market data.")
    if len(all_X) == 0:
        return None, None
    return np.vstack(all_X), np.concatenate(all_y)

def train_rf(X_train, y_train):
    print(f"🧠 Training Super RF Brain on {len(y_train)} samples...")
    model = RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_split=10, n_jobs=-1, random_state=42)
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
    X, y = build_panel_data(universe)
    if X is None:
        print('⚠️ Retraining aborted due to data fetch failure.')
        return
        
    # Split into highly-informative Training & Validation metrics
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    rf_model = train_rf(X_train, y_train)
    train_acc = rf_model.score(X_train, y_train)
    val_acc = rf_model.score(X_test, y_test)
    
    brain_data = {
        "model": rf_model, 
        "features": ["Returns", "SMA_10", "SMA_50"], 
        "train_accuracy": train_acc,
        "val_accuracy": val_acc,
        "trained_at": datetime.now().isoformat()
    }
    joblib.dump(brain_data, os.path.join(output_dir, "glu_brain_v1.joblib"))
    
    rich_log = f"RF Training Complete.\\n🎓 Training Acc: {train_acc:.2%}\\n🛡️ Validation Acc: {val_acc:.2%}\\n📊 Target Universe: {len(universe)} symbols\\n🧠 Samples: {len(y_train)}"
    fb.log_event("RETRAINING_RF", rich_log)
    print(f"✅ RF Model updated successfully: Train Acc {train_acc:.3f} | Val Acc {val_acc:.3f}")

run_retrain()
"""

# CNN Logic
cnn_logic = """# 🧠 SECTION 3: CORE LOGIC (Panel Training Pipeline)
def build_cnn_panel_data(universe, seq_len=30, period="5y"):
    all_X, all_y = [], []
    print(f"📉 Fetching {period} of data for {len(universe)} tickers...")
    for ticker in universe:
        df = yf.download(ticker, period=period, progress=False)
        if len(df) > seq_len:
            data = df[['Open', 'High', 'Low', 'Close', 'Volume']].values
            data = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0) + 1e-7)
            for i in range(len(data) - seq_len - 1):
                all_X.append(data[i:i+seq_len])
                y_val = 1 if data[i+seq_len+1, 3] > data[i+seq_len, 3] else 0
                all_y.append(y_val)
    print("✅ Successfully aggregated market sequences.")
    if len(all_X) == 0:
        return None, None
    return np.array(all_X), np.array(all_y)

def train_cnn(X, y):
    print(f"🧠 Training Deep CNN Super Brain on {len(y)} target sequences...")
    model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(64, 3, activation='relu', padding='same', input_shape=(30, 5)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(128, 3, activation='relu', padding='same'),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(2, activation='softmax')
    ])
    
    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(initial_learning_rate=1e-3, decay_steps=10000, decay_rate=0.9)
    optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)
    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    
    # Train robustly to hit > 0.8 accuracy
    history = model.fit(X, y, epochs=30, batch_size=128, validation_split=0.15, verbose=1)
    
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
        
    rich_log = f"CNN Deep Training Complete.\\n🎓 Training Acc: {t_acc:.2%}\\n🛡️ Validation Acc: {v_acc:.2%}\\n📊 Target Universe: {len(universe)} symbols\\n🧠 Sequences: {len(y_all)}\\n🏗️ Output: cnn_daily_t2.tflite"
    fb.log_event("RETRAINING_CNN", rich_log)
    print(f"✅ CNN Model updated successfully: Train Acc {t_acc:.3f} | Val Acc {v_acc:.3f}")

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
        
print("Tuning patched!")
