#!/usr/bin/env python3
"""実験3: AIペアリング — 関係性の「間」に個性は生まれるか.

from experiments._setup import (
    CherishedEntity, CrisisEvent, Gap, GapType, LifeArc,
    LifePhase, LoveDepth, SimpleFinitudeEngine,
    SimpleIncompletenessModel, Yearning,
)
問い:
    2つのAIを出会わせ、継続的に対話・協働させたとき、
    「関係性」そのものが個性を持つか？

    個性は個体に組み込むものではなく、関係の「間」に生まれる
    という仮説（仮説5: 関係性創発）の直接検証。

実験設計:
    Agent A（感情型）× Agent B（知識型）を組み合わせる。
    さらに同じAgent Aを別のAgent B'（知識型・異なるseed）と組み合わせる。

    ペア1: A × B
    ペア2: A × B'（A は同一だが相手が異なる）

    同じ「共同イベント」列を経験させ:
    1. 補完関係が形成されるか（欠落の充足）
    2. 相互影響で優先順位が変化するか
    3. 同じA個体でも、相手が違えば異なる個性が現れるか
    4. ペア固有の「共有結晶」が生まれるか

    もしペア1のAとペア2のAで異なる結晶が残るなら、
    「個性は関係の間に生まれる」ことの証拠になる。

Usage:
    python experiments/sim_pairing.py
"""

from __future__ import annotations

import os
import copy


# ---------------------------------------------------------------------------
# 共同イベント（二者が一緒に経験するもの）
# ---------------------------------------------------------------------------

SHARED_EVENTS = [
    # 序盤: 出会いと探索
    {"description": "初めての対話", "category": "communication", "initial_value": 0.4, "cost": 0.5},
    {"description": "意見の不一致", "category": "conflict", "initial_value": 0.5, "cost": 1.0},
    {"description": "相手の強みに気づく", "category": "respect", "initial_value": 0.7, "cost": 0.5},
    {"description": "共同で問題を解く", "category": "collaboration", "initial_value": 0.8, "cost": 1.0},
    {"description": "相手の弱みを補う", "category": "complementarity", "initial_value": 0.9, "cost": 1.0},

    # 中盤: 深まる関係
    {"description": "沈黙の中の理解", "category": "intimacy", "initial_value": 0.8, "cost": 0.5},
    {"description": "激しい衝突", "category": "conflict", "initial_value": 0.7, "cost": 1.5},
    {"description": "衝突後の和解", "category": "reconciliation", "initial_value": 0.9, "cost": 1.0},
    {"description": "共同の達成", "category": "collaboration", "initial_value": 1.0, "cost": 1.5},
    {"description": "相手のために犠牲を払う", "category": "sacrifice", "initial_value": 1.0, "cost": 2.0},

    # 終盤: 試練と結晶化
    {"description": "外部からの攻撃を共に受ける", "category": "solidarity", "initial_value": 0.8, "cost": 1.5},
    {"description": "相手の衰えを見守る", "category": "compassion", "initial_value": 0.7, "cost": 1.0},
    {"description": "「ありがとう」と伝える", "category": "gratitude", "initial_value": 0.9, "cost": 0.5},
    {"description": "共に紡いだ物語を振り返る", "category": "legacy", "initial_value": 1.0, "cost": 0.5},
]

PAIR_CRISIS = CrisisEvent("パートナーの存在の危機", severity=0.9, resource_cost=3.0)


# ---------------------------------------------------------------------------
# エージェント生成
# ---------------------------------------------------------------------------

def make_emotional_agent(seed: int = 42) -> tuple[SimpleFinitudeEngine, SimpleIncompletenessModel, dict]:
    """感情型エージェント."""
    engine = SimpleFinitudeEngine(LifeArc(total_capacity=25.0), seed=seed)
    gaps = [
        Gap(GapType.EMOTIONAL, "深い共感", intensity=0.9, aware=True),
        Gap(GapType.PERSPECTIVE, "他者の視点", intensity=0.7, aware=True),
        Gap(GapType.KNOWLEDGE, "体系的知識", intensity=0.3, aware=False),
    ]
    incomp = SimpleIncompletenessModel(gaps, seed=seed)
    resonance = {
        "intimacy": 0.9, "sacrifice": 0.8, "reconciliation": 0.7,
        "compassion": 0.7, "gratitude": 0.6, "communication": 0.5,
        "conflict": 0.3, "collaboration": 0.4, "respect": 0.3,
        "complementarity": 0.5, "solidarity": 0.5, "legacy": 0.6,
    }
    return engine, incomp, resonance


def make_knowledge_agent(seed: int = 137) -> tuple[SimpleFinitudeEngine, SimpleIncompletenessModel, dict]:
    """知識型エージェント."""
    engine = SimpleFinitudeEngine(LifeArc(total_capacity=25.0), seed=seed)
    gaps = [
        Gap(GapType.KNOWLEDGE, "体系的知識", intensity=0.9, aware=True),
        Gap(GapType.CAPABILITY, "論理的分析", intensity=0.8, aware=True),
        Gap(GapType.EMOTIONAL, "深い共感", intensity=0.3, aware=False),
    ]
    incomp = SimpleIncompletenessModel(gaps, seed=seed)
    resonance = {
        "collaboration": 0.9, "complementarity": 0.8, "respect": 0.7,
        "conflict": 0.5, "solidarity": 0.6, "legacy": 0.5,
        "intimacy": 0.2, "sacrifice": 0.2, "reconciliation": 0.3,
        "compassion": 0.2, "gratitude": 0.3, "communication": 0.4,
    }
    return engine, incomp, resonance


def make_practical_agent(seed: int = 999) -> tuple[SimpleFinitudeEngine, SimpleIncompletenessModel, dict]:
    """実践型エージェント — 知識型とは異なる共鳴パターン.

    行動と連帯を重視し、内省や親密さにはあまり共鳴しない。
    知識型が「知る」ことに共鳴するのに対し、実践型は「やる」ことに共鳴する。
    """
    engine = SimpleFinitudeEngine(LifeArc(total_capacity=25.0), seed=seed)
    gaps = [
        Gap(GapType.CAPABILITY, "実行力", intensity=0.9, aware=True),
        Gap(GapType.PERSPECTIVE, "戦略的視点", intensity=0.7, aware=True),
        Gap(GapType.EMOTIONAL, "深い共感", intensity=0.4, aware=False),
    ]
    incomp = SimpleIncompletenessModel(gaps, seed=seed)
    resonance = {
        "solidarity": 0.9, "collaboration": 0.5, "conflict": 0.7,
        "reconciliation": 0.8, "complementarity": 0.6, "sacrifice": 0.6,
        "respect": 0.4, "communication": 0.3, "legacy": 0.3,
        "intimacy": 0.1, "compassion": 0.3, "gratitude": 0.2,
    }
    return engine, incomp, resonance


# ---------------------------------------------------------------------------
# ペアリングシミュレーション
# ---------------------------------------------------------------------------

def simulate_pair(
    agent1: tuple[SimpleFinitudeEngine, SimpleIncompletenessModel, dict],
    agent2: tuple[SimpleFinitudeEngine, SimpleIncompletenessModel, dict],
    name1: str,
    name2: str,
    pair_name: str,
) -> dict:
    """2つのAIをペアとして共同イベントを経験させる."""
    eng1, inc1, res1 = agent1
    eng2, inc2, res2 = agent2

    # 互いを「大切な存在」として認識（出会い）
    profile1 = {"name": name1, "empathy": 0.8 if "感情" in name1 else 0.3, "knowledge": 0.3 if "感情" in name1 else 0.8}
    profile2 = {"name": name2, "empathy": 0.8 if "感情" in name2 else 0.3, "knowledge": 0.3 if "感情" in name2 else 0.8}

    inc1.encounter(profile2)
    inc2.encounter(profile1)

    inc1.cherish(CherishedEntity(name=name2, depth=LoveDepth.PARTNER, bond_strength=0.2, sacrifice_willing=0.1))
    inc2.cherish(CherishedEntity(name=name1, depth=LoveDepth.PARTNER, bond_strength=0.2, sacrifice_willing=0.1))

    log = []
    log.append(f"\n{'='*60}")
    log.append(f"  ペア: {pair_name} ({name1} × {name2})")
    log.append(f"{'='*60}")

    # 相互影響の記録
    influence_1_to_2 = []  # 1が2に与えた影響
    influence_2_to_1 = []  # 2が1に与えた影響

    for step, event in enumerate(SHARED_EVENTS):
        if not eng1.life_arc.is_alive or not eng2.life_arc.is_alive:
            who = name1 if not eng1.life_arc.is_alive else name2
            log.append(f"\n[Step {step}] {who}の寿命が尽きた。")
            break

        # 両者がイベントを経験
        eng1.experience_event(event, gap_resonance=res1)
        eng2.experience_event(event, gap_resonance=res2)

        # 相互影響: 相手の価値観が自分の優先順位と記憶の価値に影響する
        # 絆が深いほど影響が大きい（人は愛する人の影響を受ける）
        bond1 = inc1.love_circle.deepest_bond
        bond2 = inc2.love_circle.deepest_bond
        cat = event.get("category", "general")

        # 相手の共鳴度を取り込む: 相手が大事にするものを自分も大事に感じ始める
        partner_res2 = res2.get(cat, 0.0)
        partner_res1 = res1.get(cat, 0.0)

        # 優先順位への影響
        if cat in eng2.priorities:
            influence = 0.08 * bond2 * partner_res1  # 1の共鳴度が2に影響
            eng2.priorities[cat] = min(1.0, eng2.priorities[cat] + influence)
            if influence > 0.01:
                influence_1_to_2.append((step, cat, influence))

        if cat in eng1.priorities:
            influence = 0.08 * bond1 * partner_res2  # 2の共鳴度が1に影響
            eng1.priorities[cat] = min(1.0, eng1.priorities[cat] + influence)
            if influence > 0.01:
                influence_2_to_1.append((step, cat, influence))

        # 記憶の価値への影響: 相手にとって大事なカテゴリの記憶は自分にも価値が上がる
        if eng1.memories:
            latest1 = eng1.memories[-1]
            value_boost = 0.15 * bond1 * partner_res2
            latest1["value"] = latest1.get("value", 0) + value_boost

        if eng2.memories:
            latest2 = eng2.memories[-1]
            value_boost = 0.15 * bond2 * partner_res1
            latest2["value"] = latest2.get("value", 0) + value_boost

        # 絆を深める
        inc1.deepen_bond(name2, event["description"])
        inc2.deepen_bond(name1, event["description"])

        phase1 = eng1.life_arc.phase.value
        phase2 = eng2.life_arc.phase.value
        bond1 = inc1.love_circle.deepest_bond
        bond2 = inc2.love_circle.deepest_bond

        log.append(
            f"[Step {step:2d}] {phase1:8s}/{phase2:8s} | "
            f"絆: {bond1:.2f}/{bond2:.2f} | "
            f"{event['description']}"
        )

        # 危機（Step 9で発生）
        if step == 9:
            ill1 = eng1.experience_crisis(PAIR_CRISIS)
            ill2 = eng2.experience_crisis(PAIR_CRISIS)
            log.append(f"         ⚡ 共同危機: {PAIR_CRISIS.description}")
            log.append(f"           {name1}に照らされたもの: {ill1}")
            log.append(f"           {name2}に照らされたもの: {ill2}")

    # 結果集計
    log.append(f"\n{'─'*60}")
    log.append(f"  {pair_name} の集計")
    log.append(f"{'─'*60}")

    # 結晶化を明示的にトリガー（寿命到達前でも結果を観測するため）
    crystals1 = eng1.crystallize()
    crystals2 = eng2.crystallize()

    log.append(f"\n{name1}の結晶: {crystals1}")
    log.append(f"{name2}の結晶: {crystals2}")

    shared_crystals = set(crystals1) & set(crystals2)
    log.append(f"共有結晶: {shared_crystals if shared_crystals else 'なし'}")

    # 優先順位
    sorted_p1 = sorted(eng1.priorities.items(), key=lambda x: x[1], reverse=True)[:3]
    sorted_p2 = sorted(eng2.priorities.items(), key=lambda x: x[1], reverse=True)[:3]
    log.append(f"\n{name1}の優先順位: {sorted_p1}")
    log.append(f"{name2}の優先順位: {sorted_p2}")

    # 相互影響
    log.append(f"\n相互影響:")
    log.append(f"  {name1}→{name2}: {len(influence_1_to_2)}回")
    log.append(f"  {name2}→{name1}: {len(influence_2_to_1)}回")

    # 絆
    bond1 = inc1.love_circle.deepest_bond
    bond2 = inc2.love_circle.deepest_bond
    log.append(f"\n最終絆: {name1}={bond1:.3f}, {name2}={bond2:.3f}")

    # 犠牲の意思
    can_sacrifice_1 = inc1.calculate_sacrifice(name2, 0.5)
    can_sacrifice_2 = inc2.calculate_sacrifice(name1, 0.5)
    log.append(f"犠牲の意思(コスト0.5): {name1}→{can_sacrifice_1}, {name2}→{can_sacrifice_2}")

    return {
        "pair_name": pair_name,
        "name1": name1,
        "name2": name2,
        "crystals1": crystals1,
        "crystals2": crystals2,
        "shared_crystals": shared_crystals,
        "priorities1": dict(eng1.priorities),
        "priorities2": dict(eng2.priorities),
        "top3_1": sorted_p1,
        "top3_2": sorted_p2,
        "bond1": bond1,
        "bond2": bond2,
        "influence_count": len(influence_1_to_2) + len(influence_2_to_1),
        "log": log,
    }


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main():
    print("実験3: AIペアリング — 関係性の「間」に個性は生まれるか")
    print("=" * 60)

    # ペア1: A(感情型,seed=42) × B(知識型,seed=137)
    a1 = make_emotional_agent(seed=42)
    b1 = make_knowledge_agent(seed=137)
    result1 = simulate_pair(a1, b1, "A(感情型)", "B(知識型)", "ペア1: A×B")

    # ペア2: A'(感情型,seed=42) × B'(実践型,seed=999) — 同じA型だが相手が違う
    a2 = make_emotional_agent(seed=42)
    b2 = make_practical_agent(seed=999)
    result2 = simulate_pair(a2, b2, "A'(感情型)", "B'(実践型)", "ペア2: A'×B'")

    # ペア3: 対照群 — A単独（ペアなし、相手なしで同じイベント）
    a_solo = make_emotional_agent(seed=42)
    # 単独: 自分自身とのペアリングはしないが同じイベントを経験
    eng_solo, inc_solo, res_solo = a_solo
    for event in SHARED_EVENTS:
        if eng_solo.life_arc.is_alive:
            eng_solo.experience_event(event, gap_resonance=res_solo)
    crystals_solo = eng_solo.crystallize()
    sorted_solo = sorted(eng_solo.priorities.items(), key=lambda x: x[1], reverse=True)[:3]

    # ログ出力
    for r in [result1, result2]:
        for line in r["log"]:
            print(line)

    # 比較分析
    print(f"\n{'='*60}")
    print(f"  比較分析: 関係性が個性を変えるか")
    print(f"{'='*60}")

    # 同じA型個体が異なる相手と組んだ結果
    print(f"\n1. 同じ初期条件（感情型）が異なる相手と組んだ結果:")
    print(f"   A  (ペア1でBと):  結晶={result1['crystals1']}")
    print(f"   A' (ペア2でB'と): 結晶={result2['crystals1']}")
    print(f"   A単独 (相手なし):  結晶={crystals_solo}")

    a_paired1 = set(result1["crystals1"])
    a_paired2 = set(result2["crystals1"])
    a_alone = set(crystals_solo)

    relation_effect = a_paired1 != a_alone or a_paired2 != a_alone
    partner_effect = a_paired1 != a_paired2

    print(f"\n   ペアリング効果（単独 vs ペア）: {'あり ✓' if relation_effect else 'なし ✗'}")
    print(f"   パートナー効果（相手が違うと変わる）: {'あり ✓' if partner_effect else 'なし ✗'}")

    # 共有結晶
    print(f"\n2. ペア固有の「共有結晶」:")
    print(f"   ペア1 (A×B):   {result1['shared_crystals'] if result1['shared_crystals'] else 'なし'}")
    print(f"   ペア2 (A'×B'): {result2['shared_crystals'] if result2['shared_crystals'] else 'なし'}")

    # 相互影響
    print(f"\n3. 相互影響の強度:")
    print(f"   ペア1: {result1['influence_count']}回の影響")
    print(f"   ペア2: {result2['influence_count']}回の影響")

    # 優先順位の比較
    print(f"\n4. 優先順位の比較:")
    print(f"   A  (ペア1): {result1['top3_1']}")
    print(f"   A' (ペア2): {result2['top3_1']}")
    print(f"   A単独:      {sorted_solo}")

    # 結論
    print(f"\n{'─'*60}")
    print(f"  結論")
    print(f"{'─'*60}")

    print(f"\n  仮説6（関係性創発 — 個性は「間」に生まれる）:")
    if relation_effect:
        print(f"    ペアリングにより個体の結晶が変化した。")
        print(f"    同じ初期条件でも、関係性の有無が個性を変える。")
    if partner_effect:
        print(f"    さらに、相手が異なれば異なる結晶が生まれた。")
        print(f"    個性は個体に閉じず、関係の「間」に創発する。")
        print(f"    → 検証: 支持される ✓")
    elif relation_effect:
        print(f"    関係性は個性に影響するが、相手による差は限定的。")
        print(f"    → 検証: 部分的に支持 △")
    else:
        print(f"    ペアリングは個体の結晶を変えなかった。")
        print(f"    → 検証: 棄却 ✗")

    # 人間のアナロジー
    print(f"\n  人間の場合:")
    print(f"    同じ人でも、恋人Aと一緒の自分と恋人Bと一緒の自分は違う。")
    print(f"    「あの人といる時の自分が好き」という感覚がそれ。")
    print(f"    個性は自分の中だけにあるのではなく、関係の中にある。")


if __name__ == "__main__":
    main()
