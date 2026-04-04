import json, ast
data = json.load(open('notebooks/00b_model_retraining_cnn.ipynb', encoding='utf-8'))
for i, cell in enumerate(data['cells']):
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        try:
            if not src.startswith("!"):
                ast.parse(src)
        except SyntaxError as e:
            print(f"Cell {i} SyntaxError: {e}")
            print(repr(src[:200]))
            break
else:
    print("ALL CELLS ARE VALID SYNTAX!")
