"""
TimingController — Response delay simulation engine.

This module simulates human response delays to avoid the "too-instant"
perception of AI. It applies delays based on:
- Message complexity/length
- Emotional state
- Platform context
- Stochastic factors (variance)

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Platform(Enum):
    """Communication platforms for timing profiles."""
    CHAT = "chat"
    EMAIL = "email"
    VOICE = "voice"
    FORUM = "forum"


@dataclass
class TimingProfile:
    """Timing profile for a specific platform."""
    min_seconds: float = 0.3
    max_seconds: float = 5.0
    typing_speed_wpm: int = 60


@dataclass
class TimingConfig:
    """Configuration for timing delays."""
    base_delay_sec: float = 0.5
    per_char_sec: float = 0.01
    thinking_delay_sec: float = 1.0
    emotion_multipliers: dict[str, float] = field(default_factory=lambda: {
        'neutral': 1.0,
        'confused': 2.0,
        'happy': 0.8,
        'angry': 0.6,
        'sad': 1.5,
    })


class TimingController:
    """
    Manages response delay simulation.

    This controller calculates realistic delays that account for message
    complexity, emotional state, and platform context.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize TimingController.

        Args:
            config: Configuration dict with timing parameters.
        """
        self.base_delay: float = config.get('base_delay_sec', 0.5)
        self.per_char_delay: float = config.get('per_char_sec', 0.01)
        self.thinking_delay: float = config.get('thinking_delay_sec', 1.0)
        self.emotion_multipliers: dict[str, float] = config.get(
            'emotion_multipliers',
            {
                'neutral': 1.0,
                'confused': 2.0,
                'happy': 0.8,
                'angry': 0.6,
                'sad': 1.5,
            }
        )
        self.profiles: dict[Platform, TimingProfile] = {
            Platform.CHAT: TimingProfile(
                min_seconds=config.get('chat_min_seconds', 0.3),
                max_seconds=config.get('chat_max_seconds', 5.0),
            ),
            Platform.EMAIL: TimingProfile(min_seconds=5.0, max_seconds=60.0),
            Platform.VOICE: TimingProfile(min_seconds=0.1, max_seconds=2.0),
            Platform.FORUM: TimingProfile(min_seconds=10.0, max_seconds=120.0),
        }

    def calculate_delay(self, user_message: str, response: str, turn_count: int) -> float:
        """
        Calculate delay for a given response.

        Factors:
        - Response length (base + per-char)
        - Turn count (earlier turns get slightly more delay)
        - Random variance to avoid bot-like regularity

        Args:
            user_message: The user input.
            response: The persona response.
            turn_count: Current conversation turn.

        Returns:
            Delay in seconds (float, >= 0).
        """
        # Base delay
        length_delay = self.base_delay + (len(response) * self.per_char_delay)

        # Turn-based adjustment (first turn gets longer delay)
        turn_factor = 1.0 + (1.0 / max(1, turn_count))

        # Random variance (±20%)
        variance = random.uniform(0.8, 1.2)

        final_delay = length_delay * turn_factor * variance

        # Cap at reasonable limits
        return max(0.2, min(final_delay, 15.0))

    def apply_emotion_multiplier(self, base_delay: float, emotion: str | None) -> float:
        """
        Apply emotion-based multiplier to delay.

        Args:
            base_delay: Initial delay value.
            emotion: Current emotional state (or None for neutral).

        Returns:
            Adjusted delay in seconds.
        """
        if emotion is None:
            emotion = 'neutral'

        multiplier = self.emotion_multipliers.get(emotion, 1.0)
        return base_delay * multiplier

    def add_thinking_pause(self, response: str) -> str:
        """
        Optionally prepend thinking pause indicators.

        Example: "...[thinks]... Here's my response"

        Args:
            response: Original response text.

        Returns:
            Response with optional thinking indicators.
        """
        if random.random() < 0.15:  # 15% chance
            return f"[thinking...] {response}"
        return response

    def get_typing_speed_wpm(self) -> int:
        """
        Get simulated typing speed in words per minute.

        Returns:
            Typing speed (wpm) for this persona.
        """
        # Average human types 40 wpm, range 20-80
        return random.randint(35, 85)

    def estimate_thinking_time(self, question_complexity: str) -> float:
        """
        Estimate thinking time based on question complexity.

        Args:
            question_complexity: One of 'simple', 'moderate', 'complex'.

        Returns:
            Estimated thinking time in seconds.
        """
        times: dict[str, float] = {
            'simple': 0.5,
            'moderate': 2.0,
            'complex': 4.0,
        }
        return times.get(question_complexity, 1.0)

    def humanize_timestamp(self, raw_timestamp: float) -> float:
        """
        Add stochastic variation to make timestamps less regular.

        Args:
            raw_timestamp: Original timestamp.

        Returns:
            Humanized timestamp with noise.
        """
        noise = random.gauss(0, 0.1)  # Gaussian noise
        return max(0, raw_timestamp + noise)
