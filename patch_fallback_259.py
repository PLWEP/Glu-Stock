import json, glob

tickers = json.load(open('tickers.json'))
jk_tickers = [f"{t}.JK" for t in tickers]

fallback_str = '    fallback = ' + str(jk_tickers) + '\n    print(f"⚠️ External fetches failed. Using MASSIVE hardcoded fallback ({len(fallback)} Papan Utama tickers).")\n'

for f in glob.glob("notebooks/*.ipynb"):
    if "00a" in f or "00b" in f or "01_" in f:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        modified = False
        for cell in data['cells']:
            if cell['cell_type'] == 'code':
                src = "".join(cell['source'])
                if "def get_full_idx_universe():" in src:
                    lines = cell['source']
                    for i, line in enumerate(lines):
                        if 'fallback = get_dynamic_lq45()' in line:
                            lines[i] = fallback_str
                            modified = True
                            break
                        
        if modified:
            with open(f, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=1)
            print(f"Patched 259 Hardcode Fallback in {f}")

