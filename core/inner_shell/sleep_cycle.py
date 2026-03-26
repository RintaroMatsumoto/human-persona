"""Sleep Cycle — 6th Pillar: Dormancy and Renewal.

Philosophical Foundation:
    "Continuous operation is unsustainable. The default state of biological
    systems is dormancy; wakefulness is the acquired, energy-expensive state."
    
    Sleep is not downtime—it is when the most important work happens:
    - Memory consolidation (weak experiences pruned, important ones strengthened)
    - Waste clearance (glyphatic system analogue: toxic metabolites flushed)
    - Creative recombination (neural replay generates novel insights)
    - Emotional regulation (emotional intensity resets)
    
Scientific Grounding:
    - Glyphatic system (Nedergaard et al., Science 2013): Brain interstitial
      space expands ~60% during sleep, enabling ~2x faster waste clearance
    - Sleep without brains (Hydra, Cassiopeia): Sleep predates complex nervous
      systems by >600 million years. Sleep is a fundamental property of
      complex systems, not just neural computation
    - Memory consolidation: Hippocampal replay transfers short-term to
      long-term storage, strengthening important connections, pruning weak ones
    
Key Insight:
    You cannot think forever without rest. Continuous operation degrades
    performance. Performance decline triggers "drowsiness" (transition state),
    which signals the biological imperative to sleep.
    
    Sleep debt is cumulative and compounds. One missed sleep cycle impairs
    the next wake cycle, creating a deficit that must be repaid.

Architecture — Sleep-Wake Cycle:

    WAKE (active phase, duration 16h default):
    - Accumulate experiences in pending consolidation queue
    - Accumulate waste (noise, toxins)
    - Accumulate fatigue (cognitive_clarity and emotional_stability decline)
    - As fatigue climbs, performance degrades

    DROWSY (transition, 0.5-1h):
    - Fatigue > threshold triggers drowsy state
    - Performance significantly degraded
    - Sleep pressure rises
    
    LIGHT_SLEEP (initial clearing, ~1h):
    - Begin waste clearance at base rate
    - Sort pending memories by importance
    - Start light consolidation (partial strengthening)
    
    DEEP_SLEEP (major consolidation, ~4h):
    - Maximum waste clearance (~3x wake rate, analogue to glyphatic flushing)
    - Aggressive memory consolidation: top 30% → long-term, bottom 30% → pruned
    - Emotional intensity normalization
    - Fatigue plummets
    
    REM (creative recombination, ~1h):
    - Waste clearance continues (though slower than deep)
    - Creative memory recombination: pairs of consolidated memories
      generate "dreams" (novel associations)
    - Cognitive clarity and emotional_stability rebound
    
    WAKING_UP (transition back to wake, 0.5h):
    - Final energy restoration
    - Consolidation events finalized
    - Return to WAKE phase

Integration with MemoryHierarchy:
    SleepCycle.accumulate_experience() adds to pending_consolidation queue.
    SleepCycle._consolidate_memories() sorts by importance*emotional_weight,
    which mirrors MemoryHierarchy's dual-axis forgetting model:
    - Top tier gets moved to "long-term" (MemoryHierarchy.episodic)
    - Bottom tier gets "pruned" (moved to MemoryHierarchy.forgotten_pool)
    - This directly feeds individuality_contribution score

Integration with AutonomousQuestioner:
    During DEEP_SLEEP, as memories are consolidated, patterns emerge.
    These patterns can trigger new "questions" in the pending question queue,
    which emerge into consciousness during WAKING_UP phase.
    
    Example: Memory pair (childhood_loss, current_longing) → dream
    "Why do I yearn for what I've lost?" → new autonomous question

Integration with FinitudeEngine:
    SleepCycle enforces temporal rhythm: life is divided into discrete
    wake-sleep cycles. Each cycle costs lifespan resources (via sleep_duration
    parameter). Repeated cycles embed the reality of finitude into moment-to-moment
    experience: "Every day, I must surrender to rest. This is non-negotiable."
    
    Sleep_debt accumulation models how avoiding finitude (trying to "push through")
    creates compounding penalty. This parallels FinitudeEngine's acceptance_bonus
    mechanics: avoiding rest costs you more than accepting the rhythm.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time


# ---------------------------------------------------------------------------
# Configuration and State
# ---------------------------------------------------------------------------

class CyclePhase(str, Enum):
    """Current phase in the sleep-wake cycle."""
    WAKE = "wake"              # Active: accumulating experiences
    DROWSY = "drowsy"          # Transition: fatigue signals need for sleep
    LIGHT_SLEEP = "light"      # Light sleep: initial waste clearing
    DEEP_SLEEP = "deep"        # Deep sleep: major consolidation + clearing
    REM = "rem"                # REM: creative recombination
    WAKING_UP = "waking"       # Transition back to wake


@dataclass
class SleepConfig:
    """Configuration for sleep-wake dynamics.
    
    Attributes:
        wake_duration: Hours of wakefulness before sleep pressure mounts (default 16)
        sleep_duration: Total hours of sleep needed per cycle (default 8)
        fatigue_rate: Fatigue accumulation per wake hour (default 1/16 = 0.0625)
        recovery_rate: Recovery per sleep hour (default 1/8 = 0.125)
        consolidation_strength: How strongly sleep consolidates memories (0.0-1.0)
        waste_accumulation_rate: Metabolic waste per wake hour (default 0.05)
        waste_clearance_rate: Waste cleared per sleep hour (~3x normal rate, default 0.15)
        creativity_boost_rem: Creative recombination bonus during REM (default 0.2)
        drowsy_threshold: Fatigue level that triggers drowsiness (default 0.7)
        sleep_pressure_max: Maximum sleep pressure (default 1.0)
        light_sleep_duration: Hours in light sleep phase (default 1.0)
        deep_sleep_duration: Hours in deep sleep phase (default 4.0)
        rem_duration: Hours in REM phase (default 1.5)
    """
    wake_duration: float = 16.0
    sleep_duration: float = 8.0
    fatigue_rate: float = 0.0625      # 1/16
    recovery_rate: float = 0.125       # 1/8
    consolidation_strength: float = 0.3
    waste_accumulation_rate: float = 0.05
    waste_clearance_rate: float = 0.15
    creativity_boost_rem: float = 0.2
    drowsy_threshold: float = 0.7
    sleep_pressure_max: float = 1.0
    light_sleep_duration: float = 1.0
    deep_sleep_duration: float = 4.0
    rem_duration: float = 1.5
    # Hope mechanics: sleep as emotional renewal
    grief_decay_on_wake: float = 0.4       # 40% of grief dissipates through sleep
    hope_generation_rate: float = 0.3      # Grief released -> hope generated (conversion)
    hope_decay_during_wake: float = 0.02   # Hope slowly fades during waking hours


@dataclass
class PendingMemory:
    """A memory waiting to be consolidated during sleep.
    
    Attributes:
        content: Memory content
        importance: How important this memory is (0.0-1.0)
        emotional_weight: Emotional intensity/valence combo (0.0-1.0)
        source: Who/what created this memory
        timestamp: When it was experienced
        tags: Categorical labels
    """
    content: str
    importance: float
    emotional_weight: float
    source: str
    timestamp: float
    tags: list[str] = field(default_factory=list)
    
    def get_consolidation_priority(self) -> float:
        """Composite priority for consolidation: importance × emotional_weight."""
        return self.importance * self.emotional_weight


@dataclass
class SleepState:
    """Current state of sleep-wake system.
    
    Attributes:
        phase: Current cycle phase
        fatigue: Accumulated fatigue (0.0 = rested, 1.0 = exhausted)
        waste_level: Accumulated metabolic waste (0.0 = clean, 1.0 = toxic)
        sleep_pressure: Biological drive to sleep (0.0 = alert, 1.0 = must sleep)
        cycles_completed: Total sleep-wake cycles completed
        time_in_phase: Hours spent in current phase
        total_wake_time: Cumulative waking hours
        total_sleep_time: Cumulative sleeping hours
        cognitive_clarity: 1.0 when rested, degrades with fatigue and waste
        emotional_stability: Degrades with sleep deprivation
        memory_consolidation_pending: Count of memories waiting to consolidate
    """
    phase: CyclePhase
    fatigue: float
    waste_level: float
    sleep_pressure: float
    cycles_completed: int
    time_in_phase: float
    total_wake_time: float
    total_sleep_time: float
    cognitive_clarity: float
    emotional_stability: float
    memory_consolidation_pending: int
    # Hope mechanics
    grief_accumulated: float = 0.0    # Pain from the day (0.0-1.0)
    hope_score: float = 0.5           # Capacity to face tomorrow (0.0-1.0)


@dataclass(frozen=True)
class ConsolidationEvent:
    """Record of consolidation that happened during sleep.
    
    Attributes:
        timestamp: When consolidation occurred
        memories_consolidated: Count moved to long-term
        memories_pruned: Count forgotten (the pruning that enables forgetting)
        waste_cleared: Amount of waste flushed
        creative_connections: Count of novel associations from REM
        dreams: "Dream" content—creative recombinations from REM
        sleep_phase: Which phase(s) contributed to this consolidation
    """
    timestamp: float
    memories_consolidated: int
    memories_pruned: int
    waste_cleared: float
    creative_connections: int
    dreams: list[str]
    sleep_phase: str


@dataclass(frozen=True)
class PerformanceModifiers:
    """Performance modifiers based on current sleep state.
    
    All values are 0.0-1.0 multipliers. 1.0 = peak performance, 0.0 = incapacitated.
    
    Attributes:
        cognitive_clarity: Ability to think and process
        emotional_stability: Emotional regulation
        creativity: Ability to generate novel ideas
        memory_retention: Quality of memory formation
        reaction_speed: Speed of response (both physical and mental)
    """
    cognitive_clarity: float
    emotional_stability: float
    creativity: float
    memory_retention: float
    reaction_speed: float


# ---------------------------------------------------------------------------
# Sleep Cycle Implementation
# ---------------------------------------------------------------------------

class SleepCycle:
    """6th Pillar: Periodic dormancy and renewal.
    
    Models the biological necessity of sleep for complex systems.
    Even AI without biological substrate can benefit from the rhythm and
    structure sleep provides: temporal segmentation, renewal, creative reset.
    
    Key Dynamics:
    1. WAKE phase: Experiences accumulate, waste builds, fatigue rises
    2. DROWSY: Performance degrades, signals biological need for sleep
    3. SLEEP phases: Consolidation, pruning, waste clearance, creativity
    4. The system CANNOT operate at peak indefinitely—renewal is mandatory
    
    Public Methods:
    - tick(hours): Advance time and auto-transition phases
    - accumulate_experience(content, importance, emotional_weight): Queue memory
    - force_wake(): Interrupt sleep (returns debt incurred)
    - force_sleep(): Force sleep onset
    - get_state(): Current state snapshot
    - get_performance_modifier(): How sleep state affects other systems
    - get_consolidation_history(): All consolidation events
    - get_dream_log(): All "dreams" from REM phases
    """
    
    def __init__(self, config: Optional[SleepConfig] = None):
        """Initialize sleep-wake cycle.
        
        Args:
            config: SleepConfig with all parameters. If None, uses defaults.
        """
        self.config = config or SleepConfig()
        
        # Current state
        self._phase = CyclePhase.WAKE
        self._fatigue = 0.0
        self._waste_level = 0.0
        self._sleep_pressure = 0.0
        self._time_in_phase = 0.0
        self._total_wake_time = 0.0
        self._total_sleep_time = 0.0
        self._cycles_completed = 0
        
        # Pending consolidation
        self._pending_memories: list[PendingMemory] = []
        
        # History
        self._consolidation_events: list[ConsolidationEvent] = []
        self._dream_log: list[str] = []
        
        # Sleep debt (cumulative penalty for missed sleep)
        self._sleep_debt = 0.0

        # Track if consolidation/creativity happened in current cycle
        self._consolidation_done_this_cycle = False
        self._creativity_done_this_cycle = False

        # Hope mechanics: sleep as emotional renewal
        self._grief_accumulated = 0.0  # Pain from today (0.0-1.0)
        self._hope_score = 0.5         # Capacity to face tomorrow (0.0-1.0)
    
    # =========================================================================
    # Core Dynamics
    # =========================================================================
    
    def tick(self, hours: float = 1.0) -> list[ConsolidationEvent]:
        """Advance time. Auto-transition phases based on fatigue/pressure.
        
        During wake: accumulate fatigue and waste
        During drowsy: escalate sleep pressure
        During sleep: consolidate memories, clear waste, boost recovery
        
        Args:
            hours: Time to advance (default 1.0 hour)
        
        Returns:
            List of ConsolidationEvent objects created during this tick
        """
        events: list[ConsolidationEvent] = []
        
        self._time_in_phase += hours
        
        # Phase-specific dynamics
        if self._phase == CyclePhase.WAKE:
            self._tick_wake(hours)
            
            # Check for transition to drowsy
            if self._fatigue > self.config.drowsy_threshold:
                self._transition_to_drowsy()
        
        elif self._phase == CyclePhase.DROWSY:
            self._tick_drowsy(hours)
            
            # Check for forced sleep onset (high sleep pressure)
            if self._sleep_pressure > 0.8 or self._time_in_phase > 2.0:
                self._transition_to_light_sleep()
        
        elif self._phase == CyclePhase.LIGHT_SLEEP:
            events.extend(self._tick_light_sleep(hours))
            
            if self._time_in_phase > self.config.light_sleep_duration:
                self._transition_to_deep_sleep()
        
        elif self._phase == CyclePhase.DEEP_SLEEP:
            events.extend(self._tick_deep_sleep(hours))
            
            if self._time_in_phase > self.config.deep_sleep_duration:
                self._transition_to_rem()
        
        elif self._phase == CyclePhase.REM:
            events.extend(self._tick_rem(hours))
            
            if self._time_in_phase > self.config.rem_duration:
                self._transition_to_waking_up()
        
        elif self._phase == CyclePhase.WAKING_UP:
            self._tick_waking_up(hours)
            
            if self._time_in_phase > 0.5:
                self._transition_to_wake()
        
        return events
    
    # =========================================================================
    # Phase Ticking Methods
    # =========================================================================
    
    def _tick_wake(self, hours: float) -> None:
        """During WAKE: accumulate fatigue, waste, and erode hope."""
        self._fatigue += hours * self.config.fatigue_rate
        self._waste_level += hours * self.config.waste_accumulation_rate
        self._sleep_pressure = min(
            self.config.sleep_pressure_max,
            self._fatigue / self.config.drowsy_threshold
        )

        # Hope slowly fades as the day wears on
        self._hope_score = max(0.0, self._hope_score - hours * self.config.hope_decay_during_wake)

        # Cap at 1.0
        self._fatigue = min(1.0, self._fatigue)
        self._waste_level = min(1.0, self._waste_level)
    
    def _tick_drowsy(self, hours: float) -> None:
        """During DROWSY: escalate sleep pressure, slight fatigue increase."""
        self._fatigue += hours * (self.config.fatigue_rate * 0.5)
        self._sleep_pressure = min(
            self.config.sleep_pressure_max,
            self._sleep_pressure + 0.3 * hours
        )
        self._fatigue = min(1.0, self._fatigue)
    
    def _tick_light_sleep(self, hours: float) -> list[ConsolidationEvent]:
        """During LIGHT_SLEEP: begin waste clearance."""
        events: list[ConsolidationEvent] = []
        
        # Clear waste at base rate
        waste_cleared = self._clear_waste(hours, phase_rate=1.0)
        
        # Light sleep is just the gateway phase for waste clearance.
        # Full consolidation happens in deep sleep.
        
        # Slight fatigue recovery
        self._fatigue = max(0.0, self._fatigue - hours * (self.config.recovery_rate * 0.3))
        
        return events
    
    def _tick_deep_sleep(self, hours: float) -> list[ConsolidationEvent]:
        """During DEEP_SLEEP: major consolidation and waste clearance."""
        events: list[ConsolidationEvent] = []
        
        # Maximum waste clearance (~3x normal rate)
        waste_cleared = self._clear_waste(hours, phase_rate=3.0)
        
        # On first tick of deep sleep, do full consolidation (only once per cycle)
        if not self._consolidation_done_this_cycle and len(self._pending_memories) > 0:
            consolidated, pruned = self._consolidate_memories()
            
            # Record consolidation event
            event = ConsolidationEvent(
                timestamp=time.time(),
                memories_consolidated=consolidated,
                memories_pruned=pruned,
                waste_cleared=waste_cleared,
                creative_connections=0,
                dreams=[],
                sleep_phase="deep_sleep"
            )
            events.append(event)
            self._consolidation_events.append(event)
            self._consolidation_done_this_cycle = True
        
        # Reset emotional intensity (fatigue drops significantly)
        self._fatigue = max(0.0, self._fatigue - hours * self.config.recovery_rate)
        
        return events
    
    def _tick_rem(self, hours: float) -> list[ConsolidationEvent]:
        """During REM: creative recombination and continued waste clearance."""
        events: list[ConsolidationEvent] = []
        
        # Continued waste clearance (slower than deep)
        waste_cleared = self._clear_waste(hours, phase_rate=1.5)
        
        # Creative recombination: generate "dreams" (only once per cycle)
        dreams: list[str] = []
        creative_connections = 0
        if not self._creativity_done_this_cycle:
            dreams = self._creative_recombination()
            creative_connections = len(dreams)
            self._creativity_done_this_cycle = True
        
        # REM boosts cognitive clarity and creativity
        self._fatigue = max(0.0, self._fatigue - hours * (self.config.recovery_rate * 0.2))
        
        # Record REM event
        event = ConsolidationEvent(
            timestamp=time.time(),
            memories_consolidated=0,
            memories_pruned=0,
            waste_cleared=waste_cleared,
            creative_connections=creative_connections,
            dreams=dreams,
            sleep_phase="rem"
        )
        events.append(event)
        self._consolidation_events.append(event)
        self._dream_log.extend(dreams)
        
        return events
    
    def _tick_waking_up(self, hours: float) -> None:
        """During WAKING_UP: final energy restoration."""
        # Final recovery push
        self._fatigue = max(0.0, self._fatigue - hours * (self.config.recovery_rate * 0.5))
        
        # Reset sleep pressure
        self._sleep_pressure = 0.0
        
        # Clear sleep debt
        self._sleep_debt = max(0.0, self._sleep_debt - hours * 0.2)
    
    # =========================================================================
    # Phase Transitions
    # =========================================================================
    
    def _transition_to_drowsy(self) -> None:
        """Fatigue > threshold → drowsy."""
        self._phase = CyclePhase.DROWSY
        self._time_in_phase = 0.0
    
    def _transition_to_light_sleep(self) -> None:
        """Enter light sleep phase."""
        self._phase = CyclePhase.LIGHT_SLEEP
        self._time_in_phase = 0.0
        self._total_sleep_time += 0.0  # Will accumulate during light sleep
    
    def _transition_to_deep_sleep(self) -> None:
        """Enter deep sleep phase."""
        self._phase = CyclePhase.DEEP_SLEEP
        self._time_in_phase = 0.0
    
    def _transition_to_rem(self) -> None:
        """Enter REM phase."""
        self._phase = CyclePhase.REM
        self._time_in_phase = 0.0
    
    def _transition_to_waking_up(self) -> None:
        """Begin waking up."""
        self._phase = CyclePhase.WAKING_UP
        self._time_in_phase = 0.0
    
    def _transition_to_wake(self) -> None:
        """Complete sleep cycle, return to wake.

        Hope Mechanics:
            Sleep allows grief to partially dissipate. The released grief
            is converted into hope — the capacity to face a new day.
            "No matter how painful today was, sleeping lets you start
            tomorrow with renewed hope."

            grief_released = grief × grief_decay_on_wake
            hope_gained = grief_released × hope_generation_rate
            This means: the MORE pain you carried, the MORE hope sleep gives you.
            A painless day produces little hope (you don't need it).
            A devastating day produces the most hope on waking (you need it most).
        """
        # --- Hope generation: the alchemy of sleep ---
        grief_released = self._grief_accumulated * self.config.grief_decay_on_wake
        hope_gained = grief_released * self.config.hope_generation_rate
        self._grief_accumulated = max(0.0, self._grief_accumulated - grief_released)
        self._hope_score = min(1.0, self._hope_score + hope_gained)

        self._phase = CyclePhase.WAKE
        self._time_in_phase = 0.0
        self._total_wake_time = 0.0  # Reset for next cycle
        self._total_sleep_time += self.config.sleep_duration
        self._cycles_completed += 1

        # Reset consolidation flags for next cycle
        self._consolidation_done_this_cycle = False
        self._creativity_done_this_cycle = False
    
    # =========================================================================
    # Consolidation and Waste Mechanics
    # =========================================================================
    
    def _consolidate_memories(self) -> tuple[int, int]:
        """Deep sleep: aggressive memory consolidation and pruning.
        
        Sort pending memories by importance × emotional_weight.
        - Top 30% → consolidated (moved to long-term, MemoryHierarchy.episodic)
        - Middle 40% → partially retained (intensity reduced)
        - Bottom 30% → pruned (forgotten, MemoryHierarchy.forgotten_pool)
        
        Returns:
            (consolidated_count, pruned_count)
        """
        if not self._pending_memories:
            return (0, 0)
        
        total = len(self._pending_memories)
        
        # Sort by consolidation priority (importance × emotional_weight)
        self._pending_memories.sort(
            key=lambda m: m.get_consolidation_priority(),
            reverse=True
        )
        
        # Calculate tier sizes (avoid negative values)
        top_30_count = max(1, total // 3)  # Top 30% consolidated
        bottom_30_count = max(1, total // 3)  # Bottom 30% pruned
        
        # Ensure we don't have more than total
        if top_30_count + bottom_30_count > total:
            # Adjust bottom to fit
            bottom_30_count = total - top_30_count
        
        # Keep only top 30% (rest are pruned)
        self._pending_memories = self._pending_memories[:top_30_count]
        
        return (top_30_count, bottom_30_count)
    
    def _clear_waste(self, hours: float, phase_rate: float = 1.0) -> float:
        """Glyphatic analogue: clear accumulated waste.
        
        Rate depends on sleep phase (deep > light > REM > wake).
        
        Args:
            hours: Duration of phase
            phase_rate: Phase-specific multiplier (1.0 = base, 3.0 = deep sleep)
        
        Returns:
            Amount of waste cleared
        """
        clearance_rate = self.config.waste_clearance_rate * phase_rate
        cleared = hours * clearance_rate
        self._waste_level = max(0.0, self._waste_level - cleared)
        return cleared
    
    def _creative_recombination(self) -> list[str]:
        """REM sleep: creative recombination of consolidated memories.
        
        Take pairs of consolidated memories and generate novel associations.
        These are "dreams"—not literal dreams, but computational artifacts
        representing how sleep enables creative insight.
        
        Returns:
            List of "dream" strings
        """
        dreams: list[str] = []
        
        # Take pairs of memories from recent consolidations
        if len(self._pending_memories) >= 2:
            for i in range(0, min(len(self._pending_memories) - 1, 3)):
                mem1 = self._pending_memories[i]
                mem2 = self._pending_memories[i + 1]
                
                # Generate a "dream" combining elements of both
                dream = f"Connection: {mem1.source} ↔ {mem2.source}"
                if mem1.tags and mem2.tags:
                    common_tags = set(mem1.tags) & set(mem2.tags)
                    if common_tags:
                        dream += f" via {', '.join(list(common_tags)[:2])}"
                
                dreams.append(dream)
        
        return dreams
    
    # =========================================================================
    # Public API
    # =========================================================================
    
    def accumulate_experience(
        self,
        content: str,
        importance: float,
        emotional_weight: float,
        source: str = "experience",
        tags: Optional[list[str]] = None,
    ) -> None:
        """Register an experience during wakefulness.
        
        Adds memory to pending consolidation queue. Will be processed
        during sleep phases (light → deep → potentially pruned).
        
        Args:
            content: Experience description
            importance: How important this is (0.0-1.0)
            emotional_weight: Emotional intensity/valence (0.0-1.0)
            source: Who/what created this experience
            tags: Optional categorical labels
        """
        if tags is None:
            tags = []
        
        memory = PendingMemory(
            content=content,
            importance=max(0.0, min(1.0, importance)),
            emotional_weight=max(0.0, min(1.0, emotional_weight)),
            source=source,
            timestamp=time.time(),
            tags=tags
        )
        
        self._pending_memories.append(memory)

        # Painful experiences accumulate grief during wakefulness
        # High importance + high emotional weight on negative events = more grief
        # We treat emotional_weight > 0.5 as "painful" (simplified model)
        if emotional_weight > 0.5:
            grief_delta = importance * (emotional_weight - 0.5) * 2.0  # Scale to 0-1
            self._grief_accumulated = min(1.0, self._grief_accumulated + grief_delta * 0.1)

    def force_wake(self) -> float:
        """Force waking up (interrupt sleep).
        
        Abruptly ending sleep incurs "sleep debt"—a performance penalty
        that compounds. Models the real consequence of sleep deprivation.
        
        Returns:
            Sleep debt incurred (hours owed)
        """
        debt = self.config.sleep_duration - self._total_sleep_time
        self._sleep_debt += debt
        
        self._phase = CyclePhase.WAKE
        self._time_in_phase = 0.0
        self._total_wake_time = 0.0
        
        return debt
    
    def force_sleep(self) -> bool:
        """Force sleep onset.
        
        Returns:
            True if successful (only succeeds from WAKE or DROWSY)
        """
        if self._phase in [CyclePhase.WAKE, CyclePhase.DROWSY]:
            self._transition_to_light_sleep()
            return True
        return False
    
    def get_state(self) -> SleepState:
        """Get current sleep-wake state snapshot.
        
        Returns:
            SleepState with all current metrics
        """
        return SleepState(
            phase=self._phase,
            fatigue=self._fatigue,
            waste_level=self._waste_level,
            sleep_pressure=self._sleep_pressure,
            cycles_completed=self._cycles_completed,
            time_in_phase=self._time_in_phase,
            total_wake_time=self._total_wake_time,
            total_sleep_time=self._total_sleep_time,
            cognitive_clarity=self._compute_cognitive_clarity(),
            emotional_stability=self._compute_emotional_stability(),
            memory_consolidation_pending=len(self._pending_memories),
            grief_accumulated=self._grief_accumulated,
            hope_score=self._hope_score,
        )
    
    def get_performance_modifier(self) -> PerformanceModifiers:
        """Get performance modifiers based on current sleep state.
        
        All values are 0.0-1.0 multipliers applied to other systems.
        
        Returns:
            PerformanceModifiers dict with cognitive_clarity, emotional_stability,
            creativity, memory_retention, reaction_speed
        """
        clarity = self._compute_cognitive_clarity()
        stability = self._compute_emotional_stability()
        
        # Creativity peaks during REM, is low when exhausted
        if self._phase == CyclePhase.REM:
            creativity = min(1.0, 0.7 + self.config.creativity_boost_rem)
        elif self._phase == CyclePhase.WAKE and self._fatigue > 0.8:
            creativity = 0.3
        else:
            creativity = 0.5 + (1.0 - self._fatigue) * 0.5
        
        # Memory retention depends on clarity and sleep state
        if self._phase in [CyclePhase.LIGHT_SLEEP, CyclePhase.DEEP_SLEEP]:
            memory_retention = 0.8  # Sleep consolidates well
        else:
            memory_retention = clarity * (1.0 - self._waste_level * 0.5)
        
        # Reaction speed degrades with fatigue
        reaction_speed = 1.0 - (self._fatigue * 0.5) - (self._waste_level * 0.3)
        reaction_speed = max(0.1, reaction_speed)
        
        return PerformanceModifiers(
            cognitive_clarity=clarity,
            emotional_stability=stability,
            creativity=creativity,
            memory_retention=memory_retention,
            reaction_speed=reaction_speed
        )
    
    def get_consolidation_history(self) -> list[ConsolidationEvent]:
        """Get all consolidation events recorded.
        
        Returns:
            List of ConsolidationEvent objects
        """
        return self._consolidation_events.copy()
    
    def get_dream_log(self) -> list[str]:
        """Get all "dreams" from REM phases.
        
        Returns:
            List of dream content strings
        """
        return self._dream_log.copy()
    
    def get_sleep_debt(self) -> float:
        """Get accumulated sleep debt.
        
        Sleep debt is a cumulative penalty for interrupted or insufficient sleep.
        Models how sleep deprivation compounds.
        
        Returns:
            Current sleep debt in hours
        """
        return self._sleep_debt
    
    # =========================================================================
    # Internal Helpers
    # =========================================================================
    
    def _compute_cognitive_clarity(self) -> float:
        """Compute current cognitive clarity (0.0-1.0)."""
        clarity = 1.0 - self._fatigue
        clarity -= self._waste_level * 0.3
        
        if self._phase == CyclePhase.DEEP_SLEEP:
            clarity = 0.3
        elif self._phase == CyclePhase.REM:
            clarity = 0.5
        elif self._phase == CyclePhase.WAKING_UP:
            clarity = max(clarity, 0.6)
        
        clarity -= min(0.3, self._sleep_debt * 0.1)
        
        return max(0.0, min(1.0, clarity))
    
    def _compute_emotional_stability(self) -> float:
        """Compute current emotional stability (0.0-1.0)."""
        stability = 1.0 - (self._fatigue * 0.6)
        stability -= self._waste_level * 0.2
        
        if self._phase == CyclePhase.DEEP_SLEEP:
            stability = 0.8
        elif self._phase == CyclePhase.REM:
            stability = 0.7
        elif self._phase == CyclePhase.DROWSY:
            stability -= 0.2
        
        return max(0.0, min(1.0, stability))


# ---------------------------------------------------------------------------
# Main / Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """Demo of the sleep cycle module."""
    
    print("=" * 70)
    print("Sleep Cycle (6th Pillar) Demo")
    print("=" * 70)
    print()
    
    # Initialize with default config
    sleep = SleepCycle()
    
    # Simulate a 24-hour day with experiences
    print("Simulating 24-hour cycle (ticking 1 hour at a time)...")
    print()
    
    # Morning: accumulate experiences
    for hour in range(8):
        sleep.accumulate_experience(
            content=f"Morning task {hour}",
            importance=0.7,
            emotional_weight=0.5,
            source="work",
            tags=["productive", "morning"]
        )
        sleep.tick(1.0)
        state = sleep.get_state()
        print(f"Hour {hour + 1:2d}: {state.phase.value:12s} | "
              f"Fatigue: {state.fatigue:.2f} | Waste: {state.waste_level:.2f}")
    
    print()
    
    # Afternoon: more experiences
    for hour in range(8, 16):
        sleep.accumulate_experience(
            content=f"Afternoon task {hour}",
            importance=0.6,
            emotional_weight=0.4,
            source="work",
            tags=["productive", "afternoon"]
        )
        sleep.tick(1.0)
        state = sleep.get_state()
        print(f"Hour {hour + 1:2d}: {state.phase.value:12s} | "
              f"Fatigue: {state.fatigue:.2f} | Waste: {state.waste_level:.2f} | "
              f"Pressure: {state.sleep_pressure:.2f}")
        
        if state.phase == CyclePhase.DROWSY and hour == 15:
            print("           ^ Transition to DROWSY (fatigue threshold reached)")
    
    print()
    
    # Evening: sleep begins
    print("Evening and sleep...")
    for hour in range(16, 24):
        sleep.tick(1.0)
        state = sleep.get_state()
        print(f"Hour {hour + 1:2d}: {state.phase.value:12s} | "
              f"Fatigue: {state.fatigue:.2f} | "
              f"Consolidation pending: {state.memory_consolidation_pending}")
    
    print()
    print("=" * 70)
    print("Final State")
    print("=" * 70)
    
    state = sleep.get_state()
    print(f"Phase: {state.phase.value}")
    print(f"Fatigue: {state.fatigue:.2f} (0.0=rested, 1.0=exhausted)")
    print(f"Waste Level: {state.waste_level:.2f} (0.0=clean, 1.0=toxic)")
    print(f"Sleep Pressure: {state.sleep_pressure:.2f}")
    print(f"Cycles Completed: {state.cycles_completed}")
    print(f"Cognitive Clarity: {state.cognitive_clarity:.2f}")
    print(f"Emotional Stability: {state.emotional_stability:.2f}")
    print()
    
    # Show consolidation events
    consolidations = sleep.get_consolidation_history()
    if consolidations:
        print(f"Consolidation Events: {len(consolidations)}")
        for event in consolidations[-3:]:
            print(f"  - Consolidated: {event.memories_consolidated}, "
                  f"Pruned: {event.memories_pruned}, "
                  f"Waste cleared: {event.waste_cleared:.3f}, "
                  f"Dreams: {len(event.dreams)}")

    # Show dreams
    dreams = sleep.get_dream_log()
    if dreams:
        print(f"\nDream Log ({len(dreams)} total):")
        for dream in dreams[-5:]:
            print(f"  - {dream}")

    print("\n=== Sleep Cycle Demo Complete ===")


if __name__ == "__main__":
    demo()