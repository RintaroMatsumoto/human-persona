"""実験プロトコル制度 — フェーズ2: 実行＋自動診断.

事前宣言（protocol.yaml）を読み込み、実験を走らせ、
結果を成功基準と照合して診断レポート（JSON）を出力する。

診断レポートは実施者の解釈を含まない。
数値と基準の照合結果だけを記録する。
解釈は フェーズ3（judge.py）で独立に行われる。

使い方:
    from experiments.runner_v2 import ExperimentRunner

    runner = ExperimentRunner("experiments/protocols/candle_flame_001.yaml")

    # 実験を走らせ、測定値を記録する
    runner.record("bias_separation", 0.321)
    runner.record("salience_decay", 0.001)

    # 診断レポートを出力する
    report = runner.finalize("experiments/results/candle_flame_001_result.json")
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from experiments.protocol import ExperimentProtocol, Prediction


# ============================================================================
# フェーズ1→2 分離ガード
# ============================================================================

def _verify_protocol_committed(path: str) -> bool:
    """プロトコルファイルがgitにコミット済みか検証する.

    git log で対象パスのコミット履歴を確認する。
    1件でもコミットがあれば True。

    gitが使えない環境では False を返す（検証不能）。
    """
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H", "-1", "--", path],
            capture_output=True, text=True, timeout=5,
        )
        return bool(result.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


# ============================================================================
# 診断レポート
# ============================================================================

@dataclass
class DiagnosticReport:
    """自動診断レポート.

    実施者の解釈を含まない。数値と基準の照合結果だけ。

    Attributes:
        experiment_id: 実験ID（プロトコルと紐付け）
        protocol_path: 使用したプロトコルファイルのパス
        executed_at: 実行日時
        results: 各予測の照合結果
        all_passed: 全ての予測が成功したか
        summary: 機械的な一文要約
    """
    experiment_id: str
    protocol_path: str
    executed_at: str
    results: List[Dict[str, Any]]
    all_passed: bool
    summary: str
    git_verified: bool = True

    def to_json(self) -> str:
        """JSON文字列に変換."""
        return json.dumps(
            {
                "experiment_id": self.experiment_id,
                "protocol_path": self.protocol_path,
                "executed_at": self.executed_at,
                "git_verified": self.git_verified,
                "all_passed": self.all_passed,
                "summary": self.summary,
                "results": self.results,
            },
            ensure_ascii=False,
            indent=2,
        )

    def save(self, path: str) -> str:
        """JSONファイルに保存."""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        return path


# ============================================================================
# 実験ランナー
# ============================================================================

class ExperimentRunner:
    """実験の実行と自動診断を行うランナー.

    使い方:
        1. プロトコルファイルのパスを渡してインスタンス化
        2. 実験を走らせ、各予測に対応する測定値を record() で記録
        3. finalize() で診断レポートを生成・保存
    """

    def __init__(self, protocol_path: str) -> None:
        """プロトコルを読み込んで初期化する.

        フェーズ1→2の分離を強制する:
        - プロトコルファイルが存在すること
        - プロトコルファイルがgitにコミット済みであること

        環境変数 PROTOCOL_SKIP_GIT_CHECK=1 でgitチェックを無効化できる
        （テスト・CI用）。その場合、診断レポートに git_verified=False が記録される。

        Args:
            protocol_path: 事前宣言YAMLファイルのパス

        Raises:
            FileNotFoundError: プロトコルファイルが存在しない場合
            RuntimeError: プロトコルがgitにコミットされていない場合
        """
        if not os.path.exists(protocol_path):
            raise FileNotFoundError(
                f"プロトコルファイルが見つからない: {protocol_path}\n"
                f"フェーズ1（事前宣言）を先に完了してください。"
            )

        # gitコミット済みチェック
        if os.environ.get("PROTOCOL_SKIP_GIT_CHECK") == "1":
            self._git_verified = False
        else:
            if not _verify_protocol_committed(protocol_path):
                raise RuntimeError(
                    f"プロトコル '{protocol_path}' がgitにコミットされていない。\n"
                    f"フェーズ1: 事前宣言をgit commitしてからフェーズ2に進んでください。\n"
                    f"（テスト時は PROTOCOL_SKIP_GIT_CHECK=1 で無効化可能）"
                )
            self._git_verified = True

        self._protocol = ExperimentProtocol.load(protocol_path)
        self._protocol_path = protocol_path
        self._measurements: Dict[str, float] = {}
        self._executed_at = datetime.now(timezone.utc).isoformat()

    @property
    def protocol(self) -> ExperimentProtocol:
        """読み込んだプロトコル."""
        return self._protocol

    def record(self, prediction_name: str, actual_value: float) -> None:
        """測定値を記録する.

        Args:
            prediction_name: 予測のname（プロトコルで定義したもの）
            actual_value: 実測値

        Raises:
            ValueError: プロトコルに存在しない予測名の場合
        """
        known_names = {p.name for p in self._protocol.predictions}
        if prediction_name not in known_names:
            raise ValueError(
                f"予測名 '{prediction_name}' はプロトコルに存在しない。"
                f"定義済みの予測: {known_names}"
            )
        self._measurements[prediction_name] = actual_value

    def finalize(self, output_path: Optional[str] = None) -> DiagnosticReport:
        """診断レポートを生成する.

        全ての予測について:
        - 測定値が記録されていれば、基準と照合する
        - 測定値が記録されていなければ、「未測定」として失敗扱い

        Args:
            output_path: JSONファイルの保存先（Noneなら保存しない）

        Returns:
            DiagnosticReport
        """
        results = []

        for prediction in self._protocol.predictions:
            if prediction.name in self._measurements:
                actual = self._measurements[prediction.name]
                result = prediction.evaluate(actual)
            else:
                result = {
                    "name": prediction.name,
                    "passed": False,
                    "actual": None,
                    "expected_min": prediction.expected_min,
                    "expected_max": prediction.expected_max,
                    "reason": "未測定: 実測値が記録されていない",
                }
            results.append(result)

        all_passed = all(r["passed"] for r in results)
        passed_count = sum(1 for r in results if r["passed"])
        total_count = len(results)

        # 機械的な要約（解釈なし）
        summary = f"{passed_count}/{total_count} の予測が基準を満たした。"
        if not all_passed:
            failed = [r["name"] for r in results if not r["passed"]]
            summary += f" 未達: {', '.join(failed)}。"

        report = DiagnosticReport(
            experiment_id=self._protocol.experiment_id,
            protocol_path=self._protocol_path,
            executed_at=self._executed_at,
            results=results,
            all_passed=all_passed,
            summary=summary,
            git_verified=self._git_verified,
        )

        if output_path:
            report.save(output_path)

        return report


def print_report(report: DiagnosticReport) -> None:
    """診断レポートを人間が読める形で表示する."""
    print("=" * 60)
    print("  自動診断レポート")
    print("=" * 60)
    print(f"  実験ID:     {report.experiment_id}")
    print(f"  プロトコル: {report.protocol_path}")
    print(f"  実行日時:   {report.executed_at}")
    print(f"  総合判定:   {'全基準クリア ✓' if report.all_passed else '一部未達 ✗'}")
    print(f"  要約:       {report.summary}")
    print()

    for r in report.results:
        status = "✓ PASS" if r["passed"] else "✗ FAIL"
        actual = f"{r['actual']:.4f}" if r["actual"] is not None else "未測定"
        bounds = []
        if r["expected_min"] is not None:
            bounds.append(f"≥ {r['expected_min']}")
        if r["expected_max"] is not None:
            bounds.append(f"≤ {r['expected_max']}")
        bound_str = ", ".join(bounds) if bounds else "制約なし"

        print(f"  [{status}] {r['name']}")
        print(f"           実測値: {actual}  (基準: {bound_str})")
        print(f"           理由:   {r['reason']}")
        print()
