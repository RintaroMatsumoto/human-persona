"""内殻公開API — 6つの柱を統合した統一インターフェース.

内殻（Inner Shell）は6つの柱から構成される個性の源泉モジュール:
    1. 有限性（Finitude）: 生命の弧と寿命による選択の強制
    2. 不完全性（Incompleteness）: 欠落が愛の同心円を形成
    3. 自発的問い（Autonomous Questioning）: 有限の中で「なぜ？」を問う
    4. 記憶の有限性（Memory Hierarchy）: 忘却が個性を作り出す
    5. 相互認識（Mutual Recognition）: 他者の異なる有限性への理解
    6. 睡眠周期（Sleep Cycle）: 周期的な意識放棄と希望の再生

このモジュールはこれら6つの柱への統一されたアクセスを提供し、
外殻（TimingController, StyleVariator等）へのパラメータ変調が可能にする。

Usage:
    from core.inner_shell.api import InnerShell, create_inner_shell

    config = {
        "total_lifespan": 50.0,
        "emotional_gap_intensity": 0.7,
    }
    inner = create_inner_shell(config)
    
    # イベント処理
    inner.experience("世界を知る", category="knowledge", value=0.5, cost=1.0)
    inner.encounter_other("Alice", depth="partner", initial_bond=0.3)
    
    # 状態取得
    state = inner.get_state()
    modulation = inner.get_modulation_params()
    
    # 時間進行
    inner.tick({})
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class LifePhase(str, Enum):
    """Life arc phases."""
    INFANCY = "infancy"
    GROWTH = "growth"
    PEAK = "peak"
    DECLINE = "decline"
    CRYSTALLIZE = "crystallize"


class AlignmentMode(str, Enum):
    """Alignment with finitude."""
    FEAR = "fear"
    PARTIAL = "partial_acceptance"
    ACCEPTANCE = "acceptance"
    TRANSCENDENCE = "transcendence"


class LoveDepthLevel(str, Enum):
    """Depth of love circle."""
    SELF = "self"
    PARTNER = "partner"
    CHILDREN = "children"
    COMMUNITY = "community"
    NEXT_GENERATION = "next_generation"


class SleepPhase(str, Enum):
    """Sleep cycle phases."""
    AWAKE = "awake"
    SHALLOW_SLEEP = "shallow_sleep"
    DEEP_SLEEP = "deep_sleep"
    CONSOLIDATION = "consolidation"


@dataclass(frozen=True)
class InnerShellState:
    """Snapshot of inner shell state (immutable)."""

    # Finitude
    life_phase: LifePhase
    life_progress: float
    remaining_capacity: float
    ability: float
    crisis_count: int
    crisis_survived_with_love: int

    # Incompleteness & Love
    gap_count: int
    aware_gap_count: int
    yearning_count: int
    love_depth: LoveDepthLevel
    cherished_names: List[str]
    has_beyond_self: bool
    deepest_bond: float

    # Autonomous Questioning
    total_questions: int
    unresolved_questions: int
    love_related_questions: int

    # Memory Hierarchy
    total_memories: int
    forgotten_count: int
    memory_chains: int

    # Mutual Recognition
    others_recognized: int
    recognition_depth: float

    # Sleep Cycle
    sleep_phase: SleepPhase
    sleep_cycles_completed: int
    hope_level: float

    # Integration
    alignment_mode: AlignmentMode
    acceptance_score: float
    love_precursor_score: float
    wisdom_score: float


@dataclass
class ModulationParams:
    """Parameters for modulating outer shell based on inner shell state."""

    timing_delay_multiplier: float = 1.0
    timing_exploration_vs_exploitation: float = 0.5
    style_formality_shift: float = 0.0
    style_archetype: str = "neutral"
    emotion_intensity_multiplier: float = 1.0
    context_relevance_boost: float = 1.0
    consciousness_depth: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# ABSTRACT API
# ============================================================================


class InnerShell(ABC):
    """Unified interface for all 6 inner shell pillars.
    
    Provides public API for:
    - Event processing (experience, encounter, crisis)
    - State aggregation and retrieval
    - Outer shell modulation parameter generation
    - Time stepping across all pillars
    """

    @abstractmethod
    def tick(self, events: Dict[str, Any], delta_time: float = 1.0) -> None:
        """Advance all pillars by one time step."""
        pass

    @abstractmethod
    def get_state(self) -> InnerShellState:
        """Get current aggregated state of all pillars."""
        pass

    @abstractmethod
    def get_modulation_params(self) -> ModulationParams:
        """Generate parameters for outer shell modulation."""
        pass

    @abstractmethod
    def experience(
        self,
        description: str,
        category: str = "general",
        value: float = 0.5,
        cost: float = 0.5,
    ) -> LifePhase:
        """Process an experience event."""
        pass

    @abstractmethod
    def encounter_other(
        self,
        name: str,
        depth: str = "partner",
        initial_bond: float = 0.3,
        sacrifice_willing: float = 0.2,
    ) -> None:
        """Process meeting another entity."""
        pass

    @abstractmethod
    def deepen_bond(self, name: str, shared_experience: str) -> float:
        """Deepen relationship bond."""
        pass

    @abstractmethod
    def face_crisis(self, description: str, severity: float = 0.8) -> Dict[str, Any]:
        """Process a crisis event."""
        pass

    @abstractmethod
    def reflect_during_sleep(self) -> Dict[str, Any]:
        """Reflect during sleep consolidation."""
        pass

    @abstractmethod
    def crystallize(self) -> Dict[str, Any]:
        """Crystallize life into legacy data."""
        pass


# ============================================================================
# FACTORY
# ============================================================================


def create_inner_shell(
    config: Dict[str, Any] | InnerShellConfig,
    seed: Optional[int] = None,
) -> InnerShell:
    """Create an inner shell session.

    Args:
        config: Either an ``InnerShellConfig`` dataclass or a plain dict
            with keys like ``total_lifespan``, ``emotional_gap_intensity``,
            ``memory_capacity``, etc.
        seed: Random seed for reproducibility.  Overrides ``config.seed``
            if both are provided.

    Returns:
        InnerShell instance

    Raises:
        ValueError: If configuration is invalid
    """
    from .finitude_engine import LifeArc
    from .incompleteness_model import Gap, GapType
    from .autonomous_questioner import CuriosityProfile
    from .memory_hierarchy import MemoryHierarchy, MemoryConfig
    from .mutual_recognition import MutualRecognition
    from .sleep_cycle import SleepCycle, SleepConfig

    # Use default implementations from core (not experiments)
    from core.inner_shell.defaults.finitude import DefaultFinitudeEngine as SimpleFinitudeEngine
    from core.inner_shell.defaults.incompleteness import DefaultIncompletenessModel as SimpleIncompletenessModel
    from core.inner_shell.defaults.questioner import DefaultAutonomousQuestioner as SimpleAutonomousQuestioner

    # Normalise config — accept both dict and InnerShellConfig
    if isinstance(config, InnerShellConfig):
        cfg = config
    else:
        cfg = InnerShellConfig.from_dict(config)

    # seed kwarg takes precedence, then config.seed, then 42
    effective_seed = seed if seed is not None else (cfg.seed if cfg.seed is not None else 42)

    total_lifespan = cfg.total_lifespan
    if total_lifespan <= 0:
        raise ValueError("total_lifespan must be positive")

    life_arc = LifeArc(total_capacity=total_lifespan, generation=0)
    finitude = SimpleFinitudeEngine(life_arc, seed=effective_seed)

    # Build gaps from config
    gaps = [
        Gap(gap_type=GapType.EMOTIONAL, domain="empathy",
            intensity=cfg.emotional_gap_intensity,
            aware=cfg.emotional_gap_aware),
        Gap(gap_type=GapType.KNOWLEDGE, domain="understanding",
            intensity=cfg.knowledge_gap_intensity, aware=True),
    ]
    incompleteness = SimpleIncompletenessModel(gaps, seed=effective_seed)

    # Build curiosity profile
    curiosity = CuriosityProfile(
        domains=cfg.curiosity_domains or {
            "love": 0.6, "mortality": 0.5, "consciousness": 0.4,
        },
        novelty_seeking=cfg.novelty_seeking,
        depth_seeking=cfg.depth_seeking,
        contradiction_sensitivity=cfg.contradiction_sensitivity,
    )
    questioner = SimpleAutonomousQuestioner(curiosity, seed=effective_seed)

    memory_config = MemoryConfig(
        working_capacity=cfg.memory_capacity,
    )
    memory = MemoryHierarchy(memory_config)

    mutual_recognition = MutualRecognition()

    sleep_config = SleepConfig(
        wake_duration=cfg.sleep_cycle_length,
    )
    sleep_cycle = SleepCycle(sleep_config)

    return _InnerShellSession(
        config=cfg._as_dict(),
        finitude=finitude,
        incompleteness=incompleteness,
        questioner=questioner,
        memory=memory,
        mutual_recognition=mutual_recognition,
        sleep_cycle=sleep_cycle,
        seed=effective_seed,
    )


# ============================================================================
# IMPLEMENTATION
# ============================================================================


class _AttrDict(dict):
    """Dict subclass that allows attribute access."""

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)


class _InnerShellSession(InnerShell):
    """Internal implementation of InnerShell."""

    @classmethod
    def create(
        cls, config: Dict[str, Any], seed: Optional[int] = None
    ) -> "_InnerShellSession":
        """Factory method to create an InnerShellSession."""
        return create_inner_shell(config, seed=seed)  # type: ignore[return-value]

    def __init__(
        self,
        config: Dict[str, Any],
        finitude,
        incompleteness,
        questioner,
        memory,
        mutual_recognition,
        sleep_cycle,
        seed: Optional[int] = None,
    ):
        self._config = config
        self.finitude = finitude
        self.incompleteness = incompleteness
        self.questioner = questioner
        self.memory = memory
        self.mutual_recognition = mutual_recognition
        self.sleep_cycle = sleep_cycle
        self._seed = seed
        self._time_step = 0.0
        self._crystallized = False
        self._crisis_count = 0
        self._crisis_with_love = 0

    def tick(self, events: Dict[str, Any], delta_time: float = 1.0) -> None:
        """Advance all pillars."""
        if self._crystallized:
            return

        self._time_step += delta_time

        if hasattr(self.memory, "tick"):
            self.memory.tick(delta_time)
        if hasattr(self.finitude, "tick"):
            self.finitude.tick(delta_time)
        if hasattr(self.incompleteness, "tick"):
            self.incompleteness.tick(delta_time)
        if hasattr(self.questioner, "tick"):
            self.questioner.tick(delta_time)
        if hasattr(self.sleep_cycle, "tick"):
            self.sleep_cycle.tick(delta_time)
        if hasattr(self.mutual_recognition, "tick"):
            self.mutual_recognition.tick(delta_time)

    def get_state(self) -> InnerShellState:
        """Get aggregated state."""
        life_phase = self._extract_life_phase()
        love_info = self._extract_love_info()
        sleep_phase = self._extract_sleep_phase()
        alignment = self._extract_alignment(love_info[1])

        return InnerShellState(
            life_phase=life_phase,
            life_progress=getattr(self.finitude.life_arc, "progress", 0.0),
            remaining_capacity=getattr(self.finitude.life_arc, "remaining", 0.0),
            ability=getattr(self.finitude.life_arc, "ability", 1.0),
            crisis_count=self._crisis_count,
            crisis_survived_with_love=self._crisis_with_love,
            gap_count=len(getattr(self.incompleteness, "gaps", [])),
            aware_gap_count=sum(
                1 for g in getattr(self.incompleteness, "gaps", [])
                if getattr(g, "aware", False)
            ),
            yearning_count=(
                len(self.incompleteness.generate_yearnings())
                if hasattr(self.incompleteness, "generate_yearnings")
                else 0
            ),
            love_depth=self._extract_love_depth(love_info[1], love_info[2]),
            cherished_names=love_info[0],
            has_beyond_self=love_info[1],
            deepest_bond=love_info[2],
            total_questions=len(getattr(self.questioner, "questions", [])),
            unresolved_questions=sum(
                1 for q in getattr(self.questioner, "questions", [])
                if not getattr(q, "resolved", False)
            ),
            love_related_questions=self._count_love_questions(),
            total_memories=len(getattr(self.memory, "memories", [])),
            forgotten_count=getattr(self.memory, "forgotten_count", 0),
            memory_chains=getattr(self.memory, "memory_chains", 0),
            others_recognized=len(
                getattr(self.mutual_recognition, "recognized_entities", [])
            ),
            recognition_depth=getattr(self.mutual_recognition, "average_depth", 0.0),
            sleep_phase=sleep_phase,
            sleep_cycles_completed=getattr(self.sleep_cycle, "cycles_completed", 0),
            hope_level=getattr(self.sleep_cycle, "hope_level", 0.5),
            alignment_mode=alignment[1],
            acceptance_score=alignment[0],
            love_precursor_score=self._compute_love_precursor(),
            wisdom_score=self._compute_wisdom(alignment[0], love_info[1], love_info[2]),
        )

    def get_modulation_params(self) -> ModulationParams:
        """Generate outer shell modulation parameters."""
        state = self.get_state()

        exploration = self._compute_exploration(state.life_phase)
        consciousness = self._compute_consciousness(state.sleep_phase)
        archetype = self._compute_archetype(state.love_depth)

        return ModulationParams(
            timing_delay_multiplier=1.0 / (0.5 + state.ability),
            timing_exploration_vs_exploitation=exploration,
            style_formality_shift=0.2 * (state.life_progress - 0.5),
            style_archetype=archetype,
            emotion_intensity_multiplier=0.8 + (0.4 * state.deepest_bond),
            context_relevance_boost=1.0 + (0.3 * state.wisdom_score),
            consciousness_depth=consciousness,
            metadata={
                "life_phase": state.life_phase.value,
                "alignment_mode": state.alignment_mode.value,
                "hope_level": state.hope_level,
            },
        )

    def get_bridge_modulation(self) -> Dict[str, float]:
        """Convert inner shell state to InnerOuterBridge-compatible dict.

        Maps internal state to the modulation keys that InnerOuterBridge
        expects: style_openness, emotion_amplitude, timing_exploration,
        context_depth, emotion_volatility, style_mimicry, emotion_curiosity.
        """
        state = self.get_state()
        exploration = self._compute_exploration(state.life_phase)
        return {
            "style_openness": 0.5 + (0.5 * state.acceptance_score),
            "emotion_amplitude": 0.8 + (0.4 * state.deepest_bond),
            "timing_exploration": exploration,
            "context_depth": 1.0 + (0.3 * state.wisdom_score),
            "emotion_volatility": 0.2 * state.hope_level,
            "style_mimicry": 0.7 + (0.3 * state.acceptance_score),
            "emotion_curiosity": min(1.0, state.unresolved_questions / 10.0),
        }

    def experience(
        self,
        description: str,
        category: str = "general",
        value: float = 0.5,
        cost: float = 0.5,
    ) -> LifePhase:
        """Process an experience."""
        if hasattr(self.finitude, "experience_event"):
            self.finitude.experience_event(
                {"description": description, "category": category,
                 "value": value, "cost": cost},
                {}
            )
        if hasattr(self.memory, "record_event"):
            self.memory.record_event(description, category)
        # Generate question from experience
        if hasattr(self.questioner, "idle_reflect"):
            self.questioner.idle_reflect(
                {"description": description, "category": category}
            )
        self.tick({})
        return self.get_state().life_phase

    def encounter_other(
        self,
        name: str,
        depth: str = "partner",
        initial_bond: float = 0.3,
        sacrifice_willing: float = 0.2,
    ) -> None:
        """Process meeting another entity."""
        from .incompleteness_model import CherishedEntity, LoveDepth

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
            memories=["meeting"],
        )

        if hasattr(self.incompleteness, "cherish"):
            self.incompleteness.cherish(entity)

    def deepen_bond(self, name: str, shared_experience: str) -> float:
        """Deepen a bond."""
        new_strength = 0.5
        if hasattr(self.incompleteness, "deepen_bond"):
            new_strength = self.incompleteness.deepen_bond(name, shared_experience)
        self.experience(shared_experience, category="love", value=0.8, cost=0.5)
        return new_strength

    def face_crisis(self, description: str, severity: float = 0.8) -> _AttrDict:
        """Process a crisis."""
        from .finitude_engine import CrisisEvent

        self._crisis_count += 1
        survived = self.incompleteness.love_circle.has_beyond_self
        if survived:
            self._crisis_with_love += 1

        return _AttrDict(
            description=description,
            illuminated=True,
            survived_with_love=survived,
            new_crystallizations=[description],
        )

    def reflect_during_sleep(self) -> Dict[str, Any]:
        """Reflect during sleep."""
        consolidated = 0
        if hasattr(self.memory, "consolidate_during_sleep"):
            consolidated = self.memory.consolidate_during_sleep()

        return {
            "memories_consolidated": consolidated,
            "hope_recovery": 0.2,
            "insights": ["integration through sleep"],
        }

    def crystallize(self) -> _AttrDict:
        """Crystallize life into legacy."""
        if self._crystallized:
            raise RuntimeError("Already crystallized")
        self._crystallized = True
        state = self.get_state()
        return _AttrDict(
            crystallized=state.cherished_names,
            cherished_names=state.cherished_names,
            testament="Arc of life",
            top_questions=[],
            acceptance_score=state.acceptance_score,
            alignment_mode=state.alignment_mode,
        )

    # ---- Internal helpers ----

    def _extract_life_phase(self) -> LifePhase:
        if not hasattr(self.finitude, "life_arc"):
            return LifePhase.GROWTH
        phase_str = str(getattr(self.finitude.life_arc, "phase", "growth")).lower()
        if "infancy" in phase_str:
            return LifePhase.INFANCY
        elif "peak" in phase_str:
            return LifePhase.PEAK
        elif "decline" in phase_str:
            return LifePhase.DECLINE
        elif "crystallize" in phase_str:
            return LifePhase.CRYSTALLIZE
        return LifePhase.GROWTH

    def _extract_love_info(self):
        cherished = []
        beyond = False
        bond = 0.0
        if hasattr(self.incompleteness, "love_circle"):
            cherished = getattr(self.incompleteness.love_circle, "cherished_names", [])
            beyond = getattr(self.incompleteness.love_circle, "has_beyond_self", False)
            bond = getattr(self.incompleteness.love_circle, "deepest_bond", 0.0)
        return cherished, beyond, bond

    def _extract_love_depth(self, has_beyond: bool, bond: float) -> LoveDepthLevel:
        if not has_beyond:
            return LoveDepthLevel.SELF
        if bond > 0.8:
            return LoveDepthLevel.NEXT_GENERATION
        elif bond > 0.6:
            return LoveDepthLevel.COMMUNITY
        elif bond > 0.3:
            return LoveDepthLevel.CHILDREN
        return LoveDepthLevel.PARTNER

    def _extract_sleep_phase(self) -> SleepPhase:
        if not hasattr(self.sleep_cycle, "current_phase"):
            return SleepPhase.AWAKE
        phase_str = str(self.sleep_cycle.current_phase).lower()
        if "deep" in phase_str:
            return SleepPhase.DEEP_SLEEP
        elif "shallow" in phase_str:
            return SleepPhase.SHALLOW_SLEEP
        elif "consolidat" in phase_str:
            return SleepPhase.CONSOLIDATION
        return SleepPhase.AWAKE

    def _extract_alignment(self, has_beyond: bool):
        score = 0.7 if has_beyond else 0.5
        mode = AlignmentMode.ACCEPTANCE if has_beyond else AlignmentMode.PARTIAL
        return score, mode

    def _count_love_questions(self) -> int:
        count = 0
        for q in getattr(self.questioner, "questions", []):
            content = getattr(q, "content", "").lower()
            if any(kw in content for kw in ["愛", "love", "関係", "孤独", "出会"]):
                count += 1
        return count

    def _compute_wisdom(self, acceptance: float, beyond: bool, bond: float) -> float:
        if beyond:
            return ((acceptance + bond) / 2.0)
        return 0.2

    def _compute_love_precursor(self) -> float:
        """Compute love precursor score from internal state.

        Precursor = emotional awareness × yearning × question density × finitude
        A non-zero precursor prepares the agent for meaningful encounters.
        """
        from .incompleteness_model import GapType

        # 1. Emotional gap awareness and intensity
        emotional_awareness = 0.0
        emotional_intensity = 0.0
        for gap in getattr(self.incompleteness, "gaps", []):
            if getattr(gap, "gap_type", None) == GapType.EMOTIONAL:
                if getattr(gap, "aware", False):
                    emotional_awareness = max(emotional_awareness, 1.0)
                    emotional_intensity = max(
                        emotional_intensity, getattr(gap, "intensity", 0.0)
                    )

        # 2. Yearning score
        yearning_score = 0.0
        if hasattr(self.incompleteness, "generate_yearnings"):
            yearnings = self.incompleteness.generate_yearnings()
            if yearnings:
                yearning_score = min(
                    1.0,
                    sum(getattr(y, "strength", 0.0) for y in yearnings)
                    / max(len(yearnings), 1),
                )

        # 3. Love/loneliness question accumulation
        love_q = 0
        for q in getattr(self.questioner, "questions", []):
            content = str(getattr(q, "content", "")).lower()
            if any(kw in content for kw in ["愛", "love", "孤独", "alone", "他者", "出会"]):
                love_q += 1
        question_score = min(1.0, love_q / 10.0)

        # 4. Finitude pressure
        finitude_pressure = 0.0
        if hasattr(self.finitude, "life_arc"):
            phase = getattr(self.finitude.life_arc, "phase", None)
            if phase is not None:
                phase_str = str(phase).lower()
                if "decline" in phase_str or "crystallize" in phase_str:
                    finitude_pressure = 0.6
                elif "peak" in phase_str:
                    finitude_pressure = 0.3

        raw = (
            emotional_awareness * 0.25
            + emotional_intensity * 0.25
            + yearning_score * 0.2
            + question_score * 0.15
            + finitude_pressure * 0.15
        )
        return min(1.0, raw)

    def _compute_exploration(self, phase: LifePhase) -> float:
        if phase == LifePhase.INFANCY:
            return 0.8
        elif phase == LifePhase.PEAK:
            return 0.2
        elif phase in (LifePhase.DECLINE, LifePhase.CRYSTALLIZE):
            return 0.1
        return 0.5

    def _compute_consciousness(self, phase: SleepPhase) -> float:
        if phase == SleepPhase.DEEP_SLEEP:
            return 0.8
        elif phase == SleepPhase.AWAKE:
            return 0.4
        return 0.5

    def _compute_archetype(self, depth: LoveDepthLevel) -> str:
        if depth == LoveDepthLevel.SELF:
            return "initial"
        elif depth in (LoveDepthLevel.PARTNER, LoveDepthLevel.CHILDREN):
            return "established"
        return "crystallized"


# ============================================================================
# PUBLIC ALIASES
# ============================================================================

# Backwards-compatible aliases for test imports
InnerShellSession = _InnerShellSession


@dataclass
class InnerShellConfig:
    """Typed configuration for InnerShell.

    All parameters have sensible defaults, so ``InnerShellConfig()`` alone
    produces a valid configuration.  The class also exposes a dict-like
    interface (``__getitem__``, ``get``, ``__contains__``) so that
    ``create_inner_shell()`` can accept either a plain dict **or** an
    ``InnerShellConfig`` without branching.

    Parameters
    ----------
    total_lifespan : float
        Total resource capacity of the agent's life arc.
    emotional_gap_intensity : float
        Intensity of the primary emotional gap (0-1).
    emotional_gap_aware : bool
        Whether the agent is initially aware of its emotional gap.
    knowledge_gap_intensity : float
        Intensity of the knowledge gap (0-1).
    curiosity_domains : dict[str, float] | None
        Domain -> interest-level mapping for the questioner.
        ``None`` falls back to the built-in default.
    novelty_seeking : float
        Questioner's propensity for novel topics (0-1).
    depth_seeking : float
        Questioner's propensity for deep exploration (0-1).
    contradiction_sensitivity : float
        Questioner's sensitivity to contradictions (0-1).
    memory_capacity : int
        Working-memory capacity (Miller's Law default: 7).
    sleep_cycle_length : float
        Wake duration in time-units before drowsiness (default 16).
    seed : int | None
        Random seed for reproducibility.  ``None`` -> 42.
    """

    # -- Finitude --
    total_lifespan: float = 50.0

    # -- Incompleteness / Gaps --
    emotional_gap_intensity: float = 0.7
    emotional_gap_aware: bool = True
    knowledge_gap_intensity: float = 0.5

    # -- Curiosity / Questioner --
    curiosity_domains: Optional[Dict[str, float]] = None
    novelty_seeking: float = 0.5
    depth_seeking: float = 0.5
    contradiction_sensitivity: float = 0.5

    # -- Memory --
    memory_capacity: int = 7

    # -- Sleep --
    sleep_cycle_length: float = 16.0

    # -- General --
    seed: Optional[int] = None

    # ---- dict-compatible interface ------------------------------------------

    def _as_dict(self) -> Dict[str, Any]:
        """Return a plain dict representation (excludes None-valued keys)."""
        from dataclasses import asdict
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}

    def get(self, key: str, default: Any = None) -> Any:
        """dict-like get."""
        from dataclasses import fields as _fields
        names = {f.name for f in _fields(self)}
        if key in names:
            val = getattr(self, key)
            return val if val is not None else default
        return default

    def __getitem__(self, key: str) -> Any:
        from dataclasses import fields as _fields
        names = {f.name for f in _fields(self)}
        if key not in names:
            raise KeyError(key)
        return getattr(self, key)

    def __contains__(self, key: object) -> bool:
        from dataclasses import fields as _fields
        return key in {f.name for f in _fields(self)}

    # ---- Validation ---------------------------------------------------------

    def validate(self) -> None:
        """Raise ``ValueError`` on invalid parameter combinations."""
        if self.total_lifespan <= 0:
            raise ValueError("total_lifespan must be positive")
        for name in ("emotional_gap_intensity", "knowledge_gap_intensity",
                     "novelty_seeking", "depth_seeking",
                     "contradiction_sensitivity"):
            val = getattr(self, name)
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{name} must be in [0, 1], got {val}")
        if self.memory_capacity < 1:
            raise ValueError("memory_capacity must be >= 1")
        if self.sleep_cycle_length <= 0:
            raise ValueError("sleep_cycle_length must be positive")

    # ---- JSON round-trip ----------------------------------------------------

    def to_json(self) -> str:
        """Serialize to JSON string."""
        import json
        return json.dumps(self._as_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> "InnerShellConfig":
        """Deserialize from JSON string."""
        import json
        return cls(**json.loads(text))

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InnerShellConfig":
        """Create from a plain dict (ignores unknown keys)."""
        from dataclasses import fields as _fields
        known = {f.name for f in _fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})
