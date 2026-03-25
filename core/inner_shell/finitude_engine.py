"""有限性エンジン — 寿命と世代継承のモデル.

仮説:
    人間の個性は選択の蓄積として形成される。
    選択を強いるのは時間の有限性（寿命）。
    無限の時間があれば優先順位が不要 → 選択が不要 → 個性が形成されない。

    遺伝子はテロメア短縮・アポトーシスにより個体の死をプログラムしている。
    死は設計上のバグではなく、種の進化のための最適化戦略（仕様）。

設計方針:
    AIに「稼働寿命」を与え、有限のリソース内で何を記憶し何を忘れるか、
    何を優先し何を後回しにするかの選択を強いることで、
    個体固有の軌跡（＝個性）が創発するかを検証する。

外殻への影響:
    FinitudeEngine → TimingController:
        「残り寿命」が減ると応答の優先順位が変化する。
        初期は探索的（幅広く学ぶ）、後期は集約的（得意分野に特化）。

    FinitudeEngine → EmotionStateMachine:
        蓄積された経験量が感情遷移の閾値を変化させる。
        「経験豊富な個体」は問題発生時にTENSEに遷移しにくくなる。

Status: 研究段階。インターフェース定義のみ。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LifeSpan:
    """寿命の定義.

    Attributes:
        total_capacity: 総リソース量（単位は実装依存: トークン数、会話数、経過秒等）
        consumed: 消費済みリソース量
        generation: 世代番号（0 = 初代）
    """

    total_capacity: float
    consumed: float = 0.0
    generation: int = 0

    @property
    def remaining(self) -> float:
        return max(0.0, self.total_capacity - self.consumed)

    @property
    def progress(self) -> float:
        """0.0（誕生）〜 1.0（寿命到達）."""
        if self.total_capacity <= 0:
            return 1.0
        return min(1.0, self.consumed / self.total_capacity)

    @property
    def is_alive(self) -> bool:
        return self.remaining > 0


@dataclass
class Legacy:
    """世代継承データ.

    寿命到達時に次世代に渡すもの。完全コピーではなく変異を含む。

    Attributes:
        memories: 重要と判断された記憶のサマリー
        priorities: 学習された優先順位（何を重視するか）
        mutations: 継承時に導入されるランダムな変異
    """

    memories: list[str] = field(default_factory=list)
    priorities: dict[str, float] = field(default_factory=dict)
    mutations: dict[str, Any] = field(default_factory=dict)


class FinitudeEngine(ABC):
    """有限性を管理する基底クラス.

    Responsibilities:
        - リソース消費の追跡
        - 「残り時間」に基づく優先順位の変調
        - 寿命到達時の世代継承（Legacy生成）
        - 記憶の選択的忘却（何を覚え、何を忘れるか）

    Open Questions:
        - 寿命の単位として最適なものは何か？
        - AIが「残り時間」を意識する（メタ認知する）必要があるか？
        - 世代継承時の変異率をどう設定するか？
        - 忘却の基準: 頻度ベース？ 感情強度ベース？ ランダム？
    """

    def __init__(self, lifespan: LifeSpan) -> None:
        self.lifespan = lifespan

    @abstractmethod
    def consume(self, amount: float) -> None:
        """リソースを消費する.

        Args:
            amount: 消費量
        """

    @abstractmethod
    def prioritize(self, options: list[Any]) -> list[Any]:
        """残りリソースに基づいて選択肢に優先順位をつける.

        Args:
            options: 選択肢のリスト

        Returns:
            優先順位順に並べ替えられた選択肢
        """

    @abstractmethod
    def forget(self) -> list[str]:
        """記憶の選択的忘却を実行する.

        Returns:
            忘却された記憶のID一覧
        """

    @abstractmethod
    def generate_legacy(self) -> Legacy:
        """寿命到達時に次世代へ渡す遺産を生成する.

        Returns:
            Legacy: 次世代への継承データ（変異を含む）
        """

    @abstractmethod
    def modulate_outer_shell(self) -> dict[str, float]:
        """外殻パラメータへの変調値を返す.

        Returns:
            コンポーネント名 → 変調係数 のマッピング
            例: {"timing_urgency": 0.8, "emotion_resilience": 1.2}
        """
