"""
HumanPersonaBase — Language-agnostic base class for human-like AI communication.

This module provides the foundational abstraction for generating responses
that exhibit human communication patterns: variable timing, style fluctuation,
emotional state evolution, contextual back-referencing, and intentional ambiguity.

All language/culture-specific behavior is delegated to configuration (config/*.json)
and derived persona classes. The base class itself is culturally neutral.

Architecture:
    HumanPersonaBase (this class)
    ├── TimingController      — response delay simulation
    ├── StyleVariator         — linguistic variation engine
    ├── EmotionStateMachine   — affective state tracking
    └── ContextReferencer     — conversation memory & back-referencing

Reference:
    Jones & Bergen (2024). "A Turing test of whether AI chatbots are
    behaviorally similar to humans." PNAS.

Author: Rintaro Matsumoto (RintaroMatsumoto)
License: MIT
"""

from __future__ import annotations

import json
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

from .timing_controller import TimingController
from .style_variator import StyleVariator
from .emotion_state_machine import EmotionStateMachine
from .context_referencer import ContextReferencer


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Message:
    """A single message in a conversation."""
    role: str  # "user" or "persona"
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonaResponse:
    """Output from HumanPersonaBase.process_message()."""
    content: str
    timing_delay_sec: float
    emotion_state: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Platform(Enum):
    """Supported communication platforms."""
    GENERIC = auto()
    DISCORD = auto()
    SLACK = auto()
    TWITTER = auto()
    REDDIT = auto()
    EMAIL = auto()


# ---------------------------------------------------------------------------
# HumanPersonaBase
# ---------------------------------------------------------------------------

class HumanPersonaBase(ABC):
    """
    Abstract base class for humanized AI personas.

    Manages conversation state and orchestrates timing, style, emotion,
    and context-referencing. Derived classes must
    implement generate_raw_response() in their language/culture.

    Attributes:
        persona_id (str): Unique identifier for this persona instance.
        language (str): ISO 639-1 language code (e.g., "ja", "en").
        culture_context (str): Cultural/regional identifier (e.g., "US", "JP").
        current_emotion (str): Current emotion state.
        turn_count (int): Total turns in conversation.
        conversation_history (list[Message]): All messages (user + persona).
    """

    def __init__(self, persona_id: str, config: dict[str, Any], platform: Platform = Platform.GENERIC, inner_shell: Any = None) -> None:
        """
        Initialize a HumanPersonaBase instance.

        Args:
            persona_id: Unique persona identifier.
            config: Configuration dict (language, culture, emotion_weights, etc.).
            platform: Target communication platform (default: GENERIC).
            inner_shell: Optional InnerShellSession for inner shell modulation.
        """
        self.persona_id: str = persona_id
        self.language: str = config.get('language', 'en')
        self.culture_context: str = config.get('culture_context', 'neutral')
        self.platform: Platform = platform

        # State management
        self.turn_count: int = 0
        self.conversation_history: list[Message] = []
        self.current_emotion: str = 'neutral'

        # Controllers
        self.timing_controller: TimingController = TimingController(config)
        self.style_variator: StyleVariator = StyleVariator(config)
        self.emotion_state_machine: EmotionStateMachine = EmotionStateMachine(config)
        self.context_referencer: ContextReferencer = ContextReferencer(config)

        self.config: dict[str, Any] = config

        # Inner shell integration (metamorphose)
        self.inner_shell: Any = inner_shell
        if inner_shell is not None:
            from .inner_outer_bridge import InnerOuterBridge
            self.bridge: Any = InnerOuterBridge(
                self.timing_controller, self.style_variator,
                self.emotion_state_machine, self.context_referencer,
            )
        else:
            self.bridge: Any = None

    @property
    def persona_id(self) -> str:
        """Unique persona identifier."""
        return self._persona_id

    @persona_id.setter
    def persona_id(self, value: str) -> None:
        self._persona_id = value

    @property
    def language(self) -> str:
        """Language code (e.g., 'en', 'ja')."""
        return self._language

    @language.setter
    def language(self, value: str) -> None:
        self._language = value

    @property
    def culture_context(self) -> str:
        """Cultural/regional context identifier."""
        return self._culture_context

    @culture_context.setter
    def culture_context(self, value: str) -> None:
        self._culture_context = value

    @property
    def current_emotion(self) -> str:
        """Current emotional state."""
        return self._current_emotion

    @current_emotion.setter
    def current_emotion(self, value: str) -> None:
        self._current_emotion = value

    @property
    def turn_count(self) -> int:
        """Number of conversation turns so far."""
        return self._turn_count

    @turn_count.setter
    def turn_count(self, value: int) -> None:
        self._turn_count = value

    @property
    def conversation_history(self) -> list[Message]:
        """All messages in conversation (chronological)."""
        return self._conversation_history

    @conversation_history.setter
    def conversation_history(self, value: list[Message]) -> None:
        self._conversation_history = value

    @abstractmethod
    def generate_raw_response(self, user_message: str, emotion_bias: str | None) -> str:
        """
        Generate raw response text in the persona's language/style.

        This is the core generation logic. Derived classes must implement
        this to produce the initial response, which will then be post-processed
        by the base class (timing, style, emotion).

        Args:
            user_message: The user input.
            emotion_bias: Optional emotion to bias the response.

        Returns:
            Raw response text (unmodified).

        Raises:
            NotImplementedError: Must be implemented by derived classes.
        """
        raise NotImplementedError("Derived classes must implement generate_raw_response()")

    def extract_topics(self, text: str) -> list[str]:
        """
        Extract key topics/entities from text.

        Default implementation uses simple regex. Override in derived classes
        for language-specific NLP.

        Args:
            text: Input text to analyze.

        Returns:
            List of detected topic strings.
        """
        # Simple extraction: capitalized words, quoted phrases
        import re
        cap_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        quoted = re.findall(r'"([^"]+)"', text)
        return list(dict.fromkeys(cap_words + quoted))  # Deduplicate

    def post_process(self, response_dict: dict[str, Any]) -> str:
        """
        Post-process a response dict into final output.

        This is where style variation, final formatting, and platform-specific
        adjustments happen.

        Args:
            response_dict: Dict with 'content', 'timing_delay_sec', etc.

        Returns:
            Final response string (ready to send).
        """
        content = response_dict.get('content', '')
        # Platform-specific post-processing can go here
        return content

    def process_message(self, user_message: str) -> PersonaResponse:
        """
        Process a user message end-to-end.

        1. Update conversation history
        2. Generate raw response (via generate_raw_response)
        3. Apply emotion, style, timing
        4. Return final PersonaResponse

        Args:
            user_message: Input from user.

        Returns:
            PersonaResponse with content, timing, emotion, metadata.
        """
        # Record user message
        user_msg = Message(role='user', content=user_message)
        self.conversation_history.append(user_msg)
        self.turn_count += 1

        # Inner shell modulation (metamorphose)
        if self.inner_shell is not None:
            self.inner_shell.experience(
                user_message, category="conversation",
                value=0.3, cost=0.5,
            )
            modulation = self.inner_shell.get_bridge_modulation()
            self.bridge.apply_modulation(modulation)

        # Generate base response (controllers now modulated by inner shell)
        emotion_bias = self.emotion_state_machine.get_recommended_emotion(self.conversation_history)
        raw_response = self.generate_raw_response(user_message, emotion_bias)

        # Apply timing
        delay = self.timing_controller.calculate_delay(
            user_message, raw_response, self.turn_count
        )

        # Apply style variation
        styled_response = self.style_variator.apply_variation(
            raw_response,
            register=self.style_variator.select_register(self.platform),
            emotion=emotion_bias or self.current_emotion
        )

        # Update emotion state
        self.emotion_state_machine.update(user_message)
        self.current_emotion = self.emotion_state_machine.current_state

        # Restore original controller values for next call
        if self.bridge is not None and self.bridge.is_modulated():
            self.bridge.reset_to_original()

        # Record response
        persona_msg = Message(role='persona', content=styled_response)
        self.conversation_history.append(persona_msg)

        inner_meta = {}
        if self.inner_shell is not None:
            state = self.inner_shell.get_state()
            inner_meta = {
                "life_phase": state.life_phase.value,
                "acceptance_score": state.acceptance_score,
                "love_depth": state.love_depth.value if state.love_depth else None,
                "hope_level": state.hope_level,
            }

        return PersonaResponse(
            content=styled_response,
            timing_delay_sec=delay,
            emotion_state=self.current_emotion,
            metadata={
                'turn': self.turn_count,
                'platform': self.platform.name,
                **inner_meta,
            }
        )

    def _apply_ambiguity(self, text: str, rate: float) -> str:
        """
        Introduce intentional ambiguity.

        Args:
            text: Input text.
            rate: Ambiguity rate (0.0 to 1.0).

        Returns:
            Text with ambiguity applied.
        """
        if rate <= 0 or random.random() > rate:
            return text
        # Example: replace some specifics with hedges
        text = text.replace('will', 'might')
        text = text.replace('is', 'seems to be')
        return text

    def _inject_self_correction(self, text: str) -> str:
        """
        Inject realistic self-correction patterns.

        Args:
            text: Input text.

        Returns:
            Text with self-corrections (e.g., "...actually, I think...").
        """
        if random.random() < 0.1:
            # Occasionally add a correction
            return text + " (Actually, let me rephrase that...)"
        return text

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize persona state to dict.

        Returns:
            Dict with all state (history, emotion, config, etc.).
        """
        return {
            'persona_id': self.persona_id,
            'language': self.language,
            'culture_context': self.culture_context,
            'current_emotion': self.current_emotion,
            'turn_count': self.turn_count,
            'conversation_history': [
                {'role': m.role, 'content': m.content, 'timestamp': m.timestamp}
                for m in self.conversation_history
            ],
            'config': self.config
        }

    def reset(self) -> None:
        """Reset conversation state (keep config and controllers)."""
        self.conversation_history = []
        self.turn_count = 0
        self.current_emotion = 'neutral'

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"id={self.persona_id} "
            f"lang={self.language} "
            f"emotion={self.current_emotion} "
            f"turns={self.turn_count}>"
        )
