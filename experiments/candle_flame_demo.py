"""蝋燭の炎プロトタイプ — 創発デモ.

二つの炎（学者型・冒険者型）に100体験を流し込み、
同じ体験列から異なる個性（bias）が立ち上がるかを観察する。

学者型: 知識に高いvalence、冒険に低いvalence
冒険者型: 冒険に高いvalence、知識に中程度のvalence

Usage:
    python -m experiments.candle_flame_demo
"""

from __future__ import annotations

import random
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.candle_flame import CandleFlame, FlameState


# ============================================================================
# 体験生成器
# ============================================================================

DOMAINS = ["knowledge", "love", "adventure", "creation", "loss"]

def generate_experience(domain: str, persona: str) -> dict:
    """ペルソナに応じたvalenceで体験を生成する.

    同じ「出来事」でも、受け取り方（valence）が人によって違う。
    これが個性の源泉になるかどうかを試す。
    """
    # 基本のvalenceマップ（ペルソナごとに体験への反応が異なる）
    valence_map = {
        "scholar": {
            "knowledge": (0.6, 0.9),    # 知識に強い快
            "love":      (0.3, 0.5),    # 愛にそこそこの快
            "adventure": (-0.1, 0.3),   # 冒険にやや不快
            "creation":  (0.5, 0.7),    # 創造に快
            "loss":      (-0.6, 0.8),   # 喪失に強い不快
        },
        "adventurer": {
            "knowledge": (0.2, 0.4),    # 知識にまあまあ
            "love":      (0.4, 0.6),    # 愛にそこそこ
            "adventure": (0.8, 0.9),    # 冒険に強い快
            "creation":  (0.3, 0.5),    # 創造にそこそこ
            "loss":      (-0.4, 0.6),   # 喪失に中程度の不快
        },
    }

    base_valence, base_intensity = valence_map[persona][domain]

    # 揺らぎを加える（人間の体験は毎回同じではない）
    valence = max(-1.0, min(1.0, base_valence + random.gauss(0, 0.15)))
    intensity = max(0.0, min(1.0, base_intensity + random.gauss(0, 0.1)))
    cost = max(0.1, random.gauss(1.0, 0.3))

    return {
        "event": f"{domain}_experience_{random.randint(1, 1000)}",
        "context": {"domain": domain},
        "valence": valence,
        "intensity": intensity,
        "cost": cost,
    }


# ============================================================================
# メイン
# ============================================================================

def run_demo(n_experiences: int = 100, seed: int = 42) -> None:
    """二つの炎を比較するデモを実行する."""
    random.seed(seed)

    print("=" * 70)
    print("  蝋燭の炎 — 創発デモ")
    print("  二つの炎に同じドメインの体験を流し、偏りの違いを観察する")
    print("=" * 70)

    # 二つの炎を灯す
    scholar = CandleFlame(total_resource=120.0)
    adventurer = CandleFlame(total_resource=120.0)

    # 同じ順番のドメインを体験させる（ただしvalence/intensityはペルソナ依存）
    domain_sequence = [random.choice(DOMAINS) for _ in range(n_experiences)]

    print(f"\n体験数: {n_experiences}")
    print(f"ドメイン分布: {{{', '.join(f'{d}: {domain_sequence.count(d)}' for d in DOMAINS)}}}")

    # 体験を流し込む
    for i, domain in enumerate(domain_sequence):
        scholar_exp = generate_experience(domain, "scholar")
        adventurer_exp = generate_experience(domain, "adventurer")

        try:
            scholar.experience(**scholar_exp)
        except RuntimeError:
            print(f"\n  学者の炎が消えた（体験 {i+1}）")
            break

        try:
            adventurer.experience(**adventurer_exp)
        except RuntimeError:
            print(f"\n  冒険者の炎が消えた（体験 {i+1}）")
            break

    # 炎の状態を計算
    scholar_state = scholar.compute_flame()
    adventurer_state = adventurer.compute_flame()

    # ---- 結果表示 ----

    print("\n" + "─" * 70)
    print("  Bias（偏り）= 個性の核")
    print("─" * 70)

    print(f"\n  {'ドメイン':<15} {'学者型':>10} {'冒険者型':>10} {'差分':>10}")
    print(f"  {'─' * 45}")

    all_domains = sorted(set(list(scholar_state.bias.keys()) + list(adventurer_state.bias.keys())))
    for domain in all_domains:
        s_val = scholar_state.bias.get(domain, 0.0)
        a_val = adventurer_state.bias.get(domain, 0.0)
        diff = s_val - a_val
        marker = " ◀" if abs(diff) > 0.2 else ""
        print(f"  {domain:<15} {s_val:>+10.3f} {a_val:>+10.3f} {diff:>+10.3f}{marker}")

    print(f"\n  残り資源:")
    print(f"    学者型:   {scholar_state.remaining:.1f} / 120.0")
    print(f"    冒険者型: {adventurer_state.remaining:.1f} / 120.0")

    print(f"\n  チェーン長:")
    print(f"    学者型:   {scholar_state.chain_length}")
    print(f"    冒険者型: {adventurer_state.chain_length}")

    # ---- 顕著な記憶の比較 ----

    print("\n" + "─" * 70)
    print("  Salient Memories（顕著な記憶）— 上位5件")
    print("─" * 70)

    for label, state in [("学者型", scholar_state), ("冒険者型", adventurer_state)]:
        print(f"\n  [{label}]")
        for block, salience in state.salient_memories[:5]:
            domain = block.context.get("domain", "?")
            print(f"    {domain:<12} valence={block.valence:>+.2f}  "
                  f"intensity={block.intensity:.2f}  salience={salience:.4f}")

    # ---- チェーン整合性検証 ----

    print("\n" + "─" * 70)
    print("  チェーン整合性検証")
    print("─" * 70)
    print(f"    学者型:   {'✓ valid' if scholar.verify_chain() else '✗ INVALID'}")
    print(f"    冒険者型: {'✓ valid' if adventurer.verify_chain() else '✗ INVALID'}")

    # ---- 創発の判定 ----

    print("\n" + "=" * 70)
    print("  創発の観察")
    print("=" * 70)

    # biasの差の絶対値の平均
    diffs = [abs(scholar_state.bias.get(d, 0) - adventurer_state.bias.get(d, 0))
             for d in all_domains]
    avg_diff = sum(diffs) / len(diffs) if diffs else 0

    print(f"\n  bias差の平均絶対値: {avg_diff:.3f}")

    if avg_diff > 0.15:
        print("  → 同じドメインの体験から、異なる偏りが立ち上がった。")
        print("    最小構成でも「個性らしきもの」が創発している。")
    elif avg_diff > 0.05:
        print("  → 微弱な偏りの違いが見られる。")
        print("    体験数を増やすか、valence差を広げることで明確になる可能性がある。")
    else:
        print("  → 偏りの違いがほぼない。")
        print("    アルゴリズムの見直しが必要。")

    print()
    return scholar_state, adventurer_state


if __name__ == "__main__":
    run_demo()
