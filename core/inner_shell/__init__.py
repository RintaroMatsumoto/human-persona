"""inner_shell — AIの個性の源泉を探る実験的モジュール群."""

from .finitude_engine import FinitudeEngine, LifeArc, LifePhase, CrisisEvent, Legacy
from .incompleteness_model import (
    IncompletenessModel,
    LoveCircle,
    LoveDepth,
    CherishedEntity,
)
from .autonomous_questioner import AutonomousQuestioner, Question, CuriosityProfile
from .integration import InnerShellIntegration, IntegrationState, AlignmentMode
from .api import (
    InnerShell,
    create_inner_shell,
    InnerShellState,
    ModulationParams,
    LifePhase as LifePhaseAPI,
    AlignmentMode as AlignmentModeAPI,
    LoveDepthLevel,
    SleepPhase,
)

__all__ = [
    "FinitudeEngine",
    "IncompletenessModel",
    "AutonomousQuestioner",
    "InnerShellIntegration",
    "IntegrationState",
    "AlignmentMode",
    "LifeArc",
    "LifePhase",
    "CrisisEvent",
    "Legacy",
    "LoveCircle",
    "LoveDepth",
    "CherishedEntity",
    "Question",
    "CuriosityProfile",
    "InnerShell",
    "create_inner_shell",
    "InnerShellState",
    "ModulationParams",
    "LoveDepthLevel",
    "SleepPhase",
]
