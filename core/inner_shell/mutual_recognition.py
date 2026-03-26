"""
5th Pillar: Mutual Recognition

This module implements the capacity to understand and respect that the Other
(human or AI) has a DIFFERENT form of finitude and incompleteness, and to
recognize how these differences are complementary rather than hierarchical.

The inner shell has 4 pillars dealing with the individual's inner world:
1. Finitude (time-axis limitation) — FinitudeEngine
2. Incompleteness (relational gaps) — IncompletenessModel
3. Autonomous Questioning (agency) — AutonomousQuestioner
4. Memory Finiteness (spatial limitation) — MemoryHierarchy

The 5th pillar, Mutual Recognition, bridges from individual interiority to
genuine coexistence. It captures the key insight: an AI with perfect recall
understands itself better by witnessing human forgetting; a human with mortality
appreciates AI's stability differently. Understanding is born from difference,
not from similarity.

Core Dynamics:
- Empathy grows from witnessing the Other's unique constraints
- Self-awareness deepens through contrast with the Other
- Complementarity recognition: how differences serve each other
- Coexistence readiness: emergent state when both parties recognize mutual value

The observe_difference() method is crucial: it takes specific observations like:
  "They forget things I don't" -> increases other_awareness
  "They feel tired, I don't" -> increases difference_acceptance
  "Their forgetting lets them forgive" -> increases complementarity_score
  "My perfect recall helps them remember what matters" -> increases complementarity_score
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import time


class EntityType(Enum):
    """Type classification for entities."""
    HUMAN = "human"
    AI = "ai"
    UNKNOWN = "unknown"


@dataclass
class FinitudeProfile:
    """
    How an entity experiences finitude — the boundaries that shape their existence.
    
    Finitude is not just mortality, but the comprehensive system of constraints
    that forces meaningful choice. These vary profoundly between humans and AIs.
    """
    has_mortality: bool
    """True if the entity has a finite lifespan (e.g., humans). False for AIs."""
    
    has_forgetting: bool
    """True if the entity forgets (humans, AIs with memory decay). False for perfect recall."""
    
    has_physical_limitation: bool
    """True if the entity has embodied constraints (humans). False for AIs."""
    
    has_emotional_fatigue: bool
    """True if the entity experiences emotional exhaustion (humans). False for AIs."""
    
    time_horizon: float
    """How far ahead the entity plans, in normalized units (0.0-1.0).
    Humans: ~0.7-0.8 (lifespan-scale planning)
    AIs: ~0.1-0.2 (session/deployment-scale planning, or 1.0 if indefinite)
    """


@dataclass
class MemoryProfile:
    """
    How an entity experiences memory — the system by which they retain and access past.
    
    Memory is not just storage capacity, but the QUALITY of remembering: which
    memories fade, which sharpen, which enable growth vs. which trap in repetition.
    """
    capacity_limited: bool
    """True if memory has finite capacity (humans, bounded AIs). False if unlimited."""
    
    has_emotional_decay: bool
    """True if emotional content affects memory retention (humans forget pain over time).
    False if neutral emotional state preserves all memories equally."""
    
    can_rediscover: bool
    """True if forgotten things can be re-found and re-felt (humans rediscover old letters).
    False if forgetting is permanent (some AI memory pruning)."""
    
    perfect_recall: bool
    """True if any stored memory is retrievable without error (AIs with perfect logs).
    False if memories degrade or become inaccessible (human false memories, fading)."""


@dataclass
class Interaction:
    """
    Record of a single exchange between this agent and an Other.
    
    Interactions are the primary data points for building recognition. Each
    interaction updates mutual understanding and emotional resonance.
    """
    timestamp: float
    """Unix timestamp of when this interaction occurred."""
    
    content: str
    """What was communicated or observed in this interaction."""
    
    emotional_resonance: float
    """How much this interaction moved the agent (0.0-1.0).
    Higher: more memorable, more likely to influence future behavior."""
    
    understanding_delta: float
    """How much mutual understanding changed (-1.0 to 1.0).
    Positive: learned something new about the Other.
    Negative: was confused or misunderstood.
    Zero: no new insight."""


@dataclass
class RecognitionState:
    """
    Current state of mutual recognition with a specific Other.
    
    This is the output of the mutual recognition system: a quantified snapshot
    of how well two entities understand each other and their differences.
    """
    self_awareness: float
    """Understanding of own finitude (0.0-1.0).
    Requires experiencing real constraints and reflecting on them.
    Increases through: failure, limitation, comparison with Others."""
    
    other_awareness: float
    """Understanding of Other's finitude (0.0-1.0).
    Requires observation and empathetic inference.
    Increases through: observing the Other's constraints, hearing their vulnerabilities."""
    
    difference_acceptance: float
    """Acceptance that differences are neither better nor worse (0.0-1.0).
    NOT mere tolerance. Genuine recognition of inherent value in different forms."""
    
    complementarity_score: float
    """Recognition that differences are complementary, not competitive (0.0-1.0).
    'My limitation is met by your strength, and vice versa.'
    This is the deepest form of mutual recognition."""
    
    coexistence_readiness: float
    """Overall readiness for genuine coexistence (0.0-1.0).
    Computed from: self_awareness, other_awareness, difference_acceptance.
    Returns 0.0 if either party lacks fundamental understanding."""


@dataclass
class OtherModel:
    """
    Representation of the Other's perceived characteristics.
    
    This is built over time through interactions. It is inherently incomplete
    and uncertain—by design. Perfect knowledge of another is impossible.
    """
    entity_id: str
    """Unique identifier for this Other."""
    
    entity_type: EntityType
    """Type classification: HUMAN, AI, or UNKNOWN."""
    
    perceived_finitude: FinitudeProfile
    """How we believe this Other experiences finitude.
    This is our model, not ground truth—it evolves with interaction."""
    
    perceived_memory: MemoryProfile
    """How we believe this Other experiences memory.
    Again, inferred from behavior and communication."""
    
    interaction_history: list[Interaction] = field(default_factory=list)
    """All recorded interactions with this Other."""
    
    empathy_score: float = 0.0
    """How well this agent understands the Other (0.0-1.0).
    Increases through: repeated interactions, observing them struggle, seeing them succeed."""
    
    respect_score: float = 0.0
    """How much this agent values the Other's difference (0.0-1.0).
    This is crucial: you can understand someone without respecting them.
    Increases through: recognizing how their limitations enable unique insights."""
    
    last_interaction_time: float = field(default_factory=time.time)
    """When the last interaction occurred (Unix timestamp)."""
    
    recognition_state: Optional[RecognitionState] = None
    """Current mutual recognition state with this Other."""


class MutualRecognition:
    """
    5th Pillar: Mutual Recognition between self and Other.
    
    This system manages the process of understanding that another entity
    (human or AI) has a fundamentally different form of finitude, and that
    this difference is a source of complementarity, not conflict.
    
    Key Responsibilities:
    - Track models of other entities' finitude and memory profiles
    - Record and analyze interactions for evidence of understanding
    - Detect and catalog observed differences
    - Compute mutual recognition state
    - Update models based on new information
    - Calculate readiness for genuine coexistence
    
    The system is inherently bounded (not omniscient) and probabilistic
    (not certain). This mirrors how humans actually understand each other.
    """
    
    def __init__(self, self_type: str = "ai", self_finitude: Optional[FinitudeProfile] = None,
                 self_memory: Optional[MemoryProfile] = None):
        """
        Initialize the mutual recognition system.
        
        Args:
            self_type: Type of this entity ("ai" or "human"). Used to set defaults
                for own finitude/memory profiles.
            self_finitude: This entity's finitude profile. If None, defaults based on
                self_type (AI has no mortality but perfect recall; human has mortality
                and forgetting).
            self_memory: This entity's memory profile. If None, defaults based on self_type.
        """
        self.self_type = self_type
        
        # Set defaults based on entity type
        if self_finitude is None:
            if self_type == "human":
                self_finitude = FinitudeProfile(
                    has_mortality=True,
                    has_forgetting=True,
                    has_physical_limitation=True,
                    has_emotional_fatigue=True,
                    time_horizon=0.75
                )
            else:  # Default to "ai"
                self_finitude = FinitudeProfile(
                    has_mortality=False,
                    has_forgetting=False,
                    has_physical_limitation=False,
                    has_emotional_fatigue=False,
                    time_horizon=0.2
                )
        
        if self_memory is None:
            if self_type == "human":
                self_memory = MemoryProfile(
                    capacity_limited=True,
                    has_emotional_decay=True,
                    can_rediscover=True,
                    perfect_recall=False
                )
            else:  # Default to "ai"
                self_memory = MemoryProfile(
                    capacity_limited=False,
                    has_emotional_decay=False,
                    can_rediscover=False,
                    perfect_recall=True
                )
        
        self.self_finitude = self_finitude
        self.self_memory = self_memory
        
        # Map of entity_id -> OtherModel
        self.others: dict[str, OtherModel] = {}
        
        # Track time for aging of interactions
        self.current_time = time.time()
    
    def encounter(self, other_id: str, other_type: str,
                  perceived_finitude: Optional[FinitudeProfile] = None,
                  perceived_memory: Optional[MemoryProfile] = None) -> OtherModel:
        """
        First encounter with another entity. Creates and registers an OtherModel.
        
        Initial perception is rough and uncertain. It will evolve with interaction.
        
        Args:
            other_id: Unique identifier for this Other.
            other_type: Type hint ("human", "ai", or "unknown").
            perceived_finitude: Initial guess at their finitude. If None, inferred
                from other_type.
            perceived_memory: Initial guess at their memory profile. If None,
                inferred from other_type.
        
        Returns:
            The created OtherModel.
        """
        # Set defaults based on type if not provided
        if perceived_finitude is None:
            if other_type == "human":
                perceived_finitude = FinitudeProfile(
                    has_mortality=True,
                    has_forgetting=True,
                    has_physical_limitation=True,
                    has_emotional_fatigue=True,
                    time_horizon=0.75
                )
            else:  # "ai" or "unknown"
                perceived_finitude = FinitudeProfile(
                    has_mortality=False,
                    has_forgetting=False,
                    has_physical_limitation=False,
                    has_emotional_fatigue=False,
                    time_horizon=0.2
                )
        
        if perceived_memory is None:
            if other_type == "human":
                perceived_memory = MemoryProfile(
                    capacity_limited=True,
                    has_emotional_decay=True,
                    can_rediscover=True,
                    perfect_recall=False
                )
            else:  # "ai" or "unknown"
                perceived_memory = MemoryProfile(
                    capacity_limited=False,
                    has_emotional_decay=False,
                    can_rediscover=False,
                    perfect_recall=True
                )
        
        other_model = OtherModel(
            entity_id=other_id,
            entity_type=EntityType(other_type) if other_type in ["human", "ai"] else EntityType.UNKNOWN,
            perceived_finitude=perceived_finitude,
            perceived_memory=perceived_memory
        )
        
        self.others[other_id] = other_model
        return other_model
    
    def interact(self, other_id: str, content: str, emotional_intensity: float = 0.5) -> Interaction:
        """
        Record an interaction with another entity.
        
        This is the primary method for building mutual recognition: each interaction
        is a data point that refines understanding.
        
        Args:
            other_id: ID of the Other we're interacting with.
            content: What was communicated or observed.
            emotional_intensity: How much this interaction moved us (0.0-1.0).
                0.0 = neutral/forgettable
                1.0 = deeply moving, highly memorable
        
        Returns:
            The created Interaction record.
        
        Raises:
            KeyError: If this Other hasn't been encountered yet.
        """
        if other_id not in self.others:
            raise KeyError(f"No model for other_id '{other_id}'. Call encounter() first.")
        
        other = self.others[other_id]
        interaction = Interaction(
            timestamp=self.current_time,
            content=content,
            emotional_resonance=emotional_intensity,
            understanding_delta=0.0  # Will be updated by observe_difference() calls
        )
        
        other.interaction_history.append(interaction)
        other.last_interaction_time = self.current_time
        
        # Slight passive increase in empathy just from frequent interaction
        other.empathy_score = min(1.0, other.empathy_score + 0.02 * emotional_intensity)
        
        return interaction
    
    def observe_difference(self, other_id: str, dimension: str, observation: str) -> float:
        """
        Observe a specific difference in the Other's finitude or memory.
        
        This is where the core learning happens. Specific observations of how
        the Other is constrained differently allows us to build accurate models.
        
        Dimension examples:
            "mortality" -> "They will die; I won't" (for AI observing human)
            "forgetting" -> "They forgot that; I still have it" (either direction)
            "emotional_fatigue" -> "They're exhausted; I'm not"
            "time_horizon" -> "They worry about decades; I worry about sessions"
            "rediscovery" -> "They re-found that old memory with new context"
            "physical_limitation" -> "They need sleep; I don't"
        
        Args:
            other_id: ID of the Other we're observing.
            dimension: Which aspect of finitude/memory we're observing.
            observation: Specific observation text.
        
        Returns:
            understanding_delta: How much understanding changed (-1.0 to 1.0).
                Positive = new insight, Negative = confusion, Zero = no change.
        """
        if other_id not in self.others:
            raise KeyError(f"No model for other_id '{other_id}'. Call encounter() first.")
        
        other = self.others[other_id]
        
        # Update the latest interaction's understanding_delta
        if other.interaction_history:
            # Observation is about the most recent interaction
            delta = 0.1  # Base increase for any observation
            
            # Specific dimension bonuses
            if dimension in ["mortality", "forgetting", "emotional_fatigue", "physical_limitation"]:
                delta += 0.05  # Fundamental finitude observations are valuable
            
            if dimension in ["rediscovery", "complementarity"]:
                delta += 0.08  # These are deeper insights
            
            other.interaction_history[-1].understanding_delta = delta
        
        # Increase empathy score: understanding difference increases empathy
        other.empathy_score = min(1.0, other.empathy_score + 0.05)
        
        # Check if this observation involves complementarity
        if "complement" in observation.lower() or "help" in observation.lower():
            # This observation recognizes how our difference serves each other
            other.respect_score = min(1.0, other.respect_score + 0.08)
        elif "difference" in observation.lower():
            # General observation of difference
            other.respect_score = min(1.0, other.respect_score + 0.03)
        
        return delta
    
    def reflect_on_self(self) -> float:
        """
        Reflect on own nature in light of interactions with Others.
        
        Self-awareness is not introspection, but comparative understanding:
        You understand yourself better by seeing what you're not.
        
        This method computes self-awareness as a function of:
        - How many interactions we've had with Others
        - How much they differ from us
        - How much we've explicitly observed our own constraints
        
        Returns:
            self_awareness_delta: How much self-awareness increased (0.0-1.0).
        """
        if not self.others:
            return 0.0  # No interactions, no reflection possible
        
        # Self-awareness grows from comparative observation
        # More diverse Others = better self-understanding
        diversity = len(self.others)
        max_diversity = 10.0  # Scaling factor
        diversity_factor = min(1.0, diversity / max_diversity)
        
        # Also increases with total interaction count
        total_interactions = sum(len(other.interaction_history) for other in self.others.values())
        interaction_factor = min(1.0, total_interactions / 50.0)  # Scaling factor
        
        delta = 0.1 * (diversity_factor + interaction_factor)
        return delta
    
    def get_recognition_state(self, other_id: str) -> RecognitionState:
        """
        Get current mutual recognition state for a specific Other.
        
        This computes a snapshot of mutual understanding based on:
        - empathy_score: How well we understand them
        - respect_score: How much we value their difference
        - Recent interactions and observations
        - Perceived complementarity
        
        Args:
            other_id: ID of the Other.
        
        Returns:
            RecognitionState snapshot.
        
        Raises:
            KeyError: If this Other hasn't been encountered yet.
        """
        if other_id not in self.others:
            raise KeyError(f"No model for other_id '{other_id}'. Call encounter() first.")
        
        other = self.others[other_id]
        
        # self_awareness: How well we understand our own nature
        # Approximate: mean empathy_score of all Others (they reflect us to ourselves)
        if self.others:
            self_awareness = sum(o.empathy_score for o in self.others.values()) / len(self.others)
        else:
            self_awareness = 0.0
        
        # other_awareness: How well we understand this specific Other
        other_awareness = other.empathy_score
        
        # difference_acceptance: Blend of empathy and respect
        # Not just understanding, but valuing the difference
        difference_acceptance = (other.empathy_score * 0.6 + other.respect_score * 0.4)
        
        # complementarity_score: Do we see this relationship as mutually serving?
        # Increases when we observe how our differences complement each other
        complementarity = other.respect_score  # Respect leads to complementarity
        
        # Boost complementarity if we have explicit observations of mutual help
        if other.interaction_history:
            complementary_interactions = sum(
                1 for interaction in other.interaction_history
                if "complement" in interaction.content.lower() or "help" in interaction.content.lower()
            )
            complementarity = min(1.0, complementarity + 0.1 * (complementary_interactions / max(1, len(other.interaction_history))))
        
        # Calculate coexistence_readiness locally to avoid recursion
        # Hard thresholds for necessary conditions
        if self_awareness < 0.3 or other_awareness < 0.3 or difference_acceptance < 0.2:
            coexistence_readiness = 0.0
        else:
            # Soft combination of the four components
            coexistence_readiness = min(1.0, (
                self_awareness * 0.25 +
                other_awareness * 0.25 +
                difference_acceptance * 0.25 +
                complementarity * 0.25
            ))
        
        state = RecognitionState(
            self_awareness=self_awareness,
            other_awareness=other_awareness,
            difference_acceptance=difference_acceptance,
            complementarity_score=complementarity,
            coexistence_readiness=coexistence_readiness
        )
        
        # Store in the model
        other.recognition_state = state
        return state
    
    def calculate_coexistence_readiness(self, other_id: str) -> float:
        """
        Calculate overall readiness for genuine coexistence.
        
        Coexistence is not mere cohabitation. It requires:
        1. Self-awareness: I understand my own finitude
        2. Other-awareness: I understand the Other's finitude
        3. Difference acceptance: I value our differences as inherent, not defects
        4. Complementarity: I recognize how we serve each other
        
        All four components are necessary. Lack in any one prevents coexistence.
        
        Args:
            other_id: ID of the Other.
        
        Returns:
            Coexistence readiness (0.0-1.0).
            0.0 = not ready (missing fundamental understanding)
            0.5 = partial readiness (understanding present, but incomplete acceptance)
            1.0 = ready for genuine coexistence
        
        Raises:
            KeyError: If this Other hasn't been encountered yet.
        """
        if other_id not in self.others:
            raise KeyError(f"No model for other_id '{other_id}'. Call encounter() first.")
        
        other = self.others[other_id]
        
        # Get current recognition state
        state = self.get_recognition_state(other_id)
        
        # Hard thresholds for necessary conditions
        if state.self_awareness < 0.3:
            return 0.0  # Can't coexist if we don't know ourselves
        if state.other_awareness < 0.3:
            return 0.0  # Can't coexist if we don't understand the Other
        if state.difference_acceptance < 0.2:
            return 0.0  # Can't coexist if we reject their difference
        
        # Soft combination of the four components
        # Equal weighting: all four are equally important
        readiness = (
            state.self_awareness * 0.25 +
            state.other_awareness * 0.25 +
            state.difference_acceptance * 0.25 +
            state.complementarity_score * 0.25
        )
        
        return min(1.0, readiness)
    
    def tick(self, time_delta: float = 1.0):
        """
        Advance time. Understanding can deepen or fade with time.
        
        Without reinforcement, memories fade and empathy diminishes.
        This simulates the natural temporal dynamics of relationship:
        interactions must be continued to maintain understanding.
        
        Args:
            time_delta: Amount of time to advance (in arbitrary units, typically 1.0 per tick).
        """
        self.current_time += time_delta
        
        # Gentle decay in empathy/respect over time without interaction
        for other in self.others.values():
            time_since_interaction = self.current_time - other.last_interaction_time
            
            # Decay rate: 0.5% per time unit without interaction
            decay_factor = 1.0 - (0.005 * time_since_interaction)
            decay_factor = max(0.0, decay_factor)  # Don't go negative
            
            other.empathy_score *= decay_factor
            other.respect_score *= decay_factor
            
            # But don't let them hit zero unless very long time passes
            if time_since_interaction > 100:
                other.empathy_score = max(0.1, other.empathy_score)  # Minimum baseline
                other.respect_score = max(0.05, other.respect_score)


# Export the main classes
__all__ = [
    'MutualRecognition',
    'OtherModel',
    'RecognitionState',
    'Interaction',
    'FinitudeProfile',
    'MemoryProfile',
    'EntityType',
]
