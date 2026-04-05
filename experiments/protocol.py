"""実験プロトコル制度 — フェーズ1: 事前宣言.

AsPredicted (https://aspredicted.org/) フォーマットに準拠した
計算実験向けの事前登録制度。

実験を走らせる前に、目的・条件・予測・成功基準をYAMLファイルに書き出す。
gitにコミットしてタイムスタンプを固定することで、後から動かせなくする。

AsPredicted 9項目との対応:
    Q1+Q9 (Data collection / Prior data) → prior_execution
    Q2    (Hypothesis)                   → purpose + predictions
    Q3    (Dependent variable)           → predictions[].metric
    Q4    (Conditions)                   → conditions
    Q5    (Analyses)                     → predictions[].expected_min/max
    Q6    (Outliers)                     → exclusion_criteria
    Q7    (Sample size)                  → sample_size_rationale
    Q8    (Other)                        → known_limitations

使い方:
    # 1. プロトコルを生成する
    protocol = ExperimentProtocol(
        experiment_id="candle_flame_003",
        title="蝋燭の炎 — 時間モデル導入によるsalience減衰の検証",
        purpose="compute_salience()の指数減衰が、時間間隔を持つ体験列で機能するか検証する",
        conditions={
            "scholar": {
                "knowledge": {"valence": 0.6, "intensity": 0.9},
                "adventure": {"valence": -0.1, "intensity": 0.3},
            },
            "adventurer": {
                "knowledge": {"valence": 0.2, "intensity": 0.4},
                "adventure": {"valence": 0.8, "intensity": 0.9},
            },
            "total_resource": 120.0,
            "salience_decay": 0.05,
            "time_interval_seconds": 0.1,
        },
        predictions=[
            Prediction(
                name="salience_temporal_decay",
                description="同じintensityの体験でも、古いものほどsalienceが低い",
                metric="最古体験のsalience / 最新体験のsalience（intensity正規化後）",
                expected_min=None,
                expected_max=0.8,
            ),
        ],
        prior_execution="candle_flame_002で同様の実験を実施済み。"
            "ただしtimestamp差がほぼゼロのため減衰が機能せず、"
            "salience_rangeが偽PASSした。本実験はその修正版。",
        exclusion_criteria="炎が途中で消えた（is_extinguished=True）場合、"
            "その炎のデータは除外する。NaN/Infが出た場合も除外。",
        sample_size_rationale="100体験 × 2ペルソナ。002と同条件で比較するため。",
        known_limitations="time.sleep()による間隔シミュレーションは実時間に依存する。"
            "OS負荷による揺らぎがsalienceに影響する可能性がある。",
    )

    # 2. YAMLファイルに保存する
    protocol.save("experiments/protocols/candle_flame_003.yaml")

    # 3. りんたろうくんがレビューして git commit する
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

    AsPredicted Q3 (Dependent variable) + Q5 (Analyses) に対応。

    Attributes:
        name: 予測の識別子（英数字、judge.pyでの照合に使う）
        description: 何を予測しているかの自然言語説明
        metric: 測定する指標の名前と計算方法
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

    AsPredicted フォーマットに準拠した計算実験向け事前登録。
    各フィールドの対応は以下の通り:

        experiment_id          — 実験の一意識別子
        title                  — 実験タイトル
        purpose                — Q2: この実験は何を検証するか（仮説）
        conditions             — Q4: 実験条件（パラメータ設定）
        predictions            — Q3+Q5: 測定指標と成功基準
        prior_execution        — Q1+Q9: 事前実行の有無と結果
        exclusion_criteria     — Q6: データ除外ルール
        sample_size_rationale  — Q7: 試行回数の根拠
        known_limitations      — Q8: 既知の限界・探索的分析
        created_at             — 作成日時（自動設定）
        author                 — 作成者
    """
    # --- 必須フィールド ---
    experiment_id: str
    title: str
    purpose: str
    predictions: List[Prediction]

    # --- AsPredicted準拠フィールド ---
    conditions: Dict[str, Any] = field(default_factory=dict)
    prior_execution: str = "なし"
    exclusion_criteria: str = "特になし"
    sample_size_rationale: str = ""
    known_limitations: str = ""

    # --- メタデータ ---
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    author: str = "Kuromi & Rintaro"

    def save(self, path: str) -> str:
        """YAMLファイルに保存する.

        AsPredictedの項目番号をコメントとして付記する。

        Args:
            path: 保存先のファイルパス

        Returns:
            保存したファイルのパス
        """
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)

        data = {
            "experiment_id": self.experiment_id,
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at,
            # Q1+Q9: 事前実行の有無
            "prior_execution": self.prior_execution,
            # Q2: 仮説・目的
            "purpose": self.purpose,
            # Q4: 実験条件
            "conditions": self.conditions,
            # Q3+Q5: 測定指標と成功基準
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
            # Q6: データ除外ルール
            "exclusion_criteria": self.exclusion_criteria,
            # Q7: 試行回数の根拠
            "sample_size_rationale": self.sample_size_rationale,
            # Q8: 既知の限界
            "known_limitations": self.known_limitations,
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

        known = Prediction.__dataclass_fields__
        predictions = [
            Prediction(**{k: v for k, v in p.items() if k in known})
            for p in data.get("predictions", [])
        ]

        return cls(
            experiment_id=data["experiment_id"],
            title=data["title"],
            purpose=data["purpose"],
            predictions=predictions,
            conditions=data.get("conditions", {}),
            prior_execution=data.get("prior_execution", "なし"),
            exclusion_criteria=data.get("exclusion_criteria", "特になし"),
            sample_size_rationale=data.get("sample_size_rationale", ""),
            known_limitations=data.get("known_limitations", ""),
            created_at=data.get("created_at", ""),
            author=data.get("author", ""),
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
