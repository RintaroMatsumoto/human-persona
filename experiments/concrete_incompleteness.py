"""Backwards-compatible wrapper.

The real implementation has moved to core.inner_shell.defaults.incompleteness.
This file remains so that existing scripts using
``from experiments.concrete_incompleteness import SimpleIncompletenessModel``
continue to work.
"""

from core.inner_shell.defaults.incompleteness import (
    DefaultIncompletenessModel as SimpleIncompletenessModel,
)
