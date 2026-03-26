"""
EmotionStateMachine — Affective state tracking and evolution.

This module tracks emotional state transitions based on conversation patterns.
States evolve realistically with inertia, recovery time, and contagion effects.

v2 API adds: no-arg constructor, from_config(), process_event(), get_tone_modifier().

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


class EmotionState(Enum):
    """Enumeration of emotion states."""
    # v1 states (keyword-trigger based)
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    CONFUSED = "confused"
    # v2 states (conversation-progression based)
    FORMAL = "formal"
    WARMING = "warming"
    TRUSTED = "trusted"
    TENSE = "tense"
    RELIEVED = "relieved"


# Tone modifier presets per v2 state
_TONE_MODIFIERS: dict[EmotionState, dict[str, float]] = {
    EmotionState.FORMAL:   {"formality": 0.9, "warmth": 0.2, "caution": 0.5},
    EmotionState.WARMING:  {"formality": 0.5, "warmth": 0.6, "caution": 0.3},
    EmotionState.TRUSTED:  {"formality": 0.3, "warmth": 0.8, "caution": 0.2},
    EmotionState.TENSE:    {"formality": 0.7, "warmth": 0.1, "caution": 0.9},
    EmotionState.RELIEVED: {"formality": 0.4, "warmth": 0.8, "caution": 0.3},
    # Fallbacks for v1 states
    EmotionState.NEUTRAL:  {"formality": 0.5, "warmth": 0.5, "caution": 0.3},
    EmotionState.HAPPY:    {"formality": 0.3, "warmth": 0.9, "caution": 0.1},
    EmotionState.SAD:      {"formality": 0.6, "warmth": 0.3, "caution": 0.6},
    EmotionState.ANGRY:    {"formality": 0.4, "warmth": 0.1, "caution": 0.7},
    EmotionState.CONFUSED: {"formality": 0.5, "warmth": 0.4, "caution": 0.8},
}


@dataclass
class EmotionTransition:
    """Single emotion state transition."""
    from_state: str
    to_state: str
    trigger: str
    probability: float


# ---------------------------------------------------------------------------
# Default v2 transition table
# ---------------------------------------------------------------------------

@dataclass
class _TransitionRule:
    """Internal transition rule for process_event()."""
    from_state: EmotionState | None  # None = wildcard (any state)
    to_state: EmotionState
    trigger: str
    threshold: int | None = None  # For exchange_count thresholds


_DEFAULT_TRANSITIONS: list[_TransitionRule] = [
    _TransitionRule(EmotionState.FORMAL, EmotionState.WARMING, "exchange", threshold=3),
    _TransitionRule(EmotionState.WARMING, EmotionState.TRUSTED, "exchange", threshold=10),
    _TransitionRule(None, EmotionState.TENSE, "problem_detected"),
    _TransitionRule(EmotionState.TENSE, EmotionState.RELIEVED, "problem_resolved"),
]


class EmotionStateMachine:
    """
    Manages emotional state evolution in conversation.

    Supports two modes:
    - v1: config-dict constructor with keyword-based emotion detection
    - v2: no-arg constructor with event-driven state transitions
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize EmotionStateMachine.

        Args:
            config: Optional configuration dict. If None, uses v2 defaults.
        """
        if config is not None:
            # v1 path: config-dict constructor
            self._init_v1(config)
        else:
            # v2 path: no-arg constructor with defaults
            self._init_v2()

    def _init_v1(self, config: dict[str, Any]) -> None:
        """Initialize from v1 config dict."""
        self.current_state: str | EmotionState = config.get('initial_emotion', 'neutral')
        self.state_history: list[str | EmotionState] = [self.current_state]
        self.transition_rules: dict[tuple[str, str], float] = config.get(
            'transition_matrix',
            {
                ('neutral', 'happy'): 0.3,
                ('neutral', 'sad'): 0.1,
                ('neutral', 'confused'): 0.2,
                ('happy', 'neutral'): 0.4,
                ('sad', 'neutral'): 0.5,
                ('confused', 'neutral'): 0.6,
            }
        )
        self.emotion_inertia: float = config.get('emotion_inertia', 0.7)
        self.trigger_keywords: dict[str, list[str]] = config.get(
            'trigger_keywords',
            {
                'happy': ['great', 'wonderful', 'excellent', 'perfect', ':)'],
                'sad': ['sorry', 'terrible', 'awful', 'bad', ':('],
                'confused': ['what', 'huh', '?', 'confused'],
                'angry': ['angry', 'furious', 'outrage', '!!!'],
            }
        )
        self.exchange_count: int = config.get('exchange_count', 0)
        self.config: dict[str, Any] = config
        self._v2_transitions: list[_TransitionRule] = []
        self._v2_mode: bool = False

    def _init_v2(self) -> None:
        """Initialize with v2 defaults (event-driven state machine)."""
        self._v2_mode: bool = True
        self.current_state: EmotionState = EmotionState.FORMAL
        self.state_history: list[EmotionState] = [EmotionState.FORMAL]
        self.exchange_count: int = 0
        self._v2_transitions: list[_TransitionRule] = list(_DEFAULT_TRANSITIONS)
        # v1 compatibility attributes
        self.emotion_inertia: float = 0.7
        self.trigger_keywords: dict[str, list[str]] = {}
        self.transition_rules: dict[tuple[str, str], float] = {}
        self.config: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # v2 API
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> EmotionStateMachine:
        """
        Create EmotionStateMachine from a config dict (e.g. config["emotion"]).

        Parses initial_state and transitions (with wildcard expansion).
        """
        sm = cls.__new__(cls)
        sm._v2_mode = True

        initial_str = config.get("initial_state", "formal")
        try:
            sm.current_state = EmotionState(initial_str)
        except ValueError:
            sm.current_state = EmotionState.FORMAL

        sm.state_history = [sm.current_state]
        sm.exchange_count = 0
        sm.emotion_inertia = 0.7
        sm.trigger_keywords = {}
        sm.transition_rules = {}
        sm.config = config

        # Parse transitions
        sm._v2_transitions = []
        all_states = [EmotionState.FORMAL, EmotionState.WARMING, EmotionState.TRUSTED,
                      EmotionState.TENSE, EmotionState.RELIEVED]

        for t in config.get("transitions", []):
            from_raw = t.get("from", "*")
            to_raw = t.get("to", "formal")
            trigger = t.get("trigger", "")

            try:
                to_state = EmotionState(to_raw)
            except ValueError:
                continue

            # Parse threshold from trigger like "exchange_count >= 3"
            threshold = None
            event_name = trigger
            if ">=" in trigger and "exchange_count" in trigger:
                parts = trigger.split(">=")
                try:
                    threshold = int(parts[1].strip())
                except (ValueError, IndexError):
                    pass
                event_name = "exchange"

            # Map resolution_confirmed → problem_resolved for compatibility
            if event_name == "resolution_confirmed":
                event_name = "problem_resolved"

            if from_raw == "*":
                # Wildcard: expand to all states except target
                for s in all_states:
                    if s != to_state:
                        sm._v2_transitions.append(
                            _TransitionRule(s, to_state, event_name, threshold)
                        )
            else:
                try:
                    from_state = EmotionState(from_raw)
                except ValueError:
                    continue
                sm._v2_transitions.append(
                    _TransitionRule(from_state, to_state, event_name, threshold)
                )

        return sm

    def process_event(self, event: str) -> None:
        """
        Process a named event and potentially transition state.

        Supported events: "exchange", "problem_detected", "problem_resolved".
        Unknown events are silently ignored.
        """
        if event == "exchange":
            self.exchange_count += 1

        # Check transitions
        for rule in self._v2_transitions:
            if rule.trigger != event:
                continue
            if rule.from_state is not None and rule.from_state != self.current_state:
                continue
            if rule.threshold is not None and self.exchange_count < rule.threshold:
                continue
            # Transition
            self.current_state = rule.to_state
            if self.state_history[-1] != rule.to_state:
                self.state_history.append(rule.to_state)
            return

    def get_tone_modifier(self) -> dict[str, float]:
        """
        Get tone modifier dict for the current state.

        Returns:
            Dict with keys: formality, warmth, caution.
        """
        state = self.current_state
        if isinstance(state, EmotionState):
            return dict(_TONE_MODIFIERS.get(state, _TONE_MODIFIERS[EmotionState.NEUTRAL]))
        # v1 string state fallback
        try:
            es = EmotionState(state)
            return dict(_TONE_MODIFIERS.get(es, _TONE_MODIFIERS[EmotionState.NEUTRAL]))
        except ValueError:
            return dict(_TONE_MODIFIERS[EmotionState.NEUTRAL])

    # ------------------------------------------------------------------
    # v1 API (preserved for backward compatibility)
    # ------------------------------------------------------------------

    def update(self, user_message: str) -> None:
        """
        Update emotion state based on user message (v1 keyword detection).

        Args:
            user_message: The user input to analyze for emotion triggers.
        """
        detected_emotion = self._detect_emotion(user_message)
        if detected_emotion:
            self._transition_to(detected_emotion)

    def _detect_emotion(self, text: str) -> str | None:
        """Detect emotion triggers in text."""
        text_lower = text.lower()
        for emotion, keywords in self.trigger_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return emotion
        return None

    def _transition_to(self, target_emotion: str) -> None:
        """Transition to target emotion (with inertia)."""
        current = self.current_state
        current_str = current.value if isinstance(current, EmotionState) else current
        if current_str == target_emotion:
            return

        key = (current_str, target_emotion)
        prob = self.transition_rules.get(key, 0.2)
        adjusted_prob = prob * (1.0 - self.emotion_inertia)

        if random.random() < adjusted_prob:
            self.current_state = target_emotion
            self.state_history.append(target_emotion)

    def get_current_emotion(self) -> str:
        """Get current emotion state as string."""
        state = self.current_state
        return state.value if isinstance(state, EmotionState) else state

    def get_recommended_emotion(self, conversation_history: list[Any]) -> str | None:
        """
        Get recommended emotion bias for next response.

        Args:
            conversation_history: List of Message objects.

        Returns:
            Recommended emotion or None.
        """
        if not conversation_history:
            return None

        user_messages = [m for m in conversation_history if m.role == 'user']
        if not user_messages:
            return None

        last_user_msg = user_messages[-1].content
        detected = self._detect_emotion(last_user_msg)

        state = self.current_state
        state_str = state.value if isinstance(state, EmotionState) else state
        return detected if detected else state_str

    def calculate_recovery_time(self, emotion: str) -> float:
        """Calculate time to naturally recover from an emotion."""
        recovery_times: dict[str, float] = {
            'neutral': 0, 'happy': 3, 'sad': 8, 'angry': 5, 'confused': 4,
        }
        return recovery_times.get(emotion, 2)

    def add_transition_rule(self, from_state: str, to_state: str, probability: float) -> None:
        """Add or update a transition rule."""
        self.transition_rules[(from_state, to_state)] = probability

    def reset(self) -> None:
        """Reset emotion state to initial."""
        if getattr(self, '_v2_mode', False):
            initial = EmotionState.FORMAL
            # Respect from_config initial_state
            if self.config and 'initial_state' in self.config:
                try:
                    initial = EmotionState(self.config['initial_state'])
                except ValueError:
                    pass
            self.current_state = initial
            self.state_history = [initial]
            self.exchange_count = 0
        else:
            self.current_state = self.config.get('initial_emotion', 'neutral')
            self.state_history = [self.current_state]

    def get_state_sequence(self) -> list[str | EmotionState]:
        """Get full emotional state history."""
        return self.state_history.copy()

    def apply_contagion(self, peer_emotion: str, contagion_strength: float = 0.3) -> None:
        """Apply emotional contagion from external source."""
        if random.random() < contagion_strength:
            self._transition_to(peer_emotion)

    def get_emotion_vector(self) -> dict[str, float]:
        """Get emotion state as probability vector."""
        state = self.current_state
        state_str = state.value if isinstance(state, EmotionState) else state

        vectors: dict[str, dict[str, float]] = {
            'neutral': {'happy': 0.2, 'sad': 0.1, 'angry': 0.05, 'confused': 0.15, 'neutral': 0.5},
            'happy':   {'happy': 0.7, 'sad': 0.05, 'angry': 0.0, 'confused': 0.1, 'neutral': 0.15},
            'sad':     {'happy': 0.1, 'sad': 0.6, 'angry': 0.1, 'confused': 0.1, 'neutral': 0.1},
            'angry':   {'happy': 0.05, 'sad': 0.2, 'angry': 0.65, 'confused': 0.0, 'neutral': 0.1},
            'confused': {'happy': 0.1, 'sad': 0.1, 'angry': 0.0, 'confused': 0.7, 'neutral': 0.1},
        }
        return vectors.get(state_str, {'happy': 0.2, 'sad': 0.2, 'angry': 0.1, 'confused': 0.2, 'neutral': 0.3})
