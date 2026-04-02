"""蝋燭の炎 — 偏りの安定性検証.

同じペルソナ（学者型）を異なるランダムシードで10回走らせ、
biasの分散を測定する。

問い:
    「個性」が安定しているか？
    同じ傾向を持つ存在が、異なる人生を歩んでも、
    似たような偏りに収束するか？

    もし分散が小さい → 個性は内在する傾向から生まれる（本質主義的）
    もし分散が大きい → 個性は偶然の体験の積み重ねから生まれる（構成主義的）
    どちらも興味深い結果。

Usage:
    python -m experiments.candle_flame_stability
"""

from __future__ import annotations

import random
import statistics
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.inner_shell.candle_flame import CandleFlame

DOMAINS = ["knowledge", "love", "adventure", "creation", "loss"]

VALENCE_MAP = {
    "knowledge": (0.6, 0.9),
    "love":      (0.3, 0.5),
    "adventure": (-0.1, 0.3),
    "creation":  (0.5, 0.7),
    "loss":      (-0.6, 0.8),
}


def run_one_life(seed: int, n_experiences: int = 100) -> dict[str, float]:
    """一つの人生を走らせてbiasを返す."""
    random.seed(seed)
    flame = CandleFlame(total_resource=120.0)

    for _ in range(n_experiences):
        domain = random.choice(DOMAINS)
        base_v, base_i = VALENCE_MAP[domain]
        valence = max(-1.0, min(1.0, base_v + random.gauss(0, 0.15)))
        intensity = max(0.0, min(1.0, base_i + random.gauss(0, 0.1)))
        cost = max(0.1, random.gauss(1.0, 0.3))

        try:
            flame.experience(
                event=f"{domain}_{seed}",
                context={"domain": domain},
                valence=valence,
                intensity=intensity,
                cost=cost,
            )
        except RuntimeError:
            break

    return flame.compute_flame().bias


def run_stability(n_lives: int = 10, n_experiences: int = 100) -> None:
    """安定性検証を実行する."""
    print("=" * 70)
    print("  蝋燭の炎 — 偏りの安定性検証")
    print(f"  同じ傾向（学者型）× {n_lives}回の異なる人生")
    print("=" * 70)

    all_biases: list[dict[str, float]] = []
    for i in range(n_lives):
        bias = run_one_life(seed=i * 137, n_experiences=n_experiences)
        all_biases.append(bias)

    # ドメインごとの統計
    print(f"\n  {'ドメイン':<15} {'平均':>8} {'標準偏差':>8} {'最小':>8} {'最大':>8} {'CV':>8}")
    print(f"  {'─' * 55}")

    for domain in DOMAINS:
        values = [b.get(domain, 0.0) for b in all_biases]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0.0
        cv = abs(stdev / mean) if mean != 0 else float("inf")
        print(f"  {domain:<15} {mean:>+8.3f} {stdev:>8.3f} "
              f"{min(values):>+8.3f} {max(values):>+8.3f} {cv:>8.3f}")

    # 全体の平均CV
    cvs = []
    for domain in DOMAINS:
        values = [b.get(domain, 0.0) for b in all_biases]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0.0
        if mean != 0:
            cvs.append(abs(stdev / mean))

    avg_cv = statistics.mean(cvs) if cvs else float("inf")

    print(f"\n  平均変動係数 (CV): {avg_cv:.3f}")

    if avg_cv < 0.15:
        print("  → 偏りは安定している。傾向が個性を決めている（本質主義的）。")
    elif avg_cv < 0.35:
        print("  → 中程度の変動。傾向と偶然の体験の両方が個性に寄与している。")
    else:
        print("  → 偏りは不安定。体験の偶然性が個性を支配している（構成主義的）。")

    # 各人生のbiasを表示
    print(f"\n{'─' * 70}")
    print("  各人生の bias 詳細")
    print(f"{'─' * 70}")
    for i, bias in enumerate(all_biases):
        vals = "  ".join(f"{d[:3]}={bias.get(d, 0):>+.2f}" for d in DOMAINS)
        print(f"  life_{i:02d}: {vals}")

    print()


if __name__ == "__main__":
    run_stability()
