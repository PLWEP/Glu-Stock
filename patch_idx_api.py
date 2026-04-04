import json, glob

new_logic = """
def get_dynamic_lq45():
    print("🌐 Fetching latest LQ45 constituents...")
    fallback = ["ACES.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK", "BRPT.JK", "BUKA.JK", "CPIN.JK", "CTRA.JK", "ESSA.JK", "EXCL.JK", "GGRM.JK", "GOTO.JK", "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK", "INTP.JK", "ISAT.JK", "ITMG.JK", "KLBF.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MTEL.JK", "PGAS.JK", "PGEO.JK", "PTBA.JK", "SIDO.JK", "SMGR.JK", "SRTG.JK", "TLKM.JK", "TPIA.JK", "UNTR.JK"]
    try:
        import urllib.request
        req = urllib.request.Request('https://raw.githubusercontent.com/yofriadi/idn-stock-list/master/lq45.json', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as url:
            data = json.loads(url.read().decode())
            return [f"{t}.JK" for t in data]
    except:
        print("⚠️ External fetch failed. Using highly-curated fallback LQ45 list.")
    return fallback

def get_full_idx_universe():
    print("🌐 Fetching ALL IDX listed companies from Official IDX API...")
    fallback = get_dynamic_lq45() # Fallback to LQ45 if fail
    
    # 1. Try Official IDX API (Hit Network)
    try:
        import urllib.request
        # Appending length=9999 handles pagination if the API enforces it
        req = urllib.request.Request('https://www.idx.co.id/primary/StockData/GetSecuritiesStock?length=9999', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as url:
            data = json.loads(url.read().decode())
            if 'data' in data:
                tickers = [f"{t['Code']}.JK" for t in data['data'] if 'Code' in t]
                if tickers:
                    print(f"✅ Successfully fetched {len(tickers)} companies from IDX Official API.")
                    return list(set(tickers)) # Unique check
    except Exception as e:
        print(f"⚠️ Official IDX API failed. Trying Github Proxy...")
        
    # 2. Try Github Alternative
    try:
        import urllib.request
        req = urllib.request.Request('https://raw.githubusercontent.com/yofriadi/idn-stock-list/master/stock-list.json', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as url:
            data = json.loads(url.read().decode())
            tickers = [f"{t['ticker']}.JK" for t in data if 'ticker' in t]
            if tickers:
                print(f"✅ Successfully fetched {len(tickers)} companies from Github proxy.")
                return tickers
    except Exception as e:
        print("⚠️ Full fetch failed. Falling back to LQ45.")
        
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
                    cell['source'] = [new_logic]
                    modified = True
                    break
                        
        if modified:
            with open(f, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=1)
            print(f"Patched {f} with Official IDX API logic")

