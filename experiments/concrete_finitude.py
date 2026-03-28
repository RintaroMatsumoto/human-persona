"""Backwards-compatible wrapper.

The real implementation has moved to core.inner_shell.defaults.finitude.
This file remains so that existing scripts using
``from experiments.concrete_finitude import SimpleFinitudeEngine``
continue to work.
"""

from core.inner_shell.defaults.finitude import (
    DefaultFinitudeEngine as SimpleFinitudeEngine,
)
