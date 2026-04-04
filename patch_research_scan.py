import json

f = 'notebooks/01_research_scan.ipynb'
try:
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
except FileNotFoundError:
    print(f"File {f} not found.")
    exit(1)

modified = False
extra_func = """
def get_full_idx_universe():
    print("🌐 Scraping ALL IDX listed companies (900++)...")
    fallback = get_dynamic_lq45() # Fallback to LQ45 if fail
    try:
        tables = pd.read_html('https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_Indonesia_Stock_Exchange')
        df = tables[0]
        for col in df.columns:
            if 'Symbol' in col or 'Ticker' in col or 'Code' in col:
                tickers = (df[col] + '.JK').tolist()
                print(f"✅ Successfully scraped {len(tickers)} companies.")
                return tickers
    except Exception as e:
        print("⚠️ Full scrape failed. Falling back to LQ45.")
    return fallback
"""

for cell in data['cells']:
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        
        # Inject the function
        if "def get_dynamic_lq45():" in src and "def get_full_idx_universe():" not in src:
            # We add it at the end of this cell
            cell['source'].append(extra_func)
            modified = True
            
        # Update the main execution
        if 'universe = ["BBCA.JK"' in src:
            lines = cell['source']
            for i, line in enumerate(lines):
                if 'universe = ["BBCA.JK"' in line:
                    lines[i] = '    universe = get_full_idx_universe()\n'
                    modified = True
                    break

if modified:
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=1)
    print("Successfully patched 01_research_scan.ipynb")
else:
    print("No changes made. Might already be patched.")
