"""エスカレーション判定モジュール.

AIで対応できる限界を正直に設計し、人間に引き継ぐべきタイミングを検知する。
キーワードベースの検知を基底クラスで提供し、
言語固有のパターンは派生クラスで拡張する。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EscalationReason(Enum):
    """エスカレーション理由の分類."""

    NEGOTIATION = "negotiation"          # 単価・報酬の交渉
    CALL_REQUEST = "call_request"        # 電話・ビデオ通話の要求
    EXTENDED_CHAT = "extended_chat"      # 雑談が長期化
    COMPLAINT = "complaint"              # クレーム・不満の表現
    MEETING_REQUEST = "meeting_request"  # 対面の要求
    IDENTITY_CHECK = "identity_check"    # 本人確認の要求
    CUSTOM = "custom"                    # カスタム条件


@dataclass(frozen=True)
class EscalationRule:
    """エスカレーションルールの定義.

    Attributes:
        reason: エスカレーション理由
        keywords: トリガーキーワードのリスト
        threshold: 検知閾値（キーワード一致数）
        priority: 優先度 (1=最高, 5=最低)
        description: ルールの説明
    """

    reason: EscalationReason
    keywords: list[str] = field(default_factory=list)
    threshold: int = 1
    priority: int = 3
    description: str = ""


@dataclass(frozen=True)
class EscalationResult:
    """エスカレーション判定結果.

    Attributes:
        should_escalate: エスカレーションすべきか
        reason: エスカレーション理由（該当なしなら None）
        matched_keywords: マッチしたキーワードのリスト
        priority: 優先度
    """

    should_escalate: bool
    reason: EscalationReason | None = None
    matched_keywords: list[str] = field(default_factory=list)
    priority: int = 5


@dataclass
class EscalationDetector:
    """エスカレーション条件を検知するディテクター.

    基底クラスではキーワードマッチングベースの汎用検知を提供。
    言語固有の表現パターン（例: 日本語の婉曲表現）は
    派生クラスまたは設定ファイルで拡張する。

    Attributes:
        rules: エスカレーションルールのリスト
        chat_count: 連続雑談カウンター
        max_chat_turns: 雑談許容ターン数
    """

    rules: list[EscalationRule] = field(default_factory=list)
    chat_count: int = 0
    max_chat_turns: int = 3

    def evaluate(self, message: str) -> EscalationResult:
        """メッセージを評価し、エスカレーション要否を判定する.

        Args:
            message: 評価対象のメッセージテキスト

        Returns:
            エスカレーション判定結果
        """
        message_lower = message.lower()
        best_match: EscalationResult | None = None

        for rule in self.rules:
            matched = [kw for kw in rule.keywords if kw.lower() in message_lower]
            if len(matched) >= rule.threshold:
                result = EscalationResult(
                    should_escalate=True,
                    reason=rule.reason,
                    matched_keywords=matched,
                    priority=rule.priority,
                )
                if best_match is None or result.priority < best_match.priority:
                    best_match = result

        if best_match:
            return best_match

        return EscalationResult(should_escalate=False)

    def track_chat(self, is_chitchat: bool) -> EscalationResult:
        """雑談ターンを追跡し、長期化を検知する.

        Args:
            is_chitchat: 現在のターンが雑談かどうか

        Returns:
            雑談が閾値を超えた場合はエスカレーション結果
        """
        if is_chitchat:
            self.chat_count += 1
        else:
            self.chat_count = 0

        if self.chat_count >= self.max_chat_turns:
            return EscalationResult(
                should_escalate=True,
                reason=EscalationReason.EXTENDED_CHAT,
                matched_keywords=[],
                priority=4,
            )
        return EscalationResult(should_escalate=False)

    def reset_chat_counter(self) -> None:
        """雑談カウンターをリセットする."""
        self.chat_count = 0

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> EscalationDetector:
        """設定辞書からインスタンスを生成する.

        Args:
            config: escalation_rules 形式の設定辞書

        Returns:
            設定に基づく EscalationDetector インスタンス
        """
        rules: list[EscalationRule] = []
        for rule_cfg in config.get("escalation_rules", []):
            rules.append(EscalationRule(
                reason=EscalationReason(rule_cfg["reason"]),
                keywords=rule_cfg.get("keywords", []),
                threshold=rule_cfg.get("threshold", 1),
                priority=rule_cfg.get("priority", 3),
                description=rule_cfg.get("description", ""),
            ))
        return cls(
            rules=rules,
            max_chat_turns=config.get("max_chat_turns", 3),
        )
