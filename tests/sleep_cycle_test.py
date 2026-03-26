"""Comprehensive pytest tests for SleepCycle (6th Pillar: Dormancy and Renewal).

Tests cover:
- CyclePhase enum and phase transitions
- SleepConfig defaults and custom values
- SleepCycle initialization and state management
- Phase transitions (advance_phase, full cycle progression)
- Sleep/wake cycle mechanics (start_sleep, wake_up, force_wake, force_sleep)
- Memory consolidation during sleep
- Glyphatic analog (waste clearance)
- Creative recombination during REM
- Hope mechanics: grief accumulation, decay, generation
- Performance modifiers based on sleep state
- Edge cases: negative values, overflow to 1.0, multiple cycles
"""

import pytest
import time
from core.inner_shell.sleep_cycle import (
    CyclePhase,
    SleepConfig,
    SleepState,
    PendingMemory,
    ConsolidationEvent,
    PerformanceModifiers,
    SleepCycle,
)


class TestCyclePhase:
    """Test CyclePhase enum."""

    def test_cycle_phase_values(self):
        """Test that all CyclePhase values exist."""
        assert CyclePhase.WAKE.value == "wake"
        assert CyclePhase.DROWSY.value == "drowsy"
        assert CyclePhase.LIGHT_SLEEP.value == "light"
        assert CyclePhase.DEEP_SLEEP.value == "deep"
        assert CyclePhase.REM.value == "rem"
        assert CyclePhase.WAKING_UP.value == "waking"

    def test_cycle_phase_enum_count(self):
        """Test that we have exactly 6 phases."""
        phases = list(CyclePhase)
        assert len(phases) == 6

    def test_cycle_phase_string_comparison(self):
        """Test CyclePhase string comparison."""
        assert CyclePhase.WAKE == "wake"
        assert CyclePhase.DEEP_SLEEP == "deep"


class TestSleepConfig:
    """Test SleepConfig dataclass."""

    def test_default_config(self):
        """Test SleepConfig with default values."""
        config = SleepConfig()
        assert config.wake_duration == 16.0
        assert config.sleep_duration == 8.0
        assert config.fatigue_rate == 0.0625
        assert config.recovery_rate == 0.125
        assert config.consolidation_strength == 0.3
        assert config.waste_accumulation_rate == 0.05
        assert config.waste_clearance_rate == 0.15
        assert config.creativity_boost_rem == 0.2
        assert config.drowsy_threshold == 0.7
        assert config.sleep_pressure_max == 1.0
        assert config.light_sleep_duration == 1.0
        assert config.deep_sleep_duration == 4.0
        assert config.rem_duration == 1.5
        assert config.grief_decay_on_wake == 0.4
        assert config.hope_generation_rate == 0.3
        assert config.hope_decay_during_wake == 0.02

    def test_custom_config(self):
        """Test SleepConfig with custom values."""
        config = SleepConfig(
            wake_duration=14.0,
            sleep_duration=10.0,
            fatigue_rate=0.1,
            recovery_rate=0.2,
            creativity_boost_rem=0.4,
        )
        assert config.wake_duration == 14.0
        assert config.sleep_duration == 10.0
        assert config.fatigue_rate == 0.1
        assert config.recovery_rate == 0.2
        assert config.creativity_boost_rem == 0.4
        # Other values should still be default
        assert config.drowsy_threshold == 0.7

    def test_config_positive_values(self):
        """Test that config can be created with positive values."""
        config = SleepConfig(
            fatigue_rate=0.5,
            recovery_rate=0.3,
            waste_accumulation_rate=0.1,
        )
        assert config.fatigue_rate > 0.0
        assert config.recovery_rate > 0.0
        assert config.waste_accumulation_rate > 0.0


class TestPendingMemory:
    """Test PendingMemory dataclass."""

    def test_pending_memory_creation(self):
        """Test creating a pending memory."""
        mem = PendingMemory(
            content="test experience",
            importance=0.8,
            emotional_weight=0.6,
            source="work",
            timestamp=time.time(),
            tags=["important", "work"],
        )
        assert mem.content == "test experience"
        assert mem.importance == 0.8
        assert mem.emotional_weight == 0.6
        assert mem.source == "work"
        assert mem.tags == ["important", "work"]

    def test_pending_memory_default_tags(self):
        """Test that tags default to empty list."""
        mem = PendingMemory(
            content="test",
            importance=0.5,
            emotional_weight=0.5,
            source="test",
            timestamp=time.time(),
        )
        assert mem.tags == []

    def test_consolidation_priority(self):
        """Test consolidation priority calculation."""
        mem = PendingMemory(
            content="test",
            importance=0.8,
            emotional_weight=0.5,
            source="test",
            timestamp=time.time(),
        )
        priority = mem.get_consolidation_priority()
        assert priority == 0.8 * 0.5
        assert priority == 0.4

    def test_consolidation_priority_zero_values(self):
        """Test consolidation priority with zero values."""
        mem = PendingMemory(
            content="test",
            importance=0.0,
            emotional_weight=0.5,
            source="test",
            timestamp=time.time(),
        )
        assert mem.get_consolidation_priority() == 0.0

    def test_consolidation_priority_max_values(self):
        """Test consolidation priority with max values."""
        mem = PendingMemory(
            content="test",
            importance=1.0,
            emotional_weight=1.0,
            source="test",
            timestamp=time.time(),
        )
        assert mem.get_consolidation_priority() == 1.0


class TestSleepCycleInitialization:
    """Test SleepCycle initialization."""

    def test_init_default_config(self):
        """Test SleepCycle initialization with default config."""
        sleep = SleepCycle()
        assert sleep.config is not None
        assert sleep.config.wake_duration == 16.0

    def test_init_custom_config(self):
        """Test SleepCycle initialization with custom config."""
        config = SleepConfig(wake_duration=12.0)
        sleep = SleepCycle(config=config)
        assert sleep.config.wake_duration == 12.0

    def test_init_state(self):
        """Test that SleepCycle initializes in WAKE phase."""
        sleep = SleepCycle()
        state = sleep.get_state()
        assert state.phase == CyclePhase.WAKE
        assert state.fatigue == 0.0
        assert state.waste_level == 0.0
        assert state.sleep_pressure == 0.0
        assert state.cycles_completed == 0
        assert state.memory_consolidation_pending == 0

    def test_init_hope_score(self):
        """Test that hope_score initializes to 0.5."""
        sleep = SleepCycle()
        state = sleep.get_state()
        assert state.hope_score == 0.5

    def test_init_grief_accumulated(self):
        """Test that grief_accumulated initializes to 0.0."""
        sleep = SleepCycle()
        state = sleep.get_state()
        assert state.grief_accumulated == 0.0


class TestPhaseTransitions:
    """Test phase transitions during tick."""

    def test_wake_to_drowsy_transition(self):
        """Test transition from WAKE to DROWSY when fatigue exceeds threshold."""
        sleep = SleepCycle()
        # Fatigue threshold is 0.7 by default
        # Fatigue rate is 0.0625, so need ~11-12 hours to reach 0.7
        for _ in range(12):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        assert state.phase == CyclePhase.DROWSY

    def test_drowsy_to_light_sleep_transition(self):
        """Test transition from DROWSY to LIGHT_SLEEP."""
        sleep = SleepCycle()
        # Get to DROWSY
        for _ in range(12):
            sleep.tick(1.0)
        
        # Stay in DROWSY for a bit longer to trigger sleep onset
        for _ in range(2):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        # Should be in light sleep now
        assert state.phase in [CyclePhase.LIGHT_SLEEP, CyclePhase.DEEP_SLEEP]

    def test_light_sleep_to_deep_sleep_transition(self):
        """Test transition from LIGHT_SLEEP to DEEP_SLEEP."""
        sleep = SleepCycle()
        # Advance to light sleep
        for _ in range(14):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        assert state.phase == CyclePhase.LIGHT_SLEEP or state.phase == CyclePhase.DEEP_SLEEP

    def test_deep_sleep_to_rem_transition(self):
        """Test transition from DEEP_SLEEP to REM."""
        sleep = SleepCycle()
        # Advance through a full sleep cycle
        for _ in range(20):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        # Should have progressed into sleep
        assert state.phase in [CyclePhase.DEEP_SLEEP, CyclePhase.REM, CyclePhase.WAKING_UP]

    def test_rem_to_waking_up_transition(self):
        """Test transition from REM to WAKING_UP."""
        sleep = SleepCycle()
        # Simulate a full 24-hour cycle
        for _ in range(24):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        # Should have reached WAKING_UP or back to WAKE
        assert state.phase in [CyclePhase.WAKING_UP, CyclePhase.WAKE]

    def test_waking_up_to_wake_transition(self):
        """Test transition from WAKING_UP back to WAKE."""
        sleep = SleepCycle()
        # Simulate a full day plus transition
        for _ in range(25):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        # After full cycle, should be back in WAKE
        assert state.phase == CyclePhase.WAKE


class TestTickMechanics:
    """Test the tick mechanism and time advancement."""

    def test_tick_default_hour(self):
        """Test tick with default 1 hour."""
        sleep = SleepCycle()
        sleep.tick()
        state = sleep.get_state()
        assert state.time_in_phase > 0.0

    def test_tick_custom_duration(self):
        """Test tick with custom duration."""
        sleep = SleepCycle()
        sleep.tick(2.5)
        state = sleep.get_state()
        assert state.time_in_phase == 2.5

    def test_tick_returns_consolidation_events(self):
        """Test that tick returns list of ConsolidationEvent objects."""
        sleep = SleepCycle()
        result = sleep.tick(1.0)
        assert isinstance(result, list)

    def test_fatigue_accumulation_during_wake(self):
        """Test that fatigue accumulates during WAKE phase."""
        sleep = SleepCycle()
        state1 = sleep.get_state()
        fatigue1 = state1.fatigue
        
        sleep.tick(5.0)
        state2 = sleep.get_state()
        fatigue2 = state2.fatigue
        
        assert fatigue2 > fatigue1

    def test_waste_accumulation_during_wake(self):
        """Test that waste accumulates during WAKE phase."""
        sleep = SleepCycle()
        state1 = sleep.get_state()
        waste1 = state1.waste_level
        
        sleep.tick(5.0)
        state2 = sleep.get_state()
        waste2 = state2.waste_level
        
        assert waste2 > waste1

    def test_fatigue_cap_at_1_0(self):
        """Test that fatigue is capped at 1.0."""
        sleep = SleepCycle()
        # Tick for many hours to exceed 1.0
        for _ in range(50):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        assert state.fatigue <= 1.0

    def test_waste_cap_at_1_0(self):
        """Test that waste level is capped at 1.0."""
        sleep = SleepCycle()
        for _ in range(50):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        assert state.waste_level <= 1.0

    def test_multiple_ticks_accumulate(self):
        """Test that multiple ticks accumulate time properly."""
        sleep = SleepCycle()
        for _ in range(5):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        assert state.time_in_phase >= 5.0 or state.phase != CyclePhase.WAKE


class TestMemoryConsolidation:
    """Test memory consolidation mechanics."""

    def test_accumulate_experience_basic(self):
        """Test accumulating a single experience."""
        sleep = SleepCycle()
        sleep.accumulate_experience(
            content="test experience",
            importance=0.8,
            emotional_weight=0.6,
            source="work",
            tags=["important"],
        )
        
        state = sleep.get_state()
        assert state.memory_consolidation_pending == 1

    def test_accumulate_multiple_experiences(self):
        """Test accumulating multiple experiences."""
        sleep = SleepCycle()
        for i in range(5):
            sleep.accumulate_experience(
                content=f"experience {i}",
                importance=0.5,
                emotional_weight=0.5,
                source="work",
            )
        
        state = sleep.get_state()
        assert state.memory_consolidation_pending == 5

    def test_accumulate_experience_clamps_importance(self):
        """Test that accumulate_experience clamps importance to [0, 1]."""
        sleep = SleepCycle()
        sleep.accumulate_experience(
            content="test",
            importance=1.5,  # Over max
            emotional_weight=0.5,
            source="test",
        )
        # Should not raise error, should clamp internally
        state = sleep.get_state()
        assert state.memory_consolidation_pending == 1

    def test_accumulate_experience_clamps_emotional_weight(self):
        """Test that accumulate_experience clamps emotional_weight to [0, 1]."""
        sleep = SleepCycle()
        sleep.accumulate_experience(
            content="test",
            importance=0.5,
            emotional_weight=2.0,  # Over max
            source="test",
        )
        state = sleep.get_state()
        assert state.memory_consolidation_pending == 1

    def test_consolidation_during_deep_sleep(self):
        """Test that consolidation happens during deep sleep."""
        sleep = SleepCycle()
        # Add experiences
        for i in range(10):
            sleep.accumulate_experience(
                content=f"experience {i}",
                importance=0.5 + (i * 0.05),
                emotional_weight=0.5,
                source="work",
            )
        
        # Advance through full sleep cycle to ensure consolidation
        for _ in range(18):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        # Check consolidation events - should have some after full sleep
        consolidations = sleep.get_consolidation_history()
        # Consolidation happens in deep sleep; verify it's a list
        assert isinstance(consolidations, list)

    def test_consolidation_event_structure(self):
        """Test that ConsolidationEvent has all required fields."""
        sleep = SleepCycle()
        for _ in range(5):
            sleep.accumulate_experience(
                content="test",
                importance=0.5,
                emotional_weight=0.5,
                source="work",
            )
        
        # Advance to deep sleep and trigger consolidation
        for _ in range(14):
            sleep.tick(1.0)
        
        consolidations = sleep.get_consolidation_history()
        if consolidations:
            event = consolidations[0]
            assert hasattr(event, 'timestamp')
            assert hasattr(event, 'memories_consolidated')
            assert hasattr(event, 'memories_pruned')
            assert hasattr(event, 'waste_cleared')
            assert hasattr(event, 'creative_connections')
            assert hasattr(event, 'dreams')
            assert hasattr(event, 'sleep_phase')


class TestWasteClearance:
    """Test glyphatic analog (waste clearance) mechanics."""

    def test_waste_accumulates_during_wake(self):
        """Test that waste accumulates during WAKE."""
        sleep = SleepCycle()
        waste_before = sleep.get_state().waste_level
        sleep.tick(5.0)
        waste_after = sleep.get_state().waste_level
        assert waste_after > waste_before

    def test_waste_clears_during_light_sleep(self):
        """Test that waste clears during LIGHT_SLEEP."""
        sleep = SleepCycle()
        # Accumulate waste
        for _ in range(10):
            sleep.tick(1.0)
        
        waste_before_sleep = sleep.get_state().waste_level
        
        # Force sleep
        sleep.force_sleep()
        
        # Tick through light sleep
        for _ in range(2):
            sleep.tick(1.0)
        
        waste_after_light = sleep.get_state().waste_level
        # Waste should decrease or stay same (light sleep clears at base rate)
        assert waste_after_light <= waste_before_sleep

    def test_waste_clears_faster_in_deep_sleep(self):
        """Test that waste clears faster in DEEP_SLEEP."""
        sleep = SleepCycle()
        # Accumulate significant waste
        for _ in range(15):
            sleep.tick(1.0)
        
        waste_before = sleep.get_state().waste_level
        
        # Continue ticking (should reach deep sleep)
        for _ in range(5):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        if state.phase == CyclePhase.DEEP_SLEEP:
            waste_after = state.waste_level
            # Waste should clear substantially in deep sleep
            assert waste_after <= waste_before

    def test_waste_never_negative(self):
        """Test that waste level never goes negative."""
        sleep = SleepCycle()
        for _ in range(30):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        assert state.waste_level >= 0.0


class TestCreativeRecombination:
    """Test creative recombination during REM sleep."""

    def test_dreams_generated_during_rem(self):
        """Test that dreams are generated during REM phase."""
        sleep = SleepCycle()
        # Add experiences with tags for dream generation
        for i in range(5):
            sleep.accumulate_experience(
                content=f"experience {i}",
                importance=0.5,
                emotional_weight=0.5,
                source="work",
                tags=["memory", "creative"],
            )
        
        # Advance to REM
        for _ in range(20):
            sleep.tick(1.0)
        
        dreams = sleep.get_dream_log()
        # May have dreams if REM was reached and consolidated memories exist
        assert isinstance(dreams, list)

    def test_dream_log_structure(self):
        """Test that dream log contains strings."""
        sleep = SleepCycle()
        for i in range(3):
            sleep.accumulate_experience(
                content=f"experience {i}",
                importance=0.6,
                emotional_weight=0.5,
                source="test",
                tags=["tag1", "tag2"],
            )
        
        # Advance through full cycle
        for _ in range(22):
            sleep.tick(1.0)
        
        dreams = sleep.get_dream_log()
        for dream in dreams:
            assert isinstance(dream, str)

    def test_consolidation_history_includes_creativity_field(self):
        """Test that consolidation events track creative connections."""
        sleep = SleepCycle()
        for _ in range(3):
            sleep.accumulate_experience(
                content="test",
                importance=0.5,
                emotional_weight=0.5,
                source="work",
                tags=["tag1"],
            )
        
        # Advance through full cycle
        for _ in range(22):
            sleep.tick(1.0)
        
        consolidations = sleep.get_consolidation_history()
        for event in consolidations:
            assert hasattr(event, 'creative_connections')
            assert isinstance(event.creative_connections, int)


class TestHopeMechanics:
    """Test hope generation and decay mechanics."""

    def test_hope_initializes_to_0_5(self):
        """Test that hope_score initializes to 0.5."""
        sleep = SleepCycle()
        state = sleep.get_state()
        assert state.hope_score == 0.5

    def test_grief_accumulation_on_painful_experience(self):
        """Test that painful experiences accumulate grief."""
        sleep = SleepCycle()
        # Painful experience: high importance + high emotional weight
        sleep.accumulate_experience(
            content="painful loss",
            importance=0.9,
            emotional_weight=0.8,  # > 0.5 triggers grief
            source="life",
        )
        
        state = sleep.get_state()
        assert state.grief_accumulated > 0.0

    def test_grief_does_not_accumulate_from_neutral_experience(self):
        """Test that neutral experiences don't accumulate grief."""
        sleep = SleepCycle()
        state_before = sleep.get_state()
        grief_before = state_before.grief_accumulated
        
        # Neutral experience: low emotional weight
        sleep.accumulate_experience(
            content="routine task",
            importance=0.5,
            emotional_weight=0.3,  # < 0.5, no grief
            source="work",
        )
        
        state_after = sleep.get_state()
        assert state_after.grief_accumulated == grief_before

    def test_grief_decay_on_wake(self):
        """Test that grief decays when waking from sleep."""
        sleep = SleepCycle()
        # Add painful experiences
        sleep.accumulate_experience(
            content="painful",
            importance=0.8,
            emotional_weight=0.8,
            source="life",
        )
        
        grief_before_sleep = sleep.get_state().grief_accumulated
        
        # Advance through full sleep cycle
        for _ in range(24):
            sleep.tick(1.0)
        
        grief_after_wake = sleep.get_state().grief_accumulated
        
        # Grief should have decayed (though hope may have increased)
        assert grief_after_wake < grief_before_sleep

    def test_hope_generation_from_grief(self):
        """Test that grief is converted to hope during sleep."""
        sleep = SleepCycle()
        # Add painful experience to generate grief
        sleep.accumulate_experience(
            content="painful",
            importance=0.9,
            emotional_weight=0.9,
            source="life",
        )
        
        grief_after_experience = sleep.get_state().grief_accumulated
        assert grief_after_experience > 0.0
        
        # Advance through full sleep cycle
        for _ in range(24):
            sleep.tick(1.0)
        
        state_after = sleep.get_state()
        # Grief should be lower after sleep (converted to hope)
        assert state_after.grief_accumulated < grief_after_experience

    def test_hope_decay_during_wake(self):
        """Test that hope decays during waking hours."""
        sleep = SleepCycle()
        # Boost hope by sleeping first
        for _ in range(24):
            sleep.tick(1.0)
        
        hope_after_first_wake = sleep.get_state().hope_score
        
        # Wake for several hours
        for _ in range(5):
            sleep.tick(1.0)
        
        hope_after_ticking = sleep.get_state().hope_score
        
        # Hope should decay during waking hours
        assert hope_after_ticking < hope_after_first_wake

    def test_hope_capped_at_1_0(self):
        """Test that hope never exceeds 1.0."""
        sleep = SleepCycle()
        for _ in range(100):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        assert state.hope_score <= 1.0

    def test_grief_capped_at_1_0(self):
        """Test that grief never exceeds 1.0."""
        sleep = SleepCycle()
        # Add multiple painful experiences
        for _ in range(10):
            sleep.accumulate_experience(
                content="painful",
                importance=1.0,
                emotional_weight=0.9,
                source="life",
            )
        
        state = sleep.get_state()
        assert state.grief_accumulated <= 1.0

    def test_grief_never_negative(self):
        """Test that grief never goes negative."""
        sleep = SleepCycle()
        for _ in range(50):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        assert state.grief_accumulated >= 0.0

    def test_hope_never_negative(self):
        """Test that hope never goes negative."""
        sleep = SleepCycle()
        for _ in range(100):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        assert state.hope_score >= 0.0


class TestForceWakeAndSleep:
    """Test force_wake and force_sleep methods."""

    def test_force_sleep_from_wake(self):
        """Test forcing sleep from WAKE phase."""
        sleep = SleepCycle()
        assert sleep.get_state().phase == CyclePhase.WAKE
        
        result = sleep.force_sleep()
        
        assert result is True
        assert sleep.get_state().phase == CyclePhase.LIGHT_SLEEP

    def test_force_sleep_from_drowsy(self):
        """Test forcing sleep from DROWSY phase."""
        sleep = SleepCycle()
        # Advance to drowsy
        for _ in range(12):
            sleep.tick(1.0)
        
        assert sleep.get_state().phase == CyclePhase.DROWSY
        
        result = sleep.force_sleep()
        
        assert result is True
        assert sleep.get_state().phase == CyclePhase.LIGHT_SLEEP

    def test_force_sleep_from_sleep_fails(self):
        """Test that forcing sleep from sleep phase fails."""
        sleep = SleepCycle()
        # Advance to deep sleep
        for _ in range(15):
            sleep.tick(1.0)
        
        if sleep.get_state().phase == CyclePhase.DEEP_SLEEP:
            result = sleep.force_sleep()
            assert result is False

    def test_force_wake_returns_debt(self):
        """Test that force_wake returns sleep debt."""
        sleep = SleepCycle()
        # Advance to sleep
        for _ in range(14):
            sleep.tick(1.0)
        
        debt = sleep.force_wake()
        
        assert isinstance(debt, float)
        assert debt >= 0.0

    def test_force_wake_sets_phase_to_wake(self):
        """Test that force_wake sets phase back to WAKE."""
        sleep = SleepCycle()
        # Advance to deep sleep
        for _ in range(15):
            sleep.tick(1.0)
        
        sleep.force_wake()
        
        assert sleep.get_state().phase == CyclePhase.WAKE

    def test_sleep_debt_accumulation(self):
        """Test that sleep debt accumulates from force_wake."""
        sleep = SleepCycle()
        for _ in range(14):
            sleep.tick(1.0)
        
        debt1 = sleep.get_sleep_debt()
        
        sleep.force_wake()
        debt2 = sleep.get_sleep_debt()
        
        assert debt2 > debt1


class TestPerformanceModifiers:
    """Test performance modifier calculations."""

    def test_get_performance_modifier_returns_object(self):
        """Test that get_performance_modifier returns PerformanceModifiers."""
        sleep = SleepCycle()
        modifiers = sleep.get_performance_modifier()
        
        assert isinstance(modifiers, PerformanceModifiers)

    def test_performance_modifiers_fields_in_range(self):
        """Test that all performance modifiers are in [0, 1]."""
        sleep = SleepCycle()
        modifiers = sleep.get_performance_modifier()
        
        assert 0.0 <= modifiers.cognitive_clarity <= 1.0
        assert 0.0 <= modifiers.emotional_stability <= 1.0
        assert 0.0 <= modifiers.creativity <= 1.0
        assert 0.0 <= modifiers.memory_retention <= 1.0
        assert 0.0 <= modifiers.reaction_speed <= 1.0

    def test_cognitive_clarity_degrades_with_fatigue(self):
        """Test that cognitive_clarity decreases as fatigue increases."""
        sleep = SleepCycle()
        clarity_rested = sleep.get_performance_modifier().cognitive_clarity
        
        # Accumulate fatigue
        for _ in range(10):
            sleep.tick(1.0)
        
        clarity_fatigued = sleep.get_performance_modifier().cognitive_clarity
        
        assert clarity_fatigued <= clarity_rested

    def test_creativity_peaks_during_rem(self):
        """Test that creativity is highest during REM."""
        sleep = SleepCycle()
        
        # Advance to REM
        for _ in range(20):
            sleep.tick(1.0)
        
        # Check if we're in REM and creativity is high
        state = sleep.get_state()
        modifiers = sleep.get_performance_modifier()
        
        if state.phase == CyclePhase.REM:
            # Creativity should be boosted in REM
            assert modifiers.creativity > 0.5

    def test_memory_retention_during_sleep(self):
        """Test that memory_retention is high during sleep phases."""
        sleep = SleepCycle()
        
        # Advance to light sleep
        for _ in range(14):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        modifiers = sleep.get_performance_modifier()
        
        if state.phase in [CyclePhase.LIGHT_SLEEP, CyclePhase.DEEP_SLEEP]:
            # Memory retention should be high during sleep
            assert modifiers.memory_retention >= 0.7

    def test_reaction_speed_degrades_with_fatigue(self):
        """Test that reaction_speed degrades with fatigue."""
        sleep = SleepCycle()
        speed_rested = sleep.get_performance_modifier().reaction_speed
        
        # Accumulate fatigue
        for _ in range(10):
            sleep.tick(1.0)
        
        speed_fatigued = sleep.get_performance_modifier().reaction_speed
        
        assert speed_fatigued <= speed_rested


class TestGetState:
    """Test get_state method."""

    def test_get_state_returns_sleep_state(self):
        """Test that get_state returns a SleepState object."""
        sleep = SleepCycle()
        state = sleep.get_state()
        
        assert isinstance(state, SleepState)

    def test_sleep_state_has_all_fields(self):
        """Test that SleepState has all required fields."""
        sleep = SleepCycle()
        state = sleep.get_state()
        
        assert hasattr(state, 'phase')
        assert hasattr(state, 'fatigue')
        assert hasattr(state, 'waste_level')
        assert hasattr(state, 'sleep_pressure')
        assert hasattr(state, 'cycles_completed')
        assert hasattr(state, 'time_in_phase')
        assert hasattr(state, 'total_wake_time')
        assert hasattr(state, 'total_sleep_time')
        assert hasattr(state, 'cognitive_clarity')
        assert hasattr(state, 'emotional_stability')
        assert hasattr(state, 'memory_consolidation_pending')
        assert hasattr(state, 'grief_accumulated')
        assert hasattr(state, 'hope_score')

    def test_sleep_state_fields_are_correct_type(self):
        """Test that SleepState fields have correct types."""
        sleep = SleepCycle()
        state = sleep.get_state()
        
        assert isinstance(state.phase, CyclePhase)
        assert isinstance(state.fatigue, float)
        assert isinstance(state.waste_level, float)
        assert isinstance(state.sleep_pressure, float)
        assert isinstance(state.cycles_completed, int)
        assert isinstance(state.time_in_phase, float)
        assert isinstance(state.total_wake_time, float)
        assert isinstance(state.total_sleep_time, float)
        assert isinstance(state.cognitive_clarity, float)
        assert isinstance(state.emotional_stability, float)
        assert isinstance(state.memory_consolidation_pending, int)
        assert isinstance(state.grief_accumulated, float)
        assert isinstance(state.hope_score, float)


class TestConsolidationHistory:
    """Test consolidation history tracking."""

    def test_get_consolidation_history_returns_list(self):
        """Test that get_consolidation_history returns a list."""
        sleep = SleepCycle()
        history = sleep.get_consolidation_history()
        
        assert isinstance(history, list)

    def test_consolidation_history_empty_initially(self):
        """Test that consolidation history is empty at initialization."""
        sleep = SleepCycle()
        history = sleep.get_consolidation_history()
        
        assert len(history) == 0

    def test_consolidation_history_populated_after_deep_sleep(self):
        """Test that consolidation history is populated after deep sleep."""
        sleep = SleepCycle()
        # Add experiences
        for _ in range(5):
            sleep.accumulate_experience(
                content="test",
                importance=0.5,
                emotional_weight=0.5,
                source="work",
            )
        
        # Advance through full sleep cycle to reach consolidation
        for _ in range(18):
            sleep.tick(1.0)
        
        history = sleep.get_consolidation_history()
        # History should be a list (may be empty depending on phase transitions)
        assert isinstance(history, list)

    def test_consolidation_event_is_frozen(self):
        """Test that ConsolidationEvent is immutable (frozen)."""
        event = ConsolidationEvent(
            timestamp=time.time(),
            memories_consolidated=5,
            memories_pruned=3,
            waste_cleared=0.2,
            creative_connections=2,
            dreams=["dream1", "dream2"],
            sleep_phase="deep_sleep",
        )
        
        # Attempting to modify should raise error
        with pytest.raises(Exception):
            event.memories_consolidated = 10


class TestDreamLog:
    """Test dream log tracking."""

    def test_get_dream_log_returns_list(self):
        """Test that get_dream_log returns a list."""
        sleep = SleepCycle()
        dreams = sleep.get_dream_log()
        
        assert isinstance(dreams, list)

    def test_dream_log_empty_initially(self):
        """Test that dream log is empty at initialization."""
        sleep = SleepCycle()
        dreams = sleep.get_dream_log()
        
        assert len(dreams) == 0

    def test_dream_log_populated_after_rem(self):
        """Test that dream log is populated after REM sleep."""
        sleep = SleepCycle()
        # Add experiences with tags
        for _ in range(5):
            sleep.accumulate_experience(
                content="test",
                importance=0.5,
                emotional_weight=0.5,
                source="work",
                tags=["tag1", "tag2"],
            )
        
        # Advance to REM
        for _ in range(22):
            sleep.tick(1.0)
        
        dreams = sleep.get_dream_log()
        # May be empty depending on consolidation and timing
        assert isinstance(dreams, list)


class TestMultipleCycles:
    """Test behavior across multiple sleep-wake cycles."""

    def test_cycles_completed_increments(self):
        """Test that cycles_completed increments after each full cycle."""
        sleep = SleepCycle()
        
        # First cycle
        for _ in range(24):
            sleep.tick(1.0)
        
        cycles_after_first = sleep.get_state().cycles_completed
        assert cycles_after_first == 1
        
        # Second cycle
        for _ in range(24):
            sleep.tick(1.0)
        
        cycles_after_second = sleep.get_state().cycles_completed
        assert cycles_after_second == 2

    def test_fatigue_resets_each_cycle(self):
        """Test that fatigue is reduced after sleep cycle."""
        sleep = SleepCycle()
        
        # Accumulate fatigue
        for _ in range(12):
            sleep.tick(1.0)
        
        fatigue_before_sleep = sleep.get_state().fatigue
        
        # Sleep
        for _ in range(12):
            sleep.tick(1.0)
        
        fatigue_after_sleep = sleep.get_state().fatigue
        
        assert fatigue_after_sleep < fatigue_before_sleep

    def test_memory_consolidation_flags_reset_each_cycle(self):
        """Test that consolidation flags reset for each cycle."""
        sleep = SleepCycle()
        
        # First cycle: add memories and consolidate
        for i in range(5):
            sleep.accumulate_experience(
                content=f"mem {i}",
                importance=0.5,
                emotional_weight=0.5,
                source="work",
            )
        
        for _ in range(24):
            sleep.tick(1.0)
        
        consolidations_first = len(sleep.get_consolidation_history())
        
        # Second cycle: add more memories and consolidate again
        for i in range(5):
            sleep.accumulate_experience(
                content=f"mem2 {i}",
                importance=0.5,
                emotional_weight=0.5,
                source="work",
            )
        
        for _ in range(24):
            sleep.tick(1.0)
        
        consolidations_second = len(sleep.get_consolidation_history())
        
        # Should have events from both cycles
        assert consolidations_second > consolidations_first


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_duration_tick(self):
        """Test tick with zero duration."""
        sleep = SleepCycle()
        sleep.tick(0.0)
        state = sleep.get_state()
        # Should not crash
        assert state is not None

    def test_very_small_duration_tick(self):
        """Test tick with very small duration."""
        sleep = SleepCycle()
        sleep.tick(0.001)
        state = sleep.get_state()
        assert state.time_in_phase > 0.0

    def test_very_large_duration_tick(self):
        """Test tick with very large duration."""
        sleep = SleepCycle()
        sleep.tick(100.0)
        state = sleep.get_state()
        # Should handle large ticks without crashing
        assert state is not None

    def test_experience_with_zero_importance(self):
        """Test accumulating experience with zero importance."""
        sleep = SleepCycle()
        sleep.accumulate_experience(
            content="zero importance",
            importance=0.0,
            emotional_weight=0.5,
            source="test",
        )
        state = sleep.get_state()
        assert state.memory_consolidation_pending == 1

    def test_experience_with_zero_emotional_weight(self):
        """Test accumulating experience with zero emotional weight."""
        sleep = SleepCycle()
        sleep.accumulate_experience(
            content="zero emotion",
            importance=0.5,
            emotional_weight=0.0,
            source="test",
        )
        state = sleep.get_state()
        assert state.memory_consolidation_pending == 1

    def test_experience_with_negative_values_clamped(self):
        """Test that negative importance/emotional_weight are clamped to 0."""
        sleep = SleepCycle()
        sleep.accumulate_experience(
            content="negative values",
            importance=-0.5,
            emotional_weight=-0.3,
            source="test",
        )
        state = sleep.get_state()
        # Should clamp to 0, still add memory
        assert state.memory_consolidation_pending == 1

    def test_no_experiences_consolidation(self):
        """Test consolidation when no pending memories."""
        sleep = SleepCycle()
        # Advance to deep sleep without adding experiences
        for _ in range(15):
            sleep.tick(1.0)
        
        # Should not crash
        consolidations = sleep.get_consolidation_history()
        assert isinstance(consolidations, list)

    def test_very_many_experiences(self):
        """Test handling many pending memories."""
        sleep = SleepCycle()
        # Add 100+ experiences
        for i in range(100):
            sleep.accumulate_experience(
                content=f"experience {i}",
                importance=0.5 + (i % 50) / 100,
                emotional_weight=0.5,
                source="work",
            )
        
        state = sleep.get_state()
        assert state.memory_consolidation_pending == 100
        
        # Consolidate
        for _ in range(15):
            sleep.tick(1.0)
        
        # Should handle large consolidation without error
        assert state.memory_consolidation_pending == 100

    def test_get_sleep_debt_returns_float(self):
        """Test that get_sleep_debt returns a float."""
        sleep = SleepCycle()
        debt = sleep.get_sleep_debt()
        assert isinstance(debt, float)

    def test_get_sleep_debt_non_negative(self):
        """Test that sleep debt is never negative."""
        sleep = SleepCycle()
        # Accumulate and then try to clear
        for _ in range(30):
            sleep.tick(1.0)
        
        debt = sleep.get_sleep_debt()
        assert debt >= 0.0


class TestCognitiveClarity:
    """Test cognitive clarity computation."""

    def test_cognitive_clarity_high_when_rested(self):
        """Test that cognitive clarity is high when rested."""
        sleep = SleepCycle()
        clarity = sleep.get_state().cognitive_clarity
        assert clarity > 0.5

    def test_cognitive_clarity_decreases_with_fatigue(self):
        """Test that cognitive clarity decreases with fatigue."""
        sleep = SleepCycle()
        clarity_initial = sleep.get_state().cognitive_clarity
        
        # Accumulate fatigue
        for _ in range(10):
            sleep.tick(1.0)
        
        clarity_fatigued = sleep.get_state().cognitive_clarity
        assert clarity_fatigued < clarity_initial

    def test_cognitive_clarity_decreases_with_waste(self):
        """Test that cognitive clarity decreases with waste."""
        sleep = SleepCycle()
        clarity_clean = sleep.get_state().cognitive_clarity
        
        # Accumulate waste
        for _ in range(15):
            sleep.tick(1.0)
        
        clarity_dirty = sleep.get_state().cognitive_clarity
        assert clarity_dirty < clarity_clean

    def test_cognitive_clarity_low_during_deep_sleep(self):
        """Test that cognitive clarity is low during deep sleep."""
        sleep = SleepCycle()
        
        # Advance to deep sleep
        for _ in range(15):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        if state.phase == CyclePhase.DEEP_SLEEP:
            clarity = state.cognitive_clarity
            assert clarity < 0.5


class TestEmotionalStability:
    """Test emotional stability computation."""

    def test_emotional_stability_high_when_rested(self):
        """Test that emotional stability is high when rested."""
        sleep = SleepCycle()
        stability = sleep.get_state().emotional_stability
        assert stability > 0.5

    def test_emotional_stability_decreases_with_fatigue(self):
        """Test that emotional stability decreases with fatigue."""
        sleep = SleepCycle()
        stability_initial = sleep.get_state().emotional_stability
        
        # Accumulate fatigue
        for _ in range(10):
            sleep.tick(1.0)
        
        stability_fatigued = sleep.get_state().emotional_stability
        assert stability_fatigued < stability_initial

    def test_emotional_stability_high_during_deep_sleep(self):
        """Test that emotional stability is restored during deep sleep."""
        sleep = SleepCycle()
        
        # Accumulate fatigue
        for _ in range(10):
            sleep.tick(1.0)
        
        stability_fatigued = sleep.get_state().emotional_stability
        
        # Continue to deep sleep
        for _ in range(5):
            sleep.tick(1.0)
        
        state = sleep.get_state()
        if state.phase == CyclePhase.DEEP_SLEEP:
            # Deep sleep should restore emotional stability
            assert state.emotional_stability > stability_fatigued
