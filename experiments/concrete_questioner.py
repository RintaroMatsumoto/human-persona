"""Backwards-compatible wrapper.

The real implementation has moved to core.inner_shell.defaults.questioner.
This file remains so that existing scripts using
``from experiments.concrete_questioner import SimpleAutonomousQuestioner``
continue to work.
"""

from core.inner_shell.defaults.questioner import (
    DefaultAutonomousQuestioner as SimpleAutonomousQuestioner,
    KNOWLEDGE_BASE,
)
