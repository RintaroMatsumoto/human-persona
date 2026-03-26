"""
EmotionStateMachine — Affective state tracking and evolution.

This module tracks emotional state transitions based on conversation patterns.
States evolve realistically with inertia, recovery time, and contagion effects.

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


class EmotionState(Enum):
    """Enumeration of emotion states."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    CONFUSED = "confused"


@dataclass
class EmotionTransition:
    """Single emotion state transition."""
    from_state: str
    to_state: str
    trigger: str
    probability: float


class EmotionStateMachine:
    """
    Manages emotional state evolution in conversation.

    Tracks state transitions with realistic inertia, recovery times,
    and emotional contagion from user inputs.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize EmotionStateMachine.

        Args:
            config: Configuration with emotion weights and transition rules.
        """
        self.current_state: str = config.get('initial_emotion', 'neutral')
        self.state_history: list[str] = [self.current_state]
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

    def update(self, user_message: str) -> None:
        """
        Update emotion state based on user message.

        Args:
            user_message: The user input to analyze for emotion triggers.
        """
        detected_emotion = self._detect_emotion(user_message)
        if detected_emotion:
            self._transition_to(detected_emotion)

    def _detect_emotion(self, text: str) -> str | None:
        """
        Detect emotion triggers in text.

        Args:
            text: Text to analyze.

        Returns:
            Detected emotion or None.
        """
        text_lower = text.lower()

        for emotion, keywords in self.trigger_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return emotion

        return None

    def _transition_to(self, target_emotion: str) -> None:
        """
        Transition to target emotion (with inertia).

        Args:
            target_emotion: Target emotion state.
        """
        current = self.current_state
        if current == target_emotion:
            return

        # Check transition rule
        key = (current, target_emotion)
        prob = self.transition_rules.get(key, 0.2)

        # Apply inertia (less likely to change)
        adjusted_prob = prob * (1.0 - self.emotion_inertia)

        import random
        if random.random() < adjusted_prob:
            self.current_state = target_emotion
            self.state_history.append(target_emotion)

    def get_current_emotion(self) -> str:
        """
        Get current emotion state.

        Returns:
            Current emotion string.
        """
        return self.current_state

    def get_recommended_emotion(self, conversation_history: list[Any]) -> str | None:
        """
        Get recommended emotion bias for next response.

        Based on conversation history, may recommend a specific emotion
        to make response feel more contextually appropriate.

        Args:
            conversation_history: List of Message objects in conversation.

        Returns:
            Recommended emotion or None for neutral.
        """
        if not conversation_history:
            return None

        # Look at last user message
        user_messages = [m for m in conversation_history if m.role == 'user']
        if not user_messages:
            return None

        last_user_msg = user_messages[-1].content
        detected = self._detect_emotion(last_user_msg)

        return detected if detected else self.current_state

    def calculate_recovery_time(self, emotion: str) -> float:
        """
        Calculate time to naturally recover from an emotion.

        Args:
            emotion: Emotion state.

        Returns:
            Recovery time in turns.
        """
        recovery_times: dict[str, float] = {
            'neutral': 0,
            'happy': 3,
            'sad': 8,
            'angry': 5,
            'confused': 4,
        }
        return recovery_times.get(emotion, 2)

    def add_transition_rule(self, from_state: str, to_state: str, probability: float) -> None:
        """
        Add or update a transition rule.

        Args:
            from_state: Source emotion state.
            to_state: Target emotion state.
            probability: Transition probability (0.0 to 1.0).
        """
        self.transition_rules[(from_state, to_state)] = probability

    def reset(self) -> None:
        """Reset emotion state to initial."""
        self.current_state = self.config.get('initial_emotion', 'neutral')
        self.state_history = [self.current_state]

    def get_state_sequence(self) -> list[str]:
        """
        Get full emotional state history.

        Returns:
            List of emotion states in chronological order.
        """
        return self.state_history.copy()

    def apply_contagion(self, peer_emotion: str, contagion_strength: float = 0.3) -> None:
        """
        Apply emotional contagion from external source.

        Simulates how emotions can spread from one persona to another
        in multi-agent scenarios.

        Args:
            peer_emotion: Emotion state of external agent.
            contagion_strength: Strength of contagion effect (0.0 to 1.0).
        """
        import random
        if random.random() < contagion_strength:
            self._transition_to(peer_emotion)

    def get_emotion_vector(self) -> dict[str, float]:
        """
        Get emotion state as probability vector.

        Returns:
            Dict mapping emotions to activation levels.
        """
        if self.current_state == 'neutral':
            return {
                'happy': 0.2,
                'sad': 0.1,
                'angry': 0.05,
                'confused': 0.15,
                'neutral': 0.5,
            }
        elif self.current_state == 'happy':
            return {
                'happy': 0.7,
                'sad': 0.05,
                'angry': 0.0,
                'confused': 0.1,
                'neutral': 0.15,
            }
        elif self.current_state == 'sad':
            return {
                'happy': 0.1,
                'sad': 0.6,
                'angry': 0.1,
                'confused': 0.1,
                'neutral': 0.1,
            }
        elif self.current_state == 'angry':
            return {
                'happy': 0.05,
                'sad': 0.2,
                'angry': 0.65,
                'confused': 0.0,
                'neutral': 0.1,
            }
        elif self.current_state == 'confused':
            return {
                'happy': 0.1,
                'sad': 0.1,
                'angry': 0.0,
                'confused': 0.7,
                'neutral': 0.1,
            }
        else:
            return {
                'happy': 0.2,
                'sad': 0.2,
                'angry': 0.1,
                'confused': 0.2,
                'neutral': 0.3,
            }
