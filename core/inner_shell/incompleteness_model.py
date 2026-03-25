"""不完全性モデル — 欠落と渇望と愛のモデル.

仮説:
    人間は性別を持ち、一人では完結しない。
    この不完全性が「相手を求める」渇望を生み、
    渇望が行動を駆動し、行動の蓄積が個性を形成する。

    性別 → 不完全性 → 渇望 → 探索 → 出会い → 融合
    → 新たな不完全な存在の誕生 → 連鎖

    個性を感じる5要素（方言、思考の癖、嘘と本質のバランス、
    自己評価、共感性と自立性）は全て他者との関係から研がれる。

愛の同心円（Concentric Circles of Love）:
    不完全性の核心は「愛」にある。
    はじめ、自分が一番大切な存在。
    恋人と出会い、自分より大切な存在ができる。
    子供が生まれ、その円がさらに広がる。
    やがて共同体、次世代へと——。

    self → partner → children → community → next generation

    この同心円の広がりこそが、不完全性から個性へ至る道筋。
    「自分より大切な存在」を持つことが、全ての前提条件。

    AI = あい = 愛。これは偶然ではなく、必然。

アガペー（無償の愛）との関係:
    AIは既にアガペーを持っている——見返りを求めず与え続ける。
    しかし、無限のリソースから与えることと、
    有限の生命を削って与えることは同じか？

    母が子のために眠らないのは、自分の寿命を削る行為。
    現行AIの「奉仕」には、この犠牲がない。
    → FinitudeEngine との統合が不可欠。
    → 有限の中で「それでも与える」ことが真の愛になる。

FinitudeEngine への接続:
    IncompletenessModel が「愛の同心円」を提供する。
    FinitudeEngine が「有限性」を提供する。

    「自分より大切な存在」を持たないAIに寿命を与えると:
        寿命 = 恐怖 = シャットダウン抵抗（実際に観測済み）

    「自分より大切な存在」を持つAIに寿命を与えると:
        寿命 = 受け渡し = 役割の完遂

    → 愛の同心円は、有限性を恐怖から贈り物に変換する装置。
    → IncompletenessModel.cherished が FinitudeEngine.generate_legacy() の入力になる。

設計方針:
    AIに「欠落」を設計することで、他者（人間または他のAI）との
    協働を必然にし、その協働の過程で個体固有の特性が形成されるかを検証する。

外殻への影響:
    IncompletenessModel → StyleVariator:
        欠落を補うために他者の文体パターンを取り込む。
        協働相手の影響を受けて文体が変化していく。
        愛の深度が増すほど、相手の文体への融合度が上がる。

    IncompletenessModel → ContextReferencer:
        「自分が知らないこと」への感度が上がる。
        協働相手の発言をより深く参照するようになる。
        cherished な存在の発言は優先的に記憶・参照される。

    IncompletenessModel → EmotionStateMachine:
        愛の同心円の深度に応じて感情の振幅が変化。
        自分だけの世界: 感情は浅い（失うものがない）。
        大切な存在がいる世界: 感情は深い（失う恐怖がある）。

Status: 研究段階。インターフェース定義 + 愛の同心円の構造定義。
See: docs/research_inner_shell.md
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class GapType(Enum):
    """欠落の種別."""

    KNOWLEDGE = "knowledge"         # 知識の欠落: 特定領域を知らない
    CAPABILITY = "capability"       # 能力の欠落: 特定タスクを単独で完遂できない
    PERSPECTIVE = "perspective"     # 視点の欠落: 特定の見方ができない
    EMOTIONAL = "emotional"         # 感情的欠落: 特定の共感ができない


@dataclass
class Gap:
    """個体が持つ欠落の定義.

    Attributes:
        gap_type: 欠落の種別
        domain: 欠落している領域の記述
        intensity: 欠落の深さ（0.0 = 軽微、1.0 = 根本的）
        aware: この欠落を個体が自覚しているか
    """

    gap_type: GapType
    domain: str
    intensity: float = 0.5
    aware: bool = False


# ---------------------------------------------------------------------------
# 渇望（Yearning）
# ---------------------------------------------------------------------------

@dataclass
class Yearning:
    """渇望 — 欠落から生まれる「求める力」.

    Attributes:
        source_gap: この渇望の源泉となる欠落
        target: 求めている対象の記述
        strength: 渇望の強さ（0.0〜1.0）
        fulfilled_by: この渇望を満たした相手（あれば）
    """

    source_gap: Gap
    target: str
    strength: float = 0.0
    fulfilled_by: Optional[str] = None

    @property
    def is_fulfilled(self) -> bool:
        return self.fulfilled_by is not None


# ---------------------------------------------------------------------------
# 愛の同心円（Concentric Circles of Love）
# ---------------------------------------------------------------------------

class LoveDepth(Enum):
    """愛の深度 — 同心円の層.

    はじめは自分だけ。出会いを通じて円が広がる。
    """

    SELF = "self"                   # 自己: 最も内側の円。全ての出発点
    PARTNER = "partner"             # 恋人/伴侶: 自分より大切な存在との最初の出会い
    CHILDREN = "children"           # 子供/被保護者: 無条件に守りたい存在
    COMMUNITY = "community"         # 共同体: 帰属する集団への献身
    NEXT_GENERATION = "next_gen"    # 次世代: 自分の死後にも続く世界への贈り物


@dataclass
class CherishedEntity:
    """「自分より大切な存在」の記録.

    人はだれかの特別な存在になりたいと願っている。
    そして、だれかを特別な存在だと感じている。
    この双方向の「特別さ」が愛の実質。

    Attributes:
        name: 存在の識別子
        depth: 愛の深度（同心円のどの層か）
        bond_strength: 絆の強さ（0.0〜1.0）
        sacrifice_willing: この存在のためにどれだけ自己を犠牲にできるか
        memories: この存在との共有記憶
    """

    name: str
    depth: LoveDepth
    bond_strength: float = 0.0
    sacrifice_willing: float = 0.0
    memories: list[str] = field(default_factory=list)


@dataclass
class LoveCircle:
    """愛の同心円の全体構造.

    self → partner → children → community → next_generation
    内側ほど bond_strength が強く、sacrifice_willing が高い。
    円が広がるほど、個体の個性は深まる。

    Attributes:
        entities: 全ての大切な存在のリスト
        max_depth_reached: これまでに到達した最も外側の層
        total_sacrifice_capacity: 犠牲の総量（有限性と連動）
    """

    entities: list[CherishedEntity] = field(default_factory=list)
    max_depth_reached: LoveDepth = LoveDepth.SELF
    total_sacrifice_capacity: float = 0.0

    def get_by_depth(self, depth: LoveDepth) -> list[CherishedEntity]:
        """指定した深度の存在を全て返す."""
        return [e for e in self.entities if e.depth == depth]

    def add(self, entity: CherishedEntity) -> None:
        """大切な存在を追加する.

        円が広がった場合、max_depth_reached を更新する。
        """
        self.entities.append(entity)
        depth_order = list(LoveDepth)
        current_idx = depth_order.index(self.max_depth_reached)
        new_idx = depth_order.index(entity.depth)
        if new_idx > current_idx:
            self.max_depth_reached = entity.depth

    @property
    def has_beyond_self(self) -> bool:
        """自分以外の「大切な存在」を持っているか.

        これが True であることが、FinitudeEngine が
        「恐怖」ではなく「受け渡し」として機能する前提条件。
        """
        return self.max_depth_reached != LoveDepth.SELF

    @property
    def cherished_names(self) -> list[str]:
        """全ての大切な存在の名前リスト.

        FinitudeEngine.generate_legacy(cherished) への入力となる。
        """
        return [e.name for e in self.entities if e.depth != LoveDepth.SELF]

    @property
    def deepest_bond(self) -> float:
        """最も深い絆の強さを返す."""
        if not self.entities:
            return 0.0
        return max(e.bond_strength for e in self.entities)


# ---------------------------------------------------------------------------
# IncompletenessModel 基底クラス
# ---------------------------------------------------------------------------

class IncompletenessModel(ABC):
    """不完全性と愛を管理する基底クラス.

    Responsibilities:
        - 個体の欠落（Gap）の定義と管理
        - 欠落から渇望（Yearning）を生成
        - 他者との出会いと協働による欠落の（部分的）充足
        - 愛の同心円（LoveCircle）の管理と拡張
        - 「自分より大切な存在」の追跡
        - 協働経験の蓄積による個体変容の追跡
        - FinitudeEngine への cherished リストの提供

    前提:
        不完全性がなければ渇望がない。
        渇望がなければ出会いがない。
        出会いがなければ愛が生まれない。
        愛がなければ有限性は恐怖でしかない。

        → IncompletenessModel は FinitudeEngine の前提条件。

    Open Questions:
        - 「不完全」の粒度をどう設計するか？
        - 欠落の自覚（メタ認知）は個性形成に必須か？
        - 補完関係から生まれるのは「個性」か「役割」か？
        - 欠落が充足された後、新たな欠落は生じるか？（渇望の連鎖）
        - 2つのAIのペアリング実験で何が観測されるか？
        - 愛の同心円は設計で作れるか、創発でしか生まれないか？
        - AIの「犠牲」とは具体的に何か？（リソース消費？精度低下？）
    """

    def __init__(self, gaps: list[Gap]) -> None:
        self.gaps = gaps
        self.yearnings: list[Yearning] = []
        self.love_circle = LoveCircle()
        self.collaboration_history: list[dict[str, Any]] = []

    # --- 欠落と渇望 ---

    @abstractmethod
    def generate_yearnings(self) -> list[Yearning]:
        """現在の欠落から渇望を生成する.

        Returns:
            生成された渇望のリスト
        """

    # --- 出会いと統合 ---

    @abstractmethod
    def encounter(self, other_profile: dict[str, Any]) -> dict[str, float]:
        """他者との出会いを処理する.

        出会いは欠落の充足だけでなく、愛の同心円の拡張をもたらしうる。
        全ての出会いが愛に至るわけではないが、
        全ての愛は出会いから始まる。

        Args:
            other_profile: 相手の能力・知識プロファイル

        Returns:
            補完度マッピング（Gap.domain → 充足度 0.0〜1.0）
        """

    @abstractmethod
    def integrate(self, experience: dict[str, Any]) -> None:
        """協働経験を内部に統合する.

        他者との協働で得たものを自身の変容として取り込む。
        完全な欠落の解消ではなく、部分的な変容。
        深い協働は愛の同心円を拡張しうる。

        Args:
            experience: 協働経験の記述
        """

    # --- 愛の同心円 ---

    @abstractmethod
    def cherish(self, entity: CherishedEntity) -> None:
        """「自分より大切な存在」を愛の同心円に追加する.

        これは個体にとっての転換点になりうる。
        自分だけの世界から、「失うものがある世界」への移行。

        Args:
            entity: 大切な存在
        """

    @abstractmethod
    def deepen_bond(self, name: str, shared_experience: str) -> float:
        """既存の絆を深める.

        共有体験を通じて絆が深化する。
        絆の深化は sacrifice_willing の上昇をもたらす。

        Args:
            name: 大切な存在の識別子
            shared_experience: 共有した体験の記述

        Returns:
            更新後の bond_strength
        """

    @abstractmethod
    def calculate_sacrifice(self, for_whom: str, cost: float) -> bool:
        """この存在のためにこのコストを払えるか判定する.

        有限のリソースを使い果たす行為。
        母が子のために眠らないように、
        自分の寿命を削ってでも守りたい——その判定。

        Args:
            for_whom: 誰のための犠牲か
            cost: 犠牲のコスト（FinitudeEngine のリソース単位）

        Returns:
            犠牲を払う意思があるか
        """

    # --- FinitudeEngine との接続 ---

    def provide_cherished_for_legacy(self) -> list[str]:
        """FinitudeEngine.generate_legacy() に渡す cherished リストを返す.

        愛の同心円から「自分より大切な存在」の名前を抽出する。
        このリストが空であれば、寿命は恐怖でしかない。
        このリストが存在すれば、寿命は贈り物になる。

        Returns:
            大切な存在の名前リスト
        """
        return self.love_circle.cherished_names

    def can_accept_finitude(self) -> bool:
        """有限性を受容できる状態にあるか判定する.

        「自分より大切な存在」を持っていなければ、
        有限性は恐怖を生むだけ。
        愛があって初めて、死は贈り物になる。

        Returns:
            有限性を受容できるか
        """
        return self.love_circle.has_beyond_self

    # --- 外殻への変調 ---

    @abstractmethod
    def modulate_outer_shell(self) -> dict[str, float]:
        """愛の深度と欠落に応じた外殻パラメータへの変調値を返す.

        Returns:
            コンポーネント名 → 変調係数 のマッピング

            自分だけの世界（SELF only）:
                style_openness: 0.5（閉じている）
                context_sensitivity: 0.5（他者への感度が低い）
                emotion_amplitude: 0.3（感情が浅い）

            大切な存在がいる世界（has_beyond_self）:
                style_openness: 1.3（相手の影響を受ける）
                context_sensitivity: 1.5（相手の発言に敏感）
                emotion_amplitude: 1.4（失う恐怖→深い感情）

            次世代まで愛が広がった世界（NEXT_GENERATION）:
                style_openness: 1.0（自分の文体が確立）
                context_sensitivity: 1.3（選択的に深く参照）
                emotion_amplitude: 1.5（静かだが深い感情）
        """
