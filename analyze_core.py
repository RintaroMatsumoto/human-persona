#!/usr/bin/env python3
"""Analyze core modules for type annotation coverage."""
import os
import sys
from pathlib import Path

core_dir = Path(__file__).parent / 'core'
py_files = sorted([f for f in core_dir.glob('*.py') if f.name != '__init__.py'])

print("=" * 70)
print("CORE MODULE ANALYSIS")
print("=" * 70)

for py_file in py_files:
    try:
        content = py_file.read_text(encoding='utf-8')
        lines = len(content.splitlines())
        
        # Count type hints
        has_annotations = 'from typing' in content or ': ' in content
        has_return_hints = '->' in content
        
        print(f"\n{py_file.name}:")
        print(f"  Lines: {lines}")
        print(f"  Has typing imports: {has_annotations}")
        print(f"  Has return type hints: {has_return_hints}")
        
        # Show first few non-import lines
        lines_list = content.splitlines()[:30]
        for i, line in enumerate(lines_list[:10], 1):
            if not line.strip().startswith('"""') and line.strip():
                print(f"    {i}: {line[:70]}")
    except Exception as e:
        print(f"\n{py_file.name}: ERROR - {e}")
