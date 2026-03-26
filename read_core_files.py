#!/usr/bin/env python3
"""Read and save all core module contents."""
import pathlib

core_dir = pathlib.Path('C:/Users/GoldRush/Documents/MyProject/human-persona/core')

files_to_read = [
    'base_persona.py',
    'timing_controller.py',
    'style_variator.py',
    'emotion_state_machine.py',
    'context_referencer.py',
    'escalation_detector.py',
    'config_validator.py',
    'escalation_detector.py',
    'inner_outer_bridge.py',
]

# Also check inner_shell
inner_shell_files = sorted((core_dir / 'inner_shell').glob('*.py'))
if inner_shell_files:
    files_to_read.extend([f.name for f in inner_shell_files if f.name != '__init__.py'])

output = []
for filename in files_to_read:
    filepath = core_dir / filename
    if filepath.exists():
        try:
            content = filepath.read_text(encoding='utf-8')
            output.append(f"\n{'='*80}")
            output.append(f"FILE: {filepath.relative_to(core_dir.parent)}")
            output.append(f"{'='*80}")
            output.append(content[:3000])  # First 3000 chars
            if len(content) > 3000:
                output.append(f"\n... ({len(content) - 3000} more characters) ...\n")
        except Exception as e:
            output.append(f"ERROR reading {filename}: {e}\n")

result = '\n'.join(output)
print(result)
