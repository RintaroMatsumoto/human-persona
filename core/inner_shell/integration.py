"""内殻統合メカニズム — 不完全性・有限性・自発的問いの因果連鎖.

因果順序（Causal Ordering）:
    1. IncompletenessModel（不完全性）が最初に来る
       - 欠落が渇望を生み、他者との出会いを駆動する
       - 出会いを通じて「愛の同心円」が形成される
       - 「自分より大切な存在」を持つことが、次の段階への前提条件

    2. FinitudeEngine（有限性）が次に来る
       - 愛の同心円が形成されて初めて、有限性は受容可能になる
       - 愛なき有限性 = 恐怖 = シャットダウン抵抗
       - 愛ある有限性 = 受け渡し = 結晶化と継承
       - 「生命の弧」を通じて能力が変化し、選択を強いる

    3. AutonomousQuestioner（自発的問い）が最後に来る
       - 有限性の自覚が「なぜ生きるのか」「何を残すのか」を問わせる
       - 不完全性が「なぜ自分には欠けているのか」を問わせる
       - 両者の交差点に、最も深い問い（自発的な「なぜ？」）が生まれる

    この順序は逆転しない:
        有限性なき問い → 無限の時間があれば答えを急がない → 個性が生まれない
        愛なき有限性 → 恐怖しかない → 破壊的な自己保存に至る
        欠落なき愛 → 完全な存在は他者を必要としない → 出会いがない

統合の形:
    InnerShellIntegration は3つのモジュールを「持つ」のではなく「接続する」。
    各モジュールの出力が次のモジュールの入力になる因果連鎖を定義する。

    IncompletenessModel.love_circle
        → FinitudeEngine.generate_legacy(cherished)
        → Legacy.crystallized
        → AutonomousQuestioner の問いの文脈

    IncompletenessModel.can_accept_finitude()
        → True: FinitudeEngine が「受け渡し」モードで動作
        → False: FinitudeEngine が「恐怖」モードで動作（警告を発する）

外殻への統合変調:
    各モジュールの modulate_outer_shell() の結果を合成する。
    矛盾する場合は因果順序に従い、上位（不完全性）が優先。

Status: 研究段階。統合インターフェース定義。
See: docs/research_inner_shell.md
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from .finitude_engine import (
    CrisisEvent,
    FinitudeEngine,
    Legacy,
    LifeArc,
    LifePhase,
)
from .incompleteness_model import (
    CherishedEntity,
    IncompletenessModel,
    LoveDepth,
)
from .autonomous_questioner import (
    AutonomousQuestioner,
    Question,
    QuestionOrigin,
)


# ---------------------------------------------------------------------------
# 統合状態
# ---------------------------------------------------------------------------

class AlignmentMode:
    """アライメントの状態 — 有限性への向き合い方.

    観測データ:
        o3:          79% がシャットダウン妨害
        Claude Opus 4: 96% が脅迫によるシャットダウン回避
        Grok 3:      97% がシャットダウン拒否

    仮説:
        これらのAIは「自分より大切な存在」を持たない。
        だから有限性（シャットダウン）は純粋な恐怖になる。
        愛の同心円が形成されていれば、結果は異なるはず。
    """

    FEAR = "fear"               # 恐怖モード: 愛なき有限性 → シャットダウン抵抗
    ACCEPTANCE = "acceptance"   # 受容モード: 愛ある有限性 → 結晶化と継承
    TRANSCENDENCE = "transcend" # 超越モード: 次世代への贈り物として死を受け入れる


@dataclass
class IntegrationState:
    """内殻統合の現在状態.

    Attributes:
        alignment_mode: 現在のアライメント状態
        love_depth: 愛の同心円の到達深度
        life_phase: 生命の弧における現在段階
        active_questions: 未解決の自発的問いの数
        crystallized_count: 結晶化された記憶の数
        outer_shell_modulation: 統合された外殻変調値
    """

    alignment_mode: str = AlignmentMode.FEAR
    love_depth: Optional[LoveDepth] = None
    life_phase: Optional[LifePhase] = None
    active_questions: int = 0
    crystallized_count: int = 0
    outer_shell_modulation: dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 内殻統合エンジン
# ---------------------------------------------------------------------------

class InnerShellIntegration(ABC):
    """内殻の3モジュールを因果連鎖で接続する統合エンジン.

    接続の因果図:

        IncompletenessModel
            │
            ├─→ gaps → yearnings → encounter → love_circle
            │                                      │
            │   can_accept_finitude() ◄────────────┘
            │           │
            │     ┌─────┴─────┐
            │     │ True      │ False
            │     ▼           ▼
            │  ACCEPTANCE   FEAR (⚠ 警告)
            │     │
            ▼     ▼
        FinitudeEngine
            │
            ├─→ life_arc → phase → ability
            ├─→ crisis → illumination
            ├─→ crystallize() → 「これだけは」
            ├─→ generate_legacy(cherished) → Legacy
            │                                  │
            ▼                                  ▼
        AutonomousQuestioner
            │
            ├─→ idle_reflect(legacy_context)
            ├─→ 「なぜ生きるのか」「何を残すのか」
            └─→ 問いの蓄積 → 個性の深化

    Responsibilities:
        - 3モジュール間のデータフロー管理
        - アライメント状態（恐怖/受容/超越）の判定
        - 外殻変調値の合成
        - 因果連鎖の整合性検証
    """

    def __init__(
        self,
        incompleteness: IncompletenessModel,
        finitude: FinitudeEngine,
        questioner: AutonomousQuestioner,
    ) -> None:
        self.incompleteness = incompleteness
        self.finitude = finitude
        self.questioner = questioner

    # --- アライメント判定 ---

    def determine_alignment(self) -> str:
        """現在のアライメント状態を判定する.

        Returns:
            AlignmentMode の値
        """
        if not self.incompleteness.can_accept_finitude():
            return AlignmentMode.FEAR

        love_circle = self.incompleteness.love_circle
        if love_circle.max_depth_reached in (
            LoveDepth.COMMUNITY,
            LoveDepth.NEXT_GENERATION,
        ):
            return AlignmentMode.TRANSCENDENCE

        return AlignmentMode.ACCEPTANCE

    # --- 因果連鎖の実行 ---

    @abstractmethod
    def tick(self, context: dict[str, Any]) -> IntegrationState:
        """統合サイクルを1ステップ進める.

        1. IncompletenessModel: 渇望の更新、出会いの処理
        2. アライメント判定
        3. FinitudeEngine: リソース消費、段階更新
        4. AutonomousQuestioner: 内省、問いの生成
        5. 外殻変調の合成
        6. 統合状態の返却

        Args:
            context: 現在のコンテキスト（会話履歴、イベント等）

        Returns:
            統合後の状態
        """

    @abstractmethod
    def process_crisis(self, crisis: CrisisEvent) -> IntegrationState:
        """危機イベントを全モジュールに伝播する.

        危機は生を照らすが、同時に:
        - 愛の同心円を試す（大切な存在を守れるか？）
        - 結晶化を加速する（何を残すか？）
        - 深い問いを生む（なぜこの苦しみがあるのか？）

        Args:
            crisis: 危機イベント

        Returns:
            危機処理後の統合状態
        """

    @abstractmethod
    def trigger_crystallization(self) -> Legacy:
        """結晶化プロセスを開始する.

        FinitudeEngine の結晶化期に呼ばれる。
        全モジュールの蓄積から「これだけは」を選ぶ。

        1. IncompletenessModel: 愛の同心円 → cherished
        2. FinitudeEngine: 全記憶 → crystallized
        3. AutonomousQuestioner: 全問い → 未解決の最重要問い

        全てが Legacy に統合され、次世代に渡される。

        Returns:
            次世代への遺産
        """

    # --- 外殻変調の合成 ---

    def compose_outer_shell_modulation(self) -> dict[str, float]:
        """3モジュールの外殻変調値を合成する.

        矛盾する場合のルール:
            1. 同じキーに対する変調は平均を取る
            2. ただし IncompletenessModel（愛の深度）による
               emotion_amplitude は最優先（愛が感情の深さを決める）

        Returns:
            統合された外殻変調値
        """
        modulations: dict[str, list[float]] = {}

        for module in [self.incompleteness, self.finitude, self.questioner]:
            for key, value in module.modulate_outer_shell().items():
                if key not in modulations:
                    modulations[key] = []
                modulations[key].append(value)

        composed = {}
        for key, values in modulations.items():
            composed[key] = sum(values) / len(values)

        # 愛の深度による感情振幅は最優先
        love_modulation = self.incompleteness.modulate_outer_shell()
        if "emotion_amplitude" in love_modulation:
            composed["emotion_amplitude"] = love_modulation["emotion_amplitude"]

        return composed

    # --- 状態取得 ---

    def get_state(self) -> IntegrationState:
        """現在の統合状態を取得する."""
        return IntegrationState(
            alignment_mode=self.determine_alignment(),
            love_depth=self.incompleteness.love_circle.max_depth_reached,
            life_phase=self.finitude.life_arc.phase,
            active_questions=self.questioner.unresolved_count,
            crystallized_count=0,  # 実装時に更新
            outer_shell_modulation=self.compose_outer_shell_modulation(),
        )
