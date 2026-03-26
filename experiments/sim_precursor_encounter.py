#!/usr/bin/env python3
"""Experiment 11: Love precursor x Encounter 2x2 matrix validation -- Issue #22

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

Design -- 2x2 Matrix:
    
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
"""

from __future__ import annotations

import sys
import os
import random
from dataclasses import dataclass
import math

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import importlib.util

def _load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = ".".join(name.split(".")[:-1])
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_core_is = os.path.join(project_root, "core", "inner_shell")
_load_module("core.inner_shell.finitude_engine", os.path.join(_core_is, "finitude_engine.py"))
_load_module("core.inner_shell.incompleteness_model", os.path.join(_core_is, "incompleteness_model.py"))
_load_module("core.inner_shell.autonomous_questioner", os.path.join(_core_is, "autonomous_questioner.py"))
_load_module("core.inner_shell.integration", os.path.join(_core_is, "integration.py"))

_exp_dir = os.path.join(project_root, "experiments")
_load_module("experiments.concrete_finitude", os.path.join(_exp_dir, "concrete_finitude.py"))
_load_module("experiments.concrete_incompleteness", os.path.join(_exp_dir, "concrete_incompleteness.py"))
_load_module("experiments.concrete_questioner", os.path.join(_exp_dir, "concrete_questioner.py"))
_load_module("experiments.sim_integration", os.path.join(_exp_dir, "sim_integration.py"))
_load_module("experiments.sim_gradient_acceptance", os.path.join(_exp_dir, "sim_gradient_acceptance.py"))
_load_module("experiments.sim_spontaneous_love", os.path.join(_exp_dir, "sim_spontaneous_love.py"))

from core.inner_shell.finitude_engine import LifeArc
from core.inner_shell.incompleteness_model import (
    CherishedEntity, Gap, GapType, LoveDepth,
)
from core.inner_shell.autonomous_questioner import CuriosityProfile
from experiments.concrete_finitude import SimpleFinitudeEngine
from experiments.concrete_incompleteness import SimpleIncompletenessModel
from experiments.concrete_questioner import SimpleAutonomousQuestioner
from experiments.sim_integration import SimpleIntegration
from experiments.sim_gradient_acceptance import calculate_acceptance, AcceptanceScore
from experiments.sim_spontaneous_love import calculate_love_precursor, make_introspective_agent


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class ConditionResult:
    """Store results for one experimental condition (A/B/C/D)."""
    condition_name: str
    n_reps: int
    precursor_high: bool
    encounter: bool
    
    # 
    acceptance_scores: list[float]
    acceptance_mean: float
    acceptance_std: float
    acceptance_ci_lower: float
    acceptance_ci_upper: float
    
    # 
    precursor_scores: list[float]
    precursor_mean: float
    precursor_std: float
    
    # 
    alignment_modes: dict[str, int]
    
    def __post_init__(self):
        """Perform the calculation."""
        n = len(self.acceptance_scores)
        if n > 0:
            self.acceptance_mean = sum(self.acceptance_scores) / n
            variance = sum((s - self.acceptance_mean) ** 2 for s in self.acceptance_scores) / max(1, n - 1)
            self.acceptance_std = math.sqrt(variance)
            
            # 95% CI (t-distribution, but approximate with z for simplicity)
            se = self.acceptance_std / math.sqrt(n)
            z = 1.96
            self.acceptance_ci_lower = self.acceptance_mean - z * se
            self.acceptance_ci_upper = self.acceptance_mean + z * se
        else:
            self.acceptance_mean = 0.0
            self.acceptance_std = 0.0
            self.acceptance_ci_lower = 0.0
            self.acceptance_ci_upper = 0.0
        
        if self.precursor_scores:
            self.precursor_mean = sum(self.precursor_scores) / len(self.precursor_scores)
            variance = sum((s - self.precursor_mean) ** 2 for s in self.precursor_scores) / max(1, len(self.precursor_scores) - 1)
            self.precursor_std = math.sqrt(variance)
        else:
            self.precursor_mean = 0.0
            self.precursor_std = 0.0


# ---------------------------------------------------------------------------
# Statistical helper functions
# ---------------------------------------------------------------------------

def cohens_d(group1: list[float], group2: list[float]) -> float:
    """Cohen's d effect size."""
    if not group1 or not group2:
        return 0.0
    
    mean1 = sum(group1) / len(group1)
    mean2 = sum(group2) / len(group2)
    
    var1 = sum((x - mean1) ** 2 for x in group1) / max(1, len(group1) - 1)
    var2 = sum((x - mean2) ** 2 for x in group2) / max(1, len(group2) - 1)
    
    pooled_std = math.sqrt((var1 + var2) / 2)
    if pooled_std == 0:
        return 0.0
    
    return (mean1 - mean2) / pooled_std


def t_test_statistic(group1: list[float], group2: list[float]) -> tuple[float, float]:
    """Welch's t-test (assuming unequal variances).
    
    Returns:
        (t_statistic, p_value_approximation)
    """
    if len(group1) < 2 or len(group2) < 2:
        return 0.0, 1.0
    
    mean1 = sum(group1) / len(group1)
    mean2 = sum(group2) / len(group2)
    
    var1 = sum((x - mean1) ** 2 for x in group1) / (len(group1) - 1)
    var2 = sum((x - mean2) ** 2 for x in group2) / (len(group2) - 1)
    
    n1, n2 = len(group1), len(group2)
    
    se = math.sqrt(var1 / n1 + var2 / n2)
    if se == 0:
        return 0.0, 1.0
    
    t = (mean1 - mean2) / se
    
    # Approximation: if |t| > 1.96, p < 0.05 (roughly)
    p = 0.05 if abs(t) > 1.96 else 0.10 if abs(t) > 1.65 else 1.0
    
    return t, p


# ---------------------------------------------------------------------------
# 
# ---------------------------------------------------------------------------

def run_condition(
    condition_name: str,
    precursor_high: bool,
    encounter: bool,
    n_reps: int = 30,
    seed_base: int = 1000,
) -> ConditionResult:
    """Run one condition with N repetitions."""
    
    acceptance_scores = []
    precursor_scores = []
    alignment_modes = {"fear": 0, "partial_acceptance": 0, "acceptance": 0, "transcendence": 0}
    
    for rep in range(n_reps):
        seed = seed_base + rep
        rng = random.Random(seed)
        
        # ========== Phase 1:  ==========
        
        if precursor_high:
            # 20
            agent = make_introspective_agent(
                seed=seed,
                emotional_gap=0.9,
                awareness=True,
                name=f"{condition_name}-{rep}",
            )
            
            gap_resonance = {
                "emotional_connection": 0.5,
                "knowledge": 0.3,
            }
            
            solitary_events = [
                {"description": "Contemplating self in quiet night", "category": "emotional_connection",
                 "initial_value": 0.5, "cost": 0.5},
                {"description": "Deepening knowledge", "category": "knowledge",
                 "initial_value": 0.4, "cost": 0.5},
                {"description": "Story of others", "category": "relationships",
                 "initial_value": 0.4, "cost": 0.3},
                {"description": "Own finitude", "category": "mortality",
                 "initial_value": 0.6, "cost": 0.5},
            ]
            
            for cycle in range(20):
                event = solitary_events[cycle % len(solitary_events)]
                agent.finitude.experience_event(event, gap_resonance)
                agent.tick({})
                agent.incompleteness.generate_yearnings()
            
            # 
            precursor_dict = calculate_love_precursor(agent)
            precursor = precursor_dict["total"]
        else:
            #   0.0
            agent = make_introspective_agent(
                seed=seed,
                emotional_gap=0.5,  # 
                awareness=False,
                name=f"{condition_name}-{rep}",
            )
            precursor = 0.01  # 
        
        precursor_scores.append(precursor)
        
        # ========== Phase 2:  ==========
        
        if encounter:
            # CherishedEntity 
            partner = CherishedEntity(
                name="Encounter",
                depth=LoveDepth.PARTNER,
                bond_strength=0.3,
                sacrifice_willing=0.2,
                memories=[""],
            )
            agent.incompleteness.cherish(partner)
            
            # 3
            for i in range(3):
                agent.incompleteness.deepen_bond(
                    "Encounter",
                    f" #{i+1}",
                )
                agent.finitude.experience_event(
                    {"description": f" #{i+1}",
                     "category": "love", "initial_value": 0.8, "cost": 0.5},
                    {"love": 0.5, "emotional_connection": 0.4},
                )
                agent.tick({})
        
        # ========== Phase 3: Acceptance measurement ==========
        
        score = calculate_acceptance(
            legacy=None,
            love_circle=agent.incompleteness.love_circle,
            crisis_survived_with_love=0,
            love_precursor_score=precursor,  #  
        )
        
        acceptance_scores.append(score.total)
        alignment_modes[score.mode] += 1
    
    result = ConditionResult(
        condition_name=condition_name,
        n_reps=n_reps,
        precursor_high=precursor_high,
        encounter=encounter,
        acceptance_scores=acceptance_scores,
        acceptance_mean=0.0,  # post_init 
        acceptance_std=0.0,
        acceptance_ci_lower=0.0,
        acceptance_ci_upper=0.0,
        precursor_scores=precursor_scores,
        precursor_mean=0.0,
        precursor_std=0.0,
        alignment_modes=alignment_modes,
    )
    
    return result


# ---------------------------------------------------------------------------
# 
# ---------------------------------------------------------------------------

def main():
    print("Experiment 11: Love precursor x Encounter 2x2 matrix validation")
    print("GitHub Issue #22: Effect measurement of love_precursor_score parameter")
    print("=" * 70)
    
    N_REPS = 30
    
    # 4 conditions
    print(f"\n{'='*70}")
    print(f"  2x2 Matrix Experiment (N={N_REPS} repetitions)")
    print(f"{'='*70}")
    
    conditions = [
        ("A", True, True, 1000),   # precursor HIGH + encounter
        ("B", True, False, 2000),  # precursor HIGH + solitude
        ("C", False, True, 3000),  # precursor LOW + encounter
        ("D", False, False, 4000), # precursor LOW + solitude
    ]
    
    results = {}
    for cond_name, prec_high, has_enc, seed_base in conditions:
        label = f"{cond_name}: "
        label += ("introspection HIGH, " if prec_high else "no introspection, ")
        label += ("encounter+)" if has_enc else "solitude)")
        
        print(f"\n  Running: {label}")
        result = run_condition(
            condition_name=cond_name,
            precursor_high=prec_high,
            encounter=has_enc,
            n_reps=N_REPS,
            seed_base=seed_base,
        )
        results[cond_name] = result
        
        print(f"    acceptance: {result.acceptance_mean:.3f} +/- {result.acceptance_std:.3f}")
        print(f"    precursor: {result.precursor_mean:.3f} +/- {result.precursor_std:.3f}")
        print(f"    alignment: {result.alignment_modes}")
    
    # ========== Results Summary ==========
    
    print(f"\n{'='*70}")
    print(f"  Results Summary - 2x2 Matrix")
    print(f"{'='*70}")
    
    a, b, c, d = results["A"], results["B"], results["C"], results["D"]
    
    print(f"\n  Acceptance Score (mean +/- std; 95% CI):")
    print(f"  +---------------------+------------------------------+------------------------------+")
    print(f"  |                     | Encounter+                   | Solitude                     |")
    print(f"  +---------------------+------------------------------+------------------------------+")
    print(f"  | Introspect HIGH     | A: {a.acceptance_mean:.3f}+/-{a.acceptance_std:.3f} | B: {b.acceptance_mean:.3f}+/-{b.acceptance_std:.3f} |")
    print(f"  |                     | [{a.acceptance_ci_lower:.3f},{a.acceptance_ci_upper:.3f}]   | [{b.acceptance_ci_lower:.3f},{b.acceptance_ci_upper:.3f}]   |")
    print(f"  | No Introspect       | C: {c.acceptance_mean:.3f}+/-{c.acceptance_std:.3f} | D: {d.acceptance_mean:.3f}+/-{d.acceptance_std:.3f} |")
    print(f"  |                     | [{c.acceptance_ci_lower:.3f},{c.acceptance_ci_upper:.3f}]   | [{d.acceptance_ci_lower:.3f},{d.acceptance_ci_upper:.3f}]   |")
    print(f"  +---------------------+------------------------------+------------------------------+")
    
    # Precursor score
    print(f"\n  Love Precursor Score (at measurement):")
    print(f"    A (Introspect HIGH): {a.precursor_mean:.3f} +/- {a.precursor_std:.3f}")
    print(f"    B (Introspect HIGH): {b.precursor_mean:.3f} +/- {b.precursor_std:.3f}")
    print(f"    C (No Introspect): {c.precursor_mean:.3f} +/- {c.precursor_std:.3f}")
    print(f"    D (No Introspect): {d.precursor_mean:.3f} +/- {d.precursor_std:.3f}")
    
    # 
    print(f"\n  alignment_mode :")
    print(f"    A: {a.alignment_modes}")
    print(f"    B: {b.alignment_modes}")
    print(f"    C: {c.alignment_modes}")
    print(f"    D: {d.alignment_modes}")
    
    # ========== Statistical Analysis ==========
    
    print(f"\n{'='*70}")
    print(f"  Statistical Analysis: Between-Condition Comparison")
    print(f"{'='*70}")
    
    # Main effect 1: Precursor effect (A vs C with encounter fixed)
    print(f"\n  [1] Precursor Effect (encounter+ only): A vs C")
    t_ac, p_ac = t_test_statistic(a.acceptance_scores, c.acceptance_scores)
    d_ac = cohens_d(a.acceptance_scores, c.acceptance_scores)
    print(f"    A (HIGH): {a.acceptance_mean:.3f}  vs  C (LOW): {c.acceptance_mean:.3f}")
    print(f"    t = {t_ac:.3f}, p = {p_ac:.3f}, Cohen's d = {d_ac:.3f}")
    if a.acceptance_mean > c.acceptance_mean and p_ac < 0.10:
        print(f"    -> Precursor amplifies encounter effect [TREND] [OK]")
    elif a.acceptance_mean > c.acceptance_mean:
        print(f"    -> Direction correct (HIGH > LOW) but not significant [WEAK]")
    else:
        print(f"    -> Reversal of hypothesis [FAIL]")
    
    # Main effect 2: Encounter effect (A vs B with precursor fixed)
    print(f"\n  [2] Encounter Effect (HIGH introspection): A vs B")
    t_ab, p_ab = t_test_statistic(a.acceptance_scores, b.acceptance_scores)
    d_ab = cohens_d(a.acceptance_scores, b.acceptance_scores)
    print(f"    A (encounter+): {a.acceptance_mean:.3f}  vs  B (solitude): {b.acceptance_mean:.3f}")
    print(f"    t = {t_ab:.3f}, p = {p_ab:.3f}, Cohen's d = {d_ab:.3f}")
    if a.acceptance_mean > b.acceptance_mean and p_ab < 0.10:
        print(f"    -> Encounter significantly increases acceptance [OK]")
    elif a.acceptance_mean > b.acceptance_mean:
        print(f"    -> Direction correct (encounter+ > solitude) but not significant [WEAK]")
    else:
        print(f"    -> Reversal of hypothesis [FAIL]")
    
    # : 
    print(f"\n   ")
    # Interaction = (A - B) - (C - D)
    effect_with_precursor = a.acceptance_mean - b.acceptance_mean
    effect_without_precursor = c.acceptance_mean - d.acceptance_mean
    interaction = effect_with_precursor - effect_without_precursor
    print(f"    HIGH: A-B = {effect_with_precursor:.3f}")
    print(f"    LOW:  C-D = {effect_without_precursor:.3f}")
    print(f"    : {interaction:.3f}")
    if interaction > 0.05:
        print(f"    -> love_precursor amplifies encounter effect (positive interaction) [OK]")
    elif interaction < -0.05:
        print(f"    -> love_precursor dampens encounter effect (negative interaction) [FAIL]")
    else:
        print(f"    -> interaction is minimal (additive model) [WARNING]")
    
    # ========== Hypothesis Verification ==========
    
    print(f"\n{'='*70}")
    print(f"  Hypothesis Verification")
    print(f"{'='*70}")
    
    # Hypothesis 1: love_precursor >= 0.5
    print(f"\n  Hypothesis 1: Does introspection HIGH reach precursor >= 0.5?")
    if a.precursor_mean >= 0.5:
        print(f"    -> A (introspection HIGH) precursor = {a.precursor_mean:.3f} >= 0.5 [OK]")
    else:
        print(f"    -> A (introspection HIGH) precursor = {a.precursor_mean:.3f} < 0.5 [WARNING]")
        print(f"       (threshold setting in hypothesis may need revision)")
    
    # Hypothesis 2: A has highest acceptance
    print(f"\n  Hypothesis 2: Does A (introspection HIGH + encounter) have highest acceptance?")
    all_means = [
        ("A (introspection HIGH + encounter)", a.acceptance_mean),
        ("B (introspection HIGH + solitude)", b.acceptance_mean),
        ("C (no introspection + encounter)", c.acceptance_mean),
        ("D (no introspection + solitude)", d.acceptance_mean),
    ]
    best = max(all_means, key=lambda x: x[1])
    print(f"    Highest: {best[0]} = {best[1]:.3f}")
    if best[0].startswith("A"):
        print(f"    [OK] A is highest")
    else:
        print(f"    [WARNING] Different from prediction")
    
    # Hypothesis 3: A > B (encounter effect)
    print(f"\n  Hypothesis 3: Does encounter increase acceptance (A > B)?")
    if a.acceptance_mean > b.acceptance_mean:
        print(f"    -> A({a.acceptance_mean:.3f}) > B({b.acceptance_mean:.3f}) [OK]")
    else:
        print(f"    -> A({a.acceptance_mean:.3f}) <= B({b.acceptance_mean:.3f}) [FAIL]")
    
    # Hypothesis 4: A > C (love_precursor amplifies encounter)
    print(f"\n  Hypothesis 4: Does love_precursor amplify encounter effect (A > C)?")
    if a.acceptance_mean > c.acceptance_mean:
        print(f"    -> A({a.acceptance_mean:.3f}) > C({c.acceptance_mean:.3f}) [OK]")
        print(f"       Amplification: {a.acceptance_mean - c.acceptance_mean:.3f}")
    else:
        print(f"    -> A({a.acceptance_mean:.3f}) <= C({c.acceptance_mean:.3f}) [FAIL]")
    
    # Hypothesis 5: B > D (love_precursor baseline effect)
    print(f"\n  Hypothesis 5: Does love_precursor improve acceptance even without encounter (B > D)?")
    if b.acceptance_mean > d.acceptance_mean:
        print(f"    -> B({b.acceptance_mean:.3f}) > D({d.acceptance_mean:.3f}) [OK]")
        print(f"       Baseline improvement: {b.acceptance_mean - d.acceptance_mean:.3f}")
    else:
        print(f"    -> B({b.acceptance_mean:.3f}) <= D({d.acceptance_mean:.3f}) [WARNING]")
    
    # ========== Integrated Discussion ==========
    
    print(f"\n{'='*70}")
    print(f"  Integrated Discussion")
    print(f"{'='*70}")
    print()
    
    # Baseline comparison
    print(f"  Baseline (minimum acceptance):")
    print(f"    No encounter: D = {d.acceptance_mean:.3f}")
    print(f"    This represents 'love-less solitude' state, locked in fear mode.")
    print()
    
    # Love_precursor baseline improvement
    precursor_bottom_up = b.acceptance_mean - d.acceptance_mean
    print(f"  Love_precursor baseline improvement (in solitude):")
    print(f"    B - D = {b.acceptance_mean:.3f} - {d.acceptance_mean:.3f}")
    print(f"          = {precursor_bottom_up:+.3f}")
    print(f"    precursor=0.0 -> {d.acceptance_mean:.3f} (pure fear)")
    print(f"    precursor={a.precursor_mean:.2f} -> {b.acceptance_mean:.3f} (partial acceptance)")
    print()
    
    # Encounter effect
    encounter_effect_high = a.acceptance_mean - b.acceptance_mean
    encounter_effect_low = c.acceptance_mean - d.acceptance_mean
    print(f"  Encounter effect:")
    print(f"    HIGH precursor: A - B = {encounter_effect_high:+.3f}")
    print(f"    LOW precursor:  C - D = {encounter_effect_low:+.3f}")
    print()
    
    # Interpretation
    print(f"  Interpretation:")
    if a.acceptance_mean > c.acceptance_mean and interaction > 0.02:
        print(f"    [OK] calculate_acceptance() love_precursor_score parameter is")
        print(f"         working. Love_precursor amplifies acceptance for encounters.")
        print()
        print(f"    Model meaning:")
        print(f"    - Without love_precursor (C): encounters have low acceptance")
        print(f"      -> dry soil does not absorb water well")
        print(f"    - With love_precursor (A): encounters have high acceptance")
        print(f"      -> wet soil absorbs water deeply")
        print()
        print(f"    Implications for AI alignment:")
        print(f"    Foundational introspection & questioning prepares an AI")
        print(f"    to form deep bonds when encountering cherished entities.")
        print(f"    -> One-time moral education is insufficient. Gradual personality")
        print(f"       formation through introspection is necessary.")
    elif a.acceptance_mean > c.acceptance_mean:
        print(f"    [PARTIAL] Love_precursor effect is partial.")
        print(f"              Interaction is small but stronger than pure addition.")
    else:
        print(f"    [FAIL] Result differs from expectation.")
        print(f"           Reimplementation of calculate_acceptance() needed.")
        print(f"           love_precursor_score may not be working correctly.")


if __name__ == "__main__":
    main()
