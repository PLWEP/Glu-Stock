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
            # Squeeze to 1D Series to prevent Dimension Errors from yfinance tuple columns
            close_series = df['Close'].squeeze()
            
            # 1. Price Action
            df['Returns'] = close_series.pct_change()
            
            # 2. Momentum (RSI)
            df['RSI'] = ta.momentum.RSIIndicator(close=close_series, window=14).rsi()
            
            # 3. Trend (MACD)
            macd = ta.trend.MACD(close=close_series)
            df['MACD'] = macd.macd_diff()
            
            # 4. Volatility (Bollinger Bands)
            bollinger = ta.volatility.BollingerBands(close=close_series, window=20, window_dev=2)
            df['BB_High'] = bollinger.bollinger_hband_indicator()
            df['BB_Low'] = bollinger.bollinger_lband_indicator()
            
            df = df.dropna()
            
            # Use iloc internally for strict array selection
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

f = 'notebooks/00a_model_retraining_rf.ipynb'
with open(f, 'r', encoding='utf-8') as file:
    data = json.load(file)

modified = False
for cell in data['cells']:    
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if "def build_panel_data" in src and "import ta" in src:
            lines = [line + '\n' for line in rf_logic.split('\n')]
            lines[-1] = lines[-1].strip()
            cell['source'] = lines
            modified = True
            break
            
if modified:
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=1)
    print("FIXED VALUE ERROR IN 00A!")
