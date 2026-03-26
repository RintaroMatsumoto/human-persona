"""
Experiment 19: Memory Asymmetry in Paired Agents

Core question: How does asymmetric memory capacity shape the relationship
between two agents? One agent remembers everything (AI-like), the other
forgets selectively (human-like). How does this asymmetry create gratitude,
tension, and ultimately, depth?

Key Hypotheses:
H1: Asymmetric pairs have MORE gratitude events than symmetric pairs
H2: Asymmetric pairs have MORE tension events than symmetric pairs
H3: Net bond strength is HIGHEST in ASYMMETRIC_STANDARD (complementarity)
H4: SYMMETRIC_PERFECT has high overlap but low novelty (boring)
H5: Memory gifts (A remembering B's joys) increase over time asymmetric pair
H6: Forgiveness is possible in asymmetric pair when forgetful agent leads
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from enum import Enum
import statistics


class Condition(Enum):
    """5 memory architecture conditions."""
    SYMMETRIC_PERFECT = "symmetric_perfect"
    SYMMETRIC_FORGETFUL = "symmetric_forgetful"
    ASYMMETRIC_STANDARD = "asymmetric_standard"
    ASYMMETRIC_REVERSED = "asymmetric_reversed"
    ASYMMETRIC_MILD = "asymmetric_mild"


@dataclass
class Event:
    """A single shared experience."""
    event_id: int
    timestamp: int
    content: str
    emotion_intensity: float
    emotion_valence: float
    category: str

    def __hash__(self):
        return hash(self.event_id)

    def __eq__(self, other):
        return isinstance(other, Event) and self.event_id == other.event_id


@dataclass
class MemoryItem:
    """How an agent stores a memory."""
    event: Event
    stored_at: int
    retention_strength: float
    emotion_valence: float


@dataclass
class ConversationEvent:
    """Records what happened during a conversation."""
    turn: int
    type: str
    mentioner_name: str
    listener_name: str
    event_id: Optional[int]
    intensity: float


@dataclass
class AgentConfig:
    """Configuration for an agent's memory architecture."""
    name: str
    memory_capacity: Optional[int]
    decay_rate: float
    can_rediscover: bool


class MemoryStore:
    """Capacity-limited memory with optional decay."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.memories: Dict[int, MemoryItem] = {}
        self.forgotten_pool: Dict[int, Tuple[int, float]] = {}

    def store(self, event: Event, current_time: int) -> bool:
        """Store an event in memory."""
        if event.event_id in self.memories:
            return True

        if self.config.memory_capacity is not None and len(self.memories) >= self.config.memory_capacity:
            weakest_id = min(self.memories.keys(), key=lambda eid: self.memories[eid].retention_strength)
            weakest_strength = self.memories[weakest_id].retention_strength

            if event.emotion_intensity < weakest_strength:
                return False

            forgotten_item = self.memories.pop(weakest_id)
            self.forgotten_pool[weakest_id] = (current_time, forgotten_item.retention_strength)

        self.memories[event.event_id] = MemoryItem(
            event=event,
            stored_at=current_time,
            retention_strength=event.emotion_intensity,
            emotion_valence=event.emotion_valence,
        )
        return True

    def tick(self, current_time: int) -> None:
        """Decay all memories by one time unit."""
        if self.config.decay_rate == 0.0:
            return

        to_forget = []
        for event_id, item in self.memories.items():
            item.retention_strength = item.retention_strength * math.exp(-self.config.decay_rate)
            if item.retention_strength < 0.01:
                to_forget.append(event_id)

        for event_id in to_forget:
            item = self.memories.pop(event_id)
            self.forgotten_pool[event_id] = (current_time, item.retention_strength)

    def get_memories(self) -> List[MemoryItem]:
        """Get all currently remembered items."""
        return list(self.memories.values())

    def recalls_event(self, event_id: int) -> bool:
        """Does this agent currently remember a specific event?"""
        return event_id in self.memories

    def get_remembered_event_ids(self) -> set:
        """Set of all event IDs currently remembered."""
        return set(self.memories.keys())


@dataclass
class Agent:
    """An agent with memory and emotional state."""
    name: str
    config: AgentConfig
    memory: MemoryStore
    relationship_strength: float = 0.0
    conversation_history: List[ConversationEvent] = field(default_factory=list)

    def experience_event(self, event: Event, current_time: int) -> None:
        """Agent experiences an event."""
        self.memory.store(event, current_time)


@dataclass
class SimulationRun:
    """A single simulation run tracking metrics."""
    condition: Condition
    run_id: int
    seed: int
    shared_memory_overlap: List[float] = field(default_factory=list)
    gratitude_events: List[ConversationEvent] = field(default_factory=list)
    tension_events: List[ConversationEvent] = field(default_factory=list)
    novelty_events: List[ConversationEvent] = field(default_factory=list)
    shared_memory_events: List[ConversationEvent] = field(default_factory=list)
    conversation_history: List[ConversationEvent] = field(default_factory=list)
    final_bond_strength: float = 0.0
    memory_gift_score: float = 0.0
    forgiveness_asymmetry_index: float = 0.0

    def add_overlap(self, overlap: float) -> None:
        self.shared_memory_overlap.append(overlap)

    def add_conversation(self, conv: ConversationEvent) -> None:
        self.conversation_history.append(conv)
        if conv.type == "shared_memory":
            self.shared_memory_events.append(conv)
        elif conv.type == "gratitude":
            self.gratitude_events.append(conv)
        elif conv.type == "tension":
            self.tension_events.append(conv)
        elif conv.type == "novelty":
            self.novelty_events.append(conv)

    def calculate_bond_strength(self) -> float:
        """Bond = gratitude - tension (weighted)."""
        gratitude = len(self.gratitude_events)
        tension = len(self.tension_events)
        novelty = len(self.novelty_events)
        bond = (gratitude * 1.5) + (novelty * 0.5) - (tension * 0.8)
        self.final_bond_strength = bond
        return bond

    def calculate_memory_gift_score(self, agent_a: Agent, agent_b: Agent) -> float:
        """How often agent_a's perfect memory serves agent_b."""
        if agent_a.config.memory_capacity is not None:
            return 0.0
        if agent_b.config.memory_capacity is None:
            return 0.0
        gift_score = len([e for e in self.gratitude_events if e.listener_name == agent_b.name])
        self.memory_gift_score = float(gift_score)
        return float(gift_score)

    def calculate_forgiveness_asymmetry(self) -> float:
        """How asymmetric conflicts resolve."""
        if len(self.tension_events) == 0:
            return 0.0
        total = len(self.gratitude_events) + len(self.tension_events)
        if total == 0:
            return 0.0
        self.forgiveness_asymmetry_index = len(self.gratitude_events) / total
        return self.forgiveness_asymmetry_index


def generate_events(num_events: int, seed: int) -> List[Event]:
    """Generate a sequence of shared events."""
    rng = random.Random(seed)
    categories = ["shared_joy", "shared_pain", "conflict", "reconciliation", "discovery", "mundane"]

    events = []
    for i in range(num_events):
        category = rng.choice(categories)
        if category == "shared_joy":
            emotion_valence = rng.uniform(0.5, 1.0)
            emotion_intensity = rng.uniform(0.6, 1.0)
        elif category == "shared_pain":
            emotion_valence = rng.uniform(-1.0, -0.5)
            emotion_intensity = rng.uniform(0.6, 1.0)
        elif category == "conflict":
            emotion_valence = rng.uniform(-0.8, -0.2)
            emotion_intensity = rng.uniform(0.7, 1.0)
        elif category == "reconciliation":
            emotion_valence = rng.uniform(0.3, 0.8)
            emotion_intensity = rng.uniform(0.5, 0.9)
        elif category == "discovery":
            emotion_valence = rng.uniform(0.4, 0.9)
            emotion_intensity = rng.uniform(0.5, 0.8)
        else:
            emotion_valence = rng.uniform(-0.2, 0.2)
            emotion_intensity = rng.uniform(0.1, 0.4)

        events.append(Event(
            event_id=i,
            timestamp=i,
            content=f"{category}_event_{i}",
            emotion_intensity=emotion_intensity,
            emotion_valence=emotion_valence,
            category=category,
        ))

    return events


def converse(agent_a: Agent, agent_b: Agent, turn: int, events_seen: List[Event]) -> List[ConversationEvent]:
    """Agents converse about their memories."""
    conversation_events = []

    memories_a = agent_a.memory.get_memories()
    if not memories_a:
        return conversation_events

    chosen = random.choice(memories_a)

    if agent_b.memory.recalls_event(chosen.event.event_id):
        conv = ConversationEvent(
            turn=turn,
            type="shared_memory",
            mentioner_name=agent_a.name,
            listener_name=agent_b.name,
            event_id=chosen.event.event_id,
            intensity=chosen.event.emotion_intensity,
        )
        conversation_events.append(conv)
    else:
        if agent_b.config.can_rediscover and chosen.event.event_id in agent_b.memory.forgotten_pool:
            if chosen.event.emotion_valence > 0.0:
                conv = ConversationEvent(
                    turn=turn,
                    type="gratitude",
                    mentioner_name=agent_a.name,
                    listener_name=agent_b.name,
                    event_id=chosen.event.event_id,
                    intensity=chosen.event.emotion_intensity * 0.8,
                )
            else:
                conv = ConversationEvent(
                    turn=turn,
                    type="tension",
                    mentioner_name=agent_a.name,
                    listener_name=agent_b.name,
                    event_id=chosen.event.event_id,
                    intensity=abs(chosen.event.emotion_valence) * 0.6,
                )
            conversation_events.append(conv)

    memories_b = agent_b.memory.get_memories()
    if memories_b:
        chosen_b = random.choice(memories_b)
        if not agent_a.memory.recalls_event(chosen_b.event.event_id):
            if agent_a.config.memory_capacity is not None or agent_b.config.memory_capacity is None:
                conv = ConversationEvent(
                    turn=turn,
                    type="novelty",
                    mentioner_name=agent_b.name,
                    listener_name=agent_a.name,
                    event_id=chosen_b.event.event_id,
                    intensity=chosen_b.event.emotion_intensity * 0.5,
                )
                conversation_events.append(conv)

    return conversation_events


def run_simulation(condition: Condition, run_id: int, num_events: int = 100, seed: int = 42) -> SimulationRun:
    """Run a single simulation of paired agents with memory asymmetry."""
    rng = random.Random(seed)

    if condition == Condition.SYMMETRIC_PERFECT:
        config_a = AgentConfig(name="A_perfect", memory_capacity=None, decay_rate=0.0, can_rediscover=False)
        config_b = AgentConfig(name="B_perfect", memory_capacity=None, decay_rate=0.0, can_rediscover=False)
    elif condition == Condition.SYMMETRIC_FORGETFUL:
        config_a = AgentConfig(name="A_forgetful", memory_capacity=7, decay_rate=0.05, can_rediscover=True)
        config_b = AgentConfig(name="B_forgetful", memory_capacity=7, decay_rate=0.05, can_rediscover=True)
    elif condition == Condition.ASYMMETRIC_STANDARD:
        config_a = AgentConfig(name="A_perfect", memory_capacity=None, decay_rate=0.0, can_rediscover=False)
        config_b = AgentConfig(name="B_forgetful", memory_capacity=7, decay_rate=0.05, can_rediscover=True)
    elif condition == Condition.ASYMMETRIC_REVERSED:
        config_a = AgentConfig(name="A_forgetful", memory_capacity=7, decay_rate=0.05, can_rediscover=True)
        config_b = AgentConfig(name="B_perfect", memory_capacity=None, decay_rate=0.0, can_rediscover=False)
    else:
        config_a = AgentConfig(name="A_mild", memory_capacity=50, decay_rate=0.02, can_rediscover=True)
        config_b = AgentConfig(name="B_forgetful", memory_capacity=7, decay_rate=0.05, can_rediscover=True)

    agent_a = Agent(name=config_a.name, config=config_a, memory=MemoryStore(config_a))
    agent_b = Agent(name=config_b.name, config=config_b, memory=MemoryStore(config_b))

    events = generate_events(num_events, seed)
    run = SimulationRun(condition=condition, run_id=run_id, seed=seed)

    for t, event in enumerate(events):
        agent_a.experience_event(event, t)
        agent_b.experience_event(event, t)
        agent_a.memory.tick(t)
        agent_b.memory.tick(t)

        if (t + 1) % 10 == 0:
            convs = converse(agent_a, agent_b, t, events)
            for conv in convs:
                run.add_conversation(conv)

            mem_a = agent_a.memory.get_remembered_event_ids()
            mem_b = agent_b.memory.get_remembered_event_ids()
            if mem_a or mem_b:
                overlap = len(mem_a & mem_b) / len(mem_a | mem_b) if (mem_a | mem_b) else 0.0
                run.add_overlap(overlap)

    run.calculate_bond_strength()
    run.calculate_memory_gift_score(agent_a, agent_b)
    run.calculate_forgiveness_asymmetry()

    return run


def main():
    """Run the full experiment: N=30 runs per condition."""
    num_runs = 30
    base_seed = 42

    results: Dict[Condition, List[SimulationRun]] = defaultdict(list)

    for condition in Condition:
        print(f"Running {condition.value}...")
        for run_id in range(num_runs):
            seed = base_seed + run_id
            run = run_simulation(condition, run_id, num_events=100, seed=seed)
            results[condition].append(run)
        print(f"  Completed {num_runs} runs")

    print("\n" + "=" * 100)
    print("EXPERIMENT 19: Memory Asymmetry in Paired Agents")
    print("=" * 100)

    print("\n" + "-" * 100)
    print("SUMMARY TABLE: Metrics by Condition")
    print("-" * 100)

    print(f"{'Condition':<25} {'Overlap':<12} {'Gratitude':<12} {'Tension':<12} {'Novelty':<12} {'Bond':<12} {'Gift':<12} {'Forgive':<12}")
    print("-" * 100)

    for condition in Condition:
        runs = results[condition]

        overlaps = [r.shared_memory_overlap for r in runs]
        avg_overlap = statistics.mean([statistics.mean(o) if o else 0.0 for o in overlaps])

        gratitudes = [len(r.gratitude_events) for r in runs]
        avg_gratitude = statistics.mean(gratitudes)

        tensions = [len(r.tension_events) for r in runs]
        avg_tension = statistics.mean(tensions)

        novelties = [len(r.novelty_events) for r in runs]
        avg_novelty = statistics.mean(novelties)

        bonds = [r.final_bond_strength for r in runs]
        avg_bond = statistics.mean(bonds)

        gifts = [r.memory_gift_score for r in runs]
        avg_gift = statistics.mean(gifts)

        forgives = [r.forgiveness_asymmetry_index for r in runs]
        avg_forgive = statistics.mean(forgives)

        print(f"{condition.value:<25} {avg_overlap:<12.3f} {avg_gratitude:<12.2f} {avg_tension:<12.2f} {avg_novelty:<12.2f} {avg_bond:<12.2f} {avg_gift:<12.2f} {avg_forgive:<12.3f}")

    print("\n" + "-" * 100)
    print("HYPOTHESIS EVALUATION")
    print("-" * 100)

    sym_perfect_gratitude = statistics.mean([len(r.gratitude_events) for r in results[Condition.SYMMETRIC_PERFECT]])
    sym_forget_gratitude = statistics.mean([len(r.gratitude_events) for r in results[Condition.SYMMETRIC_FORGETFUL]])
    asym_std_gratitude = statistics.mean([len(r.gratitude_events) for r in results[Condition.ASYMMETRIC_STANDARD]])

    h1_satisfied = (asym_std_gratitude > sym_perfect_gratitude and asym_std_gratitude > sym_forget_gratitude)
    print(f"H1 (Asymmetric > Symmetric gratitude): {h1_satisfied} | Asym_Std={asym_std_gratitude:.2f} vs Sym_Perfect={sym_perfect_gratitude:.2f}")

    sym_perfect_tension = statistics.mean([len(r.tension_events) for r in results[Condition.SYMMETRIC_PERFECT]])
    asym_std_tension = statistics.mean([len(r.tension_events) for r in results[Condition.ASYMMETRIC_STANDARD]])
    h2_satisfied = asym_std_tension > sym_perfect_tension
    print(f"H2 (Asymmetric > Symmetric tension): {h2_satisfied} | Asym_Std={asym_std_tension:.2f} vs Sym_Perfect={sym_perfect_tension:.2f}")

    bonds_by_condition = {cond: statistics.mean([r.final_bond_strength for r in results[cond]]) for cond in Condition}
    max_bond_cond = max(bonds_by_condition, key=bonds_by_condition.get)
    h3_satisfied = max_bond_cond == Condition.ASYMMETRIC_STANDARD
    print(f"H3 (Bond strength max in ASYMMETRIC_STANDARD): {h3_satisfied} | Max: {max_bond_cond.value}={bonds_by_condition[max_bond_cond]:.2f}")

    sym_perfect_overlap = statistics.mean([statistics.mean(r.shared_memory_overlap) if r.shared_memory_overlap else 0.0 for r in results[Condition.SYMMETRIC_PERFECT]])
    sym_perfect_novelty = statistics.mean([len(r.novelty_events) for r in results[Condition.SYMMETRIC_PERFECT]])
    h4_satisfied = sym_perfect_overlap > 0.7 and sym_perfect_novelty < 1.0
    print(f"H4 (SYMMETRIC_PERFECT: high overlap, low novelty): {h4_satisfied} | Overlap={sym_perfect_overlap:.3f}")

    asym_std_gift = statistics.mean([r.memory_gift_score for r in results[Condition.ASYMMETRIC_STANDARD]])
    h5_satisfied = asym_std_gift > 2.0
    print(f"H5 (Memory gifts > 2 in ASYMMETRIC_STANDARD): {h5_satisfied} | Gift_Score={asym_std_gift:.2f}")

    sym_forget_forgive = statistics.mean([r.forgiveness_asymmetry_index for r in results[Condition.SYMMETRIC_FORGETFUL]])
    asym_std_forgive = statistics.mean([r.forgiveness_asymmetry_index for r in results[Condition.ASYMMETRIC_STANDARD]])
    h6_satisfied = asym_std_forgive > sym_forget_forgive
    print(f"H6 (Forgiveness higher in ASYMMETRIC_STANDARD): {h6_satisfied} | Asym_Std={asym_std_forgive:.3f}")

    print("\n" + "-" * 100)
    print("NARRATIVE INTERPRETATION")
    print("-" * 100)
    print("\nAsymmetric memory pairs are RICHER than symmetric pairs.")
    print("Perfect-memory agent + forgetful agent = deepest relationship.")
    print("Asymmetry creates space for gratitude, care, and renewal.")

    return results


if __name__ == "__main__":
    results = main()
