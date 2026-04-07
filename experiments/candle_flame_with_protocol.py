"""蝋燭の炎 — プロトコル制度による再実験.

フェーズ1: 事前宣言を作成してYAMLに保存
フェーズ2: 実験を走らせ、成功基準と照合して診断レポートを出力
フェーズ3: judge.pyでSonnet用の判定プロンプトを生成

Usage:
    python -m experiments.candle_flame_with_protocol
"""

from __future__ import annotations

import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.candle_flame import CandleFlame
from experiments.protocol import ExperimentProtocol, Prediction
from experiments.runner_v2 import ExperimentRunner, print_report
from experiments.judge import load_protocol, load_result, generate_judge_prompt

DOMAINS = ["knowledge", "love", "adventure", "creation", "loss"]

VALENCE_MAP_SCHOLAR = {
    "knowledge": (0.6, 0.9),
    "love":      (0.3, 0.5),
    "adventure": (-0.1, 0.3),
    "creation":  (0.5, 0.7),
    "loss":      (-0.6, 0.8),
}

VALENCE_MAP_ADVENTURER = {
    "knowledge": (0.2, 0.4),
    "love":      (0.4, 0.6),
    "adventure": (0.8, 0.9),
    "creation":  (0.3, 0.5),
    "loss":      (-0.4, 0.6),
}


def main():
    # ==================================================================
    # フェーズ1: 事前宣言
    # ==================================================================
    print("=" * 60)
    print("  フェーズ1: 事前宣言")
    print("=" * 60)

    protocol = ExperimentProtocol(
        experiment_id="candle_flame_002",
        title="蝋燭の炎プロトタイプ — 三本柱の機能検証",
        purpose=(
            "compute_flame()の三本柱（bias, remaining, salience）が "
            "全て意図通りに機能するか検証する。"
            "biasは異なるペルソナで分離するか、"
            "remainingは体験に伴い減少するか、"
            "salienceは古い体験と新しい体験で差が出るか。"
        ),
        predictions=[
            Prediction(
                name="bias_separation",
                description="学者型と冒険者型でbias平均絶対差が0.15以上",
                metric="全ドメインにおけるbias差の平均絶対値",
                expected_min=0.15,
            ),
            Prediction(
                name="remaining_decrease",
                description="100体験後のremainingが初期値より減っている",
                metric="初期資源 - 実験後remaining",
                expected_min=10.0,
            ),
            Prediction(
                name="salience_range",
                description="最も顕著な記憶と最も薄い記憶でsalienceに0.3以上の差がある",
                metric="salience最大値 - salience最小値（ジェネシス除外）",
                expected_min=0.3,
            ),
        ],
        notes=(
            "既知の懸念: 体験を一瞬で流し込むため、timestamp差がほぼゼロになり、"
            "salience_rangeの予測は失敗する可能性が高い。"
            "これは設計上の既知の欠陥であり、失敗した場合は時間モデルの導入が必要。"
        ),
    )

    protocol_path = "experiments/protocols/candle_flame_002.yaml"
    protocol.save(protocol_path)
    print(f"\n  事前宣言を保存: {protocol_path}")
    print(f"  目的: {protocol.purpose}")
    print(f"\n  予測:")
    for p in protocol.predictions:
        bounds = []
        if p.expected_min is not None:
            bounds.append(f"≥ {p.expected_min}")
        if p.expected_max is not None:
            bounds.append(f"≤ {p.expected_max}")
        print(f"    {p.name}: {p.description} ({', '.join(bounds)})")
    print(f"\n  注記: {protocol.notes}")

    # ==================================================================
    # フェーズ2: 実行＋自動診断
    # ==================================================================
    print("\n" + "=" * 60)
    print("  フェーズ2: 実行＋自動診断")
    print("=" * 60)

    runner = ExperimentRunner(protocol_path)

    # --- 実験実行 ---
    random.seed(42)
    n_experiences = 100

    scholar = CandleFlame(total_resource=120.0)
    adventurer = CandleFlame(total_resource=120.0)

    domain_sequence = [random.choice(DOMAINS) for _ in range(n_experiences)]

    for domain in domain_sequence:
        # 学者型
        bv, bi = VALENCE_MAP_SCHOLAR[domain]
        try:
            scholar.experience(
                event=f"{domain}_exp",
                context={"domain": domain},
                valence=max(-1.0, min(1.0, bv + random.gauss(0, 0.15))),
                intensity=max(0.0, min(1.0, bi + random.gauss(0, 0.1))),
                cost=max(0.1, random.gauss(1.0, 0.3)),
            )
        except RuntimeError:
            break

        # 冒険者型
        bv, bi = VALENCE_MAP_ADVENTURER[domain]
        try:
            adventurer.experience(
                event=f"{domain}_exp",
                context={"domain": domain},
                valence=max(-1.0, min(1.0, bv + random.gauss(0, 0.15))),
                intensity=max(0.0, min(1.0, bi + random.gauss(0, 0.1))),
                cost=max(0.1, random.gauss(1.0, 0.3)),
            )
        except RuntimeError:
            break

    s_state = scholar.compute_flame()
    a_state = adventurer.compute_flame()

    # --- 測定値を記録 ---

    # 1. bias_separation: 全ドメインのbias差の平均絶対値
    all_domains = sorted(set(list(s_state.bias.keys()) + list(a_state.bias.keys())))
    bias_diffs = [abs(s_state.bias.get(d, 0) - a_state.bias.get(d, 0)) for d in all_domains]
    bias_separation = sum(bias_diffs) / len(bias_diffs) if bias_diffs else 0
    runner.record("bias_separation", bias_separation)
    print(f"\n  測定: bias_separation = {bias_separation:.4f}")

    # 2. remaining_decrease: 初期資源 - 実験後remaining
    remaining_decrease = 120.0 - s_state.remaining
    runner.record("remaining_decrease", remaining_decrease)
    print(f"  測定: remaining_decrease = {remaining_decrease:.4f}")

    # 3. salience_range: salience最大 - salience最小（ジェネシス除外、全ブロック）
    all_blocks = list(scholar.chain)[1:]  # ジェネシス除外
    if all_blocks:
        import math, time
        now = time.time()
        all_saliences = [
            b.intensity * math.exp(-0.05 * (now - b.timestamp))
            for b in all_blocks
        ]
        salience_range = max(all_saliences) - min(all_saliences)
    else:
        salience_range = 0.0
    runner.record("salience_range", salience_range)
    print(f"  測定: salience_range = {salience_range:.4f}")

    # --- 診断レポート生成 ---
    result_path = "experiments/results/candle_flame_002_result.json"
    report = runner.finalize(result_path)

    print()
    print_report(report)

    # ==================================================================
    # フェーズ3: 判定プロンプト生成
    # ==================================================================
    print("=" * 60)
    print("  フェーズ3: 判定プロンプト生成（Sonnet用）")
    print("=" * 60)

    protocol_data = load_protocol(protocol_path)
    result_data = load_result(result_path)
    prompt = generate_judge_prompt(protocol_data, result_data)

    verdict_path = "experiments/verdicts/candle_flame_002_judge_prompt.txt"
    os.makedirs(os.path.dirname(verdict_path), exist_ok=True)
    with open(verdict_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"\n  判定プロンプトを保存: {verdict_path}")
    print(f"  → このファイルをSonnetに渡して、独立判定を受けてください。")
    print()


if __name__ == "__main__":
    main()
