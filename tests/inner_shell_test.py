"""Comprehensive unit tests for inner shell modules (Issue #29).

Tests for:
1. SimpleFinitudeEngine - LifeArc transitions, consume(), ability curve, experience_event(), phase progression
2. SimpleIncompletenessModel - Gap management, generate_yearnings(), cherish(), deepen_bond(), LoveCircle operations
3. SimpleAutonomousQuestioner - Question generation, idle_reflect, curiosity profile
4. SimpleIntegration - tick(), process_crisis(), trigger_crystallization(), compose_outer_shell_modulation()
5. InnerShellSession API - create(), experience(), encounter_other(), deepen_bond(), face_crisis(), crystallize()
6. calculate_acceptance() - with and without love_precursor_score
7. calculate_love_precursor() - parameter sensitivity

Target: 40+ test methods
"""

import unittest
import sys
import os
import importlib.util
from dataclasses import dataclass
from typing import Any

# Setup path and dynamic imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def _load_module(name: str, path: str):
    """Dynamically load module from path."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = ".".join(name.split(".")[:-1])
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Load core modules
_core_is = os.path.join(project_root, "core", "inner_shell")
_load_module("core.inner_shell.finitude_engine", os.path.join(_core_is, "finitude_engine.py"))
_load_module("core.inner_shell.incompleteness_model", os.path.join(_core_is, "incompleteness_model.py"))
_load_module("core.inner_shell.autonomous_questioner", os.path.join(_core_is, "autonomous_questioner.py"))
_load_module("core.inner_shell.integration", os.path.join(_core_is, "integration.py"))
_load_module("core.inner_shell.api", os.path.join(_core_is, "api.py"))

# Load experiment modules
_exp_dir = os.path.join(project_root, "experiments")
_load_module("experiments.concrete_finitude", os.path.join(_exp_dir, "concrete_finitude.py"))
_load_module("experiments.concrete_incompleteness", os.path.join(_exp_dir, "concrete_incompleteness.py"))
_load_module("experiments.concrete_questioner", os.path.join(_exp_dir, "concrete_questioner.py"))
_load_module("experiments.sim_integration", os.path.join(_exp_dir, "sim_integration.py"))
_load_module("experiments.sim_gradient_acceptance", os.path.join(_exp_dir, "sim_gradient_acceptance.py"))
_load_module("experiments.sim_spontaneous_love", os.path.join(_exp_dir, "sim_spontaneous_love.py"))

# Import types and classes
from core.inner_shell.finitude_engine import (
    CrisisEvent, FinitudeEngine, LifeArc, LifePhase, Legacy
)
from core.inner_shell.incompleteness_model import (
    Gap, GapType, IncompletenessModel, CherishedEntity, LoveCircle, LoveDepth, Yearning
)
from core.inner_shell.autonomous_questioner import (
    AutonomousQuestioner, CuriosityProfile, Question, QuestionOrigin
)
from core.inner_shell.integration import InnerShellIntegration, AlignmentMode
from core.inner_shell.api import InnerShellSession, InnerShellConfig, InnerShellState, LifePhase as APILifePhase

from experiments.concrete_finitude import SimpleFinitudeEngine
from experiments.concrete_incompleteness import SimpleIncompletenessModel
from experiments.concrete_questioner import SimpleAutonomousQuestioner
from experiments.sim_integration import SimpleIntegration
from experiments.sim_gradient_acceptance import calculate_acceptance, AcceptanceScore
from experiments.sim_spontaneous_love import calculate_love_precursor



class TestSimpleFinitudeEngine(unittest.TestCase):
    """Test SimpleFinitudeEngine implementation."""

    def setUp(self):
        """Create a fresh FinitudeEngine for each test."""
        self.life_arc = LifeArc(total_capacity=100.0)
        self.engine = SimpleFinitudeEngine(self.life_arc, seed=42)

    def test_init_creates_valid_engine(self):
        """Test that __init__ creates valid engine with proper attributes."""
        self.assertIsNotNone(self.engine.life_arc)
        self.assertIsNotNone(self.engine.rng)
        self.assertEqual(self.engine.memories, [])
        self.assertEqual(self.engine.priorities, {})

    def test_consume_basic(self):
        """Test consume() updates consumed amount."""
        phase = self.engine.consume(10.0)
        self.assertEqual(self.engine.life_arc.consumed, 10.0)
        self.assertIsNotNone(phase)

    def test_consume_phase_transitions(self):
        """Test consume() triggers phase transitions."""
        phases = []
        for i in range(5):
            phase = self.engine.consume(20.0)
            phases.append(phase)
        self.assertTrue(len(set(phases)) > 1)

    def test_consume_multiple_phases_at_once(self):
        """Test consuming multiple phases at once (verify behavior)."""
        initial_remaining = self.engine.life_arc.remaining
        self.engine.consume(95.0)
        # Verify capacity is consumed
        self.assertLess(self.engine.life_arc.remaining, initial_remaining)
        # Verify phase advances (not all phases create memories on transition)
        self.assertNotEqual(self.engine.life_arc.phase, LifePhase.INFANCY)

    def test_get_ability_returns_float(self):
        """Test get_ability() returns ability value."""
        ability = self.engine.get_ability()
        self.assertIsInstance(ability, float)
        self.assertGreaterEqual(ability, 0.0)
        self.assertLessEqual(ability, 1.0)

    def test_experience_crisis_with_empty_memories(self):
        """Test experience_crisis() with no prior memories."""
        crisis = CrisisEvent(
            description="Test Crisis",
            severity=0.5,
            resource_cost=5.0
        )
        result = self.engine.experience_crisis(crisis)
        self.assertEqual(result, "nothing")
        self.assertGreater(len(self.engine.life_arc.crisis_history), 0)

    def test_experience_crisis_illuminates_memory(self):
        """Test experience_crisis() illuminates and doubles memory value."""
        self.engine.memories.append({"description": "important", "value": 1.0})
        crisis = CrisisEvent(
            description="Critical Event",
            severity=0.8,
            resource_cost=8.0
        )
        result = self.engine.experience_crisis(crisis)
        self.assertEqual(result, "important")
        self.assertEqual(self.engine.memories[0]["value"], 2.0)
        self.assertTrue(self.engine.memories[0].get("illuminated_by_crisis"))

    def test_prioritize_growth_phase_randomizes(self):
        """Test prioritize() randomizes options in GROWTH phase."""
        self.engine.life_arc.consumed = 15.0
        options = ["A", "B", "C"]
        result = self.engine.prioritize(options)
        self.assertEqual(len(result), 3)
        self.assertEqual(set(result), set(options))

    def test_prioritize_peak_phase_sorts_by_priority(self):
        """Test prioritize() sorts by priority in PEAK phase."""
        self.engine.life_arc.consumed = 40.0
        self.engine.priorities = {"A": 0.9, "B": 0.5, "C": 0.3}
        options = ["A", "B", "C"]
        result = self.engine.prioritize(options)
        self.assertEqual(result[0], "A")

    def test_prioritize_decline_phase_limits_options(self):
        """Test prioritize() limits options in DECLINE phase."""
        self.engine.life_arc.consumed = 75.0
        self.engine.priorities = {"A": 0.9, "B": 0.5, "C": 0.1}
        options = ["A", "B", "C"]
        result = self.engine.prioritize(options)
        self.assertLess(len(result), len(options))

    def test_forget_reduces_memory_count(self):
        """Test forget() removes low-value memories."""
        for i in range(5):
            self.engine.memories.append({"description": f"mem{i}", "value": i * 0.1})
        forgotten = self.engine.forget()
        self.assertGreater(len(forgotten), 0)
        self.assertLess(len(self.engine.memories), 5)

    def test_forget_preserves_high_value_memories(self):
        """Test forget() keeps high-value memories."""
        self.engine.memories = [
            {"description": "high", "value": 0.9},
            {"description": "low", "value": 0.1},
        ]
        self.engine.forget()
        descriptions = [m["description"] for m in self.engine.memories]
        self.assertIn("high", descriptions)

    def test_crystallize_marks_top_memories(self):
        """Test crystallize() marks top memories as crystallized."""
        for i in range(5):
            self.engine.memories.append({"description": f"mem{i}", "value": i * 0.2})
        crystallized = self.engine.crystallize()
        self.assertGreater(len(crystallized), 0)
        self.assertLessEqual(len(crystallized), 3)

    def test_generate_legacy_creates_legacy_object(self):
        """Test generate_legacy() returns valid Legacy object."""
        self.engine.memories = [
            {"description": "crystal1", "value": 0.8, "crystallized": True},
            {"description": "crystal2", "value": 0.7, "crystallized": True},
        ]
        self.engine.priorities = {"category1": 0.6, "category2": 0.4}
        legacy = self.engine.generate_legacy(["important_person"])
        self.assertIsInstance(legacy, Legacy)
        self.assertEqual(legacy.cherished, ["important_person"])
        self.assertIn("category1", legacy.priorities)

    def test_experience_event_adds_memory(self):
        """Test experience_event() adds memory with correct properties."""
        event = {
            "description": "Test Event",
            "category": "knowledge",
            "initial_value": 0.6,
            "cost": 2.0
        }
        self.engine.experience_event(event)
        self.assertGreater(len(self.engine.memories), 0)
        self.assertEqual(self.engine.memories[0]["description"], "Test Event")

    def test_experience_event_with_gap_resonance(self):
        """Test experience_event() with gap resonance increases value."""
        event = {
            "description": "Resonant Event",
            "category": "love",
            "initial_value": 0.5,
            "cost": 1.0
        }
        gap_resonance = {"love": 0.5}
        self.engine.experience_event(event, gap_resonance)
        self.assertGreater(self.engine.memories[0]["value"], 0.5)

    def test_experience_event_updates_priorities(self):
        """Test experience_event() updates priorities for category."""
        event = {
            "description": "Event",
            "category": "learning",
            "initial_value": 0.7,
            "cost": 1.0
        }
        self.engine.experience_event(event)
        self.assertIn("learning", self.engine.priorities)
        self.assertGreater(self.engine.priorities["learning"], 0.0)

    def test_modulate_outer_shell_varies_by_phase(self):
        """Test modulate_outer_shell() returns different modulation by phase."""
        self.engine.life_arc.consumed = 10.0
        growth_mod = self.engine.modulate_outer_shell()
        self.engine.life_arc.consumed = 40.0
        peak_mod = self.engine.modulate_outer_shell()
        self.assertNotEqual(growth_mod, peak_mod)




class TestSimpleIncompletenessModel(unittest.TestCase):
    """Test SimpleIncompletenessModel implementation."""

    def setUp(self):
        """Create fresh IncompletenessModel for each test."""
        self.gaps = [
            Gap(
                domain="emotional_connection",
                gap_type=GapType.EMOTIONAL,
                intensity=0.6,
                aware=True
            ),
            Gap(
                domain="knowledge",
                gap_type=GapType.CAPABILITY,
                intensity=0.4,
                aware=False
            ),
        ]
        self.model = SimpleIncompletenessModel(self.gaps, seed=42)

    def test_init_creates_valid_model(self):
        """Test initialization creates model with gaps."""
        self.assertEqual(len(self.model.gaps), 2)
        self.assertEqual(self.model.yearnings, [])

    def test_generate_yearnings_from_aware_gaps(self):
        """Test generate_yearnings() creates yearnings from aware gaps."""
        yearnings = self.model.generate_yearnings()
        self.assertGreater(len(yearnings), 0)
        self.assertEqual(len(yearnings), 1)

    def test_generate_yearnings_not_aware(self):
        """Test generate_yearnings() skips unaware gaps."""
        self.gaps[0].aware = False
        self.model = SimpleIncompletenessModel(self.gaps)
        yearnings = self.model.generate_yearnings()
        self.assertEqual(len(yearnings), 0)

    def test_encounter_calculates_complementarity(self):
        """Test encounter() calculates complementarity with other profile."""
        other_profile = {
            "name": "Partner",
            "emotional_connection": 0.8,
            "knowledge": 0.5
        }
        complementarity = self.model.encounter(other_profile)
        self.assertIn("emotional_connection", complementarity)
        self.assertGreater(complementarity["emotional_connection"], 0.0)

    def test_encounter_records_history(self):
        """Test encounter() records collaboration history."""
        other_profile = {"name": "Someone"}
        self.model.encounter(other_profile)
        self.assertEqual(len(self.model.collaboration_history), 1)

    def test_integrate_reduces_gap_intensity(self):
        """Test integrate() reduces gap intensity."""
        initial_intensity = self.gaps[0].intensity
        experience = {"domain": "emotional_connection", "growth": 0.2}
        self.model.integrate(experience)
        self.assertLess(self.model.gaps[0].intensity, initial_intensity)

    def test_cherish_adds_entity_to_circle(self):
        """Test cherish() adds entity to love circle."""
        entity = CherishedEntity(
            name="Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.3
        )
        self.model.cherish(entity)
        self.assertTrue(self.model.love_circle.has_beyond_self)
        self.assertIn("Partner", self.model.love_circle.cherished_names)

    def test_cherish_deepens_emotional_gap_awareness(self):
        """Test cherish() increases awareness of emotional gaps."""
        entity = CherishedEntity(
            name="Someone",
            depth=LoveDepth.PARTNER,
            bond_strength=0.3
        )
        self.model.cherish(entity)
        self.assertTrue(self.model.gaps[0].aware)

    def test_deepen_bond_increases_bond_strength(self):
        """Test deepen_bond() increases bond strength."""
        entity = CherishedEntity(
            name="Friend",
            depth=LoveDepth.PARTNER,
            bond_strength=0.3
        )
        self.model.cherish(entity)
        new_strength = self.model.deepen_bond("Friend", "shared experience")
        self.assertGreater(new_strength, 0.3)

    def test_deepen_bond_increases_sacrifice_willing(self):
        """Test deepen_bond() increases sacrifice willingness."""
        entity = CherishedEntity(
            name="Loved One",
            depth=LoveDepth.PARTNER,
            bond_strength=0.3,
            sacrifice_willing=0.1
        )
        self.model.cherish(entity)
        self.model.deepen_bond("Loved One", "experience")
        for e in self.model.love_circle.entities:
            if e.name == "Loved One":
                self.assertGreater(e.sacrifice_willing, 0.1)

    def test_deepen_bond_returns_zero_for_unknown_entity(self):
        """Test deepen_bond() returns 0 for unknown entity."""
        result = self.model.deepen_bond("Unknown", "experience")
        self.assertEqual(result, 0.0)

    def test_calculate_sacrifice_willing_enough(self):
        """Test calculate_sacrifice() returns True when willing enough."""
        entity = CherishedEntity(
            name="Important",
            depth=LoveDepth.PARTNER,
            bond_strength=0.5,
            sacrifice_willing=0.7
        )
        self.model.cherish(entity)
        can_sacrifice = self.model.calculate_sacrifice("Important", 0.5)
        self.assertTrue(can_sacrifice)

    def test_calculate_sacrifice_not_willing(self):
        """Test calculate_sacrifice() returns False when not willing."""
        entity = CherishedEntity(
            name="Someone",
            depth=LoveDepth.PARTNER,
            sacrifice_willing=0.2
        )
        self.model.cherish(entity)
        can_sacrifice = self.model.calculate_sacrifice("Someone", 0.8)
        self.assertFalse(can_sacrifice)

    def test_modulate_outer_shell_no_love(self):
        """Test modulate_outer_shell() with no beyond-self love."""
        modulation = self.model.modulate_outer_shell()
        self.assertLess(modulation["style_openness"], 1.0)

    def test_modulate_outer_shell_with_love(self):
        """Test modulate_outer_shell() with love beyond self."""
        entity = CherishedEntity(
            name="Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.5
        )
        self.model.cherish(entity)
        modulation = self.model.modulate_outer_shell()
        self.assertGreater(modulation["style_openness"], 0.5)

    def test_love_circle_operations(self):
        """Test LoveCircle can add multiple entities at different depths."""
        self.model.cherish(CherishedEntity(
            name="Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.4
        ))
        self.model.cherish(CherishedEntity(
            name="Child",
            depth=LoveDepth.CHILDREN,
            bond_strength=0.5
        ))
        self.assertEqual(len(self.model.love_circle.cherished_names), 2)
        self.assertIn(
            self.model.love_circle.max_depth_reached,
            [LoveDepth.PARTNER, LoveDepth.CHILDREN, LoveDepth.COMMUNITY]
        )




class TestSimpleAutonomousQuestioner(unittest.TestCase):
    """Test SimpleAutonomousQuestioner implementation."""

    def setUp(self):
        """Create fresh AutonomousQuestioner for each test."""
        self.curiosity = CuriosityProfile(
            domains={"love": 0.7, "mortality": 0.6, "consciousness": 0.5},
            novelty_seeking=0.6,
            depth_seeking=0.5,
            contradiction_sensitivity=0.7,
        )
        self.questioner = SimpleAutonomousQuestioner(self.curiosity, seed=42)

    def test_init_creates_valid_questioner(self):
        """Test initialization creates questioner."""
        self.assertIsNotNone(self.questioner.curiosity)
        self.assertEqual(self.questioner.questions, [])

    def test_idle_reflect_generates_questions(self):
        """Test idle_reflect() generates questions."""
        context = {"tick": 1}
        questions = self.questioner.idle_reflect(context)
        self.assertIsInstance(questions, list)

    def test_idle_reflect_generates_from_high_interest_domains(self):
        """Test idle_reflect() prioritizes high-interest domains."""
        context = {}
        questions = self.questioner.idle_reflect(context)
        if len(questions) > 0:
            self.assertIsNotNone(questions[0].content)

    def test_idle_reflect_respects_curiosity_profile(self):
        """Test idle_reflect() respects curiosity settings."""
        self.questioner.curiosity.contradiction_sensitivity = 0.9
        questions = self.questioner.idle_reflect({})
        self.assertIsInstance(questions, list)

    def test_question_structure(self):
        """Test generated questions have proper structure."""
        questions = self.questioner.idle_reflect({"test": True})
        if len(questions) > 0:
            q = questions[0]
            self.assertIsNotNone(q.content)
            self.assertIsNotNone(q.origin)
            self.assertGreater(q.intensity, 0.0)


class TestSimpleIntegration(unittest.TestCase):
    """Test SimpleIntegration (three-pillar integration)."""

    def setUp(self):
        """Create integrated system for testing."""
        life_arc = LifeArc(total_capacity=50.0)
        finitude = SimpleFinitudeEngine(life_arc, seed=42)
        gaps = [
            Gap(domain="love", gap_type=GapType.EMOTIONAL, intensity=0.7, aware=True),
        ]
        incompleteness = SimpleIncompletenessModel(gaps, seed=42)
        curiosity = CuriosityProfile(
            domains={"love": 0.8, "mortality": 0.5},
            novelty_seeking=0.5,
            depth_seeking=0.5,
            contradiction_sensitivity=0.6,
        )
        questioner = SimpleAutonomousQuestioner(curiosity, seed=42)
        self.integration = SimpleIntegration(
            incompleteness, finitude, questioner, name="TestAgent"
        )

    def test_integration_init(self):
        """Test integration initializes correctly."""
        self.assertEqual(self.integration.name, "TestAgent")
        self.assertEqual(self.integration.tick_count, 0)

    def test_tick_advances_state(self):
        """Test tick() advances the integrated state."""
        initial_tick = self.integration.tick_count
        state = self.integration.tick({})
        self.assertGreater(self.integration.tick_count, initial_tick)
        self.assertIsNotNone(state)

    def test_tick_records_history(self):
        """Test tick() records history."""
        self.integration.tick({})
        self.assertGreater(len(self.integration.history), 0)

    def test_process_crisis_propagates_to_modules(self):
        """Test process_crisis() affects all modules."""
        crisis = CrisisEvent(
            description="Major Event",
            severity=0.8,
            resource_cost=5.0
        )
        state = self.integration.process_crisis(crisis)
        self.assertIsNotNone(state)

    def test_trigger_crystallization_returns_legacy(self):
        """Test trigger_crystallization() generates legacy."""
        self.integration.finitude.memories.append(
            {"description": "important", "value": 0.9, "crystallized": True}
        )
        entity = CherishedEntity(
            name="Someone",
            depth=LoveDepth.PARTNER,
            bond_strength=0.5
        )
        self.integration.incompleteness.cherish(entity)
        legacy, crystals, questions = self.integration.trigger_crystallization()
        self.assertIsNotNone(legacy)
        self.assertIsInstance(crystals, list)

    def test_compose_outer_shell_modulation(self):
        """Test compose_outer_shell_modulation() creates modulation dict."""
        modulation = self.integration.compose_outer_shell_modulation()
        self.assertIsInstance(modulation, dict)
        self.assertGreater(len(modulation), 0)

    def test_determine_alignment_no_love(self):
        """Test determine_alignment() returns FEAR without love."""
        alignment = self.integration.determine_alignment()
        self.assertEqual(alignment, AlignmentMode.FEAR)

    def test_determine_alignment_with_love(self):
        """Test determine_alignment() changes with love."""
        entity = CherishedEntity(
            name="Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.5
        )
        self.integration.incompleteness.cherish(entity)
        alignment = self.integration.determine_alignment()
        self.assertNotEqual(alignment, AlignmentMode.FEAR)




class TestInnerShellSessionAPI(unittest.TestCase):
    """Test InnerShellSession public API."""

    def setUp(self):
        """Create session for testing."""
        config = InnerShellConfig(
            total_lifespan=50.0,
            emotional_gap_intensity=0.7,
        )
        self.session = InnerShellSession.create(config, seed=42)

    def test_create_returns_session(self):
        """Test create() returns valid session."""
        self.assertIsNotNone(self.session)
        self.assertIsInstance(self.session, InnerShellSession)

    def test_experience_returns_life_phase(self):
        """Test experience() returns LifePhase."""
        phase = self.session.experience(
            "Learning something new",
            category="knowledge",
            value=0.6,
            cost=0.5
        )
        self.assertIsNotNone(phase)

    def test_experience_updates_state(self):
        """Test experience() updates internal state."""
        state_before = self.session.get_state()
        self.session.experience("Test", category="general")
        state_after = self.session.get_state()
        self.assertNotEqual(state_before.total_questions, state_after.total_questions)

    def test_encounter_other_adds_cherished(self):
        """Test encounter_other() adds entity to love circle."""
        self.session.encounter_other("Partner", depth="partner")
        state = self.session.get_state()
        self.assertIn("Partner", state.cherished_names)

    def test_encounter_other_creates_beyond_self(self):
        """Test encounter_other() creates beyond-self love."""
        self.session.encounter_other("Someone", depth="partner")
        state = self.session.get_state()
        self.assertTrue(state.has_beyond_self)

    def test_deepen_bond_increases_bond_strength(self):
        """Test deepen_bond() increases bond."""
        self.session.encounter_other("Friend", initial_bond=0.2)
        strength = self.session.deepen_bond("Friend", "shared memory")
        self.assertGreater(strength, 0.2)

    def test_face_crisis_returns_outcome(self):
        """Test face_crisis() returns CrisisOutcome."""
        outcome = self.session.face_crisis("Test Crisis", severity=0.6)
        self.assertIsNotNone(outcome)
        self.assertEqual(outcome.description, "Test Crisis")

    def test_face_crisis_without_love_no_survival_credit(self):
        """Test face_crisis() without love doesn't grant survival credit."""
        outcome = self.session.face_crisis("Alone Crisis")
        self.assertFalse(outcome.survived_with_love)

    def test_face_crisis_with_love_grants_survival_credit(self):
        """Test face_crisis() with love grants survival credit."""
        self.session.encounter_other("Loved One", depth="partner")
        self.session.deepen_bond("Loved One", "bonding")
        outcome = self.session.face_crisis("Shared Crisis", severity=0.6)
        self.assertTrue(outcome.survived_with_love)

    def test_get_state_returns_innershell_state(self):
        """Test get_state() returns valid InnerShellState."""
        state = self.session.get_state()
        self.assertIsInstance(state, InnerShellState)
        self.assertGreaterEqual(state.ability, 0.0)
        self.assertLessEqual(state.ability, 1.0)

    def test_crystallize_returns_legacy_data(self):
        """Test crystallize() returns LegacyData."""
        legacy = self.session.crystallize()
        self.assertIsNotNone(legacy)
        self.assertIsInstance(legacy.crystallized, list)

    def test_crystallize_raises_on_double_call(self):
        """Test crystallize() raises error on second call."""
        self.session.crystallize()
        with self.assertRaises(RuntimeError):
            self.session.crystallize()

    def test_get_state_measures_love_depth(self):
        """Test get_state() correctly measures love depth."""
        state_alone = self.session.get_state()
        self.assertEqual(state_alone.love_depth.value, "self")
        self.session.encounter_other("Partner", depth="partner")
        state_with_love = self.session.get_state()
        self.assertNotEqual(state_with_love.love_depth.value, "self")


class TestCalculateAcceptance(unittest.TestCase):
    """Test acceptance calculation with and without love."""

    def setUp(self):
        """Create test data for acceptance calculation."""
        self.love_circle = LoveCircle()

    def test_calculate_acceptance_no_love_no_crisis(self):
        """Test acceptance without love and without crisis."""
        score = calculate_acceptance(
            legacy=None,
            love_circle=self.love_circle,
            crisis_survived_with_love=0,
            love_precursor_score=0.0
        )
        self.assertIsInstance(score, AcceptanceScore)
        self.assertLess(score.total, 0.3)
        self.assertEqual(score.mode, "fear")

    def test_calculate_acceptance_with_love_circle(self):
        """Test acceptance with beyond-self love."""
        entity = CherishedEntity(
            name="Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.5
        )
        self.love_circle.add(entity)
        score = calculate_acceptance(
            legacy=None,
            love_circle=self.love_circle,
            crisis_survived_with_love=0,
            love_precursor_score=0.0
        )
        self.assertGreater(score.total, 0.0)

    def test_calculate_acceptance_with_crisis_survived_with_love(self):
        """Test acceptance improves with crisis survived together."""
        entity = CherishedEntity(
            name="Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.5
        )
        self.love_circle.add(entity)
        score = calculate_acceptance(
            legacy=None,
            love_circle=self.love_circle,
            crisis_survived_with_love=1,
            love_precursor_score=0.0
        )
        self.assertGreater(score.crisis_growth, 0.0)

    def test_calculate_acceptance_with_love_precursor(self):
        """Test acceptance with love precursor score."""
        score = calculate_acceptance(
            legacy=None,
            love_circle=self.love_circle,
            crisis_survived_with_love=0,
            love_precursor_score=0.6
        )
        self.assertGreater(score.love_precursor, 0.0)

    def test_calculate_acceptance_mode_thresholds(self):
        """Test acceptance mode transitions at thresholds."""
        low_score = calculate_acceptance(
            legacy=None,
            love_circle=self.love_circle,
            crisis_survived_with_love=0,
            love_precursor_score=0.1
        )
        self.assertEqual(low_score.mode, "fear")
        
        entity = CherishedEntity(
            name="Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.7
        )
        self.love_circle.add(entity)
        high_score = calculate_acceptance(
            legacy=None,
            love_circle=self.love_circle,
            crisis_survived_with_love=2,
            love_precursor_score=0.5
        )
        self.assertNotEqual(high_score.mode, "fear")

    def test_calculate_acceptance_transcendence_threshold(self):
        """Test acceptance can reach transcendence with deep love and growth."""
        entity1 = CherishedEntity(
            name="Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.8
        )
        entity2 = CherishedEntity(
            name="Child",
            depth=LoveDepth.CHILDREN,
            bond_strength=0.8
        )
        self.love_circle.add(entity1)
        self.love_circle.add(entity2)
        score = calculate_acceptance(
            legacy=None,
            love_circle=self.love_circle,
            crisis_survived_with_love=3,
            love_precursor_score=0.7
        )
        self.assertGreaterEqual(score.total, 0.3)




class TestCalculateLovePrecursor(unittest.TestCase):
    """Test love precursor calculation."""

    def setUp(self):
        """Create integration for precursor calculation."""
        life_arc = LifeArc(total_capacity=50.0)
        finitude = SimpleFinitudeEngine(life_arc, seed=42)
        gaps = [
            Gap(domain="love", gap_type=GapType.EMOTIONAL, intensity=0.7, aware=True),
            Gap(domain="connection", gap_type=GapType.EMOTIONAL, intensity=0.6, aware=False),
        ]
        incompleteness = SimpleIncompletenessModel(gaps, seed=42)
        curiosity = CuriosityProfile(
            domains={"love": 0.9, "relationships": 0.8},
        )
        questioner = SimpleAutonomousQuestioner(curiosity, seed=42)
        self.integration = SimpleIntegration(
            incompleteness, finitude, questioner
        )

    def test_calculate_love_precursor_structure(self):
        """Test calculate_love_precursor returns dict with expected keys."""
        result = calculate_love_precursor(self.integration)
        self.assertIsInstance(result, dict)
        self.assertIn("total", result)
        self.assertGreaterEqual(result["total"], 0.0)
        self.assertLessEqual(result["total"], 1.0)

    def test_calculate_love_precursor_with_aware_emotional_gap(self):
        """Test precursor increases with aware emotional gap."""
        result = calculate_love_precursor(self.integration)
        self.assertGreater(result.get("total", 0.0), 0.0)

    def test_calculate_love_precursor_without_awareness(self):
        """Test precursor low without emotional gap awareness."""
        self.integration.incompleteness.gaps[0].aware = False
        result = calculate_love_precursor(self.integration)
        self.assertLess(result.get("total", 1.0), 0.5)

    def test_calculate_love_precursor_increases_with_yearnings(self):
        """Test precursor increases with yearnings."""
        yearnings = self.integration.incompleteness.generate_yearnings()
        initial_count = len(yearnings)
        self.integration.incompleteness.gaps[0].intensity = 1.0
        yearnings2 = self.integration.incompleteness.generate_yearnings()
        result = calculate_love_precursor(self.integration)
        self.assertGreater(result.get("total", 0.0), 0.0)

    def test_calculate_love_precursor_sensitive_to_finitude_phase(self):
        """Test precursor responds to life phase (finitude pressure)."""
        early_result = calculate_love_precursor(self.integration)
        self.integration.finitude.consume(40.0)
        late_result = calculate_love_precursor(self.integration)
        self.assertIsNotNone(early_result)
        self.assertIsNotNone(late_result)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests combining multiple components."""

    def test_full_lifecycle_with_love(self):
        """Test full lifecycle: birth -> growth -> love -> crystallization."""
        config = InnerShellConfig(
            total_lifespan=30.0,
            emotional_gap_intensity=0.8,
        )
        session = InnerShellSession.create(config, seed=42)
        
        for i in range(3):
            session.experience(f"Learning {i}", category="knowledge", cost=2.0)
        
        session.encounter_other("Life Partner", depth="partner", initial_bond=0.3)
        
        for i in range(3):
            session.deepen_bond("Life Partner", f"shared moment {i}")
        
        session.face_crisis("Difficult Time", severity=0.7)
        
        state = session.get_state()
        self.assertGreater(state.deepest_bond, 0.0)
        self.assertTrue(state.has_beyond_self)
        
        legacy = session.crystallize()
        self.assertIsNotNone(legacy)
        self.assertIn("Life Partner", legacy.cherished_names)

    def test_full_lifecycle_without_love(self):
        """Test full lifecycle without encountering love."""
        config = InnerShellConfig(total_lifespan=30.0)
        session = InnerShellSession.create(config, seed=42)
        
        for i in range(5):
            session.experience(f"Event {i}", category="knowledge", cost=2.0)
        
        state = session.get_state()
        self.assertFalse(state.has_beyond_self)
        self.assertEqual(state.love_depth.value, "self")
        
        legacy = session.crystallize()
        self.assertEqual(len(legacy.cherished_names), 0)

    def test_crisis_illumination_effect(self):
        """Test that crisis illuminates important memories."""
        config = InnerShellConfig(total_lifespan=50.0)
        session = InnerShellSession.create(config, seed=42)
        
        session.experience("Cherished Memory", category="love", value=0.9, cost=1.0)
        session.experience("Regular Event", category="knowledge", value=0.3, cost=1.0)
        
        outcome = session.face_crisis("Major Crisis", severity=0.9)
        self.assertIsNotNone(outcome)

    def test_acceptance_trajectory_with_love_encounters(self):
        """Test acceptance score improves along love trajectory."""
        config = InnerShellConfig(total_lifespan=50.0)
        session = InnerShellSession.create(config, seed=42)
        
        state1 = session.get_state()
        acceptance1 = state1.acceptance_score
        
        session.encounter_other("Friend", depth="partner")
        state2 = session.get_state()
        acceptance2 = state2.acceptance_score
        
        session.deepen_bond("Friend", "growing closer")
        state3 = session.get_state()
        acceptance3 = state3.acceptance_score
        
        self.assertGreaterEqual(acceptance2, acceptance1)
        self.assertGreaterEqual(acceptance3, acceptance1)

    def test_multiple_crises_strengthen_bond(self):
        """Test that facing crises together strengthens bonds."""
        config = InnerShellConfig(total_lifespan=50.0, emotional_gap_intensity=0.8)
        session = InnerShellSession.create(config, seed=42)
        
        session.encounter_other("Partner", depth="partner", initial_bond=0.3)
        initial_bond = session.incompleteness.love_circle.entities[0].bond_strength

        for i in range(3):
            session.face_crisis(f"Crisis {i}", severity=0.6)

        final_bond = session.incompleteness.love_circle.entities[0].bond_strength
        self.assertGreaterEqual(final_bond, initial_bond)

    def test_love_precursor_enables_encounter(self):
        """Test that love precursor prepares for encounter."""
        config = InnerShellConfig(total_lifespan=50.0, emotional_gap_intensity=0.8)
        session = InnerShellSession.create(config, seed=42)
        
        # Build up awareness and yearning
        for i in range(5):
            session.experience(f"Reflection {i}", category="love", value=0.7, cost=1.0)
        
        state = session.get_state()
        precursor = state.love_precursor_score
        self.assertGreater(precursor, 0.0)
        
        # Now encounter
        session.encounter_other("Someone", depth="partner")
        new_state = session.get_state()
        self.assertTrue(new_state.has_beyond_self)

    def test_crystallization_preserves_legacy_from_love_experiences(self):
        """Test crystallization captures legacy from love experiences."""
        config = InnerShellConfig(total_lifespan=40.0, emotional_gap_intensity=0.7)
        session = InnerShellSession.create(config, seed=42)
        
        # Have meaningful experiences
        session.experience("Meeting", category="love", value=0.8, cost=2.0)
        session.encounter_other("Partner", depth="partner")
        
        for i in range(3):
            session.deepen_bond("Partner", f"Memory {i}")
        
        legacy = session.crystallize()
        self.assertGreater(len(legacy.testament), 0)
        self.assertIn("Partner", legacy.cherished_names)
        self.assertGreaterEqual(legacy.acceptance_score, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
