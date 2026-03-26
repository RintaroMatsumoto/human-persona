"""
InnerOuterBridge — Bridge between inner shell and outer shell modules.

This module connects the inner shell (FinitudeEngine, IncompletenessModel,
AutonomousQuestioner, MemoryHierarchy, MutualRecognition, SleepCycle) with
the outer shell (TimingController, StyleVariator, EmotionStateMachine,
ContextReferencer, EscalationDetector).

The bridge accepts a modulation dict from inner shell state and applies
adjustments to outer shell controllers, while preserving original values
for restoration.

Modulation keys:
    style_openness: Multiplier for StyleVariator.uncertainty_rate
    emotion_amplitude: Multiplier for EmotionStateMachine.exchange_count
    timing_exploration: Multiplier for timing profile range expansion
    context_depth: Multiplier for ContextReferencer.max_history
    emotion_volatility: Reserved hook for future emotion volatility control
    style_mimicry: Multiplier for StylePattern(CONFIRMATION).weight
    emotion_curiosity: Additive factor for StylePattern(UNCERTAIN).weight

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .timing_controller import TimingController, Platform
from .style_variator import StyleVariator, StyleType
from .emotion_state_machine import EmotionStateMachine
from .context_referencer import ContextReferencer


@dataclass
class ControllerSnapshot:
    """Snapshot of original controller values before modulation."""
    style_uncertainty_rate: float = 0.0
    style_pattern_weights: dict[str, float] = field(default_factory=dict)
    emotion_exchange_count: int = 0
    emotion_inertia: float = 0.7
    timing_min_seconds: float = 0.3
    timing_max_seconds: float = 5.0
    context_max_history: int = 10


class InnerOuterBridge:
    """
    Bridge between inner and outer shell architectures.

    Accepts modulation dicts from inner shell and applies them to
    outer shell controllers, preserving originals for reversal.
    """

    def __init__(
        self,
        timing: TimingController,
        style: StyleVariator,
        emotion: EmotionStateMachine,
        context: ContextReferencer,
    ) -> None:
        self.timing = timing
        self.style = style
        self.emotion = emotion
        self.context = context
        self._original_snapshot: Optional[ControllerSnapshot] = None
        self._current_modulation: dict[str, float] = {}

    def is_modulated(self) -> bool:
        """Return True if modulation is currently applied."""
        return self._original_snapshot is not None

    def apply_modulation(self, modulation: dict[str, float]) -> None:
        """Apply inner shell modulation to outer shell controllers.

        If already modulated, restores to original first, then applies new.

        Args:
            modulation: Dict mapping modulation keys to float values.
        """
        if not modulation:
            return

        # If already modulated, restore first then re-apply from original
        if self._original_snapshot is not None:
            self._restore_from_snapshot(self._original_snapshot)

        # Take snapshot of current (original) values
        self._original_snapshot = self._take_snapshot()
        self._current_modulation = dict(modulation)

        # Apply each modulation
        if "style_openness" in modulation:
            self.style.uncertainty_rate *= modulation["style_openness"]

        if "emotion_amplitude" in modulation:
            self.emotion.exchange_count = int(
                self.emotion.exchange_count * modulation["emotion_amplitude"]
            )

        if "timing_exploration" in modulation:
            factor = modulation["timing_exploration"]
            profile = self.timing.profiles[Platform.CHAT]
            midpoint = (profile.min_seconds + profile.max_seconds) / 2.0
            half_range = (profile.max_seconds - profile.min_seconds) / 2.0
            new_half = half_range * factor
            profile.min_seconds = max(0.0, midpoint - new_half)
            profile.max_seconds = midpoint + new_half

        if "context_depth" in modulation:
            self.context.max_history = max(
                1, int(self.context.max_history * modulation["context_depth"])
            )

        if "style_mimicry" in modulation:
            if StyleType.CONFIRMATION in self.style.patterns:
                self.style.patterns[StyleType.CONFIRMATION].weight *= (
                    modulation["style_mimicry"]
                )

        if "emotion_curiosity" in modulation:
            if StyleType.UNCERTAIN in self.style.patterns:
                self.style.patterns[StyleType.UNCERTAIN].weight *= (
                    1.0 + modulation["emotion_curiosity"]
                )

        # emotion_volatility: accepted but currently a design hook
        # No-op for now, but presence doesn't cause errors.

    def restore_original_values(self) -> None:
        """Restore all controllers to original values.

        Raises:
            RuntimeError: If no modulation has been applied.
        """
        if self._original_snapshot is None:
            raise RuntimeError(
                "Cannot restore: no modulation has been applied."
            )
        self._restore_from_snapshot(self._original_snapshot)
        self._original_snapshot = None
        self._current_modulation = {}

    def reset_to_original(self) -> None:
        """Reset bridge state completely (restore + clear snapshot)."""
        if self._original_snapshot is not None:
            self._restore_from_snapshot(self._original_snapshot)
        self._original_snapshot = None
        self._current_modulation = {}

    def get_current_modulation(self) -> dict[str, float]:
        """Return the currently applied modulation dict."""
        return dict(self._current_modulation)

    def _take_snapshot(self) -> ControllerSnapshot:
        """Capture current controller state."""
        pattern_weights = {}
        for st, pat in self.style.patterns.items():
            pattern_weights[st.value] = pat.weight

        profile = self.timing.profiles[Platform.CHAT]
        return ControllerSnapshot(
            style_uncertainty_rate=self.style.uncertainty_rate,
            style_pattern_weights=pattern_weights,
            emotion_exchange_count=self.emotion.exchange_count,
            emotion_inertia=self.emotion.emotion_inertia,
            timing_min_seconds=profile.min_seconds,
            timing_max_seconds=profile.max_seconds,
            context_max_history=self.context.max_history,
        )

    def _restore_from_snapshot(self, snap: ControllerSnapshot) -> None:
        """Restore controller values from snapshot."""
        self.style.uncertainty_rate = snap.style_uncertainty_rate
        for st, pat in self.style.patterns.items():
            if st.value in snap.style_pattern_weights:
                pat.weight = snap.style_pattern_weights[st.value]

        self.emotion.exchange_count = snap.emotion_exchange_count
        self.emotion.emotion_inertia = snap.emotion_inertia

        profile = self.timing.profiles[Platform.CHAT]
        profile.min_seconds = snap.timing_min_seconds
        profile.max_seconds = snap.timing_max_seconds

        self.context.max_history = snap.context_max_history
