"""
StyleVariator — Linguistic style variation engine.

This module applies stylistic variations to responses, making AI-generated text
less uniform and more human-like. Supports multiple registers (formal, business,
casual) and emotion-based adjustments.

v2 API adds: no-arg constructor, from_config(), select_style(), get_template(),
get_filler(), get_structure_pattern(), add_variation().

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Register(Enum):
    """Linguistic register levels."""
    FORMAL = "formal"
    BUSINESS = "business"
    CASUAL = "casual"
    TECHNICAL = "technical"


class StyleType(Enum):
    """Types of stylistic patterns."""
    CONFIRMATION = "confirmation"
    UNCERTAIN = "uncertain"
    EMPHATIC = "emphatic"
    HEDGE = "hedge"
    FILLER = "filler"


@dataclass
class StylePattern:
    """A stylistic pattern with adjustable weight."""
    style_type: StyleType
    weight: float = 1.0
    templates: list[str] = field(default_factory=list)

    @property
    def examples(self) -> list[str]:
        """Backward-compatible alias for templates."""
        return self.templates

    @examples.setter
    def examples(self, value: list[str]) -> None:
        self.templates = value


# ---------------------------------------------------------------------------
# Language-specific defaults
# ---------------------------------------------------------------------------

_FILLER_WORDS: dict[str, list[str]] = {
    "ja": ["えっと", "あの", "まあ", "そうですね", "ちょっと"],
    "en": ["well", "um", "like", "you know", "I mean"],
    "es": ["bueno", "pues", "o sea", "a ver", "digamos"],
}

_STRUCTURE_PATTERNS: dict[str, list[str]] = {
    "ja": [
        "結論→理由→補足",
        "共感→提案→確認",
        "状況確認→回答→次のアクション",
        "質問返し→自分の見解→提案",
    ],
    "en": [
        "answer → reasoning → caveat",
        "acknowledge → respond → follow-up",
        "context → solution → next steps",
        "restate question → answer → offer help",
    ],
    "es": [
        "respuesta → razón → matiz",
        "empatía → propuesta → confirmación",
        "contexto → solución → pasos siguientes",
        "reformulación → respuesta → oferta de ayuda",
    ],
}

_DEFAULT_PATTERNS: dict[StyleType, StylePattern] = {
    StyleType.CONFIRMATION: StylePattern(
        style_type=StyleType.CONFIRMATION, weight=1.0,
        templates=["right", "exactly", "indeed"],
    ),
    StyleType.UNCERTAIN: StylePattern(
        style_type=StyleType.UNCERTAIN, weight=1.0,
        templates=["maybe", "perhaps", "I'm not sure"],
    ),
    StyleType.EMPHATIC: StylePattern(
        style_type=StyleType.EMPHATIC, weight=1.0,
        templates=["absolutely", "definitely", "certainly"],
    ),
    StyleType.HEDGE: StylePattern(
        style_type=StyleType.HEDGE, weight=1.0,
        templates=["I think", "kind of", "maybe", "I guess"],
    ),
    StyleType.FILLER: StylePattern(
        style_type=StyleType.FILLER, weight=1.0,
        templates=["well", "um", "like"],
    ),
}

# Map config type strings to StyleType enum
_TYPE_MAP: dict[str, StyleType] = {
    "confirmation": StyleType.CONFIRMATION,
    "uncertain": StyleType.UNCERTAIN,
    "emphatic": StyleType.EMPHATIC,
    "hedge": StyleType.HEDGE,
    "filler": StyleType.FILLER,
    # Aliases from config files
    "empathy": StyleType.EMPHATIC,
    "deferral": StyleType.HEDGE,
    "transition": StyleType.FILLER,
}


class StyleVariator:
    """
    Manages linguistic style variation.

    Supports two modes:
    - v1: config-dict constructor with apply_variation()
    - v2: no-arg / from_config() with select_style(), get_template(), etc.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize StyleVariator.

        Args:
            config: Optional configuration dict. If None, uses defaults.
        """
        if config is not None:
            self._init_v1(config)
        else:
            self._init_defaults()

    def _init_v1(self, config: dict[str, Any]) -> None:
        """Initialize from v1 config dict."""
        self.config: dict[str, Any] = config
        self.register_rules: dict[str, dict[str, str]] = config.get('register_rules', {})
        self.hedges: list[str] = config.get('hedges', ['I think', 'kind of', 'maybe', 'I guess'])
        self.intensifiers: list[str] = config.get('intensifiers', ['really', 'very', 'quite'])
        self.uncertainty_rate: float = config.get('uncertainty_rate', 0.15)
        self.patterns: dict[StyleType, StylePattern] = {
            st: StylePattern(style_type=st, weight=p.weight, templates=list(p.templates))
            for st, p in _DEFAULT_PATTERNS.items()
        }
        # v2 attributes
        self.history: list[StyleType] = []
        self.max_history: int = 20

    def _init_defaults(self) -> None:
        """Initialize with defaults (v2 no-arg)."""
        self.config: dict[str, Any] = {}
        self.register_rules: dict[str, dict[str, str]] = {}
        self.hedges: list[str] = ['I think', 'kind of', 'maybe', 'I guess']
        self.intensifiers: list[str] = ['really', 'very', 'quite']
        self.uncertainty_rate: float = 0.15
        self.patterns: dict[StyleType, StylePattern] = {
            st: StylePattern(style_type=st, weight=p.weight, templates=list(p.templates))
            for st, p in _DEFAULT_PATTERNS.items()
        }
        self.history: list[StyleType] = []
        self.max_history: int = 20

    # ------------------------------------------------------------------
    # v2 API
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, style_config: dict[str, Any]) -> StyleVariator:
        """
        Create StyleVariator from a style config section.

        Args:
            style_config: Dict with keys like uncertainty_rate, style_patterns, etc.
        """
        sv = cls.__new__(cls)
        sv.config = style_config
        sv.register_rules = {}
        sv.hedges = ['I think', 'kind of', 'maybe', 'I guess']
        sv.intensifiers = ['really', 'very', 'quite']
        sv.uncertainty_rate = style_config.get('uncertainty_rate', 0.15)
        sv.history = []
        sv.max_history = 20

        # Parse style_patterns from config
        sv.patterns = {}
        for p_conf in style_config.get('style_patterns', []):
            type_str = p_conf.get('type', '')
            style_type = _TYPE_MAP.get(type_str)
            if style_type is None:
                continue
            sv.patterns[style_type] = StylePattern(
                style_type=style_type,
                weight=p_conf.get('weight', 1.0),
                templates=p_conf.get('templates', []),
            )

        # Ensure all StyleType values have patterns
        for st in StyleType:
            if st not in sv.patterns:
                sv.patterns[st] = StylePattern(
                    style_type=st, weight=_DEFAULT_PATTERNS[st].weight,
                    templates=list(_DEFAULT_PATTERNS[st].templates),
                )

        return sv

    def select_style(self, context: dict[str, float] | None = None) -> StyleType:
        """
        Select a style type using weighted random selection with anti-repeat.

        Args:
            context: Optional tone modifier dict (from EmotionStateMachine).

        Returns:
            Selected StyleType.
        """
        weights: dict[StyleType, float] = {}
        for st, pattern in self.patterns.items():
            w = pattern.weight
            # Reduce weight for recently used styles
            if st in self.history[-3:]:
                w *= 0.3
            weights[st] = max(w, 0.01)

        styles = list(weights.keys())
        w_list = [weights[s] for s in styles]
        total = sum(w_list)
        w_norm = [w / total for w in w_list]

        r = random.random()
        cumulative = 0.0
        selected = styles[0]
        for style, w in zip(styles, w_norm):
            cumulative += w
            if r <= cumulative:
                selected = style
                break

        self.history.append(selected)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        return selected

    def get_template(self, style_type: StyleType) -> str | None:
        """
        Get a random template for the given style type.

        Returns:
            Template string, or None if no templates available.
        """
        pattern = self.patterns.get(style_type)
        if pattern and pattern.templates:
            return random.choice(pattern.templates)
        return None

    def get_filler(self, lang: str) -> str:
        """
        Get a random filler word for the given language.

        Args:
            lang: ISO 639-1 language code (ja, en, es).
        """
        fillers = _FILLER_WORDS.get(lang, _FILLER_WORDS["en"])
        return random.choice(fillers)

    def get_structure_pattern(self, lang: str) -> str:
        """
        Get a random structure pattern for the given language.

        Args:
            lang: ISO 639-1 language code (ja, en, es).
        """
        patterns = _STRUCTURE_PATTERNS.get(lang, _STRUCTURE_PATTERNS["en"])
        return random.choice(patterns)

    def add_variation(self, text: str) -> str:
        """
        Base implementation: passthrough (no modification).

        Derived classes may override for language-specific variation.
        """
        return text

    # ------------------------------------------------------------------
    # v1 API (preserved for backward compatibility)
    # ------------------------------------------------------------------

    def apply_variation(self, text: str, register: Register | str = Register.CASUAL, emotion: str | None = None) -> str:
        """
        Apply stylistic variation to text.

        Args:
            text: Input text to modify.
            register: Linguistic register (formal/business/casual/technical).
            emotion: Current emotion state (affects intensity, hedging).

        Returns:
            Stylistically varied text.
        """
        if isinstance(register, str):
            try:
                register = Register(register)
            except ValueError:
                register = Register.CASUAL

        text = self._apply_register(text, register)
        if emotion:
            text = self._apply_emotion(text, emotion)
        text = self._add_stochastic_variation(text)
        return text

    def _apply_register(self, text: str, register: Register) -> str:
        """Apply register-specific transformations."""
        if register == Register.FORMAL:
            text = text.replace("don't", "do not")
            text = text.replace("won't", "will not")
            text = text.replace("can't", "cannot")
            text = text.replace("I'm", "I am")
            text = text.replace("it's", "it is")
            if random.random() < 0.3:
                text = "I would like to note that " + text
        elif register == Register.BUSINESS:
            text = text.replace("gonna", "going to")
            text = text.replace("kinda", "kind of")
            if random.random() < 0.2:
                text = "Based on my analysis, " + text
        elif register == Register.CASUAL:
            if random.random() < 0.1:
                text = text.replace(" really ", " like, really ")
            if random.random() < 0.15:
                text = text + " y'know?"
        elif register == Register.TECHNICAL:
            if random.random() < 0.2:
                text = "Technically speaking, " + text
        return text

    def _apply_emotion(self, text: str, emotion: str) -> str:
        """Apply emotion-driven modifications."""
        if emotion == 'happy':
            if random.random() < 0.2:
                text = text + " :)"
            text = re.sub(r'\.(\s|$)', r'!\1', text, count=1)
        elif emotion == 'angry':
            if random.random() < 0.2:
                text = text.upper()
            text = re.sub(r'\.(\s|$)', r'!!\1', text, count=1)
        elif emotion == 'sad':
            if random.random() < 0.3:
                text = random.choice(self.hedges) + " " + text
        elif emotion == 'confused':
            if random.random() < 0.3:
                text = text + " ...I think?"
        return text

    def _add_stochastic_variation(self, text: str) -> str:
        """Add random stylistic variations."""
        if random.random() < 0.15:
            hedge = random.choice(self.hedges)
            text = hedge + ", " + text
        if random.random() < 0.1:
            intensifier = random.choice(self.intensifiers)
            words = text.split()
            for i, word in enumerate(words):
                if len(word) > 5:
                    words.insert(i, intensifier)
                    text = ' '.join(words)
                    break
        return text

    def select_register(self, platform: object | None) -> Register:
        """Select appropriate register based on platform."""
        if platform is None:
            return Register.CASUAL
        platform_str = str(platform).lower()
        if 'email' in platform_str or 'slack' in platform_str:
            return Register.BUSINESS
        elif 'twitter' in platform_str or 'reddit' in platform_str:
            return Register.CASUAL
        elif 'discord' in platform_str:
            return Register.CASUAL
        else:
            return Register.CASUAL

    def vary_sentence_structure(self, text: str) -> str:
        """Vary sentence structure and length."""
        return text

    def add_filler_words(self, text: str, rate: float = 0.1) -> str:
        """Add filler words for spoken-like text."""
        if random.random() < rate:
            fillers = ['well', 'um', 'like', 'you know', 'I mean']
            filler = random.choice(fillers)
            return filler + ", " + text
        return text

    def humanize_punctuation(self, text: str) -> str:
        """Vary punctuation for more human feel."""
        if random.random() < 0.05:
            text = re.sub(r'\.(\s|$)', r'...\1', text, count=1)
        if random.random() < 0.03:
            words = text.split()
            if len(words) > 5:
                split_point = random.randint(2, len(words) - 2)
                text = ' '.join(words[:split_point]) + "..." + ' '.join(words[split_point:])
        return text
