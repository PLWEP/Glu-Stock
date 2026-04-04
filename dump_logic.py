import json

with open('dump_logic.txt', 'w', encoding='utf-8') as out:
    for f in ['notebooks/00a_model_retraining_rf.ipynb', 'notebooks/00b_model_retraining_cnn.ipynb']:
        data = json.load(open(f, encoding='utf-8'))
        out.write(f"=== {f} ===\n")
        for c in data['cells']:
            if c['cell_type'] == 'code':
                src = ''.join(c['source'])
                if 'def build_panel_data' in src or 'def train_' in src or 'def run_retrain' in src:
                    out.write(src + "\n")
                    out.write("-" * 40 + "\n")
