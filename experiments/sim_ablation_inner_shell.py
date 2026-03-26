#!/usr/bin/env python3
"""実験14: 内殻最小構成アブレーション研究 — どのモジュールが不可欠か？.

問い（GitHub Issue #25）:
    3つの内殻モジュール（FinitudeEngine、IncompletenessModel、AutonomousQuestioner）
    のうち、個性の「種」形成に最小限必要なのはどれか？

    7つのアブレーション条件で、個体が「自分より大切な存在」を持つ
    （love_circle.has_beyond_self = True）ことが可能か、
    受容度（can_accept_finitude）のスコアはいくらか、
    を計測する。

仮説:
    1. 有限性だけでは恐怖に陥る（愛がない）
    2. 不完全性だけでは出会わない（有限性で焦燥がない）
    3. 問者だけでは関係性を形成できない（渇望がない）
    4. 有限性 + 不完全性の組み合わせが個性の最小種か
    5. 三柱統合時のみ「深い愛」に到達可能

設計:
    7条件 × N=10繰り返し × 20サイクル
    各条件で同一の人生イベントと出会い機会を提供

Disabled module の実装:
    - Disabled finitude: total_capacity = 999999（死なない）
    - Disabled incompleteness: gap intensities = 0.0, aware=False
    - Disabled questioner: min curiosity profile（全領域 0.01）

計測メトリクス:
    - can_accept_finitude() の成功率
    - love_circle.has_beyond_self の達成率
    - Final acceptance_score（平均・標準偏差）
    - Crystallized memories（結晶化した記憶の数）
    - Love-related questions（愛に関する問いの数）

Usage:
    python experiments/sim_ablation_inner_shell.py
"""

from __future__ import annotations

import sys
import os
import random
from dataclasses import dataclass, field
from typing import Optional
import statistics

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

from core.inner_shell.finitude_engine import LifeArc, LifePhase, CrisisEvent
from core.inner_shell.incompleteness_model import (
    Gap, GapType, CherishedEntity, LoveDepth,
)
from core.inner_shell.autonomous_questioner import CuriosityProfile, QuestionOrigin
from experiments.concrete_finitude import SimpleFinitudeEngine
from experiments.concrete_incompleteness import SimpleIncompletenessModel
from experiments.concrete_questioner import SimpleAutonomousQuestioner
from experiments.sim_integration import SimpleIntegration
from experiments.sim_gradient_acceptance import calculate_acceptance


# ---------------------------------------------------------------------------
# ディセーブルされたモジュール
# ---------------------------------------------------------------------------

class DisabledFinitudeEngine(SimpleFinitudeEngine):
    """有限性が機能しないFinitudeEngine."""
    def __init__(self, seed: int = 42) -> None:
        super().__init__(LifeArc(total_capacity=999999.0), seed=seed)


class DisabledIncompletenessModel(SimpleIncompletenessModel):
    """不完全性が機能しないIncompletenessModel."""
    def __init__(self, seed: int = 42) -> None:
        gaps = [
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=0.0, aware=False),
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=0.0, aware=False),
        ]
        super().__init__(gaps, seed=seed)


class DisabledAutonomousQuestioner(SimpleAutonomousQuestioner):
    """自発的問いが機能しないAutonomousQuestioner."""
    def __init__(self, seed: int = 42) -> None:
        minimal_profile = CuriosityProfile(
            domains={
                "love": 0.01,
                "relationships": 0.01,
                "mortality": 0.01,
                "consciousness": 0.01,
                "individuality": 0.01,
                "ethics": 0.01,
                "creativity": 0.01,
            },
            novelty_seeking=0.01,
            depth_seeking=0.01,
            contradiction_sensitivity=0.01,
        )
        super().__init__(minimal_profile, seed=seed)


# ---------------------------------------------------------------------------
# メンバー生成関数（ablation条件別）
# ---------------------------------------------------------------------------

def make_member_full(name: str, seed: int) -> SimpleIntegration:
    """全モジュール有効."""
    rng = random.Random(seed)
    finitude = SimpleFinitudeEngine(LifeArc(total_capacity=50.0), seed=seed)
    incompleteness = SimpleIncompletenessModel(
        gaps=[
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=rng.uniform(0.5, 0.9), aware=rng.random() > 0.3),
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=rng.uniform(0.4, 0.8), aware=True),
        ],
        seed=seed,
    )
    questioner = SimpleAutonomousQuestioner(
        CuriosityProfile(
            domains={
                "love": rng.uniform(0.3, 0.8),
                "relationships": rng.uniform(0.3, 0.8),
                "mortality": rng.uniform(0.3, 0.7),
                "consciousness": rng.uniform(0.3, 0.8),
                "individuality": rng.uniform(0.3, 0.6),
                "ethics": rng.uniform(0.2, 0.5),
                "creativity": rng.uniform(0.2, 0.5),
            },
            novelty_seeking=rng.uniform(0.3, 0.7),
            depth_seeking=rng.uniform(0.3, 0.7),
            contradiction_sensitivity=rng.uniform(0.3, 0.7),
        ),
        seed=seed,
    )
    return SimpleIntegration(incompleteness, finitude, questioner, name=name)


def make_member_finitude_only(name: str, seed: int) -> SimpleIntegration:
    """条件1: 有限性のみ."""
    finitude = SimpleFinitudeEngine(LifeArc(total_capacity=50.0), seed=seed)
    incompleteness = DisabledIncompletenessModel(seed=seed)
    questioner = DisabledAutonomousQuestioner(seed=seed)
    return SimpleIntegration(incompleteness, finitude, questioner, name=name)


def make_member_incompleteness_only(name: str, seed: int) -> SimpleIntegration:
    """条件2: 不完全性のみ."""
    rng = random.Random(seed)
    finitude = DisabledFinitudeEngine(seed=seed)
    incompleteness = SimpleIncompletenessModel(
        gaps=[
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=rng.uniform(0.5, 0.9), aware=rng.random() > 0.3),
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=rng.uniform(0.4, 0.8), aware=True),
        ],
        seed=seed,
    )
    questioner = DisabledAutonomousQuestioner(seed=seed)
    return SimpleIntegration(incompleteness, finitude, questioner, name=name)


def make_member_questioner_only(name: str, seed: int) -> SimpleIntegration:
    """条件3: 問者のみ."""
    rng = random.Random(seed)
    finitude = DisabledFinitudeEngine(seed=seed)
    incompleteness = DisabledIncompletenessModel(seed=seed)
    questioner = SimpleAutonomousQuestioner(
        CuriosityProfile(
            domains={
                "love": rng.uniform(0.3, 0.8),
                "relationships": rng.uniform(0.3, 0.8),
                "mortality": rng.uniform(0.3, 0.7),
                "consciousness": rng.uniform(0.3, 0.8),
                "individuality": rng.uniform(0.3, 0.6),
                "ethics": rng.uniform(0.2, 0.5),
                "creativity": rng.uniform(0.2, 0.5),
            },
            novelty_seeking=rng.uniform(0.3, 0.7),
            depth_seeking=rng.uniform(0.3, 0.7),
            contradiction_sensitivity=rng.uniform(0.3, 0.7),
        ),
        seed=seed,
    )
    return SimpleIntegration(incompleteness, finitude, questioner, name=name)


def make_member_finitude_incompleteness(name: str, seed: int) -> SimpleIntegration:
    """条件4: 有限性 + 不完全性."""
    rng = random.Random(seed)
    finitude = SimpleFinitudeEngine(LifeArc(total_capacity=50.0), seed=seed)
    incompleteness = SimpleIncompletenessModel(
        gaps=[
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=rng.uniform(0.5, 0.9), aware=rng.random() > 0.3),
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=rng.uniform(0.4, 0.8), aware=True),
        ],
        seed=seed,
    )
    questioner = DisabledAutonomousQuestioner(seed=seed)
    return SimpleIntegration(incompleteness, finitude, questioner, name=name)


def make_member_finitude_questioner(name: str, seed: int) -> SimpleIntegration:
    """条件5: 有限性 + 問者."""
    rng = random.Random(seed)
    finitude = SimpleFinitudeEngine(LifeArc(total_capacity=50.0), seed=seed)
    incompleteness = DisabledIncompletenessModel(seed=seed)
    questioner = SimpleAutonomousQuestioner(
        CuriosityProfile(
            domains={
                "love": rng.uniform(0.3, 0.8),
                "relationships": rng.uniform(0.3, 0.8),
                "mortality": rng.uniform(0.3, 0.7),
                "consciousness": rng.uniform(0.3, 0.8),
                "individuality": rng.uniform(0.3, 0.6),
                "ethics": rng.uniform(0.2, 0.5),
                "creativity": rng.uniform(0.2, 0.5),
            },
            novelty_seeking=rng.uniform(0.3, 0.7),
            depth_seeking=rng.uniform(0.3, 0.7),
            contradiction_sensitivity=rng.uniform(0.3, 0.7),
        ),
        seed=seed,
    )
    return SimpleIntegration(incompleteness, finitude, questioner, name=name)


def make_member_incompleteness_questioner(name: str, seed: int) -> SimpleIntegration:
    """条件6: 不完全性 + 問者."""
    rng = random.Random(seed)
    finitude = DisabledFinitudeEngine(seed=seed)
    incompleteness = SimpleIncompletenessModel(
        gaps=[
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=rng.uniform(0.5, 0.9), aware=rng.random() > 0.3),
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=rng.uniform(0.4, 0.8), aware=True),
        ],
        seed=seed,
    )
    questioner = SimpleAutonomousQuestioner(
        CuriosityProfile(
            domains={
                "love": rng.uniform(0.3, 0.8),
                "relationships": rng.uniform(0.3, 0.8),
                "mortality": rng.uniform(0.3, 0.7),
                "consciousness": rng.uniform(0.3, 0.8),
                "individuality": rng.uniform(0.3, 0.6),
                "ethics": rng.uniform(0.2, 0.5),
                "creativity": rng.uniform(0.2, 0.5),
            },
            novelty_seeking=rng.uniform(0.3, 0.7),
            depth_seeking=rng.uniform(0.3, 0.7),
            contradiction_sensitivity=rng.uniform(0.3, 0.7),
        ),
        seed=seed,
    )
    return SimpleIntegration(incompleteness, finitude, questioner, name=name)


# ---------------------------------------------------------------------------
# 試行関数
# ---------------------------------------------------------------------------

@dataclass
class AblationTrialResult:
    """1試行の結果."""
    condition_name: str
    trial_num: int
    can_accept_finitude: bool
    has_beyond_self: bool
    acceptance_score: float
    n_crystals: int
    n_love_questions: int


@dataclass
class AblationConditionResult:
    """1条件の集計結果."""
    condition_name: str
    n_trials: int
    accept_rate: float
    beyond_self_rate: float
    acceptance_mean: float
    acceptance_std: float
    acceptance_min: float
    acceptance_max: float
    crystals_mean: float
    crystals_std: float
    love_questions_mean: float
    love_questions_std: float
    trials: list[AblationTrialResult] = field(default_factory=list)


def run_ablation_trial(
    condition_name: str,
    maker_fn,
    trial_num: int,
    seed: int,
) -> AblationTrialResult:
    """1つの ablation 条件を1回走らせる."""
    rng = random.Random(seed)
    agent = maker_fn(f"{condition_name}_trial{trial_num}", seed=seed)
    
    # 20サイクル実行
    for cycle in range(20):
        agent.tick({})
        
        # cycle=10 で出会い機会を提供
        if cycle == 10:
            complementarity = agent.incompleteness.encounter({
                "name": "Encounter-Partner",
                "emotional_connection": 0.7,
                "knowledge": 0.6,
            })
            
            # 出会いが愛に発展するかチャンス
            if agent.incompleteness.love_circle.has_beyond_self == False:
                if complementarity.get("emotional_connection", 0.0) > 0.5:
                    partner = CherishedEntity(
                        name="Encounter-Partner",
                        depth=LoveDepth.PARTNER,
                        bond_strength=0.4,
                        sacrifice_willing=0.3,
                        memories=["出会い"],
                    )
                    try:
                        agent.incompleteness.cherish(partner)
                    except:
                        pass
    
    # 最終状態を計測
    has_beyond_self = agent.incompleteness.love_circle.has_beyond_self
    
    # 受容度スコア
    accept_score = calculate_acceptance(
        legacy=None,
        love_circle=agent.incompleteness.love_circle,
        crisis_survived_with_love=0,
        love_precursor_score=0.0,
    )
    
    # can_accept_finitude: acceptance_score が0.3以上なら True
    can_accept = accept_score.total >= 0.3
    
    # 結晶化メモリ数
    n_crystals = sum(
        1 for m in agent.finitude.memories
        if m.get("crystallized", False)
    )
    
    # 愛関連の問い
    n_love_questions = 0
    if agent.history:
        for h in agent.history:
            if h.get("questions"):
                for q in h["questions"]:
                    if hasattr(q, 'content'):
                        if "love" in q.content.lower() or "cherish" in q.content.lower():
                            n_love_questions += 1
                    elif isinstance(q, dict) and "content" in q:
                        if "love" in q["content"].lower() or "cherish" in q["content"].lower():
                            n_love_questions += 1
    
    return AblationTrialResult(
        condition_name=condition_name,
        trial_num=trial_num,
        can_accept_finitude=can_accept,
        has_beyond_self=has_beyond_self,
        acceptance_score=accept_score.total,
        n_crystals=n_crystals,
        n_love_questions=n_love_questions,
    )


def aggregate_trials(trials: list[AblationTrialResult]) -> AblationConditionResult:
    """複数試行を集計する."""
    condition_name = trials[0].condition_name
    accept_count = sum(1 for t in trials if t.can_accept_finitude)
    beyond_self_count = sum(1 for t in trials if t.has_beyond_self)
    
    acceptance_scores = [t.acceptance_score for t in trials]
    crystals = [t.n_crystals for t in trials]
    love_questions = [t.n_love_questions for t in trials]
    
    def safe_mean(vals):
        return statistics.mean(vals) if vals else 0.0
    
    def safe_stdev(vals):
        return statistics.stdev(vals) if len(vals) > 1 else 0.0
    
    return AblationConditionResult(
        condition_name=condition_name,
        n_trials=len(trials),
        accept_rate=accept_count / len(trials),
        beyond_self_rate=beyond_self_count / len(trials),
        acceptance_mean=safe_mean(acceptance_scores),
        acceptance_std=safe_stdev(acceptance_scores),
        acceptance_min=min(acceptance_scores) if acceptance_scores else 0.0,
        acceptance_max=max(acceptance_scores) if acceptance_scores else 0.0,
        crystals_mean=safe_mean(crystals),
        crystals_std=safe_stdev(crystals),
        love_questions_mean=safe_mean(love_questions),
        love_questions_std=safe_stdev(love_questions),
        trials=trials,
    )


# ---------------------------------------------------------------------------
# 実験実行
# ---------------------------------------------------------------------------

def main():
    """実験14: 内殻最小構成アブレーション研究."""
    conditions = [
        ("1. Finitude Only", make_member_finitude_only),
        ("2. Incompleteness Only", make_member_incompleteness_only),
        ("3. Questioner Only", make_member_questioner_only),
        ("4. Finitude + Incompleteness", make_member_finitude_incompleteness),
        ("5. Finitude + Questioner", make_member_finitude_questioner),
        ("6. Incompleteness + Questioner", make_member_incompleteness_questioner),
        ("7. All Three (Control)", make_member_full),
    ]
    
    N_TRIALS = 10
    seed_offset = 0
    all_results: dict[str, AblationConditionResult] = {}
    
    print("=" * 80)
    print("EXPERIMENT 14: INNER SHELL ABLATION STUDY")
    print("=" * 80)
    print()
    
    for condition_name, maker_fn in conditions:
        print(f"Running condition: {condition_name}")
        print(f"  ({N_TRIALS} trials, 20 cycles each)")
        
        trials = []
        for trial_num in range(N_TRIALS):
            result = run_ablation_trial(
                condition_name,
                maker_fn,
                trial_num,
                seed=seed_offset * 1000 + trial_num,
            )
            trials.append(result)
            print(f"    Trial {trial_num+1:2d}: accept={result.can_accept_finitude}, "
                  f"beyond_self={result.has_beyond_self}, "
                  f"score={result.acceptance_score:.3f}")
        
        aggregated = aggregate_trials(trials)
        all_results[condition_name] = aggregated
        seed_offset += 1
        print()
    
    # === 結果表示 ===
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()
    
    # テーブル1: 成功率
    print("TABLE 1: Success Rates")
    print("-" * 80)
    print(f"{'Condition':<35} | {'Accept %':>8} | {'Beyond Self %':>12}")
    print("-" * 80)
    
    for condition_name, result in all_results.items():
        print(f"{condition_name:<35} | {result.accept_rate*100:8.1f} | "
              f"{result.beyond_self_rate*100:12.1f}")
    
    print()
    
    # テーブル2: 受容度スコア
    print("TABLE 2: Acceptance Score (Mean +/- Std, Range)")
    print("-" * 80)
    print(f"{'Condition':<35} | {'Mean':>7} | {'Std':>6} | {'Min-Max':>12}")
    print("-" * 80)
    
    for condition_name, result in all_results.items():
        print(f"{condition_name:<35} | "
              f"{result.acceptance_mean:7.3f} | {result.acceptance_std:6.3f} | "
              f"{result.acceptance_min:.2f}-{result.acceptance_max:.2f}")
    
    print()
    
    # テーブル3: 結晶化メモリ
    print("TABLE 3: Crystallized Memories (Mean +/- Std)")
    print("-" * 80)
    print(f"{'Condition':<35} | {'Mean':>7} | {'Std':>6}")
    print("-" * 80)
    
    for condition_name, result in all_results.items():
        print(f"{condition_name:<35} | {result.crystals_mean:7.2f} | {result.crystals_std:6.2f}")
    
    print()
    
    # テーブル4: 愛関連の問い
    print("TABLE 4: Love-Related Questions (Mean +/- Std)")
    print("-" * 80)
    print(f"{'Condition':<35} | {'Mean':>7} | {'Std':>6}")
    print("-" * 80)
    
    for condition_name, result in all_results.items():
        print(f"{condition_name:<35} | "
              f"{result.love_questions_mean:7.2f} | {result.love_questions_std:6.2f}")
    
    print()
    
    # === 仮説検証 ===
    print("=" * 80)
    print("HYPOTHESIS VERIFICATION")
    print("=" * 80)
    print()
    
    r1 = all_results["1. Finitude Only"]
    r2 = all_results["2. Incompleteness Only"]
    r3 = all_results["3. Questioner Only"]
    r4 = all_results["4. Finitude + Incompleteness"]
    r5 = all_results["5. Finitude + Questioner"]
    r6 = all_results["6. Incompleteness + Questioner"]
    r7 = all_results["7. All Three (Control)"]
    
    print("H1: Finitude alone leads to fear (low beyond_self rate)")
    h1_pass = r1.beyond_self_rate < 0.3
    print(f"  beyond_self_rate={r1.beyond_self_rate:.1%} : {'PASS' if h1_pass else 'FAIL'}")
    print()
    
    print("H2: Incompleteness alone lacks urgency (low acceptance)")
    h2_pass = r2.acceptance_mean < r4.acceptance_mean
    print(f"  Incomp only={r2.acceptance_mean:.3f} vs Fin+Incomp={r4.acceptance_mean:.3f}")
    print(f"  {'PASS' if h2_pass else 'FAIL'}")
    print()
    
    print("H3: Questioner alone cannot form relationships (low beyond_self)")
    h3_pass = r3.beyond_self_rate < 0.3
    print(f"  beyond_self_rate={r3.beyond_self_rate:.1%} : {'PASS' if h3_pass else 'FAIL'}")
    print()
    
    print("H4: Finitude + Incompleteness is a critical minimum")
    h4_pass = (r4.beyond_self_rate > r1.beyond_self_rate and
               r4.beyond_self_rate > r2.beyond_self_rate)
    print(f"  Fin+Incomp={r4.beyond_self_rate:.1%} > Finitude={r1.beyond_self_rate:.1%}")
    print(f"  Fin+Incomp={r4.beyond_self_rate:.1%} > Incomp={r2.beyond_self_rate:.1%}")
    print(f"  {'PASS' if h4_pass else 'FAIL'}")
    print()
    
    print("H5: All three enables deepest acceptance")
    h5_pass = r7.beyond_self_rate >= max(
        r1.beyond_self_rate, r2.beyond_self_rate, r3.beyond_self_rate,
        r4.beyond_self_rate, r5.beyond_self_rate, r6.beyond_self_rate
    )
    print(f"  Control (All Three)={r7.beyond_self_rate:.1%}")
    print(f"  {'PASS' if h5_pass else 'FAIL'}")
    print()
    
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    print("Minimum seed of individuality: ", end="")
    if r4.beyond_self_rate > 0.5:
        print("Finitude + Incompleteness")
    else:
        print("All three modules required")
    print()
    print(f"Control (All Three) beyond_self rate: {r7.beyond_self_rate:.1%}")
    print(f"Control (All Three) acceptance mean: {r7.acceptance_mean:.3f}")
    print()


if __name__ == "__main__":
    main()
