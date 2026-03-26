with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(1, 43):
        print(f'{i}: {lines[i-1]}', end='')
