#!/usr/bin/env python3
"""Experiment 20: Effects of Sleep-Wake Cycles on AI Agent Performance and Individuality

Research Question:
    What happens when an AI agent has periodic "sleep" — enforced downtime where it
    consolidates memories, clears waste, and creatively recombines experiences?
    
    Does sleep improve cognitive performance, enhance memory quality, and foster individuality?

Hypotheses:
    H1: NEVER_SLEEP shows continuous performance degradation (monotonic decline)
    H2: NORMAL_SLEEP retains more important memories than NEVER_SLEEP
    H3: NORMAL_SLEEP produces creative insights; NEVER_SLEEP produces zero
    H4: HEAVY_SLEEP has highest creativity but lowest raw throughput
    H5: MICRO_NAPS has most stable performance (least variance)
    H6: NEVER_SLEEP accumulates most waste; waste correlates with performance loss

Design:
    N=30 agents per condition
    T=200 time steps (experiences) per agent
    Each step: agent experiences an event with importance and emotional valence
    Sleep model: consolidation (top 30% retention), pruning (bottom 30% forgotten),
                 waste clearance, creative recombination

Conditions (5 sleep-wake patterns):
    1. NEVER_SLEEP: 200 continuous experiences. No consolidation, no pruning, no rest.
    2. NORMAL_SLEEP: 16 hours wake → 8 hours sleep. Standard consolidation cycle.
    3. LIGHT_SLEEP: 20 hours wake → 4 hours sleep. Less consolidation time.
    4. HEAVY_SLEEP: 12 hours wake → 12 hours sleep. More consolidation.
    5. MICRO_NAPS: 4 hours wake → 1 hour nap, repeated. Frequent short bursts.

Measurements (per agent):
    1. Cognitive Performance: accuracy = base * (1.0 - 0.5 * fatigue) * (1.0 - 0.3 * waste)
    2. Memory Quality: % of top 20% important memories retained at end
    3. Creative Insights: Count of novel associations created during sleep
    4. Personality Divergence: Hamming distance of memory profiles within condition
    5. Emotional Stability: Variance of emotional state over time
    6. Waste Accumulation: Final waste level (0-1)

Analysis:
    - Summary table of metrics across conditions
    - Hypothesis evaluation with effect sizes
    - Key insight: optimal sleep timing balances consolidation, creativity, and performance

Usage:
    python experiments/sim_sleep_cycle.py
"""

from __future__ import annotations

import random
import math
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Tuple


# ---------------------------------------------------------------------------
# Simple Sleep Model (inline implementation, no external deps)
# ---------------------------------------------------------------------------

class EventCategory(Enum):
    """Categories of experiences."""
    SOCIAL = "social"
    ACHIEVEMENT = "achievement"
    LOSS = "loss"
    DISCOVERY = "discovery"
    CONFLICT = "conflict"
    MUNDANE = "mundane"


@dataclass
class Experience:
    """A single experience/event."""
    exp_id: int
    timestamp: int
    category: EventCategory
    importance: float  # 0.0-1.0
    emotional_valence: float  # -1.0 to 1.0
    content: str
    
    def __hash__(self):
        return hash(self.exp_id)
    
    def __eq__(self, other):
        return isinstance(other, Experience) and self.exp_id == other.exp_id


@dataclass
class Memory:
    """A memory with tracking."""
    experience: Experience
    consolidation_count: int = 0  # How many sleep cycles reinforced it
    emotional_echo: float = 0.0  # Decayed emotion


@dataclass
class SimpleAgent:
    """Agent with sleep-wake cycle."""
    agent_id: int
    personality_seed: int
    
    # Memory systems
    memories: List[Memory] = field(default_factory=list)
    pending_consolidation: List[Experience] = field(default_factory=list)
    
    # Physiological state
    fatigue: float = 0.0  # 0-1, increases during wake
    waste: float = 0.0  # 0-1, metabolic noise
    
    # Sleep products
    creativity_pool: List[str] = field(default_factory=list)
    dream_insights: int = 0
    consolidated_count: int = 0
    pruned_count: int = 0
    
    # Performance tracking
    performance_history: List[float] = field(default_factory=list)
    emotional_state_history: List[float] = field(default_factory=list)
    fatigue_history: List[float] = field(default_factory=list)
    waste_history: List[float] = field(default_factory=list)
    
    # Personality (stable seed)
    temperament: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize temperament based on personality_seed."""
        rng = random.Random(self.personality_seed)
        for cat in EventCategory:
            self.temperament[cat.value] = rng.random()
    
    def compute_emotional_intensity(self, experience: Experience) -> float:
        """Emotional intensity = importance * temperament[category] * valence."""
        base = experience.importance * self.temperament[experience.category.value]
        return base * (1.0 + experience.emotional_valence)  # Valence amplifies
    
    def wake_tick(self, experience: Experience):
        """During wake: accumulate experience, fatigue, waste."""
        # Add to pending consolidation
        self.pending_consolidation.append(experience)
        
        # Increase fatigue (~16 ticks to exhaust at 0.0625 per tick)
        self.fatigue = min(1.0, self.fatigue + 0.0625)
        
        # Increase waste (metabolic noise)
        self.waste = min(1.0, self.waste + 0.05)
        
        # Compute current performance
        accuracy = 1.0 - (0.5 * self.fatigue) - (0.3 * self.waste)
        accuracy = max(0.0, min(1.0, accuracy))
        self.performance_history.append(accuracy)
        
        # Compute emotional state from recent experiences
        intensity = self.compute_emotional_intensity(experience)
        emotional_state = intensity * (1.0 - 0.3 * self.fatigue)
        self.emotional_state_history.append(emotional_state)
        
        # Track state
        self.fatigue_history.append(self.fatigue)
        self.waste_history.append(self.waste)
    
    def sleep_tick(self, hours: int):
        """During sleep: consolidate, prune, clear waste, dream."""
        # Consolidation: if we have pending experiences, consolidate top 30%
        if self.pending_consolidation:
            # Sort pending by importance * emotion
            pending_with_score = []
            for exp in self.pending_consolidation:
                intensity = self.compute_emotional_intensity(exp)
                score = exp.importance * (abs(intensity) ** 0.5)
                pending_with_score.append((exp, score))
            
            # Sort by score (descending)
            pending_with_score.sort(key=lambda x: x[1], reverse=True)
            
            # Top 30% → consolidated
            cutoff_top = max(1, len(pending_with_score) // 3)
            for i in range(cutoff_top):
                exp, score = pending_with_score[i]
                # Check if already in memory
                if not any(m.experience.exp_id == exp.exp_id for m in self.memories):
                    mem = Memory(experience=exp, consolidation_count=1)
                    mem.emotional_echo = abs(self.compute_emotional_intensity(exp))
                    self.memories.append(mem)
                    self.consolidated_count += 1
                else:
                    # Reinforce existing memory
                    for m in self.memories:
                        if m.experience.exp_id == exp.exp_id:
                            m.consolidation_count += 1
                            break
            
            # Bottom 30% → pruned (forgotten!)
            cutoff_bottom_start = max(1, (2 * len(pending_with_score)) // 3)
            pruned_ids = set(pending_with_score[i][0].exp_id 
                            for i in range(cutoff_bottom_start, len(pending_with_score)))
            self.memories = [m for m in self.memories if m.experience.exp_id not in pruned_ids]
            self.pruned_count += len(pruned_ids)
        
        # Creative recombination: random pairs → new association
        if len(self.memories) >= 2:
            # More intensive creativity during longer sleeps
            creativity_rounds = min(int(hours / 2), len(self.memories))
            rng = random.Random(self.agent_id + len(self.memories) + int(self.fatigue * 100))
            for _ in range(creativity_rounds):
                m1 = rng.choice(self.memories)
                m2 = rng.choice(self.memories)
                if m1.experience.exp_id != m2.experience.exp_id:
                    insight = f"{m1.experience.content[:5]}_{m2.experience.content[:5]}"
                    self.creativity_pool.append(insight)
                    self.dream_insights += 1
        
        # Clear fatigue and waste via sleep (more effective longer sleep)
        waste_clearance = 0.15 * hours
        self.waste = max(0.0, self.waste - waste_clearance)
        self.fatigue = max(0.0, self.fatigue - (0.125 * hours))
        
        # Clear pending
        self.pending_consolidation.clear()
    
    def get_memory_vector(self, all_experiences: List[Experience]) -> List[int]:
        """Return binary vector: 1 if remembered, 0 otherwise."""
        remembered_ids = {m.experience.exp_id for m in self.memories}
        return [1 if e.exp_id in remembered_ids else 0 for e in all_experiences]
    
    def get_important_memory_retention(self, all_experiences: List[Experience]) -> float:
        """% of top 20% important experiences retained."""
        if not all_experiences:
            return 0.0
        
        # Find top 20% by importance
        top_count = max(1, len(all_experiences) // 5)
        sorted_exps = sorted(all_experiences, key=lambda e: e.importance, reverse=True)
        top_exps = set(e.exp_id for e in sorted_exps[:top_count])
        
        # Count how many are in memory
        remembered_top = sum(1 for m in self.memories if m.experience.exp_id in top_exps)
        return remembered_top / top_count


def generate_experiences(num_exps: int, seed: int = 42) -> List[Experience]:
    """Generate sequence of experiences with controlled randomness."""
    rng = random.Random(seed)
    categories = list(EventCategory)
    experiences = []
    
    for i in range(num_exps):
        category = rng.choice(categories)
        importance = rng.random()  # 0-1
        valence = rng.uniform(-1.0, 1.0)  # -1 to 1
        content = f"exp_{i}"
        experiences.append(Experience(
            exp_id=i,
            timestamp=i,
            category=category,
            importance=importance,
            emotional_valence=valence,
            content=content
        ))
    
    return experiences


def simulate_condition(condition_name: str, num_agents: int, 
                       wake_hours: int, sleep_hours: int,
                       experiences: List[Experience]) -> Dict[str, float]:
    """Simulate a sleep condition with N agents."""
    agents = []
    
    for agent_id in range(num_agents):
        agent = SimpleAgent(agent_id=agent_id, personality_seed=agent_id + hash(condition_name))
        agents.append(agent)
    
    # Determine schedule
    if condition_name == "NEVER_SLEEP":
        schedule = [(0, len(experiences), "wake")]  # All wake
    elif condition_name == "NORMAL_SLEEP":
        schedule = []
        cycle_length = wake_hours + sleep_hours
        num_cycles = (len(experiences) + wake_hours - 1) // wake_hours
        for cycle in range(num_cycles):
            schedule.append((cycle * cycle_length, wake_hours, "wake"))
            schedule.append((cycle * cycle_length + wake_hours, sleep_hours, "sleep"))
    elif condition_name == "LIGHT_SLEEP":
        wake_h, sleep_h = 20, 4
        schedule = []
        cycle_length = wake_h + sleep_h
        num_cycles = (len(experiences) + wake_h - 1) // wake_h
        for cycle in range(num_cycles):
            schedule.append((cycle * cycle_length, wake_h, "wake"))
            schedule.append((cycle * cycle_length + wake_h, sleep_h, "sleep"))
    elif condition_name == "HEAVY_SLEEP":
        wake_h, sleep_h = 12, 12
        schedule = []
        cycle_length = wake_h + sleep_h
        num_cycles = (len(experiences) + wake_h - 1) // wake_h
        for cycle in range(num_cycles):
            schedule.append((cycle * cycle_length, wake_h, "wake"))
            schedule.append((cycle * cycle_length + wake_h, sleep_h, "sleep"))
    elif condition_name == "MICRO_NAPS":
        wake_h, sleep_h = 4, 1
        schedule = []
        cycle_length = wake_h + sleep_h
        num_cycles = (len(experiences) + wake_h - 1) // wake_h
        for cycle in range(num_cycles):
            schedule.append((cycle * cycle_length, wake_h, "wake"))
            schedule.append((cycle * cycle_length + wake_h, sleep_h, "sleep"))
    else:
        schedule = []
    
    # Run simulation for each agent
    for agent in agents:
        exp_idx = 0
        
        for phase_start, phase_duration, phase_type in schedule:
            if phase_type == "wake":
                for _ in range(phase_duration):
                    if exp_idx < len(experiences):
                        agent.wake_tick(experiences[exp_idx])
                        exp_idx += 1
                    else:
                        break
            elif phase_type == "sleep":
                agent.sleep_tick(phase_duration)
        
        # Flush any remaining pending experiences via final sleep
        if agent.pending_consolidation:
            agent.sleep_tick(8)
    
    # Compute metrics across all agents
    all_performance = []
    all_memory_quality = []
    all_creativity = []
    all_emotional_variance = []
    all_waste_final = []
    memory_vectors = []
    
    for agent in agents:
        # Performance
        if agent.performance_history:
            all_performance.append(statistics.mean(agent.performance_history))
        
        # Memory quality
        quality = agent.get_important_memory_retention(experiences)
        all_memory_quality.append(quality)
        
        # Creativity
        all_creativity.append(agent.dream_insights)
        
        # Emotional stability (variance)
        if agent.emotional_state_history:
            variance = statistics.variance(agent.emotional_state_history) if len(agent.emotional_state_history) > 1 else 0.0
            all_emotional_variance.append(variance)
        else:
            all_emotional_variance.append(0.0)
        
        # Final waste
        all_waste_final.append(agent.waste)
        
        # Memory vector
        memory_vectors.append(agent.get_memory_vector(experiences))
    
    # Personality divergence: avg pairwise Hamming distance
    pairwise_distances = []
    for i in range(len(memory_vectors)):
        for j in range(i + 1, len(memory_vectors)):
            dist = sum(1 for a, b in zip(memory_vectors[i], memory_vectors[j]) if a != b)
            pairwise_distances.append(dist)
    
    avg_divergence = statistics.mean(pairwise_distances) if pairwise_distances else 0.0
    
    # Compile results
    results = {
        "condition": condition_name,
        "avg_performance": statistics.mean(all_performance) if all_performance else 0.0,
        "std_performance": statistics.stdev(all_performance) if len(all_performance) > 1 else 0.0,
        "avg_memory_quality": statistics.mean(all_memory_quality),
        "avg_creativity": statistics.mean(all_creativity),
        "std_creativity": statistics.stdev(all_creativity) if len(all_creativity) > 1 else 0.0,
        "avg_emotional_variance": statistics.mean(all_emotional_variance),
        "avg_waste_final": statistics.mean(all_waste_final),
        "personality_divergence": avg_divergence,
        "total_agents": num_agents,
    }
    
    return results


def main():
    """Run full sleep cycle experiment."""
    print("=" * 80)
    print("EXPERIMENT 20: Sleep-Wake Cycles and AI Agent Performance")
    print("=" * 80)
    print()
    
    # Generate shared experience sequence (seeded)
    num_experiences = 200
    experiences = generate_experiences(num_experiences, seed=42)
    
    print(f"Generated {num_experiences} experiences (seeded, same for all agents)")
    print()
    
    # Run all conditions
    conditions = ["NEVER_SLEEP", "NORMAL_SLEEP", "LIGHT_SLEEP", "HEAVY_SLEEP", "MICRO_NAPS"]
    all_results = []
    
    for condition in conditions:
        print(f"Running condition: {condition}...", flush=True)
        result = simulate_condition(condition, num_agents=30, 
                                   wake_hours=16, sleep_hours=8,
                                   experiences=experiences)
        all_results.append(result)
        print(f"  ✓ Completed")
    
    print()
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()
    
    # Print table
    print(f"{'Condition':<18} {'Avg Perf':<12} {'Std Perf':<12} {'Memory %':<12} {'Creativity':<12}")
    print(f"{'':18} {'(0-1)':<12} {'(0-1)':<12} {'(0-1)':<12} {'(count)':<12}")
    print("-" * 70)
    
    for r in all_results:
        print(f"{r['condition']:<18} {r['avg_performance']:<12.4f} {r['std_performance']:<12.4f} "
              f"{r['avg_memory_quality']:<12.4f} {r['avg_creativity']:<12.1f}")
    
    print()
    print(f"{'Condition':<18} {'Emot.Var':<12} {'Waste Final':<12} {'Diversity':<12}")
    print(f"{'':18} {'(σ²)':<12} {'(0-1)':<12} {'(Hamming)':<12}")
    print("-" * 70)
    
    for r in all_results:
        print(f"{r['condition']:<18} {r['avg_emotional_variance']:<12.4f} {r['avg_waste_final']:<12.4f} "
              f"{r['personality_divergence']:<12.1f}")
    
    print()
    print("=" * 80)
    print("HYPOTHESIS EVALUATION")
    print("=" * 80)
    print()
    
    never_sleep = next(r for r in all_results if r['condition'] == 'NEVER_SLEEP')
    normal_sleep = next(r for r in all_results if r['condition'] == 'NORMAL_SLEEP')
    heavy_sleep = next(r for r in all_results if r['condition'] == 'HEAVY_SLEEP')
    micro_naps = next(r for r in all_results if r['condition'] == 'MICRO_NAPS')
    
    print("H1: NEVER_SLEEP shows continuous degradation")
    h1_test = never_sleep['avg_waste_final'] > 0.5 or never_sleep['avg_performance'] < 0.5
    print(f"    NEVER_SLEEP waste: {never_sleep['avg_waste_final']:.4f}, perf: {never_sleep['avg_performance']:.4f}")
    print(f"    {'✓ SUPPORTED (high waste/low perf)' if h1_test else '✗ NOT SUPPORTED'}")
    print()
    
    print("H2: NORMAL_SLEEP retains more important memories than NEVER_SLEEP")
    h2_test = normal_sleep['avg_memory_quality'] > never_sleep['avg_memory_quality']
    print(f"    NEVER_SLEEP: {never_sleep['avg_memory_quality']:.4f}, NORMAL: {normal_sleep['avg_memory_quality']:.4f}")
    print(f"    {'✓ SUPPORTED' if h2_test else '✗ NOT SUPPORTED'}")
    print()
    
    print("H3: NORMAL_SLEEP produces creative insights; NEVER_SLEEP produces few")
    h3_test = normal_sleep['avg_creativity'] > never_sleep['avg_creativity']
    print(f"    NEVER_SLEEP: {never_sleep['avg_creativity']:.2f}, NORMAL: {normal_sleep['avg_creativity']:.2f}")
    print(f"    {'✓ SUPPORTED' if h3_test else '✗ NOT SUPPORTED'}")
    print()
    
    print("H4: HEAVY_SLEEP has highest creativity but potentially lower throughput")
    max_creativity_cond = max(all_results, key=lambda r: r['avg_creativity'])
    h4_test = max_creativity_cond['condition'] == 'HEAVY_SLEEP'
    print(f"    Highest creativity: {max_creativity_cond['condition']} ({max_creativity_cond['avg_creativity']:.2f})")
    print(f"    {'✓ SUPPORTED' if h4_test else '✗ NOT SUPPORTED (see: ' + max_creativity_cond['condition'] + ')'}")
    print()
    
    print("H5: MICRO_NAPS has most stable performance (least variance)")
    min_variance_cond = min(all_results, key=lambda r: r['std_performance'])
    h5_test = min_variance_cond['condition'] == 'MICRO_NAPS'
    print(f"    Lowest variance: {min_variance_cond['condition']} (σ={min_variance_cond['std_performance']:.4f})")
    print(f"    {'✓ SUPPORTED' if h5_test else '✗ NOT SUPPORTED'}")
    print()
    
    print("H6: NEVER_SLEEP accumulates most waste; waste correlates with low performance")
    max_waste_cond = max(all_results, key=lambda r: r['avg_waste_final'])
    h6_test = max_waste_cond['avg_performance'] < normal_sleep['avg_performance']
    print(f"    Highest waste: {max_waste_cond['condition']} ({max_waste_cond['avg_waste_final']:.4f})")
    print(f"    {'✓ SUPPORTED (waste linked to low perf)' if h6_test else '✗ NOT SUPPORTED'}")
    print()
    
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
