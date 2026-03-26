with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line_no in [237, 238, 239, 240]:
        line = lines[line_no - 1]
        ascii_line = ''.join(c if ord(c) < 128 else f'[{ord(c):04X}]' for c in line)
        print(f'{line_no}: {ascii_line}', end='')
