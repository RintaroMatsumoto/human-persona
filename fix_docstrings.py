with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 99: docstring with Japanese
lines[98] = '    """Store results for one experimental condition (A/B/C/D)."""\n'

# Line 121: method docstring with Japanese
lines[120] = '        """Perform the calculation."""\n'

# Line 210: function docstring with Japanese
lines[209] = '    """Run one condition with N repetitions."""\n'

with open('experiments/sim_precursor_encounter.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed docstrings")
