"""
HumanPersonaBase — Language-agnostic base class for human-like AI communication.

This module provides the foundational abstraction for generating responses
that exhibit human communication patterns: variable timing, style fluctuation,
emotional state evolution, contextual back-referencing, intentional ambiguity,
and escalation detection.

All language/culture-specific behavior is delegated to configuration (config/*.json)
and derived persona classes. The base class itself is culturally neutral.

Architecture:
    HumanPersonaBase (this class)
    ├── TimingController      — response delay simulation
    ├── StyleVariator         — linguistic variation engine
    ├── EmotionStateMachine   — affective state tracking
    ├── ContextReferencer     — conversation memory & back-referencing
    └── EscalationDetector    — human handoff trigger detection

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
from .escalation_detector import EscalationDetector


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
    """Output of the persona pipeline."""
    content: str
    delay_seconds: float
    emotion_state: str
    escalation_triggered: bool = False
    escalation_type: Optional[str] = None
    escalation_action: Optional[str] = None
    debug: dict[str, Any] = field(default_factory=dict)


class Platform(Enum):
    """Supported communication platforms."""
    CHAT = auto()
    CROWDSOURCING = auto()
    EMAIL = auto()
    CUSTOM = auto()


# ---------------------------------------------------------------------------
# Configuration loader
# ---------------------------------------------------------------------------

def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load and validate a persona configuration JSON file.

    Args:
        config_path: Path to a persona config JSON (e.g. config/ja.json).

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If config file does not exist.
        json.JSONDecodeError: If config is not valid JSON.
        ValueError: If required top-level keys are missing.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    required_keys = {"meta", "timing", "style", "emotion", "escalation"}
    missing = required_keys - set(config.keys())
    if missing:
        raise ValueError(f"Config missing required keys: {missing}")

    return config


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class HumanPersonaBase(ABC):
    """Abstract base class for human-like AI persona behavior.

    This class orchestrates the full response pipeline:
    1. Receive incoming message
    2. Detect escalation conditions
    3. Update emotional state
    4. Generate response content (delegated to subclass)
    5. Apply style variation
    6. Insert context references
    7. Apply intentional ambiguity
    8. Calculate response delay

    Subclasses MUST implement:
        - generate_raw_response(message, context) -> str
        - extract_topics(message) -> list[str]

    Subclasses MAY override:
        - on_escalation(trigger) -> PersonaResponse
        - post_process(response) -> str
    """

    def __init__(self, config: dict[str, Any], platform: Platform = Platform.CHAT):
        """Initialize persona with configuration.

        Args:
            config: Parsed persona configuration dictionary.
            platform: Communication platform for timing calibration.
        """
        self._config = config
        self._platform = platform
        self._conversation: list[Message] = []
        self._turn_count: int = 0

        # Initialize sub-components
        self._timing = TimingController(
            config.get("timing", {}),
            platform.name.lower(),
        )
        self._style = StyleVariator(config.get("style", {}))
        self._emotion = EmotionStateMachine(config.get("emotion", {}))
        self._context = ContextReferencer(config.get("context_reference", {}))
        self._escalation = EscalationDetector(config.get("escalation", {}))

    # -- Properties ----------------------------------------------------------

    @property
    def persona_id(self) -> str:
        return self._config.get("meta", {}).get("persona_id", "unknown")

    @property
    def language(self) -> str:
        return self._config.get("meta", {}).get("language", "en")

    @property
    def culture_context(self) -> str:
        return self._config.get("meta", {}).get("context_culture", "low")

    @property
    def current_emotion(self) -> str:
        return self._emotion.current_state

    @property
    def turn_count(self) -> int:
        return self._turn_count

    @property
    def conversation_history(self) -> list[Message]:
        return list(self._conversation)

    # -- Abstract methods (subclass contract) --------------------------------

    @abstractmethod
    def generate_raw_response(
        self,
        message: str,
        context: list[Message],
    ) -> str:
        """Generate the core response content.

        This is where the actual LLM call or template logic lives.
        The base class handles all human-likeness transformations around it.

        Args:
            message: The incoming user message text.
            context: Recent conversation history for reference.

        Returns:
            Raw response string before style/ambiguity processing.
        """
        ...

    @abstractmethod
    def extract_topics(self, message: str) -> list[str]:
        """Extract key topics/entities from a message.

        Used by ContextReferencer to generate natural back-references.

        Args:
            message: Message text to analyze.

        Returns:
            List of topic strings found in the message.
        """
        ...

    # -- Overridable hooks ---------------------------------------------------

    def on_escalation(
        self,
        trigger_type: str,
        action: str,
        message: str,
    ) -> PersonaResponse:
        """Handle an escalation event.

        Default behavior: return the configured fallback message.
        Override for custom escalation logic (e.g. Slack notification).

        Args:
            trigger_type: Category of escalation trigger.
            action: Configured action (notify_human, pause_and_notify, etc.).
            message: The message that triggered escalation.

        Returns:
            PersonaResponse with escalation metadata.
        """
        fallback = self._config.get("escalation", {}).get(
            "fallback_message",
            "I'll need to check on that and get back to you.",
        )
        delay = self._timing.calculate_delay(len(fallback))

        return PersonaResponse(
            content=fallback,
            delay_seconds=delay,
            emotion_state=self._emotion.current_state,
            escalation_triggered=True,
            escalation_type=trigger_type,
            escalation_action=action,
        )

    def post_process(self, response: str) -> str:
        """Final transformation hook before returning response.

        Override for language-specific post-processing
        (e.g. honorific adjustment, character-width normalization).

        Args:
            response: Processed response text.

        Returns:
            Final response text.
        """
        return response

    # -- Core pipeline -------------------------------------------------------

    def process_message(self, message: str) -> PersonaResponse:
        """Full persona response pipeline.

        This is the main entry point. Call this with each incoming message.

        Pipeline stages:
            1. Record incoming message
            2. Check escalation conditions
            3. Update emotion state
            4. Generate raw response
            5. Apply style variation
            6. Insert context references
            7. Apply ambiguity
            8. Post-process (subclass hook)
            9. Calculate timing delay
            10. Record outgoing message

        Args:
            message: Incoming message text.

        Returns:
            PersonaResponse containing the final response and metadata.
        """
        # 1. Record incoming
        incoming = Message(role="user", content=message)
        self._conversation.append(incoming)
        self._turn_count += 1

        # 2. Escalation check (before generating response)
        esc_result = self._escalation.check(
            message=message,
            turn_count=self._turn_count,
            conversation=self._conversation,
        )
        if esc_result is not None:
            return self.on_escalation(
                trigger_type=esc_result["type"],
                action=esc_result["action"],
                message=message,
            )

        # 3. Update emotion state
        self._emotion.update(
            message=message,
            turn_count=self._turn_count,
        )

        # 4. Generate raw response
        recent_context = self._conversation[-10:]  # last 10 messages
        raw_response = self.generate_raw_response(message, recent_context)

        # 5. Apply style variation
        styled = self._style.apply(
            text=raw_response,
            emotion_params=self._emotion.current_params,
        )

        # 6. Insert context references
        topics = self.extract_topics(message)
        referenced = self._context.apply(
            text=styled,
            topics=topics,
            conversation=self._conversation,
        )

        # 7. Apply ambiguity
        ambiguity_config = self._config.get("ambiguity", {})
        ambiguous = self._apply_ambiguity(referenced, ambiguity_config)

        # 8. Post-process (subclass hook)
        final_text = self.post_process(ambiguous)

        # 9. Calculate delay
        emotion_multiplier = self._emotion.current_params.get(
            "response_delay_multiplier", 1.0
        )
        delay = self._timing.calculate_delay(
            message_length=len(message),
            multiplier=emotion_multiplier,
        )

        # 10. Record outgoing
        outgoing = Message(
            role="persona",
            content=final_text,
            metadata={
                "emotion_state": self._emotion.current_state,
                "delay_seconds": delay,
                "style_applied": True,
            },
        )
        self._conversation.append(outgoing)

        return PersonaResponse(
            content=final_text,
            delay_seconds=delay,
            emotion_state=self._emotion.current_state,
            debug={
                "raw_response": raw_response,
                "turn_count": self._turn_count,
                "topics_extracted": topics,
            },
        )

    # -- Internal helpers ----------------------------------------------------

    def _apply_ambiguity(self, text: str, config: dict[str, Any]) -> str:
        """Apply intentional imperfection to response text.

        Adds hedging, approximations, and occasional self-corrections
        to avoid the uncanny precision of AI-generated text.
        """
        hedge_prob = config.get("hedge_probability", 0.15)
        self_correction_rate = config.get("self_correction_rate", 0.02)

        result = text

        # Self-correction injection (very rare)
        if random.random() < self_correction_rate:
            result = self._inject_self_correction(result)

        return result

    def _inject_self_correction(self, text: str) -> str:
        """Inject a natural self-correction into the text.

        This is a base implementation; derived classes should override
        with language-appropriate corrections.
        """
        # Base implementation is a no-op; language-specific subclasses
        # provide actual self-correction patterns
        return text

    # -- Serialization -------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize persona state for persistence."""
        return {
            "persona_id": self.persona_id,
            "turn_count": self._turn_count,
            "emotion_state": self._emotion.current_state,
            "conversation_length": len(self._conversation),
            "platform": self._platform.name,
        }

    def reset(self) -> None:
        """Reset persona to initial state (new conversation)."""
        self._conversation.clear()
        self._turn_count = 0
        self._emotion.reset()
        self._context.reset()

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"id={self.persona_id!r} "
            f"lang={self.language!r} "
            f"turn={self._turn_count} "
            f"emotion={self.current_emotion!r}>"
        )
