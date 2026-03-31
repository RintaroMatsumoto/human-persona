import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import re

experiment_files = {
    'sim_metamorphose_society.py': 1,
    'sim_society.py': 2,
    'sim_large_scale_society.py': 3,
    'sim_pairing.py': 4,
    'sim_generation.py': 5,
    'sim_inheritance.py': 6,
    'sim_network_topology.py': 7,
    'sim_precursor_encounter.py': 8,
    'sim_coexistence.py': 9,
    'sim_spontaneous_love.py': 10,
    'sim_sleep_coexistence.py': 11,
    'sim_loveless_lineage.py': 12,
    'sim_antilove.py': 13,
    'sim_antilove_density.py': 14,
}

def extract_summary(filepath):
    """Extract docstring and key info from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract docstring (first """ ... """)
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        docstring = docstring_match.group(1).strip() if docstring_match else ""
        
        # Get first 3 lines of docstring
        docstring_lines = docstring.split('\n')[:3]
        
        # Find classes and main functions
        classes = re.findall(r'class\s+(\w+)', content)
        
        # Find if file has data output/logging
        has_append = 'append' in content or '.json' in content or '.csv' in content
        
        return {
            'docstring': docstring,
            'classes': classes,
            'has_output': has_append
        }
    except Exception as e:
        return {'error': str(e)}

print("=" * 90)
print("DETAILED EXPERIMENT ANALYSIS")
print("=" * 90)

for filename, priority in sorted(experiment_files.items(), key=lambda x: x[1]):
    filepath = os.path.join(os.getcwd(), filename)
    
    print(f"\n[{priority}] {filename}")
    print("-" * 90)
    
    if not os.path.exists(filepath):
        print("FILE NOT FOUND")
        continue
    
    result = extract_summary(filepath)
    
    if 'error' in result:
        print(f"ERROR: {result['error']}")
        continue
    
    docstring = result['docstring']
    
    # Print first 300 chars of docstring
    first_part = docstring[:400]
    print(first_part)
    print("\n---")
    print(f"Classes: {', '.join(result['classes']) if result['classes'] else 'None'}")
    print(f"Has data output: {result['has_output']}")

print("\n" + "=" * 90)
print("END OF ANALYSIS")
print("=" * 90)
