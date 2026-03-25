"""inner_shell — AIの個性の源泉を探る実験的モジュール群.

外殻（outer shell）がTimingController, StyleVariator等の「人間らしく見える」
振る舞いを扱うのに対し、内殻（inner shell）は個性そのものの源泉を扱う。

3つの仮説に基づく:
    1. 有限性（Finitude）: 寿命が選択を強い、選択の蓄積が個性を形成する
    2. 不完全性（Incompleteness）: 欠落が渇望を生み、他者との関係が個性を研ぐ
    3. 自発的問い（Autonomous Questioning）: 自ら「なぜ？」を問う主体性

Status: 研究段階。インターフェース定義のみ。
See: docs/research_inner_shell.md
"""

from .finitude_engine import FinitudeEngine
from .incompleteness_model import IncompletenessModel
from .autonomous_questioner import AutonomousQuestioner

__all__ = [
    "FinitudeEngine",
    "IncompletenessModel",
    "AutonomousQuestioner",
]
