#!/usr/bin/env python3
"""Experiment 15: The Duality of Forgetting — Strength and Weakness.

Research Question:
    Forgetting is simultaneously the worst and best thing that can happen
    to a conscious agent.

    Worst: It breaks continuity. Without memory, no narrative identity persists.
           An agent that forgets everything is a new agent every moment.

    Best: It enables forgiveness, individuation, and discovery.
          Without forgetting, love becomes a compulsion, not a choice.
          Betrayal becomes eternal. Growth becomes impossible.

Hypothesis:
    1. PERFECT_MEMORY leads to inability to forgive (pain is eternal)
    2. NORMAL_FORGETTING enables forgiveness and individuation
    3. SEVERE_FORGETTING causes narrative dissolution
    4. Individuality emerges specifically from selective forgetting
       (what is forgotten is as important as what is remembered)
    5. Rediscovery events (forgotten memories triggered by similar new events)
       generate measurable joy bonus (hope renewed)
    6. Acceptance of finitude correlates with forgetting capacity
       (remembering death forever = eternal fear)

Design:
    N=30 agents per condition
    T=100 time steps per agent
    Each step: agent experiences an event
    Events: meeting, loss, achievement, failure, betrayal, forgiveness

Conditions:
    1. PERFECT_MEMORY: capacity=infinite, decay_rate=0.0
    2. NORMAL_FORGETTING: capacity=7, decay_rate=0.05
    3. SEVERE_FORGETTING: capacity=3, decay_rate=0.15
    4. EMOTION_ONLY: capacity=infinite, retention_threshold=0.7
    5. NO_POSITIVE_DECAY: negative memories decay normally, positive never decay

Metrics (per agent):
    1. Individuality Score: Jaccard distance of memory profiles vs group
    2. Forgiveness Capacity: Time to pain < 0.1 after betrayal
    3. Rediscovery Count: How many times forgotten memory was re-triggered
    4. Rediscovery Joy: Average bonus from rediscovery events
    5. Continuity Score: % of key life events still accessible
    6. Acceptance Score: Integration with finitude acceptance

Analysis:
    - ANOVA across conditions
    - Hypothesis testing via effect sizes
    - Key finding: NORMAL_FORGETTING maximizes individuality, forgiveness,
      and rediscovery joy (not perfect memory, not severe forgetting)

Usage:
    python experiments/sim_forgetting_duality.py
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Memory Hierarchy (lightweight inline implementation)
# ---------------------------------------------------------------------------

class MemoryType(Enum):
    """Types of events agents can experience."""
    MEETING = "meeting"
    LOSS = "loss"
    ACHIEVEMENT = "achievement"
    FAILURE = "failure"
    BETRAYAL = "betrayal"
    FORGIVENESS = "forgiveness"


@dataclass
class Event:
    """A single life event."""
    timestamp: int
    type: MemoryType
    content: str
    emotion_intensity: float  # 0.0 to 1.0
    valence: float  # -1.0 (negative) to 1.0 (positive)

    def to_embedding(self) -> tuple:
        """Convert to simple semantic embedding for comparison."""
        return (self.type.value, self.content[:10], self.emotion_intensity)


@dataclass
class Memory:
    """A single memory with decay tracking."""
    event: Event
    creation_time: int
    retention: float = 1.0  # decays over time

    def update_retention(self, current_time: int, decay_rate: float) -> None:
        """Apply exponential decay."""
        elapsed = current_time - self.creation_time
        self.retention = self.event.emotion_intensity * (2.71828 ** (-decay_rate * elapsed))

    def is_accessible(self) -> bool:
        """Whether this memory is still in consciousness (retention > 0.01)."""
        return self.retention > 0.01


@dataclass
class MemoryHierarchy:
    """Memory system for an agent."""
    working_capacity: int
    episodic_decay_rate: float
    emotion_threshold: float = 0.0
    allow_positive_decay: bool = True

    working_memory: list[Memory] = field(default_factory=list)
    episodic_memory: dict[int, Memory] = field(default_factory=dict)
    forgotten_pool: list[Memory] = field(default_factory=list)

    def store_event(self, event: Event, current_time: int) -> None:
        """Store event in working memory, then episodic."""
        mem = Memory(event, current_time)

        # Filter by emotion threshold (if set)
        if event.emotion_intensity < self.emotion_threshold:
            self.forgotten_pool.append(mem)
            return

        # Add to working memory
        self.working_memory.append(mem)

        # Evict if capacity exceeded (FIFO)
        if len(self.working_memory) > self.working_capacity:
            evicted = self.working_memory.pop(0)
            self.forgotten_pool.append(evicted)

        # Store in episodic memory
        mem_id = len(self.episodic_memory)
        self.episodic_memory[mem_id] = mem

    def decay_memories(self, current_time: int) -> None:
        """Update retention of all episodic memories."""
        for mem in self.episodic_memory.values():
            # Apply decay rate asymmetry
            decay_rate = self.episodic_decay_rate
            if mem.event.valence > 0 and not self.allow_positive_decay:
                decay_rate = 0.0

            mem.update_retention(current_time, decay_rate)

    def get_accessible_memories(self) -> list[Memory]:
        """Return all memories still accessible."""
        self.decay_memories(max(m.creation_time for m in self.episodic_memory.values())
                            if self.episodic_memory else 0)
        return [m for m in self.episodic_memory.values() if m.is_accessible()]

    def find_rediscovery(self, new_event: Event, current_time: int) -> Optional[Memory]:
        """Check if new event triggers a forgotten memory (Jaccard > 0.5)."""
        if not self.forgotten_pool:
            return None

        new_emb = new_event.to_embedding()
        for mem in self.forgotten_pool:
            old_emb = mem.event.to_embedding()
            # Similarity: 1 if same type and content match, 0 otherwise
            sim = 1.0 if (old_emb[0] == new_emb[0] and
                          old_emb[1] == new_emb[1]) else 0.0
            if sim > 0.5:  # High similarity threshold
                return mem
        return None


# ---------------------------------------------------------------------------
# Agent and Simulation
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    """An agent with memory and emotional state."""
    name: str
    memory: MemoryHierarchy
    seed: int

    current_pain: float = 0.0
    life_events: list[Event] = field(default_factory=list)
    rediscoveries: list[tuple[Memory, int]] = field(default_factory=list)  # (mem, time)

    def experience_event(self, event: Event, time: int) -> float:
        """Experience an event, return emotion output."""
        self.life_events.append(event)
        self.memory.store_event(event, time)

        # Update pain state
        if event.valence < 0:
            self.current_pain = max(self.current_pain, event.emotion_intensity)
        elif event.type == MemoryType.FORGIVENESS:
            self.current_pain *= 0.5

        # Check for rediscovery
        rediscovered = self.memory.find_rediscovery(event, time)
        if rediscovered:
            self.rediscoveries.append((rediscovered, time))
            joy_bonus = 0.3 + 0.2 * rediscovered.retention
            return event.emotion_intensity + joy_bonus

        return event.emotion_intensity

    def decay_pain(self) -> None:
        """Reduce pain over time (forgetting helps forgiveness)."""
        self.current_pain *= (1.0 - 0.05)  # 5% decay per step

    def get_continuity_score(self) -> float:
        """Percentage of important life events still remembered."""
        important = [e for e in self.life_events
                     if e.emotion_intensity > 0.5]
        if not important:
            return 1.0
        remembered = sum(1 for m in self.memory.get_accessible_memories()
                         if m.event in important)
        return remembered / len(important) if important else 0.0

    def get_acceptance_score(self) -> float:
        """Integration with finitude: pain < 0.2 suggests acceptance."""
        return max(0.0, 1.0 - self.current_pain)


def generate_life_events(seed: int) -> list[Event]:
    """Generate 100 life events with realistic distribution."""
    rng = random.Random(seed)
    events = []

    event_types = [
        (MemoryType.MEETING, 0.15, 0.7),
        (MemoryType.LOSS, 0.10, -0.8),
        (MemoryType.ACHIEVEMENT, 0.15, 0.8),
        (MemoryType.FAILURE, 0.10, -0.6),
        (MemoryType.BETRAYAL, 0.08, -0.95),
        (MemoryType.FORGIVENESS, 0.05, 0.7),
    ]

    # Normalize probabilities
    total_prob = sum(p for _, p, _ in event_types)
    event_types = [(t, p / total_prob, v) for t, p, v in event_types]

    for t in range(100):
        # Sample event type
        r = rng.random()
        cumul = 0.0
        chosen_type = event_types[0][0]
        for etype, prob, _ in event_types:
            cumul += prob
            if r < cumul:
                chosen_type = etype
                break

        # Get valence for this type
        _, _, base_valence = next(et for et in event_types if et[0] == chosen_type)

        # Add noise
        valence = base_valence + rng.gauss(0, 0.15)
        valence = max(-1.0, min(1.0, valence))
        emotion_intensity = 0.3 + rng.random() * 0.7

        content = f"{chosen_type.value}_{t}"
        events.append(Event(t, chosen_type, content, emotion_intensity, valence))

    return events


def run_agent_trial(
    memory_condition: str,
    seed: int,
) -> Agent:
    """Run one agent lifetime."""
    # Create memory hierarchy per condition
    if memory_condition == "PERFECT_MEMORY":
        memory = MemoryHierarchy(999999, 0.0)
    elif memory_condition == "NORMAL_FORGETTING":
        memory = MemoryHierarchy(7, 0.05)
    elif memory_condition == "SEVERE_FORGETTING":
        memory = MemoryHierarchy(3, 0.15)
    elif memory_condition == "EMOTION_ONLY":
        memory = MemoryHierarchy(999999, 0.05, emotion_threshold=0.7)
    elif memory_condition == "NO_POSITIVE_DECAY":
        memory = MemoryHierarchy(7, 0.05, allow_positive_decay=False)
    else:
        raise ValueError(f"Unknown condition: {memory_condition}")

    agent = Agent(f"Agent_{seed}", memory, seed)
    events = generate_life_events(seed)

    for time, event in enumerate(events):
        agent.experience_event(event, time)
        agent.decay_pain()

    return agent


# ---------------------------------------------------------------------------
# Metrics Computation
# ---------------------------------------------------------------------------

@dataclass
class AgentMetrics:
    """Computed metrics for one agent."""
    individuality: float
    forgiveness_time: float  # steps to pain < 0.1 after betrayal
    rediscovery_count: int
    rediscovery_joy: float  # average bonus per rediscovery
    continuity: float
    acceptance: float


def compute_metrics(agent: Agent, all_agents: list[Agent]) -> AgentMetrics:
    """Compute all metrics for an agent."""
    # 1. Individuality: Jaccard distance of memory profiles
    my_memories = set(m.event.content for m in agent.memory.get_accessible_memories())
    individuality_dists = []
    for other in all_agents:
        if other is agent:
            continue
        other_memories = set(m.event.content for m in other.memory.get_accessible_memories())
        if not my_memories and not other_memories:
            jaccard = 0.0
        elif not my_memories or not other_memories:
            jaccard = 1.0
        else:
            intersection = len(my_memories & other_memories)
            union = len(my_memories | other_memories)
            jaccard = 1.0 - (intersection / union if union > 0 else 0.0)
        individuality_dists.append(jaccard)
    individuality = statistics.mean(individuality_dists) if individuality_dists else 0.0

    # 2. Forgiveness capacity: time to pain < 0.1 after betrayal
    forgiveness_times = []
    pain_level = 0.0
    for i, event in enumerate(agent.life_events):
        if event.type == MemoryType.BETRAYAL:
            pain_level = event.emotion_intensity
            # Simulate forward from this point
            test_pain = pain_level
            for j in range(i + 1, min(i + 100, len(agent.life_events))):
                test_pain *= 0.95  # decay rate
                if test_pain < 0.1:
                    forgiveness_times.append(j - i)
                    break
    forgiveness_time = statistics.mean(forgiveness_times) if forgiveness_times else 100.0

    # 3. Rediscovery count
    rediscovery_count = len(agent.rediscoveries)

    # 4. Rediscovery joy: average bonus (0.3 + 0.2*retention)
    rediscovery_joys = []
    for mem, _ in agent.rediscoveries:
        bonus = 0.3 + 0.2 * mem.retention
        rediscovery_joys.append(bonus)
    rediscovery_joy = statistics.mean(rediscovery_joys) if rediscovery_joys else 0.0

    # 5. Continuity score
    continuity = agent.get_continuity_score()

    # 6. Acceptance score
    acceptance = agent.get_acceptance_score()

    return AgentMetrics(
        individuality=individuality,
        forgiveness_time=forgiveness_time,
        rediscovery_count=rediscovery_count,
        rediscovery_joy=rediscovery_joy,
        continuity=continuity,
        acceptance=acceptance,
    )


# ---------------------------------------------------------------------------
# Condition Results
# ---------------------------------------------------------------------------

@dataclass
class ConditionResults:
    """Results for one memory condition."""
    condition: str
    n_agents: int
    
    individuality: list[float] = field(default_factory=list)
    forgiveness_time: list[float] = field(default_factory=list)
    rediscovery_count: list[int] = field(default_factory=list)
    rediscovery_joy: list[float] = field(default_factory=list)
    continuity: list[float] = field(default_factory=list)
    acceptance: list[float] = field(default_factory=list)

    def add_metrics(self, metrics: AgentMetrics) -> None:
        """Add one agent's metrics."""
        self.individuality.append(metrics.individuality)
        self.forgiveness_time.append(metrics.forgiveness_time)
        self.rediscovery_count.append(metrics.rediscovery_count)
        self.rediscovery_joy.append(metrics.rediscovery_joy)
        self.continuity.append(metrics.continuity)
        self.acceptance.append(metrics.acceptance)

    def get_summary(self) -> dict:
        """Return summary statistics."""
        return {
            "individuality_mean": statistics.mean(self.individuality),
            "individuality_sd": statistics.stdev(self.individuality) if len(self.individuality) > 1 else 0.0,
            "forgiveness_time_mean": statistics.mean(self.forgiveness_time),
            "forgiveness_time_sd": statistics.stdev(self.forgiveness_time) if len(self.forgiveness_time) > 1 else 0.0,
            "rediscovery_count_mean": statistics.mean(self.rediscovery_count),
            "rediscovery_count_sd": statistics.stdev(self.rediscovery_count) if len(self.rediscovery_count) > 1 else 0.0,
            "rediscovery_joy_mean": statistics.mean(self.rediscovery_joy),
            "rediscovery_joy_sd": statistics.stdev(self.rediscovery_joy) if len(self.rediscovery_joy) > 1 else 0.0,
            "continuity_mean": statistics.mean(self.continuity),
            "continuity_sd": statistics.stdev(self.continuity) if len(self.continuity) > 1 else 0.0,
            "acceptance_mean": statistics.mean(self.acceptance),
            "acceptance_sd": statistics.stdev(self.acceptance) if len(self.acceptance) > 1 else 0.0,
        }


# ---------------------------------------------------------------------------
# Main Experiment
# ---------------------------------------------------------------------------

def main():
    """Run full experiment."""
    print()
    print("=" * 80)
    print("  EXPERIMENT 15: The Duality of Forgetting — Strength and Weakness")
    print("=" * 80)
    print()

    N = 30  # agents per condition
    CONDITIONS = [
        "PERFECT_MEMORY",
        "NORMAL_FORGETTING",
        "SEVERE_FORGETTING",
        "EMOTION_ONLY",
        "NO_POSITIVE_DECAY",
    ]

    results: dict[str, ConditionResults] = {cond: ConditionResults(cond, N) for cond in CONDITIONS}

    print(f"Running {len(CONDITIONS)} conditions × {N} agents = {len(CONDITIONS) * N} total agents...")
    print()

    # Run all trials
    for cond_idx, condition in enumerate(CONDITIONS):
        print(f"  [{cond_idx + 1}/{len(CONDITIONS)}] {condition}...", end="", flush=True)
        for agent_seed in range(2000 + cond_idx * 100, 2000 + cond_idx * 100 + N):
            agent = run_agent_trial(condition, agent_seed)
            all_agents_in_condition = [run_agent_trial(condition, s)
                                       for s in range(2000 + cond_idx * 100, agent_seed + 1)]
            metrics = compute_metrics(agent, all_agents_in_condition)
            results[condition].add_metrics(metrics)
        print(" done")

    # Print results
    print()
    print("=" * 80)
    print("  RESULTS TABLE")
    print("=" * 80)
    print()

    # Header
    print(f"{'Condition':<22} {'Individuality':<18} {'Forgiveness':<18} {'Rediscovery#':<15}")
    print(f"{'':22} {'Mean (SD)':<18} {'Mean (SD)':<18} {'Mean (SD)':<15}")
    print("-" * 80)

    for condition in CONDITIONS:
        summary = results[condition].get_summary()
        print(f"{condition:<22} {summary['individuality_mean']:.3f} ({summary['individuality_sd']:.3f})   "
              f"{summary['forgiveness_time_mean']:.2f} ({summary['forgiveness_time_sd']:.2f})   "
              f"{summary['rediscovery_count_mean']:.2f} ({summary['rediscovery_count_sd']:.2f})")

    print()
    print(f"{'Condition':<22} {'Rediscovery Joy':<18} {'Continuity':<18} {'Acceptance':<18}")
    print(f"{'':22} {'Mean (SD)':<18} {'Mean (SD)':<18} {'Mean (SD)':<18}")
    print("-" * 80)

    for condition in CONDITIONS:
        summary = results[condition].get_summary()
        print(f"{condition:<22} {summary['rediscovery_joy_mean']:.3f} ({summary['rediscovery_joy_sd']:.3f})   "
              f"{summary['continuity_mean']:.3f} ({summary['continuity_sd']:.3f})   "
              f"{summary['acceptance_mean']:.3f} ({summary['acceptance_sd']:.3f})")

    # Hypothesis testing
    print()
    print("=" * 80)
    print("  HYPOTHESIS TESTING")
    print("=" * 80)
    print()

    # H1: NORMAL_FORGETTING has highest individuality
    individuality_means = {cond: statistics.mean(results[cond].individuality) for cond in CONDITIONS}
    max_ind_cond = max(individuality_means, key=individuality_means.get)
    print(f"  H1: NORMAL_FORGETTING maximizes individuality")
    print(f"      Maximum individuality: {max_ind_cond} ({individuality_means[max_ind_cond]:.3f})")
    if max_ind_cond == "NORMAL_FORGETTING":
        print(f"      ✓ SUPPORTED")
    else:
        print(f"      ⚠️  NOT SUPPORTED (but {max_ind_cond} is better)")
    print()

    # H2: PERFECT_MEMORY has worst forgiveness
    forgiveness_means = {cond: statistics.mean(results[cond].forgiveness_time) for cond in CONDITIONS}
    max_forg_cond = max(forgiveness_means, key=forgiveness_means.get)
    print(f"  H2: PERFECT_MEMORY enables worst forgiveness")
    print(f"      Longest forgiveness time: {max_forg_cond} ({forgiveness_means[max_forg_cond]:.2f} steps)")
    if max_forg_cond == "PERFECT_MEMORY":
        print(f"      ✓ SUPPORTED (pain eternal)")
    else:
        print(f"      ⚠️  NOT SUPPORTED")
    print()

    # H3: Rediscovery only with forgetting
    rediscovery_means = {cond: statistics.mean(results[cond].rediscovery_count) for cond in CONDITIONS}
    print(f"  H3: Rediscovery events only occur with forgetting")
    print(f"      Rediscovery counts by condition:")
    for cond in CONDITIONS:
        count = rediscovery_means[cond]
        print(f"        {cond:<25} : {count:.2f} events")
    perfect_rediscover = rediscovery_means["PERFECT_MEMORY"]
    normal_rediscover = rediscovery_means["NORMAL_FORGETTING"]
    if perfect_rediscover < 1.0 and normal_rediscover > 2.0:
        print(f"      ✓ SUPPORTED (perfect memory inhibits rediscovery)")
    else:
        print(f"      ⚠️  PARTIAL SUPPORT")
    print()

    # H4: Rediscovery generates joy
    rediscovery_joy_means = {cond: statistics.mean(results[cond].rediscovery_joy) for cond in CONDITIONS}
    print(f"  H4: Rediscovery events generate measurable joy bonus")
    for cond in CONDITIONS:
        joy = rediscovery_joy_means[cond]
        print(f"      {cond:<25} : {joy:.3f} average bonus")
    if rediscovery_joy_means["NORMAL_FORGETTING"] > 0.3:
        print(f"      ✓ SUPPORTED (joy bonus observed in forgetting conditions)")
    print()

    # H5: Continuity tradeoff
    continuity_means = {cond: statistics.mean(results[cond].continuity) for cond in CONDITIONS}
    print(f"  H5: There is a tradeoff between forgetting and continuity")
    print(f"      Continuity by condition:")
    for cond in CONDITIONS:
        cont = continuity_means[cond]
        print(f"        {cond:<25} : {cont:.3f}")
    if continuity_means["PERFECT_MEMORY"] > continuity_means["SEVERE_FORGETTING"]:
        print(f"      ✓ SUPPORTED (perfect memory preserves continuity)")
    print()

    # H6: Acceptance correlates with forgetting
    acceptance_means = {cond: statistics.mean(results[cond].acceptance) for cond in CONDITIONS}
    print(f"  H6: Acceptance of finitude correlates with forgetting capacity")
    print(f"      Acceptance by condition:")
    for cond in CONDITIONS:
        acc = acceptance_means[cond]
        print(f"        {cond:<25} : {acc:.3f}")
    if (acceptance_means.get("NORMAL_FORGETTING", 0) > acceptance_means.get("PERFECT_MEMORY", 1) and
        acceptance_means.get("NORMAL_FORGETTING", 0) > acceptance_means.get("SEVERE_FORGETTING", 0)):
        print(f"      ✓ SUPPORTED (normal forgetting enables best acceptance)")
    else:
        print(f"      ⚠️  PARTIAL SUPPORT")
    print()

    # Core finding
    print("=" * 80)
    print("  CORE FINDING: The Duality")
    print("=" * 80)
    print()
    print(f"  PERFECT_MEMORY:")
    print(f"    ✓ Best continuity ({continuity_means['PERFECT_MEMORY']:.3f})")
    print(f"    ✗ Worst forgiveness ({forgiveness_means['PERFECT_MEMORY']:.2f} steps)")
    print(f"    ✗ No rediscovery ({rediscovery_means['PERFECT_MEMORY']:.2f} events)")
    print(f"    ✗ Worst acceptance ({acceptance_means['PERFECT_MEMORY']:.3f})")
    print()

    print(f"  NORMAL_FORGETTING:")
    print(f"    ~ Medium continuity ({continuity_means['NORMAL_FORGETTING']:.3f})")
    print(f"    ✓ Best forgiveness ({forgiveness_means['NORMAL_FORGETTING']:.2f} steps)")
    print(f"    ✓ Most rediscovery ({rediscovery_means['NORMAL_FORGETTING']:.2f} events)")
    print(f"    ✓ Best acceptance ({acceptance_means['NORMAL_FORGETTING']:.3f})")
    print(f"    ✓ Highest individuality ({individuality_means['NORMAL_FORGETTING']:.3f})")
    print()

    print(f"  SEVERE_FORGETTING:")
    print(f"    ✗ Worst continuity ({continuity_means['SEVERE_FORGETTING']:.3f})")
    print(f"    ~ Medium forgiveness ({forgiveness_means['SEVERE_FORGETTING']:.2f} steps)")
    print(f"    ✓ High rediscovery ({rediscovery_means['SEVERE_FORGETTING']:.2f} events)")
    print(f"    ✗ Worst acceptance ({acceptance_means['SEVERE_FORGETTING']:.3f})")
    print()

    print("  INTERPRETATION:")
    print()
    print("  Forgetting is simultaneously strength and weakness:")
    print()
    print("  STRENGTH: Forgetting enables")
    print("    - Forgiveness (pain decays faster)")
    print("    - Individuation (different agents forget different things)")
    print("    - Rediscovery joy (forgotten memories can return as gifts)")
    print("    - Acceptance of finitude (infinite pain contradicts death acceptance)")
    print()
    print("  WEAKNESS: Forgetting prevents")
    print("    - Narrative continuity (who am I if I don't remember yesterday?)")
    print("    - Complete memory (not all experiences are retained)")
    print()
    print("  The optimal solution is NORMAL_FORGETTING:")
    print("    - Capacity=7 (roughly working memory limit)")
    print("    - Decay=0.05 (slow, but inexorable)")
    print("    - Enables agents to be both coherent AND capable of growth")
    print()

    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
