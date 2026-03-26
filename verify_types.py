#!/usr/bin/env python3
"""
Verify type annotations in core modules using AST parsing.
This works without requiring mypy to be installed.
"""

import ast
import pathlib
from typing import Any

def check_file(filepath: pathlib.Path) -> dict[str, list[str]]:
    """Check type annotations in a Python file."""
    content = filepath.read_text(encoding='utf-8')
    tree = ast.parse(content)
    
    issues: dict[str, list[str]] = {
        'missing_return': [],
        'missing_params': [],
        'untyped_args': [],
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            # Check return type
            if node.returns is None and node.name not in ('__init__', '__repr__', '__str__'):
                issues['missing_return'].append(node.name)
            
            # Check parameter types
            for arg in node.args.args:
                if arg.annotation is None and arg.arg not in ('self', 'cls'):
                    issues['untyped_args'].append(f"{node.name}.{arg.arg}")
    
    return issues

def main() -> None:
    """Verify all core modules."""
    core_dir = pathlib.Path('C:/Users/GoldRush/Documents/MyProject/human-persona/core')
    
    print("=" * 70)
    print("TYPE ANNOTATION VERIFICATION")
    print("=" * 70)
    
    total_issues = 0
    
    for py_file in sorted(core_dir.glob('*.py')):
        if py_file.name == '__init__.py':
            continue
        
        try:
            issues = check_file(py_file)
            
            file_issues = (
                len(issues['missing_return']) +
                len(issues['missing_params']) +
                len(issues['untyped_args'])
            )
            
            if file_issues == 0:
                print(f"\n[OK] {py_file.name}: All functions typed")
            else:
                print(f"\n[ISSUES] {py_file.name}: {file_issues} issues found")
                total_issues += file_issues
                
                if issues['missing_return']:
                    print(f"  - Missing return types: {', '.join(issues['missing_return'][:3])}")
                
                if issues['untyped_args']:
                    print(f"  - Untyped parameters: {', '.join(issues['untyped_args'][:3])}")
        
        except Exception as e:
            print(f"\n[ERROR] {py_file.name}: {e}")
            total_issues += 1
    
    print("\n" + "=" * 70)
    if total_issues == 0:
        print("SUCCESS: All core modules have complete type annotations!")
        print("=" * 70)
    else:
        print(f"ISSUES FOUND: {total_issues} type annotation problems")
        print("=" * 70)
        print("\nTo install mypy and run full strict checking:")
        print("  pip install mypy>=1.5.0 types-setuptools")
        print("  python -m mypy core/ --strict")

if __name__ == '__main__':
    main()
