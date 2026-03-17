"""HumanPersonaBase: 人間らしいAI振る舞いの基底クラス.

言語・文化・属性に依存しない普遍的構造を提供する。
具体的な言語・ペルソナは派生クラスで定義する。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.context_referencer import ContextReferencer
from core.emotion_state_machine import EmotionState, EmotionStateMachine
from core.escalation_detector import (
    EscalationDetector,
    EscalationReason,
    EscalationResult,
)
from core.style_variator import StyleType, StyleVariator
from core.timing_controller import Platform, TimingController


@dataclass
class PersonaResponse:
    """ペルソナの応答結果.

    Attributes:
        content: 応答テキスト
        delay_seconds: 返信までの遅延秒数
        emotion_state: 現在の感情状態
        style_used: 使用した文体パターン
        escalation: エスカレーション判定結果（該当なしなら None）
        metadata: 追加メタデータ
    """

    content: str
    delay_seconds: float
    emotion_state: EmotionState
    style_used: StyleType
    escalation: EscalationResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HumanPersonaBase:
    """人間らしいAI振る舞いの基底クラス.

    すべてのコンポーネントを統合し、人間らしい応答を生成する。
    派生クラスは言語・文化固有のパラメータを注入する。

    Attributes:
        name: ペルソナ名（識別用）
        timing: 返信速度コントローラー
        style: 文体揺らぎジェネレーター
        emotion: 感情状態機械
        context: 前文脈参照マネージャー
        escalation: エスカレーションディテクター
        platform: 現在のプラットフォーム
    """

    name: str = "BasePersona"
    timing: TimingController = field(default_factory=TimingController)
    style: StyleVariator = field(default_factory=StyleVariator)
    emotion: EmotionStateMachine = field(default_factory=EmotionStateMachine)
    context: ContextReferencer = field(default_factory=ContextReferencer)
    escalation: EscalationDetector = field(default_factory=EscalationDetector)
    platform: Platform = Platform.CHAT

    def process_message(self, user_message: str, topics: list[str] | None = None) -> PersonaResponse:
        """ユーザーメッセージを処理し、人間らしい応答パラメータを生成する.

        このメソッドは応答テキスト自体は生成しない（それはLLMの仕事）。
        返信タイミング・文体・感情状態・エスカレーション判定を提供する。

        Args:
            user_message: ユーザーからのメッセージ
            topics: メッセージから抽出されたトピック

        Returns:
            PersonaResponse（応答パラメータ一式）
        """
        # 1. 文脈に追加
        self.context.add_turn("user", user_message, topics)

        # 2. エスカレーション判定
        escalation_result = self.escalation.evaluate(user_message)
        if escalation_result.should_escalate:
            # クレーム・交渉検知時は感情状態も連鎖遷移させる
            _PROBLEM_REASONS = {EscalationReason.COMPLAINT, EscalationReason.NEGOTIATION}
            if escalation_result.reason in _PROBLEM_REASONS:
                self.emotion.process_event("problem_detected")
            return PersonaResponse(
                content="",  # エスカレーション時は内容を人間に委ねる
                delay_seconds=0,
                emotion_state=self.emotion.current_state,
                style_used=StyleType.CONFIRMATION,
                escalation=escalation_result,
            )

        # 3. 感情状態を更新
        self.emotion.process_event("exchange")

        # 4. 返信遅延を計算
        delay = self.timing.calculate_delay(self.platform)

        # 5. 文体パターンを選択
        tone = self.emotion.get_tone_modifier()
        style = self.style.select_style(context={"tone": tone})

        # 6. 応答コンテキストを構築
        consistency = self.context.get_consistency_context()

        return PersonaResponse(
            content="",  # 実際のテキスト生成はLLM側で行う
            delay_seconds=delay,
            emotion_state=self.emotion.current_state,
            style_used=style,
            metadata={
                "tone_modifier": tone,
                "consistency_context": consistency,
                "should_reference_previous": self.context.should_reference_previous(),
                "insert_uncertainty": self.style.should_insert_uncertainty(),
            },
        )

    def get_system_prompt_context(self) -> dict[str, Any]:
        """LLMのシステムプロンプトに注入する文脈情報を返す.

        Returns:
            感情状態・文体指示・文脈参照情報を含む辞書
        """
        tone = self.emotion.get_tone_modifier()
        return {
            "persona_name": self.name,
            "emotion_state": self.emotion.current_state.value,
            "tone": tone,
            "recent_topics": self.context.get_recent_topics(),
            "exchange_count": self.emotion.exchange_count,
            "should_reference_previous": self.context.should_reference_previous(),
        }

    def reset(self) -> None:
        """全コンポーネントを初期状態にリセットする."""
        self.emotion.reset()
        self.context.history.clear()
        self.escalation.reset_chat_counter()
        self.style.history.clear()

    @classmethod
    def from_config_file(cls, config_path: str | Path) -> HumanPersonaBase:
        """設定ファイルからインスタンスを生成する.

        Args:
            config_path: JSON設定ファイルのパス

        Returns:
            設定に基づく HumanPersonaBase インスタンス
        """
        path = Path(config_path)
        with path.open("r", encoding="utf-8") as f:
            config = json.load(f)

        return cls(
            name=config.get("name", "BasePersona"),
            timing=TimingController.from_config(config.get("timing", {})),
            style=StyleVariator.from_config(config.get("style", {})),
            emotion=EmotionStateMachine.from_config(config.get("emotion", {})),
            escalation=EscalationDetector.from_config(config.get("escalation", {})),
            platform=Platform(config.get("platform", "chat")),
        )
