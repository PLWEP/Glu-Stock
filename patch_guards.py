import json, glob

for f in glob.glob('notebooks/*retraining*.ipynb'):
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    modified = False
    for cell in data['cells']:
        if cell['cell_type'] == 'code':
            src = "".join(cell['source'])
            
            # Patch build_panel_data to check for empty all_X
            if "def build_panel_data(" in src or "def build_cnn_panel_data(" in src:
                lines = cell['source']
                for i, line in enumerate(lines):
                    if "return np.vstack(all_X)" in line or "return np.array(all_X)" in line:
                        if "if not all_X:" not in "".join(lines):
                            indent = line[:line.find("return")]
                            validation = f"{indent}if len(all_X) == 0:\n{indent}    print('❌ ERROR: NO DATA FETCHED! Check your internet connection (DNS issue with Yahoo) or yfinance version.')\n{indent}    return None, None\n"
                            lines.insert(i, validation)
                            modified = True
                            break
                            
            # Patch run_retrain to gracefully exit if X_train is None
            if "def run_retrain():" in src:
                lines = cell['source']
                for i, line in enumerate(lines):
                    if "X_train, y_train =" in line:
                        if "if X_train is None: return" not in "".join(lines):
                            indent = line[:line.find("X_train")]
                            validation = f"{indent}if X_train is None:\n{indent}    print('⚠️ Retraining aborted due to data fetch failure.')\n{indent}    return\n"
                            lines.insert(i+1, validation)
                            modified = True
                            break
                            
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=1)
        print(f"Added guards to {f}")
