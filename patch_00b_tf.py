import json

f = 'notebooks/00b_model_retraining_cnn.ipynb'
with open(f, 'r', encoding='utf-8') as file:
    data = json.load(file)

modified = False
for i, cell in enumerate(data['cells']):
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if "import tflite_runtime.interpreter as tflite" in src:
            # We must restore full TensorFlow here
            new_lines = []
            for line in cell['source']:
                if 'import tflite_runtime' in line or 'except ImportError' in line or 'import tensorflow.lite' in line:
                    continue # erase tflite_runtime logic
                if 'try:' in line and 'tflite_runtime' in cell['source'][cell['source'].index(line)+1]:
                    continue # erase try block
                
                # Insert full tensorflow
                if 'import numpy as np' in line:
                    new_lines.append(line)
                    new_lines.append("import tensorflow as tf\n")
                else:
                    new_lines.append(line)
            data['cells'][i]['source'] = new_lines
            modified = True
            break
                
if modified:
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=1)
    print("RESTORED FULL TENSORFLOW IMPORT TO 00B!")
else:
    print("Target cell not found. Cannot patch.")
