#!/usr/bin/env python3
import pathlib

core_dir = pathlib.Path('C:/Users/GoldRush/Documents/MyProject/human-persona/core')
output_file = core_dir.parent / 'core_analysis.txt'

files_to_read = [
    'base_persona.py',
    'timing_controller.py',
    'style_variator.py',
    'emotion_state_machine.py',
    'context_referencer.py',
    'escalation_detector.py',
    'config_validator.py',
    'inner_outer_bridge.py',
]

output = []
for filename in sorted(set(files_to_read)):
    filepath = core_dir / filename
    if filepath.exists():
        content = filepath.read_text(encoding='utf-8')
        lines = content.splitlines()
        output.append(f"\n{'='*80}")
        output.append(f"FILE: {filename} ({len(lines)} lines)")
        output.append(f"{'='*80}\n")
        output.append('\n'.join(lines[:100]))

result = '\n'.join(output)
output_file.write_text(result, encoding='utf-8')
print(f"Wrote analysis to {output_file}")
