"""
StyleVariator — Linguistic style variation engine.

This module applies stylistic variations to responses, making AI-generated text
less uniform and more human-like. Supports multiple registers (formal, business,
casual) and emotion-based adjustments.

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

import random
import re
from enum import Enum
from typing import Any


class Register(Enum):
    """Linguistic register levels."""
    FORMAL = "formal"
    BUSINESS = "business"
    CASUAL = "casual"
    TECHNICAL = "technical"


class StyleVariator:
    """
    Manages linguistic style variation.

    Applies register-based adjustments, emotion-driven modifications,
    and stochastic variations to avoid bot-like repetitiveness.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize StyleVariator.

        Args:
            config: Configuration dict with style parameters.
        """
        self.config: dict[str, Any] = config
        self.register_rules: dict[str, dict[str, str]] = config.get('register_rules', {})
        self.hedges: list[str] = config.get('hedges', ['I think', 'kind of', 'maybe', 'I guess'])
        self.intensifiers: list[str] = config.get('intensifiers', ['really', 'very', 'quite'])

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

        # Apply register-specific rules
        text = self._apply_register(text, register)

        # Apply emotion-based modifications
        if emotion:
            text = self._apply_emotion(text, emotion)

        # Random stylistic tweaks
        text = self._add_stochastic_variation(text)

        return text

    def _apply_register(self, text: str, register: Register) -> str:
        """
        Apply register-specific transformations.

        Args:
            text: Input text.
            register: Target register.

        Returns:
            Modified text.
        """
        if register == Register.FORMAL:
            # Avoid contractions
            text = text.replace("don't", "do not")
            text = text.replace("won't", "will not")
            text = text.replace("can't", "cannot")
            text = text.replace("I'm", "I am")
            text = text.replace("it's", "it is")
            # Add formal markers
            if random.random() < 0.3:
                text = "I would like to note that " + text

        elif register == Register.BUSINESS:
            # Professional but accessible
            text = text.replace("gonna", "going to")
            text = text.replace("kinda", "kind of")
            # Add business language
            if random.random() < 0.2:
                text = "Based on my analysis, " + text

        elif register == Register.CASUAL:
            # Allow contractions, colloquialisms
            if random.random() < 0.1:
                text = text.replace(" really ", " like, really ")
            # Add casual markers
            if random.random() < 0.15:
                text = text + " y'know?"

        elif register == Register.TECHNICAL:
            # Add technical vocabulary
            if random.random() < 0.2:
                text = "Technically speaking, " + text

        return text

    def _apply_emotion(self, text: str, emotion: str) -> str:
        """
        Apply emotion-driven modifications.

        Args:
            text: Input text.
            emotion: Emotion state.

        Returns:
            Emotion-modified text.
        """
        if emotion == 'happy':
            # Add positive markers
            if random.random() < 0.2:
                text = text + " :)"
            # Add exclamation
            text = re.sub(r'\.(\s|$)', r'!\1', text, count=1)

        elif emotion == 'angry':
            # More emphatic
            if random.random() < 0.2:
                text = text.upper()
            text = re.sub(r'\.(\s|$)', r'!!\1', text, count=1)

        elif emotion == 'sad':
            # Add hedges and uncertainty
            if random.random() < 0.3:
                text = random.choice(self.hedges) + " " + text

        elif emotion == 'confused':
            # Add uncertainty markers
            if random.random() < 0.3:
                text = text + " ...I think?"

        return text

    def _add_stochastic_variation(self, text: str) -> str:
        """
        Add random stylistic variations.

        Args:
            text: Input text.

        Returns:
            Varied text.
        """
        # Occasionally add hedges
        if random.random() < 0.15:
            hedge = random.choice(self.hedges)
            text = hedge + ", " + text

        # Occasionally use intensifiers
        if random.random() < 0.1:
            intensifier = random.choice(self.intensifiers)
            # Find an adjective and intensify it
            words = text.split()
            for i, word in enumerate(words):
                if len(word) > 5:  # Rough heuristic for adjectives
                    words.insert(i, intensifier)
                    text = ' '.join(words)
                    break

        return text

    def select_register(self, platform: object | None) -> Register:
        """
        Select appropriate register based on platform.

        Args:
            platform: Communication platform (e.g., Discord, LinkedIn, Email).

        Returns:
            Recommended Register.
        """
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
        """
        Vary sentence structure and length.

        Args:
            text: Input text.

        Returns:
            Text with varied sentence structure.
        """
        sentences = re.split(r'([.!?]+)', text)
        # Shuffle sentence structure (careful to preserve meaning)
        # This is a placeholder; real implementation would be more sophisticated
        return text

    def add_filler_words(self, text: str, rate: float = 0.1) -> str:
        """
        Add filler words like 'um', 'like', 'well' for spoken-like text.

        Args:
            text: Input text.
            rate: Probability of adding filler (0.0 to 1.0).

        Returns:
            Text with filler words.
        """
        if random.random() < rate:
            fillers = ['well', 'um', 'like', 'you know', 'I mean']
            filler = random.choice(fillers)
            return filler + ", " + text

        return text

    def humanize_punctuation(self, text: str) -> str:
        """
        Vary punctuation for more human feel.

        Args:
            text: Input text.

        Returns:
            Text with humanized punctuation.
        """
        # Sometimes replace period with ellipsis
        if random.random() < 0.05:
            text = re.sub(r'\.(\s|$)', r'...\1', text, count=1)

        # Sometimes add ellipsis mid-sentence
        if random.random() < 0.03:
            words = text.split()
            if len(words) > 5:
                split_point = random.randint(2, len(words) - 2)
                text = ' '.join(words[:split_point]) + "..." + ' '.join(words[split_point:])

        return text
