import json

f = 'notebooks/00b_model_retraining_cnn.ipynb'
with open(f, 'r', encoding='utf-8') as file:
    data = json.load(file)

# ════════════════════════════════════════════════════════
# SECTION 3: CNN Meta-Labeling Core Logic
# ════════════════════════════════════════════════════════
section3 = [
    "# \U0001f9e0 SECTION 3: CORE LOGIC (CNN-LSTM Meta-Labeling Pipeline)\n",
    "import optuna\n",
    "optuna.logging.set_verbosity(optuna.logging.WARNING)\n",
    "\n",
    "def build_cnn_panel_data(universe, seq_len=30, period='5y'):\n",
    "    all_X, all_y = [], []\n",
    "    print(f'\U0001f4c9 Fetching {period} of data for {len(universe)} tickers...')\n",
    "    for ticker in universe:\n",
    "        try:\n",
    "            df = yf.download(ticker, period=period, progress=False)\n",
    "            if len(df) < seq_len + 10:\n",
    "                continue\n",
    "            close = df['Close'].squeeze()\n",
    "            high = df['High'].squeeze()\n",
    "            low = df['Low'].squeeze()\n",
    "            volume = df['Volume'].squeeze()\n",
    "            # ATR as 6th channel\n",
    "            import ta\n",
    "            atr = ta.volatility.AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()\n",
    "            raw = np.column_stack([df['Open'].squeeze().values, high.values, low.values, close.values, volume.values, atr.values])\n",
    "            # Drop NaN rows from ATR warmup\n",
    "            valid_start = np.argmax(~np.isnan(raw).any(axis=1))\n",
    "            raw = raw[valid_start:]\n",
    "            close_vals = close.values[valid_start:]\n",
    "            for i in range(len(raw) - seq_len - 1):\n",
    "                seq = raw[i:i+seq_len]\n",
    "                seq_min = seq.min(axis=0)\n",
    "                seq_max = seq.max(axis=0)\n",
    "                norm_seq = (seq - seq_min) / (seq_max - seq_min + 1e-7)\n",
    "                all_X.append(norm_seq)\n",
    "                y_val = 1 if close_vals[i+seq_len+1] > close_vals[i+seq_len] else 0\n",
    "                all_y.append(y_val)\n",
    "        except Exception:\n",
    "            continue\n",
    "    print('\u2705 Successfully aggregated market sequences.')\n",
    "    if len(all_X) == 0:\n",
    "        return None, None\n",
    "    return np.array(all_X), np.array(all_y)\n",
    "\n",
    "def build_meta_labels(y_true, rf_meta_path='/kaggle/working/rf_oos_meta.json'):\n",
    "    \"\"\"Load RF OOS predictions and create meta-labels (1=RF was correct, 0=RF was wrong)\"\"\"\n",
    "    try:\n",
    "        import json as _json\n",
    "        with open(rf_meta_path) as mf:\n",
    "            meta = _json.load(mf)\n",
    "        print(f'\u2705 Loaded RF meta-labels: {len(meta[\"oos_correct\"])} OOS predictions (RF Val Acc: {meta[\"val_acc\"]:.2%})')\n",
    "        return np.array(meta['oos_correct']), True\n",
    "    except FileNotFoundError:\n",
    "        print('\u26a0\ufe0f RF meta-labels not found. Training in standalone mode (standard labels).')\n",
    "        return y_true, False\n",
    "\n",
    "def train_cnn(X, y, conv1=64, conv2=128, lstm_units=64, dropout=0.4, lr=1e-3, epochs=40, batch_size=128):\n",
    "    print(f'\U0001f9e0 Training Deep L-CNN Meta Brain on {len(y)} sequences...')\n",
    "    n_features = X.shape[2]\n",
    "    seq_len = X.shape[1]\n",
    "    model = tf.keras.Sequential([\n",
    "        tf.keras.layers.Conv1D(conv1, 3, activation='relu', padding='same', input_shape=(seq_len, n_features)),\n",
    "        tf.keras.layers.BatchNormalization(),\n",
    "        tf.keras.layers.MaxPooling1D(2),\n",
    "        tf.keras.layers.Conv1D(conv2, 3, activation='relu', padding='same'),\n",
    "        tf.keras.layers.BatchNormalization(),\n",
    "        tf.keras.layers.LSTM(lstm_units, return_sequences=False),\n",
    "        tf.keras.layers.Dense(64, activation='relu'),\n",
    "        tf.keras.layers.Dropout(dropout),\n",
    "        tf.keras.layers.Dense(2, activation='softmax')\n",
    "    ])\n",
    "    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(initial_learning_rate=lr, decay_steps=10000, decay_rate=0.9)\n",
    "    optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)\n",
    "    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])\n",
    "    split_idx = int(len(X) * 0.85)\n",
    "    X_tr, X_te = X[:split_idx], X[split_idx:]\n",
    "    y_tr, y_te = y[:split_idx], y[split_idx:]\n",
    "    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True)\n",
    "    history = model.fit(X_tr, y_tr, epochs=epochs, batch_size=batch_size, validation_data=(X_te, y_te), callbacks=[early_stop], verbose=1)\n",
    "    t_acc = max(history.history['accuracy'])\n",
    "    v_acc = max(history.history['val_accuracy'])\n",
    "    return model, t_acc, v_acc\n",
    "\n",
    "def optimize_cnn(X, y, n_trials=20):\n",
    "    print(f'\U0001f50d Running Optuna HPO for CNN ({n_trials} trials)...')\n",
    "    def objective(trial):\n",
    "        params = {\n",
    "            'conv1': trial.suggest_categorical('conv1', [32, 64, 128]),\n",
    "            'conv2': trial.suggest_categorical('conv2', [64, 128, 256]),\n",
    "            'lstm_units': trial.suggest_categorical('lstm_units', [32, 64, 128]),\n",
    "            'dropout': trial.suggest_float('dropout', 0.2, 0.5),\n",
    "            'lr': trial.suggest_float('lr', 1e-4, 1e-2, log=True),\n",
    "            'batch_size': trial.suggest_categorical('batch_size', [64, 128, 256]),\n",
    "        }\n",
    "        _, _, v_acc = train_cnn(X, y, epochs=10, **params)\n",
    "        return v_acc\n",
    "    study = optuna.create_study(direction='maximize')\n",
    "    study.optimize(objective, n_trials=n_trials, timeout=1500)\n",
    "    print(f'\u2705 Optuna Best Val Acc: {study.best_value:.4f}')\n",
    "    print(f'\u2705 Best Params: {study.best_params}')\n",
    "    return study.best_params, study.best_value\n",
]

# ════════════════════════════════════════════════════════
# SECTION 4: MAIN EXECUTION — Meta-Labeling Pipeline
# ════════════════════════════════════════════════════════
section4 = [
    "# \U0001f680 SECTION 4: MAIN EXECUTION\n",
    "def run_retrain():\n",
    "    secrets = KaggleInfra.load_secrets()\n",
    "    fb = FirebaseHandler(secrets)\n",
    "    output_dir = '/kaggle/working/'\n",
    "    \n",
    "    universe = get_full_idx_universe()\n",
    "    \n",
    "    # 1. Build 6-Channel Panel Data (OHLCV + ATR)\n",
    "    X_all, y_all = build_cnn_panel_data(universe)\n",
    "    if X_all is None:\n",
    "        print('\u26a0\ufe0f Retraining aborted due to data fetch failure.')\n",
    "        return\n",
    "    \n",
    "    # 2. Try Meta-Labeling (load RF OOS predictions)\n",
    "    meta_labels, is_meta = build_meta_labels(y_all)\n",
    "    # If meta available, use only the last N samples matching meta size\n",
    "    if is_meta and len(meta_labels) < len(y_all):\n",
    "        X_meta = X_all[-len(meta_labels):]\n",
    "        y_meta = meta_labels\n",
    "    else:\n",
    "        X_meta = X_all\n",
    "        y_meta = y_all if not is_meta else meta_labels\n",
    "    \n",
    "    # 3. Optuna HPO\n",
    "    best_params, best_cv = optimize_cnn(X_meta, y_meta, n_trials=20)\n",
    "    \n",
    "    # 4. Final Training with Best Params\n",
    "    safe_params = {k: v for k, v in best_params.items() if k in ['conv1','conv2','lstm_units','dropout','lr','batch_size']}\n",
    "    cnn_model, t_acc, v_acc = train_cnn(X_meta, y_meta, epochs=40, **safe_params)\n",
    "    \n",
    "    # 5. TFLite Export\n",
    "    print('\u2699\ufe0f Converting to TFLite...')\n",
    "    converter = tf.lite.TFLiteConverter.from_keras_model(cnn_model)\n",
    "    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]\n",
    "    converter._experimental_lower_tensor_list_ops = False\n",
    "    tflite_model = converter.convert()\n",
    "    with open(os.path.join(output_dir, 'cnn_daily_t2.tflite'), 'wb') as f:\n",
    "        f.write(tflite_model)\n",
    "    \n",
    "    # 6. Rich Firebase Telemetry\n",
    "    mode_str = 'Meta-Labeling' if is_meta else 'Standalone'\n",
    "    log_lines = [\n",
    "        f'L-CNN Deep Training Complete ({mode_str} Mode).',\n",
    "        f'\U0001f393 Training Acc: {t_acc:.2%}',\n",
    "        f'\U0001f6e1\ufe0f OOS Validation Acc: {v_acc:.2%}',\n",
    "        f'\U0001f50d Optuna Best CV: {best_cv:.2%}',\n",
    "        f'\U0001f4ca Universe: {len(universe)} symbols | Sequences: {len(y_meta)}',\n",
    "        f'\U0001f3af Input Shape: {X_meta.shape}',\n",
    "        f'\U0001f9e0 Best Params: {best_params}',\n",
    "    ]\n",
    "    fb.log_event('RETRAINING_CNN', chr(10).join(log_lines))\n",
    "    for line in log_lines:\n",
    "        print(line)\n",
    "\n",
    "run_retrain()\n",
]

# ── Also update pip install cell ──
for cell in data['cells']:
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if '!pip install' in src:
            if 'optuna' not in src:
                new_src = src.rstrip()
                if 'ta' not in new_src:
                    new_src += ' ta'
                new_src += ' optuna'
                cell['source'] = [new_src]

# ── Inject into correct cells ──
for cell in data['cells']:
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if "def build_cnn_panel_data" in src:
            cell['source'] = section3
        elif "def run_retrain" in src:
            cell['source'] = section4

with open(f, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=1)
print("00B FULLY PATCHED WITH PHASE 18 META-LABELING!")
