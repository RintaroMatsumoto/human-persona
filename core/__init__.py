"""
Core module — Language-agnostic framework for humanized AI personas.

Exports:
    - HumanPersonaBase: Abstract base class for persona implementations
    - TimingController: Response delay simulation
    - StyleVariator: Linguistic style variation engine
    - EmotionStateMachine: Emotional state tracking
    - ContextReferencer: Conversation memory and back-referencing
    - EscalationDetector: Human handoff trigger detection
    - ConfigValidator: Configuration validation
    - InnerOuterBridge: Bridge between inner and outer shell modules
"""

from __future__ import annotations

from .base_persona import HumanPersonaBase, Message, PersonaResponse, Platform
from .config_validator import ConfigValidator, ValidationResult
from .context_referencer import ContextReferencer, ContextRef
from .emotion_state_machine import EmotionStateMachine
from .escalation_detector import EscalationDetector, EscalationResult
from .inner_outer_bridge import InnerOuterBridge, ModulationValues, BridgeState
from .style_variator import StyleVariator, Register
from .timing_controller import TimingController, TimingConfig

__all__ = [
    'HumanPersonaBase',
    'Message',
    'PersonaResponse',
    'Platform',
    'TimingController',
    'TimingConfig',
    'StyleVariator',
    'Register',
    'EmotionStateMachine',
    'ContextReferencer',
    'ContextRef',
    'EscalationDetector',
    'EscalationResult',
    'ConfigValidator',
    'ValidationResult',
    'InnerOuterBridge',
    'ModulationValues',
    'BridgeState',
]

__version__ = '0.2.0'
