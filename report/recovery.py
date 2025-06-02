#Script to remove all outputs from a Jupyter notebook
import json

with open('combinatorics.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

for cell in notebook.get('cells', []):
    if 'outputs' in cell:
        cell['outputs'] = []

with open('combinatorics_cleaned.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False)