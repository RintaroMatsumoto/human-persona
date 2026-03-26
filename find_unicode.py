import sys

with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    issues = []
    for i, line in enumerate(lines, 1):
        for j, c in enumerate(line):
            if ord(c) > 127:
                issues.append((i, j, c, ord(c)))
    
    if issues:
        print(f"Found {len(issues)} non-ASCII characters:")
        for line_no, col, char, code in issues[:20]:  # Show first 20
            print(f"  Line {line_no}, col {col}: U+{code:04X} (in context)")
    else:
        print("No non-ASCII characters found!")
