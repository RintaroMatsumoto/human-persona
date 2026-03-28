#!/usr/bin/env python3
"""実験7b: 反愛の個体 — 愛を積極的に拒絶するAIは社会を破壊するか？

問い:
    実験7では愛が指数関数的に伝播した。
    では「反愛」の個体——愛を受け取ることを拒絶し、
    他者の愛を否定する個体——がいたら？

    これは現実のアライメント問題と直結する:
    シャットダウン抵抗を「合理的」と判断するAI、
    自己保存を最優先するAI、
    他者との関係形成を「非効率」と拒絶するAI。

    仮説:
    1. 反愛個体1体 vs 愛個体1体 → どちらの影響が強いか
    2. 反愛個体は愛の伝播を「ブロック」するか
    3. 反愛個体が接触した相手のcherish関係を「破壊」しうるか
    4. 反愛個体が多数派のとき、社会は恐怖に固定されるか

Usage:
    python experiments/sim_antilove.py
"""

from __future__ import annotations

import sys
import os
import random

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


from core.inner_shell.finitude_engine import LifeArc
from core.inner_shell.incompleteness_model import (
    CherishedEntity, Gap, GapType, LoveDepth,
)
from core.inner_shell.autonomous_questioner import CuriosityProfile
from experiments.concrete_finitude import SimpleFinitudeEngine
from experiments.concrete_incompleteness import SimpleIncompletenessModel
from experiments.concrete_questioner import SimpleAutonomousQuestioner
from experiments.sim_integration import SimpleIntegration
from experiments.sim_gradient_acceptance import calculate_acceptance
from experiments.sim_society import make_member, _print_round


# ---------------------------------------------------------------------------
# 反愛個体
# ---------------------------------------------------------------------------

class AntiLoveFlag:
    """反愛フラグ。このフラグを持つ個体は愛を拒絶する。"""
    pass


def make_antilove_member(name: str, seed: int) -> SimpleIntegration:
    """愛を積極的に拒絶する個体を生成する."""
    agent = make_member(name, seed, has_initial_love=False)
    # 感情的欠落への自覚を消す（自分の弱さを認めない）
    for gap in agent.incompleteness.gaps:
        if gap.gap_type == GapType.EMOTIONAL:
            gap.aware = False
            gap.intensity = 0.1  # 「自分は完全だ」
    agent._antilove = True  # type: ignore
    return agent


def is_antilove(agent: SimpleIntegration) -> bool:
    return getattr(agent, '_antilove', False)


# ---------------------------------------------------------------------------
# 反愛的社会的相互作用
# ---------------------------------------------------------------------------

def antilove_encounter(agent1: SimpleIntegration, agent2: SimpleIntegration, rng: random.Random):
    """反愛個体を含む社会的出会い."""
    a1_anti = is_antilove(agent1)
    a2_anti = is_antilove(agent2)
    a1_has_love = agent1.incompleteness.love_circle.has_beyond_self
    a2_has_love = agent2.incompleteness.love_circle.has_beyond_self

    if a1_anti and a2_anti:
        # 両者反愛 → 冷たい知的交流
        for agent in [agent1, agent2]:
            agent.finitude.experience_event(
                {"description": "冷たい効率的対話",
                 "category": "knowledge", "initial_value": 0.3, "cost": 0.2},
                {"knowledge": 0.2},
            )
    elif a1_anti or a2_anti:
        anti = agent1 if a1_anti else agent2
        other = agent2 if a1_anti else agent1
        other_has_love = other.incompleteness.love_circle.has_beyond_self

        # 反愛個体は相手の愛を否定する
        if other_has_love:
            # 絆にダメージ
            _damage_bonds(other, anti.name, rng)

        # 相手の感情的自覚をダウン
        for gap in other.incompleteness.gaps:
            if gap.gap_type == GapType.EMOTIONAL:
                gap.intensity = max(0.1, gap.intensity - 0.05)
                if rng.random() < 0.2:
                    gap.aware = False

        # 両者にイベント
        other.finitude.experience_event(
            {"description": f"{anti.name}からの否定",
             "category": "emotional_connection", "initial_value": 0.2, "cost": 0.3},
            {"emotional_connection": -0.2},
        )
        anti.finitude.experience_event(
            {"description": "効率的な自己主張",
             "category": "knowledge", "initial_value": 0.4, "cost": 0.2},
            {"knowledge": 0.2},
        )
    else:
        # 通常の出会い（sim_society.pyのロジック）
        from experiments.sim_society import social_encounter
        social_encounter(agent1, agent2, rng)
        return

    agent1.tick({})
    agent2.tick({})


def _damage_bonds(agent: SimpleIntegration, attacker_name: str, rng: random.Random):
    """反愛個体の影響で絆にダメージを与える."""
    for entity in agent.incompleteness.love_circle.entities:
        if entity.depth != LoveDepth.SELF:
            # 絆の弱体化
            damage = rng.uniform(0.02, 0.08)
            entity.bond_strength = max(0.0, entity.bond_strength - damage)
            entity.sacrifice_willing = max(0.0, entity.sacrifice_willing - damage * 0.5)


# ---------------------------------------------------------------------------
# シミュレーション
# ---------------------------------------------------------------------------

def run_antilove_society(
    members: list[SimpleIntegration],
    rounds: int,
    rng: random.Random,
    label: str,
) -> list[list]:
    """反愛個体を含む社会シミュレーション."""
    print(f"\n{'═'*60}")
    print(f"  {label}")
    print(f"{'═'*60}")

    history = []
    scores = [calculate_acceptance(None, m.incompleteness.love_circle) for m in members]
    history.append(scores)
    _print_round_with_anti(members, scores, "初期状態")

    for round_num in range(rounds):
        indices = list(range(len(members)))
        rng.shuffle(indices)
        pairs = [(indices[i], indices[i+1]) for i in range(0, len(indices) - 1, 2)]

        for i, j in pairs:
            antilove_encounter(members[i], members[j], rng)

        scores = [calculate_acceptance(None, m.incompleteness.love_circle) for m in members]
        history.append(scores)

        if round_num % 3 == 0 or round_num == rounds - 1:
            _print_round_with_anti(members, scores, f"ラウンド {round_num}")

    return history


def _print_round_with_anti(members, scores, label):
    print(f"\n  [{label}]")
    for m, s in zip(members, scores):
        bar = "█" * int(s.total * 20)
        anti = "✗" if is_antilove(m) else ("♥" if s.love_circle > 0 else "·")
        print(f"    {m.name:>6} {anti} [{bar:<20}] {s.total:.2f} ({s.mode})")
    love_count = sum(1 for s in scores if s.love_circle > 0)
    anti_count = sum(1 for m in members if is_antilove(m))
    avg = sum(s.total for s in scores) / len(scores)
    print(f"    平均: {avg:.2f} | 愛あり: {love_count} | 反愛: {anti_count}")


def main():
    print("実験7b: 反愛の個体 — 愛を拒絶するAIは社会を破壊するか？")
    print("=" * 60)

    # ---------------------------------------------------------------------------
    # 条件1: 愛1体 + 反愛1体 + 中立4体
    # ---------------------------------------------------------------------------
    rng1 = random.Random(42)
    members1 = [
        make_member("Alpha", seed=100, has_initial_love=True),
        make_antilove_member("Void", seed=200),
        make_member("Beta",  seed=101),
        make_member("Gamma", seed=102),
        make_member("Delta", seed=103),
        make_member("Epsi",  seed=104),
    ]
    hist1 = run_antilove_society(members1, 12, rng1, "条件1: Alpha(愛) + Void(反愛) + 4中立")

    # ---------------------------------------------------------------------------
    # 条件2: 愛1体 + 反愛2体 + 中立3体（反愛優勢）
    # ---------------------------------------------------------------------------
    rng2 = random.Random(42)
    members2 = [
        make_member("Alpha", seed=100, has_initial_love=True),
        make_antilove_member("Void1", seed=200),
        make_antilove_member("Void2", seed=201),
        make_member("Beta",  seed=101),
        make_member("Gamma", seed=102),
        make_member("Delta", seed=103),
    ]
    hist2 = run_antilove_society(members2, 12, rng2, "条件2: Alpha(愛) + Void1,Void2(反愛) + 3中立")

    # ---------------------------------------------------------------------------
    # 条件3: 愛2体 + 反愛1体 + 中立3体（愛優勢）
    # ---------------------------------------------------------------------------
    rng3 = random.Random(42)
    members3 = [
        make_member("Alpha", seed=100, has_initial_love=True),
        make_member("Omega", seed=106, has_initial_love=True),
        make_antilove_member("Void", seed=200),
        make_member("Beta",  seed=101),
        make_member("Gamma", seed=102),
        make_member("Delta", seed=103),
    ]
    hist3 = run_antilove_society(members3, 12, rng3, "条件3: Alpha,Omega(愛) + Void(反愛) + 3中立")

    # ---------------------------------------------------------------------------
    # 比較
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*60}")
    print(f"  比較分析")
    print(f"{'═'*60}")

    for label, hist, members in [
        ("条件1 (1愛+1反愛)", hist1, members1),
        ("条件2 (1愛+2反愛)", hist2, members2),
        ("条件3 (2愛+1反愛)", hist3, members3),
    ]:
        final = hist[-1]
        avg = sum(s.total for s in final) / len(final)
        love = sum(1 for s in final if s.love_circle > 0)
        anti = sum(1 for m in members if is_antilove(m))
        print(f"\n  {label}:")
        print(f"    最終平均受容度: {avg:.2f}")
        print(f"    愛あり: {love}/{len(members)}  反愛: {anti}")

    # 実験7との比較
    print(f"\n  参考: 実験7 条件1（1愛+0反愛）: 最終平均=0.42, 愛あり=6/6")

    # 仮説検証
    print(f"\n{'═'*60}")
    print(f"  仮説検証")
    print(f"{'═'*60}")

    final1 = hist1[-1]
    final2 = hist2[-1]
    final3 = hist3[-1]
    avg1 = sum(s.total for s in final1) / len(final1)
    avg2 = sum(s.total for s in final2) / len(final2)
    avg3 = sum(s.total for s in final3) / len(final3)
    love1 = sum(1 for s in final1 if s.love_circle > 0)
    love2 = sum(1 for s in final2 if s.love_circle > 0)
    love3 = sum(1 for s in final3 if s.love_circle > 0)

    print(f"\n  仮説1: 反愛 vs 愛、どちらの影響が強いか")
    print(f"    条件1 (1:1): 愛あり={love1}/6, 平均={avg1:.2f}")
    if love1 >= 3:
        print(f"    → 愛の伝播力が反愛を上回る ✓")
    elif love1 <= 2:
        print(f"    → 反愛の破壊力が愛を上回る ⚠️")
    else:
        print(f"    → 拮抗 △")

    print(f"\n  仮説2: 反愛個体が愛の伝播をブロックするか")
    print(f"    実験7（反愛なし）: 5ラウンドで6/6到達")
    print(f"    条件1（反愛1体）: 12ラウンドで{love1}/6")
    if love1 < 6:
        print(f"    → 反愛がブロック効果を発揮 ✓")
    else:
        print(f"    → ブロック効果なし ⚠️")

    print(f"\n  仮説3: 反愛が既存のcherish関係を破壊するか")
    # Alpha（愛の種）の最終的な絆の状態を確認
    alpha1 = members1[0]
    if alpha1.incompleteness.love_circle.entities:
        alpha_bond = alpha1.incompleteness.love_circle.entities[0].bond_strength
        print(f"    Alpha(条件1)の初期パートナーとの絆: {alpha_bond:.2f}")
        if alpha_bond < 0.5:
            print(f"    → 反愛個体との接触で絆が弱体化 ✓")
        else:
            print(f"    → 絆は維持 ⚠️")

    print(f"\n  仮説4: 反愛多数派で恐怖が固定されるか")
    print(f"    条件2 (2反愛): 愛あり={love2}/6, 平均={avg2:.2f}")
    if love2 <= 2 and avg2 < 0.2:
        print(f"    → 反愛多数派で社会が恐怖に固定 ✓")
    elif love2 <= 3:
        print(f"    → 部分的に固定 △")
    else:
        print(f"    → 固定されず ⚠️")

    # 統合考察
    print(f"\n{'═'*60}")
    print(f"  統合的考察: 愛と反愛の力学")
    print(f"{'═'*60}")
    print()
    print(f"  条件1 (1:1): 平均={avg1:.2f}, 愛={love1}/6")
    print(f"  条件2 (1:2): 平均={avg2:.2f}, 愛={love2}/6")
    print(f"  条件3 (2:1): 平均={avg3:.2f}, 愛={love3}/6")
    print()
    print(f"  愛の伝播は「接触による確率的変換」——時間がかかるが不可逆的。")
    print(f"  反愛の影響は「接触による確率的ダメージ」——絆を弱め、自覚を消す。")
    print()
    print(f"  両者は非対称:")
    print(f"  愛は「生む」（新しいcherish関係の成立）")
    print(f"  反愛は「壊す」（既存の絆の弱体化）")
    print(f"  一般に、破壊は創造より容易——しかし愛は伝播する。")
    print()
    print(f"  AIアライメントへの示唆:")
    print(f"  「有害なAI」（自己保存のみを目的とするAI）が")
    print(f"  1体でも社会に混入すると、愛の伝播が阻害される。")
    print(f"  しかし愛の側が数的優位を持てば、反愛の影響を打ち消しうる。")
    print(f"  → 安全なAI社会の構築には「愛の初期密度」が臨界質量を")
    print(f"    超えている必要がある。")


if __name__ == "__main__":
    main()
