"""Inner→Outer shell bridge: Applying inner shell modulation to outer shell modules.

This module bridges the inner shell (FinitudeEngine, IncompletenessModel, AutonomousQuestioner)
and outer shell (TimingController, StyleVariator, EmotionStateMachine, ContextReferencer).

The inner shell generates modulation values (e.g., {"timing_exploration": 1.5}) that
adjust outer shell parameters in real-time. The bridge applies these modulations while
preserving original values for restoration (testing, reversion).

Usage:
    from core.inner_outer_bridge import InnerOuterBridge
    from core.timing_controller import TimingController
    from core.style_variator import StyleVariator
    from core.emotion_state_machine import EmotionStateMachine
    from core.context_referencer import ContextReferencer
    
    timing = TimingController()
    style = StyleVariator()
    emotion = EmotionStateMachine()
    context = ContextReferencer()
    
    bridge = InnerOuterBridge(timing, style, emotion, context)
    
    # Apply modulation from inner shell
    modulation = {"timing_exploration": 1.5, "style_openness": 1.3}
    bridge.apply_modulation(modulation)
    
    # Later, restore original values
    bridge.restore_original_values()

Modulation mapping:
    style_openness        → StyleVariator.uncertainty_rate multiplier
    emotion_amplitude     → EmotionStateMachine tone_modifier amplification
    timing_exploration    → TimingController delay multiplier
    context_depth         → ContextReferencer.max_history adjustment
    emotion_volatility    → EmotionStateMachine transition sensitivity
    style_mimicry         → StyleVariator pattern weight adjustment
    emotion_curiosity     → EmotionStateMachine curiosity bias

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
class ModulationSnapshot:
    """Snapshot of outer shell state before modulation."""
    
    # TimingController
    timing_profiles: dict[Platform, Any]
    timing_night_queue: bool
    
    # StyleVariator
    style_uncertainty_rate: float
    style_patterns: dict[StyleType, Any]
    
    # EmotionStateMachine
    emotion_current_state: Any
    emotion_exchange_count: int
    
    # ContextReferencer
    context_max_history: int


class InnerOuterBridge:
    """Bridge applying inner shell modulation to outer shell modules.
    
    Attributes:
        timing_controller: TimingController instance
        style_variator: StyleVariator instance
        emotion_state_machine: EmotionStateMachine instance
        context_referencer: ContextReferencer instance
        _original_snapshot: Saved state for restoration
        _is_modulated: Whether modulation is currently applied
    """
    
    def __init__(
        self,
        timing_controller: TimingController,
        style_variator: StyleVariator,
        emotion_state_machine: EmotionStateMachine,
        context_referencer: ContextReferencer,
    ) -> None:
        """Initialize the bridge with outer shell module instances.
        
        Args:
            timing_controller: Timing controller instance
            style_variator: Style variator instance
            emotion_state_machine: Emotion state machine instance
            context_referencer: Context referencer instance
        """
        self.timing_controller = timing_controller
        self.style_variator = style_variator
        self.emotion_state_machine = emotion_state_machine
        self.context_referencer = context_referencer
        
        self._original_snapshot: Optional[ModulationSnapshot] = None
        self._is_modulated = False
        self._current_modulation: dict[str, float] = {}
    
    def save_original_state(self) -> None:
        """Save current outer shell state before applying modulation."""
        self._original_snapshot = ModulationSnapshot(
            # TimingController state
            timing_profiles={
                platform: profile
                for platform, profile in self.timing_controller.profiles.items()
            },
            timing_night_queue=self.timing_controller.night_queue,
            
            # StyleVariator state
            style_uncertainty_rate=self.style_variator.uncertainty_rate,
            style_patterns={
                style_type: pattern
                for style_type, pattern in self.style_variator.patterns.items()
            },
            
            # EmotionStateMachine state
            emotion_current_state=self.emotion_state_machine.current_state,
            emotion_exchange_count=self.emotion_state_machine.exchange_count,
            
            # ContextReferencer state
            context_max_history=self.context_referencer.max_history,
        )
    
    def apply_modulation(self, modulation: dict[str, float]) -> None:
        """Apply inner shell modulation values to outer shell modules.
        
        Args:
            modulation: Dictionary of modulation keys and values
                        (e.g., {"timing_exploration": 1.5})
        """
        # Save original state if not already saved
        if not self._is_modulated:
            self.save_original_state()
        
        self._current_modulation = dict(modulation)
        
        # Apply style_openness → StyleVariator.uncertainty_rate
        if "style_openness" in modulation:
            openness = modulation["style_openness"]
            # openness 0.5 → uncertainty_rate *= 0.5
            # openness 1.3 → uncertainty_rate *= 1.3
            base_rate = self.style_variator.uncertainty_rate
            if self._original_snapshot:
                base_rate = self._original_snapshot.style_uncertainty_rate
            self.style_variator.uncertainty_rate = base_rate * openness
        
        # Apply emotion_amplitude → EmotionStateMachine (scale emotion effects)
        # Higher amplitude = deeper emotional responses
        # This is tracked by exchange_count acceleration
        if "emotion_amplitude" in modulation:
            amplitude = modulation["emotion_amplitude"]
            # Accelerate emotional development by scaling exchange_count
            # amplitude 1.3 → emotions deepen 1.3x faster
            original_count = self.emotion_state_machine.exchange_count
            if self._original_snapshot:
                original_count = self._original_snapshot.emotion_exchange_count
            self.emotion_state_machine.exchange_count = int(original_count * amplitude)
        
        # Apply timing_exploration → TimingController delay multiplier
        if "timing_exploration" in modulation:
            exploration = modulation["timing_exploration"]
            # Higher exploration = more variance in delays
            # We scale the spread of the distribution
            for platform in self.timing_controller.profiles:
                profile = self.timing_controller.profiles[platform]
                # Scale the range by exploration factor
                min_s = profile.min_seconds
                max_s = profile.max_seconds
                if self._original_snapshot:
                    orig_profile = self._original_snapshot.timing_profiles.get(platform, profile)
                    min_s = orig_profile.min_seconds
                    max_s = orig_profile.max_seconds
                
                midpoint = (min_s + max_s) / 2
                original_range = max_s - min_s
                new_range = original_range * exploration
                new_min = max(0, midpoint - new_range / 2)
                new_max = midpoint + new_range / 2
                
                from .timing_controller import TimingProfile
                self.timing_controller.profiles[platform] = TimingProfile(
                    min_seconds=new_min,
                    max_seconds=new_max,
                )
        
        # Apply context_depth → ContextReferencer.max_history
        if "context_depth" in modulation:
            depth = modulation["context_depth"]
            base_history = self.context_referencer.max_history
            if self._original_snapshot:
                base_history = self._original_snapshot.context_max_history
            self.context_referencer.max_history = max(1, int(base_history * depth))
        
        # Apply emotion_volatility → EmotionStateMachine state
        # Higher volatility = more sensitive to events, faster transitions
        # For now, we track this conceptually but actual transitions are
        # determined by the transition table in the EmotionStateMachine
        if "emotion_volatility" in modulation:
            volatility = modulation["emotion_volatility"]
            # Could accelerate exchange_count further for high volatility
            # volatility > 1.0 means more reactive, < 1.0 means more stable
            # This is a design hook for future enhancement
            pass
        
        # Apply style_mimicry → StyleVariator pattern weight adjustment
        if "style_mimicry" in modulation:
            mimicry = modulation["style_mimicry"]
            # Increase weight of existing patterns by mimicry factor
            for style_type in self.style_variator.patterns:
                pattern = self.style_variator.patterns[style_type]
                base_weight = pattern.weight
                if self._original_snapshot and style_type in self._original_snapshot.style_patterns:
                    base_weight = self._original_snapshot.style_patterns[style_type].weight
                pattern.weight = base_weight * mimicry
        
        # Apply emotion_curiosity → bias toward UNCERTAIN style type
        if "emotion_curiosity" in modulation:
            curiosity = modulation["emotion_curiosity"]
            # Higher curiosity → higher weight for UNCERTAIN style
            if StyleType.UNCERTAIN in self.style_variator.patterns:
                pattern = self.style_variator.patterns[StyleType.UNCERTAIN]
                base_weight = pattern.weight
                if self._original_snapshot and StyleType.UNCERTAIN in self._original_snapshot.style_patterns:
                    base_weight = self._original_snapshot.style_patterns[StyleType.UNCERTAIN].weight
                pattern.weight = base_weight * (1.0 + curiosity)
        
        self._is_modulated = True
    
    def restore_original_values(self) -> None:
        """Restore outer shell modules to original state.
        
        Raises:
            RuntimeError: If no original state was saved
        """
        if self._original_snapshot is None:
            raise RuntimeError("No original state saved. Call apply_modulation first.")
        
        snapshot = self._original_snapshot
        
        # Restore TimingController
        self.timing_controller.profiles = dict(snapshot.timing_profiles)
        self.timing_controller.night_queue = snapshot.timing_night_queue
        
        # Restore StyleVariator
        self.style_variator.uncertainty_rate = snapshot.style_uncertainty_rate
        self.style_variator.patterns = dict(snapshot.style_patterns)
        
        # Restore EmotionStateMachine
        self.emotion_state_machine.current_state = snapshot.emotion_current_state
        self.emotion_state_machine.exchange_count = snapshot.emotion_exchange_count
        
        # Restore ContextReferencer
        self.context_referencer.max_history = snapshot.context_max_history
        
        self._is_modulated = False
        self._current_modulation = {}
    
    def get_current_modulation(self) -> dict[str, float]:
        """Get currently applied modulation values.
        
        Returns:
            Dictionary of modulation keys and values
        """
        return dict(self._current_modulation)
    
    def is_modulated(self) -> bool:
        """Check if modulation is currently applied.
        
        Returns:
            True if modulation is applied, False otherwise
        """
        return self._is_modulated
    
    def apply_temporary_modulation(self, modulation: dict[str, float]) -> None:
        """Apply modulation and restore after exiting context.
        
        This is a convenience method that can be used with a context manager pattern.
        For use with 'with' statement, client code should wrap this.
        
        Args:
            modulation: Modulation values to apply temporarily
        """
        self.apply_modulation(modulation)
    
    def reset_to_original(self) -> None:
        """Reset to original state, clearing all modulation."""
        if self._is_modulated:
            self.restore_original_values()
        self._original_snapshot = None
        self._current_modulation = {}
