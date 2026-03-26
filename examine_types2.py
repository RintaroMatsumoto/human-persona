#!/usr/bin/env python3
"""Examine type annotations in core modules."""
import ast
import pathlib

core_dir = pathlib.Path('C:/Users/GoldRush/Documents/MyProject/human-persona/core')
output = []

for py_file in sorted(core_dir.glob('*.py')):
    if py_file.name == '__init__.py':
        continue
    
    try:
        content = py_file.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        output.append(f"\n{'='*70}")
        output.append(f"FILE: {py_file.name}")
        output.append(f"{'='*70}")
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_return = "Y" if node.returns else "N"
                arg_hints = sum(1 for arg in node.args.args if arg.annotation)
                total_args = len(node.args.args)
                
                if not node.returns or arg_hints < total_args:
                    output.append(f"  {has_return} {node.name} -> return={node.returns}, args={arg_hints}/{total_args}")
            
            elif isinstance(node, ast.ClassDef):
                output.append(f"\n  CLASS: {node.name}")
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        has_return = "Y" if item.returns else "N"
                        arg_hints = sum(1 for arg in item.args.args if arg.annotation)
                        total_args = max(0, len(item.args.args) - 1)  # exclude self
                        
                        if not item.returns or (total_args > 0 and arg_hints < total_args):
                            output.append(f"    {has_return} {item.name} -> args={arg_hints}/{total_args}")
    
    except Exception as e:
        output.append(f"\nERROR in {py_file.name}: {e}")

result_text = '\n'.join(output)
pathlib.Path('C:/Users/GoldRush/Documents/MyProject/human-persona/type_analysis.txt').write_text(result_text)
print("Analysis written to type_analysis.txt")
print(result_text[:2000])
