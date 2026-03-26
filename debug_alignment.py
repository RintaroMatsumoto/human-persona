with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(240, 275):
        if i < len(lines):
            print(f'{i+1}: {lines[i]}', end='')
