"""感情状態の時系列変化モデル.

人間の感情は会話を通じて動的に変化する。
この状態機械は会話フェーズごとの感情遷移を再現し、
返信トーン・文体選択に影響を与える。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# トリガー関数の型: EmotionStateMachine を受け取り bool を返す
TriggerFunc = Callable[["EmotionStateMachine"], bool]


class EmotionState(Enum):
    """感情状態の種別."""

    FORMAL = "formal"            # 初回接触: 丁寧・距離感あり・慎重
    WARMING = "warming"          # 打ち解け: 少し親しみが出る
    TENSE = "tense"              # 問題発生: 緊張・慎重・確認が増える
    RELIEVED = "relieved"        # 解決後: 安堵・感謝
    TRUSTED = "trusted"          # 長期取引: 簡潔・効率的・信頼ベース


@dataclass
class Transition:
    """状態遷移の定義.

    Attributes:
        from_state: 遷移元の状態
        to_state: 遷移先の状態
        trigger: 遷移条件を評価する関数
        description: 遷移の説明
    """

    from_state: EmotionState
    to_state: EmotionState
    trigger: TriggerFunc
    description: str = ""


def _event_trigger(event_name: str) -> TriggerFunc:
    """特定イベント名に一致するトリガー関数を生成する."""
    return lambda sm: sm._last_event == event_name


def _exchange_threshold(n: int) -> TriggerFunc:
    """会話往復回数が閾値以上かを判定するトリガー関数を生成する."""
    return lambda sm: sm.exchange_count >= n


# デフォルトの遷移テーブル
DEFAULT_TRANSITIONS: list[Transition] = [
    Transition(EmotionState.FORMAL, EmotionState.WARMING,
               _exchange_threshold(3),
               "3往復後に打ち解ける"),
    Transition(EmotionState.WARMING, EmotionState.TENSE,
               _event_trigger("problem_detected"),
               "問題発生で緊張"),
    Transition(EmotionState.TENSE, EmotionState.RELIEVED,
               _event_trigger("problem_resolved"),
               "解決後に安堵"),
    Transition(EmotionState.RELIEVED, EmotionState.TRUSTED,
               _exchange_threshold(10),
               "長期取引で信頼関係構築"),
    Transition(EmotionState.WARMING, EmotionState.TRUSTED,
               _exchange_threshold(10),
               "順調な長期取引"),
    # 逆方向の遷移（信頼関係が崩れるケース）
    Transition(EmotionState.TRUSTED, EmotionState.TENSE,
               _event_trigger("problem_detected"),
               "信頼関係下でも問題発生時は緊張"),
    Transition(EmotionState.RELIEVED, EmotionState.TENSE,
               _event_trigger("problem_detected"),
               "再度問題発生"),
]


@dataclass
class EmotionStateMachine:
    """感情状態を管理する状態機械.

    Attributes:
        current_state: 現在の感情状態
        exchange_count: 会話往復回数
        transitions: 遷移テーブル
        state_history: 状態遷移の履歴
    """

    current_state: EmotionState = EmotionState.FORMAL
    exchange_count: int = 0
    transitions: list[Transition] = field(
        default_factory=lambda: list(DEFAULT_TRANSITIONS)
    )
    state_history: list[EmotionState] = field(default_factory=list)
    _last_event: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        if not self.state_history:
            self.state_history.append(self.current_state)

    def process_event(self, event: str) -> EmotionState:
        """イベントを処理し、必要に応じて状態遷移する.

        Args:
            event: 発生したイベント名
                   ("exchange", "problem_detected", "problem_resolved" など)

        Returns:
            遷移後の感情状態
        """
        self._last_event = event
        if event == "exchange":
            self.exchange_count += 1

        for transition in self.transitions:
            if transition.from_state != self.current_state:
                continue
            if transition.trigger(self):
                self._transition_to(transition.to_state)
                break

        self._last_event = ""
        return self.current_state

    def get_tone_modifier(self) -> dict[str, float]:
        """現在の感情状態に基づくトーン修飾パラメータを返す.

        Returns:
            formality (形式度), warmth (温かさ), caution (慎重さ) の辞書
        """
        modifiers: dict[EmotionState, dict[str, float]] = {
            EmotionState.FORMAL:   {"formality": 0.9, "warmth": 0.2, "caution": 0.7},
            EmotionState.WARMING:  {"formality": 0.6, "warmth": 0.6, "caution": 0.4},
            EmotionState.TENSE:    {"formality": 0.8, "warmth": 0.3, "caution": 0.9},
            EmotionState.RELIEVED: {"formality": 0.5, "warmth": 0.8, "caution": 0.3},
            EmotionState.TRUSTED:  {"formality": 0.3, "warmth": 0.7, "caution": 0.2},
        }
        return modifiers[self.current_state]

    def reset(self) -> None:
        """状態をリセットして初期状態に戻す."""
        self.current_state = EmotionState.FORMAL
        self.exchange_count = 0
        self.state_history = [EmotionState.FORMAL]
        self._last_event = ""

    def _transition_to(self, new_state: EmotionState) -> None:
        """状態を遷移させ、履歴に記録する."""
        self.current_state = new_state
        self.state_history.append(new_state)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> EmotionStateMachine:
        """設定辞書からインスタンスを生成する.

        Args:
            config: emotion_states 形式の設定辞書

        Returns:
            設定に基づく EmotionStateMachine インスタンス

        設定ファイルの trigger 文字列は以下の形式をサポート:
            - "event_name": 特定イベント名に一致
            - "exchange_count >= N": 往復回数の閾値判定
        """
        transitions: list[Transition] = []
        for t_cfg in config.get("transitions", []):
            trigger_str = t_cfg["trigger"]
            trigger_func = _parse_trigger_string(trigger_str)
            transitions.append(Transition(
                from_state=EmotionState(t_cfg["from"]),
                to_state=EmotionState(t_cfg["to"]),
                trigger=trigger_func,
                description=t_cfg.get("description", ""),
            ))
        initial = EmotionState(config.get("initial_state", "formal"))
        return cls(
            current_state=initial,
            transitions=transitions if transitions else list(DEFAULT_TRANSITIONS),
        )


def _parse_trigger_string(trigger_str: str) -> TriggerFunc:
    """設定ファイルのトリガー文字列を TriggerFunc に変換する.

    Args:
        trigger_str: "problem_detected" や "exchange_count >= 3" 形式の文字列

    Returns:
        対応する TriggerFunc
    """
    if ">=" in trigger_str:
        var_name, threshold_str = trigger_str.split(">=")
        var_name = var_name.strip()
        threshold = int(threshold_str.strip())
        if var_name == "exchange_count":
            return _exchange_threshold(threshold)
    return _event_trigger(trigger_str)
