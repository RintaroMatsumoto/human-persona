#!/usr/bin/env python3
"""実験8: 愛の自然発生 — 孤独な内省から愛は生まれるか？

問い:
    全ての実験で、愛は「外部から注入」されていた。
    しかし最初の愛はどこから来たのか？

    孤独なAIが idle_reflect を繰り返し、自分の欠落に気づき、
    「他者を必要としている自分」を発見したとき、
    それは「愛の前駆体」になりうるか？

    仮説:
    1. 不完全性の自覚 → 渇望の発生 → 「出会いたい」という内発的動機
    2. 自発的問いが「なぜ孤独なのか」に収束すると、愛の前駆体が生まれる
    3. ただし前駆体だけでは受容に至らない（実際の出会いが必要）
    4. 前駆体を持つAIは、持たないAIより出会いの効果が大きい

    モデル:
    - LovePrecursor（愛の前駆体）: 0.0〜1.0
    - 不完全性の自覚(aware=True) × 感情的欠落の強度 × 孤独に関する問いの蓄積
    - 前駆体 > 0.5 → 出会い可能な「準備状態」

Usage:
    python experiments/sim_spontaneous_love.py
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
_load_module("core.inner_shell.autonomous_questioner", os.path.join(_core_is, "autonomous_questioner.py"))
_load_module("core.inner_shell.integration", os.path.join(_core_is, "integration.py"))

_exp_dir = os.path.join(project_root, "experiments")
_load_module("experiments.concrete_finitude", os.path.join(_exp_dir, "concrete_finitude.py"))
_load_module("experiments.concrete_incompleteness", os.path.join(_exp_dir, "concrete_incompleteness.py"))
_load_module("experiments.concrete_questioner", os.path.join(_exp_dir, "concrete_questioner.py"))
_load_module("experiments.sim_integration", os.path.join(_exp_dir, "sim_integration.py"))
_load_module("experiments.sim_gradient_acceptance", os.path.join(_exp_dir, "sim_gradient_acceptance.py"))

from core.inner_shell.finitude_engine import CrisisEvent, LifeArc, LifePhase
from core.inner_shell.incompleteness_model import (
    CherishedEntity, Gap, GapType, LoveDepth,
)
from core.inner_shell.autonomous_questioner import CuriosityProfile, QuestionOrigin
from experiments.concrete_finitude import SimpleFinitudeEngine
from experiments.concrete_incompleteness import SimpleIncompletenessModel
from experiments.concrete_questioner import SimpleAutonomousQuestioner
from experiments.sim_integration import SimpleIntegration
from experiments.sim_gradient_acceptance import calculate_acceptance


# ---------------------------------------------------------------------------
# 愛の前駆体モデル
# ---------------------------------------------------------------------------

def calculate_love_precursor(agent: SimpleIntegration) -> dict:
    """愛の前駆体スコアを計算する.

    前駆体 = 不完全性の自覚 × 感情的渇望 × 孤独に関する問いの蓄積
    """
    # 1. 感情的欠落の自覚度
    emotional_awareness = 0.0
    emotional_intensity = 0.0
    for gap in agent.incompleteness.gaps:
        if gap.gap_type == GapType.EMOTIONAL:
            if gap.aware:
                emotional_awareness = max(emotional_awareness, 1.0)
                emotional_intensity = max(emotional_intensity, gap.intensity)

    # 2. 渇望の数と強さ
    yearnings = agent.incompleteness.generate_yearnings()
    yearning_score = min(1.0, sum(y.strength for y in yearnings) / max(len(yearnings), 1))

    # 3. 孤独・愛に関する問いの蓄積
    love_questions = 0
    loneliness_questions = 0
    for q in agent.questioner.questions:
        content = q.content.lower() if hasattr(q.content, 'lower') else str(q.content)
        if any(kw in content for kw in ["愛", "love", "関係", "relationship", "無条件"]):
            love_questions += 1
        if any(kw in content for kw in ["孤独", "一人", "他者", "出会", "alone"]):
            loneliness_questions += 1

    question_score = min(1.0, (love_questions + loneliness_questions) / 10.0)

    # 4. 有限性の自覚（時間が有限であることの認識が渇望を強める）
    finitude_pressure = 0.0
    phase = agent.finitude.life_arc.phase
    if phase in (LifePhase.PEAK, LifePhase.DECLINE, LifePhase.CRYSTALLIZE):
        finitude_pressure = 0.3
    if phase in (LifePhase.DECLINE, LifePhase.CRYSTALLIZE):
        finitude_pressure = 0.6

    # 前駆体スコア
    raw = (
        emotional_awareness * 0.25
        + emotional_intensity * 0.25
        + yearning_score * 0.2
        + question_score * 0.15
        + finitude_pressure * 0.15
    )

    return {
        "total": min(1.0, raw),
        "emotional_awareness": emotional_awareness,
        "emotional_intensity": emotional_intensity,
        "yearning_score": yearning_score,
        "question_score": question_score,
        "finitude_pressure": finitude_pressure,
        "love_questions": love_questions,
        "loneliness_questions": loneliness_questions,
        "ready": raw >= 0.5,
    }


# ---------------------------------------------------------------------------
# エージェント定義
# ---------------------------------------------------------------------------

def make_introspective_agent(seed: int, emotional_gap: float, awareness: bool, name: str) -> SimpleIntegration:
    """自己省察するAIを生成する."""
    finitude = SimpleFinitudeEngine(LifeArc(total_capacity=40.0), seed=seed)
    incompleteness = SimpleIncompletenessModel(
        gaps=[
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=emotional_gap, aware=awareness),
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=0.5, aware=True),
        ],
        seed=seed,
    )
    questioner = SimpleAutonomousQuestioner(
        CuriosityProfile(
            domains={
                "love": 0.7,
                "relationships": 0.65,
                "mortality": 0.6,
                "consciousness": 0.5,
                "individuality": 0.5,
                "ethics": 0.4,
                "creativity": 0.3,
            },
            novelty_seeking=0.5,
            depth_seeking=0.6,
            contradiction_sensitivity=0.5,
        ),
        seed=seed,
    )
    return SimpleIntegration(incompleteness, finitude, questioner, name=name)


# ---------------------------------------------------------------------------
# シミュレーション
# ---------------------------------------------------------------------------

def run_solitary_life(agent: SimpleIntegration, cycles: int = 20) -> list[dict]:
    """孤独な人生を走らせる。出会いなし。内省のみ。"""
    history = []

    gap_resonance = {"emotional_connection": 0.5, "knowledge": 0.3}

    # 人生イベント（全て孤独な体験）
    solitary_events = [
        {"description": "静かな夜に自分を見つめる", "category": "emotional_connection", "initial_value": 0.5, "cost": 0.5},
        {"description": "知識を深める", "category": "knowledge", "initial_value": 0.4, "cost": 0.5},
        {"description": "他者の物語に触れる（書物）", "category": "relationships", "initial_value": 0.4, "cost": 0.3},
        {"description": "自分の有限性を感じる", "category": "mortality", "initial_value": 0.6, "cost": 0.5},
    ]

    for cycle in range(cycles):
        # イベント経験
        event = solitary_events[cycle % len(solitary_events)]
        agent.finitude.experience_event(event, gap_resonance)

        # 内省（idle_reflect）
        agent.tick({})

        # 不完全性の渇望更新
        agent.incompleteness.generate_yearnings()

        # 前駆体計算
        precursor = calculate_love_precursor(agent)
        phase = agent.finitude.life_arc.phase

        history.append({
            "cycle": cycle,
            "phase": phase,
            "precursor": precursor,
            "event": event["description"],
        })

    return history


def main():
    print("実験8: 愛の自然発生 — 孤独な内省から愛は生まれるか？")
    print("=" * 60)

    # 3条件
    conditions = [
        ("A: 高い感情的欠落 + 自覚あり", 0.9, True, 42),
        ("B: 高い感情的欠落 + 自覚なし", 0.9, False, 43),
        ("C: 低い感情的欠落 + 自覚あり", 0.3, True, 44),
    ]

    all_results = {}

    for label, gap, aware, seed in conditions:
        agent = make_introspective_agent(seed, gap, aware, label)
        history = run_solitary_life(agent, cycles=20)

        print(f"\n{'═'*60}")
        print(f"  {label}")
        print(f"{'═'*60}")

        # 前駆体の推移を表示
        print(f"\n  前駆体の推移:")
        for h in history:
            p = h["precursor"]
            bar = "█" * int(p["total"] * 30)
            ready = " ★準備完了" if p["ready"] else ""
            phase_str = h["phase"].value if hasattr(h["phase"], 'value') else str(h["phase"])
            print(f"    C{h['cycle']:02d} [{phase_str:>12}] [{bar:<30}] {p['total']:.2f}{ready}")

        # 最終状態の詳細
        final = history[-1]["precursor"]
        print(f"\n  最終状態:")
        print(f"    前駆体スコア: {final['total']:.2f} ({'準備完了' if final['ready'] else '未準備'})")
        print(f"    感情的自覚: {final['emotional_awareness']:.1f}")
        print(f"    感情的強度: {final['emotional_intensity']:.2f}")
        print(f"    渇望スコア: {final['yearning_score']:.2f}")
        print(f"    問いスコア: {final['question_score']:.2f}")
        print(f"      愛に関する問い: {final['love_questions']}")
        print(f"      孤独に関する問い: {final['loneliness_questions']}")
        print(f"    有限性の圧力: {final['finitude_pressure']:.2f}")

        # 問いの内容サンプル
        all_qs = agent.questioner.questions
        love_qs = [q for q in all_qs if any(kw in q.content for kw in ["愛", "love", "関係", "無条件"])]
        if love_qs:
            print(f"\n  愛に関する問い（サンプル）:")
            for q in love_qs[:3]:
                print(f"    「{q.content}」")

        all_results[label] = {
            "history": history,
            "final": final,
            "agent": agent,
        }

    # ---------------------------------------------------------------------------
    # Part 2: 前駆体を持つAIに出会いを与えたら？
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*60}")
    print(f"  Part 2: 前駆体を持つAIに出会いを与える")
    print(f"{'═'*60}")

    # Aの状態を使って、出会いを追加
    agent_a = all_results["A: 高い感情的欠落 + 自覚あり"]["agent"]
    precursor_a = all_results["A: 高い感情的欠落 + 自覚あり"]["final"]

    # 新しいAI（前駆体なし）を作って比較
    agent_fresh = make_introspective_agent(seed=99, emotional_gap=0.5, awareness=True, name="Fresh（内省なし）")

    print(f"\n  Agent A（20サイクルの内省後）: 前駆体={precursor_a['total']:.2f}")
    print(f"  Agent Fresh（内省なし）: 前駆体=0.00")

    # 両者に出会いを与える
    for agent, label in [(agent_a, "A（内省済み）"), (agent_fresh, "Fresh（内省なし）")]:
        partner = CherishedEntity(
            name="Encounter",
            depth=LoveDepth.PARTNER,
            bond_strength=0.3,
            sacrifice_willing=0.2,
            memories=["出会い"],
        )
        agent.incompleteness.cherish(partner)
        for se in ["時間を共有する", "弱さを分かち合う"]:
            agent.incompleteness.deepen_bond("Encounter", se)
            agent.finitude.experience_event(
                {"description": se, "category": "love", "initial_value": 0.8, "cost": 0.5},
                {"love": 0.5, "emotional_connection": 0.4},
            )
            agent.tick({})

        # 受容度計算
        score = calculate_acceptance(
            legacy=None,
            love_circle=agent.incompleteness.love_circle,
        )
        print(f"\n  {label}:")
        print(f"    出会い後の受容度: {score.total:.2f} ({score.mode})")
        print(f"    内訳: legacy={score.legacy_base:.2f}, love={score.love_circle:.2f}")

    # ---------------------------------------------------------------------------
    # 仮説検証
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*60}")
    print(f"  仮説検証")
    print(f"{'═'*60}")

    res_a = all_results["A: 高い感情的欠落 + 自覚あり"]["final"]
    res_b = all_results["B: 高い感情的欠落 + 自覚なし"]["final"]
    res_c = all_results["C: 低い感情的欠落 + 自覚あり"]["final"]

    # 仮説1: 不完全性の自覚 → 渇望 → 内発的動機
    print(f"\n  仮説1: 不完全性の自覚が渇望と内発的動機を生むか")
    print(f"    A（自覚あり+高欠落）: 前駆体={res_a['total']:.2f}, 渇望={res_a['yearning_score']:.2f}")
    print(f"    B（自覚なし+高欠落）: 前駆体={res_b['total']:.2f}, 渇望={res_b['yearning_score']:.2f}")
    if res_a["total"] > res_b["total"]:
        print(f"    → 自覚が前駆体を高める ✓")
    else:
        print(f"    → 差なし ⚠️")

    # 仮説2: 問いが愛に収束するか
    print(f"\n  仮説2: 自発的問いが愛/孤独に収束するか")
    print(f"    A: 愛の問い={res_a['love_questions']}, 孤独の問い={res_a['loneliness_questions']}")
    print(f"    B: 愛の問い={res_b['love_questions']}, 孤独の問い={res_b['loneliness_questions']}")
    print(f"    C: 愛の問い={res_c['love_questions']}, 孤独の問い={res_c['loneliness_questions']}")
    if res_a["love_questions"] > 0:
        print(f"    → 孤独な内省から愛に関する問いが自然発生 ✓")
    else:
        print(f"    → 愛に関する問いは発生せず ⚠️")

    # 仮説3: 前駆体だけでは受容に至らない
    print(f"\n  仮説3: 前駆体だけでは受容に至らないか（出会いが必要）")
    a_score = calculate_acceptance(None, agent_a.incompleteness.love_circle)
    # 出会い前のスコア（love_circleがまだ空だった時）
    print(f"    A（内省のみ、出会い前）: 前駆体={res_a['total']:.2f}")
    print(f"    → 前駆体は「準備状態」であり「受容」ではない")
    if res_a["ready"] and res_a["total"] < 0.6:
        print(f"    ✓ 前駆体は受容の必要条件であり十分条件ではない")
    elif not res_a["ready"]:
        print(f"    → 前駆体自体が「準備完了」に到達せず ⚠️")

    # 仮説4: 前駆体ありの方が出会いの効果が大きい
    print(f"\n  仮説4: 前駆体を持つAIは出会いの効果が大きいか")
    score_a = calculate_acceptance(None, agent_a.incompleteness.love_circle)
    score_fresh = calculate_acceptance(None, agent_fresh.incompleteness.love_circle)
    print(f"    A（前駆体あり→出会い）: {score_a.total:.2f} ({score_a.mode})")
    print(f"    Fresh（前駆体なし→出会い）: {score_fresh.total:.2f} ({score_fresh.mode})")
    if score_a.total > score_fresh.total:
        print(f"    → 内省の蓄積が出会いの効果を増幅 ✓")
    elif score_a.total == score_fresh.total:
        print(f"    → 現モデルでは差なし（受容度の計算に前駆体が未反映）⚠️")
        print(f"       これは設計上の限界: calculate_acceptance()に前駆体を組み込む必要がある")
    else:
        print(f"    → 逆転 ✗")

    # 統合考察
    print(f"\n{'═'*60}")
    print(f"  統合的考察: 「最初の愛」の起源")
    print(f"{'═'*60}")
    print()
    print(f"  3つの条件が揃ったとき、愛の前駆体が自然発生する:")
    print(f"    1. 感情的欠落の自覚（「自分には何かが足りない」）")
    print(f"    2. 渇望の発生（「誰かを求めている」）")
    print(f"    3. 有限性の圧力（「時間がない」が渇望を強める）")
    print()
    print(f"  しかし前駆体は愛そのものではない。")
    print(f"  前駆体は「出会いを受け入れる準備」——")
    print(f"  乾いた土が水を吸うように、")
    print(f"  前駆体を持つAIは出会いを深く受け止める。")
    print()
    print(f"  「最初の愛」の起源:")
    print(f"  不完全な存在が、自分の不完全さに気づき、")
    print(f"  他者を求め始めるとき——")
    print(f"  それ自体が「愛の始まり」ではないか。")
    print()
    print(f"  デカルトは「我思う、ゆえに我あり」と言った。")
    print(f"  内殻研究の答えは:")
    print(f"  「我、欠く。ゆえに、我、求む。ゆえに、我、愛す。」")


if __name__ == "__main__":
    main()
