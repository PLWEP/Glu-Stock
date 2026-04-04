import json, glob

idx_script = """
def get_dynamic_lq45():
    print("🌐 Fetching latest LQ45 constituents from alternative sources...")
    fallback = ["ACES.JK", "ADRO.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BMRI.JK", "BRIS.JK", "BRPT.JK", "BUKA.JK", "CPIN.JK", "CTRA.JK", "ESSA.JK", "EXCL.JK", "GGRM.JK", "GOTO.JK", "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK", "INKP.JK", "INTP.JK", "ISAT.JK", "ITMG.JK", "KLBF.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MTEL.JK", "PGAS.JK", "PGEO.JK", "PTBA.JK", "SIDO.JK", "SMGR.JK", "SRTG.JK", "TLKM.JK", "TPIA.JK", "UNTR.JK"]
    try:
        # Instead of Wikipedia, use Stockbit / Investing.com via requests, or reliable fallback
        # For maximum Kaggle resilience without HTTP blocks, we will use a static-updated known list
        # Since Wikipedia is blocked, relying on direct IDX API requires complex Auth tokens.
        # This fallback is practically updated. Let's return it directly if external API fails.
        import urllib.request
        req = urllib.request.Request('https://raw.githubusercontent.com/yofriadi/idn-stock-list/master/lq45.json', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as url:
            data = json.loads(url.read().decode())
            return [f"{t}.JK" for t in data]
    except:
        print("⚠️ External fetch failed. Using highly-curated fallback LQ45 list.")
    return fallback

def get_full_idx_universe():
    print("🌐 Fetching ALL IDX listed companies (900++) from alternative sources...")
    fallback = get_dynamic_lq45() # Fallback to LQ45 if fail
    try:
        import urllib.request
        req = urllib.request.Request('https://raw.githubusercontent.com/yofriadi/idn-stock-list/master/stock-list.json', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as url:
            data = json.loads(url.read().decode())
            tickers = [f"{t['ticker']}.JK" for t in data if 'ticker' in t]
            if tickers:
                print(f"✅ Successfully fetched {len(tickers)} companies.")
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
                    # Strip the original cell logic entirely and replace it with our new logic
                    # To be safe, we just replace the whole cell if it contains the old Wikipedia code
                    if "wikipedia.org" in src:
                        cell['source'] = [idx_script]
                        modified = True
                        
        if modified:
            with open(f, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=1)
            print(f"Patched {f} with Alternative Sources")
