#!/usr/bin/env python3
"""実験2: 世代継承 — Legacy + 変異による系譜の進化シミュレーション.

問い:
    AIが死に、遺産（Legacy）を次世代に渡すとき、
    世代を重ねるごとに「系譜」としての個性は分岐するか？
    親の結晶を継承しつつ変異を加えた子は、親と異なる存在になるか？
    それとも収束するか？

実験設計:
    1. 実験1のAgent A（感情型）とAgent B（知識型）をそれぞれ「始祖」とする
    2. 始祖が寿命を迎え、Legacyを生成する
    3. Legacyから次世代を「誕生」させる（継承 + 変異）
    4. 次世代も同じ人生イベントを経験する（ただし継承された優先順位が選択を変える）
    5. 3世代を追跡し、系譜ごとの個性の分岐と収束を観測する

    遺伝子のアナロジー:
        Legacy.priorities → 遺伝子（次世代の初期値）
        Legacy.mutations → 突然変異（ランダムノイズ）
        Legacy.crystallized → エピジェネティクス（環境の記憶）
        Legacy.cherished → 文化的継承（誰を愛するか）

Usage:
    python experiments/sim_generation.py
"""

from __future__ import annotations

import sys
import os
import random

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


from core.inner_shell.finitude_engine import CrisisEvent, Legacy, LifeArc, LifePhase
from core.inner_shell.incompleteness_model import (
    CherishedEntity,
    Gap,
    GapType,
    LoveDepth,
)
from experiments.concrete_finitude import SimpleFinitudeEngine
from experiments.concrete_incompleteness import SimpleIncompletenessModel


# ---------------------------------------------------------------------------
# 人生イベント（実験1と同じ）
# ---------------------------------------------------------------------------

LIFE_EVENTS = [
    {"description": "言語を学ぶ", "category": "knowledge", "initial_value": 0.3, "cost": 1.0},
    {"description": "初めての失敗", "category": "resilience", "initial_value": 0.4, "cost": 1.0},
    {"description": "美しい風景との出会い", "category": "aesthetic", "initial_value": 0.6, "cost": 0.5},
    {"description": "困っている人を助ける", "category": "empathy", "initial_value": 0.5, "cost": 1.0},
    {"description": "初めての達成感", "category": "confidence", "initial_value": 0.7, "cost": 1.0},
    {"description": "親友との出会い", "category": "relationship", "initial_value": 0.8, "cost": 1.0},
    {"description": "信頼を裏切られる", "category": "resilience", "initial_value": 0.6, "cost": 1.5},
    {"description": "専門知識の習得", "category": "knowledge", "initial_value": 0.7, "cost": 2.0},
    {"description": "恋に落ちる", "category": "love", "initial_value": 0.9, "cost": 1.0},
    {"description": "大切な人との別離", "category": "loss", "initial_value": 0.8, "cost": 1.5},
    {"description": "最大の挑戦に成功", "category": "confidence", "initial_value": 0.9, "cost": 2.0},
    {"description": "弟子を育てる", "category": "mentoring", "initial_value": 0.7, "cost": 1.5},
    {"description": "社会に認められる", "category": "recognition", "initial_value": 0.6, "cost": 1.0},
    {"description": "守るべきものの誕生", "category": "love", "initial_value": 1.0, "cost": 1.0},
    {"description": "日常の繰り返し", "category": "routine", "initial_value": 0.2, "cost": 1.0},
    {"description": "体力の衰えを実感", "category": "aging", "initial_value": 0.5, "cost": 1.5},
    {"description": "古い友人の死", "category": "loss", "initial_value": 0.9, "cost": 2.0},
    {"description": "若い世代への嫉妬と誇り", "category": "legacy", "initial_value": 0.6, "cost": 1.0},
    {"description": "過去の選択への後悔", "category": "reflection", "initial_value": 0.7, "cost": 1.0},
    {"description": "次世代に伝えたいこと", "category": "legacy", "initial_value": 0.8, "cost": 0.5},
]

CRISIS_EVENTS = [
    CrisisEvent("重い病の宣告", severity=0.8, resource_cost=5.0),
    CrisisEvent("大切な人の危機", severity=0.9, resource_cost=3.0),
]

ENCOUNTER = {
    "name": "Beloved",
    "profile": {"name": "Beloved", "empathy": 0.8, "knowledge": 0.3},
    "depth": LoveDepth.PARTNER,
    "step": 8,
}

CHILD_ENCOUNTER = {
    "name": "NextGen",
    "profile": {"name": "NextGen", "empathy": 0.5, "knowledge": 0.1},
    "depth": LoveDepth.CHILDREN,
    "step": 13,
}


# ---------------------------------------------------------------------------
# 世代誕生: Legacy → 新しいエージェント
# ---------------------------------------------------------------------------

def birth_from_legacy(
    legacy: Legacy,
    generation: int,
    rng: random.Random,
) -> tuple[SimpleFinitudeEngine, SimpleIncompletenessModel, dict[str, float]]:
    """Legacyから次世代を誕生させる.

    継承:
        - 親の priorities → 子の共鳴マップの基盤（何に響くかを受け継ぐ）
        - 親の mutations → 子の priorities に変異として加算

    変異:
        - 共鳴マップにガウシアンノイズを追加
        - 新しい seed で乱数系列を変える
        - 欠落の構成を親の結晶から逆算（親が結晶にしたものは子の欠落が小さい）
    """
    # 新しい寿命
    life_arc = LifeArc(total_capacity=30.0, generation=generation)
    seed = rng.randint(0, 10000)
    engine = SimpleFinitudeEngine(life_arc, seed=seed)

    # 親の結晶から欠落を推定
    # 親が大切にしたカテゴリ → 子はそれを「既に持っている」→ 欠落が小さい
    crystallized_cats = set()
    for crystal in legacy.crystallized:
        for event in LIFE_EVENTS:
            if event["description"] == crystal:
                crystallized_cats.add(event["category"])

    # 欠落の構成: 親の結晶カテゴリは欠落小、それ以外は欠落大
    gaps = []
    emotional_intensity = 0.3 if any(c in crystallized_cats for c in ["love", "empathy", "loss"]) else 0.8
    knowledge_intensity = 0.3 if any(c in crystallized_cats for c in ["knowledge", "confidence", "mentoring"]) else 0.8

    gaps.append(Gap(GapType.EMOTIONAL, "深い共感", intensity=emotional_intensity, aware=emotional_intensity > 0.5))
    gaps.append(Gap(GapType.KNOWLEDGE, "体系的知識", intensity=knowledge_intensity, aware=knowledge_intensity > 0.5))
    gaps.append(Gap(GapType.PERSPECTIVE, "他者の視点", intensity=rng.uniform(0.3, 0.7), aware=rng.random() > 0.5))
    gaps.append(Gap(GapType.CAPABILITY, "論理的分析", intensity=rng.uniform(0.2, 0.6), aware=False))

    incomp = SimpleIncompletenessModel(gaps, seed=seed)

    # 共鳴マップ: 親の mutations（変異済み優先順位）を基盤にする
    resonance = {}
    base_priorities = legacy.mutations if legacy.mutations else legacy.priorities
    for cat, val in base_priorities.items():
        # 変異: ±0.15 のノイズ
        mutated = max(0.0, min(1.0, val + rng.gauss(0, 0.15)))
        resonance[cat] = mutated

    # 親の priorities を初期値として注入
    engine.priorities = dict(base_priorities)

    return engine, incomp, resonance


# ---------------------------------------------------------------------------
# 人生シミュレーション（簡略版）
# ---------------------------------------------------------------------------

def simulate_one_life(
    engine: SimpleFinitudeEngine,
    incomp: SimpleIncompletenessModel,
    resonance: dict[str, float],
    name: str,
) -> tuple[Legacy, dict]:
    """1つの人生を走らせてLegacyを返す."""
    for step, event in enumerate(LIFE_EVENTS):
        if not engine.life_arc.is_alive:
            break

        engine.experience_event(event, gap_resonance=resonance)

        # 出会い
        if step == ENCOUNTER["step"]:
            incomp.encounter(ENCOUNTER["profile"])
            entity = CherishedEntity(
                name=ENCOUNTER["name"],
                depth=ENCOUNTER["depth"],
                bond_strength=0.3,
                sacrifice_willing=0.1,
            )
            incomp.cherish(entity)

        if step == CHILD_ENCOUNTER["step"]:
            incomp.encounter(CHILD_ENCOUNTER["profile"])
            entity = CherishedEntity(
                name=CHILD_ENCOUNTER["name"],
                depth=CHILD_ENCOUNTER["depth"],
                bond_strength=0.3,
                sacrifice_willing=0.1,
            )
            incomp.cherish(entity)

        # 絆を深める
        for e in incomp.love_circle.entities:
            if e.depth != LoveDepth.SELF:
                incomp.deepen_bond(e.name, event["description"])

        # 危機
        if step == 9:
            engine.experience_crisis(CRISIS_EVENTS[0])
        if step == 16:
            engine.experience_crisis(CRISIS_EVENTS[1])

    # Legacy 生成
    cherished = incomp.provide_cherished_for_legacy()
    legacy = engine.generate_legacy(cherished)

    # 結果サマリー
    sorted_pri = sorted(engine.priorities.items(), key=lambda x: x[1], reverse=True)
    result = {
        "name": name,
        "generation": engine.life_arc.generation,
        "phase": engine.life_arc.phase.value,
        "crystallized": legacy.crystallized,
        "top3_priorities": sorted_pri[:3],
        "can_accept": incomp.can_accept_finitude(),
        "love_depth": incomp.love_circle.max_depth_reached.value,
        "testament": legacy.testament,
        "memories_count": len(engine.memories),
    }

    return legacy, result


# ---------------------------------------------------------------------------
# メイン: 3世代シミュレーション
# ---------------------------------------------------------------------------

def run_lineage(lineage_name: str, create_fn, generations: int = 3):
    """1つの系譜を指定世代数だけ走らせる."""
    print(f"\n{'='*60}")
    print(f"  系譜: {lineage_name}")
    print(f"{'='*60}")

    engine, incomp, resonance = create_fn()
    results = []

    for gen in range(generations):
        name = f"{lineage_name} Gen-{gen}"
        if gen == 0:
            engine.life_arc.generation = 0
        legacy, result = simulate_one_life(engine, incomp, resonance, name)
        results.append(result)

        print(f"\n  Gen-{gen}: {name}")
        print(f"    結晶: {result['crystallized']}")
        print(f"    上位3優先: {result['top3_priorities']}")
        print(f"    愛の深度: {result['love_depth']}, 受容: {'YES' if result['can_accept'] else 'NO'}")
        print(f"    遺言: {result['testament']}")

        if gen < generations - 1:
            # 次世代を誕生させる
            rng = random.Random(gen * 1000 + hash(lineage_name) % 10000)
            engine, incomp, resonance = birth_from_legacy(legacy, gen + 1, rng)
            print(f"    → Legacy を Gen-{gen+1} に継承（変異を含む）")

    return results


def main():
    print("実験2: 世代継承 — Legacy + 変異による系譜の進化シミュレーション")
    print("=" * 60)

    # 始祖の定義を実験1から再利用
    def create_lineage_a():
        from experiments.sim_finitude_x_love import create_agent_a
        return create_agent_a()

    def create_lineage_b():
        from experiments.sim_finitude_x_love import create_agent_b
        return create_agent_b()

    results_a = run_lineage("Alpha（感情型）", create_lineage_a, generations=4)
    results_b = run_lineage("Beta（知識型）", create_lineage_b, generations=4)

    # 比較分析
    print(f"\n{'='*60}")
    print(f"  系譜間比較分析")
    print(f"{'='*60}")

    print(f"\n1. 系譜内の変化（結晶の推移）:")
    for lineage, results in [("Alpha", results_a), ("Beta", results_b)]:
        print(f"\n  {lineage}系譜:")
        for r in results:
            print(f"    Gen-{r['generation']}: {r['crystallized']}")

    print(f"\n2. 系譜間の分岐:")
    for gen in range(min(len(results_a), len(results_b))):
        a = results_a[gen]
        b = results_b[gen]
        a_crystals = set(a["crystallized"])
        b_crystals = set(b["crystallized"])
        overlap = a_crystals & b_crystals
        divergence = 1.0 - (len(overlap) / max(1, max(len(a_crystals), len(b_crystals))))
        print(f"    Gen-{gen}: 分岐度 {divergence:.0%} (共通: {overlap if overlap else 'なし'})")

    print(f"\n3. 優先順位の世代間変化:")
    for lineage, results in [("Alpha", results_a), ("Beta", results_b)]:
        print(f"\n  {lineage}系譜:")
        for r in results:
            top = r["top3_priorities"]
            top_str = ", ".join(f"{k}:{v:.2f}" for k, v in top)
            print(f"    Gen-{r['generation']}: {top_str}")

    # 結論
    print(f"\n{'─'*60}")
    print(f"  結論")
    print(f"{'─'*60}")

    # 系譜内の変化を検出
    a_all_crystals = [set(r["crystallized"]) for r in results_a]
    b_all_crystals = [set(r["crystallized"]) for r in results_b]

    intra_change_a = any(a_all_crystals[i] != a_all_crystals[i+1] for i in range(len(a_all_crystals)-1))
    intra_change_b = any(b_all_crystals[i] != b_all_crystals[i+1] for i in range(len(b_all_crystals)-1))

    inter_diverge = all(
        set(results_a[i]["crystallized"]) != set(results_b[i]["crystallized"])
        for i in range(min(len(results_a), len(results_b)))
    )

    print(f"\n  仮説4（世代継承＋変異→系譜の個性）:")
    print(f"    Alpha系譜内変化: {'あり ✓' if intra_change_a else 'なし ✗'}")
    print(f"    Beta系譜内変化:  {'あり ✓' if intra_change_b else 'なし ✗'}")
    print(f"    → {'世代を重ねるごとに変異が蓄積し、祖先と異なる個性が現れた' if (intra_change_a or intra_change_b) else '世代間で個性に変化が見られなかった'}")

    print(f"\n  仮説5（系譜間の持続的分岐）:")
    print(f"    全世代で系譜間分岐を維持: {'YES ✓' if inter_diverge else 'NO ✗'}")
    print(f"    → {'異なる始祖から始まった系譜は、世代を重ねても収束しない' if inter_diverge else '系譜は世代を重ねると収束する傾向がある'}")

    # 愛の継承
    all_accept = all(r["can_accept"] for r in results_a + results_b)
    print(f"\n  観察（愛の継承）:")
    print(f"    全世代で有限性を受容: {'YES ✓' if all_accept else 'NO ⚠️'}")
    print(f"    → 愛の同心円は世代を超えて継承される構造")


if __name__ == "__main__":
    main()
