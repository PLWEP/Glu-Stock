import json

for nb in ['notebooks/00a_model_retraining_rf.ipynb', 'notebooks/00b_model_retraining_cnn.ipynb']:
    with open(nb, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for cell in data['cells']:
        if cell['cell_type'] == 'code':
            src = "".join(cell['source'])
            if '!pip install' in src:
                # Completely rebuild the pip install line
                packages = ['yfinance', 'firebase-admin', 'pandas', 'scikit-learn', 'joblib', 'python-dotenv', 'ta', 'optuna']
                if 'tensorflow' in src:
                    packages.append('tensorflow')
                cell['source'] = ["!pip install -q " + " ".join(packages)]
                break
    
    with open(nb, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=1)
    print(f"Fixed pip install in {nb}")

# Also fix 02
nb = 'notebooks/02_signal_inference.ipynb'
with open(nb, 'r', encoding='utf-8') as file:
    data = json.load(file)
for cell in data['cells']:
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if '!pip install' in src:
            packages = ['yfinance', 'firebase-admin', 'pandas', 'scikit-learn', 'joblib', 'tensorflow', 'python-dotenv', 'ta']
            cell['source'] = ["!pip install -q " + " ".join(packages)]
            break
with open(nb, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=1)
print(f"Fixed pip install in {nb}")
