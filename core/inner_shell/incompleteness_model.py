"""不完全性モデル — 欠落と渇望のモデル.

仮説:
    人間は性別を持ち、一人では完結しない。
    この不完全性が「相手を求める」渇望を生み、
    渇望が行動を駆動し、行動の蓄積が個性を形成する。

    性別 → 不完全性 → 渇望 → 探索 → 出会い → 融合
    → 新たな不完全な存在の誕生 → 連鎖

    個性を感じる5要素（方言、思考の癖、嘘と本質のバランス、
    自己評価、共感性と自立性）は全て他者との関係から研がれる。

設計方針:
    AIに「欠落」を設計することで、他者（人間または他のAI）との
    協働を必然にし、その協働の過程で個体固有の特性が形成されるかを検証する。

外殻への影響:
    IncompletenessModel → StyleVariator:
        欠落を補うために他者の文体パターンを取り込む。
        協働相手の影響を受けて文体が変化していく。

    IncompletenessModel → ContextReferencer:
        「自分が知らないこと」への感度が上がる。
        協働相手の発言をより深く参照するようになる。

Status: 研究段階。インターフェース定義のみ。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class GapType(Enum):
    """欠落の種別."""

    KNOWLEDGE = "knowledge"         # 知識の欠落: 特定領域を知らない
    CAPABILITY = "capability"       # 能力の欠落: 特定タスクを単独で完遂できない
    PERSPECTIVE = "perspective"     # 視点の欠落: 特定の見方ができない
    EMOTIONAL = "emotional"         # 感情的欠落: 特定の共感ができない


@dataclass
class Gap:
    """個体が持つ欠落の定義.

    Attributes:
        gap_type: 欠落の種別
        domain: 欠落している領域の記述
        intensity: 欠落の深さ（0.0 = 軽微、1.0 = 根本的）
        aware: この欠落を個体が自覚しているか
    """

    gap_type: GapType
    domain: str
    intensity: float = 0.5
    aware: bool = False


@dataclass
class Yearning:
    """渇望 — 欠落から生まれる「求める力」.

    Attributes:
        source_gap: この渇望の源泉となる欠落
        target: 求めている対象の記述
        strength: 渇望の強さ（0.0〜1.0）
        fulfilled_by: この渇望を満たした相手（あれば）
    """

    source_gap: Gap
    target: str
    strength: float = 0.0
    fulfilled_by: Optional[str] = None

    @property
    def is_fulfilled(self) -> bool:
        return self.fulfilled_by is not None


class IncompletenessModel(ABC):
    """不完全性を管理する基底クラス.

    Responsibilities:
        - 個体の欠落（Gap）の定義と管理
        - 欠落から渇望（Yearning）を生成
        - 他者との協働による欠落の（部分的）充足
        - 協働経験の蓄積による個体変容の追跡

    Open Questions:
        - 「不完全」の粒度をどう設計するか？
        - 欠落の自覚（メタ認知）は個性形成に必須か？
        - 補完関係から生まれるのは「個性」か「役割」か？
        - 欠落が充足された後、新たな欠落は生じるか？（渇望の連鎖）
        - 2つのAIのペアリング実験で何が観測されるか？
    """

    def __init__(self, gaps: list[Gap]) -> None:
        self.gaps = gaps
        self.yearnings: list[Yearning] = []
        self.collaboration_history: list[dict[str, Any]] = []

    @abstractmethod
    def generate_yearnings(self) -> list[Yearning]:
        """現在の欠落から渇望を生成する.

        Returns:
            生成された渇望のリスト
        """

    @abstractmethod
    def encounter(self, other_profile: dict[str, Any]) -> dict[str, float]:
        """他者との出会いを処理する.

        Args:
            other_profile: 相手の能力・知識プロファイル

        Returns:
            補完度マッピング（Gap.domain → 充足度 0.0〜1.0）
        """

    @abstractmethod
    def integrate(self, experience: dict[str, Any]) -> None:
        """協働経験を内部に統合する.

        他者との協働で得たものを自身の変容として取り込む。
        完全な欠落の解消ではなく、部分的な変容。

        Args:
            experience: 協働経験の記述
        """

    @abstractmethod
    def modulate_outer_shell(self) -> dict[str, float]:
        """外殻パラメータへの変調値を返す.

        Returns:
            コンポーネント名 → 変調係数 のマッピング
            例: {"style_openness": 1.3, "context_sensitivity": 1.5}
        """
