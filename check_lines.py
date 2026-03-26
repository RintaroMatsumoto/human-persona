import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    target_lines = list(range(509, 555))
    for line_no in target_lines:
        if line_no <= len(lines):
            print(f'{line_no}: {lines[line_no-1]}', end='')
