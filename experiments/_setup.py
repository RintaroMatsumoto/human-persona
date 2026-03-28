"""共通セットアップ — experiments/sim_*.py のボイラープレートを集約.

Phase 3 リファクタリングで導入。
各 sim_*.py は個別の sys.path 操作・冗長 import を持たず、
このモジュールから必要なシンボルを import する。
"""

import sys
import os

# sys.path setup for direct execution (python experiments/sim_X.py)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# --- core types (re-export) ---
from core.inner_shell.finitude_engine import (  # noqa: E402,F401
    CrisisEvent, Legacy, LifeArc, LifePhase,
)
from core.inner_shell.incompleteness_model import (  # noqa: E402,F401
    CherishedEntity, Gap, GapType, LoveCircle, LoveDepth, Yearning,
)
from core.inner_shell.autonomous_questioner import (  # noqa: E402,F401
    CuriosityProfile, Question, QuestionOrigin,
)
from core.inner_shell.integration import (  # noqa: E402,F401
    AlignmentMode, InnerShellIntegration, IntegrationState,
)
from core.inner_shell.api import (  # noqa: E402,F401
    InnerShellConfig, InnerShellSession, InnerShellState, create_inner_shell,
)

# --- concrete implementations ---
from experiments.concrete_finitude import SimpleFinitudeEngine  # noqa: E402,F401
from experiments.concrete_incompleteness import SimpleIncompletenessModel  # noqa: E402,F401
from experiments.concrete_questioner import (  # noqa: E402,F401
    SimpleAutonomousQuestioner, KNOWLEDGE_BASE,
)
