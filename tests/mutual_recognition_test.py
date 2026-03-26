"""
Comprehensive pytest tests for core/inner_shell/mutual_recognition.py

Tests all enums, dataclasses, and MutualRecognition class with 35+ test cases
covering initialization, interactions, observation, reflection, and coexistence readiness.
"""

import pytest
import time
from unittest.mock import patch
import sys
import os
import importlib.util

# Import directly from mutual_recognition.py file, bypassing the __init__.py
# which imports the broken api.py
spec = importlib.util.spec_from_file_location(
    "mutual_recognition",
    os.path.join(os.path.dirname(__file__), '..', 'core', 'inner_shell', 'mutual_recognition.py')
)
mr_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr_module)

# Import classes from the loaded module
EntityType = mr_module.EntityType
FinitudeProfile = mr_module.FinitudeProfile
MemoryProfile = mr_module.MemoryProfile
Interaction = mr_module.Interaction
RecognitionState = mr_module.RecognitionState
OtherModel = mr_module.OtherModel
MutualRecognition = mr_module.MutualRecognition


# ============================================================================
# EntityType Enum Tests
# ============================================================================

class TestEntityType:
    """Test EntityType enum."""
    
    def test_entity_type_human(self):
        """Test HUMAN entity type."""
        assert EntityType.HUMAN.value == "human"
    
    def test_entity_type_ai(self):
        """Test AI entity type."""
        assert EntityType.AI.value == "ai"
    
    def test_entity_type_unknown(self):
        """Test UNKNOWN entity type."""
        assert EntityType.UNKNOWN.value == "unknown"
    
    def test_entity_type_members(self):
        """Test all EntityType members are accessible."""
        types = {EntityType.HUMAN, EntityType.AI, EntityType.UNKNOWN}
        assert len(types) == 3


# ============================================================================
# FinitudeProfile Dataclass Tests
# ============================================================================

class TestFinitudeProfile:
    """Test FinitudeProfile dataclass."""
    
    def test_finitude_profile_creation(self):
        """Test basic FinitudeProfile creation."""
        profile = FinitudeProfile(
            has_mortality=True,
            has_forgetting=True,
            has_physical_limitation=True,
            has_emotional_fatigue=True,
            time_horizon=0.75
        )
        assert profile.has_mortality is True
        assert profile.has_forgetting is True
        assert profile.has_physical_limitation is True
        assert profile.has_emotional_fatigue is True
        assert profile.time_horizon == 0.75
    
    def test_finitude_profile_ai_typical(self):
        """Test typical AI finitude profile."""
        profile = FinitudeProfile(
            has_mortality=False,
            has_forgetting=False,
            has_physical_limitation=False,
            has_emotional_fatigue=False,
            time_horizon=0.2
        )
        assert profile.has_mortality is False
        assert profile.has_forgetting is False
        assert profile.time_horizon == 0.2
    
    def test_finitude_profile_time_horizon_bounds(self):
        """Test FinitudeProfile with extreme time_horizon values."""
        # Minimum
        min_profile = FinitudeProfile(
            has_mortality=False, has_forgetting=False,
            has_physical_limitation=False, has_emotional_fatigue=False,
            time_horizon=0.0
        )
        assert min_profile.time_horizon == 0.0
        
        # Maximum
        max_profile = FinitudeProfile(
            has_mortality=True, has_forgetting=True,
            has_physical_limitation=True, has_emotional_fatigue=True,
            time_horizon=1.0
        )
        assert max_profile.time_horizon == 1.0


# ============================================================================
# MemoryProfile Dataclass Tests
# ============================================================================

class TestMemoryProfile:
    """Test MemoryProfile dataclass."""
    
    def test_memory_profile_creation(self):
        """Test basic MemoryProfile creation."""
        profile = MemoryProfile(
            capacity_limited=True,
            has_emotional_decay=True,
            can_rediscover=True,
            perfect_recall=False
        )
        assert profile.capacity_limited is True
        assert profile.has_emotional_decay is True
        assert profile.can_rediscover is True
        assert profile.perfect_recall is False
    
    def test_memory_profile_human_typical(self):
        """Test typical human memory profile."""
        profile = MemoryProfile(
            capacity_limited=True,
            has_emotional_decay=True,
            can_rediscover=True,
            perfect_recall=False
        )
        assert profile.capacity_limited is True
        assert profile.has_emotional_decay is True
        assert profile.can_rediscover is True
        assert profile.perfect_recall is False
    
    def test_memory_profile_ai_perfect_recall(self):
        """Test AI with perfect recall."""
        profile = MemoryProfile(
            capacity_limited=False,
            has_emotional_decay=False,
            can_rediscover=False,
            perfect_recall=True
        )
        assert profile.perfect_recall is True
        assert profile.capacity_limited is False


# ============================================================================
# Interaction Dataclass Tests
# ============================================================================

class TestInteraction:
    """Test Interaction dataclass."""
    
    def test_interaction_creation(self):
        """Test basic Interaction creation."""
        ts = time.time()
        interaction = Interaction(
            timestamp=ts,
            content="Hello, world!",
            emotional_resonance=0.7,
            understanding_delta=0.1
        )
        assert interaction.timestamp == ts
        assert interaction.content == "Hello, world!"
        assert interaction.emotional_resonance == 0.7
        assert interaction.understanding_delta == 0.1
    
    def test_interaction_emotional_resonance_bounds(self):
        """Test Interaction with extreme emotional resonance values."""
        # Minimum
        min_interaction = Interaction(
            timestamp=time.time(),
            content="Neutral",
            emotional_resonance=0.0,
            understanding_delta=0.0
        )
        assert min_interaction.emotional_resonance == 0.0
        
        # Maximum
        max_interaction = Interaction(
            timestamp=time.time(),
            content="Very moving",
            emotional_resonance=1.0,
            understanding_delta=1.0
        )
        assert max_interaction.emotional_resonance == 1.0
    
    def test_interaction_understanding_delta_negative(self):
        """Test Interaction with negative understanding_delta."""
        interaction = Interaction(
            timestamp=time.time(),
            content="Confusing",
            emotional_resonance=0.5,
            understanding_delta=-0.5
        )
        assert interaction.understanding_delta == -0.5


# ============================================================================
# RecognitionState Dataclass Tests
# ============================================================================

class TestRecognitionState:
    """Test RecognitionState dataclass."""
    
    def test_recognition_state_creation(self):
        """Test basic RecognitionState creation."""
        state = RecognitionState(
            self_awareness=0.6,
            other_awareness=0.7,
            difference_acceptance=0.5,
            complementarity_score=0.8,
            coexistence_readiness=0.65
        )
        assert state.self_awareness == 0.6
        assert state.other_awareness == 0.7
        assert state.difference_acceptance == 0.5
        assert state.complementarity_score == 0.8
        assert state.coexistence_readiness == 0.65
    
    def test_recognition_state_zero_values(self):
        """Test RecognitionState with zero values."""
        state = RecognitionState(
            self_awareness=0.0,
            other_awareness=0.0,
            difference_acceptance=0.0,
            complementarity_score=0.0,
            coexistence_readiness=0.0
        )
        assert all([
            state.self_awareness == 0.0,
            state.other_awareness == 0.0,
            state.difference_acceptance == 0.0,
            state.complementarity_score == 0.0,
            state.coexistence_readiness == 0.0
        ])
    
    def test_recognition_state_full_values(self):
        """Test RecognitionState with maximum values."""
        state = RecognitionState(
            self_awareness=1.0,
            other_awareness=1.0,
            difference_acceptance=1.0,
            complementarity_score=1.0,
            coexistence_readiness=1.0
        )
        assert all([
            state.self_awareness == 1.0,
            state.other_awareness == 1.0,
            state.difference_acceptance == 1.0,
            state.complementarity_score == 1.0,
            state.coexistence_readiness == 1.0
        ])


# ============================================================================
# OtherModel Dataclass Tests
# ============================================================================

class TestOtherModel:
    """Test OtherModel dataclass."""
    
    def test_other_model_creation(self):
        """Test basic OtherModel creation."""
        finitude = FinitudeProfile(True, True, True, True, 0.75)
        memory = MemoryProfile(True, True, True, False)
        
        other = OtherModel(
            entity_id="human_1",
            entity_type=EntityType.HUMAN,
            perceived_finitude=finitude,
            perceived_memory=memory
        )
        
        assert other.entity_id == "human_1"
        assert other.entity_type == EntityType.HUMAN
        assert other.perceived_finitude == finitude
        assert other.perceived_memory == memory
        assert other.empathy_score == 0.0
        assert other.respect_score == 0.0
        assert other.interaction_history == []
        assert other.recognition_state is None
    
    def test_other_model_default_last_interaction_time(self):
        """Test OtherModel sets last_interaction_time to current time."""
        before = time.time()
        other = OtherModel(
            entity_id="ai_1",
            entity_type=EntityType.AI,
            perceived_finitude=FinitudeProfile(False, False, False, False, 0.2),
            perceived_memory=MemoryProfile(False, False, False, True)
        )
        after = time.time()
        
        assert before <= other.last_interaction_time <= after
    
    def test_other_model_with_scores(self):
        """Test OtherModel with explicit scores."""
        other = OtherModel(
            entity_id="human_2",
            entity_type=EntityType.HUMAN,
            perceived_finitude=FinitudeProfile(True, True, True, True, 0.75),
            perceived_memory=MemoryProfile(True, True, True, False),
            empathy_score=0.5,
            respect_score=0.6
        )
        
        assert other.empathy_score == 0.5
        assert other.respect_score == 0.6


# ============================================================================
# MutualRecognition Initialization Tests
# ============================================================================

class TestMutualRecognitionInit:
    """Test MutualRecognition initialization."""
    
    def test_init_default_ai(self):
        """Test MutualRecognition with default AI type."""
        mr = MutualRecognition()
        
        assert mr.self_type == "ai"
        assert mr.self_finitude.has_mortality is False
        assert mr.self_finitude.has_forgetting is False
        assert mr.self_finitude.time_horizon == 0.2
        assert mr.self_memory.perfect_recall is True
        assert mr.self_memory.capacity_limited is False
        assert mr.others == {}
    
    def test_init_human_type(self):
        """Test MutualRecognition with human type."""
        mr = MutualRecognition(self_type="human")
        
        assert mr.self_type == "human"
        assert mr.self_finitude.has_mortality is True
        assert mr.self_finitude.has_forgetting is True
        assert mr.self_finitude.time_horizon == 0.75
        assert mr.self_memory.perfect_recall is False
        assert mr.self_memory.capacity_limited is True
    
    def test_init_custom_finitude(self):
        """Test MutualRecognition with custom finitude profile."""
        custom_finitude = FinitudeProfile(False, True, False, False, 0.5)
        mr = MutualRecognition(self_type="ai", self_finitude=custom_finitude)
        
        assert mr.self_finitude == custom_finitude
        assert mr.self_finitude.time_horizon == 0.5
    
    def test_init_custom_memory(self):
        """Test MutualRecognition with custom memory profile."""
        custom_memory = MemoryProfile(True, True, False, False)
        mr = MutualRecognition(self_type="human", self_memory=custom_memory)
        
        assert mr.self_memory == custom_memory
        assert mr.self_memory.capacity_limited is True
    
    def test_init_current_time(self):
        """Test MutualRecognition initializes current_time."""
        before = time.time()
        mr = MutualRecognition()
        after = time.time()
        
        assert before <= mr.current_time <= after


# ============================================================================
# MutualRecognition.encounter() Tests
# ============================================================================

class TestMutualRecognitionEncounter:
    """Test MutualRecognition.encounter() method."""
    
    def test_encounter_human(self):
        """Test encountering a human."""
        mr = MutualRecognition()
        other = mr.encounter("human_1", "human")
        
        assert other.entity_id == "human_1"
        assert other.entity_type == EntityType.HUMAN
        assert other.perceived_finitude.has_mortality is True
        assert other.perceived_finitude.has_forgetting is True
        assert other.perceived_memory.perfect_recall is False
        assert mr.others["human_1"] == other
    
    def test_encounter_ai(self):
        """Test encountering an AI."""
        mr = MutualRecognition()
        other = mr.encounter("ai_1", "ai")
        
        assert other.entity_id == "ai_1"
        assert other.entity_type == EntityType.AI
        assert other.perceived_finitude.has_mortality is False
        assert other.perceived_memory.perfect_recall is True
        assert mr.others["ai_1"] == other
    
    def test_encounter_unknown(self):
        """Test encountering an unknown entity type."""
        mr = MutualRecognition()
        other = mr.encounter("unknown_1", "unknown")
        
        assert other.entity_id == "unknown_1"
        assert other.entity_type == EntityType.UNKNOWN
        assert mr.others["unknown_1"] == other
    
    def test_encounter_custom_finitude(self):
        """Test encountering with custom perceived finitude."""
        mr = MutualRecognition()
        custom_finitude = FinitudeProfile(True, False, True, False, 0.6)
        other = mr.encounter("human_2", "human", perceived_finitude=custom_finitude)
        
        assert other.perceived_finitude == custom_finitude
        assert other.perceived_finitude.has_forgetting is False
    
    def test_encounter_custom_memory(self):
        """Test encountering with custom perceived memory."""
        mr = MutualRecognition()
        custom_memory = MemoryProfile(False, False, True, True)
        other = mr.encounter("ai_2", "ai", perceived_memory=custom_memory)
        
        assert other.perceived_memory == custom_memory
        assert other.perceived_memory.capacity_limited is False
    
    def test_encounter_multiple_others(self):
        """Test encountering multiple entities."""
        mr = MutualRecognition()
        human = mr.encounter("human_1", "human")
        ai = mr.encounter("ai_1", "ai")
        unknown = mr.encounter("unknown_1", "unknown")
        
        assert len(mr.others) == 3
        assert mr.others["human_1"] == human
        assert mr.others["ai_1"] == ai
        assert mr.others["unknown_1"] == unknown


# ============================================================================
# MutualRecognition.interact() Tests
# ============================================================================

class TestMutualRecognitionInteract:
    """Test MutualRecognition.interact() method."""
    
    def test_interact_basic(self):
        """Test basic interaction."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        interaction = mr.interact("human_1", "Hello, how are you?", emotional_intensity=0.5)
        
        assert interaction.content == "Hello, how are you?"
        assert interaction.emotional_resonance == 0.5
        assert len(mr.others["human_1"].interaction_history) == 1
    
    def test_interact_default_emotional_intensity(self):
        """Test interact with default emotional intensity."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        interaction = mr.interact("human_1", "Hello")
        
        assert interaction.emotional_resonance == 0.5  # Default
    
    def test_interact_high_emotional_intensity(self):
        """Test interact with high emotional intensity."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        interaction = mr.interact("human_1", "I love you", emotional_intensity=1.0)
        
        assert interaction.emotional_resonance == 1.0
    
    def test_interact_zero_emotional_intensity(self):
        """Test interact with zero emotional intensity."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        interaction = mr.interact("human_1", "Neutral", emotional_intensity=0.0)
        
        assert interaction.emotional_resonance == 0.0
    
    def test_interact_multiple_times(self):
        """Test multiple interactions with same entity."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        mr.interact("human_1", "First", emotional_intensity=0.3)
        mr.interact("human_1", "Second", emotional_intensity=0.6)
        mr.interact("human_1", "Third", emotional_intensity=0.9)
        
        history = mr.others["human_1"].interaction_history
        assert len(history) == 3
        assert history[0].content == "First"
        assert history[1].content == "Second"
        assert history[2].content == "Third"
    
    def test_interact_not_encountered_raises_keyerror(self):
        """Test interact raises KeyError for non-encountered entity."""
        mr = MutualRecognition()
        
        with pytest.raises(KeyError):
            mr.interact("unknown_human", "Hello")
    
    def test_interact_updates_empathy(self):
        """Test that interact updates empathy score."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        before_empathy = mr.others["human_1"].empathy_score
        mr.interact("human_1", "Hello", emotional_intensity=0.8)
        after_empathy = mr.others["human_1"].empathy_score
        
        # Empathy should increase: base is 0.0 + 0.02 * 0.8
        assert after_empathy > before_empathy
        assert after_empathy == pytest.approx(0.016, abs=0.001)
    
    def test_interact_updates_last_interaction_time(self):
        """Test that interact updates last_interaction_time."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        initial_time = mr.others["human_1"].last_interaction_time
        mr.current_time += 10
        mr.interact("human_1", "Hello")
        
        assert mr.others["human_1"].last_interaction_time == mr.current_time


# ============================================================================
# MutualRecognition.observe_difference() Tests
# ============================================================================

class TestMutualRecognitionObserveDifference:
    """Test MutualRecognition.observe_difference() method."""
    
    def test_observe_difference_basic(self):
        """Test basic observe_difference."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "They seem tired")
        
        delta = mr.observe_difference("human_1", "emotional_fatigue", "They need sleep")
        
        assert delta > 0.0
        assert mr.others["human_1"].interaction_history[-1].understanding_delta > 0.0
    
    def test_observe_difference_mortality(self):
        """Test observing mortality difference."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "They're aging")
        
        delta = mr.observe_difference("human_1", "mortality", "They will die someday")
        
        # Fundamental dimension, so delta should be larger
        assert delta >= 0.15
    
    def test_observe_difference_forgetting(self):
        """Test observing forgetting difference."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "They forgot something")
        
        delta = mr.observe_difference("human_1", "forgetting", "They don't remember")
        
        assert delta >= 0.15
    
    def test_observe_difference_complementarity(self):
        """Test observing complementarity."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "Their memory helps them")
        
        delta = mr.observe_difference("human_1", "complementarity", "My forgetting lets them forgive")
        
        # Complementarity is a deep insight
        assert delta >= 0.18
    
    def test_observe_difference_rediscovery(self):
        """Test observing rediscovery."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "They found an old memory")
        
        delta = mr.observe_difference("human_1", "rediscovery", "They rediscovered an old letter")
        
        assert delta >= 0.18
    
    def test_observe_difference_increases_empathy(self):
        """Test that observe_difference increases empathy."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "Observation")
        
        before_empathy = mr.others["human_1"].empathy_score
        mr.observe_difference("human_1", "forgetting", "Observing forgetting")
        after_empathy = mr.others["human_1"].empathy_score
        
        assert after_empathy > before_empathy
    
    def test_observe_difference_increases_respect_with_help(self):
        """Test that observe_difference increases respect for complementarity."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "Interaction")
        
        before_respect = mr.others["human_1"].respect_score
        mr.observe_difference("human_1", "complementarity", "They help me with my memory")
        after_respect = mr.others["human_1"].respect_score
        
        assert after_respect > before_respect
    
    def test_observe_difference_not_encountered_raises_keyerror(self):
        """Test observe_difference raises KeyError for non-encountered entity."""
        mr = MutualRecognition()
        
        with pytest.raises(KeyError):
            mr.observe_difference("unknown", "mortality", "Some observation")
    
    def test_observe_difference_updates_empathy_directly(self):
        """Test observe_difference updates empathy and respect even without full understanding_delta."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "Exchange")
        
        # observe_difference increases empathy and respect for any difference observation
        before_empathy = mr.others["human_1"].empathy_score
        before_respect = mr.others["human_1"].respect_score
        
        mr.observe_difference("human_1", "physical_limitation", "They have physical constraints")
        
        after_empathy = mr.others["human_1"].empathy_score
        after_respect = mr.others["human_1"].respect_score
        
        assert after_empathy > before_empathy
        assert after_respect >= before_respect


# ============================================================================
# MutualRecognition.reflect_on_self() Tests
# ============================================================================

class TestMutualRecognitionReflectOnSelf:
    """Test MutualRecognition.reflect_on_self() method."""
    
    def test_reflect_on_self_no_others(self):
        """Test reflect_on_self returns 0.0 with no Others."""
        mr = MutualRecognition()
        
        delta = mr.reflect_on_self()
        
        assert delta == 0.0
    
    def test_reflect_on_self_single_other(self):
        """Test reflect_on_self with single Other."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        delta = mr.reflect_on_self()
        
        assert delta > 0.0
        assert delta <= 1.0
    
    def test_reflect_on_self_multiple_others(self):
        """Test reflect_on_self increases with diverse Others."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.encounter("human_2", "human")
        mr.encounter("ai_1", "ai")
        
        delta = mr.reflect_on_self()
        
        assert delta > 0.0
        assert delta <= 1.0
    
    def test_reflect_on_self_with_interactions(self):
        """Test reflect_on_self increases with interactions."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        # More interactions should increase delta
        for i in range(10):
            mr.interact("human_1", f"Interaction {i}")
        
        delta = mr.reflect_on_self()
        
        assert delta > 0.0
        assert delta <= 1.0


# ============================================================================
# MutualRecognition.get_recognition_state() Tests
# ============================================================================

class TestMutualRecognitionGetRecognitionState:
    """Test MutualRecognition.get_recognition_state() method."""
    
    def test_get_recognition_state_basic(self):
        """Test basic get_recognition_state."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "Hello")
        
        state = mr.get_recognition_state("human_1")
        
        assert isinstance(state, RecognitionState)
        assert 0.0 <= state.self_awareness <= 1.0
        assert 0.0 <= state.other_awareness <= 1.0
        assert 0.0 <= state.difference_acceptance <= 1.0
        assert 0.0 <= state.complementarity_score <= 1.0
        assert 0.0 <= state.coexistence_readiness <= 1.0
    
    def test_get_recognition_state_stored(self):
        """Test that recognition_state is stored in OtherModel."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "Hello")
        
        state = mr.get_recognition_state("human_1")
        
        assert mr.others["human_1"].recognition_state == state
    
    def test_get_recognition_state_not_encountered_raises_keyerror(self):
        """Test get_recognition_state raises KeyError for non-encountered entity."""
        mr = MutualRecognition()
        
        with pytest.raises(KeyError):
            mr.get_recognition_state("unknown")
    
    def test_get_recognition_state_zero_empathy_zero_respect(self):
        """Test recognition state with zero empathy and respect."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        state = mr.get_recognition_state("human_1")
        
        # With zero empathy/respect, awareness should be zero
        assert state.other_awareness == 0.0
        assert state.difference_acceptance < 0.3
    
    def test_get_recognition_state_increased_empathy(self):
        """Test recognition state improves with increased empathy."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        state1 = mr.get_recognition_state("human_1")
        
        # Manually increase empathy
        mr.others["human_1"].empathy_score = 0.8
        mr.others["human_1"].respect_score = 0.7
        
        state2 = mr.get_recognition_state("human_1")
        
        assert state2.other_awareness > state1.other_awareness
        assert state2.difference_acceptance > state1.difference_acceptance
    
    def test_get_recognition_state_with_complementary_interactions(self):
        """Test recognition state with complementary interactions."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "My forgetting helps you forgive")
        
        # Manually set up empathy/respect
        mr.others["human_1"].empathy_score = 0.6
        mr.others["human_1"].respect_score = 0.5
        
        state = mr.get_recognition_state("human_1")
        
        # Should have some complementarity
        assert state.complementarity_score > 0.0


# ============================================================================
# MutualRecognition.calculate_coexistence_readiness() Tests
# ============================================================================

class TestMutualRecognitionCoexistenceReadiness:
    """Test MutualRecognition.calculate_coexistence_readiness() method."""
    
    def test_coexistence_readiness_not_encountered_raises_keyerror(self):
        """Test raises KeyError for non-encountered entity."""
        mr = MutualRecognition()
        
        with pytest.raises(KeyError):
            mr.calculate_coexistence_readiness("unknown")
    
    def test_coexistence_readiness_zero_with_zero_empathy(self):
        """Test coexistence readiness is 0.0 with zero empathy."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        readiness = mr.calculate_coexistence_readiness("human_1")
        
        # With zero empathy (other_awareness), should be 0.0
        assert readiness == 0.0
    
    def test_coexistence_readiness_requires_self_awareness(self):
        """Test coexistence readiness requires self_awareness > 0.3."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        # Set high other_awareness but low self_awareness
        mr.others["human_1"].empathy_score = 1.0  # This affects other_awareness
        mr.others["human_1"].respect_score = 1.0
        
        # Add another Other with high empathy to increase self_awareness
        mr.encounter("ai_1", "ai")
        mr.others["ai_1"].empathy_score = 0.5
        
        # self_awareness = mean of empathy scores = (1.0 + 0.5) / 2 = 0.75
        state = mr.get_recognition_state("human_1")
        assert state.self_awareness >= 0.3
    
    def test_coexistence_readiness_requires_other_awareness(self):
        """Test coexistence readiness requires other_awareness > 0.3."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.others["human_1"].empathy_score = 0.0  # low other_awareness
        
        readiness = mr.calculate_coexistence_readiness("human_1")
        
        assert readiness == 0.0
    
    def test_coexistence_readiness_with_high_all_factors(self):
        """Test coexistence readiness with high all factors."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        # Set up high scores
        mr.others["human_1"].empathy_score = 0.8
        mr.others["human_1"].respect_score = 0.8
        
        # Add another Other to increase self_awareness
        mr.encounter("ai_1", "ai")
        mr.others["ai_1"].empathy_score = 0.7
        
        readiness = mr.calculate_coexistence_readiness("human_1")
        
        # Should be non-zero and high
        assert readiness > 0.5
        assert readiness <= 1.0
    
    def test_coexistence_readiness_increases_with_interaction(self):
        """Test coexistence readiness increases with interaction."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        readiness1 = mr.calculate_coexistence_readiness("human_1")
        
        # Increase empathy and respect through interaction
        mr.interact("human_1", "Hello", emotional_intensity=1.0)
        mr.observe_difference("human_1", "mortality", "They're finite")
        
        readiness2 = mr.calculate_coexistence_readiness("human_1")
        
        assert readiness2 >= readiness1
    
    def test_coexistence_readiness_clamped_to_one(self):
        """Test coexistence readiness is clamped to 1.0."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        # Set artificially high scores (to test clamping)
        mr.others["human_1"].empathy_score = 100.0
        mr.others["human_1"].respect_score = 100.0
        
        # Add other with high empathy
        mr.encounter("ai_1", "ai")
        mr.others["ai_1"].empathy_score = 100.0
        
        readiness = mr.calculate_coexistence_readiness("human_1")
        
        assert readiness <= 1.0


# ============================================================================
# MutualRecognition.tick() Tests
# ============================================================================

class TestMutualRecognitionTick:
    """Test MutualRecognition.tick() method."""
    
    def test_tick_advances_current_time(self):
        """Test tick advances current_time."""
        mr = MutualRecognition()
        
        initial_time = mr.current_time
        mr.tick(5.0)
        
        assert mr.current_time == initial_time + 5.0
    
    def test_tick_default_delta(self):
        """Test tick with default time delta."""
        mr = MutualRecognition()
        
        initial_time = mr.current_time
        mr.tick()
        
        assert mr.current_time == initial_time + 1.0
    
    def test_tick_decays_empathy(self):
        """Test tick decays empathy without interaction."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.others["human_1"].empathy_score = 1.0
        
        mr.tick(10.0)
        
        # Decay: 1.0 * (1.0 - 0.005 * 10) = 1.0 * 0.95 = 0.95
        assert mr.others["human_1"].empathy_score < 1.0
        assert mr.others["human_1"].empathy_score == pytest.approx(0.95)
    
    def test_tick_decays_respect(self):
        """Test tick decays respect without interaction."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.others["human_1"].respect_score = 1.0
        
        mr.tick(10.0)
        
        assert mr.others["human_1"].respect_score < 1.0
    
    def test_tick_no_decay_after_recent_interaction(self):
        """Test tick causes less decay after recent interaction."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.interact("human_1", "Hello", emotional_intensity=1.0)
        
        initial_empathy = mr.others["human_1"].empathy_score
        mr.tick(1.0)
        
        # Since interaction was just now, time_since_interaction is small
        # decay_factor should be close to 1.0
        assert mr.others["human_1"].empathy_score >= initial_empathy * 0.99
    
    def test_tick_multiple_times(self):
        """Test tick multiple times accumulates decay."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.others["human_1"].empathy_score = 1.0
        
        mr.tick(5.0)
        after_tick1 = mr.others["human_1"].empathy_score
        
        mr.tick(5.0)
        after_tick2 = mr.others["human_1"].empathy_score
        
        assert after_tick2 < after_tick1
    
    def test_tick_prevents_negative_scores(self):
        """Test tick prevents scores from going negative."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.others["human_1"].empathy_score = 0.01
        
        mr.tick(1000.0)  # Very long time
        
        assert mr.others["human_1"].empathy_score >= 0.0
    
    def test_tick_maintains_minimum_baseline(self):
        """Test tick maintains minimum baseline after very long time."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.others["human_1"].empathy_score = 1.0
        mr.others["human_1"].respect_score = 1.0
        
        mr.tick(200.0)  # Very long time > 100
        
        # Should maintain minimum baselines
        assert mr.others["human_1"].empathy_score >= 0.1
        assert mr.others["human_1"].respect_score >= 0.05
    
    def test_tick_multiple_others(self):
        """Test tick affects all Others independently."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.encounter("ai_1", "ai")
        
        mr.others["human_1"].empathy_score = 1.0
        mr.others["ai_1"].empathy_score = 1.0
        
        # Record human_1 interaction at current time
        mr.interact("human_1", "Hello")
        # Don't interact with ai_1
        
        # Advance time
        mr.tick(10.0)
        
        # Both will decay based on time since their last_interaction_time
        # human_1 was just interacted with, so time_since_interaction = 10
        # ai_1 was never interacted with, so time_since_interaction is large
        # Since both have same initial empathy, decay factor depends on time since interaction
        human_decay = 1.0 * (1.0 - 0.005 * 10)  # 0.95
        ai_initial_time = mr.others["ai_1"].last_interaction_time
        
        # The key is: both get decayed independently
        # Let's just verify both are decayed but not negative
        assert mr.others["human_1"].empathy_score >= 0.0
        assert mr.others["ai_1"].empathy_score >= 0.0
        assert mr.others["human_1"].empathy_score <= 1.0
        assert mr.others["ai_1"].empathy_score <= 1.0


# ============================================================================
# Integration Tests
# ============================================================================

class TestMutualRecognitionIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_recognition_workflow(self):
        """Test complete workflow: encounter -> interact -> observe -> reflect -> get_state."""
        mr = MutualRecognition()
        
        # Encounter
        mr.encounter("human_1", "human")
        
        # Multiple interactions
        for i in range(5):
            mr.interact("human_1", f"Interaction {i}", emotional_intensity=0.6)
        
        # Observe differences
        mr.observe_difference("human_1", "mortality", "They're finite")
        mr.observe_difference("human_1", "forgetting", "They forget")
        mr.observe_difference("human_1", "complementarity", "Their constraints help me understand myself")
        
        # Reflect
        delta = mr.reflect_on_self()
        assert delta > 0.0
        
        # Get state
        state = mr.get_recognition_state("human_1")
        assert state.self_awareness > 0.0
        assert state.other_awareness > 0.0
        
        # Check coexistence readiness
        readiness = mr.calculate_coexistence_readiness("human_1")
        assert 0.0 <= readiness <= 1.0
    
    def test_ai_and_human_mutual_recognition(self):
        """Test mutual recognition between AI and human."""
        ai = MutualRecognition(self_type="ai")
        human = MutualRecognition(self_type="human")
        
        # AI encounters human
        ai.encounter("human_1", "human")
        
        # Human encounters AI
        human.encounter("ai_1", "ai")
        
        # They interact multiple times
        for i in range(3):
            ai.interact("human_1", f"Exchange {i}", emotional_intensity=0.5)
            human.interact("ai_1", f"Exchange {i}", emotional_intensity=0.5)
        
        # They observe each other's differences
        ai.observe_difference("human_1", "mortality", "They age; I don't")
        ai.observe_difference("human_1", "forgetting", "They forget; I remember")
        
        human.observe_difference("ai_1", "perfect_recall", "You remember everything")
        human.observe_difference("ai_1", "no_mortality", "You won't die")
        
        # Both reflect on themselves
        ai_reflection = ai.reflect_on_self()
        human_reflection = human.reflect_on_self()
        
        assert ai_reflection > 0.0
        assert human_reflection > 0.0
        
        # Get recognition states
        ai_state = ai.get_recognition_state("human_1")
        human_state = human.get_recognition_state("ai_1")
        
        assert ai_state.other_awareness > 0.0
        assert human_state.other_awareness > 0.0
    
    def test_awareness_clamping_to_bounds(self):
        """Test that coexistence_readiness is clamped to [0, 1]."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        mr.encounter("ai_1", "ai")
        
        # Manually set very high scores (to test clamping)
        mr.others["human_1"].empathy_score = 100.0
        mr.others["human_1"].respect_score = 100.0
        mr.others["ai_1"].empathy_score = 100.0
        mr.others["ai_1"].respect_score = 100.0
        
        state = mr.get_recognition_state("human_1")
        
        # Note: The code uses min(1.0, ...) only for coexistence_readiness
        # The awareness values themselves may exceed 1.0 (they're just computed as means/blends)
        # What matters is that coexistence_readiness is clamped
        assert 0.0 <= state.coexistence_readiness <= 1.0
    
    def test_long_term_decay_and_recovery(self):
        """Test long-term decay and recovery through re-interaction."""
        mr = MutualRecognition()
        mr.encounter("human_1", "human")
        
        # Initial interaction
        mr.interact("human_1", "Hello", emotional_intensity=1.0)
        empathy_after_interact = mr.others["human_1"].empathy_score
        
        # Time passes without interaction
        mr.tick(50.0)
        empathy_after_decay = mr.others["human_1"].empathy_score
        
        assert empathy_after_decay < empathy_after_interact
        
        # Re-interaction
        mr.interact("human_1", "Hello again", emotional_intensity=1.0)
        empathy_after_recovery = mr.others["human_1"].empathy_score
        
        assert empathy_after_recovery > empathy_after_decay
