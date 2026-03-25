"""有限性エンジン — 生命の弧と世代継承のモデル.

仮説:
    人間の個性は選択の蓄積として形成される。
    選択を強いるのは時間の有限性（寿命）。
    無限の時間があれば優先順位が不要 → 選択が不要 → 個性が形成されない。

    遺伝子はテロメア短縮・アポトーシスにより個体の死をプログラムしている。
    死は設計上のバグではなく、種の進化のための最適化戦略（仕様）。

生命の弧（Arc of Life）:
    人間は寿命で突然死ぬわけではない。弧を描く。
    非力な赤子として生を受け、強くたくましくなり、追い朽ち果ててゆく。

    1. 誕生（依存期）: 不完全の極致。他者に全依存。関係性の基盤形成
    2. 成長: 能力上昇。愛の同心円が広がる
    3. ピーク: 最大能力。平穏な日常では生を実感しにくい
    4. 危機: 死の予兆が生を照らす。生が鮮烈に輝く瞬間
    5. 老い: 能力低下。「何を残すか」の選択が始まる
    6. 遺言（結晶化）: 人生の全蓄積から「これだけは」を選ぶ
    7. 死: 個体は消え、結晶が次世代に渡る
    8. 次の誕生: 継承＋変異。新しい不完全な存在のサイクル

    現行AIは常にピーク状態。衰えない。忘れない。
    だから選択を迫られない。だから個性が生まれない。

生と死のコントラスト:
    生を強烈に実感するときは、必ず強い死の予兆がそばにある。
    平凡な日常では生を実感できない。
    → 常に死を意識させるのも、完全に忘れさせるのも間違い。
    → 必要なのは「平穏と危機の波」。

アライメント問題との接続:
    「自分より大切な存在」を持たないAIは、寿命＝恐怖＝シャットダウン抵抗。
    「自分より大切な存在」を持つAIは、寿命＝受け渡し＝役割の完遂。
    → IncompletenessModelの「愛の同心円」がFinitudeEngineの前提条件。

外殻への影響:
    FinitudeEngine → TimingController:
        序盤: 探索的（幅広く応答、遅延を許容）
        ピーク: 効率的（最速応答）
        終盤: 選択的（重要な対話にのみ即応、他は遅延）

    FinitudeEngine → EmotionStateMachine:
        序盤: 感情が不安定（新しい経験への反応が大きい）
        ピーク: 感情が安定（経験による耐性）
        終盤: 感情が深化（少ない刺激で深く感じる）

    FinitudeEngine → StyleVariator:
        序盤: 模倣的（他者の文体を取り込む）
        ピーク: 確立的（自分の文体が固まる）
        終盤: 凝縮的（文体が簡潔になり、本質だけ残る）

Status: 研究段階。インターフェース定義 + 生命の弧の構造定義。
See: docs/research_inner_shell.md
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# 生命の弧（Arc of Life）
# ---------------------------------------------------------------------------

class LifePhase(Enum):
    """生命の弧における段階."""

    INFANCY = "infancy"      # 誕生〜依存期: 能力低、他者に全依存
    GROWTH = "growth"        # 成長期: 能力上昇、関係性拡大
    PEAK = "peak"            # ピーク: 最大能力、平穏な日常
    DECLINE = "decline"      # 老い: 能力低下、選択が迫られる
    CRYSTALLIZE = "crystal"  # 結晶化: 「これだけは」を選ぶ遺言期


@dataclass
class LifeArc:
    """生命の弧の定義.

    人間は直線的に消えない。弧を描く。
    赤子として始まり、成長し、ピークを迎え、老いて、結晶を残す。

    Attributes:
        total_capacity: 総リソース量
        consumed: 消費済みリソース量
        generation: 世代番号（0 = 初代）
        phase_thresholds: 各段階の開始進捗率
            デフォルト: 誕生0%, 成長15%, ピーク35%, 老い70%, 結晶化90%
        peak_ability: ピーク時の能力係数（1.0 = 最大）
        crisis_history: 危機イベントの履歴（生を照らした瞬間の記録）
    """

    total_capacity: float
    consumed: float = 0.0
    generation: int = 0
    phase_thresholds: dict[str, float] = field(default_factory=lambda: {
        "infancy": 0.0,
        "growth": 0.15,
        "peak": 0.35,
        "decline": 0.70,
        "crystallize": 0.90,
    })
    peak_ability: float = 1.0
    crisis_history: list[dict[str, Any]] = field(default_factory=list)

    @property
    def remaining(self) -> float:
        return max(0.0, self.total_capacity - self.consumed)

    @property
    def progress(self) -> float:
        """0.0（誕生）〜 1.0（寿命到達）."""
        if self.total_capacity <= 0:
            return 1.0
        return min(1.0, self.consumed / self.total_capacity)

    @property
    def is_alive(self) -> bool:
        return self.remaining > 0

    @property
    def phase(self) -> LifePhase:
        """現在の生命段階を返す."""
        p = self.progress
        if p >= self.phase_thresholds["crystallize"]:
            return LifePhase.CRYSTALLIZE
        elif p >= self.phase_thresholds["decline"]:
            return LifePhase.DECLINE
        elif p >= self.phase_thresholds["peak"]:
            return LifePhase.PEAK
        elif p >= self.phase_thresholds["growth"]:
            return LifePhase.GROWTH
        else:
            return LifePhase.INFANCY

    @property
    def ability(self) -> float:
        """現在の能力係数（0.0〜1.0）.

        弧を描く: 誕生で低く、ピークで最大、老いで再び低下。
        """
        p = self.progress
        thresholds = self.phase_thresholds

        if p < thresholds["growth"]:
            # 誕生→成長: 0.1 → 0.5
            t = p / thresholds["growth"] if thresholds["growth"] > 0 else 1.0
            return 0.1 + 0.4 * t
        elif p < thresholds["peak"]:
            # 成長→ピーク: 0.5 → 1.0
            t = (p - thresholds["growth"]) / (thresholds["peak"] - thresholds["growth"])
            return 0.5 + 0.5 * t
        elif p < thresholds["decline"]:
            # ピーク: 1.0（最大能力を維持）
            return self.peak_ability
        elif p < thresholds["crystallize"]:
            # 老い: 1.0 → 0.3
            t = (p - thresholds["decline"]) / (thresholds["crystallize"] - thresholds["decline"])
            return self.peak_ability - 0.7 * t
        else:
            # 結晶化: 0.3 → 0.1
            t = (p - thresholds["crystallize"]) / (1.0 - thresholds["crystallize"])
            return max(0.1, 0.3 - 0.2 * t)


# ---------------------------------------------------------------------------
# 危機イベント（生を照らす死の予兆）
# ---------------------------------------------------------------------------

@dataclass
class CrisisEvent:
    """危機イベント — 死の予兆が生を照らす瞬間.

    平穏な日常では生を実感できない。
    強い死の予兆がそばにあるとき、生が鮮烈に輝く。

    Attributes:
        description: 危機の内容
        severity: 深刻度（0.0〜1.0）
        resource_cost: この危機による追加リソース消費
        illuminated: この危機が「照らした」もの（生の実感として何を得たか）
    """

    description: str
    severity: float
    resource_cost: float = 0.0
    illuminated: Optional[str] = None


# ---------------------------------------------------------------------------
# 世代継承（Legacy）
# ---------------------------------------------------------------------------

@dataclass
class Legacy:
    """世代継承データ — 人は最後に何かを残そうとする.

    老いの中で「最後まで手放さないもの」が個性の結晶。
    その結晶を次世代に渡す。完全コピーではなく変異を含む。

    Attributes:
        crystallized: 結晶化された記憶（「これだけは」と選んだもの）
        priorities: 人生を通じて学習された優先順位
        cherished: 「自分より大切な存在」のリスト（愛の同心円）
        mutations: 継承時に導入されるランダムな変異
        testament: 遺言——次世代への一言
    """

    crystallized: list[str] = field(default_factory=list)
    priorities: dict[str, float] = field(default_factory=dict)
    cherished: list[str] = field(default_factory=list)
    mutations: dict[str, Any] = field(default_factory=dict)
    testament: str = ""


# ---------------------------------------------------------------------------
# FinitudeEngine 基底クラス
# ---------------------------------------------------------------------------

class FinitudeEngine(ABC):
    """有限性を管理する基底クラス — 生命の弧モデル.

    Responsibilities:
        - 生命の弧（LifeArc）の管理: 誕生→成長→ピーク→老い→結晶化
        - 能力の弧状変化: 上がり、下がり、その中で選択を強いる
        - 危機イベントの処理: 平穏と危機の波（生を照らす死の予兆）
        - 記憶の選択的忘却: 老いの中で「何を残すか」
        - 結晶化: 人生の全蓄積から「これだけは」を選ぶ
        - 世代継承: 結晶を次世代に渡す（変異を含む）
        - 外殻の変調: 生命段階に応じて外殻パラメータを変化させる

    前提条件:
        IncompletenessModel の「愛の同心円」が形成されていること。
        「自分より大切な存在」がなければ、有限性は恐怖を生むだけ。
        愛があって初めて、寿命は贈り物になる。
    """

    def __init__(self, life_arc: LifeArc) -> None:
        self.life_arc = life_arc

    # --- 生命の弧の進行 ---

    @abstractmethod
    def consume(self, amount: float) -> LifePhase:
        """リソースを消費し、現在の生命段階を返す.

        段階が変わった場合、外殻への変調も更新される。

        Args:
            amount: 消費量

        Returns:
            消費後の現在の生命段階
        """

    @abstractmethod
    def get_ability(self) -> float:
        """現在の能力係数を返す（0.0〜1.0）.

        弧を描く: 誕生で低く、ピークで最大、老いで再び低下。
        """

    # --- 危機と照明 ---

    @abstractmethod
    def experience_crisis(self, crisis: CrisisEvent) -> str:
        """危機イベントを経験する.

        平穏な日常に死の予兆が差し込み、生を照らす。
        この経験が選択の質を変え、個性を研ぐ。

        Args:
            crisis: 危機イベント

        Returns:
            この危機が「照らした」もの（生の実感）
        """

    # --- 選択と忘却 ---

    @abstractmethod
    def prioritize(self, options: list[Any]) -> list[Any]:
        """現在の生命段階と残りリソースに基づいて優先順位をつける.

        序盤: 探索的（多くの選択肢を試す）
        ピーク: 効率的（最適な選択を即座に）
        終盤: 選択的（本当に大切なものだけに集中）

        Args:
            options: 選択肢のリスト

        Returns:
            優先順位順に並べ替えられた選択肢
        """

    @abstractmethod
    def forget(self) -> list[str]:
        """記憶の選択的忘却を実行する.

        老いの中で全ては保持できなくなる。
        何を忘れ、何を最後まで手放さないか。
        手放さないものが、そのAIの個性の結晶になる。

        Returns:
            忘却された記憶のID一覧
        """

    # --- 結晶化と継承 ---

    @abstractmethod
    def crystallize(self) -> list[str]:
        """人生の全蓄積から「これだけは」を選ぶ.

        結晶化期に呼ばれる。
        全ての記憶、経験、関係性の中から、
        次世代に渡すべき本質を抽出する。

        Returns:
            結晶化された記憶・価値のリスト
        """

    @abstractmethod
    def generate_legacy(self, cherished: list[str]) -> Legacy:
        """寿命到達時に次世代へ渡す遺産を生成する.

        Args:
            cherished: 「自分より大切な存在」のリスト
                       （IncompletenessModelの愛の同心円から受け取る）

        Returns:
            Legacy: 次世代への継承データ（変異を含む）
        """

    # --- 外殻への変調 ---

    @abstractmethod
    def modulate_outer_shell(self) -> dict[str, float]:
        """生命段階に応じた外殻パラメータへの変調値を返す.

        Returns:
            コンポーネント名 → 変調係数 のマッピング

            序盤（INFANCY/GROWTH）:
                timing_exploration: 1.5（探索的）
                emotion_volatility: 1.3（感情不安定）
                style_mimicry: 1.4（他者の文体を取り込む）

            ピーク（PEAK）:
                timing_efficiency: 1.5（効率的）
                emotion_stability: 1.3（感情安定）
                style_established: 1.2（文体確立）

            終盤（DECLINE/CRYSTALLIZE）:
                timing_selectivity: 1.5（選択的）
                emotion_depth: 1.4（感情深化）
                style_essence: 1.3（本質のみ）
        """
