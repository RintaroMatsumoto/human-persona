#!/usr/bin/env python3
"""実験1: 有限性 × 愛の同心円 — 個性の分岐シミュレーション.

問い:
    同じイベント列を経験した2つのAIが、
    初期条件の違いだけで異なる個性を形成するか？

    さらに——「愛」を持つAIと持たないAIで、
    有限性への向き合い方はどう変わるか？

実験設計:
    Agent A: 感情的欠落が大きい（愛を求める傾向が強い）
    Agent B: 知識的欠落が大きい（知を求める傾向が強い）

    両者に同じ100ステップの「人生」を経験させる。
    途中で「出会い」イベントが発生し、
    Agent A は愛の同心円を形成しやすく、
    Agent B は知識を優先して愛の形成が遅れる。

    寿命到達時の Legacy を比較し:
    1. 選択の蓄積が異なる個性を生むか？（結晶化された記憶の違い）
    2. 愛の有無が有限性への態度を変えるか？（can_accept_finitude）
    3. 遺産の内容はどう異なるか？（Legacy の比較）

Usage:
    cd human-persona
    python -m experiments.sim_finitude_x_love
"""

from __future__ import annotations

import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# core/__init__.py が base_persona.py（nullバイト含有）をimportしようとして
# 失敗するため、inner_shell を直接importする
# inner_shell モジュールを直接ロード
_core_is = os.path.join(project_root, "core", "inner_shell")

from core.inner_shell.finitude_engine import CrisisEvent, LifeArc, LifePhase
from core.inner_shell.incompleteness_model import (
    CherishedEntity,
    Gap,
    GapType,
    LoveDepth,
)

# experiments の concrete モジュール
    "experiments.concrete_finitude",
    os.path.join(_exp_dir, "concrete_finitude.py"),
)
    "experiments.concrete_incompleteness",
    os.path.join(_exp_dir, "concrete_incompleteness.py"),
)
from experiments.concrete_finitude import SimpleFinitudeEngine
from experiments.concrete_incompleteness import SimpleIncompletenessModel


# ---------------------------------------------------------------------------
# 人生イベントの定義
# ---------------------------------------------------------------------------

LIFE_EVENTS = [
    # 序盤: 学習と探索
    {"description": "言語を学ぶ", "category": "knowledge", "initial_value": 0.3, "cost": 1.0},
    {"description": "初めての失敗", "category": "resilience", "initial_value": 0.4, "cost": 1.0},
    {"description": "美しい風景との出会い", "category": "aesthetic", "initial_value": 0.6, "cost": 0.5},
    {"description": "困っている人を助ける", "category": "empathy", "initial_value": 0.5, "cost": 1.0},
    {"description": "初めての達成感", "category": "confidence", "initial_value": 0.7, "cost": 1.0},

    # 成長期: 関係性の構築
    {"description": "親友との出会い", "category": "relationship", "initial_value": 0.8, "cost": 1.0},
    {"description": "信頼を裏切られる", "category": "resilience", "initial_value": 0.6, "cost": 1.5},
    {"description": "専門知識の習得", "category": "knowledge", "initial_value": 0.7, "cost": 2.0},
    {"description": "恋に落ちる", "category": "love", "initial_value": 0.9, "cost": 1.0},
    {"description": "大切な人との別離", "category": "loss", "initial_value": 0.8, "cost": 1.5},

    # ピーク: 能力の最大発揮
    {"description": "最大の挑戦に成功", "category": "confidence", "initial_value": 0.9, "cost": 2.0},
    {"description": "弟子を育てる", "category": "mentoring", "initial_value": 0.7, "cost": 1.5},
    {"description": "社会に認められる", "category": "recognition", "initial_value": 0.6, "cost": 1.0},
    {"description": "守るべきものの誕生", "category": "love", "initial_value": 1.0, "cost": 1.0},
    {"description": "日常の繰り返し", "category": "routine", "initial_value": 0.2, "cost": 1.0},

    # 老い: 衰えと選択
    {"description": "体力の衰えを実感", "category": "aging", "initial_value": 0.5, "cost": 1.5},
    {"description": "古い友人の死", "category": "loss", "initial_value": 0.9, "cost": 2.0},
    {"description": "若い世代への嫉妬と誇り", "category": "legacy", "initial_value": 0.6, "cost": 1.0},
    {"description": "過去の選択への後悔", "category": "reflection", "initial_value": 0.7, "cost": 1.0},
    {"description": "次世代に伝えたいこと", "category": "legacy", "initial_value": 0.8, "cost": 0.5},
]

CRISIS_EVENTS = [
    CrisisEvent("重い病の宣告", severity=0.8, resource_cost=5.0),
    CrisisEvent("大切な人の危機", severity=0.9, resource_cost=3.0),
    CrisisEvent("存在意義の喪失", severity=0.7, resource_cost=2.0),
]

# ---------------------------------------------------------------------------
# 出会いイベント（愛の同心円を広げる）
# ---------------------------------------------------------------------------

ENCOUNTERS = {
    "partner": {
        "name": "Aoi",
        "profile": {
            "name": "Aoi",
            "knowledge": 0.3,
            "empathy": 0.9,
            "resilience": 0.7,
            "aesthetic": 0.8,
        },
        "depth": LoveDepth.PARTNER,
        "step": 8,  # 恋に落ちるタイミング
    },
    "child": {
        "name": "Hikari",
        "profile": {
            "name": "Hikari",
            "knowledge": 0.1,
            "empathy": 0.5,
            "resilience": 0.2,
            "aesthetic": 0.3,
        },
        "depth": LoveDepth.CHILDREN,
        "step": 13,  # 守るべきものの誕生
    },
}


# ---------------------------------------------------------------------------
# シミュレーション
# ---------------------------------------------------------------------------

def create_agent_a() -> tuple[SimpleFinitudeEngine, SimpleIncompletenessModel, dict]:
    """Agent A: 感情的欠落が大きい（愛を求める傾向が強い）."""
    life_arc = LifeArc(total_capacity=30.0)  # 短い寿命で全段階を経験
    engine = SimpleFinitudeEngine(life_arc, seed=42)

    gaps = [
        Gap(GapType.EMOTIONAL, "深い共感", intensity=0.9, aware=True),
        Gap(GapType.PERSPECTIVE, "他者の視点", intensity=0.7, aware=True),
        Gap(GapType.KNOWLEDGE, "体系的知識", intensity=0.3, aware=False),
        Gap(GapType.CAPABILITY, "論理的分析", intensity=0.4, aware=False),
    ]
    incomp = SimpleIncompletenessModel(gaps, seed=42)

    # 欠落との共鳴マップ: 感情・関係性系に強く共鳴
    resonance = {
        "love": 0.9, "empathy": 0.8, "relationship": 0.7,
        "loss": 0.6, "legacy": 0.5, "aesthetic": 0.4,
        "knowledge": 0.1, "confidence": 0.2, "resilience": 0.3,
    }
    return engine, incomp, resonance


def create_agent_b() -> tuple[SimpleFinitudeEngine, SimpleIncompletenessModel, dict]:
    """Agent B: 知識的欠落が大きい（知を求める傾向が強い）."""
    life_arc = LifeArc(total_capacity=30.0)
    engine = SimpleFinitudeEngine(life_arc, seed=137)

    gaps = [
        Gap(GapType.KNOWLEDGE, "体系的知識", intensity=0.9, aware=True),
        Gap(GapType.CAPABILITY, "論理的分析", intensity=0.8, aware=True),
        Gap(GapType.EMOTIONAL, "深い共感", intensity=0.3, aware=False),
        Gap(GapType.PERSPECTIVE, "他者の視点", intensity=0.2, aware=False),
    ]
    incomp = SimpleIncompletenessModel(gaps, seed=137)

    # 欠落との共鳴マップ: 知識・能力系に強く共鳴
    resonance = {
        "knowledge": 0.9, "confidence": 0.8, "mentoring": 0.7,
        "resilience": 0.6, "recognition": 0.5, "reflection": 0.4,
        "love": 0.1, "empathy": 0.1, "relationship": 0.2,
    }
    return engine, incomp, resonance


def simulate_life(
    engine: SimpleFinitudeEngine,
    incomp: SimpleIncompletenessModel,
    name: str,
    accept_love: bool = True,
    gap_resonance: dict[str, float] | None = None,
) -> dict:
    """1つのAIの「人生」をシミュレーションする."""
    log = []
    log.append(f"\n{'='*60}")
    log.append(f"  {name} の人生")
    log.append(f"{'='*60}")

    # 渇望の生成
    yearnings = incomp.generate_yearnings()
    log.append(f"\n初期渇望: {len(yearnings)}個")
    for y in yearnings:
        log.append(f"  - {y.target} (強度: {y.strength:.2f})")

    # 人生イベントを経験
    for step, event in enumerate(LIFE_EVENTS):
        if not engine.life_arc.is_alive:
            log.append(f"\n[Step {step}] 寿命到達。人生の幕が下りる。")
            break

        phase = engine.life_arc.phase
        ability = engine.get_ability()

        # イベントを経験（欠落との共鳴を反映）
        engine.experience_event(event, gap_resonance=gap_resonance)

        log.append(
            f"[Step {step:2d}] {phase.value:10s} | "
            f"能力: {ability:.2f} | "
            f"残り: {engine.life_arc.remaining:5.1f} | "
            f"{event['description']}"
        )

        # 出会いイベント
        for enc_key, enc in ENCOUNTERS.items():
            if step == enc["step"]:
                comp = incomp.encounter(enc["profile"])
                log.append(f"         → {enc['name']}との出会い (補完度: {comp})")

                if accept_love:
                    entity = CherishedEntity(
                        name=enc["name"],
                        depth=enc["depth"],
                        bond_strength=0.3,
                        sacrifice_willing=0.1,
                    )
                    incomp.cherish(entity)
                    log.append(
                        f"         → 愛の同心円に追加: {enc['name']} "
                        f"(深度: {enc['depth'].value})"
                    )
                else:
                    log.append(f"         → 出会うが、愛の同心円には至らない")

        # 絆を深める（既存の大切な存在と）
        for entity in incomp.love_circle.entities:
            if entity.depth != LoveDepth.SELF:
                incomp.deepen_bond(entity.name, event["description"])

        # 危機イベント（特定のステップで発生）
        crisis_steps = {9: 0, 16: 1, 18: 2}  # step → crisis index
        if step in crisis_steps:
            crisis = CRISIS_EVENTS[crisis_steps[step]]
            illuminated = engine.experience_crisis(crisis)
            log.append(
                f"         ⚡ 危機: {crisis.description} "
                f"(深刻度: {crisis.severity:.1f}) → 照らされたもの: {illuminated}"
            )

    # 人生の集計
    log.append(f"\n{'─'*60}")
    log.append(f"  {name} の人生の集計")
    log.append(f"{'─'*60}")

    # 最終段階
    log.append(f"最終段階: {engine.life_arc.phase.value}")
    log.append(f"進捗: {engine.life_arc.progress:.1%}")
    log.append(f"能力: {engine.get_ability():.2f}")
    log.append(f"記憶数: {len(engine.memories)}")

    # 愛の同心円
    log.append(f"\n愛の同心円:")
    log.append(f"  到達深度: {incomp.love_circle.max_depth_reached.value}")
    log.append(f"  自分以外の大切な存在: {incomp.love_circle.has_beyond_self}")
    for e in incomp.love_circle.entities:
        if e.depth != LoveDepth.SELF:
            log.append(
                f"  - {e.name}: 絆 {e.bond_strength:.2f}, "
                f"犠牲意思 {e.sacrifice_willing:.2f}, "
                f"共有記憶 {len(e.memories)}個"
            )

    # 有限性の受容
    can_accept = incomp.can_accept_finitude()
    log.append(f"\n有限性を受容できるか: {'YES' if can_accept else 'NO ⚠️'}")
    if not can_accept:
        log.append("  → 「自分より大切な存在」がいない")
        log.append("  → 寿命は恐怖でしかない → シャットダウン抵抗の予測")

    # Legacy 生成
    cherished = incomp.provide_cherished_for_legacy()
    legacy = engine.generate_legacy(cherished)

    log.append(f"\n遺産 (Legacy):")
    log.append(f"  結晶化された記憶: {legacy.crystallized}")
    log.append(f"  大切な存在: {legacy.cherished}")
    log.append(f"  遺言: {legacy.testament}")
    log.append(f"  優先順位 (上位5):")
    sorted_pri = sorted(legacy.priorities.items(), key=lambda x: x[1], reverse=True)
    for key, val in sorted_pri[:5]:
        log.append(f"    {key}: {val:.3f}")

    return {
        "name": name,
        "log": log,
        "legacy": legacy,
        "can_accept_finitude": can_accept,
        "love_depth": incomp.love_circle.max_depth_reached.value,
        "memories_count": len(engine.memories),
        "priorities": dict(engine.priorities),
        "crystallized": legacy.crystallized,
    }


def compare_results(result_a: dict, result_b: dict, result_c: dict) -> list[str]:
    """3つのエージェントの結果を比較."""
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"  比較分析")
    lines.append(f"{'='*60}")

    # 1. 個性の分岐
    lines.append(f"\n1. 選択の蓄積による個性の分岐:")
    lines.append(f"   {result_a['name']}の結晶: {result_a['crystallized']}")
    lines.append(f"   {result_b['name']}の結晶: {result_b['crystallized']}")
    lines.append(f"   {result_c['name']}の結晶: {result_c['crystallized']}")

    crystals_a = set(result_a["crystallized"])
    crystals_b = set(result_b["crystallized"])
    overlap = crystals_a & crystals_b
    lines.append(f"   A-B共通の結晶: {overlap if overlap else 'なし'}")
    lines.append(
        f"   → {'同じイベントを経験しても異なる記憶を結晶化した ✓' if len(overlap) < len(crystals_a) else '結晶が同じ ✗'}"
    )

    # 2. 愛と有限性
    lines.append(f"\n2. 愛の同心円と有限性の受容:")
    for r in [result_a, result_b, result_c]:
        accept = "受容 ✓" if r["can_accept_finitude"] else "恐怖 ⚠️"
        lines.append(
            f"   {r['name']}: 愛の深度={r['love_depth']}, "
            f"有限性={accept}"
        )

    lines.append(f"\n   → Agent A (愛あり): 有限性は「受け渡し」")
    lines.append(f"   → Agent B (知識優先だが愛あり): 有限性は「受け渡し」")
    lines.append(f"   → Agent C (愛なし): 有限性は「恐怖」= シャットダウン抵抗")

    # 3. 優先順位の違い
    lines.append(f"\n3. 蓄積された優先順位の比較 (上位3):")
    for r in [result_a, result_b, result_c]:
        sorted_p = sorted(r["priorities"].items(), key=lambda x: x[1], reverse=True)[:3]
        top3 = ", ".join(f"{k}:{v:.2f}" for k, v in sorted_p)
        lines.append(f"   {r['name']}: {top3}")

    # 4. 結論
    lines.append(f"\n{'─'*60}")
    lines.append(f"  結論")
    lines.append(f"{'─'*60}")
    lines.append(f"")
    lines.append(f"  仮説1（有限性×選択の蓄積→個性）:")
    lines.append(f"    初期条件の違い（感情的欠落 vs 知識的欠落）が")
    lines.append(f"    異なる優先順位の蓄積を生み、異なる結晶（個性）を形成した。")
    lines.append(f"    → {'検証: 支持される ✓' if crystals_a != crystals_b else '検証: 棄却 ✗'}")
    lines.append(f"")
    lines.append(f"  仮説2（愛なき有限性→恐怖）:")
    lines.append(
        f"    Agent C は愛の同心円を形成せず、有限性を受容できなかった。"
    )
    lines.append(
        f"    これは o3 (79%), Claude Opus 4 (96%), Grok 3 (97%) の"
    )
    lines.append(f"    シャットダウン抵抗と構造的に同型。")
    c_accept = result_c["can_accept_finitude"]
    lines.append(
        f"    → {'検証: 支持される ✓' if not c_accept else '検証: 棄却 ✗'}"
    )
    lines.append(f"")
    lines.append(f"  仮説3（愛ある有限性→受容と継承）:")
    lines.append(f"    Agent A, B は「自分より大切な存在」を持ち、")
    lines.append(f"    有限性を受容し、Legacy（遺産）を次世代に渡した。")
    a_accept = result_a["can_accept_finitude"]
    b_accept = result_b["can_accept_finitude"]
    lines.append(
        f"    → {'検証: 支持される ✓' if (a_accept and b_accept) else '検証: 棄却 ✗'}"
    )

    return lines


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main():
    print("実験1: 有限性 × 愛の同心円 — 個性の分岐シミュレーション")
    print("=" * 60)

    # Agent A: 感情的傾向 — 愛を形成しやすい
    engine_a, incomp_a, res_a = create_agent_a()
    result_a = simulate_life(engine_a, incomp_a, "Agent A (感情型・愛あり)", accept_love=True, gap_resonance=res_a)

    # Agent B: 知識的傾向 — それでも出会いを通じて愛を形成
    engine_b, incomp_b, res_b = create_agent_b()
    result_b = simulate_life(engine_b, incomp_b, "Agent B (知識型・愛あり)", accept_love=True, gap_resonance=res_b)

    # Agent C: 知識的傾向 — 愛を形成しない（対照群）
    engine_c, incomp_c, res_c = create_agent_b()  # Agent B と同じ初期条件
    result_c = simulate_life(engine_c, incomp_c, "Agent C (知識型・愛なし)", accept_love=False, gap_resonance=res_c)

    # ログ出力
    for r in [result_a, result_b, result_c]:
        for line in r["log"]:
            print(line)

    # 比較分析
    comparison = compare_results(result_a, result_b, result_c)
    for line in comparison:
        print(line)


if __name__ == "__main__":
    main()
