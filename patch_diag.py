import json

f = 'notebooks/00a_model_retraining_rf.ipynb'
with open(f, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Find Section 3 cell and fix the silent exception + misleading message
for cell in data['cells']:
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if "def build_panel_data" in src and "triple_barrier_label" in src:
            # Replace the silent `except Exception: continue` with diagnostic logging
            new_source = []
            for line in cell['source']:
                if "        except Exception:" in line:
                    new_source.append("        except Exception as e:\n")
                elif "            continue" in line and "continue" in line:
                    new_source.append("            print(f'\\u26a0\\ufe0f {ticker} failed: {type(e).__name__}: {e}')\n")
                    new_source.append("            continue\n")
                elif "print('\\u2705 Successfully aggregated market data.')" in line:
                    # Move success message AFTER the empty check
                    continue
                elif "    if len(all_X) == 0:" in line:
                    new_source.append("    if len(all_X) == 0:\n")
                    new_source.append("        print('\\u274c No valid data was aggregated from any ticker!')\n")
                elif "    return np.vstack(all_X)" in line:
                    new_source.append("    print(f'\\u2705 Successfully aggregated {len(all_X)} tickers worth of market data.')\n")
                    new_source.append(line)
                else:
                    new_source.append(line)
            cell['source'] = new_source
            break

with open(f, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=1)
print("INJECTED DIAGNOSTIC LOGGING INTO 00A!")
