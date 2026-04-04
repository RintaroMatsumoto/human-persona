"""実験プロトコル制度 — フェーズ3: 独立判定.

事前宣言（protocol.yaml）と診断レポート（result.json）を受け取り、
独立判定者（DeepSeek API）に判定を依頼する。

実施者（Opus/クロミ）は判定に関与しない。
判定者は事前宣言と結果だけを見て判断する。

使い方:
    # プロンプト生成のみ（従来互換）
    python -m experiments.judge \\
        experiments/protocols/candle_flame_001.yaml \\
        experiments/results/candle_flame_001_result.json

    # API呼び出しまで実行（独立判定を自動化）
    python -m experiments.judge \\
        experiments/protocols/candle_flame_001.yaml \\
        experiments/results/candle_flame_001_result.json \\
        --execute

    環境変数 DEEPSEEK_API_KEY にAPIキーをセットしておくこと。
"""

from __future__ import annotations

import json
import sys
import os
from datetime import datetime, timezone
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ============================================================================
# DeepSeek API 設定
# ============================================================================

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


# ============================================================================
# プロトコル・結果の読み込み
# ============================================================================

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


# ============================================================================
# 判定プロンプト生成
# ============================================================================

def generate_judge_prompt(protocol: dict, result: dict) -> str:
    """独立判定者に渡す判定プロンプトを生成する.

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

    # 条件を整形
    conditions = protocol.get("conditions", {})
    if conditions:
        conditions_str = json.dumps(conditions, ensure_ascii=False, indent=4)
    else:
        conditions_str = "  （記載なし）"

    prompt = f"""あなたは実験の独立判定者です。
実施者とは別の存在として、事前宣言と実行結果を照合し、
実験が目的を達成したかを判定してください。

実施者の解釈や感想は一切含まれていません。
数値と基準だけを見て判断してください。

===== 事前宣言（AsPredicted準拠） =====
実験ID: {protocol.get('experiment_id', '不明')}
タイトル: {protocol.get('title', '不明')}
作成日時: {protocol.get('created_at', '不明')}

[Q1+Q9] 事前実行の有無: {protocol.get('prior_execution', 'なし')}

[Q2] 目的・仮説: {protocol.get('purpose', '不明')}

[Q4] 実験条件:
{conditions_str}

[Q3+Q5] 予測（成功基準）:
{chr(10).join(prediction_lines)}

[Q6] データ除外ルール: {protocol.get('exclusion_criteria', '特になし')}

[Q7] 試行回数の根拠: {protocol.get('sample_size_rationale', '記載なし')}

[Q8] 既知の限界: {protocol.get('known_limitations', '記載なし')}

===== 実行結果 =====
実行日時: {result.get('executed_at', '不明')}
事前宣言のgit検証: {'済' if result.get('git_verified', False) else '未検証'}
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


# ============================================================================
# DeepSeek API 呼び出し
# ============================================================================

def call_deepseek_api(prompt: str, api_key: str) -> str:
    """DeepSeek Chat APIを呼び出して判定を取得する.

    Args:
        prompt: 判定プロンプト
        api_key: DeepSeek APIキー

    Returns:
        判定者の回答テキスト

    Raises:
        RuntimeError: API呼び出しに失敗した場合
    """
    payload = json.dumps({
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,  # 判定に創造性は不要
    }).encode("utf-8")

    req = Request(
        DEEPSEEK_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"DeepSeek API returned HTTP {e.code}: {body}"
        ) from e
    except URLError as e:
        raise RuntimeError(
            f"DeepSeek APIへの接続に失敗: {e.reason}"
        ) from e


def judge_with_api(
    protocol_path: str,
    result_path: str,
    output_dir: str = "experiments/verdicts",
) -> str:
    """フェーズ3を完全自動化: プロンプト生成→API呼び出し→判定保存.

    Args:
        protocol_path: 事前宣言YAMLのパス
        result_path: 診断レポートJSONのパス
        output_dir: 判定ファイルの保存先ディレクトリ

    Returns:
        保存した判定ファイルのパス

    Raises:
        RuntimeError: APIキーが未設定、またはAPI呼び出し失敗
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "環境変数 DEEPSEEK_API_KEY が設定されていない。\n"
            "export DEEPSEEK_API_KEY=sk-xxxxx"
        )

    protocol = load_protocol(protocol_path)
    result = load_result(result_path)
    prompt = generate_judge_prompt(protocol, result)

    # API呼び出し
    print("  DeepSeek APIに判定を依頼中...")
    verdict_text = call_deepseek_api(prompt, api_key)
    print("  判定を受信しました。")

    # 判定結果をJSON構造で保存
    experiment_id = protocol.get("experiment_id", "unknown")
    verdict = {
        "experiment_id": experiment_id,
        "judge_model": DEEPSEEK_MODEL,
        "judged_at": datetime.now(timezone.utc).isoformat(),
        "protocol_path": protocol_path,
        "result_path": result_path,
        "prompt": prompt,
        "verdict": verdict_text,
    }

    os.makedirs(output_dir, exist_ok=True)
    verdict_path = os.path.join(output_dir, f"{experiment_id}_verdict.json")
    with open(verdict_path, "w", encoding="utf-8") as f:
        json.dump(verdict, f, ensure_ascii=False, indent=2)

    return verdict_path


# ============================================================================
# ファイル出力（従来互換）
# ============================================================================

def generate_verdict_file(protocol: dict, result: dict, output_path: str) -> str:
    """判定プロンプトをファイルに保存する（従来互換）."""
    prompt = generate_judge_prompt(protocol, result)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    return output_path


# ============================================================================
# CLI
# ============================================================================

def main():
    """コマンドライン実行.

    使い方:
        # プロンプト生成のみ
        python -m experiments.judge <protocol.yaml> <result.json>

        # API呼び出しまで実行
        python -m experiments.judge <protocol.yaml> <result.json> --execute

        # プロンプトをファイルに保存（従来互換）
        python -m experiments.judge <protocol.yaml> <result.json> -o <output.txt>
    """
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    if len(args) < 2:
        print("使い方: python -m experiments.judge <protocol.yaml> <result.json> [options]")
        print()
        print("オプション:")
        print("  --execute    DeepSeek APIで独立判定を実行し、verdicts/に保存")
        print("  -o <path>    判定プロンプトをファイルに保存（従来互換）")
        sys.exit(1)

    protocol_path = args[0]
    result_path = args[1]

    if "--execute" in flags:
        # フェーズ3: API呼び出しまで自動化
        verdict_path = judge_with_api(protocol_path, result_path)
        print(f"\n  判定結果を保存: {verdict_path}")

        # 判定内容を表示
        with open(verdict_path, "r", encoding="utf-8") as f:
            verdict = json.load(f)
        print("\n" + "=" * 60)
        print("  独立判定結果")
        print("=" * 60)
        print(f"  判定モデル: {verdict['judge_model']}")
        print(f"  判定日時:   {verdict['judged_at']}")
        print()
        print(verdict["verdict"])
        print()
    elif "-o" in args:
        # 従来互換: プロンプトをファイル保存
        idx = args.index("-o")
        if idx + 1 < len(args):
            output_path = args[idx + 1]
        else:
            print("エラー: -o の後に出力パスを指定してください")
            sys.exit(1)
        protocol = load_protocol(protocol_path)
        result = load_result(result_path)
        generate_verdict_file(protocol, result, output_path)
        print(f"判定プロンプトを保存しました: {output_path}")
    else:
        # デフォルト: プロンプトを標準出力
        protocol = load_protocol(protocol_path)
        result = load_result(result_path)
        prompt = generate_judge_prompt(protocol, result)
        print(prompt)


if __name__ == "__main__":
    main()
