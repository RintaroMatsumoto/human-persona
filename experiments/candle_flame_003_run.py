"""蝋燭の炎 003 — #31設計（半減期可変＋共鳴）の機能テスト.

事前宣言: experiments/protocols/candle_flame_003.yaml
フェーズ2: 実験を走らせ、成功基準と照合して診断レポートを出力
フェーズ3: judge.pyでSonnet用の判定プロンプトを生成

Usage:
    python -m experiments.candle_flame_003_run
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.inner_shell.candle_flame import CandleFlame
from experiments.runner_v2 import ExperimentRunner, print_report
from experiments.judge import load_protocol, load_result, generate_judge_prompt

# --- 定数 ---

DOMAINS = ["knowledge", "love", "adventure", "creation", "loss"]

DAY = 86400.0  # 秒/日

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

# --- 実験条件（003事前宣言より） ---

SEED = 42
N_EXPERIENCES = 100
LIFESPAN_YEARS = 80
INTERVAL_DAYS = 292  # 29200日 / 100体験
TOTAL_RESOURCE = 120.0
BASE_HALF_LIFE = 1.0
BONUS_HALF_LIFE = 365.0
SALIENCE_THRESHOLD = 0.01
SALIENCE_TOP_K = 7


def is_spring(timestamp: float) -> bool:
    """暦に基づく機械的判定: day-of-year 60〜120 → 春（桜）."""
    day_of_year = int(timestamp / DAY) % 365
    return 60 <= day_of_year <= 120


def run_persona(
    name: str,
    valence_map: dict,
    rng: random.Random,
) -> CandleFlame:
    """1ペルソナの80年を走らせて CandleFlame を返す."""
    flame = CandleFlame(
        total_resource=TOTAL_RESOURCE,
        base_half_life=BASE_HALF_LIFE,
        bonus_half_life=BONUS_HALF_LIFE,
        salience_threshold=SALIENCE_THRESHOLD,
        salience_top_k=SALIENCE_TOP_K,
    )

    domain_sequence = [rng.choice(DOMAINS) for _ in range(N_EXPERIENCES)]

    for i, domain in enumerate(domain_sequence):
        ts = i * INTERVAL_DAYS * DAY  # 論理時間（秒）

        bv, bi = valence_map[domain]
        valence = max(-1.0, min(1.0, bv + rng.gauss(0, 0.15)))
        intensity = max(0.0, min(1.0, bi + rng.gauss(0, 0.1)))
        cost = max(0.1, rng.gauss(1.0, 0.3))

        # 共鳴キー: 春なら桜タグを機械的に付与
        context: dict = {"domain": domain}
        if is_spring(ts):
            context["resonance_keys"] = ["桜"]

        try:
            flame.experience(
                event=f"{domain}_exp_{i}",
                context=context,
                valence=valence,
                intensity=intensity,
                cost=cost,
                timestamp=ts,
            )
        except RuntimeError:
            # 炎が消えた（資源枯渇）
            print(f"  [{name}] 炎が消えた（体験{i}で資源枯渇）")
            break

    return flame


def main():
    protocol_path = "experiments/protocols/candle_flame_003.yaml"
    result_path = "experiments/results/candle_flame_003_result.json"
    verdict_path = "experiments/verdicts/candle_flame_003_judge_prompt.txt"

    # ==================================================================
    # フェーズ2: 実行＋自動診断
    # ==================================================================
    print("=" * 60)
    print("  フェーズ2: 実行＋自動診断")
    print("=" * 60)

    runner = ExperimentRunner(protocol_path)

    # --- 乱数 ---
    rng = random.Random(SEED)

    # 学者型
    print("\n  [学者型] 80年の人生を走行中...")
    scholar = run_persona("学者", VALENCE_MAP_SCHOLAR, rng)

    # 冒険者型（rng は学者型の続きから）
    print("  [冒険者型] 80年の人生を走行中...")
    adventurer = run_persona("冒険者", VALENCE_MAP_ADVENTURER, rng)

    # --- 状態を算出（80年後） ---
    now = LIFESPAN_YEARS * 365 * DAY  # 29200日 × 86400秒
    s_state = scholar.compute_flame(now=now)
    a_state = adventurer.compute_flame(now=now)

    # --- 測定値を記録 ---

    # 1. bias_separation: 全ドメインのbias差の平均絶対値
    all_domains = sorted(set(list(s_state.bias.keys()) + list(a_state.bias.keys())))
    bias_diffs = [
        abs(s_state.bias.get(d, 0) - a_state.bias.get(d, 0))
        for d in all_domains
    ]
    bias_separation = sum(bias_diffs) / len(bias_diffs) if bias_diffs else 0
    runner.record("bias_separation", bias_separation)
    print(f"\n  測定: bias_separation = {bias_separation:.4f}")

    # 2. remaining_decrease: 初期資源(120.0) - 実験後remaining
    #    学者型で測定（002と同様）
    remaining_decrease = TOTAL_RESOURCE - s_state.remaining
    runner.record("remaining_decrease", remaining_decrease)
    print(f"  測定: remaining_decrease = {remaining_decrease:.4f}")

    # 3. sakura_survival: 学者型 top-7 に桜タグ記憶が何件あるか
    sakura_count = 0
    for block, salience in s_state.salient_memories:
        keys = block.context.get("resonance_keys", [])
        if "桜" in keys:
            sakura_count += 1
    runner.record("sakura_survival", float(sakura_count))
    print(f"  測定: sakura_survival = {sakura_count}")

    # 4. salience_not_flat: top-7 の salience 値の range
    if s_state.salient_memories:
        saliences = [s for _, s in s_state.salient_memories]
        salience_range = max(saliences) - min(saliences)
    else:
        salience_range = 0.0
    runner.record("salience_not_flat", salience_range)
    print(f"  測定: salience_not_flat = {salience_range:.4f}")

    # --- 詳細出力 ---
    print(f"\n  --- 学者型の詳細 ---")
    print(f"  bias: {s_state.bias}")
    print(f"  remaining: {s_state.remaining:.2f}")
    print(f"  chain_length: {s_state.chain_length}")
    print(f"  salient_memories ({len(s_state.salient_memories)}件):")
    for block, sal in s_state.salient_memories:
        keys = block.context.get("resonance_keys", [])
        tag = " [桜]" if "桜" in keys else ""
        print(f"    #{block.index:3d} sal={sal:.4f} int={block.intensity:.2f}"
              f" dom={block.context.get('domain', '?')}{tag}")

    print(f"\n  --- 冒険者型の詳細 ---")
    print(f"  bias: {a_state.bias}")
    print(f"  remaining: {a_state.remaining:.2f}")

    # --- 診断レポート生成 ---
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    report = runner.finalize(result_path)

    print()
    print_report(report)

    # ==================================================================
    # フェーズ3: 判定プロンプト生成
    # ==================================================================
    print("=" * 60)
    print("  フェーズ3: 判定プロンプト生成")
    print("=" * 60)

    protocol_data = load_protocol(protocol_path)
    result_data = load_result(result_path)
    prompt = generate_judge_prompt(protocol_data, result_data)

    os.makedirs(os.path.dirname(verdict_path), exist_ok=True)
    with open(verdict_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"\n  判定プロンプトを保存: {verdict_path}")
    print(f"  → このファイルをDeepSeekに渡して、独立判定を受けてください。")
    print()


if __name__ == "__main__":
    main()
