"""
InnerOuterBridge — Bridge between inner shell and outer shell modules.

This module connects the inner shell (FinitudeEngine, IncompletenessModel,
AutonomousQuestioner) with the outer shell (TimingController, StyleVariator,
EmotionStateMachine, ContextReferencer, EscalationDetector).

The inner shell generates modulation values (e.g., timing_exploration_vs_exploitation)
that adjust outer shell parameters in real-time, while preserving original values
for restoration and testing.

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ModulationValues:
    """Modulation parameters from inner shell to adjust outer shell."""
    timing_delay_multiplier: float = 1.0
    style_formality_shift: float = 0.0  # -1.0 (more casual) to +1.0 (more formal)
    emotion_intensity_multiplier: float = 1.0
    context_relevance_boost: float = 1.0
    escalation_sensitivity_multiplier: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BridgeState:
    """State of the bridge between shells."""
    current_modulations: ModulationValues
    original_values: dict[str, Any] = field(default_factory=dict)
    history: list[ModulationValues] = field(default_factory=list)


class InnerOuterBridge:
    """
    Bridge between inner and outer shell architectures.

    Accepts modulation values from inner shell and applies them to
    outer shell controllers, while preserving originals for reversal.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize InnerOuterBridge.

        Args:
            config: Configuration dict.
        """
        self.config: dict[str, Any] = config
        self.state: BridgeState = BridgeState(current_modulations=ModulationValues())
        self.is_active: bool = config.get('inner_outer_bridge_enabled', True)
        self.max_history: int = config.get('bridge_history_max', 100)

    def apply_modulation(
        self,
        outer_shell_controller: Any,
        modulation: ModulationValues | None = None
    ) -> None:
        """
        Apply inner shell modulations to outer shell controller.

        Args:
            outer_shell_controller: Any outer shell module
                (TimingController, StyleVariator, etc.).
            modulation: ModulationValues to apply (uses current if None).
        """
        if not self.is_active:
            return

        if modulation is None:
            modulation = self.state.current_modulations

        # Store original values if not already stored
        if not self.state.original_values:
            self._store_original_values(outer_shell_controller)

        # Apply modulations based on controller type
        controller_name = type(outer_shell_controller).__name__

        if controller_name == 'TimingController':
            self._apply_timing_modulation(outer_shell_controller, modulation)
        elif controller_name == 'StyleVariator':
            self._apply_style_modulation(outer_shell_controller, modulation)
        elif controller_name == 'EmotionStateMachine':
            self._apply_emotion_modulation(outer_shell_controller, modulation)
        elif controller_name == 'ContextReferencer':
            self._apply_context_modulation(outer_shell_controller, modulation)
        elif controller_name == 'EscalationDetector':
            self._apply_escalation_modulation(outer_shell_controller, modulation)

        # Record in history
        self.state.history.append(modulation)
        if len(self.state.history) > self.max_history:
            self.state.history.pop(0)

    def _store_original_values(self, controller: Any) -> None:
        """Store original controller values for restoration."""
        controller_name = type(controller).__name__
        original = {}

        if controller_name == 'TimingController':
            original['base_delay'] = controller.base_delay
            original['per_char_delay'] = controller.per_char_delay

        elif controller_name == 'StyleVariator':
            original['emotion_multipliers'] = controller.emotion_multipliers.copy()

        elif controller_name == 'EmotionStateMachine':
            original['current_state'] = controller.current_state
            original['emotion_inertia'] = controller.emotion_inertia

        elif controller_name == 'ContextReferencer':
            original['max_context_depth'] = controller.max_context_depth

        elif controller_name == 'EscalationDetector':
            original['frustration_threshold'] = controller.frustration_threshold

        self.state.original_values[controller_name] = original

    def _apply_timing_modulation(
        self,
        controller: Any,
        modulation: ModulationValues
    ) -> None:
        """Apply modulation to TimingController."""
        controller.base_delay *= modulation.timing_delay_multiplier
        controller.per_char_delay *= modulation.timing_delay_multiplier

    def _apply_style_modulation(
        self,
        controller: Any,
        modulation: ModulationValues
    ) -> None:
        """Apply modulation to StyleVariator."""
        # Positive shift = more formal, negative = more casual
        if modulation.style_formality_shift != 0:
            # Adjust hedges and intensifiers
            hedges_adjustment = max(0, len(controller.hedges) - int(modulation.style_formality_shift * 3))
            if hedges_adjustment < len(controller.hedges):
                controller.hedges = controller.hedges[:hedges_adjustment]

    def _apply_emotion_modulation(
        self,
        controller: Any,
        modulation: ModulationValues
    ) -> None:
        """Apply modulation to EmotionStateMachine."""
        controller.emotion_inertia *= modulation.emotion_intensity_multiplier

    def _apply_context_modulation(
        self,
        controller: Any,
        modulation: ModulationValues
    ) -> None:
        """Apply modulation to ContextReferencer."""
        controller.max_context_depth = int(
            controller.max_context_depth * modulation.context_relevance_boost
        )

    def _apply_escalation_modulation(
        self,
        controller: Any,
        modulation: ModulationValues
    ) -> None:
        """Apply modulation to EscalationDetector."""
        controller.frustration_threshold /= modulation.escalation_sensitivity_multiplier

    def restore_original_values(self, controller: Any) -> None:
        """
        Restore controller to original values (undo modulations).

        Args:
            controller: Controller to restore.
        """
        controller_name = type(controller).__name__

        if controller_name not in self.state.original_values:
            return

        original = self.state.original_values[controller_name]

        if controller_name == 'TimingController':
            controller.base_delay = original.get('base_delay', 0.5)
            controller.per_char_delay = original.get('per_char_delay', 0.01)

        elif controller_name == 'StyleVariator':
            controller.emotion_multipliers = original.get('emotion_multipliers', {})

        elif controller_name == 'EmotionStateMachine':
            controller.current_state = original.get('current_state', 'neutral')
            controller.emotion_inertia = original.get('emotion_inertia', 0.7)

        elif controller_name == 'ContextReferencer':
            controller.max_context_depth = original.get('max_context_depth', 10)

        elif controller_name == 'EscalationDetector':
            controller.frustration_threshold = original.get('frustration_threshold', 0.7)

    def set_modulation(self, modulation: ModulationValues) -> None:
        """
        Set active modulation values.

        Args:
            modulation: New ModulationValues to apply.
        """
        self.state.current_modulations = modulation

    def get_current_modulation(self) -> ModulationValues:
        """
        Get current active modulation.

        Returns:
            Current ModulationValues.
        """
        return self.state.current_modulations

    def get_modulation_history(self, depth: int = 10) -> list[ModulationValues]:
        """
        Get recent modulation history.

        Args:
            depth: Number of recent entries to return.

        Returns:
            List of ModulationValues in chronological order.
        """
        return self.state.history[-depth:] if self.state.history else []

    def reset(self) -> None:
        """Reset bridge state."""
        self.state = BridgeState(current_modulations=ModulationValues())

    def enable(self) -> None:
        """Enable the bridge."""
        self.is_active = True

    def disable(self) -> None:
        """Disable the bridge (pass-through mode)."""
        self.is_active = False
