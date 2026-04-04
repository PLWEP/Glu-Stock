import json

f = 'notebooks/00b_model_retraining_cnn.ipynb'
with open(f, 'r', encoding='utf-8') as file:
    data = json.load(file)
    
modified = False
for cell in data['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            # The buggy line is where I did cell_source.replace("import numpy as np", "import numpy as np\\ntry:\\n...")
            if 'import numpy as np\\ntry:\\n' in line:
                # the line literally has python escape sequences in it.
                # Let's completely replace it with proper json array formatting
                clean_lines = [
                    "import numpy as np\n",
                    "try:\n",
                    "    import tflite_runtime.interpreter as tflite\n",
                    "except ImportError:\n",
                    "    import tensorflow.lite as tflite\n"
                ]
                new_source.extend(clean_lines)
                modified = True
            else:
                new_source.append(line)
        cell['source'] = new_source

if modified:
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=1)
    print("Fixed formatting in 00b_model_retraining_cnn.ipynb")
else:
    print("No errors found.")
