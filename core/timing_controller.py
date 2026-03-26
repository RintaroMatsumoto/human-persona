"""
TimingController — Response delay simulation engine.

This module simulates human response delays to avoid the "too-instant"
perception of AI. It applies delays based on:
- Message complexity/length
- Emotional state
- Platform context
- Stochastic factors (variance)

v2 API adds: frozen TimingProfile with validation, DEFAULT_PROFILES,
no-arg constructor, from_config(), is_active_hours(), should_queue(),
single-arg calculate_delay(platform).

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import Any


class Platform(Enum):
    """Communication platforms for timing profiles."""
    CHAT = "chat"
    CROWDSOURCING = "crowdsourcing"
    EMAIL = "email"
    VOICE = "voice"
    FORUM = "forum"


@dataclass(frozen=True)
class TimingProfile:
    """Timing profile for a specific platform."""
    min_seconds: float = 0.3
    max_seconds: float = 5.0
    typing_speed_wpm: int = 60

    def __post_init__(self) -> None:
        if self.min_seconds < 0:
            raise ValueError(f"min_seconds must be >= 0, got {self.min_seconds}")
        if self.max_seconds < 0:
            raise ValueError(f"max_seconds must be >= 0, got {self.max_seconds}")
        if self.min_seconds > self.max_seconds:
            raise ValueError(
                f"min_seconds ({self.min_seconds}) must be <= max_seconds ({self.max_seconds})"
            )


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


# ---------------------------------------------------------------------------
# Module-level default profiles
# ---------------------------------------------------------------------------

DEFAULT_PROFILES: dict[Platform, TimingProfile] = {
    Platform.CHAT: TimingProfile(min_seconds=5, max_seconds=45),
    Platform.CROWDSOURCING: TimingProfile(min_seconds=120, max_seconds=900),
    Platform.EMAIL: TimingProfile(min_seconds=1800, max_seconds=14400),
    Platform.VOICE: TimingProfile(min_seconds=10, max_seconds=60),
    Platform.FORUM: TimingProfile(min_seconds=300, max_seconds=3600),
}


class TimingController:
    """
    Manages response delay simulation.

    Supports two modes:
    - v1: config-dict constructor with calculate_delay(user_message, response, turn_count)
    - v2: no-arg / from_config() with calculate_delay(platform), is_active_hours(), should_queue()
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        *,
        profiles: dict[Platform, TimingProfile] | None = None,
        active_start: time | None = None,
        active_end: time | None = None,
        night_queue: bool = False,
    ) -> None:
        """
        Initialize TimingController.

        Args:
            config: Optional v1 configuration dict.
            profiles: Optional custom profiles dict (v2).
            active_start: Start of active hours (v2).
            active_end: End of active hours (v2).
            night_queue: Whether to queue messages outside active hours.
        """
        if config is not None:
            self._init_v1(config)
        else:
            self._init_v2(profiles, active_start, active_end, night_queue)

    def _init_v1(self, config: dict[str, Any]) -> None:
        """Initialize from v1 config dict."""
        self.base_delay: float = config.get('base_delay_sec', 0.5)
        self.per_char_delay: float = config.get('per_char_sec', 0.01)
        self.thinking_delay: float = config.get('thinking_delay_sec', 1.0)
        self.emotion_multipliers: dict[str, float] = config.get(
            'emotion_multipliers',
            {'neutral': 1.0, 'confused': 2.0, 'happy': 0.8, 'angry': 0.6, 'sad': 1.5}
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
        self.active_start: time | None = None
        self.active_end: time | None = None
        self.night_queue: bool = False

    def _init_v2(
        self,
        profiles: dict[Platform, TimingProfile] | None,
        active_start: time | None,
        active_end: time | None,
        night_queue: bool,
    ) -> None:
        """Initialize v2 (no-arg or keyword-arg)."""
        self.profiles: dict[Platform, TimingProfile] = dict(profiles) if profiles else dict(DEFAULT_PROFILES)
        self.active_start: time | None = active_start
        self.active_end: time | None = active_end
        self.night_queue: bool = night_queue
        # v1 compatibility defaults
        self.base_delay: float = 0.5
        self.per_char_delay: float = 0.01
        self.thinking_delay: float = 1.0
        self.emotion_multipliers: dict[str, float] = {
            'neutral': 1.0, 'confused': 2.0, 'happy': 0.8, 'angry': 0.6, 'sad': 1.5
        }

    # ------------------------------------------------------------------
    # v2 API
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, timing_config: dict[str, Any]) -> TimingController:
        """
        Create TimingController from a timing config section.

        Args:
            timing_config: Dict with platform_timing, active_hours, night_queue.
        """
        pt = timing_config.get("platform_timing", {})

        profiles: dict[Platform, TimingProfile] = {}

        # CHAT
        chat_cfg = pt.get("chat", {})
        if chat_cfg:
            profiles[Platform.CHAT] = TimingProfile(
                min_seconds=chat_cfg.get("min_sec", 5),
                max_seconds=chat_cfg.get("max_sec", 45),
            )

        # CROWDSOURCING (may be "crowdsourcing_message" in config)
        crowd_cfg = pt.get("crowdsourcing_message", pt.get("crowdsourcing", {}))
        if crowd_cfg:
            profiles[Platform.CROWDSOURCING] = TimingProfile(
                min_seconds=crowd_cfg.get("min_sec", 120),
                max_seconds=crowd_cfg.get("max_sec", 900),
            )

        # EMAIL (uses hours in config, convert to seconds)
        email_cfg = pt.get("email", {})
        if email_cfg:
            min_h = email_cfg.get("min_hour", 0.5)
            max_h = email_cfg.get("max_hour", 12)
            profiles[Platform.EMAIL] = TimingProfile(
                min_seconds=int(min_h * 3600),
                max_seconds=int(max_h * 3600),
            )

        # Active hours
        active_start: time | None = None
        active_end: time | None = None
        night_queue = pt.get("night_queue", timing_config.get("night_queue", False))

        active_hours_str = pt.get("active_hours", "")
        if active_hours_str and "-" in active_hours_str:
            parts = active_hours_str.split("-")
            try:
                start_parts = parts[0].strip().split(":")
                end_parts = parts[1].strip().split(":")
                active_start = time(int(start_parts[0]), int(start_parts[1]))
                active_end = time(int(end_parts[0]), int(end_parts[1]))
            except (ValueError, IndexError):
                pass

        # Fill in defaults for any platforms not in config
        for platform, default_profile in DEFAULT_PROFILES.items():
            if platform not in profiles:
                profiles[platform] = default_profile

        return cls(profiles=profiles, active_start=active_start,
                   active_end=active_end, night_queue=night_queue)

    def is_active_hours(self, t: time) -> bool:
        """
        Check if a given time is within active hours.

        Args:
            t: Time to check.

        Returns:
            True if within active hours (or if no active hours configured).
        """
        if self.active_start is None or self.active_end is None:
            return True
        return self.active_start <= t <= self.active_end

    def should_queue(self, t: time) -> bool:
        """
        Check if a message at this time should be queued.

        Args:
            t: Time to check.

        Returns:
            True if night_queue is enabled and time is outside active hours.
        """
        if not self.night_queue:
            return False
        return not self.is_active_hours(t)

    def calculate_delay(self, platform_or_message: Platform | str, response: str | None = None, turn_count: int | None = None) -> float:
        """
        Calculate delay. Supports both v1 and v2 signatures.

        v2: calculate_delay(Platform) → float (truncated normal in profile range)
        v1: calculate_delay(user_message, response, turn_count) → float
        """
        if isinstance(platform_or_message, Platform):
            return self._calculate_delay_v2(platform_or_message)
        # v1 path
        user_message = platform_or_message
        if response is None:
            response = ""
        if turn_count is None:
            turn_count = 1
        return self._calculate_delay_v1(user_message, response, turn_count)

    def _calculate_delay_v2(self, platform: Platform) -> float:
        """Calculate delay for a platform using truncated normal distribution."""
        profile = self.profiles.get(platform)
        if profile is None:
            # Fallback to CHAT default
            profile = self.profiles.get(Platform.CHAT, DEFAULT_PROFILES[Platform.CHAT])

        mean = (profile.min_seconds + profile.max_seconds) / 2
        std = (profile.max_seconds - profile.min_seconds) / 4  # ~95% within range

        if std <= 0:
            return profile.min_seconds

        delay = random.gauss(mean, std)
        return max(profile.min_seconds, min(delay, profile.max_seconds))

    def _calculate_delay_v1(self, user_message: str, response: str, turn_count: int) -> float:
        """v1 delay calculation."""
        length_delay = self.base_delay + (len(response) * self.per_char_delay)
        turn_factor = 1.0 + (1.0 / max(1, turn_count))
        variance = random.uniform(0.8, 1.2)
        final_delay = length_delay * turn_factor * variance
        return max(0.2, min(final_delay, 15.0))

    # ------------------------------------------------------------------
    # v1 API (preserved)
    # ------------------------------------------------------------------

    def apply_emotion_multiplier(self, base_delay: float, emotion: str | None) -> float:
        """Apply emotion-based multiplier to delay."""
        if emotion is None:
            emotion = 'neutral'
        multiplier = self.emotion_multipliers.get(emotion, 1.0)
        return base_delay * multiplier

    def add_thinking_pause(self, response: str) -> str:
        """Optionally prepend thinking pause indicators."""
        if random.random() < 0.15:
            return f"[thinking...] {response}"
        return response

    def get_typing_speed_wpm(self) -> int:
        """Get simulated typing speed in words per minute."""
        return random.randint(35, 85)

    def estimate_thinking_time(self, question_complexity: str) -> float:
        """Estimate thinking time based on question complexity."""
        times: dict[str, float] = {'simple': 0.5, 'moderate': 2.0, 'complex': 4.0}
        return times.get(question_complexity, 1.0)

    def humanize_timestamp(self, raw_timestamp: float) -> float:
        """Add stochastic variation to make timestamps less regular."""
        noise = random.gauss(0, 0.1)
        return max(0, raw_timestamp + noise)
