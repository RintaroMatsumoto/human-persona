with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    in_docstring = False
    for i, line in enumerate(lines, 1):
        if i == 1:
            continue
        if '"""' in line:
            if not in_docstring:
                in_docstring = True
                print(f'Docstring starts at line 2')
            else:
                in_docstring = False
                print(f'Docstring ends at line {i}')
                print(f'First code line: {i+1}')
                break
