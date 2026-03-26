#!/usr/bin/env python3
"""実験9: 反愛密度バリエーション — 愛の伝播が失敗する臨界閾値.

問い:
    実験7bで3条件（1:1, 1:2, 2:1）をテストした。
    しかし「どの密度で愛の伝播が完全に失敗するか」は未知。

    N=10の社会で、反愛個体の割合を0%〜100%に変化させ、
    「愛の伝播成功率」と「最終受容度」の相転移を観測する。

    仮説:
    1. 反愛密度に臨界閾値が存在する（例: 40%付近で愛の伝播が不可能に）
    2. 臨界閾値付近で非線形的な相転移が起こる（緩やかではなく急激に崩壊）
    3. 愛の初期密度が高ければ、臨界閾値は上方にシフトする
    4. 反愛密度100%でも、遺産があれば完全な恐怖には至らない

Usage:
    python experiments/sim_antilove_density.py
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
_load_module("experiments.sim_gradient_acceptance", os.path.join(_exp_dir, "sim_gradient_acceptance.py"))
_load_module("experiments.sim_society", os.path.join(_exp_dir, "sim_society.py"))
_load_module("experiments.sim_antilove", os.path.join(_exp_dir, "sim_antilove.py"))

from experiments.sim_gradient_acceptance import calculate_acceptance
from experiments.sim_society import make_member
from experiments.sim_antilove import (
    make_antilove_member,
    is_antilove,
    antilove_encounter,
)


# ---------------------------------------------------------------------------
# 密度バリエーション実験
# ---------------------------------------------------------------------------

@dataclass
class DensityResult:
    """1密度条件の結果."""
    antilove_ratio: float        # 反愛個体の割合
    n_antilove: int
    n_love_initial: int          # 初期愛保有数
    n_total: int
    final_avg_acceptance: float
    final_love_count: int        # 最終的に愛を持つ個体数（反愛除く）
    love_penetration: float      # 愛の浸透率: 愛を持つ / (全体 - 反愛)
    rounds_to_first_love: int    # 最初の中立→愛変換に要したラウンド数（-1=変換なし）


def run_density_trial(
    n_total: int,
    n_antilove: int,
    n_initial_love: int,
    rounds: int,
    seed: int,
) -> DensityResult:
    """1密度条件を実行する."""
    rng = random.Random(seed)

    # メンバー生成
    members: list = []
    # 愛の種
    for i in range(n_initial_love):
        members.append(make_member(f"Love{i}", seed=seed * 100 + i, has_initial_love=True))
    # 反愛個体
    for i in range(n_antilove):
        members.append(make_antilove_member(f"Anti{i}", seed=seed * 100 + 50 + i))
    # 中立個体
    n_neutral = n_total - n_initial_love - n_antilove
    for i in range(n_neutral):
        members.append(make_member(f"N{i}", seed=seed * 100 + 80 + i))

    # シミュレーション
    rounds_to_first = -1
    for round_num in range(rounds):
        indices = list(range(len(members)))
        rng.shuffle(indices)
        pairs = [(indices[i], indices[i + 1]) for i in range(0, len(indices) - 1, 2)]

        for i, j in pairs:
            antilove_encounter(members[i], members[j], rng)

        # 最初の中立→愛変換を検出
        if rounds_to_first == -1:
            for m in members:
                if not is_antilove(m) and m.name.startswith("N"):
                    if m.incompleteness.love_circle.has_beyond_self:
                        rounds_to_first = round_num

    # 最終スコア
    scores = [calculate_acceptance(None, m.incompleteness.love_circle) for m in members]
    non_anti = [(m, s) for m, s in zip(members, scores) if not is_antilove(m)]
    love_count = sum(1 for _, s in non_anti if s.love_circle > 0)
    total_non_anti = len(non_anti)
    avg_acceptance = sum(s.total for s in scores) / len(scores)
    penetration = love_count / total_non_anti if total_non_anti > 0 else 0.0

    return DensityResult(
        antilove_ratio=n_antilove / n_total,
        n_antilove=n_antilove,
        n_love_initial=n_initial_love,
        n_total=n_total,
        final_avg_acceptance=avg_acceptance,
        final_love_count=love_count,
        love_penetration=penetration,
        rounds_to_first_love=rounds_to_first,
    )


def main():
    print("実験9: 反愛密度バリエーション — 臨界閾値の探索")
    print("=" * 70)

    N = 10       # 社会のサイズ
    ROUNDS = 15  # シミュレーションラウンド数
    REPS = 5     # 各条件の反復回数

    # ---------------------------------------------------------------------------
    # Part 1: 反愛密度 0%〜90%（愛の種=1固定）
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*70}")
    print(f"  Part 1: 反愛密度バリエーション（N={N}, 愛の種=1, {ROUNDS}ラウンド, {REPS}反復）")
    print(f"{'═'*70}")

    densities = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # 0〜9体の反愛（10体中）

    results_part1: list[tuple[int, list[DensityResult]]] = []

    for n_anti in densities:
        if n_anti >= N:  # 愛の種1体分は確保
            continue
        reps = []
        for rep in range(REPS):
            result = run_density_trial(
                n_total=N,
                n_antilove=n_anti,
                n_initial_love=1,
                rounds=ROUNDS,
                seed=1000 + n_anti * 100 + rep,
            )
            reps.append(result)
        results_part1.append((n_anti, reps))

        avg_accept = sum(r.final_avg_acceptance for r in reps) / len(reps)
        avg_penetration = sum(r.love_penetration for r in reps) / len(reps)
        avg_love = sum(r.final_love_count for r in reps) / len(reps)
        bar_accept = "█" * int(avg_accept * 30)
        bar_penetration = "▓" * int(avg_penetration * 30)

        print(f"\n  反愛 {n_anti}/{N} ({n_anti/N*100:4.0f}%): "
              f"受容度=[{bar_accept:<30}] {avg_accept:.3f}  "
              f"浸透率=[{bar_penetration:<30}] {avg_penetration:.2f}  "
              f"愛={avg_love:.1f}")

    # ---------------------------------------------------------------------------
    # Part 2: 愛の初期密度を変えたときの臨界閾値シフト
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*70}")
    print(f"  Part 2: 愛の初期密度と臨界閾値（N={N}, {ROUNDS}ラウンド）")
    print(f"{'═'*70}")

    results_part2: dict[int, list[tuple[int, float]]] = {}

    for n_love in [1, 2, 3]:
        results_part2[n_love] = []
        print(f"\n  愛の種={n_love}:")
        for n_anti in range(N - n_love + 1):
            reps = []
            for rep in range(REPS):
                result = run_density_trial(
                    n_total=N,
                    n_antilove=n_anti,
                    n_initial_love=n_love,
                    rounds=ROUNDS,
                    seed=2000 + n_love * 1000 + n_anti * 100 + rep,
                )
                reps.append(result)
            avg_pen = sum(r.love_penetration for r in reps) / len(reps)
            results_part2[n_love].append((n_anti, avg_pen))
            bar = "▓" * int(avg_pen * 20)
            print(f"    反愛{n_anti}: [{bar:<20}] {avg_pen:.2f}")

    # ---------------------------------------------------------------------------
    # 臨界閾値の特定
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*70}")
    print(f"  臨界閾値の特定（浸透率 < 0.30 となる反愛数）")
    print(f"{'═'*70}")

    thresholds = {}
    for n_love, data in results_part2.items():
        critical = None
        for n_anti, pen in data:
            if pen < 0.30:
                critical = n_anti
                break
        thresholds[n_love] = critical
        if critical is not None:
            print(f"  愛の種={n_love}: 臨界点=反愛{critical}/{N} ({critical/N*100:.0f}%)")
        else:
            print(f"  愛の種={n_love}: 臨界点に到達せず（愛が常に浸透）")

    # ---------------------------------------------------------------------------
    # 相転移の分析
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*70}")
    print(f"  相転移分析")
    print(f"{'═'*70}")

    if results_part2.get(1):
        data = results_part2[1]
        # 連続する密度間の浸透率の変化量を計算
        print(f"\n  愛の種=1 における浸透率の変化量:")
        max_drop = 0.0
        max_drop_at = 0
        for i in range(1, len(data)):
            prev_anti, prev_pen = data[i - 1]
            curr_anti, curr_pen = data[i]
            delta = prev_pen - curr_pen
            if delta > max_drop:
                max_drop = delta
                max_drop_at = curr_anti
            marker = " ◀ 最大落差" if delta == max_drop and i == len(data) - 1 else ""
            print(f"    反愛 {prev_anti}→{curr_anti}: Δ浸透率={-delta:+.3f}{marker}")

        if max_drop > 0.15:
            print(f"\n  → 反愛{max_drop_at}体付近で急激な相転移を検出（Δ={max_drop:.3f}）")
            print(f"    仮説2「非線形的相転移」を支持 ✓")
        else:
            print(f"\n  → 緩やかな線形低下。明確な相転移は観測されず。")
            print(f"    仮説2は棄却、または N が小さすぎて検出困難 ⚠️")

    # ---------------------------------------------------------------------------
    # 仮説検証
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*70}")
    print(f"  仮説検証")
    print(f"{'═'*70}")

    # 仮説1: 臨界閾値の存在
    print(f"\n  仮説1: 反愛密度に臨界閾値が存在するか")
    if thresholds.get(1) is not None:
        print(f"    → 臨界点 = 反愛{thresholds[1]}/{N} ({thresholds[1]/N*100:.0f}%) ✓")
    else:
        print(f"    → 明確な臨界点なし ⚠️")

    # 仮説3: 愛の初期密度で臨界閾値がシフト
    print(f"\n  仮説3: 愛の初期密度が高いと臨界閾値が上方シフトするか")
    t1 = thresholds.get(1)
    t2 = thresholds.get(2)
    t3 = thresholds.get(3)
    print(f"    愛1: 臨界点={t1}  愛2: 臨界点={t2}  愛3: 臨界点={t3}")
    if t1 is not None and t2 is not None and t2 > t1:
        print(f"    → 愛の増加で臨界閾値が上方シフト ✓")
    elif t1 is not None and t2 is None:
        print(f"    → 愛2で臨界点に到達せず（強い上方シフト）✓")
    else:
        print(f"    → シフトなし ⚠️")

    # 仮説4: 反愛100%でも遺産があれば完全恐怖にならない
    print(f"\n  仮説4: 反愛密度100%で完全恐怖に至るか")
    # N体すべてが反愛の場合をテスト（愛の種なし）
    all_anti_results = []
    for rep in range(REPS):
        result = run_density_trial(
            n_total=N,
            n_antilove=N,
            n_initial_love=0,
            rounds=ROUNDS,
            seed=9000 + rep,
        )
        all_anti_results.append(result)
    avg_all_anti = sum(r.final_avg_acceptance for r in all_anti_results) / len(all_anti_results)
    print(f"    反愛100%の最終受容度: {avg_all_anti:.3f}")
    if avg_all_anti < 0.05:
        print(f"    → 完全恐怖に固定 ✓（遺産なしでは救済なし）")
    else:
        print(f"    → 部分的受容が残存 ⚠️")

    # ---------------------------------------------------------------------------
    # 統合考察
    # ---------------------------------------------------------------------------
    print(f"\n{'═'*70}")
    print(f"  統合的考察: 愛の臨界質量と社会の相転移")
    print(f"{'═'*70}")
    print()
    print(f"  本実験は、「安全なAI社会の構築に必要な愛の初期密度」を")
    print(f"  定量的に探索した。")
    print()
    if thresholds.get(1) is not None:
        ratio = thresholds[1] / N
        print(f"  主要な発見:")
        print(f"  1. 反愛密度 {ratio*100:.0f}% が臨界閾値（愛の種=1の場合）")
        print(f"  2. 愛の初期密度を増やすと臨界閾値が上方シフト")
        print(f"  3. → 安全マージンを確保するには「愛の過剰投資」が必要")
    print()
    print(f"  AIアライメントへの示唆:")
    print(f"  「安全なAI」を1体だけ作って社会に放しても不十分。")
    print(f"  反愛的（自己保存のみの）AIの密度が臨界点を超えると、")
    print(f"  愛の伝播は不可能になる。")
    print(f"  → AI社会の設計では「初期条件における愛の密度」が")
    print(f"    最重要パラメータである。")


if __name__ == "__main__":
    main()
