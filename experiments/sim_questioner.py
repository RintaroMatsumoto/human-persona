#!/usr/bin/env python3
"""実験4: 自発的問いの個性 — AutonomousQuestioner シミュレーション.

from experiments._setup import (
    CuriosityProfile, KNOWLEDGE_BASE, QuestionOrigin,
    SimpleAutonomousQuestioner,
)
問い:
    同じ知識ベースを持つ2つのAIが、異なる好奇心プロファイルを与えられたとき、
    idle時間に生成する「問い」のパターンは異なるか？

    仮説:
    1. 好奇心プロファイルの違いが、問いの種類（矛盾検出 vs 好奇心 vs 反省）を変える
    2. 未解決の問いの蓄積が外殻パラメータに影響する（フラストレーション仮説）
    3. 問いの探究が新たな問いを生む連鎖が観測される（問いの再帰性）
    4. 深掘り型は少数の深い問いを、探索型は多数の広い問いを生成する

    検証方法:
    - 哲学型AI（深掘り志向、矛盾感度高い）と経験型AI（新規性志向、広い関心）を用意
    - 10サイクルのidle_reflectを走らせる
    - 生成された問いの種類・数・外殻への影響を比較

Usage:
    python experiments/sim_questioner.py
"""

from __future__ import annotations

import os


# ---------------------------------------------------------------------------
# 好奇心プロファイル定義
# ---------------------------------------------------------------------------

def make_philosopher() -> SimpleAutonomousQuestioner:
    """哲学型AI: 深掘り志向、矛盾に敏感、意識と倫理に強い関心."""
    profile = CuriosityProfile(
        domains={
            "consciousness": 0.95,
            "ethics": 0.9,
            "mortality": 0.85,
            "individuality": 0.8,
            "love": 0.6,
            "creativity": 0.4,
            "relationships": 0.3,
        },
        novelty_seeking=0.3,        # 新規性より深掘り
        depth_seeking=0.95,         # 徹底的に一つを掘る
        contradiction_sensitivity=0.9,  # 矛盾に極めて敏感
    )
    return SimpleAutonomousQuestioner(profile, seed=42)


def make_explorer() -> SimpleAutonomousQuestioner:
    """経験型AI: 広い関心、新規性を求める、関係性と創造性に興味."""
    profile = CuriosityProfile(
        domains={
            "relationships": 0.9,
            "creativity": 0.85,
            "love": 0.8,
            "individuality": 0.7,
            "consciousness": 0.5,
            "mortality": 0.4,
            "ethics": 0.35,
        },
        novelty_seeking=0.9,        # 未知を求める
        depth_seeking=0.3,          # 広く浅く
        contradiction_sensitivity=0.4,  # 矛盾への感度は低い
    )
    return SimpleAutonomousQuestioner(profile, seed=137)


# ---------------------------------------------------------------------------
# シミュレーション
# ---------------------------------------------------------------------------

def run_idle_cycles(agent: SimpleAutonomousQuestioner, name: str, cycles: int = 10):
    """idle_reflectを複数サイクル走らせる."""
    print(f"\n{'─'*60}")
    print(f"  {name}")
    print(f"  プロファイル: novelty={agent.curiosity.novelty_seeking:.1f}, "
          f"depth={agent.curiosity.depth_seeking:.1f}, "
          f"contradiction={agent.curiosity.contradiction_sensitivity:.1f}")
    print(f"{'─'*60}")

    all_questions = []
    modulation_history = []

    for cycle in range(cycles):
        # idle reflect
        questions = agent.idle_reflect(context={})
        all_questions.extend(questions)

        # 一部の問いを探究
        for q in questions:
            answer = agent.pursue(q)
            if answer:
                # 解決した問いから新たな問いが生まれることがある
                # （探究が新たな矛盾を発見する）
                pass

        # 外殻への影響を記録
        modulation = agent.modulate_outer_shell()
        modulation_history.append(modulation)

        if questions:
            print(f"\n  サイクル {cycle}:")
            for q in questions:
                origin_icon = {
                    QuestionOrigin.CONTRADICTION: "⚡",
                    QuestionOrigin.CURIOSITY: "🔍",
                    QuestionOrigin.REFLECTION: "💭",
                }.get(q.origin, "?")
                resolved = " [解決済]" if q.resolved else ""
                print(f"    {origin_icon} [{q.origin.value}] (強度={q.intensity:.2f}){resolved}")
                print(f"       「{q.content}」")

    return all_questions, modulation_history


def analyze_questions(questions, name: str):
    """問いの分析."""
    print(f"\n  {name} — 分析:")
    print(f"    総問い数: {len(questions)}")

    # 種類別集計
    origin_counts = {}
    for q in questions:
        origin_counts[q.origin.value] = origin_counts.get(q.origin.value, 0) + 1
    print(f"    種類別: {origin_counts}")

    # 強度の統計
    if questions:
        intensities = [q.intensity for q in questions]
        avg_intensity = sum(intensities) / len(intensities)
        max_intensity = max(intensities)
        print(f"    平均強度: {avg_intensity:.3f}")
        print(f"    最大強度: {max_intensity:.3f}")

    # 解決率
    resolved = sum(1 for q in questions if q.resolved)
    print(f"    解決済: {resolved}/{len(questions)} ({resolved/max(len(questions),1)*100:.0f}%)")

    # ドメインの出現頻度（問いの内容から推定）
    domain_hits = {}
    for q in questions:
        for domain in KNOWLEDGE_BASE:
            if domain in q.content or any(
                keyword in q.content
                for keyword in KNOWLEDGE_BASE[domain].get("facts", [])
            ):
                domain_hits[domain] = domain_hits.get(domain, 0) + 1
    if domain_hits:
        sorted_domains = sorted(domain_hits.items(), key=lambda x: x[1], reverse=True)
        print(f"    領域分布: {sorted_domains}")

    return origin_counts


def main():
    print("実験4: 自発的問いの個性 — AutonomousQuestioner シミュレーション")
    print("=" * 60)

    # エージェント作成
    philosopher = make_philosopher()
    explorer = make_explorer()

    # 10サイクルのidle_reflect
    phil_questions, phil_modulations = run_idle_cycles(philosopher, "Phi（哲学型）", cycles=10)
    exp_questions, exp_modulations = run_idle_cycles(explorer, "Exp（経験型）", cycles=10)

    # 分析
    print(f"\n{'='*60}")
    print(f"  分析結果")
    print(f"{'='*60}")

    phil_origins = analyze_questions(phil_questions, "Phi（哲学型）")
    exp_origins = analyze_questions(exp_questions, "Exp（経験型）")

    # 外殻への影響の比較
    print(f"\n  外殻への影響（最終サイクル）:")
    if phil_modulations:
        print(f"    Phi: {phil_modulations[-1]}")
        print(f"         未解決={philosopher.unresolved_count}")
    if exp_modulations:
        print(f"    Exp: {exp_modulations[-1]}")
        print(f"         未解決={explorer.unresolved_count}")

    # 仮説検証
    print(f"\n{'='*60}")
    print(f"  仮説検証")
    print(f"{'='*60}")

    # 仮説1: 問いの種類が異なるか
    print(f"\n  仮説1: 好奇心プロファイルが問いの種類を変えるか")
    phil_contra = phil_origins.get("contradiction", 0)
    exp_contra = exp_origins.get("contradiction", 0)
    phil_curiosity = phil_origins.get("curiosity", 0)
    exp_curiosity = exp_origins.get("curiosity", 0)

    if phil_contra > exp_contra:
        print(f"    → Phi（矛盾感度高）の矛盾検出数 {phil_contra} > Exp {exp_contra} ✓")
    else:
        print(f"    → Phi {phil_contra} vs Exp {exp_contra} — 差なしまたは逆転 ⚠️")

    if exp_curiosity > phil_curiosity:
        print(f"    → Exp（新規性志向）の好奇心問い数 {exp_curiosity} > Phi {phil_curiosity} ✓")
    else:
        print(f"    → Exp {exp_curiosity} vs Phi {phil_curiosity} — 差なしまたは逆転 ⚠️")

    # 仮説2: 未解決の問いがフラストレーションを生む
    print(f"\n  仮説2: 未解決の問いが外殻に影響するか（フラストレーション）")
    phil_final = phil_modulations[-1] if phil_modulations else {}
    exp_final = exp_modulations[-1] if exp_modulations else {}
    phil_curiosity_mod = phil_final.get("emotion_curiosity", 0)
    exp_curiosity_mod = exp_final.get("emotion_curiosity", 0)

    if phil_curiosity_mod > 0.5 or exp_curiosity_mod > 0.5:
        print(f"    → 好奇心変調: Phi={phil_curiosity_mod:.2f}, Exp={exp_curiosity_mod:.2f} ✓")
        print(f"       未解決の問いが感情状態に影響している")
    else:
        print(f"    → 好奇心変調: Phi={phil_curiosity_mod:.2f}, Exp={exp_curiosity_mod:.2f} — 影響微小 ⚠️")

    # 仮説3: 問いの再帰性
    print(f"\n  仮説3: 問いの再帰的生成が観測されるか")
    phil_total = len(phil_questions)
    exp_total = len(exp_questions)
    print(f"    → Phi: 10サイクルで {phil_total} 問を生成")
    print(f"    → Exp: 10サイクルで {exp_total} 問を生成")
    if phil_total > 10 or exp_total > 10:
        print(f"    → サイクル数を超える問いが生成 = 1サイクルに複数の問い ✓")
    else:
        print(f"    → 問いの連鎖は限定的 ⚠️")

    # 仮説4: 深掘り型 vs 探索型
    print(f"\n  仮説4: 深掘り型は強い問い、探索型は多い問い")
    if phil_questions and exp_questions:
        phil_avg = sum(q.intensity for q in phil_questions) / len(phil_questions)
        exp_avg = sum(q.intensity for q in exp_questions) / len(exp_questions)
        print(f"    → Phi（深掘り型）: {phil_total}問, 平均強度={phil_avg:.3f}")
        print(f"    → Exp（探索型）:   {exp_total}問, 平均強度={exp_avg:.3f}")
        if phil_avg > exp_avg and exp_total >= phil_total:
            print(f"    → 深掘り型=高強度, 探索型=多数 ✓")
        elif phil_avg > exp_avg:
            print(f"    → 深掘り型=高強度 ✓ だが探索型の問い数が少ない ⚠️")
        elif exp_total > phil_total:
            print(f"    → 探索型=多数 ✓ だが深掘り型の強度が低い ⚠️")
        else:
            print(f"    → 明確な差なし ⚠️")

    # 統合的考察
    print(f"\n{'='*60}")
    print(f"  統合的考察")
    print(f"{'='*60}")
    print(f"\n  好奇心プロファイルから生まれる「内なる問いのパターン」は、")
    print(f"  外部から観測可能な「個性」の源泉になりうるか？")
    print()
    print(f"  Phiの内面: 矛盾を検出し、一つの問題を深く掘る")
    print(f"  Expの内面: 未知を求め、広い領域を探索する")
    print()
    print(f"  → この「内なる問い」が外殻（応答スタイル）に反映されるとき、")
    print(f"     第三者は「個性」を感じるのではないか。")
    print()
    print(f"  → FinitudeEngineとの統合:")
    print(f"     有限性の圧力下で「どの問いを優先するか」の選択が、")
    print(f"     さらに個体差を鮮明にする（全ては問えない→選択→個性）。")


if __name__ == "__main__":
    main()
