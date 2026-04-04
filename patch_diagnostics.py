import json, glob

complete_infra = """# 🏗️ SECTION 2: INFRASTRUCTURE (Firebase, Secrets & Web Fetchers)
import json, os, firebase_admin, joblib, numpy as np, pandas as pd, yfinance as yf
from firebase_admin import credentials, firestore
from datetime import datetime

try:
    from kaggle_secrets import UserSecretsClient
    IS_KAGGLE = True
except ImportError:
    IS_KAGGLE = False

class KaggleInfra:
    @staticmethod
    def load_secrets():
        if IS_KAGGLE:
            user_secrets = UserSecretsClient()
            try: tg = user_secrets.get_secret("TELEGRAM_TOKEN")
            except: tg = None
            return {
                "key": json.loads(user_secrets.get_secret("FIREBASE_KEY_JSON")),
                "telegram": tg
            }
        else:
            from dotenv import load_dotenv
            load_dotenv()
            return {
                "key": json.loads(os.getenv("FIREBASE_KEY_JSON", "{}")),
                "telegram": os.getenv("TELEGRAM_TOKEN")
            }

class FirebaseHandler:
    def __init__(self, secrets):
        if not firebase_admin._apps:
            cred = credentials.Certificate(secrets['key'])
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        
    def get_and_clear_queue(self, queue_name: str):
        docs = self.db.collection(f"glu_stock_queue_{queue_name}").get()
        tasks = []
        for doc in docs:
            dt = doc.to_dict()
            tasks.append(dt.get('payload', dt))
            doc.reference.delete()
        return tasks
        
    def push_task(self, queue_name: str, data):
        self.db.collection(f"glu_stock_queue_{queue_name}").add({'payload': data, 'timestamp': datetime.now().isoformat()})
        
    def insert_trade(self, trade_data):
        self.db.collection("glu_stock_trades").add(trade_data)
        
    def get_history(self, limit=5):
        docs = self.db.collection("glu_stock_history").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).get()
        history = [doc.to_dict() for doc in docs]
        return {str(i): h for i, h in enumerate(reversed(history))} if history else {}
        
    def get_active_trades(self):
        docs = self.db.collection("glu_stock_trades").where("status", "==", "OPEN").get()
        return [doc.to_dict() for doc in docs]
        
    def log_event(self, phase, details):
        self.db.collection("glu_stock_history").add({'timestamp': datetime.now().isoformat(), 'phase': phase.upper(), 'details': details})

def get_dynamic_lq45():
    print("🌐 Fetching latest LQ45 constituents...")
    fallback = ["ACES.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK", "BRPT.JK", "BUKA.JK", "CPIN.JK", "CTRA.JK", "ESSA.JK", "EXCL.JK", "GGRM.JK", "GOTO.JK", "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK", "INTP.JK", "ISAT.JK", "ITMG.JK", "KLBF.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MTEL.JK", "PGAS.JK", "PGEO.JK", "PTBA.JK", "SIDO.JK", "SMGR.JK", "SRTG.JK", "TLKM.JK", "TPIA.JK", "UNTR.JK"]
    try:
        import urllib.request
        req = urllib.request.Request('https://raw.githubusercontent.com/yofriadi/idn-stock-list/master/lq45.json', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as url:
            data = json.loads(url.read().decode())
            return [f"{t}.JK" for t in data]
    except Exception as e:
        print(f"⚠️ Github LQ45 fetch failed: {e}. Using highly-curated fallback LQ45 list.")
    return fallback

def get_full_idx_universe():
    print("🌐 Fetching ALL IDX listed companies from Official IDX API...")
    fallback = get_dynamic_lq45() 
    
    # 1. Try Official IDX API
    try:
        import urllib.request
        # We add robust headers to prevent 403 Forbidden errors
        hdrs = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.idx.co.id/'
        }
        req = urllib.request.Request('https://www.idx.co.id/primary/StockData/GetSecuritiesStock?length=9999', headers=hdrs)
        with urllib.request.urlopen(req, timeout=10) as url:
            data = json.loads(url.read().decode())
            if 'data' in data:
                tickers = [f"{t['Code']}.JK" for t in data['data'] if 'Code' in t]
                if tickers:
                    print(f"✅ Successfully fetched {len(tickers)} companies from IDX Official API.")
                    return list(set(tickers)) 
    except Exception as e:
        print(f"⚠️ Official IDX API failed: {e}. Trying Github Proxy...")
        
    # 2. Try Github Alternative
    try:
        import urllib.request
        req = urllib.request.Request('https://raw.githubusercontent.com/yofriadi/idn-stock-list/master/stock-list.json', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as url:
            data = json.loads(url.read().decode())
            tickers = [f"{t['ticker']}.JK" for t in data if 'ticker' in t]
            if tickers:
                print(f"✅ Successfully fetched {len(tickers)} companies from Github proxy.")
                return list(set(tickers))
    except Exception as e:
        print(f"⚠️ Full fetch failed: {e}. Falling back to LQ45.")
        
    return fallback
"""

for f in glob.glob("notebooks/*.ipynb"):
    if "00a" in f or "00b" in f or "01_" in f:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        modified = False
        for cell in data['cells']:
            if cell['cell_type'] == 'code':
                src = "".join(cell['source'])
                if "def get_dynamic_lq45():" in src:
                    cell_source = complete_infra
                    if "00b" in f:
                        cell_source = cell_source.replace("import numpy as np", "import numpy as np\\ntry:\\n    import tflite_runtime.interpreter as tflite\\nexcept ImportError:\\n    import tensorflow.lite as tflite")
                        
                    cell['source'] = [line + '\\n' for line in cell_source.split('\\n')]
                    modified = True
                    break
                        
        if modified:
            with open(f, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=1)
            print(f"INJECTED VERBOSE DIAGNOSTICS INTO: {f}")
