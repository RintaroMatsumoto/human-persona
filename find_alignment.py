import re

with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        if 'alignment_modes' in line:
            print(f'{i}: {line}', end='')
