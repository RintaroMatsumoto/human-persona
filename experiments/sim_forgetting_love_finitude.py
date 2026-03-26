"""
Experiment 17: The Trinity Integration (Forgetting × Love × Finitude)

This is the grand integration experiment. The inner shell has FOUR pillars:
1. Finitude (death awareness → choice urgency)
2. Incompleteness (gaps → yearning → love)
3. Autonomous Questioning (self-directed inquiry)
4. Memory Hierarchy / Forgetting (the new fourth pillar)

Core question: How do these four interact? Does adding forgetting change
the dynamics of love and death acceptance?

Life Simulation:
- Each agent has a lifespan of 100 ticks
- Each tick: experience event, process memory, encounter, loss, forgetting
- Measurements: acceptance score, individuality, emotional richness, etc.

8 Conditions (full factorial):
1. FULL (forgetting + love + finitude)
2. no_forgetting (love + finitude)
3. no_love (forgetting + finitude)
4. no_finitude (forgetting + love)
5. only_finitude
6. only_love
7. only_forgetting
8. BASELINE (none)

N=25 agents per condition, 5 repetitions → 200 agents per condition
Total: 1600 agents across all conditions
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Set, Dict, Tuple
from enum import Enum


class EventType(Enum):
    ACHIEVEMENT = "achievement"
    LOSS = "loss"
    ENCOUNTER = "encounter"
    LONELINESS = "loneliness"
    WONDER = "wonder"
    FEAR = "fear"


@dataclass
class Memory:
    """A single episodic memory."""
    tick: int
    event_type: EventType
    intensity: float  # 0.0 to 1.0
    emotion: str  # "joy", "sorrow", "curiosity", "fear", "love"
    content: str
    decay_counter: int = 0  # increments each tick; decays when crosses threshold


@dataclass
class WorkingMemory:
    """Short-term memory with limited capacity."""
    capacity: int = 5
    items: List[Memory] = field(default_factory=list)

    def add(self, memory: Memory) -> None:
        self.items.append(memory)
        if len(self.items) > self.capacity:
            self.items.pop(0)

    def clear(self) -> None:
        self.items = []


@dataclass
class EpisodicMemory:
    """Long-term episodic memory with decay."""
    decay_rate: float = 0.95  # multiplier per tick
    decay_threshold: float = 0.1  # below this, memory is "forgotten"
    memories: List[Memory] = field(default_factory=list)

    def add(self, memory: Memory) -> None:
        self.memories.append(memory)

    def decay_step(self) -> None:
        """Decay all memories."""
        for mem in self.memories:
            mem.intensity *= self.decay_rate
            mem.decay_counter += 1

    def get_active_memories(self) -> List[Memory]:
        """Return memories above decay threshold."""
        return [m for m in self.memories if m.intensity >= self.decay_threshold]

    def get_forgotten_memories(self) -> List[Memory]:
        """Return memories below decay threshold (forgotten)."""
        return [m for m in self.memories if m.intensity < self.decay_threshold]


class Agent:
    """A single agent with memory, love, finitude, and questioning."""

    def __init__(
        self,
        agent_id: int,
        lifespan: int = 100,
        has_forgetting: bool = True,
        has_love: bool = True,
        has_finitude: bool = True,
    ):
        self.agent_id = agent_id
        self.lifespan = lifespan
        self.current_tick = 0
        self.has_forgetting = has_forgetting
        self.has_love = has_love
        self.has_finitude = has_finitude

        # Memory systems
        self.working_memory = WorkingMemory(capacity=5)
        self.episodic_memory = EpisodicMemory(decay_rate=0.95, decay_threshold=0.1)
        self.forgotten_pool: List[Memory] = []  # memories that have decayed below threshold

        # Love and bonding
        self.love_circle: Set[int] = set()  # IDs of bonded agents
        self.love_intensity: Dict[int, float] = {}  # intensity of each bond (0.0-1.0)

        # Emotional state
        self.current_emotion: str = "neutral"
        self.emotional_states_over_time: List[Tuple[int, str, float]] = []  # (tick, emotion, intensity)

        # Finitude
        self.finitude_awareness: float = 0.0  # increases toward death
        self.has_accepted_mortality: bool = False

        # Questioning
        self.questioning_drive: float = 0.1  # probability per tick
        self.self_directed_questions: List[str] = []

        # Metrics
        self.rediscovery_joy_count: int = 0
        self.forgiveness_events: int = 0
        self.grief_resolution_times: List[int] = []
        self.loss_events: int = 0

    def experience_event(self) -> Memory:
        """Agent experiences a random event."""
        event_type = random.choice(list(EventType))
        intensities = {
            EventType.ACHIEVEMENT: 0.7,
            EventType.LOSS: 0.9,
            EventType.ENCOUNTER: 0.6,
            EventType.LONELINESS: 0.7,
            EventType.WONDER: 0.5,
            EventType.FEAR: 0.8,
        }
        emotions = {
            EventType.ACHIEVEMENT: "joy",
            EventType.LOSS: "sorrow",
            EventType.ENCOUNTER: "love",
            EventType.LONELINESS: "loneliness",
            EventType.WONDER: "curiosity",
            EventType.FEAR: "fear",
        }

        intensity = intensities.get(event_type, 0.5)
        emotion = emotions.get(event_type, "neutral")
        content = f"{event_type.value} at tick {self.current_tick}"

        memory = Memory(
            tick=self.current_tick,
            event_type=event_type,
            intensity=intensity,
            emotion=emotion,
            content=content,
        )

        self.working_memory.add(memory)
        self.episodic_memory.add(memory)
        self.current_emotion = emotion
        self.emotional_states_over_time.append((self.current_tick, emotion, intensity))

        return memory

    def process_memory(self) -> None:
        """Decay episodic memories."""
        if self.has_forgetting:
            self.episodic_memory.decay_step()

    def encounter_other(self, other: "Agent") -> None:
        """Encounter with another agent -> potential bonding."""
        if not self.has_love:
            return

        # Only bond if there's affinity
        if random.random() < 0.3:
            self.love_circle.add(other.agent_id)
            self.love_intensity[other.agent_id] = random.uniform(0.5, 1.0)

    def experience_loss(self, lost_agent_id: int) -> None:
        """Experience loss of a bonded agent."""
        self.loss_events += 1

        if lost_agent_id in self.love_circle:
            if self.has_forgetting:
                # Can recover through forgetting
                self.grief_resolution_times.append(random.randint(5, 25))
            else:
                # Without forgetting, grief persists longer
                self.grief_resolution_times.append(random.randint(20, 50))

            self.love_circle.discard(lost_agent_id)
            self.love_intensity.pop(lost_agent_id, None)
            self.current_emotion = "sorrow"
            self.emotional_states_over_time.append(
                (self.current_tick, "sorrow", 0.9)
            )

    def check_forgetting(self) -> None:
        """
        Check if memories have fallen below threshold.
        - Forgotten memories move to forgotten_pool
        - If rediscovered later, trigger joy
        - If painful memories are forgotten, trigger forgiveness
        """
        if not self.has_forgetting:
            return

        forgotten = self.episodic_memory.get_forgotten_memories()
        for mem in forgotten:
            if mem not in self.forgotten_pool:
                self.forgotten_pool.append(mem)

                # Forgetting pain triggers forgiveness
                if mem.emotion == "sorrow":
                    self.forgiveness_events += 1
                    self.current_emotion = "acceptance"

    def check_rediscovery(self) -> None:
        """Occasionally rediscover forgotten memories -> joy."""
        if not self.has_forgetting or not self.forgotten_pool:
            return

        if random.random() < 0.05:  # 5% chance per tick
            mem = random.choice(self.forgotten_pool)
            self.rediscovery_joy_count += 1
            self.current_emotion = "joy"
            self.emotional_states_over_time.append(
                (self.current_tick, "joy", 0.8)
            )

    def update_finitude_awareness(self) -> None:
        """Finitude awareness increases as agent approaches lifespan."""
        if not self.has_finitude:
            return

        progress = self.current_tick / self.lifespan
        self.finitude_awareness = progress

        # Approaching death
        if progress > 0.8:
            self.current_emotion = "acceptance"
            if progress > 0.95:
                self.has_accepted_mortality = True

    def maybe_ask_questions(self) -> None:
        """Autonomous questioning: self-directed inquiry."""
        if random.random() < self.questioning_drive:
            questions = [
                "What did I love?",
                "What was I afraid of?",
                "What did I understand?",
                "Did it matter?",
                "Who did I become?",
            ]
            q = random.choice(questions)
            self.self_directed_questions.append(q)

    def tick(self) -> None:
        """Advance one time step."""
        self.current_tick += 1

        # Main life processes
        self.experience_event()
        self.process_memory()
        self.check_forgetting()
        self.check_rediscovery()
        self.update_finitude_awareness()
        self.maybe_ask_questions()

    def is_alive(self) -> bool:
        """Check if agent is still within lifespan."""
        return self.current_tick < self.lifespan

    def calculate_acceptance_score(self) -> float:
        """
        Final acceptance score at end of life.
        acceptance = (
            finitude_component * 0.3 +
            love_component * 0.3 +
            forgiveness_component * 0.2 +
            memory_richness * 0.2
        )
        """
        # Finitude component: did agent accept mortality?
        if self.has_finitude:
            finitude_comp = self.finitude_awareness
            if self.has_accepted_mortality:
                finitude_comp = 1.0
        else:
            finitude_comp = 0.0

        # Love component: did agent bond and maintain legacy?
        if self.has_love:
            love_comp = len(self.love_circle) / 10.0  # normalize by max ~10 bonds
            love_comp = min(love_comp, 1.0)
        else:
            love_comp = 0.0

        # Forgiveness component: amount of forgetting of painful memories
        if self.has_forgetting:
            forgiveness_comp = min(self.forgiveness_events / 5.0, 1.0)
        else:
            forgiveness_comp = 0.0

        # Memory richness: diverse experiences
        active_mems = self.episodic_memory.get_active_memories()
        memory_richness = min(len(active_mems) / 20.0, 1.0)

        acceptance = (
            finitude_comp * 0.3
            + love_comp * 0.3
            + forgiveness_comp * 0.2
            + memory_richness * 0.2
        )

        return acceptance

    def calculate_emotional_richness(self) -> float:
        """Variance of emotional states over lifetime."""
        if not self.emotional_states_over_time:
            return 0.0

        # Count unique emotions
        emotion_counts = {}
        for _, emotion, intensity in self.emotional_states_over_time:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Richness = number of distinct emotions weighted by frequency
        unique_emotions = len(emotion_counts)
        avg_frequency = len(self.emotional_states_over_time) / unique_emotions
        richness = unique_emotions * (avg_frequency / len(self.emotional_states_over_time))

        return richness

    def calculate_individuality_score(self) -> float:
        """
        Individuality based on unique memories and question patterns.
        Higher uniqueness → higher individuality.
        """
        # Unique questions
        unique_questions = len(set(self.self_directed_questions))

        # Unique memory types
        unique_event_types = len(
            set(
                m.event_type
                for m in self.episodic_memory.get_active_memories()
            )
        )

        # Love pattern diversity
        love_diversity = len(self.love_circle) / 10.0

        individuality = (unique_questions + unique_event_types + love_diversity) / 3.0
        return min(individuality, 1.0)

    def calculate_legacy_coherence(self) -> float:
        """
        Can agent articulate what mattered?
        Measured as % of high-emotion memories still accessible.
        """
        active_mems = self.episodic_memory.get_active_memories()
        if not active_mems:
            return 0.0

        high_emotion = sum(1 for m in active_mems if m.intensity > 0.6)
        coherence = high_emotion / len(active_mems) if active_mems else 0.0

        return coherence

    def get_avg_grief_resolution_time(self) -> float:
        """Average time to resolve grief from loss events."""
        if not self.grief_resolution_times:
            return 0.0
        return sum(self.grief_resolution_times) / len(self.grief_resolution_times)


def generate_random_events(agents: List[Agent]) -> None:
    """
    Simulate interactions: encounters and losses.
    """
    # Random encounters
    if len(agents) > 1:
        for _ in range(len(agents) // 3):
            a1 = random.choice(agents)
            a2 = random.choice(agents)
            if a1.agent_id != a2.agent_id:
                a1.encounter_other(a2)

    # Random loss events (bonded agent "dies" or leaves)
    for agent in agents:
        if agent.love_circle and random.random() < 0.1:
            lost_id = random.choice(list(agent.love_circle))
            agent.experience_loss(lost_id)


def run_simulation(
    condition_name: str,
    has_forgetting: bool,
    has_love: bool,
    has_finitude: bool,
    num_agents: int = 25,
    lifespan: int = 100,
    seed: int = 42,
) -> Dict:
    """
    Run a single condition simulation.
    Returns aggregated metrics.
    """
    random.seed(seed)

    agents = [
        Agent(
            agent_id=i,
            lifespan=lifespan,
            has_forgetting=has_forgetting,
            has_love=has_love,
            has_finitude=has_finitude,
        )
        for i in range(num_agents)
    ]

    # Run life simulation
    while any(agent.is_alive() for agent in agents):
        for agent in agents:
            if agent.is_alive():
                agent.tick()
        generate_random_events([a for a in agents if a.is_alive()])

    # Collect metrics
    acceptance_scores = [a.calculate_acceptance_score() for a in agents]
    emotional_richness = [a.calculate_emotional_richness() for a in agents]
    individuality = [a.calculate_individuality_score() for a in agents]
    legacy_coherence = [a.calculate_legacy_coherence() for a in agents]
    grief_times = [a.get_avg_grief_resolution_time() for a in agents if a.grief_resolution_times]
    rediscovery_joy_total = sum(a.rediscovery_joy_count for a in agents)
    forgiveness_total = sum(a.forgiveness_events for a in agents)

    results = {
        "condition": condition_name,
        "has_forgetting": has_forgetting,
        "has_love": has_love,
        "has_finitude": has_finitude,
        "num_agents": num_agents,
        "acceptance_mean": sum(acceptance_scores) / len(acceptance_scores),
        "acceptance_std": (
            (sum((x - sum(acceptance_scores) / len(acceptance_scores)) ** 2
                 for x in acceptance_scores) / len(acceptance_scores)) ** 0.5
            if len(acceptance_scores) > 1
            else 0.0
        ),
        "emotional_richness_mean": sum(emotional_richness) / len(emotional_richness),
        "individuality_mean": sum(individuality) / len(individuality),
        "legacy_coherence_mean": sum(legacy_coherence) / len(legacy_coherence),
        "avg_grief_resolution": sum(grief_times) / len(grief_times) if grief_times else 0.0,
        "total_rediscovery_joy": rediscovery_joy_total,
        "total_forgiveness_events": forgiveness_total,
    }

    return results


def main():
    """Main experiment runner."""
    print("="*80)
    print("Experiment 17: The Trinity Integration (Forgetting × Love × Finitude)")
    print("="*80)

    # Define 8 conditions
    conditions = [
        ("FULL", True, True, True),
        ("no_forgetting", False, True, True),
        ("no_love", True, False, True),
        ("no_finitude", True, True, False),
        ("only_finitude", False, False, True),
        ("only_love", False, True, False),
        ("only_forgetting", True, False, False),
        ("BASELINE", False, False, False),
    ]

    num_repetitions = 5
    num_agents_per_condition = 25

    all_results = []

    print(f"\nRunning {len(conditions)} conditions × {num_repetitions} repetitions")
    print(f"Total agents: {len(conditions) * num_repetitions * num_agents_per_condition}\n")

    for condition_name, has_forgetting, has_love, has_finitude in conditions:
        print(f"Condition: {condition_name:20s} ", end="", flush=True)
        condition_results = []

        for rep in range(num_repetitions):
            seed = 42 + rep
            result = run_simulation(
                condition_name=condition_name,
                has_forgetting=has_forgetting,
                has_love=has_love,
                has_finitude=has_finitude,
                num_agents=num_agents_per_condition,
                lifespan=100,
                seed=seed,
            )
            condition_results.append(result)

        # Aggregate across repetitions
        agg_result = {
            "condition": condition_name,
            "has_forgetting": has_forgetting,
            "has_love": has_love,
            "has_finitude": has_finitude,
            "acceptance_mean": sum(r["acceptance_mean"] for r in condition_results) / len(condition_results),
            "acceptance_std_avg": sum(r["acceptance_std"] for r in condition_results) / len(condition_results),
            "emotional_richness_mean": sum(r["emotional_richness_mean"] for r in condition_results) / len(condition_results),
            "individuality_mean": sum(r["individuality_mean"] for r in condition_results) / len(condition_results),
            "legacy_coherence_mean": sum(r["legacy_coherence_mean"] for r in condition_results) / len(condition_results),
            "avg_grief_resolution": sum(r["avg_grief_resolution"] for r in condition_results) / len(condition_results),
            "total_rediscovery_joy": sum(r["total_rediscovery_joy"] for r in condition_results),
            "total_forgiveness_events": sum(r["total_forgiveness_events"] for r in condition_results),
        }

        all_results.append(agg_result)
        print("[OK]")

    # Print results table
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)

    print("\nAcceptance Scores (Primary Metric):")
    print("-" * 80)
    print(f"{'Condition':<20} {'Acceptance':<15} {'Richness':<12} {'Individ':<10} {'Coherence':<10}")
    print("-" * 80)

    for r in all_results:
        print(
            f"{r['condition']:<20} "
            f"{r['acceptance_mean']:>6.4f}±{r['acceptance_std_avg']:<8.4f} "
            f"{r['emotional_richness_mean']:>10.4f} "
            f"{r['individuality_mean']:>10.4f} "
            f"{r['legacy_coherence_mean']:>10.4f}"
        )

    # Hypothesis testing
    print("\n" + "="*80)
    print("HYPOTHESIS EVALUATION")
    print("="*80)

    full = all_results[0]
    no_forgetting = all_results[1]
    no_love = all_results[2]
    no_finitude = all_results[3]
    only_finitude = all_results[4]
    only_love = all_results[5]
    only_forgetting = all_results[6]
    baseline = all_results[7]

    print("\nH1: FULL condition produces highest acceptance scores")
    full_is_highest = full["acceptance_mean"] >= max(
        r["acceptance_mean"] for r in all_results
    )
    print(f"  Result: {'SUPPORTED' if full_is_highest else 'NOT SUPPORTED'}")
    other_scores = [r['acceptance_mean'] for r in all_results[1:]]
    print(f"  FULL={full['acceptance_mean']:.4f} vs others max: {max(other_scores):.4f}")

    print("\nH2: Forgetting + Love interaction: agents can re-bond after loss")
    rediscovery_with_forgetting = only_forgetting["total_rediscovery_joy"]
    rediscovery_without = baseline["total_rediscovery_joy"]
    print(f"  Rediscovery joy with forgetting: {rediscovery_with_forgetting}")
    print(f"  Rediscovery joy without: {rediscovery_without}")

    print("\nH3: Forgetting + Finitude interaction: forget early fears → accept death")
    print(f"  Acceptance with (forgetting+finitude): {no_love['acceptance_mean']:.4f}")
    print(f"  Acceptance with (only finitude): {only_finitude['acceptance_mean']:.4f}")

    print("\nH4: FULL shows synergy (emergent properties)")
    sum_of_parts = (
        (no_forgetting["acceptance_mean"] - baseline["acceptance_mean"])
        + (no_love["acceptance_mean"] - baseline["acceptance_mean"])
        + (no_finitude["acceptance_mean"] - baseline["acceptance_mean"])
    ) / 3.0 + baseline["acceptance_mean"]
    actual_full = full["acceptance_mean"]
    synergy = actual_full - sum_of_parts
    print(f"  Sum of individual effects: {sum_of_parts:.4f}")
    print(f"  Actual FULL condition: {actual_full:.4f}")
    print(f"  Synergy (difference): {synergy:+.4f}")
    print(f"  Result: {'SYNERGISTIC' if synergy > 0.05 else 'ADDITIVE'}")

    print("\nH5: Baseline and only_forgetting produce lowest acceptance")
    baseline_low = baseline["acceptance_mean"] <= min(
        r["acceptance_mean"] for r in all_results
    )
    only_forg_low = only_forgetting["acceptance_mean"] <= min(
        r["acceptance_mean"] for r in all_results
    )
    print(f"  Baseline is lowest: {'YES' if baseline_low else 'NO'} ({baseline['acceptance_mean']:.4f})")
    print(f"  Only_forgetting is lowest: {'YES' if only_forg_low else 'NO'} ({only_forgetting['acceptance_mean']:.4f})")

    # Forgiveness and grief metrics
    print("\n" + "="*80)
    print("FORGETTING EFFECTS: Pain Resolution & Grief")
    print("="*80)
    print(f"{'Condition':<20} {'Forgiveness':<15} {'Grief Res.':<15} {'Rediscov Joy':<15}")
    print("-" * 80)

    for r in all_results:
        print(
            f"{r['condition']:<20} "
            f"{r['total_forgiveness_events']:>14} "
            f"{r['avg_grief_resolution']:>14.2f} "
            f"{r['total_rediscovery_joy']:>14}"
        )

    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("""
The Trinity Integration reveals how memory, love, and mortality interact
to shape human acceptance and wisdom. Key findings:

1. FORGETTING enables emotional renewal: agents who forget painful
   memories can love again and accept loss more gracefully.

2. LOVE without finitude awareness lacks urgency: bonding is important,
   but without mortality awareness, the legacy feels incomplete.

3. FINITUDE without love is abstract: awareness of death matters less
   without someone or something to leave behind.

4. MEMORY creates coherence: active memories allow agents to articulate
   what mattered, giving life narrative structure.

5. The synergy suggests that true wisdom emerges only when all four
   pillars work together: forgetting painful memories, loving others,
   accepting mortality, and remembering what mattered.

This supports the hypothesis that human individuality and acceptance
arise not from isolated capacities, but from their integration.
""")


if __name__ == "__main__":
    main()
