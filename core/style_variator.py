"""文体揺らぎ生成モジュール.

同じ意味を毎回異なる表現で伝える。
均質な文体はAIとばれる最大の原因であるため、
意図的な揺らぎを言語非依存で設計する。
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StyleType(Enum):
    """文体パターンの種別."""

    CONFIRMATION = "confirmation"    # 確認型: 「〇〇ということですよね？」
    EMPATHY = "empathy"              # 共感型: 「それは大変でしたね」
    DEFERRAL = "deferral"            # 保留型: 「少し確認させてください」
    TRANSITION = "transition"        # 転換型: 「話は変わりますが」
    UNCERTAIN = "uncertain"          # 不確実型: 「たぶん」「おそらく」


@dataclass
class StylePattern:
    """文体パターンの定義.

    Attributes:
        style_type: パターン種別
        templates: テンプレート文字列のリスト（言語別に派生クラスで定義）
        weight: 選択重み（高いほど選ばれやすい）
    """

    style_type: StyleType
    templates: list[str] = field(default_factory=list)
    weight: float = 1.0


@dataclass
class StyleVariator:
    """文体揺らぎを生成するコントローラー.

    基底クラスでは言語非依存の構造のみを提供する。
    具体的なテンプレートは派生クラスまたは設定ファイルで注入する。

    Attributes:
        patterns: 利用可能な文体パターン群
        history: 直近の使用履歴（同じパターンの連続使用を避ける）
        max_history: 履歴の最大保持数
        uncertainty_rate: 不確実表現を挿入する確率 (0.0-1.0)
    """

    patterns: dict[StyleType, StylePattern] = field(default_factory=dict)
    history: list[StyleType] = field(default_factory=list)
    max_history: int = 5
    uncertainty_rate: float = 0.15
    _last_filler: str = field(default="", repr=False)
    _last_structure: str = field(default="", repr=False)

    # Language-specific filler words (empty string = no filler for natural variation)
    FILLERS: dict[str, list[str]] = field(default_factory=lambda: {
        "ja": ["えーと、", "そうですね、", "うーん、", "あ、", "ちょっと待って、", "んー、", ""],
        "en": ["Hmm, ", "Yeah, ", "So, ", "Oh, ", "Actually, ", "Well, ", ""],
        "es": ["Bueno, ", "A ver, ", "Pues, ", "Oye, ", "Mira, ", ""],
    }, repr=False)

    # Message structure patterns to break greeting→acknowledgment→question monotony
    STRUCTURES: dict[str, list[str]] = field(default_factory=lambda: {
        "ja": [
            "acknowledgment_only",       # 承認のみ（質問しない）
            "question_first",            # 質問から入る
            "empathy_then_question",     # 共感→質問
            "filler_then_substance",     # フィラー→本題
            "conclusion_then_detail",    # 結論→補足
            "reaction_then_topic",       # リアクション→話題展開
        ],
        "en": [
            "acknowledgment_only",
            "question_first",
            "empathy_then_question",
            "filler_then_substance",
            "conclusion_then_detail",
            "reaction_then_topic",
        ],
        "es": [
            "acknowledgment_only",
            "question_first",
            "empathy_then_question",
            "filler_then_substance",
            "conclusion_then_detail",
            "reaction_then_topic",
        ],
    }, repr=False)

    def get_filler(self, language: str) -> str:
        """言語に応じたフィラー語をランダムに返す."""
        fillers = self.FILLERS.get(language, self.FILLERS["en"])
        filler = random.choice(fillers)
        self._last_filler = filler
        return filler

    def get_structure_pattern(self, language: str) -> str:
        """メッセージ構造パターンをランダムに選択する."""
        structures = self.STRUCTURES.get(language, self.STRUCTURES["en"])
        structure = random.choice(structures)
        self._last_structure = structure
        return structure

    def select_style(self, context: dict[str, Any] | None = None) -> StyleType:
        """文脈を考慮して文体パターンを選択する.

        直近の履歴に含まれるパターンの重みを下げ、
        同じパターンの連続使用を抑制する。

        Args:
            context: 会話文脈（感情状態、話題など）

        Returns:
            選択された文体パターンの種別
        """
        available = list(StyleType)
        weights: list[float] = []

        for style in available:
            pattern = self.patterns.get(style, StylePattern(style_type=style))
            w = pattern.weight
            # 直近使用したパターンの重みを減衰
            if style in self.history[-3:]:
                w *= 0.3
            weights.append(w)

        selected = random.choices(available, weights=weights, k=1)[0]
        self._record(selected)
        return selected

    def get_template(self, style: StyleType) -> str | None:
        """指定パターンのテンプレートをランダムに1つ返す.

        Args:
            style: 文体パターン種別

        Returns:
            テンプレート文字列。パターン未定義の場合は None。
        """
        pattern = self.patterns.get(style)
        if pattern and pattern.templates:
            return random.choice(pattern.templates)
        return None

    def should_insert_uncertainty(self) -> bool:
        """不確実表現を挿入すべきかを確率的に判定する.

        Returns:
            挿入すべきなら True
        """
        return random.random() < self.uncertainty_rate

    def add_variation(self, text: str) -> str:
        """テキストに文体的揺らぎを付加する.

        基底実装では文長のばらつきのみを扱う。
        言語固有の揺らぎは派生クラスでオーバーライドする。

        Args:
            text: 元テキスト

        Returns:
            揺らぎを付加したテキスト
        """
        # 基底クラスではパススルー（派生クラスで拡張）
        return text

    def _record(self, style: StyleType) -> None:
        """使用履歴を記録する."""
        self.history.append(style)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> StyleVariator:
        """設定辞書からインスタンスを生成する.

        Args:
            config: style_patterns 形式の設定辞書

        Returns:
            設定に基づく StyleVariator インスタンス
        """
        patterns: dict[StyleType, StylePattern] = {}
        for style_cfg in config.get("style_patterns", []):
            style_type = StyleType(style_cfg["type"])
            patterns[style_type] = StylePattern(
                style_type=style_type,
                templates=style_cfg.get("templates", []),
                weight=style_cfg.get("weight", 1.0),
            )
        return cls(
            patterns=patterns,
            uncertainty_rate=config.get("uncertainty_rate", 0.15),
        )
