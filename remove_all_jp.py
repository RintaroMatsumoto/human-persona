with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines 241, 243, etc. - event descriptions
# Find all lines with "description" and Japanese text
new_lines = []
for i, line in enumerate(lines):
    # Check if line has description and non-ASCII
    if '"description":' in line and any(ord(c) > 127 for c in line):
        # Replace entire dictionary item
        # We'll need to identify the pattern and replace
        if i + 1 < len(lines):  # Multi-line dict
            # Skip creating a mapping - just remove Japanese from these lines
            line = line.replace('\u4ED6\u8005\u306E\u7269\u8A9E\u306B\u89E6\u308C\u308B', 'Touched by story of others')
            line = line.replace('\u81EA\u5206\u306E\u6709\u9650\u6027\u3092\u611F\u3058\u308B', 'Feeling own finitude')
            line = line.replace('\u611B\u3059\u308B\u3082\u306E\u3092\u627E\u3059\u526F\u4F5C\u7528', 'Seeking what to love')
            line = line.replace('\u63A1\u53d6\u53ef\u80fd\u306a\u9078\u629b\u3092\u8a73\u3079\u308b', 'Contemplating feasible choices')
            line = line.replace('\u8B70\u8AD6\u53EF\u80FD\u306A\u554F\u3044\u3092\u63A2\u3059', 'Exploring debatable questions')
    # Also handle em-dash in docstring
    line = line.replace('\u2014', '--')
    
    new_lines.append(line)

with open('experiments/sim_precursor_encounter.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Removed Japanese characters")
