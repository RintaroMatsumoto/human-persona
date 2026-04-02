"""実験プロトコル制度 — フェーズ1: 事前宣言.

実験を走らせる前に、目的・予測・成功基準をYAMLファイルに書き出す。
gitにコミットしてタイムスタンプを固定することで、後から動かせなくする。

使い方:
    # 1. プロトコルを生成する
    protocol = ExperimentProtocol(
        experiment_id="candle_flame_001",
        title="蝋燭の炎プロトタイプ — bias分離の検証",
        purpose="compute_flame()の三本柱（bias, remaining, salience）が全て機能するか検証する",
        predictions=[
            Prediction(
                name="bias_separation",
                description="学者型と冒険者型でbiasに有意な差が出る",
                metric="bias差の平均絶対値",
                expected_min=0.15,
                expected_max=None,
            ),
            Prediction(
                name="salience_decay",
                description="最古と最新の体験でsalienceに差が出る（減衰が機能している）",
                metric="salience最大値 - salience最小値",
                expected_min=0.3,
                expected_max=None,
            ),
        ],
    )

    # 2. YAMLファイルに保存する
    protocol.save("experiments/protocols/candle_flame_001.yaml")

    # 3. git commit する（手動 or スクリプト）
    #    → タイムスタンプが固定される

    # 4. 実験を走らせる（runner_v2.py）
    #    → プロトコルファイルのパスを渡す
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# PyYAMLがなければ簡易的にダンプする
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ============================================================================
# データ構造
# ============================================================================

@dataclass
class Prediction:
    """一つの予測（成功基準）.

    Attributes:
        name: 予測の識別子（英数字、judge.pyでの照合に使う）
        description: 何を予測しているかの自然言語説明
        metric: 測定する指標の名前
        expected_min: この値以上なら成功（Noneなら下限なし）
        expected_max: この値以下なら成功（Noneなら上限なし）
    """
    name: str
    description: str
    metric: str
    expected_min: Optional[float] = None
    expected_max: Optional[float] = None

    def evaluate(self, actual: float) -> dict:
        """実測値と照合して合否を判定する.

        Returns:
            {"name": ..., "passed": bool, "actual": float,
             "expected_min": ..., "expected_max": ..., "reason": str}
        """
        passed = True
        reasons = []

        if self.expected_min is not None and actual < self.expected_min:
            passed = False
            reasons.append(f"実測値 {actual:.4f} < 下限 {self.expected_min}")

        if self.expected_max is not None and actual > self.expected_max:
            passed = False
            reasons.append(f"実測値 {actual:.4f} > 上限 {self.expected_max}")

        if passed:
            reasons.append("基準を満たした")

        return {
            "name": self.name,
            "passed": passed,
            "actual": actual,
            "expected_min": self.expected_min,
            "expected_max": self.expected_max,
            "reason": "; ".join(reasons),
        }


@dataclass
class ExperimentProtocol:
    """実験プロトコル（事前宣言）.

    Attributes:
        experiment_id: 実験の一意識別子
        title: 実験タイトル
        purpose: この実験は何を検証するか
        predictions: 予測のリスト（成功基準）
        created_at: 作成日時（自動設定）
        author: 作成者
        notes: 補足メモ
    """
    experiment_id: str
    title: str
    purpose: str
    predictions: List[Prediction]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    author: str = "Kuromi & Rintaro"
    notes: str = ""

    def save(self, path: str) -> str:
        """YAMLファイルに保存する.

        Args:
            path: 保存先のファイルパス

        Returns:
            保存したファイルのパス
        """
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)

        data = {
            "experiment_id": self.experiment_id,
            "title": self.title,
            "purpose": self.purpose,
            "author": self.author,
            "created_at": self.created_at,
            "notes": self.notes,
            "predictions": [
                {
                    "name": p.name,
                    "description": p.description,
                    "metric": p.metric,
                    "expected_min": p.expected_min,
                    "expected_max": p.expected_max,
                }
                for p in self.predictions
            ],
        }

        if HAS_YAML:
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        else:
            # PyYAMLがない場合の簡易ダンプ
            with open(path, "w", encoding="utf-8") as f:
                f.write(_simple_yaml_dump(data))

        return path

    @classmethod
    def load(cls, path: str) -> "ExperimentProtocol":
        """YAMLファイルから読み込む."""
        if HAS_YAML:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        else:
            raise RuntimeError("PyYAML is required to load protocols. pip install pyyaml")

        predictions = [
            Prediction(**p) for p in data.get("predictions", [])
        ]

        return cls(
            experiment_id=data["experiment_id"],
            title=data["title"],
            purpose=data["purpose"],
            predictions=predictions,
            created_at=data.get("created_at", ""),
            author=data.get("author", ""),
            notes=data.get("notes", ""),
        )


def _simple_yaml_dump(data: Dict[str, Any], indent: int = 0) -> str:
    """PyYAMLなしの簡易YAMLダンプ."""
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    first = True
                    for k, v in item.items():
                        marker = "- " if first else "  "
                        first = False
                        lines.append(f"{prefix}  {marker}{k}: {_format_value(v)}")
                else:
                    lines.append(f"{prefix}  - {_format_value(item)}")
        elif isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_simple_yaml_dump(value, indent + 1))
        else:
            lines.append(f"{prefix}{key}: {_format_value(value)}")

    return "\n".join(lines)


def _format_value(v: Any) -> str:
    """YAML値のフォーマット."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        if any(c in v for c in ":#{}[]|>&*!%@`"):
            return f'"{v}"'
        return v
    return str(v)
