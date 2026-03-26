with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    jp_comments = []
    for i, line in enumerate(lines, 1):
        # Look for lines with # followed by Japanese characters
        if '#' in line:
            after_hash = line[line.find('#'):]
            for c in after_hash:
                if ord(c) > 127 and c not in '\n\r':
                    jp_comments.append(i)
                    break

print(f"Lines with Japanese in comments: {jp_comments}")
if jp_comments:
    print("\nShowing first 10:")
    for line_no in jp_comments[:10]:
        print(f"{line_no}: {repr(lines[line_no-1][:100])}")
