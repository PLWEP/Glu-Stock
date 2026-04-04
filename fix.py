import json, glob
for f in glob.glob('notebooks/*.ipynb'):
    if '00a' in f or '00b' in f or '01_' in f:
        data = json.load(open(f, 'r', encoding='utf-8'))
        modified = False
        for cell in data['cells']:
            if cell['cell_type'] == 'code':
                new_source = []
                for line in cell['source']:
                    if '\\n\n' in line:
                        line = line.replace('\\n\n', '\n')
                        modified = True
                    new_source.append(line)
                cell['source'] = new_source
        if modified:
            json.dump(data, open(f, 'w', encoding='utf-8'), indent=1)
            print('Fixed', f)
