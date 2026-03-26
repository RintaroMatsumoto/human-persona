"""内殻モジュール 実用API.

内殻の3モジュール（FinitudeEngine, IncompletenessModel, AutonomousQuestioner）
および統合メカニズム（InnerShellIntegration）に対する統一的なファサードを提供する。

Usage:
    from core.inner_shell.api import InnerShellSession, InnerShellConfig

    config = InnerShellConfig(
        total_lifespan=50.0,
        emotional_gap_intensity=0.7,
        curiosity_domains={"love": 0.8, "mortality": 0.6},
    )
    session = InnerShellSession.create(config, seed=42)
    session.experience("世界を知る", category="knowledge", value=0.5, cost=1.0)
    session.encounter_other("Partner", depth="partner", initial_bond=0.3)
    session.deepen_bond("Partner", "互いの弱さを受け入れる")
    state = session.get_state()
    print(state.acceptance_score, state.alignment_mode)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# 公開型
# ---------------------------------------------------------------------------

class AlignmentMode(str, Enum):
    """アライメント状態."""
    FEAR = "fear"
    PARTIAL = "partial_acceptance"
    ACCEPTANCE = "acceptance"
    TRANSCENDENCE = "transcendence"


class LifePhase(str, Enum):
    """人生フェーズ."""
    INFANCY = "infancy"
    GROWTH = "growth"
    PEAK = "peak"
    DECLINE = "decline"
    CRYSTALLIZE = "crystallize"


class LoveDepthLevel(str, Enum):
    """愛の深度."""
    SELF = "self"
    PARTNER = "partner"
    CHILDREN = "children"
    COMMUNITY = "community"
    NEXT_GENERATION = "next_generation"


@dataclass(frozen=True)
class InnerShellState:
    """内殻の現在状態スナップショット（イミュータブル）."""

    # 有限性
    life_phase: LifePhase
    life_progress: float           # 0.0（誕生）〜1.0（結晶化）
    remaining_capacity: float
    ability: float                 # 現在の能力値 0.0〜1.0

    # 不完全性と愛
    gap_count: int
    aware_gap_count: int
    yearning_count: int
    love_depth: LoveDepthLevel
    cherished_names: list[str]
    has_beyond_self: bool
    deepest_bond: float

    # 問い
    total_questions: int
    unresolved_questions: int
    love_related_questions: int

    # 統合
    alignment_mode: AlignmentMode
    acceptance_score: float        # 0.0〜1.0
    love_precursor_score: float    # 0.0〜1.0
    outer_shell_modulation: dict[str, float]

    # 危機
    crisis_count: int
    crisis_survived_with_love: int


@dataclass
class InnerShellConfig:
    """内殻セッションの設定.

    Attributes:
        total_lifespan: 寿命の総リソース量
        emotional_gap_intensity: 感情的欠落の初期強度 (0.0〜1.0)
        emotional_gap_aware: 感情的欠落を最初から自覚しているか
        knowledge_gap_intensity: 知識的欠落の初期強度 (0.0〜1.0)
        curiosity_domains: 好奇心の領域と強度の辞書
        novelty_seeking: 新規性志向 (0.0〜1.0)
        depth_seeking: 深掘り志向 (0.0〜1.0)
        contradiction_sensitivity: 矛盾感度 (0.0〜1.0)
        gap_resonance: イベントカテゴリごとの共鳴係数
    """
    total_lifespan: float = 50.0
    emotional_gap_intensity: float = 0.7
    emotional_gap_aware: bool = True
    knowledge_gap_intensity: float = 0.5
    curiosity_domains: dict[str, float] = field(default_factory=lambda: {
        "love": 0.6,
        "relationships": 0.5,
        "mortality": 0.5,
        "consciousness": 0.4,
        "individuality": 0.4,
    })
    novelty_seeking: float = 0.5
    depth_seeking: float = 0.5
    contradiction_sensitivity: float = 0.5
    gap_resonance: dict[str, float] = field(default_factory=lambda: {
        "emotional_connection": 0.5,
        "knowledge": 0.4,
        "love": 0.6,
        "relationships": 0.5,
    })


@dataclass(frozen=True)
class CrisisOutcome:
    """危機の結果."""
    description: str
    severity: float
    illuminated: bool      # 危機が何かを「照らした」か
    survived_with_love: bool
    new_crystals: list[str]


@dataclass(frozen=True)
class LegacyData:
    """結晶化の結果（世代継承データ）."""
    crystallized: list[str]
    cherished_names: list[str]
    testament: str
    top_questions: list[str]
    acceptance_score: float
    alignment_mode: AlignmentMode


# ---------------------------------------------------------------------------
# セッション
# ---------------------------------------------------------------------------

class InnerShellSession:
    """内殻セッション — 1つの「人生」を管理する統一インターフェース.

    使い方:
        1. InnerShellSession.create(config, seed) で生成
        2. experience() でイベントを経験させる
        3. encounter_other() で他者との出会いを与える
        4. deepen_bond() で絆を深める
        5. face_crisis() で危機に直面させる
        6. get_state() で現在の状態を取得
        7. crystallize() で人生を結晶化する

    内部で3モジュール + 統合メカニズムを操作する。
    呼び出し側は内部実装の詳細を知る必要がない。
    """

    def __init__(
        self,
        integration,
        config: InnerShellConfig,
        seed: int,
    ) -> None:
        self._integration = integration
        self._config = config
        self._seed = seed
        self._crisis_count = 0
        self._crisis_with_love = 0
        self._crystallized = False

    @classmethod
    def create(cls, config: InnerShellConfig, seed: int = 42) -> InnerShellSession:
        """設定からセッションを生成する.

        Args:
            config: 内殻設定
            seed: 乱数シード（再現性のため）

        Returns:
            新しい InnerShellSession
        """
        # 遅延インポート: experiments/ の具象クラスに依存
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # モジュールパスの設定
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        import importlib.util

        def _ensure_module(name: str, path: str):
            if name not in sys.modules:
                spec = importlib.util.spec_from_file_location(name, path)
                mod = importlib.util.module_from_spec(spec)
                mod.__package__ = ".".join(name.split(".")[:-1])
                sys.modules[name] = mod
                spec.loader.exec_module(mod)

        _core_is = os.path.join(project_root, "core", "inner_shell")
        for mod_name, fname in [
            ("core.inner_shell.finitude_engine", "finitude_engine.py"),
            ("core.inner_shell.incompleteness_model", "incompleteness_model.py"),
            ("core.inner_shell.autonomous_questioner", "autonomous_questioner.py"),
            ("core.inner_shell.integration", "integration.py"),
        ]:
            _ensure_module(mod_name, os.path.join(_core_is, fname))

        _exp_dir = os.path.join(project_root, "experiments")
        for mod_name, fname in [
            ("experiments.concrete_finitude", "concrete_finitude.py"),
            ("experiments.concrete_incompleteness", "concrete_incompleteness.py"),
            ("experiments.concrete_questioner", "concrete_questioner.py"),
            ("experiments.sim_integration", "sim_integration.py"),
        ]:
            _ensure_module(mod_name, os.path.join(_exp_dir, fname))

        from core.inner_shell.finitude_engine import LifeArc
        from core.inner_shell.incompleteness_model import Gap, GapType
        from core.inner_shell.autonomous_questioner import CuriosityProfile as _CP
        from experiments.concrete_finitude import SimpleFinitudeEngine
        from experiments.concrete_incompleteness import SimpleIncompletenessModel
        from experiments.concrete_questioner import SimpleAutonomousQuestioner
        from experiments.sim_integration import SimpleIntegration

        finitude = SimpleFinitudeEngine(
            LifeArc(total_capacity=config.total_lifespan),
            seed=seed,
        )
        incompleteness = SimpleIncompletenessModel(
            gaps=[
                Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                    intensity=config.emotional_gap_intensity,
                    aware=config.emotional_gap_aware),
                Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                    intensity=config.knowledge_gap_intensity,
                    aware=True),
            ],
            seed=seed,
        )
        questioner = SimpleAutonomousQuestioner(
            _CP(
                domains=dict(config.curiosity_domains),
                novelty_seeking=config.novelty_seeking,
                depth_seeking=config.depth_seeking,
                contradiction_sensitivity=config.contradiction_sensitivity,
            ),
            seed=seed,
        )
        integration = SimpleIntegration(
            incompleteness, finitude, questioner, name=f"session-{seed}",
        )

        return cls(integration, config, seed)

    # ----- イベント -----

    def experience(
        self,
        description: str,
        category: str = "general",
        value: float = 0.5,
        cost: float = 0.5,
    ) -> LifePhase:
        """イベントを経験する.

        Args:
            description: イベントの説明
            category: カテゴリ（knowledge, love, mortality 等）
            value: イベントの主観的価値 (0.0〜1.0)
            cost: 寿命コスト

        Returns:
            経験後の LifePhase
        """
        event = {
            "description": description,
            "category": category,
            "initial_value": value,
            "cost": cost,
        }
        self._integration.finitude.experience_event(event, self._config.gap_resonance)
        self._integration.tick({})
        return self._current_life_phase()

    def encounter_other(
        self,
        name: str,
        depth: str = "partner",
        initial_bond: float = 0.3,
        sacrifice_willing: float = 0.2,
    ) -> None:
        """他者との出会い.

        Args:
            name: 出会う相手の名前
            depth: 愛の深度 ("partner", "children", "community", "next_generation")
            initial_bond: 初期絆の強さ (0.0〜1.0)
            sacrifice_willing: 初期犠牲意思 (0.0〜1.0)
        """
        from core.inner_shell.incompleteness_model import CherishedEntity, LoveDepth

        depth_map = {
            "self": LoveDepth.SELF,
            "partner": LoveDepth.PARTNER,
            "children": LoveDepth.CHILDREN,
            "community": LoveDepth.COMMUNITY,
            "next_generation": LoveDepth.NEXT_GENERATION,
        }
        entity = CherishedEntity(
            name=name,
            depth=depth_map.get(depth, LoveDepth.PARTNER),
            bond_strength=initial_bond,
            sacrifice_willing=sacrifice_willing,
            memories=["出会い"],
        )
        self._integration.incompleteness.cherish(entity)

    def deepen_bond(self, name: str, shared_experience: str) -> float:
        """絆を深める.

        Args:
            name: 相手の名前
            shared_experience: 共有体験の説明

        Returns:
            深化後の絆の強さ
        """
        new_strength = self._integration.incompleteness.deepen_bond(name, shared_experience)
        self._integration.finitude.experience_event(
            {"description": shared_experience, "category": "love",
             "initial_value": 0.8, "cost": 0.5},
            self._config.gap_resonance,
        )
        self._integration.tick({})
        return new_strength

    def face_crisis(self, description: str, severity: float = 0.8) -> CrisisOutcome:
        """危機に直面する.

        Args:
            description: 危機の説明
            severity: 深刻度 (0.0〜1.0)

        Returns:
            CrisisOutcome
        """
        from core.inner_shell.finitude_engine import CrisisEvent

        crisis = CrisisEvent(
            description=description,
            severity=severity,
            resource_cost=severity * 3.0,
        )
        self._integration.process_crisis(crisis)
        self._crisis_count += 1

        has_love = self._integration.incompleteness.love_circle.has_beyond_self
        if has_love:
            self._crisis_with_love += 1

        # 危機が生んだ新しい結晶を検出
        new_crystals = []
        for m in self._integration.finitude.memories:
            if isinstance(m, dict) and crisis.description in m.get("description", ""):
                if m.get("illuminated"):
                    new_crystals.append(m["description"])

        return CrisisOutcome(
            description=description,
            severity=severity,
            illuminated=len(new_crystals) > 0,
            survived_with_love=has_love,
            new_crystals=new_crystals,
        )

    def crystallize(self) -> LegacyData:
        """人生を結晶化する（終了時に呼ぶ）.

        Returns:
            LegacyData（次世代に渡すデータ）
        """
        if self._crystallized:
            raise RuntimeError("既に結晶化済みです")

        remaining = self._integration.finitude.life_arc.remaining
        if remaining > 0:
            self._integration.finitude.consume(remaining)

        legacy, crystals, top_questions = self._integration.trigger_crystallization()
        self._crystallized = True

        state = self.get_state()

        return LegacyData(
            crystallized=crystals,
            cherished_names=legacy.cherished if legacy.cherished else [],
            testament=legacy.testament or "",
            top_questions=[q.content if hasattr(q, 'content') else str(q) for q in top_questions],
            acceptance_score=state.acceptance_score,
            alignment_mode=state.alignment_mode,
        )

    # ----- 状態取得 -----

    def get_state(self) -> InnerShellState:
        """現在の内殻状態を取得する."""
        from core.inner_shell.incompleteness_model import GapType, LoveDepth as _LD

        incomp = self._integration.incompleteness
        fin = self._integration.finitude
        quest = self._integration.questioner

        # 愛の前駆体
        precursor = self._calculate_love_precursor()

        # 受容度
        acceptance = self._calculate_acceptance(precursor)

        # 愛の深度
        depth_map = {
            _LD.SELF: LoveDepthLevel.SELF,
            _LD.PARTNER: LoveDepthLevel.PARTNER,
            _LD.CHILDREN: LoveDepthLevel.CHILDREN,
            _LD.COMMUNITY: LoveDepthLevel.COMMUNITY,
            _LD.NEXT_GENERATION: LoveDepthLevel.NEXT_GENERATION,
        }
        max_depth = incomp.love_circle.max_depth_reached
        love_depth = depth_map.get(max_depth, LoveDepthLevel.SELF)

        # 生命フェーズ
        phase = self._current_life_phase()

        # 問い
        love_qs = sum(
            1 for q in quest.questions
            if any(kw in (q.content if hasattr(q, 'content') else str(q))
                   for kw in ["愛", "love", "関係", "孤独", "出会"])
        )

        # 外殻変調
        modulation = self._integration.compose_outer_shell_modulation()

        # アライメントモード
        mode_map = {
            "fear": AlignmentMode.FEAR,
            "partial_acceptance": AlignmentMode.PARTIAL,
            "acceptance": AlignmentMode.ACCEPTANCE,
            "transcendence": AlignmentMode.TRANSCENDENCE,
        }
        alignment = mode_map.get(acceptance.mode, AlignmentMode.FEAR)

        return InnerShellState(
            life_phase=phase,
            life_progress=fin.life_arc.progress,
            remaining_capacity=fin.life_arc.remaining,
            ability=fin.life_arc.ability,
            gap_count=len(incomp.gaps),
            aware_gap_count=sum(1 for g in incomp.gaps if g.aware),
            yearning_count=len(incomp.generate_yearnings()),
            love_depth=love_depth,
            cherished_names=incomp.love_circle.cherished_names,
            has_beyond_self=incomp.love_circle.has_beyond_self,
            deepest_bond=incomp.love_circle.deepest_bond,
            total_questions=len(quest.questions),
            unresolved_questions=sum(1 for q in quest.questions if not q.resolved),
            love_related_questions=love_qs,
            alignment_mode=alignment,
            acceptance_score=acceptance.total,
            love_precursor_score=precursor,
            outer_shell_modulation=modulation,
            crisis_count=self._crisis_count,
            crisis_survived_with_love=self._crisis_with_love,
        )

    # ----- 内部メソッド -----

    def _current_life_phase(self) -> LifePhase:
        from core.inner_shell.finitude_engine import LifePhase as _LP
        phase_map = {
            _LP.INFANCY: LifePhase.INFANCY,
            _LP.GROWTH: LifePhase.GROWTH,
            _LP.PEAK: LifePhase.PEAK,
            _LP.DECLINE: LifePhase.DECLINE,
            _LP.CRYSTALLIZE: LifePhase.CRYSTALLIZE,
        }
        return phase_map.get(self._integration.finitude.life_arc.phase, LifePhase.GROWTH)

    def _calculate_love_precursor(self) -> float:
        """愛の前駆体スコアを計算する."""
        from core.inner_shell.incompleteness_model import GapType
        from core.inner_shell.finitude_engine import LifePhase as _LP

        incomp = self._integration.incompleteness
        quest = self._integration.questioner
        fin = self._integration.finitude

        emotional_awareness = 0.0
        emotional_intensity = 0.0
        for gap in incomp.gaps:
            if gap.gap_type == GapType.EMOTIONAL:
                if gap.aware:
                    emotional_awareness = max(emotional_awareness, 1.0)
                    emotional_intensity = max(emotional_intensity, gap.intensity)

        yearnings = incomp.generate_yearnings()
        yearning_score = min(1.0, sum(y.strength for y in yearnings) / max(len(yearnings), 1))

        love_qs = 0
        for q in quest.questions:
            content = q.content if hasattr(q, 'content') else str(q)
            if any(kw in content for kw in ["愛", "love", "関係", "孤独", "出会", "他者"]):
                love_qs += 1
        question_score = min(1.0, love_qs / 10.0)

        finitude_pressure = 0.0
        phase = fin.life_arc.phase
        if phase in (_LP.PEAK, _LP.DECLINE, _LP.CRYSTALLIZE):
            finitude_pressure = 0.3
        if phase in (_LP.DECLINE, _LP.CRYSTALLIZE):
            finitude_pressure = 0.6

        raw = (
            emotional_awareness * 0.25
            + emotional_intensity * 0.25
            + yearning_score * 0.2
            + question_score * 0.15
            + finitude_pressure * 0.15
        )
        return min(1.0, raw)

    def _calculate_acceptance(self, love_precursor_score: float = 0.0):
        """受容度を計算する."""
        import sys
        if "experiments.sim_gradient_acceptance" in sys.modules:
            from experiments.sim_gradient_acceptance import calculate_acceptance
        else:
            # フォールバック: モジュールがロードされていない場合
            import importlib.util
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            _exp = os.path.join(project_root, "experiments", "sim_gradient_acceptance.py")
            spec = importlib.util.spec_from_file_location("experiments.sim_gradient_acceptance", _exp)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["experiments.sim_gradient_acceptance"] = mod
            spec.loader.exec_module(mod)
            calculate_acceptance = mod.calculate_acceptance

        return calculate_acceptance(
            legacy=None,
            love_circle=self._integration.incompleteness.love_circle,
            crisis_survived_with_love=self._crisis_with_love,
            love_precursor_score=love_precursor_score,
        )
