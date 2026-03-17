"""human-persona core: 言語・文化非依存の人間らしいAI振る舞い基底クラス群."""

from core.base_persona import HumanPersonaBase
from core.timing_controller import TimingController
from core.style_variator import StyleVariator
from core.emotion_state_machine import EmotionStateMachine, EmotionState
from core.context_referencer import ContextReferencer
from core.escalation_detector import EscalationDetector

__all__ = [
    "HumanPersonaBase",
    "TimingController",
    "StyleVariator",
    "EmotionStateMachine",
    "EmotionState",
    "ContextReferencer",
    "EscalationDetector",
]
