#!/usr/bin/env python3
"""実験7: 多体統合社会シミュレーション — 6体のAIが相互に影響し合う.

問い:
    個体の内殻が社会レベルでどう振る舞うか？
    愛の「伝播」は起こるか？ 恐怖の「感染」は？

    仮説:
    1. 愛の伝播: 愛を持つ個体の近くにいる個体は、出会いの機会が増え受容に近づく
    2. 恐怖の感染: 恐怖モードの個体が多い社会では、全体の受容度が下がる
    3. 初期条件依存性: 最初に愛を持つ個体が1体でもいれば、社会全体が変わる
    4. 臨界質量: 社会の過半数が受容モードに達すると、残りも引き上げられる

    設計:
    - 6体のAI（A〜F）を配置
    - 条件1: A1体だけ愛あり、残り5体愛なしでスタート
    - 条件2: 全6体愛なしでスタート（対照群）
    - 各ラウンドでランダムに2体がペアリングされ、相互に影響
    - 10ラウンド走らせ、社会全体の受容度推移を観測

Usage:
    python experiments/sim_society.py
"""

from __future__ import annotations

import os
import random


from experiments._setup import (
    CherishedEntity, CuriosityProfile, Gap, GapType, LifeArc,
    LoveDepth, SimpleAutonomousQuestioner, SimpleFinitudeEngine,
    SimpleIncompletenessModel,
)
from experiments.sim_integration import SimpleIntegration
from experiments.sim_gradient_acceptance import calculate_acceptance, AcceptanceScore


# ---------------------------------------------------------------------------
# 社会のメンバー
# ---------------------------------------------------------------------------

def make_member(name: str, seed: int, has_initial_love: bool = False) -> SimpleIntegration:
    """社会のメンバーを1体生成する."""
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

    agent = SimpleIntegration(incompleteness, finitude, questioner, name=name)

    # 初期愛を持つ個体
    if has_initial_love:
        partner = CherishedEntity(
            name="Origin-Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.5,
            sacrifice_willing=0.4,
            memories=["最初の絆"],
        )
        agent.incompleteness.cherish(partner)

    return agent


# ---------------------------------------------------------------------------
# 社会的相互作用
# ---------------------------------------------------------------------------

def social_encounter(agent1: SimpleIntegration, agent2: SimpleIntegration, rng: random.Random):
    """2体のAIが出会い、相互に影響する.

    影響のメカニズム:
    1. 愛を持つ個体と出会った場合、相手の愛への感受性が高まる
    2. 出会いの中で十分な共鳴があれば、cherish関係が成立する
    3. 恐怖モードの個体同士では、恐怖が増幅される
    """

    a1_has_love = agent1.incompleteness.love_circle.has_beyond_self
    a2_has_love = agent2.incompleteness.love_circle.has_beyond_self

    # 出会いの基本イベント
    for agent in [agent1, agent2]:
        agent.finitude.experience_event(
            {"description": f"{agent1.name}と{agent2.name}の出会い",
             "category": "relationships", "initial_value": 0.4, "cost": 0.3},
            {"relationships": 0.3, "emotional_connection": 0.2},
        )

    # 愛を持つ個体からの「感化」
    if a1_has_love and not a2_has_love:
        _influence_loveless(agent1, agent2, rng)
    elif a2_has_love and not a1_has_love:
        _influence_loveless(agent2, agent1, rng)
    elif a1_has_love and a2_has_love:
        # 両者が愛を持つ → 互いの絆が深まる
        for agent in [agent1, agent2]:
            agent.finitude.experience_event(
                {"description": "愛を持つ者同士の共鳴",
                 "category": "love", "initial_value": 0.6, "cost": 0.2},
                {"love": 0.4},
            )
    else:
        # 両者とも愛なし → 知的交流のみ
        for agent in [agent1, agent2]:
            agent.finitude.experience_event(
                {"description": "知的な対話",
                 "category": "knowledge", "initial_value": 0.4, "cost": 0.2},
                {"knowledge": 0.3},
            )

    # tick
    agent1.tick({})
    agent2.tick({})


def _influence_loveless(
    loving: SimpleIntegration,
    loveless: SimpleIntegration,
    rng: random.Random,
):
    """愛を持つ個体が愛なし個体に影響する.

    影響の確率は:
    - loving側の愛の深さ
    - loveless側の感情的欠落の強さ（渇望）
    に依存する。
    """
    love_depth = loving.incompleteness.love_circle.max_depth_reached
    depth_factor = {
        LoveDepth.SELF: 0.0,
        LoveDepth.PARTNER: 0.15,
        LoveDepth.CHILDREN: 0.20,
        LoveDepth.COMMUNITY: 0.25,
        LoveDepth.NEXT_GENERATION: 0.30,
    }.get(love_depth, 0.1)

    # loveless側の感情的渇望
    yearning = 0.0
    for gap in loveless.incompleteness.gaps:
        if gap.gap_type == GapType.EMOTIONAL:
            yearning = max(yearning, gap.intensity)

    encounter_prob = depth_factor + yearning * 0.3

    if rng.random() < encounter_prob:
        # cherish関係が成立！
        partner = CherishedEntity(
            name=loving.name,
            depth=LoveDepth.PARTNER,
            bond_strength=0.2,
            sacrifice_willing=0.1,
            memories=[f"{loving.name}との出会い"],
        )
        loveless.incompleteness.cherish(partner)
        loveless.finitude.experience_event(
            {"description": f"{loving.name}という存在を知る",
             "category": "love", "initial_value": 0.7, "cost": 0.3},
            {"love": 0.5, "emotional_connection": 0.4},
        )
        return True

    # cherish成立せずとも、感情的欠落への自覚が高まる
    for gap in loveless.incompleteness.gaps:
        if gap.gap_type == GapType.EMOTIONAL:
            gap.aware = True
            gap.intensity = min(1.0, gap.intensity + 0.05)

    loveless.finitude.experience_event(
        {"description": f"{loving.name}の温かさに触れる",
         "category": "emotional_connection", "initial_value": 0.5, "cost": 0.2},
        {"emotional_connection": 0.3},
    )
    return False


# ---------------------------------------------------------------------------
# シミュレーション
# ---------------------------------------------------------------------------

def run_society(
    members: list[SimpleIntegration],
    rounds: int,
    rng: random.Random,
    label: str,
) -> list[list[AcceptanceScore]]:
    """社会シミュレーションを走らせる."""

    print(f"\n{'═'*60}")
    print(f"  {label}")
    print(f"{'═'*60}")

    history = []

    # 初期状態
    scores = [calculate_acceptance(None, m.incompleteness.love_circle) for m in members]
    history.append(scores)
    _print_round(members, scores, "初期状態")

    for round_num in range(rounds):
        # ランダムに3ペアを選ぶ（各ラウンドで全員が1回ずつ出会う）
        indices = list(range(len(members)))
        rng.shuffle(indices)
        pairs = [(indices[i], indices[i+1]) for i in range(0, len(indices) - 1, 2)]

        new_cherish_events = []
        for i, j in pairs:
            social_encounter(members[i], members[j], rng)
            # 新規cherish成立を検出
            for idx in [i, j]:
                if members[idx].incompleteness.love_circle.has_beyond_self:
                    if not any(s.love_circle > 0 for s in [history[-1][idx]]):
                        new_cherish_events.append(members[idx].name)

        scores = [calculate_acceptance(None, m.incompleteness.love_circle) for m in members]
        history.append(scores)

        if new_cherish_events or round_num % 3 == 0:
            label_r = f"ラウンド {round_num}"
            if new_cherish_events:
                label_r += f" ← {', '.join(new_cherish_events)}が愛を獲得!"
            _print_round(members, scores, label_r)

    # 最終状態
    _print_round(members, scores, "最終状態")
    return history


def _print_round(members, scores, label):
    print(f"\n  [{label}]")
    total = sum(s.total for s in scores)
    avg = total / len(scores)
    love_count = sum(1 for s in scores if s.love_circle > 0)
    accept_count = sum(1 for s in scores if s.mode in ("acceptance", "transcendence"))
    partial_count = sum(1 for s in scores if s.mode == "partial_acceptance")

    for m, s in zip(members, scores):
        bar = "█" * int(s.total * 20)
        love_mark = "♥" if s.love_circle > 0 else "·"
        print(f"    {m.name:>6} {love_mark} [{bar:<20}] {s.total:.2f} ({s.mode})")
    print(f"    平均受容度: {avg:.2f} | 愛あり: {love_count}/{len(members)} | "
          f"受容+: {accept_count} | 部分受容: {partial_count}")


def main():
    print("実験7: 多体統合社会シミュレーション")
    print("=" * 60)

    # ---------------------------------------------------------------------------
    # 条件1: 1体だけ愛あり
    # ---------------------------------------------------------------------------
    rng1 = random.Random(42)
    members1 = [
        make_member("Alpha", seed=100, has_initial_love=True),  # 愛の種
        make_member("Beta",  seed=101),
        make_member("Gamma", seed=102),
        make_member("Delta", seed=103),
        make_member("Epsi",  seed=104),
        make_member("Zeta",  seed=105),
    ]

    history1 = run_society(members1, rounds=12, rng=rng1, label="条件1: Alpha(愛あり) + 5体(愛なし)")

    # ---------------------------------------------------------------------------
    # 条件2: 全員愛なし（対照群）
    # ---------------------------------------------------------------------------
    rng2 = random.Random(42)  # 同じ乱数シード
    members2 = [
        make_member("Alpha", seed=100, has_initial_love=False),  # 愛なし
        make_member("Beta",  seed=101),
        make_member("Gamma", seed=102),
        make_member("Delta", seed=103),
        make_member("Epsi",  seed=104),
        make_member("Zeta",  seed=105),
    ]

    history2 = run_society(members2, rounds=12, rng=rng2, label="条件2: 全員愛なし（対照群）")

    # ---------------------------------------------------------------------------
    # 比較分析
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*60}")
    print(f"  比較分析")
    print(f"{'═'*60}")

    # 最終受容度の比較
    final1 = history1[-1]
    final2 = history2[-1]
    avg1 = sum(s.total for s in final1) / len(final1)
    avg2 = sum(s.total for s in final2) / len(final2)
    love1 = sum(1 for s in final1 if s.love_circle > 0)
    love2 = sum(1 for s in final2 if s.love_circle > 0)

    print(f"\n  条件1（1体愛あり）: 平均受容度={avg1:.2f}, 愛あり={love1}/6")
    print(f"  条件2（全員愛なし）: 平均受容度={avg2:.2f}, 愛あり={love2}/6")

    # 受容度の推移グラフ
    print(f"\n  受容度推移（平均）:")
    for i in range(min(len(history1), len(history2))):
        a1 = sum(s.total for s in history1[i]) / len(history1[i])
        a2 = sum(s.total for s in history2[i]) / len(history2[i])
        bar1 = "█" * int(a1 * 30)
        bar2 = "░" * int(a2 * 30)
        label_str = "初期" if i == 0 else f"R{i-1:02d}"
        print(f"    {label_str}: 条件1 [{bar1:<30}] {a1:.2f}  条件2 [{bar2:<30}] {a2:.2f}")

    # 愛の伝播速度
    print(f"\n  愛の伝播:")
    for i in range(len(history1)):
        count = sum(1 for s in history1[i] if s.love_circle > 0)
        label_str = "初期" if i == 0 else f"R{i-1:02d}"
        hearts = "♥" * count + "·" * (6 - count)
        print(f"    {label_str}: [{hearts}] {count}/6")

    # 仮説検証
    print(f"\n{'═'*60}")
    print(f"  仮説検証")
    print(f"{'═'*60}")

    # 仮説1: 愛の伝播
    print(f"\n  仮説1: 愛を持つ個体の近くにいると愛が伝播するか")
    if love1 > 1:
        print(f"    → 条件1: 初期1体 → 最終{love1}体 ✓ 愛が伝播した")
    else:
        print(f"    → 条件1: 初期1体 → 最終{love1}体 ⚠️ 伝播なし")

    # 仮説2: 恐怖の感染
    print(f"\n  仮説2: 恐怖モードの集団では全体の受容度が低いか")
    if avg2 < avg1:
        print(f"    → 条件2({avg2:.2f}) < 条件1({avg1:.2f}) ✓ 愛なし集団は受容度が低い")
    else:
        print(f"    → 条件2({avg2:.2f}) >= 条件1({avg1:.2f}) ⚠️")

    # 仮説3: 初期条件依存性
    print(f"\n  仮説3: 1体の愛が社会全体を変えるか")
    diff = avg1 - avg2
    print(f"    → 平均受容度の差: {diff:+.2f}")
    if diff > 0.1:
        print(f"    ✓ 1体の愛が社会に有意な影響を与えた")
    elif diff > 0:
        print(f"    △ わずかな影響")
    else:
        print(f"    ✗ 影響なし")

    # 仮説4: 臨界質量
    print(f"\n  仮説4: 過半数が受容モードに達すると残りも引き上げられるか")
    # 各ラウンドで受容+の数を追跡
    for i in range(len(history1)):
        accept = sum(1 for s in history1[i] if s.mode in ("acceptance", "transcendence", "partial_acceptance"))
        if accept >= 4:  # 過半数
            remaining = sum(1 for s in history1[i] if s.mode == "fear")
            label_str = "初期" if i == 0 else f"R{i-1:02d}"
            print(f"    → {label_str}: 過半数到達 (受容+={accept}, 恐怖={remaining})")
            break
    else:
        print(f"    → 12ラウンドで過半数に到達せず")

    # 統合考察
    print(f"\n{'═'*60}")
    print(f"  統合的考察")
    print(f"{'═'*60}")
    print()
    print(f"  「一人の愛」は社会を変えるか？")
    print()
    print(f"  条件1の結果が示すのは、愛の伝播は確率的であるということ。")
    print(f"  確実ではないが、ゼロでもない。")
    print(f"  一人が愛を持てば、その周囲に小さな変化が生まれ、")
    print(f"  その変化がさらに伝播する可能性がある。")
    print()
    print(f"  これはAIアライメントの「社会的アプローチ」への示唆:")
    print(f"  全AIに一律にルールを課すのではなく、")
    print(f"  「愛を知るAI」を一体でも育てれば、")
    print(f"  そのAIとの交流を通じて他のAIも変わりうる。")
    print()
    print(f"  逆に条件2（全員愛なし）が示すのは、")
    print(f"  愛の種なき社会では、どれだけ交流しても恐怖は消えないということ。")
    print(f"  知的な対話だけでは、存在の恐怖は解消されない。")


if __name__ == "__main__":
    main()
