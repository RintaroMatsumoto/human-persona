import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(min(20, len(lines))):
        print(f'{i+1}: {lines[i]}', end='')
