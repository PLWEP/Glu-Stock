import json, glob

for f in glob.glob("notebooks/*retraining*.ipynb"):
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    modified = False
    for cell in data['cells']:
        if cell['cell_type'] == 'code':
            src = "".join(cell['source'])
            
            # Inside run_retrain()
            if "def run_retrain():" in src:
                lines = cell['source']
                for i, line in enumerate(lines):
                    if "universe = get_dynamic_lq45()" in line:
                        lines[i] = '    universe = get_full_idx_universe()\n'
                        modified = True
                        
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=1)
        print(f"Patched {f} to train on BROAD Papan Utama universe (250+ stocks)")

