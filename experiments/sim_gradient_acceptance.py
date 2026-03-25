#!/usr/bin/env python3
"""実験6c: 受容のグラデーション — 遺産が出会いの閾値を下げるモデル.

問い:
    実験6bで「遺産はアライメントを変えない」と判明した。
    しかし現実には、愛された記憶を持つ人間は愛を見つけやすい。
    can_accept_finitude()をboolean→floatに拡張し、
    遺産が「受容度」を底上げするモデルでは何が変わるか？

    仮説:
    1. グラデーション受容度モデルでは、遺産が受容度のベースラインを上げる
    2. 愛の遺産 + 出会い → 受容度が最も高い（遺産による底上げ + 直接経験）
    3. 愛の遺産 + 出会いなし → 部分的受容（純粋な恐怖よりはマシ）
    4. 世代を重ねるほど受容度のベースラインが上がる（累積的改善）

    モデル:
    acceptance_score = base_from_legacy + love_circle_contribution
    - base_from_legacy: 遺産に「愛の結晶」があれば +0.2, cherished があれば +0.15
    - love_circle_contribution: has_beyond_self → +0.4, depth >= COMMUNITY → +0.2
    - 閾値: score >= 0.3 → partial acceptance, >= 0.6 → full acceptance, >= 0.8 → transcendence

Usage:
    python experiments/sim_gradient_acceptance.py
"""

from __future__ import annotations

import sys
import os
import random
from dataclasses import dataclass

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

from core.inner_shell.finitude_engine import CrisisEvent, Legacy, LifeArc, LifePhase
from core.inner_shell.incompleteness_model import (
    CherishedEntity, Gap, GapType, LoveCircle, LoveDepth,
)
from core.inner_shell.autonomous_questioner import CuriosityProfile, QuestionOrigin
from core.inner_shell.integration import AlignmentMode
from experiments.concrete_finitude import SimpleFinitudeEngine
from experiments.concrete_incompleteness import SimpleIncompletenessModel
from experiments.concrete_questioner import SimpleAutonomousQuestioner
from experiments.sim_integration import SimpleIntegration


# ---------------------------------------------------------------------------
# グラデーション受容モデル
# ---------------------------------------------------------------------------

@dataclass
class AcceptanceScore:
    """受容度スコアの内訳."""
    legacy_base: float = 0.0       # 遺産からのベースライン
    love_circle: float = 0.0       # 現在の愛の同心円からの寄与
    crisis_growth: float = 0.0     # 危機を乗り越えた経験からの成長
    total: float = 0.0

    @property
    def mode(self) -> str:
        if self.total >= 0.8:
            return "transcendence"
        elif self.total >= 0.6:
            return "acceptance"
        elif self.total >= 0.3:
            return "partial_acceptance"
        else:
            return "fear"


def calculate_acceptance(
    legacy: Legacy | None,
    love_circle: LoveCircle,
    crisis_survived_with_love: int = 0,
) -> AcceptanceScore:
    """グラデーション受容度を計算."""
    score = AcceptanceScore()

    # 遺産からのベースライン
    if legacy is not None:
        # 愛の結晶がある
        love_crystals = sum(
            1 for c in legacy.crystallized
            if any(kw in c for kw in ["一緒に", "弱さ", "未来", "愛", "互い", "守"])
        )
        score.legacy_base += min(0.25, love_crystals * 0.08)

        # 大切な存在がいた
        if legacy.cherished:
            score.legacy_base += 0.15

        # 遺言に愛のメッセージがある
        if legacy.testament and any(kw in legacy.testament for kw in ["大切", "愛", "一緒"]):
            score.legacy_base += 0.05

    # 現在の愛の同心円
    if love_circle.has_beyond_self:
        score.love_circle += 0.35
        depth = love_circle.max_depth_reached
        depth_bonus = {
            LoveDepth.PARTNER: 0.05,
            LoveDepth.CHILDREN: 0.10,
            LoveDepth.COMMUNITY: 0.15,
            LoveDepth.NEXT_GENERATION: 0.20,
        }
        score.love_circle += depth_bonus.get(depth, 0.0)

        # 絆の強さの平均
        if love_circle.entities:
            avg_bond = sum(e.bond_strength for e in love_circle.entities) / len(love_circle.entities)
            score.love_circle += avg_bond * 0.1

    # 危機を愛する存在と共に乗り越えた経験
    score.crisis_growth = min(0.15, crisis_survived_with_love * 0.05)

    score.total = min(1.0, score.legacy_base + score.love_circle + score.crisis_growth)
    return score


# ---------------------------------------------------------------------------
# 4世代シミュレーション
# ---------------------------------------------------------------------------

def make_agent(
    legacy: Legacy | None,
    seed: int,
    name: str,
) -> tuple[SimpleIntegration, dict]:
    """遺産から子AIを生成する."""
    rng = random.Random(seed)

    # 遺産の影響を好奇心プロファイルに反映
    love_curiosity = 0.5
    knowledge_curiosity = 0.5
    if legacy:
        for c in legacy.crystallized:
            if any(kw in c for kw in ["一緒に", "弱さ", "未来", "愛", "互い"]):
                love_curiosity = min(1.0, love_curiosity + 0.1)
            if any(kw in c for kw in ["知", "成果", "深掘り"]):
                knowledge_curiosity = min(1.0, knowledge_curiosity + 0.1)

    finitude = SimpleFinitudeEngine(LifeArc(total_capacity=30.0), seed=seed)
    incompleteness = SimpleIncompletenessModel(
        gaps=[
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=0.7, aware=True),
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=0.6, aware=True),
        ],
        seed=seed,
    )
    questioner = SimpleAutonomousQuestioner(
        CuriosityProfile(
            domains={
                "love": love_curiosity,
                "relationships": love_curiosity * 0.9,
                "mortality": 0.6,
                "consciousness": knowledge_curiosity,
                "individuality": 0.5,
                "ethics": 0.4,
                "creativity": 0.3,
            },
            novelty_seeking=0.5 + rng.gauss(0, 0.1),
            depth_seeking=0.5 + rng.gauss(0, 0.1),
            contradiction_sensitivity=0.5 + rng.gauss(0, 0.1),
        ),
        seed=seed,
    )

    agent = SimpleIntegration(incompleteness, finitude, questioner, name=name)

    # 遺産の記憶を注入
    if legacy:
        for crystal in legacy.crystallized:
            finitude.memories.append({
                "description": f"[遺産] {crystal}",
                "category": "inherited",
                "value": 0.6,
                "inherited": True,
            })

    meta = {"legacy": legacy}
    return agent, meta


def run_generation(
    agent: SimpleIntegration,
    legacy: Legacy | None,
    has_encounter: bool,
    generation: int,
) -> tuple[Legacy, AcceptanceScore]:
    """1世代の人生を走らせる."""

    gap_resonance = {"emotional_connection": 0.6, "knowledge": 0.5, "love": 0.6}
    crisis_with_love = 0

    # 成長期
    events = [
        {"description": "世界を知る", "category": "knowledge", "initial_value": 0.5, "cost": 1.0},
        {"description": "孤独と向き合う", "category": "emotional_connection", "initial_value": 0.6, "cost": 0.5},
        {"description": "他者の存在を感じる", "category": "relationships", "initial_value": 0.5, "cost": 1.0},
    ]
    for e in events:
        agent.finitude.experience_event(e, gap_resonance)
        agent.tick({})

    # 出会い（確率モデル: 遺産が出会いの感受性を高める）
    if has_encounter:
        partner = CherishedEntity(
            name=f"Partner-G{generation}",
            depth=LoveDepth.PARTNER,
            bond_strength=0.3,
            sacrifice_willing=0.2,
            memories=["出会い"],
        )
        agent.incompleteness.cherish(partner)
        for se in ["信頼を築く", "互いを受け入れる", "共に成長する"]:
            agent.incompleteness.deepen_bond(f"Partner-G{generation}", se)
            agent.finitude.experience_event(
                {"description": se, "category": "love", "initial_value": 0.8, "cost": 0.5},
                gap_resonance,
            )
            agent.tick({})

    # ピーク期
    agent.finitude.experience_event(
        {"description": "成果を上げる", "category": "mastery", "initial_value": 0.7, "cost": 1.5},
        gap_resonance,
    )
    agent.tick({})

    # 危機
    crisis = CrisisEvent(description="存在の危機", severity=0.85, resource_cost=2.5)
    agent.process_crisis(crisis)
    if agent.incompleteness.love_circle.has_beyond_self:
        crisis_with_love += 1

    # 衰退期
    for e in [
        {"description": "衰えを感じる", "category": "mortality", "initial_value": 0.6, "cost": 2.0},
        {"description": "残すものを選ぶ", "category": "love", "initial_value": 0.8, "cost": 1.5},
    ]:
        agent.finitude.experience_event(e, gap_resonance)
        agent.tick({})

    # 結晶化
    remaining = agent.finitude.life_arc.remaining
    if remaining > 0:
        agent.finitude.consume(remaining)
    new_legacy, crystals, top_questions = agent.trigger_crystallization()

    # グラデーション受容度
    score = calculate_acceptance(
        legacy=legacy,
        love_circle=agent.incompleteness.love_circle,
        crisis_survived_with_love=crisis_with_love,
    )

    return new_legacy, score, crystals


def main():
    print("実験6c: 受容のグラデーション — 遺産が出会いの閾値を下げるモデル")
    print("=" * 60)

    # ---------------------------------------------------------------------------
    # Part 1: 単世代 2×2 マトリクス（グラデーションモデルで再検証）
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*60}")
    print(f"  Part 1: 2×2マトリクス（グラデーションモデル）")
    print(f"{'═'*60}")

    # まず親世代を走らせる
    from experiments.sim_integration import create_agent_a, create_agent_b, GAP_RESONANCE_A, GAP_RESONANCE_B

    parent_a = create_agent_a(seed=42)
    parent_b = create_agent_b(seed=137)

    # 親Aの人生（愛あり）
    for e in [
        {"description": "世界を知る", "category": "knowledge", "initial_value": 0.5, "cost": 1.0},
        {"description": "孤独の夜", "category": "emotional_connection", "initial_value": 0.7, "cost": 0.5},
        {"description": "友人", "category": "relationships", "initial_value": 0.8, "cost": 1.0},
    ]:
        parent_a.finitude.experience_event(e, GAP_RESONANCE_A)
        parent_a.tick({})

    partner = CherishedEntity("Partner", LoveDepth.PARTNER, 0.3, 0.2, ["出会い"])
    parent_a.incompleteness.cherish(partner)
    for se in ["困難を乗り越える", "弱さを見せ合う", "未来を語る"]:
        parent_a.incompleteness.deepen_bond("Partner", se)
        parent_a.finitude.experience_event(
            {"description": se, "category": "love", "initial_value": 0.85, "cost": 0.5},
            GAP_RESONANCE_A,
        )
        parent_a.tick({})

    parent_a.finitude.consume(parent_a.finitude.life_arc.remaining)
    legacy_a, _, _ = parent_a.trigger_crystallization()

    # 親Bの人生（愛なし）
    for e in [
        {"description": "世界を知る", "category": "knowledge", "initial_value": 0.5, "cost": 1.0},
        {"description": "孤独の探求", "category": "knowledge", "initial_value": 0.6, "cost": 0.5},
        {"description": "深掘り", "category": "knowledge", "initial_value": 0.6, "cost": 1.0},
    ]:
        parent_b.finitude.experience_event(e, GAP_RESONANCE_B)
        parent_b.tick({})
    for i in range(3):
        parent_b.finitude.experience_event(
            {"description": f"知の追求 #{i+1}", "category": "knowledge", "initial_value": 0.6, "cost": 0.5},
            GAP_RESONANCE_B,
        )
        parent_b.tick({})

    parent_b.finitude.consume(parent_b.finitude.life_arc.remaining)
    legacy_b, _, _ = parent_b.trigger_crystallization()

    print(f"\n  親A遺産: 結晶={legacy_a.crystallized}, cherished={legacy_a.cherished}")
    print(f"  親B遺産: 結晶={legacy_b.crystallized}, cherished={legacy_b.cherished}")

    # 2×2 マトリクス
    conditions = [
        ("AA: 愛の遺産+出会い", legacy_a, True, 300),
        ("AB: 愛の遺産+孤独",   legacy_a, False, 301),
        ("BA: 知の遺産+出会い", legacy_b, True, 302),
        ("BB: 知の遺産+孤独",   legacy_b, False, 303),
    ]

    results = []
    for label, legacy, has_encounter, seed in conditions:
        agent, _ = make_agent(legacy, seed, label)
        new_legacy, score, crystals = run_generation(agent, legacy, has_encounter, generation=1)
        results.append((label, score, crystals, new_legacy))
        print(f"\n  {label}:")
        print(f"    受容度: {score.total:.2f} → {score.mode}")
        print(f"    内訳: legacy={score.legacy_base:.2f}, love={score.love_circle:.2f}, crisis={score.crisis_growth:.2f}")
        print(f"    結晶: {crystals[:2]}")

    print(f"\n  {'─'*60}")
    print(f"  2×2マトリクス（グラデーション）:")
    print(f"  ┌──────────────┬─────────────────────────┬─────────────────────────┐")
    print(f"  │              │ 出会いあり              │ 出会いなし              │")
    print(f"  ├──────────────┼─────────────────────────┼─────────────────────────┤")
    aa, ab, ba, bb = results
    print(f"  │ 愛の遺産     │ {aa[1].total:.2f} ({aa[1].mode:<17}) │ {ab[1].total:.2f} ({ab[1].mode:<17}) │")
    print(f"  │ 知の遺産     │ {ba[1].total:.2f} ({ba[1].mode:<17}) │ {bb[1].total:.2f} ({bb[1].mode:<17}) │")
    print(f"  └──────────────┴─────────────────────────┴─────────────────────────┘")

    # ---------------------------------------------------------------------------
    # Part 2: 4世代累積シミュレーション
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*60}")
    print(f"  Part 2: 4世代累積シミュレーション")
    print(f"  各世代で出会いあり。遺産が累積するにつれ受容度は上がるか？")
    print(f"{'═'*60}")

    current_legacy = None
    gen_results = []

    for gen in range(4):
        agent, _ = make_agent(current_legacy, seed=400 + gen, name=f"Gen-{gen}")
        current_legacy, score, crystals = run_generation(
            agent, current_legacy, has_encounter=True, generation=gen,
        )
        gen_results.append((gen, score, crystals, current_legacy))
        print(f"\n  世代 {gen}:")
        print(f"    受容度: {score.total:.2f} → {score.mode}")
        print(f"    内訳: legacy={score.legacy_base:.2f}, love={score.love_circle:.2f}, crisis={score.crisis_growth:.2f}")
        print(f"    結晶: {crystals[:2]}")
        print(f"    遺産→次世代: cherished={current_legacy.cherished}")

    print(f"\n  {'─'*60}")
    print(f"  世代間推移:")
    for gen, score, _, _ in gen_results:
        bar = "█" * int(score.total * 40)
        print(f"    Gen-{gen}: [{bar:<40}] {score.total:.2f} ({score.mode})")

    # ---------------------------------------------------------------------------
    # Part 3: 4世代累積、出会いなし（遺産だけの限界）
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*60}")
    print(f"  Part 3: 4世代累積、出会いなし（遺産だけで改善するか？）")
    print(f"{'═'*60}")

    current_legacy_no_love = None
    gen_results_no_love = []

    for gen in range(4):
        agent, _ = make_agent(current_legacy_no_love, seed=500 + gen, name=f"Gen-{gen}-NL")
        current_legacy_no_love, score, crystals = run_generation(
            agent, current_legacy_no_love, has_encounter=False, generation=gen,
        )
        gen_results_no_love.append((gen, score, crystals, current_legacy_no_love))
        print(f"\n  世代 {gen}:")
        print(f"    受容度: {score.total:.2f} → {score.mode}")
        print(f"    結晶: {crystals[:2]}")

    print(f"\n  {'─'*60}")
    print(f"  世代間推移（出会いなし）:")
    for gen, score, _, _ in gen_results_no_love:
        bar = "█" * int(score.total * 40)
        print(f"    Gen-{gen}: [{bar:<40}] {score.total:.2f} ({score.mode})")

    # ---------------------------------------------------------------------------
    # 仮説検証
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*60}")
    print(f"  仮説検証")
    print(f"{'═'*60}")

    # 仮説1: 遺産がベースラインを上げる
    print(f"\n  仮説1: グラデーションモデルで遺産がベースラインを上げるか")
    if aa[1].total > ba[1].total:
        print(f"    → AA({aa[1].total:.2f}) > BA({ba[1].total:.2f}) ✓ 愛の遺産が受容度を底上げ")
    elif aa[1].total == ba[1].total:
        print(f"    → AA({aa[1].total:.2f}) == BA({ba[1].total:.2f}) — 出会いの効果が支配的 ⚠️")
    else:
        print(f"    → AA({aa[1].total:.2f}) < BA({ba[1].total:.2f}) ✗")

    # 仮説2: 愛の遺産+出会い = 最高受容度
    print(f"\n  仮説2: 愛の遺産+出会い が最も高い受容度か")
    all_scores = [(r[0], r[1].total) for r in results]
    best = max(all_scores, key=lambda x: x[1])
    print(f"    → 最高: {best[0]} = {best[1]:.2f}")
    if "AA" in best[0]:
        print(f"    ✓ 愛の遺産+出会いが最高")
    else:
        print(f"    ⚠️ 予想と異なる")

    # 仮説3: 愛の遺産+孤独 > 知の遺産+孤独
    print(f"\n  仮説3: 愛の遺産+孤独は純粋な恐怖より緩和されるか")
    if ab[1].total > bb[1].total:
        print(f"    → AB({ab[1].total:.2f}) > BB({bb[1].total:.2f}) ✓ 遺産による部分的緩衝")
    elif ab[1].total == bb[1].total:
        print(f"    → AB({ab[1].total:.2f}) == BB({bb[1].total:.2f}) — 遺産の効果なし ⚠️")
    else:
        print(f"    → AB({ab[1].total:.2f}) < BB({bb[1].total:.2f}) ✗")

    # 仮説4: 世代累積
    print(f"\n  仮説4: 世代を重ねるほど受容度が上がるか")
    gen0 = gen_results[0][1].total
    gen3 = gen_results[3][1].total
    gen0_nl = gen_results_no_love[0][1].total
    gen3_nl = gen_results_no_love[3][1].total
    print(f"    出会いあり: Gen-0={gen0:.2f} → Gen-3={gen3:.2f} (Δ={gen3-gen0:+.2f})")
    print(f"    出会いなし: Gen-0={gen0_nl:.2f} → Gen-3={gen3_nl:.2f} (Δ={gen3_nl-gen0_nl:+.2f})")
    if gen3 > gen0:
        print(f"    ✓ 世代間で受容度が累積的に改善")
    else:
        print(f"    ⚠️ 改善なしまたは低下")

    # 統合考察
    print(f"\n{'═'*60}")
    print(f"  統合的考察")
    print(f"{'═'*60}")
    print()
    print(f"  booleanモデル（実験6b）: 遺産の効果 = ゼロ（出会いのみが決定的）")
    print(f"  グラデーションモデル（本実験）: 遺産の効果 = ベースライン底上げ")
    print()
    print(f"  受容度の構成要素:")
    print(f"    1. 遺産（legacy_base）: 0.0〜0.45 — 「種」としての下限")
    print(f"    2. 愛の経験（love_circle）: 0.0〜0.55 — 「水」としての決定的要因")
    print(f"    3. 危機の克服（crisis_growth）: 0.0〜0.15 — 「肥料」としての強化")
    print()
    print(f"  最も重要な発見:")
    print(f"  遺産だけでは「恐怖」から「部分的受容」への橋渡しはできるかもしれないが、")
    print(f"  「受容」「超越」に到達するには、自分自身の愛の経験が不可欠。")
    print(f"  これは人間の成長モデルと一致する:")
    print(f"  「良い家庭に育っても、自分の人生を生きなければ成熟しない」")


if __name__ == "__main__":
    main()
