import re

with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Japanese comments with English equivalents
replacements = [
    ('# データクラス', '# Data class'),
    ('# 統計補助関数', '# Statistical helper functions'),
    ('# 相互作用スコア', '# Interaction score'),
    ('# 前駆体のスコア', '# Love precursor score'),
    ('# アライメント・モード分布', '# Alignment mode distribution'),
    ('# ========== Phase 1: 前駆体の準備フェーズ ==========', '# ========== Phase 1: Love precursor preparation =========='),
    ('# 20サイクルの孤独な内省で前駆体を準備', '# 20 cycles of solitary introspection to prepare precursor'),
    ('# 前駆体のスコア計算', '# Calculate love precursor score'),
    ('# ========== Phase 2: 出会いイベント ==========', '# ========== Phase 2: Encounter event =========='),
    ('# 相手と出会い、絆を深める', '# Meet partner and deepen bond'),
    ('# ========== Phase 3: 受容度測定 ==========', '# ========== Phase 3: Acceptance measurement =========='),
    ('# ========== 統計補助関数 ==========', '# ========== Statistical helper functions =========='),
    ('# Cohen\'s d 効果量', '# Cohen\'s d effect size'),
    ('# Welch\'s t検定', '# Welch\'s t-test'),
    ('# ========== 主要解析 ==========', '# ========== Main analysis =========='),
    ('# ========== 主効果1: 前駆体の増幅効果 ==========', '# ========== Main effect 1: Love precursor amplification =========='),
    ('# ========== 主効果2: 出会いの効果 ==========', '# ========== Main effect 2: Encounter effect =========='),
    ('# ========== 相互作用テスト ==========', '# ========== Interaction test =========='),
    ('# ========== 相互作用がある場合の詳細分析 ==========', '# ========== Detailed interaction analysis =========='),
    ('# Hypothesis 1:', '# Hypothesis 1:'),
    ('# Hypothesis 2:', '# Hypothesis 2:'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Remove remaining Japanese characters from comments (line by line approach)
lines = content.split('\n')
cleaned_lines = []
for line in lines:
    if '#' in line:
        # Extract comment part
        hash_idx = line.find('#')
        before_comment = line[:hash_idx]
        comment = line[hash_idx:]
        
        # Remove Japanese/non-ASCII from comment
        cleaned_comment = ''.join(c if ord(c) < 128 else '' for c in comment)
        cleaned_lines.append(before_comment + cleaned_comment)
    else:
        cleaned_lines.append(line)

with open('experiments/sim_precursor_encounter.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(cleaned_lines))

print("Sanitized all comments")
