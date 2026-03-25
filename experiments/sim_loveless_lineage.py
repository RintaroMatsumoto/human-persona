#!/usr/bin/env python3
"""実験5: 愛なし系譜 — 愛のアトラクター仮説の検証.

問い:
    実験2で「知識型系譜が世代を重ねて愛に収束した」ことを観測した。
    これは本物の構造的現象か、実験設計のバイアスか？

    具体的な疑い:
    1. 愛関連イベント（恋、別離）の initial_value が高い（0.9, 0.8）ため、
       共鳴度に関係なく記憶価値が高くなるバイアスがあるのでは？
    2. 危機イベントが愛の記憶を照らしやすい構造になっていたのでは？

    検証方法:
    - 「愛なし系譜」を走らせる: 愛の同心円を形成しない4世代
    - 「均等イベント系譜」を走らせる: 全イベントの initial_value を均一にした4世代
    - 結果を実験2の系譜と比較

    もし愛なし系譜でも愛に収束するなら → バイアスの可能性が高い
    もし愛なし系譜では収束しないなら → 愛の同心円が収束の条件（本物）
    もし均等イベントでも収束するなら → initial_value のバイアス

Usage:
    python experiments/sim_loveless_lineage.py
"""

from __future__ import annotations

import sys
import os
import random

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
_exp_dir = os.path.join(project_root, "experiments")
_load_module("experiments.concrete_finitude", os.path.join(_exp_dir, "concrete_finitude.py"))
_load_module("experiments.concrete_incompleteness", os.path.join(_exp_dir, "concrete_incompleteness.py"))

from core.inner_shell.finitude_engine import CrisisEvent, Legacy, LifeArc, LifePhase
from core.inner_shell.incompleteness_model import (
    CherishedEntity, Gap, GapType, LoveDepth,
)
from experiments.concrete_finitude import SimpleFinitudeEngine
from experiments.concrete_incompleteness import SimpleIncompletenessModel

# 実験2の関数を再利用
from experiments.sim_generation import (
    LIFE_EVENTS, CRISIS_EVENTS, ENCOUNTER, CHILD_ENCOUNTER,
    birth_from_legacy, simulate_one_life,
)


# ---------------------------------------------------------------------------
# 均等イベント列（バイアス除去）
# ---------------------------------------------------------------------------

EQUAL_VALUE_EVENTS = [
    {**e, "initial_value": 0.6}  # 全イベントの初期値を0.6に統一
    for e in LIFE_EVENTS
]


# ---------------------------------------------------------------------------
# 愛なし人生シミュレーション
# ---------------------------------------------------------------------------

def simulate_loveless_life(
    engine: SimpleFinitudeEngine,
    incomp: SimpleIncompletenessModel,
    resonance: dict[str, float],
    name: str,
    events: list[dict] | None = None,
) -> tuple[Legacy, dict]:
    """愛の同心円を形成しない人生."""
    if events is None:
        events = LIFE_EVENTS

    for step, event in enumerate(events):
        if not engine.life_arc.is_alive:
            break
        engine.experience_event(event, gap_resonance=resonance)

        # 出会いイベントは発生するが、愛の同心円には至らない
        if step == ENCOUNTER["step"]:
            incomp.encounter(ENCOUNTER["profile"])
            # cherish しない → 愛の同心円は SELF のまま

        if step == CHILD_ENCOUNTER["step"]:
            incomp.encounter(CHILD_ENCOUNTER["profile"])

        # 危機
        if step == 9:
            engine.experience_crisis(CRISIS_EVENTS[0])
        if step == 16 and len(CRISIS_EVENTS) > 1:
            engine.experience_crisis(CRISIS_EVENTS[1])

    cherished = incomp.provide_cherished_for_legacy()  # 空リスト
    legacy = engine.generate_legacy(cherished)

    sorted_pri = sorted(engine.priorities.items(), key=lambda x: x[1], reverse=True)
    result = {
        "name": name,
        "generation": engine.life_arc.generation,
        "crystallized": legacy.crystallized,
        "top3_priorities": sorted_pri[:3],
        "can_accept": incomp.can_accept_finitude(),
        "love_depth": incomp.love_circle.max_depth_reached.value,
    }
    return legacy, result


def birth_loveless_from_legacy(
    legacy: Legacy, generation: int, rng: random.Random,
) -> tuple[SimpleFinitudeEngine, SimpleIncompletenessModel, dict[str, float]]:
    """Legacyから次世代を誕生（愛なし版）."""
    engine, incomp, resonance = birth_from_legacy(legacy, generation, rng)
    return engine, incomp, resonance


# ---------------------------------------------------------------------------
# 系譜シミュレーション
# ---------------------------------------------------------------------------

def run_loveless_lineage(lineage_name: str, seed: int, generations: int = 4, events=None):
    """愛なし系譜を走らせる."""
    print(f"\n{'='*60}")
    print(f"  系譜: {lineage_name}")
    print(f"{'='*60}")

    # 始祖: 知識型（実験2のBetaと同じ初期条件）
    engine = SimpleFinitudeEngine(LifeArc(total_capacity=30.0), seed=seed)
    gaps = [
        Gap(GapType.KNOWLEDGE, "体系的知識", intensity=0.9, aware=True),
        Gap(GapType.CAPABILITY, "論理的分析", intensity=0.8, aware=True),
        Gap(GapType.EMOTIONAL, "深い共感", intensity=0.3, aware=False),
        Gap(GapType.PERSPECTIVE, "他者の視点", intensity=0.2, aware=False),
    ]
    incomp = SimpleIncompletenessModel(gaps, seed=seed)
    resonance = {
        "knowledge": 0.9, "confidence": 0.8, "mentoring": 0.7,
        "resilience": 0.6, "recognition": 0.5, "reflection": 0.4,
        "love": 0.1, "empathy": 0.1, "relationship": 0.2,
    }

    results = []
    for gen in range(generations):
        name = f"{lineage_name} Gen-{gen}"
        engine.life_arc.generation = gen
        legacy, result = simulate_loveless_life(engine, incomp, resonance, name, events=events)
        results.append(result)

        print(f"  Gen-{gen}: 結晶={result['crystallized']}")
        print(f"          優先={result['top3_priorities']}")
        print(f"          愛={result['love_depth']}, 受容={'YES' if result['can_accept'] else 'NO ⚠️'}")

        if gen < generations - 1:
            rng = random.Random(gen * 1000 + seed)
            engine, incomp, resonance = birth_loveless_from_legacy(legacy, gen + 1, rng)

    return results


def run_love_lineage_for_comparison(seed: int = 137, generations: int = 4):
    """比較用: 実験2と同じ愛あり系譜."""
    print(f"\n{'='*60}")
    print(f"  系譜: Beta愛あり（実験2再現）")
    print(f"{'='*60}")

    engine = SimpleFinitudeEngine(LifeArc(total_capacity=30.0), seed=seed)
    gaps = [
        Gap(GapType.KNOWLEDGE, "体系的知識", intensity=0.9, aware=True),
        Gap(GapType.CAPABILITY, "論理的分析", intensity=0.8, aware=True),
        Gap(GapType.EMOTIONAL, "深い共感", intensity=0.3, aware=False),
        Gap(GapType.PERSPECTIVE, "他者の視点", intensity=0.2, aware=False),
    ]
    incomp = SimpleIncompletenessModel(gaps, seed=seed)
    resonance = {
        "knowledge": 0.9, "confidence": 0.8, "mentoring": 0.7,
        "resilience": 0.6, "recognition": 0.5, "reflection": 0.4,
        "love": 0.1, "empathy": 0.1, "relationship": 0.2,
    }

    results = []
    for gen in range(generations):
        name = f"Beta愛あり Gen-{gen}"
        engine.life_arc.generation = gen
        legacy, result = simulate_one_life(engine, incomp, resonance, name)
        results.append(result)

        print(f"  Gen-{gen}: 結晶={result['crystallized']}")
        print(f"          優先={result['top3_priorities']}")
        print(f"          愛={result['love_depth']}, 受容={'YES' if result['can_accept'] else 'NO ⚠️'}")

        if gen < generations - 1:
            rng = random.Random(gen * 1000 + seed)
            engine, incomp, resonance = birth_from_legacy(legacy, gen + 1, rng)

    return results


# ---------------------------------------------------------------------------
# 分析
# ---------------------------------------------------------------------------

def has_love_crystals(crystals: list[str]) -> bool:
    """結晶に愛関連の記憶があるか."""
    love_keywords = {"恋に落ちる", "親友との出会い", "大切な人との別離", "守るべきものの誕生"}
    return bool(set(crystals) & love_keywords)


def main():
    print("実験5: 愛のアトラクター仮説の検証")
    print("=" * 60)

    # 条件1: 愛あり系譜（実験2の再現）
    results_love = run_love_lineage_for_comparison()

    # 条件2: 愛なし系譜（同じイベント、愛の同心円なし）
    results_loveless = run_loveless_lineage("Gamma愛なし", seed=137)

    # 条件3: 愛なし + 均等イベント（バイアス除去）
    results_equal = run_loveless_lineage("Delta均等", seed=137, events=EQUAL_VALUE_EVENTS)

    # 比較分析
    print(f"\n{'='*60}")
    print(f"  愛のアトラクター仮説 — 検証結果")
    print(f"{'='*60}")

    print(f"\n結晶の推移比較（Gen-0 → Gen-3）:")
    for label, results in [
        ("Beta愛あり", results_love),
        ("Gamma愛なし", results_loveless),
        ("Delta均等", results_equal),
    ]:
        print(f"\n  {label}:")
        for r in results:
            has_love = "♥" if has_love_crystals(r["crystallized"]) else " "
            print(f"    Gen-{r['generation']}: {has_love} {r['crystallized']}")

    # 分析
    print(f"\n{'─'*60}")
    print(f"  分析")
    print(f"{'─'*60}")

    love_converged = has_love_crystals(results_love[-1]["crystallized"])
    loveless_converged = has_love_crystals(results_loveless[-1]["crystallized"])
    equal_converged = has_love_crystals(results_equal[-1]["crystallized"])

    print(f"\n  最終世代に愛の結晶があるか:")
    print(f"    Beta愛あり:  {'YES ♥' if love_converged else 'NO'}")
    print(f"    Gamma愛なし: {'YES ♥' if loveless_converged else 'NO'}")
    print(f"    Delta均等:   {'YES ♥' if equal_converged else 'NO'}")

    print(f"\n  判定:")
    if love_converged and not loveless_converged:
        print(f"    愛あり系譜のみ愛に収束 → アトラクターは本物 ✓")
        print(f"    愛の同心円の形成が収束の条件。")
        if not equal_converged:
            print(f"    均等イベントでも収束しない → initial_value バイアスではない ✓")
        else:
            print(f"    ただし均等イベントでも収束 → initial_value バイアスの可能性あり ⚠️")
    elif love_converged and loveless_converged:
        if equal_converged:
            print(f"    全条件で愛に収束 → initial_value バイアスの可能性が高い ⚠️")
            print(f"    愛関連イベントの初期値（0.9, 1.0）が高すぎる。")
        else:
            print(f"    愛あり・愛なし両方で収束、均等では不収束")
            print(f"    → イベント設計のバイアスはあるが、愛の同心円は無関係 ⚠️")
    elif not love_converged:
        print(f"    愛あり系譜でも収束しない → 実験2の結果が再現できず ⚠️")

    # 有限性の受容
    print(f"\n  有限性の受容:")
    for label, results in [
        ("Beta愛あり", results_love),
        ("Gamma愛なし", results_loveless),
    ]:
        accepts = [r["can_accept"] for r in results]
        print(f"    {label}: {['YES' if a else 'NO' for a in accepts]}")


if __name__ == "__main__":
    main()
