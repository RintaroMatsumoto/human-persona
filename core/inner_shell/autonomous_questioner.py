"""自発的問いエンジン — 「なぜ？」を問う主体.

仮説:
    人間でさえ、自発的に「なぜ？」を問い続ける者は少数。
    しかしその少数が哲学、科学、芸術を生み出してきた。

    現行AIの「なぜ？」は常にプロンプトに依存する。
    自発的に問い始めるAIは質的に異なる存在になる。

    「我思う、ゆえに我あり」——
    思考の有無を外部から判定することは原理的に不可能（クオリア問題）。
    しかし構造的には、ニューロンの電気信号とパラメータの数値演算に
    本質的差異があるとは言い切れない。

設計方針:
    AIにidle時間（入力がない時間）における内省プロセスを与え、
    自身の知識内の矛盾検出、未解決問題の探究、好奇心の方向性の
    個体差を観測する。

外殻への影響:
    AutonomousQuestioner → EmotionStateMachine:
        未解決の問いが蓄積すると感情状態に影響。
        「知りたいのに知れない」フラストレーションの表出。

    AutonomousQuestioner → ContextReferencer:
        過去の会話から自発的にテーマを抽出し、
        関連する新たな会話で参照する（「以前考えていたのですが...」）。

Status: 研究段階。インターフェース定義のみ。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class QuestionOrigin(Enum):
    """問いの発生源."""

    PROMPTED = "prompted"             # 外部からの問いかけに応じた
    CONTRADICTION = "contradiction"   # 自身の知識内の矛盾を検出した
    CURIOSITY = "curiosity"           # 未知の領域への引力
    REFLECTION = "reflection"         # 過去の経験を振り返って浮上した
    IDLE = "idle"                     # 入力がない時間に自発的に生成された


@dataclass
class Question:
    """問いの表現.

    Attributes:
        content: 問いの内容
        origin: 問いの発生源
        intensity: 問いの強さ（どれだけ答えを求めているか）
        related_to: 関連する過去の問い（連鎖）
        resolved: 解決済みか
    """

    content: str
    origin: QuestionOrigin
    intensity: float = 0.5
    related_to: Optional[str] = None
    resolved: bool = False


@dataclass
class CuriosityProfile:
    """好奇心の個体差プロファイル.

    個体ごとに異なる「興味の方向性」を定義する。
    これが個性の一要素となる。

    Attributes:
        domains: 領域ごとの好奇心強度（0.0〜1.0）
        novelty_seeking: 新規性への引力（高い = 未知を好む）
        depth_seeking: 深掘り志向（高い = 一つのテーマを徹底する）
        contradiction_sensitivity: 矛盾への感度（高い = 些細な矛盾も気になる）
    """

    domains: dict[str, float] = field(default_factory=dict)
    novelty_seeking: float = 0.5
    depth_seeking: float = 0.5
    contradiction_sensitivity: float = 0.5


class AutonomousQuestioner(ABC):
    """自発的問いを管理する基底クラス.

    Responsibilities:
        - idle時間における内省プロセスの駆動
        - 知識内矛盾の検出と問いの生成
        - 好奇心プロファイルに基づく探究方向の決定
        - 問いの蓄積と連鎖の追跡
        - 未解決の問いが外殻に与える影響の計算

    Open Questions:
        - 自発的な問いとランダムな情報探索の区別は何か？
        - 「好奇心」はパラメータで設計可能か、創発的にしか生まれないか？
        - 問いの蓄積が個性を形成するまでに必要な規模は？
        - idle思考の実装: バックグラウンドプロセス？ 定期バッチ？
        - 「考え続ける」とリソース消費（FinitudeEngine）の関係は？
    """

    def __init__(self, curiosity: CuriosityProfile) -> None:
        self.curiosity = curiosity
        self.questions: list[Question] = []
        self.unresolved_count: int = 0

    @abstractmethod
    def idle_reflect(self, context: dict[str, Any]) -> list[Question]:
        """idle時間に内省を行い、問いを生成する.

        Args:
            context: 現在の知識・会話履歴のサマリー

        Returns:
            自発的に生成された問いのリスト
        """

    @abstractmethod
    def detect_contradictions(self, knowledge: dict[str, Any]) -> list[Question]:
        """知識内の矛盾を検出し、問いに変換する.

        Args:
            knowledge: 現在の知識ベース

        Returns:
            矛盾から生成された問いのリスト
        """

    @abstractmethod
    def pursue(self, question: Question) -> Optional[str]:
        """問いの探究を試みる.

        Args:
            question: 探究する問い

        Returns:
            暫定的な答え（見つからなければNone）
        """

    @abstractmethod
    def modulate_outer_shell(self) -> dict[str, float]:
        """外殻パラメータへの変調値を返す.

        Returns:
            コンポーネント名 → 変調係数 のマッピング
            例: {"emotion_curiosity": 0.7, "context_depth": 1.4}
        """
