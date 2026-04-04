import glob, json

new_infra = [
 "# 🏗️ SECTION 2: INFRASTRUCTURE (Firebase & Secrets)\n",
 "import json, os, firebase_admin, numpy as np, pandas as pd, yfinance as yf\n",
 "from firebase_admin import credentials, firestore\n",
 "from datetime import datetime\n",
 "\n",
 "try:\n",
 "    from kaggle_secrets import UserSecretsClient\n",
 "    IS_KAGGLE = True\n",
 "except ImportError:\n",
 "    IS_KAGGLE = False\n",
 "\n",
 "class KaggleInfra:\n",
 "    @staticmethod\n",
 "    def load_secrets():\n",
 "        if IS_KAGGLE:\n",
 "            user_secrets = UserSecretsClient()\n",
 "            try: tg = user_secrets.get_secret(\"TELEGRAM_TOKEN\")\n",
 "            except: tg = None\n",
 "            return {\n",
 "                \"key\": json.loads(user_secrets.get_secret(\"FIREBASE_KEY_JSON\")),\n",
 "                \"telegram\": tg\n",
 "            }\n",
 "        else:\n",
 "            from dotenv import load_dotenv\n",
 "            load_dotenv()\n",
 "            return {\n",
 "                \"key\": json.loads(os.getenv(\"FIREBASE_KEY_JSON\", \"{}\")),\n",
 "                \"telegram\": os.getenv(\"TELEGRAM_TOKEN\")\n",
 "            }\n",
 "\n",
 "class FirebaseHandler:\n",
 "    def __init__(self, secrets):\n",
 "        if not firebase_admin._apps:\n",
 "            cred = credentials.Certificate(secrets['key'])\n",
 "            firebase_admin.initialize_app(cred)\n",
 "        self.db = firestore.client()\n",
 "        \n",
 "    def get_and_clear_queue(self, queue_name: str):\n",
 "        docs = self.db.collection(f\"glu_stock_queue_{queue_name}\").get()\n",
 "        tasks = []\n",
 "        for doc in docs:\n",
 "            dt = doc.to_dict()\n",
 "            tasks.append(dt.get('payload', dt))\n",
 "            doc.reference.delete()\n",
 "        return tasks\n",
 "        \n",
 "    def push_task(self, queue_name: str, data):\n",
 "        # Wrap in payload to allow lists\n",
 "        self.db.collection(f\"glu_stock_queue_{queue_name}\").add({'payload': data, 'timestamp': datetime.now().isoformat()})\n",
 "        \n",
 "    def insert_trade(self, trade_data):\n",
 "        self.db.collection(\"glu_stock_trades\").add(trade_data)\n",
 "        \n",
 "    def get_history(self, limit=5):\n",
 "        docs = self.db.collection(\"glu_stock_history\").order_by(\"timestamp\", direction=firestore.Query.DESCENDING).limit(limit).get()\n",
 "        history = [doc.to_dict() for doc in docs]\n",
 "        return {str(i): h for i, h in enumerate(reversed(history))} if history else {}\n",
 "        \n",
 "    def get_active_trades(self):\n",
 "        docs = self.db.collection(\"glu_stock_trades\").where(\"status\", \"==\", \"OPEN\").get()\n",
 "        return [doc.to_dict() for doc in docs]\n",
 "        \n",
 "    def log_event(self, phase, details):\n",
 "        self.db.collection(\"glu_stock_history\").add({'timestamp': datetime.now().isoformat(), 'phase': phase.upper(), 'details': details})\n",
 "\n",
 "def get_dynamic_lq45():\n",
 "    print(\"🌐 Fetching latest LQ45 constituents...\")\n",
 "    fallback = [\"ACES.JK\", \"ADRO.JK\", \"AKRA.JK\", \"AMMN.JK\", \"AMRT.JK\", \"ANTM.JK\", \"ARTO.JK\", \"ASII.JK\", \"BBCA.JK\", \"BBNI.JK\", \"BBRI.JK\", \"BBTN.JK\", \"BMRI.JK\", \"BRIS.JK\", \"BRPT.JK\", \"BUKA.JK\", \"CPIN.JK\", \"CTRA.JK\", \"ESSA.JK\", \"EXCL.JK\", \"GGRM.JK\", \"GOTO.JK\", \"HRUM.JK\", \"ICBP.JK\", \"INCO.JK\", \"INDF.JK\", \"INKP.JK\", \"INTP.JK\", \"ISAT.JK\", \"ITMG.JK\", \"KLBF.JK\", \"MAPI.JK\", \"MBMA.JK\", \"MDKA.JK\", \"MEDC.JK\", \"MTEL.JK\", \"PGAS.JK\", \"PGEO.JK\", \"PTBA.JK\", \"SIDO.JK\", \"SMGR.JK\", \"SRTG.JK\", \"TLKM.JK\", \"TPIA.JK\", \"UNTR.JK\"]\n",
 "    try:\n",
 "        tables = pd.read_html('https://id.wikipedia.org/wiki/LQ45')\n",
 "        for df in tables:\n",
 "            if 'Kode' in df.columns:\n",
 "                return (df['Kode'] + '.JK').tolist()\n",
 "            elif 'Ticker' in df.columns:\n",
 "                return (df['Ticker'] + '.JK').tolist()\n",
 "    except:\n",
 "        pass\n",
 "    return fallback\n"
]

for f in glob.glob("notebooks/*.ipynb"):
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
    modified = False
    for cell in data['cells']:
        if cell['cell_type'] == 'code':
            txt = "".join(cell['source'])
            if "class KaggleInfra:" in txt:
                extra_imports = []
                if "import telebot" in txt:
                    extra_imports.append("import telebot\n")
                if "import tensorflow as tf" in txt:
                    extra_imports.append("import tensorflow as tf\n")
                if "tflite" in txt and "import tensorflow as tf" not in txt:
                    extra_imports.append("try: import tensorflow.lite as tflite\nexcept: import tflite_runtime.interpreter as tflite\n")
                
                cell_copy = list(new_infra)
                for i, item in enumerate(extra_imports):
                    cell_copy.insert(2 + i, item)
                
                # Check for 04_monitor compatibility issue with .items()
                # If doing so, need to ensure history is a dictionary, which I made it so (str(i): h)
                
                cell['source'] = cell_copy
                modified = True
                
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=1)
        print(f"PATCHED FOR FIRESTORE: {f}")
