import json

with open('dump_02.txt', 'w', encoding='utf-8') as out:
    data = json.load(open('notebooks/02_signal_inference.ipynb', encoding='utf-8'))
    for i, c in enumerate(data['cells']):
        if c['cell_type'] == 'code':
            out.write(f"=== CELL {i} ===\n")
            out.write(''.join(c['source']))
            out.write("\n---\n")
