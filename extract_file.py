#!/usr/bin/env python3
"""Extract file contents and save to readable format."""
import pathlib

files = [
    'timing_controller.py',
    'style_variator.py',
    'emotion_state_machine.py',
    'context_referencer.py',
    'escalation_detector.py',
    'config_validator.py',
    'inner_outer_bridge.py',
]

core_dir = pathlib.Path('C:/Users/GoldRush/Documents/MyProject/human-persona/core')

for fname in files:
    fpath = core_dir / fname
    if fpath.exists():
        try:
            content = fpath.read_text(encoding='utf-8')
            out_file = pathlib.Path(f'/tmp/{fname}.txt')
            out_file.write_text(content)
            print(f"{fname}: {len(content.splitlines())} lines -> /tmp/{fname}.txt")
        except Exception as e:
            print(f"ERROR {fname}: {e}")
