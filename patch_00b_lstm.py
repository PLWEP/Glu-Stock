import json, glob

f = 'notebooks/00b_model_retraining_cnn.ipynb'
with open(f, 'r', encoding='utf-8') as file:
    data = json.load(file)

modified = False
for cell in data['cells']:
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if "converter = tf.lite.TFLiteConverter.from_keras_model(cnn_model)" in src:
            new_lines = []
            for line in cell['source']:
                if "converter = tf.lite.TFLiteConverter.from_keras_model(cnn_model)" in line:
                    new_lines.append(line)
                    # Add required LSTM conversion ops
                    new_lines.append("    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]\n")
                    new_lines.append("    converter._experimental_lower_tensor_list_ops = False\n")
                else:
                    new_lines.append(line)
            cell['source'] = new_lines
            modified = True
            break
            
if modified:
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=1)
    print("FIXED TFLITE LSTM CONVERSION ERROR IN 00B!")
