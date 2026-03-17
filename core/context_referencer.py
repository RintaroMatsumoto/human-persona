"""前文脈参照・一貫性維持モジュール.

人間は相手のメッセージを読んでいることを無意識に示す。
このモジュールは会話履歴を追跡し、適切な文脈参照を生成する。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ConversationTurn:
    """会話の1ターン（1往復分）.

    Attributes:
        role: 発言者ロール ("user" or "assistant")
        content: 発言内容
        topics: 抽出されたトピックのリスト
        turn_index: 会話内の順番
    """

    role: str
    content: str
    topics: list[str] = field(default_factory=list)
    turn_index: int = 0


@dataclass
class ContextReferencer:
    """会話履歴を管理し、前文脈参照を支援する.

    「先ほどの〇〇の件ですが」「おっしゃる通り〇〇ですね」のような
    文脈参照パターンを生成するための情報を提供する。

    Attributes:
        history: 会話履歴
        max_history: 保持する最大ターン数
        reference_patterns: 参照パターンテンプレート（派生クラスで言語別定義）
    """

    history: list[ConversationTurn] = field(default_factory=list)
    max_history: int = 20
    reference_patterns: list[str] = field(default_factory=list)

    def add_turn(self, role: str, content: str, topics: list[str] | None = None) -> None:
        """会話ターンを追加する.

        Args:
            role: 発言者ロール
            content: 発言内容
            topics: 抽出されたトピック（None の場合は空リスト）
        """
        turn = ConversationTurn(
            role=role,
            content=content,
            topics=topics or [],
            turn_index=len(self.history),
        )
        self.history.append(turn)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

    def get_recent_topics(self, n: int = 3) -> list[str]:
        """直近 n ターンのトピックを取得する.

        Args:
            n: 遡るターン数

        Returns:
            トピックのリスト（重複除去済み）
        """
        topics: list[str] = []
        seen: set[str] = set()
        for turn in reversed(self.history[-n:]):
            for topic in turn.topics:
                if topic not in seen:
                    topics.append(topic)
                    seen.add(topic)
        return topics

    def get_user_last_message(self) -> str | None:
        """ユーザーの直近メッセージを取得する.

        Returns:
            直近のユーザーメッセージ。存在しなければ None。
        """
        for turn in reversed(self.history):
            if turn.role == "user":
                return turn.content
        return None

    def find_topic_history(self, topic: str) -> list[ConversationTurn]:
        """特定トピックに関連するターンを検索する.

        Args:
            topic: 検索するトピック名

        Returns:
            該当トピックを含むターンのリスト
        """
        return [turn for turn in self.history if topic in turn.topics]

    def should_reference_previous(self) -> bool:
        """前文脈を参照すべきかを判定する.

        同一トピックが複数ターンに渡って議論されている場合、
        前文脈参照が自然な返信となる。

        Returns:
            参照すべきなら True
        """
        if len(self.history) < 2:
            return False
        recent = self.get_recent_topics(3)
        # 同一トピックが複数回登場していれば参照すべき
        return len(recent) != len(set(recent)) or len(self.history) >= 3

    def get_consistency_context(self) -> dict[str, Any]:
        """一貫性維持のための文脈情報を返す.

        Returns:
            直近トピック、メッセージ数、ユーザー最終発言を含む辞書
        """
        return {
            "recent_topics": self.get_recent_topics(),
            "total_turns": len(self.history),
            "user_last_message": self.get_user_last_message(),
        }
