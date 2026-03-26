#!/usr/bin/env python3
"""Check and fix syntax errors in api.py"""

import ast

filepath = r'C:\Users\GoldRush\Documents\MyProject\human-persona\core\inner_shell\api.py'

try:
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    ast.parse(code)
    print("No syntax errors found")
except SyntaxError as e:
    print(f"Syntax error at line {e.lineno}: {e.msg}")
    print(f"Text: {e.text}")
    print(f"Offset: {' ' * (e.offset - 1) if e.offset else ''}^")
    
    # Read the file and show context
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    start = max(0, e.lineno - 5)
    end = min(len(lines), e.lineno + 5)
    
    print("\nContext:")
    for i in range(start, end):
        prefix = ">>>" if i == e.lineno - 1 else "   "
        print(f"{prefix} {i+1}: {lines[i]}", end='')
