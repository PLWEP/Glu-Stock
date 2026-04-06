import json

# Define the per-notebook infrastructure cells with their specific needs

# 00A (LightGBM Retraining)
infra_00a = [
    "# [INFO] SECTION 2: INFRASTRUCTURE (Firebase, Secrets & LightGBM)\n",
    "import json, os, firebase_admin, joblib, numpy as np, pandas as pd, yfinance as yf, warnings\n",
    "import lightgbm as lgb\n",
    "from firebase_admin import credentials, firestore\n",
    "from datetime import datetime\n",
    "warnings.filterwarnings('ignore')\n",
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
    "            try:\n",
    "                raw = user_secrets.get_secret(\"FIREBASE_KEY_JSON\")\n",
    "                return {\"key\": json.loads(raw)}\n",
    "            except Exception as e:\n",
    "                print(f\"[ERROR] FIREBASE_KEY_JSON missing or invalid! Error: {e}\")\n",
    "                return {\"key\": None}\n",
    "        else:\n",
    "            from dotenv import load_dotenv\n",
    "            load_dotenv()\n",
    "            raw = os.getenv(\"FIREBASE_KEY_JSON\")\n",
    "            if not raw: return {\"key\": None}\n",
    "            return {\"key\": json.loads(raw)}\n",
    "\n",
    "class FirebaseHandler:\n",
    "    def __init__(self, secrets):\n",
    "        if not firebase_admin._apps:\n",
    "            if not secrets.get('key'):\n",
    "                raise ValueError(\"FIREBASE_KEY_JSON is missing. Check Kaggle Secrets.\")\n",
    "            cred = credentials.Certificate(secrets['key'])\n",
    "            firebase_admin.initialize_app(cred)\n",
    "        self.db = firestore.client()\n",
    "\n",
    "    def push_task(self, queue_name: str, data):\n",
    "        self.db.collection(f\"glu_stock_queue_{queue_name}\").add({'payload': data, 'timestamp': datetime.now().isoformat()})\n",
    "        \n",
    "    def log_event(self, phase, details):\n",
    "        self.db.collection(\"glu_stock_history\").add({'timestamp': datetime.now().isoformat(), 'phase': phase.upper(), 'details': details})\n",
    "\n",
    "def get_full_idx_universe():\n",
    "    fallback = ['AALI.JK', 'ABMM.JK', 'ACES.JK', 'ADHI.JK', 'AISA.JK', 'AKRA.JK', 'AMRT.JK', 'ANTM.JK', 'APLN.JK', 'ARNA.JK', 'ARTO.JK', 'ASGR.JK', 'ASII.JK', 'ASRI.JK', 'ASSA.JK', 'AUTO.JK', 'BACA.JK', 'BALI.JK', 'BAYU.JK', 'BBCA.JK', 'BBHI.JK', 'BBNI.JK', 'BBRI.JK', 'BBTN.JK', 'BBYB.JK', 'BCAP.JK', 'BDMN.JK', 'BEST.JK', 'BFIN.JK', 'BGTG.JK', 'BINA.JK', 'BIRD.JK', 'BISI.JK', 'BJBR.JK', 'BJTM.JK', 'BKSL.JK', 'BMRI.JK', 'BMTR.JK', 'BNGA.JK', 'BNII.JK', 'BNLI.JK', 'BRMS.JK', 'BRPT.JK', 'BSDE.JK', 'BSIM.JK', 'BTPN.JK', 'BUDI.JK', 'BUKK.JK', 'BUMI.JK', 'BVIC.JK', 'BWPT.JK', 'BYAN.JK', 'CASS.JK', 'CFIN.JK', 'CITA.JK', 'CMNP.JK', 'CPIN.JK', 'CTRA.JK', 'DEWA.JK', 'DILD.JK', 'DLTA.JK', 'DMAS.JK', 'DNET.JK', 'DOID.JK', 'DSNG.JK', 'DSSA.JK', 'ELSA.JK', 'EMTK.JK', 'ENRG.JK', 'ERAA.JK', 'ESSA.JK', 'EXCL.JK', 'GEMS.JK', 'GGRM.JK', 'GJTL.JK', 'GWSA.JK', 'HEXA.JK', 'HMSP.JK', 'HRUM.JK', 'ICBP.JK', 'IMAS.JK', 'IMPC.JK', 'INCO.JK', 'INDF.JK', 'INDY.JK', 'INKP.JK', 'INPC.JK', 'INTP.JK', 'ISAT.JK', 'ISSP.JK', 'ITMG.JK', 'JKON.JK', 'JPFA.JK', 'JRPT.JK', 'JSMR.JK', 'JTPE.JK', 'KBLI.JK', 'KIJA.JK', 'KKGI.JK', 'KLBF.JK', 'KPIG.JK', 'LPKR.JK', 'LPPF.JK', 'LSIP.JK', 'LTLS.JK', 'MAIN.JK', 'MAPI.JK', 'MAYA.JK', 'MBSS.JK', 'MCOR.JK', 'MDKA.JK', 'MEDC.JK', 'MEGA.JK', 'MIDI.JK', 'MIKA.JK', 'MLBI.JK', 'MLIA.JK', 'MLPL.JK', 'MMLP.JK', 'MNCN.JK', 'MPMX.JK', 'MREI.JK', 'MTDL.JK', 'MTLA.JK', 'MYOR.JK', 'NISP.JK', 'PANR.JK', 'PANS.JK', 'PGAS.JK', 'PNBN.JK', 'PNIN.JK', 'PNLF.JK', 'PTBA.JK', 'PTPP.JK', 'PTRO.JK', 'PWON.JK', 'RAJA.JK', 'RALS.JK', 'SAME.JK', 'SCMA.JK', 'SGRO.JK', 'SIDO.JK', 'SILO.JK', 'SIMP.JK', 'SMAR.JK', 'SMBR.JK', 'SMDR.JK', 'SMGR.JK', 'SMMA.JK', 'SMRA.JK', 'SMSM.JK', 'SRTG.JK', 'SSIA.JK', 'SSMS.JK', 'TBIG.JK', 'TBLA.JK', 'TINS.JK', 'TKIM.JK', 'TLKM.JK', 'TMAS.JK', 'TOBA.JK', 'TOTL.JK', 'TOWR.JK', 'TPMA.JK', 'TRIM.JK', 'TSPC.JK', 'ULTJ.JK', 'UNIC.JK', 'UNTR.JK', 'UNVR.JK', 'VICO.JK', 'WIIM.JK', 'WINS.JK', 'WTON.JK', 'SHIP.JK', 'POWR.JK', 'PRDA.JK', 'BRIS.JK', 'CARS.JK', 'CLEO.JK', 'WOOD.JK', 'HRTA.JK', 'MARK.JK', 'MCAS.JK', 'PSSI.JK', 'MORA.JK', 'PBID.JK', 'IPCM.JK', 'BTPS.JK', 'SPTO.JK', 'HEAL.JK', 'TUGU.JK', 'MSIN.JK', 'MAPA.JK', 'IPCC.JK', 'FILM.JK', 'PANI.JK', 'GOOD.JK', 'SKRN.JK', 'BOLA.JK', 'KOTA.JK', 'KEEN.JK', 'TEBE.JK', 'KEJU.JK', 'PSGO.JK', 'UCID.JK', 'CSRA.JK', 'SAMF.JK', 'SGER.JK', 'PNGO.JK', 'BBSI.JK', 'VICI.JK', 'WMUU.JK', 'UNIQ.JK', 'TAPG.JK', 'BMHS.JK', 'MCOL.JK', 'GTSI.JK', 'MTEL.JK', 'CMRY.JK', 'RMKE.JK', 'AVIA.JK', 'DRMA.JK', 'ADMR.JK', 'STAA.JK', 'MTMH.JK', 'TRGU.JK', 'HATM.JK', 'JARR.JK', 'ELPI.JK', 'MKTR.JK', 'OMED.JK', 'SUNI.JK', 'PGEO.JK', 'BDKR.JK', 'CUAN.JK', 'SMIL.JK', 'AMMN.JK', 'MAHA.JK', 'ERAL.JK', 'BREN.JK', 'MSTI.JK', 'ALII.JK', 'GOLF.JK', 'DAAZ.JK', 'AADI.JK', 'MDIY.JK', 'DGWG.JK', 'CBDK.JK', 'MINE.JK', 'PSAT.JK', 'BLOG.JK', 'YUPI.JK', 'MDLA.JK', 'NCKL.JK', 'MBMA.JK', 'RAAM.JK', 'ADRO.JK', 'AGRO.JK']\n",
    "    return fallback\n"
]

# 00B (CNN Retraining)
infra_00b = [
    "# [INFO] SECTION 2: INFRASTRUCTURE (Firebase, Secrets & TensorFlow)\n",
    "import json, os, firebase_admin, joblib, numpy as np, pandas as pd, yfinance as yf, warnings\n",
    "import tensorflow as tf\n",
    "from firebase_admin import credentials, firestore\n",
    "from datetime import datetime\n",
    "warnings.filterwarnings('ignore')\n",
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
    "            try:\n",
    "                raw = user_secrets.get_secret(\"FIREBASE_KEY_JSON\")\n",
    "                return {\"key\": json.loads(raw)}\n",
    "            except Exception as e:\n",
    "                print(f\"[ERROR] FIREBASE_KEY_JSON missing or invalid! Error: {e}\")\n",
    "                return {\"key\": None}\n",
    "        else:\n",
    "            from dotenv import load_dotenv\n",
    "            load_dotenv()\n",
    "            raw = os.getenv(\"FIREBASE_KEY_JSON\")\n",
    "            if not raw: return {\"key\": None}\n",
    "            return {\"key\": json.loads(raw)}\n",
    "\n",
    "class FirebaseHandler:\n",
    "    def __init__(self, secrets):\n",
    "        if not firebase_admin._apps:\n",
    "            if not secrets.get('key'):\n",
    "                raise ValueError(\"FIREBASE_KEY_JSON is missing. Check Kaggle Secrets.\")\n",
    "            cred = credentials.Certificate(secrets['key'])\n",
    "            firebase_admin.initialize_app(cred)\n",
    "        self.db = firestore.client()\n",
    "\n",
    "    def push_task(self, queue_name: str, data):\n",
    "        self.db.collection(f\"glu_stock_queue_{queue_name}\").add({'payload': data, 'timestamp': datetime.now().isoformat()})\n",
    "        \n",
    "    def log_event(self, phase, details):\n",
    "        self.db.collection(\"glu_stock_history\").add({'timestamp': datetime.now().isoformat(), 'phase': phase.upper(), 'details': details})\n",
    "\n",
    "def get_full_idx_universe():\n",
    "    fallback = ['AALI.JK', 'ABMM.JK', 'ACES.JK', 'ADHI.JK', 'AISA.JK', 'AKRA.JK', 'AMRT.JK', 'ANTM.JK', 'APLN.JK', 'ARNA.JK', 'ARTO.JK', 'ASGR.JK', 'ASII.JK', 'ASRI.JK', 'ASSA.JK', 'AUTO.JK', 'BACA.JK', 'BALI.JK', 'BAYU.JK', 'BBCA.JK', 'BBHI.JK', 'BBNI.JK', 'BBRI.JK', 'BBTN.JK', 'BBYB.JK', 'BCAP.JK', 'BDMN.JK', 'BEST.JK', 'BFIN.JK', 'BGTG.JK', 'BINA.JK', 'BIRD.JK', 'BISI.JK', 'BJBR.JK', 'BJTM.JK', 'BKSL.JK', 'BMRI.JK', 'BMTR.JK', 'BNGA.JK', 'BNII.JK', 'BNLI.JK', 'BRMS.JK', 'BRPT.JK', 'BSDE.JK', 'BSIM.JK', 'BTPN.JK', 'BUDI.JK', 'BUKK.JK', 'BUMI.JK', 'BVIC.JK', 'BWPT.JK', 'BYAN.JK', 'CASS.JK', 'CFIN.JK', 'CITA.JK', 'CMNP.JK', 'CPIN.JK', 'CTRA.JK', 'DEWA.JK', 'DILD.JK', 'DLTA.JK', 'DMAS.JK', 'DNET.JK', 'DOID.JK', 'DSNG.JK', 'DSSA.JK', 'ELSA.JK', 'EMTK.JK', 'ENRG.JK', 'ERAA.JK', 'ESSA.JK', 'EXCL.JK', 'GEMS.JK', 'GGRM.JK', 'GJTL.JK', 'GWSA.JK', 'HEXA.JK', 'HMSP.JK', 'HRUM.JK', 'ICBP.JK', 'IMAS.JK', 'IMPC.JK', 'INCO.JK', 'INDF.JK', 'INDY.JK', 'INKP.JK', 'INPC.JK', 'INTP.JK', 'ISAT.JK', 'ISSP.JK', 'ITMG.JK', 'JKON.JK', 'JPFA.JK', 'JRPT.JK', 'JSMR.JK', 'JTPE.JK', 'KBLI.JK', 'KIJA.JK', 'KKGI.JK', 'KLBF.JK', 'KPIG.JK', 'LPKR.JK', 'LPPF.JK', 'LSIP.JK', 'LTLS.JK', 'MAIN.JK', 'MAPI.JK', 'MAYA.JK', 'MBSS.JK', 'MCOR.JK', 'MDKA.JK', 'MEDC.JK', 'MEGA.JK', 'MIDI.JK', 'MIKA.JK', 'MLBI.JK', 'MLIA.JK', 'MLPL.JK', 'MMLP.JK', 'MNCN.JK', 'MPMX.JK', 'MREI.JK', 'MTDL.JK', 'MTLA.JK', 'MYOR.JK', 'NISP.JK', 'PANR.JK', 'PANS.JK', 'PGAS.JK', 'PNBN.JK', 'PNIN.JK', 'PNLF.JK', 'PTBA.JK', 'PTPP.JK', 'PTRO.JK', 'PWON.JK', 'RAJA.JK', 'RALS.JK', 'SAME.JK', 'SCMA.JK', 'SGRO.JK', 'SIDO.JK', 'SILO.JK', 'SIMP.JK', 'SMAR.JK', 'SMBR.JK', 'SMDR.JK', 'SMGR.JK', 'SMMA.JK', 'SMRA.JK', 'SMSM.JK', 'SRTG.JK', 'SSIA.JK', 'SSMS.JK', 'TBIG.JK', 'TBLA.JK', 'TINS.JK', 'TKIM.JK', 'TLKM.JK', 'TMAS.JK', 'TOBA.JK', 'TOTL.JK', 'TOWR.JK', 'TPMA.JK', 'TRIM.JK', 'TSPC.JK', 'ULTJ.JK', 'UNIC.JK', 'UNTR.JK', 'UNVR.JK', 'VICO.JK', 'WIIM.JK', 'WINS.JK', 'WTON.JK', 'SHIP.JK', 'POWR.JK', 'PRDA.JK', 'BRIS.JK', 'CARS.JK', 'CLEO.JK', 'WOOD.JK', 'HRTA.JK', 'MARK.JK', 'MCAS.JK', 'PSSI.JK', 'MORA.JK', 'PBID.JK', 'IPCCM.JK', 'BTPS.JK', 'SPTO.JK', 'HEAL.JK', 'TUGU.JK', 'MSIN.JK', 'MAPA.JK', 'IPCC.JK', 'FILM.JK', 'PANI.JK', 'GOOD.JK', 'SKRN.JK', 'BOLA.JK', 'KOTA.JK', 'KEEN.JK', 'TEBE.JK', 'KEJU.JK', 'PSGO.JK', 'UCID.JK', 'CSRA.JK', 'SAMF.JK', 'SGER.JK', 'PNGO.JK', 'BBSI.JK', 'VICI.JK', 'WMUU.JK', 'UNIQ.JK', 'TAPG.JK', 'BMHS.JK', 'MCOL.JK', 'GTSI.JK', 'MTEL.JK', 'CMRY.JK', 'RMKE.JK', 'AVIA.JK', 'DRMA.JK', 'ADMR.JK', 'STAA.JK', 'MTMH.JK', 'TRGU.JK', 'HATM.JK', 'JARR.JK', 'ELPI.JK', 'MKTR.JK', 'OMED.JK', 'SUNI.JK', 'PGEO.JK', 'BDKR.JK', 'CUAN.JK', 'SMIL.JK', 'AMMN.JK', 'MAHA.JK', 'ERAL.JK', 'BREN.JK', 'MSTI.JK', 'ALII.JK', 'GOLF.JK', 'DAAZ.JK', 'AADI.JK', 'MDIY.JK', 'DGWG.JK', 'CBDK.JK', 'MINE.JK', 'PSAT.JK', 'BLOG.JK', 'YUPI.JK', 'MDLA.JK', 'NCKL.JK', 'MBMA.JK', 'RAAM.JK', 'ADRO.JK', 'AGRO.JK']\n",
    "    return fallback\n"
]

# Define maps
mapping = {
    'notebooks/00a_model_retraining_rf.ipynb': infra_00a,
    'notebooks/00b_model_retraining_cnn.ipynb': infra_00b
}

for nb, content in mapping.items():
    with open(nb, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for cell in data['cells']:
        if cell['cell_type'] == 'code':
            s = "".join(cell['source'])
            if \"SECTION 2\" in s or \"INFRASTRUCTURE\" in s:
                cell['source'] = content
                break
    with open(nb, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1)
    print(f\"Re-fixed {nb} with specific library imports.\")
