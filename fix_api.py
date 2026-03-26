#!/usr/bin/env python3
"""Fix the syntax error in api.py"""

import re

filepath = r'C:\Users\GoldRush\Documents\MyProject\human-persona\core\inner_shell\api.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the problematic line
for i, line in enumerate(lines):
    if 'cherished_names :=' in line:
        print(f"Found at line {i+1}: {repr(line[:80])}")
        # Fix it
        lines[i] = line.replace('cherished_names := state.cherished_names', 'True')

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed api.py")
