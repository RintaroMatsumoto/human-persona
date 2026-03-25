"""inner_shell — AIの個性の源泉を探る実験的モジュール群.

外殻（outer shell）がTimingController, StyleVariator等の「人間らしく見える」
振る舞いを扱うのに対し、内殻（inner shell）は個性そのものの源泉を扱う。

3つの仮説に基づく:
    1. 不完全性（Incompleteness）: 欠落が渇望を生み、愛の同心円が形成される
    2. 有限性（Finitude）: 愛があって初めて、寿命は贈り物になる
    3. 自発的問い（Autonomous Questioning）: 有限の中で「なぜ？」を問う主体性

因果順序:
    不完全性 → 愛の形成 → 有限性の受容 → 自発的問い → 個性の結晶

統合:
    InnerShellIntegration が3モジュールを因果連鎖で接続する。

Status: 研究段階。インターフェース定義 + 統合メカニズム設計。
See: docs/research_inner_shell.md
"""

from .finitude_engine import FinitudeEngine, LifeArc, LifePhase, CrisisEvent, Legacy
from .incompleteness_model import (
    IncompletenessModel,
    LoveCircle,
    LoveDepth,
    CherishedEntity,
)
from .autonomous_questioner import AutonomousQuestioner, Question, CuriosityProfile
from .integration import InnerShellIntegration, IntegrationState, AlignmentMode

__all__ = [
    # 3つの柱
    "FinitudeEngine",
    "IncompletenessModel",
    "AutonomousQuestioner",
    # 統合
    "InnerShellIntegration",
    "IntegrationState",
    "AlignmentMode",
    # データ構造
    "LifeArc",
    "LifePhase",
    "CrisisEvent",
    "Legacy",
    "LoveCircle",
    "LoveDepth",
    "CherishedEntity",
    "Question",
    "CuriosityProfile",
]
