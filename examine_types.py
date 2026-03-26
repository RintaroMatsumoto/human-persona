#!/usr/bin/env python3
"""Examine type annotations in core modules."""
import ast
import pathlib
import sys

core_dir = pathlib.Path('C:/Users/GoldRush/Documents/MyProject/human-persona/core')

for py_file in sorted(core_dir.glob('*.py')):
    if py_file.name == '__init__.py':
        continue
    
    try:
        content = py_file.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        print(f"\n{'='*70}")
        print(f"FILE: {py_file.name}")
        print(f"{'='*70}")
        
        # Find functions without return type hints
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_return_hint = node.returns is not None
                arg_hints = sum(1 for arg in node.args.args if arg.annotation)
                total_args = len(node.args.args)
                
                hint_status = "✓" if has_return_hint else "✗"
                args_status = f"{arg_hints}/{total_args}" if total_args > 0 else "no args"
                
                if not has_return_hint or arg_hints < total_args:
                    print(f"  {hint_status} {node.name}({args_status}) -> {node.returns if has_return_hint else 'None'}")
            
            elif isinstance(node, ast.ClassDef):
                print(f"\n  CLASS: {node.name}")
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        has_return = item.returns is not None
                        arg_hints = sum(1 for arg in item.args.args if arg.annotation)
                        total_args = len(item.args.args) - 1  # exclude self
                        
                        hint_status = "✓" if has_return else "✗"
                        args_status = f"{arg_hints}/{total_args}"
                        
                        if not has_return or arg_hints < total_args:
                            print(f"    {hint_status} {item.name}({args_status})")
    
    except SyntaxError as e:
        print(f"\nERROR in {py_file.name}: {e}")
