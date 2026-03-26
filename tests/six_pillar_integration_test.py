"""
Comprehensive pytest tests for experiments/sim_six_pillar_integration.py

Tests cover:
- Enum types (EventType, ConditionType)
- Data classes (MemoryEntry, SleepState, Agent, SimulationResult)
- SixPillarSimulation class and all methods
- Pillar active/inactive behavior
- Metric computation
- Invariants from the 8-condition ablation study

Author: human-persona research team
License: MIT
"""

import pytest
import random
import statistics
from experiments.sim_six_pillar_integration import (
    EventType,
    ConditionType,
    MemoryEntry,
    SleepState,
    Agent,
    SimulationResult,
    SixPillarSimulation,
)


# =============================================================================
# ENUM TESTS
# =============================================================================

class TestEventType:
    """Test EventType enum."""

    def test_event_type_has_all_variants(self):
        """Verify all expected event types exist."""
        expected = {"SOCIAL", "ACHIEVEMENT", "LOSS", "DISCOVERY",
                   "CONFLICT", "LOVE", "MUNDANE", "CRISIS"}
        actual = {e.name for e in EventType}
        assert actual == expected

    def test_event_type_values(self):
        """Verify event type string values."""
        assert EventType.SOCIAL.value == "social"
        assert EventType.LOSS.value == "loss"
        assert EventType.LOVE.value == "love"
        assert EventType.CRISIS.value == "crisis"


class TestConditionType:
    """Test ConditionType enum."""

    def test_condition_type_has_all_variants(self):
        """Verify all 8 conditions exist."""
        expected = {"FULL", "NO_FINITUDE", "NO_INCOMPLETENESS",
                   "NO_QUESTIONING", "NO_FORGETTING", "NO_RECOGNITION",
                   "NO_SLEEP", "BASELINE"}
        actual = {c.name for c in ConditionType}
        assert actual == expected

    def test_condition_type_values(self):
        """Verify condition string values."""
        assert ConditionType.FULL.value == "full"
        assert ConditionType.BASELINE.value == "baseline"
        assert ConditionType.NO_FINITUDE.value == "no_finitude"
        assert ConditionType.NO_SLEEP.value == "no_sleep"


# =============================================================================
# DATACLASS TESTS
# =============================================================================

class TestMemoryEntry:
    """Test MemoryEntry dataclass."""

    def test_memory_entry_creation(self):
        """Test basic MemoryEntry instantiation."""
        entry = MemoryEntry(
            content="test memory",
            tick_recorded=10,
            emotional_valence=0.7,
            importance=0.8
        )
        assert entry.content == "test memory"
        assert entry.tick_recorded == 10
        assert entry.emotional_valence == 0.7
        assert entry.importance == 0.8
        assert entry.access_count == 0

    def test_memory_entry_defaults(self):
        """Test default access_count is 0."""
        entry = MemoryEntry(
            content="memory",
            tick_recorded=5,
            emotional_valence=0.5,
            importance=0.5
        )
        assert entry.access_count == 0

    def test_memory_entry_access_count_increment(self):
        """Test access_count can be modified."""
        entry = MemoryEntry(
            content="memory",
            tick_recorded=5,
            emotional_valence=0.5,
            importance=0.5
        )
        entry.access_count += 1
        assert entry.access_count == 1


class TestSleepState:
    """Test SleepState dataclass."""

    def test_sleep_state_defaults(self):
        """Test SleepState default values."""
        state = SleepState()
        assert state.is_sleeping is False
        assert state.fatigue == 0.0
        assert state.cycles_completed == 0
        assert state.grief_processing == 0.0
        assert state.hope == 0.5

    def test_sleep_state_initialization(self):
        """Test SleepState with custom values."""
        state = SleepState(
            is_sleeping=True,
            fatigue=0.8,
            cycles_completed=3,
            grief_processing=0.2,
            hope=0.9
        )
        assert state.is_sleeping is True
        assert state.fatigue == 0.8
        assert state.cycles_completed == 3
        assert state.grief_processing == 0.2
        assert state.hope == 0.9


class TestAgent:
    """Test Agent dataclass."""

    def test_agent_creation(self):
        """Test basic Agent creation."""
        agent = Agent(
            agent_id=1,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        assert agent.agent_id == 1
        assert agent.condition == ConditionType.FULL
        assert agent.lifespan == 100.0
        assert agent.max_lifespan == 100.0

    def test_agent_default_lists_and_dicts(self):
        """Test Agent initializes with empty collections."""
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=50.0,
            max_lifespan=50.0
        )
        assert agent.love_circle == []
        assert agent.question_topics == []
        assert agent.episodic_memory == {}
        assert agent.events_experienced == []
        assert agent.individuality_markers == []

    def test_agent_sleep_state_default(self):
        """Test Agent has default SleepState."""
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=50.0,
            max_lifespan=50.0
        )
        assert isinstance(agent.sleep_state, SleepState)
        assert agent.sleep_state.hope == 0.5


class TestSimulationResult:
    """Test SimulationResult dataclass and its methods."""

    def test_simulation_result_creation(self):
        """Test SimulationResult instantiation."""
        result = SimulationResult(
            condition=ConditionType.FULL,
            n_agents=30
        )
        assert result.condition == ConditionType.FULL
        assert result.n_agents == 30
        assert result.acceptance_scores == []

    def test_compute_means_empty(self):
        """Test compute_means with empty lists returns 0.0."""
        result = SimulationResult(
            condition=ConditionType.FULL,
            n_agents=0
        )
        means = result.compute_means()
        assert means['acceptance'] == 0.0
        assert means['wisdom'] == 0.0
        assert means['hope'] == 0.0

    def test_compute_means_with_data(self):
        """Test compute_means with sample data."""
        result = SimulationResult(
            condition=ConditionType.FULL,
            n_agents=3
        )
        result.acceptance_scores = [0.2, 0.4, 0.6]
        result.individuality_scores = [0.1, 0.2, 0.3]
        
        means = result.compute_means()
        assert means['acceptance'] == 0.4
        assert means['individuality'] == 0.2

    def test_compute_stdevs_single_value(self):
        """Test compute_stdevs with single value returns 0."""
        result = SimulationResult(
            condition=ConditionType.FULL,
            n_agents=1
        )
        result.acceptance_scores = [0.5]
        
        stdevs = result.compute_stdevs()
        assert stdevs['acceptance'] == 0.0

    def test_compute_stdevs_with_data(self):
        """Test compute_stdevs calculates correctly."""
        result = SimulationResult(
            condition=ConditionType.FULL,
            n_agents=4
        )
        result.wisdom_scores = [0.1, 0.2, 0.3, 0.4]
        
        stdevs = result.compute_stdevs()
        expected = statistics.stdev([0.1, 0.2, 0.3, 0.4])
        assert abs(stdevs['wisdom'] - expected) < 0.0001


# =============================================================================
# SIXPILLARSIMULATION PILLAR ACTIVE TESTS
# =============================================================================

class TestPillarActive:
    """Test the _pillar_active() helper method."""

    def test_baseline_disables_all_pillars(self):
        """BASELINE condition disables all pillars."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=100, seed=42)
        
        pillars = ['finitude', 'incompleteness', 'questioning',
                  'forgetting', 'recognition', 'sleep']
        
        for pillar in pillars:
            assert not sim._pillar_active(ConditionType.BASELINE, pillar)

    def test_full_enables_all_pillars(self):
        """FULL condition enables all pillars."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=100, seed=42)
        
        pillars = ['finitude', 'incompleteness', 'questioning',
                  'forgetting', 'recognition', 'sleep']
        
        for pillar in pillars:
            assert sim._pillar_active(ConditionType.FULL, pillar)

    def test_no_finitude_disables_finitude_only(self):
        """NO_FINITUDE disables only finitude pillar."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=100, seed=42)
        
        assert not sim._pillar_active(ConditionType.NO_FINITUDE, 'finitude')
        assert sim._pillar_active(ConditionType.NO_FINITUDE, 'incompleteness')
        assert sim._pillar_active(ConditionType.NO_FINITUDE, 'questioning')
        assert sim._pillar_active(ConditionType.NO_FINITUDE, 'forgetting')
        assert sim._pillar_active(ConditionType.NO_FINITUDE, 'recognition')
        assert sim._pillar_active(ConditionType.NO_FINITUDE, 'sleep')

    def test_no_incompleteness_disables_incompleteness_only(self):
        """NO_INCOMPLETENESS disables only incompleteness pillar."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=100, seed=42)
        
        assert sim._pillar_active(ConditionType.NO_INCOMPLETENESS, 'finitude')
        assert not sim._pillar_active(ConditionType.NO_INCOMPLETENESS, 'incompleteness')
        assert sim._pillar_active(ConditionType.NO_INCOMPLETENESS, 'questioning')

    def test_no_forgetting_disables_forgetting_only(self):
        """NO_FORGETTING disables only forgetting pillar."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=100, seed=42)
        
        assert sim._pillar_active(ConditionType.NO_FORGETTING, 'finitude')
        assert sim._pillar_active(ConditionType.NO_FORGETTING, 'incompleteness')
        assert not sim._pillar_active(ConditionType.NO_FORGETTING, 'forgetting')
        assert sim._pillar_active(ConditionType.NO_FORGETTING, 'recognition')

    def test_no_recognition_disables_recognition_only(self):
        """NO_RECOGNITION disables only recognition pillar."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=100, seed=42)
        
        assert not sim._pillar_active(ConditionType.NO_RECOGNITION, 'recognition')
        assert sim._pillar_active(ConditionType.NO_RECOGNITION, 'finitude')
        assert sim._pillar_active(ConditionType.NO_RECOGNITION, 'sleep')

    def test_no_sleep_disables_sleep_only(self):
        """NO_SLEEP disables only sleep pillar."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=100, seed=42)
        
        assert not sim._pillar_active(ConditionType.NO_SLEEP, 'sleep')
        assert sim._pillar_active(ConditionType.NO_SLEEP, 'finitude')
        assert sim._pillar_active(ConditionType.NO_SLEEP, 'incompleteness')

    def test_no_questioning_disables_questioning_only(self):
        """NO_QUESTIONING disables only questioning pillar."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=100, seed=42)
        
        assert not sim._pillar_active(ConditionType.NO_QUESTIONING, 'questioning')
        assert sim._pillar_active(ConditionType.NO_QUESTIONING, 'finitude')
        assert sim._pillar_active(ConditionType.NO_QUESTIONING, 'sleep')


# =============================================================================
# CREATE_AGENTS TESTS
# =============================================================================

class TestCreateAgents:
    """Test the create_agents() factory method."""

    def test_create_agents_correct_count(self):
        """Verify create_agents returns correct number of agents."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        
        agents = sim.create_agents(ConditionType.FULL, 10)
        assert len(agents) == 10

    def test_create_agents_no_finitude_immortal(self):
        """NO_FINITUDE agents have lifespan=100.0 (immortal)."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        
        agents = sim.create_agents(ConditionType.NO_FINITUDE, 5)
        for agent in agents:
            assert agent.lifespan == 100.0
            assert agent.max_lifespan == 100.0

    def test_create_agents_baseline_immortal(self):
        """BASELINE agents have lifespan=100.0 (no finitude pillar)."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        
        agents = sim.create_agents(ConditionType.BASELINE, 5)
        for agent in agents:
            assert agent.lifespan == 100.0
            assert agent.max_lifespan == 100.0

    def test_create_agents_full_random_lifespan(self):
        """FULL agents have random lifespan between 50-100."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        random.seed(42)
        
        agents = sim.create_agents(ConditionType.FULL, 20)
        for agent in agents:
            assert 50 <= agent.lifespan <= 100
            assert agent.lifespan == agent.max_lifespan

    def test_create_agents_unique_ids(self):
        """Agent IDs are unique."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        
        agents = sim.create_agents(ConditionType.FULL, 10)
        ids = [a.agent_id for a in agents]
        assert len(ids) == len(set(ids))

    def test_create_agents_recognition_pairing(self):
        """FULL condition pairs agents for mutual recognition."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        
        agents = sim.create_agents(ConditionType.FULL, 10)
        
        # Check that agents are paired
        paired_count = sum(1 for a in agents if a.partner is not None)
        assert paired_count == 10  # All 10 agents should have partners

    def test_create_agents_no_recognition_no_pairing(self):
        """NO_RECOGNITION condition doesn't pair agents."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        
        agents = sim.create_agents(ConditionType.NO_RECOGNITION, 10)
        
        for agent in agents:
            assert agent.partner is None

    def test_create_agents_condition_stored(self):
        """Each agent stores its condition correctly."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        
        for condition in ConditionType:
            agents = sim.create_agents(condition, 5)
            for agent in agents:
                assert agent.condition == condition


# =============================================================================
# APPLY_EVENT TESTS
# =============================================================================

class TestApplyEvent:
    """Test the apply_event() method."""

    def test_apply_event_loss_with_incompleteness(self):
        """LOSS event increases yearning when incompleteness pillar active."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        initial_yearning = agent.yearning_level
        sim.apply_event(agent, EventType.LOSS, tick=10)
        
        assert agent.yearning_level > initial_yearning

    def test_apply_event_loss_without_incompleteness(self):
        """LOSS event doesn't affect yearning when incompleteness disabled."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_INCOMPLETENESS,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        initial_yearning = agent.yearning_level
        sim.apply_event(agent, EventType.LOSS, tick=10)
        
        assert agent.yearning_level == initial_yearning

    def test_apply_event_love_with_incompleteness(self):
        """LOVE event adds to love_circle when incompleteness active."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        initial_count = len(agent.love_circle)
        sim.apply_event(agent, EventType.LOVE, tick=10)
        
        assert len(agent.love_circle) >= initial_count

    def test_apply_event_discovery_with_questioning(self):
        """DISCOVERY event increments questions_asked when questioning active."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        initial_count = agent.questions_asked
        sim.apply_event(agent, EventType.DISCOVERY, tick=10)
        
        assert agent.questions_asked > initial_count
        assert len(agent.question_topics) > 0

    def test_apply_event_discovery_without_questioning(self):
        """DISCOVERY doesn't increase questions when questioning disabled."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_QUESTIONING,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        initial_count = agent.questions_asked
        sim.apply_event(agent, EventType.DISCOVERY, tick=10)
        
        assert agent.questions_asked == initial_count

    def test_apply_event_achievement_with_forgetting(self):
        """ACHIEVEMENT event creates episodic memory when forgetting active."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        sim.apply_event(agent, EventType.ACHIEVEMENT, tick=10)
        
        assert len(agent.episodic_memory) > 0

    def test_apply_event_achievement_without_forgetting(self):
        """ACHIEVEMENT doesn't create memory when forgetting disabled."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_FORGETTING,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        sim.apply_event(agent, EventType.ACHIEVEMENT, tick=10)
        
        assert len(agent.episodic_memory) == 0

    def test_apply_event_recorded_in_history(self):
        """apply_event records event in events_experienced."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        sim.apply_event(agent, EventType.CRISIS, tick=15)
        
        assert len(agent.events_experienced) > 0
        assert agent.events_experienced[-1] == (15, EventType.CRISIS)


# =============================================================================
# PROCESS_MEMORY_DECAY TESTS
# =============================================================================

class TestProcessMemoryDecay:
    """Test the process_memory_decay() method."""

    def test_process_memory_decay_skipped_when_disabled(self):
        """Memory decay is skipped when forgetting pillar disabled."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_FORGETTING,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        # Add memories
        agent.episodic_memory['m1'] = MemoryEntry(
            content="memory1",
            tick_recorded=0,
            emotional_valence=0.5,
            importance=0.1
        )
        agent.episodic_memory['m2'] = MemoryEntry(
            content="memory2",
            tick_recorded=0,
            emotional_valence=0.5,
            importance=0.1
        )
        
        initial_count = len(agent.episodic_memory)
        
        # Process decay multiple times
        for tick in range(100):
            sim.process_memory_decay(agent, tick)
        
        # Memories should be preserved
        assert len(agent.episodic_memory) == initial_count

    def test_process_memory_decay_baseline_no_decay(self):
        """BASELINE (no pillars) doesn't decay memories."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.BASELINE,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        agent.episodic_memory['m1'] = MemoryEntry(
            content="memory",
            tick_recorded=0,
            emotional_valence=0.5,
            importance=0.1
        )
        
        initial_count = len(agent.episodic_memory)
        
        for tick in range(50):
            sim.process_memory_decay(agent, tick)
        
        assert len(agent.episodic_memory) == initial_count

    def test_process_memory_decay_full_condition_can_decay(self):
        """FULL condition allows memory decay."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        # Add many old, low-importance memories
        for i in range(20):
            agent.episodic_memory[f'm{i}'] = MemoryEntry(
                content=f"memory{i}",
                tick_recorded=0,
                emotional_valence=0.0,
                importance=0.05  # Low importance decays faster
            )
        
        initial_count = len(agent.episodic_memory)
        
        # Process decay over many ticks
        random.seed(42)
        for tick in range(1, 150):
            sim.process_memory_decay(agent, tick)
        
        # Some memories should have decayed
        assert len(agent.episodic_memory) < initial_count

    def test_process_memory_decay_caps_episodic_size(self):
        """process_memory_decay caps memory size at memory_capacity_episodic."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        # Manually add more memories than capacity
        for i in range(50):
            agent.episodic_memory[f'm{i}'] = MemoryEntry(
                content=f"memory{i}",
                tick_recorded=i,
                emotional_valence=0.5,
                importance=0.1
            )
        
        assert len(agent.episodic_memory) > agent.memory_capacity_episodic
        
        sim.process_memory_decay(agent, 100)
        
        assert len(agent.episodic_memory) <= agent.memory_capacity_episodic


# =============================================================================
# PROCESS_SLEEP_CYCLE TESTS
# =============================================================================

class TestProcessSleepCycle:
    """Test the process_sleep_cycle() method."""

    def test_process_sleep_cycle_disabled_resets_fatigue(self):
        """Sleep disabled (NO_SLEEP) resets fatigue to 0."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_SLEEP,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        agent.sleep_state.fatigue = 0.9
        sim.process_sleep_cycle(agent, 10)
        
        assert agent.sleep_state.fatigue == 0.0

    def test_process_sleep_cycle_disabled_resets_hope(self):
        """Sleep disabled sets hope to 0.5."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_SLEEP,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        agent.sleep_state.hope = 0.9
        sim.process_sleep_cycle(agent, 10)
        
        assert agent.sleep_state.hope == 0.5

    def test_process_sleep_cycle_accumulates_fatigue(self):
        """Sleep enabled accumulates fatigue over time."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        initial_fatigue = agent.sleep_state.fatigue
        sim.process_sleep_cycle(agent, 1)
        
        assert agent.sleep_state.fatigue > initial_fatigue

    def test_process_sleep_cycle_triggers_sleep(self):
        """Sleep cycle triggers at high fatigue."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        # Manually set high fatigue
        agent.sleep_state.fatigue = 0.8
        agent.sleep_state.grief_processing = 0.5
        
        sim.process_sleep_cycle(agent, 10)
        
        # Sleep should have triggered
        assert agent.sleep_state.fatigue == 0.0
        assert agent.sleep_state.hope > 0.5
        assert agent.acceptance_growth > 0.0

    def test_process_sleep_cycle_periodic_trigger(self):
        """Sleep cycle triggers periodically (every 40 ticks)."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        initial_cycles = agent.sleep_state.cycles_completed
        
        # Tick 40 should trigger sleep
        sim.process_sleep_cycle(agent, 40)
        
        assert agent.sleep_state.cycles_completed > initial_cycles


# =============================================================================
# COMPUTE SCORING METHODS TESTS
# =============================================================================

class TestComputeAcceptanceScore:
    """Test the compute_acceptance_score() method."""

    def test_acceptance_zero_without_finitude(self):
        """Acceptance is 0.0 when finitude pillar disabled."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_FINITUDE,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        acceptance = sim.compute_acceptance_score(agent)
        assert acceptance == 0.0

    def test_acceptance_baseline_near_zero(self):
        """Acceptance is near zero for BASELINE (no pillars)."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.BASELINE,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        acceptance = sim.compute_acceptance_score(agent)
        # BASELINE doesn't have finitude pillar, so should be 0
        assert acceptance == 0.0

    def test_acceptance_increases_with_sleep_cycles(self):
        """Acceptance increases with sleep cycles."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        agent.sleep_state.cycles_completed = 10
        acceptance = sim.compute_acceptance_score(agent)
        
        assert acceptance > 0.0

    def test_acceptance_increases_with_questions(self):
        """Acceptance increases with questions asked."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        agent.questions_asked = 20
        acceptance = sim.compute_acceptance_score(agent)
        
        assert acceptance > 0.0


class TestComputeIndividualityScore:
    """Test the compute_individuality_score() method."""

    def test_individuality_low_baseline(self):
        """Individuality low for BASELINE (0.1)."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.BASELINE,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        individuality = sim.compute_individuality_score(agent)
        assert individuality == 0.1

    def test_individuality_low_without_forgetting(self):
        """Individuality low when forgetting disabled (0.3)."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_FORGETTING,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        individuality = sim.compute_individuality_score(agent)
        assert individuality == 0.3

    def test_individuality_increases_with_questions(self):
        """Individuality increases with unique question topics."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        agent.question_topics = ["why?", "who am I?", "what is love?"]
        individuality = sim.compute_individuality_score(agent)
        
        assert individuality > 0.1


class TestComputeBondDepth:
    """Test the compute_bond_depth() method."""

    def test_bond_depth_zero_no_bonds(self):
        """Bond depth is 0.0 with no love_circle."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        bond_depth = sim.compute_bond_depth(agent)
        assert bond_depth == 0.0

    def test_bond_depth_increases_with_bonds(self):
        """Bond depth increases with more bonds."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        agent.love_circle = [1, 2, 3]
        bond_depth = sim.compute_bond_depth(agent)
        
        assert bond_depth > 0.0


class TestComputeHopeScore:
    """Test the compute_hope_score() method."""

    def test_hope_low_without_sleep(self):
        """Hope is 0.1 when sleep pillar disabled."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_SLEEP,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        hope = sim.compute_hope_score(agent)
        assert hope == 0.1

    def test_hope_from_sleep_state(self):
        """Hope reflects agent's sleep_state.hope."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        agent.sleep_state.hope = 0.8
        hope = sim.compute_hope_score(agent)
        
        assert hope == 0.8


class TestComputeCreativeInsights:
    """Test the compute_creative_insights() method."""

    def test_creative_insights_zero_without_questioning(self):
        """Creative insights is 0 when questioning pillar disabled."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_QUESTIONING,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        insights = sim.compute_creative_insights(agent)
        assert insights == 0

    def test_creative_insights_counts_unique_topics(self):
        """Creative insights counts unique question topics."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        agent.question_topics = ["why?", "who?", "why?", "what?"]
        insights = sim.compute_creative_insights(agent)
        
        assert insights == 3  # 3 unique topics


class TestComputeWisdom:
    """Test the compute_wisdom() method."""

    def test_wisdom_is_multiplicative(self):
        """Wisdom is product of acceptance, individuality, bond_depth."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        agent.sleep_state.cycles_completed = 10
        agent.question_topics = ["why?"]
        agent.love_circle = [1]
        
        wisdom = sim.compute_wisdom(agent)
        acceptance = sim.compute_acceptance_score(agent)
        individuality = sim.compute_individuality_score(agent)
        bond_depth = sim.compute_bond_depth(agent)
        
        expected = acceptance * individuality * bond_depth
        assert abs(wisdom - expected) < 0.001

    def test_wisdom_zero_without_finitude(self):
        """Wisdom is 0.0 without finitude (acceptance=0)."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_FINITUDE,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        wisdom = sim.compute_wisdom(agent)
        assert wisdom == 0.0

    def test_wisdom_zero_without_incompleteness(self):
        """Wisdom is 0.0 without incompleteness (bond_depth=0)."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_INCOMPLETENESS,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        wisdom = sim.compute_wisdom(agent)
        assert wisdom == 0.0


class TestComputeCoexistenceReadiness:
    """Test the compute_coexistence_readiness() method."""

    def test_coexistence_zero_without_recognition(self):
        """Coexistence readiness is 0.0 without recognition pillar."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.NO_RECOGNITION,
            lifespan=100.0,
            max_lifespan=100.0
        )
        
        coexistence = sim.compute_coexistence_readiness(agent)
        assert coexistence == 0.0

    def test_coexistence_low_without_partner(self):
        """Coexistence readiness is 0.1 for unpaired agent."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        agent.partner = None
        
        coexistence = sim.compute_coexistence_readiness(agent)
        assert coexistence == 0.1

    def test_coexistence_increases_with_partner(self):
        """Coexistence readiness increases with partner."""
        sim = SixPillarSimulation(n_agents=30, n_ticks=100, seed=42)
        agent = Agent(
            agent_id=0,
            condition=ConditionType.FULL,
            lifespan=100.0,
            max_lifespan=100.0
        )
        agent.partner = 1
        
        coexistence = sim.compute_coexistence_readiness(agent)
        assert coexistence > 0.1


# =============================================================================
# RUN_CONDITION AND INTEGRATION TESTS
# =============================================================================

class TestRunCondition:
    """Test the run_condition() method."""

    def test_run_condition_returns_simulation_result(self):
        """run_condition returns a SimulationResult."""
        sim = SixPillarSimulation(n_agents=5, n_ticks=10, seed=42)
        result = sim.run_condition(ConditionType.FULL)
        
        assert isinstance(result, SimulationResult)
        assert result.condition == ConditionType.FULL
        assert result.n_agents == 5

    def test_run_condition_populates_metrics(self):
        """run_condition populates all metric lists."""
        sim = SixPillarSimulation(n_agents=5, n_ticks=10, seed=42)
        result = sim.run_condition(ConditionType.FULL)
        
        assert len(result.acceptance_scores) == 5
        assert len(result.individuality_scores) == 5
        assert len(result.bond_depths) == 5
        assert len(result.hope_scores) == 5
        assert len(result.creative_insights) == 5
        assert len(result.wisdom_scores) == 5
        assert len(result.coexistence_readiness) == 5

    def test_run_condition_baseline_near_zero(self):
        """BASELINE condition produces near-zero metrics."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=50, seed=42)
        result = sim.run_condition(ConditionType.BASELINE)
        
        means = result.compute_means()
        avg = sum(means.values()) / len(means)
        
        # Expect very low values (near 0.029 per research notes)
        assert avg < 0.15

    def test_run_condition_full_higher_than_baseline(self):
        """FULL condition produces higher metrics than BASELINE."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=50, seed=42)
        
        full_result = sim.run_condition(ConditionType.FULL)
        baseline_result = sim.run_condition(ConditionType.BASELINE)
        
        full_means = full_result.compute_means()
        baseline_means = baseline_result.compute_means()
        
        full_avg = sum(full_means.values()) / len(full_means)
        baseline_avg = sum(baseline_means.values()) / len(baseline_means)
        
        assert full_avg > baseline_avg

    def test_run_condition_no_finitude_zero_acceptance(self):
        """NO_FINITUDE produces acceptance=0."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=50, seed=42)
        result = sim.run_condition(ConditionType.NO_FINITUDE)
        
        means = result.compute_means()
        assert means['acceptance'] == 0.0

    def test_run_condition_no_incompleteness_zero_bond_depth(self):
        """NO_INCOMPLETENESS produces bond_depth=0."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=50, seed=42)
        result = sim.run_condition(ConditionType.NO_INCOMPLETENESS)
        
        means = result.compute_means()
        assert means['bond_depth'] == 0.0

    def test_run_condition_no_recognition_zero_coexistence(self):
        """NO_RECOGNITION produces coexistence_readiness=0."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=50, seed=42)
        result = sim.run_condition(ConditionType.NO_RECOGNITION)
        
        means = result.compute_means()
        assert means['coexistence_readiness'] == 0.0

    def test_run_condition_no_sleep_low_hope(self):
        """NO_SLEEP produces low hope (0.1)."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=50, seed=42)
        result = sim.run_condition(ConditionType.NO_SLEEP)
        
        means = result.compute_means()
        assert means['hope'] == 0.1

    def test_run_condition_no_questioning_zero_insights(self):
        """NO_QUESTIONING produces creative_insights=0."""
        sim = SixPillarSimulation(n_agents=10, n_ticks=50, seed=42)
        result = sim.run_condition(ConditionType.NO_QUESTIONING)
        
        means = result.compute_means()
        assert means['creative_insights'] == 0.0


class TestSimulationInitialization:
    """Test SixPillarSimulation initialization."""

    def test_initialization_default_params(self):
        """Verify initialization with default parameters."""
        sim = SixPillarSimulation()
        
        assert sim.n_agents == 30
        assert sim.n_ticks == 200
        assert sim.seed == 42
        assert len(sim.event_pool) == 8
        assert sim.results == {}

    def test_initialization_custom_params(self):
        """Verify initialization with custom parameters."""
        sim = SixPillarSimulation(n_agents=50, n_ticks=300, seed=99)
        
        assert sim.n_agents == 50
        assert sim.n_ticks == 300
        assert sim.seed == 99

    def test_initialization_event_pool_has_all_types(self):
        """Verify event pool contains all event types."""
        sim = SixPillarSimulation()
        
        event_types = {e.value for e in sim.event_pool}
        expected_types = {e.value for e in EventType}
        
        assert event_types == expected_types


class TestRunAllConditions:
    """Test the run_all_conditions() method."""

    def test_run_all_conditions_populates_results(self):
        """run_all_conditions populates results dict."""
        sim = SixPillarSimulation(n_agents=5, n_ticks=10, seed=42)
        sim.run_all_conditions()
        
        assert len(sim.results) == 8  # 8 conditions
        assert all(c in sim.results for c in ConditionType)

    def test_run_all_conditions_all_results_valid(self):
        """All results from run_all_conditions have correct structure."""
        sim = SixPillarSimulation(n_agents=5, n_ticks=10, seed=42)
        sim.run_all_conditions()
        
        for condition, result in sim.results.items():
            assert isinstance(result, SimulationResult)
            assert result.condition == condition
            assert result.n_agents == 5
            assert len(result.acceptance_scores) == 5


# =============================================================================
# EXPERIMENT HYPOTHESIS TESTS
# =============================================================================

class TestExperimentHypotheses:
    """Test hypotheses from the research paper."""

    def test_hypothesis_baseline_near_zero(self):
        """H6: BASELINE produces near-zero metrics on all axes."""
        sim = SixPillarSimulation(n_agents=15, n_ticks=100, seed=42)
        result = sim.run_condition(ConditionType.BASELINE)
        
        means = result.compute_means()
        
        # All metrics should be very low
        assert means['acceptance'] < 0.2
        assert means['individuality'] == 0.1
        assert means['bond_depth'] == 0.0
        assert means['creative_insights'] == 0.0
        assert means['coexistence_readiness'] == 0.0

    def test_hypothesis_full_dominates_baseline(self):
        """FULL condition produces substantially higher wisdom than BASELINE."""
        sim = SixPillarSimulation(n_agents=15, n_ticks=100, seed=42)
        
        full_result = sim.run_condition(ConditionType.FULL)
        baseline_result = sim.run_condition(ConditionType.BASELINE)
        
        full_wisdom = full_result.compute_means()['wisdom']
        baseline_wisdom = baseline_result.compute_means()['wisdom']
        
        # FULL should have significantly higher wisdom
        assert full_wisdom > baseline_wisdom * 5

    def test_hypothesis_no_finitude_breaks_wisdom(self):
        """NO_FINITUDE eliminates wisdom via acceptance=0."""
        sim = SixPillarSimulation(n_agents=15, n_ticks=100, seed=42)
        result = sim.run_condition(ConditionType.NO_FINITUDE)
        
        means = result.compute_means()
        
        # Wisdom should be near zero (acceptance=0 kills it)
        assert means['wisdom'] == 0.0
        assert means['acceptance'] == 0.0

    def test_hypothesis_no_incompleteness_breaks_wisdom(self):
        """NO_INCOMPLETENESS eliminates wisdom via bond_depth=0."""
        sim = SixPillarSimulation(n_agents=15, n_ticks=100, seed=42)
        result = sim.run_condition(ConditionType.NO_INCOMPLETENESS)
        
        means = result.compute_means()
        
        # Wisdom should be zero (bond_depth=0 kills it)
        assert means['wisdom'] == 0.0
        assert means['bond_depth'] == 0.0

    def test_hypothesis_no_sleep_low_hope(self):
        """H4: NO_SLEEP produces low hope."""
        sim = SixPillarSimulation(n_agents=15, n_ticks=100, seed=42)
        result = sim.run_condition(ConditionType.NO_SLEEP)
        
        means = result.compute_means()
        assert means['hope'] == 0.1

    def test_hypothesis_no_recognition_breaks_coexistence(self):
        """H5: NO_RECOGNITION produces zero coexistence readiness."""
        sim = SixPillarSimulation(n_agents=15, n_ticks=100, seed=42)
        result = sim.run_condition(ConditionType.NO_RECOGNITION)
        
        means = result.compute_means()
        assert means['coexistence_readiness'] == 0.0

    def test_hypothesis_no_questioning_no_insights(self):
        """NO_QUESTIONING produces zero creative insights."""
        sim = SixPillarSimulation(n_agents=15, n_ticks=100, seed=42)
        result = sim.run_condition(ConditionType.NO_QUESTIONING)
        
        means = result.compute_means()
        assert means['creative_insights'] == 0.0
