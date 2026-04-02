"""実験プロトコル制度 — フェーズ3: 独立判定.

事前宣言（protocol.yaml）と診断レポート（result.json）を受け取り、
Sonnetに渡す判定プロンプトを生成する。

実施者（Opus/クロミ）は判定に関与しない。
判定者（Sonnet）は事前宣言と結果だけを見て判断する。

使い方:
    python -m experiments.judge \\
        experiments/protocols/candle_flame_001.yaml \\
        experiments/results/candle_flame_001_result.json

    → 判定プロンプトが標準出力に表示される
    → これをSonnetに渡す
"""

from __future__ import annotations

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def load_protocol(path: str) -> dict:
    """プロトコルYAMLを読み込む."""
    if not HAS_YAML:
        raise RuntimeError("PyYAML is required. pip install pyyaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_result(path: str) -> dict:
    """診断レポートJSONを読み込む."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_judge_prompt(protocol: dict, result: dict) -> str:
    """Sonnetに渡す判定プロンプトを生成する.

    プロンプトの構造:
        1. あなたの役割（独立判定者）
        2. 事前宣言の内容
        3. 実行結果の内容
        4. 判定基準
        5. 出力フォーマット
    """
    # 予測の詳細を整形
    prediction_lines = []
    for p in protocol.get("predictions", []):
        bounds = []
        if p.get("expected_min") is not None:
            bounds.append(f"≥ {p['expected_min']}")
        if p.get("expected_max") is not None:
            bounds.append(f"≤ {p['expected_max']}")
        bound_str = ", ".join(bounds) if bounds else "制約なし"
        prediction_lines.append(
            f"  - {p['name']}: {p['description']} (基準: {bound_str})"
        )

    # 結果の詳細を整形
    result_lines = []
    for r in result.get("results", []):
        status = "PASS" if r["passed"] else "FAIL"
        actual = f"{r['actual']:.4f}" if r["actual"] is not None else "未測定"
        result_lines.append(
            f"  - [{status}] {r['name']}: 実測値={actual}, 理由={r['reason']}"
        )

    prompt = f"""あなたは実験の独立判定者です。
実施者とは別の存在として、事前宣言と実行結果を照合し、
実験が目的を達成したかを判定してください。

実施者の解釈や感想は一切含まれていません。
数値と基準だけを見て判断してください。

===== 事前宣言 =====
実験ID: {protocol.get('experiment_id', '不明')}
タイトル: {protocol.get('title', '不明')}
目的: {protocol.get('purpose', '不明')}
作成日時: {protocol.get('created_at', '不明')}

予測（成功基準）:
{chr(10).join(prediction_lines)}

===== 実行結果 =====
実行日時: {result.get('executed_at', '不明')}
自動判定: {result.get('summary', '不明')}

各予測の照合:
{chr(10).join(result_lines)}

===== 判定基準 =====
以下の三段階で判定してください:
- SUCCESS: 全ての予測が基準を満たした
- PARTIAL: 一部の予測が基準を満たしたが、一部は未達
- FAILURE: 全てまたは大部分の予測が未達

===== 出力フォーマット =====
以下のフォーマットで判定を出力してください:

判定: [SUCCESS / PARTIAL / FAILURE]
根拠: [各予測の合否を踏まえた判定理由（2-3文）]
未達項目の分析: [FAILの予測について、何が不足しているかの分析]
次のステップへの提言: [実験をどう改善すべきか（1-2文）]
"""
    return prompt


def generate_verdict_file(protocol: dict, result: dict, output_path: str) -> str:
    """判定プロンプトをファイルに保存する."""
    prompt = generate_judge_prompt(protocol, result)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    return output_path


def main():
    """コマンドライン実行."""
    if len(sys.argv) < 3:
        print("使い方: python -m experiments.judge <protocol.yaml> <result.json>")
        print("  オプション: 第3引数で判定プロンプトの保存先を指定")
        sys.exit(1)

    protocol_path = sys.argv[1]
    result_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    protocol = load_protocol(protocol_path)
    result = load_result(result_path)

    prompt = generate_judge_prompt(protocol, result)

    if output_path:
        generate_verdict_file(protocol, result, output_path)
        print(f"判定プロンプトを保存しました: {output_path}")
    else:
        print(prompt)


if __name__ == "__main__":
    main()
