english_docstring = '''"""Experiment 11: Love precursor x Encounter 2x2 matrix validation — Issue #22

Research Question:
    Experiment 8 enabled calculation of love_precursor score.
    However, the actual effect of this precursor parameter was not validated.
    
    calculate_acceptance() now has a love_precursor_score parameter.
    This experiment validates whether precursor "amplifies" encounter effects.

Hypotheses:
    1. HIGH precursor: 20 cycles of solitary introspection reaches precursor >= 0.5
    2. LOW precursor: no introspection, precursor remains ~0.01
    3. encounter+: add CherishedEntity, deepen bond
    4. encounter-: no partner
    5. HIGH precursor + encounter+ shows highest acceptance
    6. love_precursor acts as amplification coefficient for encounter effects

Design — 2x2 Matrix:
    
                         encounter+                   encounter-
    introspection HIGH   A: precursor=HIGH            B: precursor=HIGH
                            acceptance=?                 acceptance=?
    
    introspection NONE   C: precursor=LOW             D: precursor=LOW
                            acceptance=?                 acceptance=?

Key Findings Expected:
    - A > B (encounter effect when precursor is ready)
    - A > C (precursor amplifies encounter encounter_effect_high > encounter_effect_low
    - B > D (precursor provides baseline acceptance even without encounter)
    - Interaction (A-B) - (C-D) > 0 (positive interaction confirms amplification)

Statistics:
    - N=30 repetitions per condition = 120 total simulation runs
    - Metrics: acceptance_score (mean, std, 95% CI), love_precursor_score, alignment_mode distribution
    - Tests: Welch t-tests (unequal variances), Cohen d effect sizes, interaction analysis

Implementation Reference:
    - calculate_love_precursor() from sim_spontaneous_love.py
    - calculate_acceptance() with love_precursor_score parameter
    - SimpleIntegration combining IncompletenessModel, FinitudeEngine, AutonomousQuestioner
"""'''

with open('experiments/sim_precursor_encounter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find docstring boundaries
start = 1
end = 41
for i in range(2, len(lines)):
    if '"""' in lines[i]:
        end = i
        break

# Reconstruct file
new_lines = [lines[0]]  # Keep shebang
new_lines.append(english_docstring + '\n')
new_lines.extend(lines[end+1:])

with open('experiments/sim_precursor_encounter.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Replaced docstring (lines 2-{end+1}) with English version")
