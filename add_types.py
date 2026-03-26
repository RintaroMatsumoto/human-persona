#!/usr/bin/env python3
"""
Script to analyze and add type annotations to core modules.
This script identifies functions/methods missing type hints.
"""
import re
import pathlib
from typing import Dict, List, Tuple

core_dir = pathlib.Path('C:/Users/GoldRush/Documents/MyProject/human-persona/core')

# Patterns to help identify missing type hints
def analyze_file(filepath: pathlib.Path) -> Dict[str, List[str]]:
    """Analyze a Python file for missing type hints."""
    content = filepath.read_text(encoding='utf-8')
    issues = {'missing_return': [], 'missing_param': []}
    
    # Find function definitions
    func_pattern = r'^\s*(?:async\s+)?def\s+(\w+)\s*\((.*?)\)(?:\s*->\s*[^:]+)?:'
    
    for match in re.finditer(func_pattern, content, re.MULTILINE):
        func_name = match.group(1)
        params = match.group(2)
        
        # Check if return type is present
        full_sig = content[match.start():match.end()]
        if '->' not in full_sig:
            issues['missing_return'].append(f"{func_name}()")
        
        # Check if all params have types
        param_list = [p.strip() for p in params.split(',') if p.strip() and p.strip() != 'self']
        for param in param_list:
            if ':' not in param:
                issues['missing_param'].append(f"{func_name}({param})")
    
    return issues

print("Type Annotation Analysis")
print("="*70)

for py_file in sorted(core_dir.glob('*.py')):
    if py_file.name == '__init__.py':
        continue
    
    issues = analyze_file(py_file)
    
    print(f"\n{py_file.name}:")
    if issues['missing_return']:
        print(f"  Missing return types: {len(issues['missing_return'])}")
    if issues['missing_param']:
        print(f"  Missing param types: {len(issues['missing_param'])}")
    if not issues['missing_return'] and not issues['missing_param']:
        print(f"  OK - appears fully typed")
