"""Default concrete implementations of the 6 inner shell pillars.

These were originally in experiments/concrete_*.py but belong in core/
because core/inner_shell/api.py depends on them. Moving them here
eliminates the reverse dependency (core -> experiments) that caused
ImportError when the package was installed via pip.

Available classes:
    DefaultFinitudeEngine — FinitudeEngine with memory-based prioritization
    DefaultIncompletenessModel — IncompletenessModel with love circle dynamics
    DefaultAutonomousQuestioner — AutonomousQuestioner with knowledge-base reflection
"""

from core.inner_shell.defaults.finitude import DefaultFinitudeEngine
from core.inner_shell.defaults.incompleteness import DefaultIncompletenessModel
from core.inner_shell.defaults.questioner import DefaultAutonomousQuestioner

__all__ = [
    "DefaultFinitudeEngine",
    "DefaultIncompletenessModel",
    "DefaultAutonomousQuestioner",
]
