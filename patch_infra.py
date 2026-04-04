import glob, json

new_infra = [
 "# 🏗️ SECTION 2: INFRASTRUCTURE (Firebase & Secrets)\n",
 "import json, os, firebase_admin, numpy as np, pandas as pd, yfinance as yf\n",
 "from firebase_admin import credentials, db\n",
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
 "                \"url\": user_secrets.get_secret(\"FIREBASE_URL\"),\n",
 "                \"key\": json.loads(user_secrets.get_secret(\"FIREBASE_KEY_JSON\")),\n",
 "                \"telegram\": tg\n",
 "            }\n",
 "        else:\n",
 "            from dotenv import load_dotenv\n",
 "            load_dotenv()\n",
 "            return {\n",
 "                \"url\": os.getenv(\"FIREBASE_URL\"),\n",
 "                \"key\": json.loads(os.getenv(\"FIREBASE_KEY_JSON\", \"{}\")),\n",
 "                \"telegram\": os.getenv(\"TELEGRAM_TOKEN\")\n",
 "            }\n",
 "\n",
 "class FirebaseHandler:\n",
 "    def __init__(self, secrets):\n",
 "        if not firebase_admin._apps:\n",
 "            cred = credentials.Certificate(secrets['key'])\n",
 "            firebase_admin.initialize_app(cred, {'databaseURL': secrets['url']})\n",
 "        self.root_ref = db.reference(\"glu_stock\")\n",
 "        \n",
 "    def get_and_clear_queue(self, queue_name: str):\n",
 "        ref = self.root_ref.child(f\"task_queue/{queue_name}\")\n",
 "        tasks = ref.get()\n",
 "        if not tasks: return []\n",
 "        ref.delete()\n",
 "        return list(tasks.values())\n",
 "        \n",
 "    def push_task(self, queue_name: str, data):\n",
 "        self.root_ref.child(f\"task_queue/{queue_name}\").push(data)\n",
 "        \n",
 "    def insert_trade(self, trade_data):\n",
 "        self.root_ref.child(\"trades\").push(trade_data)\n",
 "        \n",
 "    def get_history(self, limit=5):\n",
 "        return self.root_ref.child(\"history\").order_by_child(\"timestamp\").limit_to_last(limit).get()\n",
 "        \n",
 "    def get_active_trades(self):\n",
 "        trades = self.root_ref.child(\"trades\").get()\n",
 "        if not trades: return []\n",
 "        return [v for v in trades.values() if v.get('status') == 'OPEN']\n",
 "        \n",
 "    def log_event(self, phase, details):\n",
 "        self.root_ref.child(\"history\").push({'timestamp': datetime.now().isoformat(), 'phase': phase.upper(), 'details': details})\n",
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
        # Update pip install
        if cell['cell_type'] == 'code' and any('pip install' in line for line in cell['source']):
            for idx, line in enumerate(cell['source']):
                if 'pip install' in line and 'python-dotenv' not in line:
                    cell['source'][idx] = line.replace('\n', '') + ' python-dotenv\n'
                    modified = True

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
                
                cell['source'] = cell_copy
                modified = True
                
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=1)
        print(f"PATCHED: {f}")
