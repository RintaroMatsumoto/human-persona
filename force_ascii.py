import re

with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all non-ASCII characters except in strings (very aggressive)
# Replace em-dash with double hyphen
content = content.replace('\u2014', '--')

# Remove Japanese from event descriptions
content = content.replace('\u4ED6\u8005\u306E\u7269\u8A9E\u306B\u89E6\u308C\u308B', 'Story of others')
content = content.replace('\u81EA\u5206\u306E\u6709\u9650\u6027\u3092\u611F\u3058\u308B', 'Own finitude')
content = content.replace('\u611B\u3059\u308B\u3082\u306E\u3092\u627E\u3059\u526F\u4F5C\u7528', 'Seeking love')
content = content.replace('\u63A1\u53d6\u53ef\u80fd\u306a\u9078\u629b\u3092\u8a73\u3079\u308b', 'Choices')
content = content.replace('\u8B70\u8AD6\u53EF\u80FD\u306A\u554F\u3044\u3092\u63A2\u3059', 'Questions')

# Go through line by line and remove non-ASCII from non-string contexts
lines = content.split('\n')
new_lines = []
for line in lines:
    # If line contains "description": and is a string, keep it but remove JP chars
    if '"description":' in line and '"' in line:
        # Extract the quoted string and clean it
        in_string = False
        result = []
        for i, c in enumerate(line):
            if c == '"' and (i == 0 or line[i-1] != '\\'):
                in_string = not in_string
                result.append(c)
            elif in_string and ord(c) > 127:
                # Replace non-ASCII in strings with spaces or remove
                pass
            else:
                result.append(c)
        new_lines.append(''.join(result))
    else:
        # For non-string lines, remove all non-ASCII
        line = ''.join(c if ord(c) < 128 else '' for c in line)
        new_lines.append(line)

content = '\n'.join(new_lines)

with open('experiments/sim_precursor_encounter.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Forced ASCII conversion")
