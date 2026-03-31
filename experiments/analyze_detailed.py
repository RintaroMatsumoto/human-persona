import sys
sys.stdout.reconfigure(encoding='utf-8')

import ast
import os

experiment_files = [
    'sim_metamorphose_society.py',
    'sim_society.py',
    'sim_large_scale_society.py',
    'sim_pairing.py',
    'sim_generation.py',
    'sim_inheritance.py',
    'sim_network_topology.py',
    'sim_precursor_encounter.py',
    'sim_coexistence.py',
    'sim_spontaneous_love.py',
    'sim_sleep_coexistence.py',
    'sim_loveless_lineage.py',
    'sim_antilove.py',
    'sim_antilove_density.py',
]

results = {}

for filename in experiment_files:
    filepath = os.path.join(os.getcwd(), filename)
    
    if not os.path.exists(filepath):
        results[filename] = None
        continue
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check file exists
        results[filename] = {
            'size': len(lines),
            'first_30_lines': ''.join(lines[:30])
        }
    except Exception as e:
        results[filename] = {'error': str(e)}

# Output results
for fname, data in results.items():
    print(f"\n{'='*60}")
    print(f"FILE: {fname}")
    print(f"{'='*60}")
    if data is None:
        print("FILE NOT FOUND")
    elif 'error' in data:
        print(f"ERROR: {data['error']}")
    else:
        print(f"Size: {data['size']} lines\n")
        print(data['first_30_lines'])
