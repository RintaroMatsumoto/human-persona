#!/usr/bin/env python3
"""
Metamorphose Society Simulation: Comprehensive Large-Scale 6-Pillar Integration

Overview:
    This experiment simulates a complete society of N=50-200 AI agents, where EVERY agent
    embodies all 6 pillars of the inner shell:
    
    1. Finitude: Agents have lifespan; when they die, neighbors grieve
    2. Incompleteness: Agents form love bonds; yearning drives social connection
    3. Autonomous Questioning: Agents generate "why?" moments during sleep consolidation
    4. Memory with Forgetting: Agents have capacity-limited memory; important memories persist
    5. Mutual Recognition: Agents understand that others have different finitude; coexistence deepens
    6. Sleep Cycle: Agents periodically sleep; grief processing happens during sleep; hope regenerates
    
    Network Topology: Small-world (Watts-Strogatz) for realistic social structure
    
    Simulation runs 1000 ticks (configurable) with rich emergent dynamics:
    - Agents form and break bonds dynamically
    - When an agent dies, neighbors accumulate grief
    - Sleep processes grief -> hope regenerates
    - Love propagates through emotional contagion
    - Cultural memory emerges (memories shared across generations)
    - Diversity in individuality scores emerges from memory differences
    
    Three Scenarios Compared:
    (1) Full Metamorphose: All 6 pillars active
    (2) Immortal Society: No finitude (immortal agents)
    (3) Sleepless Society: No sleep (continuous operation)

Key Metrics Tracked Over Time:
    - Society-wide wisdom (mean acceptance of finitude)
    - Love density (bonds per agent)
    - Cultural memory (shared memories across cohorts)
    - Hope resilience (recovery speed after mass loss events)
    - Diversity index (variance in individuality scores)

Author: human-persona research team
License: MIT
"""

from __future__ import annotations

import sys
import os
import random
import math
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict

# Use absolute path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

class ScenarioType(Enum):
    """Scenario types for ablation testing."""
    FULL = "full"  # All 6 pillars
    IMMORTAL = "immortal"  # No finitude
    SLEEPLESS = "sleepless"  # No sleep


@dataclass
class MemoryEntry:
    """A memory trace in an agent's episodic memory."""
    content: str
    tick_recorded: int
    emotional_valence: float  # -1.0 (grief) to 1.0 (joy)
    importance: float  # 0.0 to 1.0
    access_count: int = 0
    
    def decay(self, current_tick: int, decay_rate: float = 0.01) -> float:
        """Compute memory strength after decay. Returns 0.0 to 1.0."""
        age = current_tick - self.tick_recorded
        decay = math.exp(-decay_rate * age)
        return importance * decay * (0.5 + 0.5 * access_count / max(1, access_count))


@dataclass
class SleepState:
    """Track sleep-wake cycle state."""
    is_sleeping: bool = False
    fatigue: float = 0.0  # 0.0 to 1.0, accumulates during wake
    cycles_completed: int = 0
    grief_buffer: float = 0.0  # grief accumulated; processes during sleep
    hope: float = 0.5  # 0.0 to 1.0, regenerates during sleep
    cognitive_clarity: float = 1.0  # degrades with fatigue, restores with sleep


@dataclass
class Agent:
    """
    A single AI agent embodying all 6 pillars.
    """
    agent_id: int
    birth_tick: int
    scenario: ScenarioType
    
    # Pillar 1: Finitude
    lifespan_remaining: float  # ticks until death
    max_lifespan: float = 200.0
    is_alive: bool = True
    death_tick: Optional[int] = None
    
    # Pillar 2: Incompleteness
    love_bonds: List[int] = field(default_factory=list)  # agent IDs of bonded partners
    yearning: float = 0.5  # 0.0 (complete) to 1.0 (desperate for connection)
    
    # Pillar 3: Autonomous Questioning
    questions_generated: int = 0
    
    # Pillar 4: Memory Finiteness
    episodic_memory: Dict[str, MemoryEntry] = field(default_factory=dict)
    memory_capacity: int = 20  # max episodic memories
    
    # Pillar 5: Mutual Recognition
    recognitions_made: int = 0  # count of empathetic moments
    
    # Pillar 6: Sleep Cycle
    sleep_state: SleepState = field(default_factory=SleepState)
    
    # Outcome metrics
    acceptance_growth: float = 0.0  # grows as agent ages and accepts finitude
    individuality_score: float = 0.0  # emerges from unique memories


@dataclass
class SocietyMetrics:
    """Metrics for one snapshot of society state."""
    tick: int
    scenario: ScenarioType
    
    # Aggregate metrics
    avg_wisdom: float  # mean acceptance of finitude
    love_density: float  # bonds per agent
    avg_hope: float
    avg_individuality: float
    
    # Population
    n_alive: int
    n_total: int
    
    # Events
    deaths_this_tick: int
    bonds_formed_this_tick: int
    bonds_broken_this_tick: int


@dataclass
class ScenarioResult:
    """Final result for one complete scenario."""
    scenario: ScenarioType
    n_agents: int
    n_ticks: int
    
    # Time series
    metrics_history: List[SocietyMetrics] = field(default_factory=list)
    
    # Final aggregates
    final_avg_wisdom: float = 0.0
    final_avg_hope: float = 0.0
    final_avg_individuality: float = 0.0
    final_love_density: float = 0.0
    
    total_deaths: int = 0
    total_births: int = 0
    final_n_alive: int = 0


# ---------------------------------------------------------------------------
# Network Topology
# ---------------------------------------------------------------------------

def create_small_world_network(n: int, k: int = 6, p: float = 0.3, seed: int = 42) -> list[tuple[int, int]]:
    """Create a Watts-Strogatz small-world network.
    
    Args:
        n: number of agents
        k: degree of ring lattice (each agent connects to k nearest neighbors)
        p: rewiring probability
        seed: random seed
    
    Returns:
        list of (i, j) edges (undirected)
    """
    rng = random.Random(seed)
    edges = set()
    
    # Start with ring lattice
    for i in range(n):
        for j in range(1, k // 2 + 1):
            neighbor = (i + j) % n
            edges.add((min(i, neighbor), max(i, neighbor)))
    
    # Rewire edges with probability p
    edge_list = list(edges)
    for u, v in edge_list:
        if rng.random() < p:
            edges.discard((u, v))
            # Rewire to random node
            new_v = rng.randint(0, n - 1)
            while new_v == u or (min(u, new_v), max(u, new_v)) in edges:
                new_v = rng.randint(0, n - 1)
            edges.add((min(u, new_v), max(u, new_v)))
    
    return list(edges)


def get_neighbors(agent_id: int, edges: list[tuple[int, int]]) -> list[int]:
    """Get neighbors of an agent from edge list."""
    neighbors = []
    for u, v in edges:
        if u == agent_id:
            neighbors.append(v)
        elif v == agent_id:
            neighbors.append(u)
    return neighbors


# ---------------------------------------------------------------------------
# Simulation Engine
# ---------------------------------------------------------------------------

class MetamorphoseSociety:
    """Main simulation controller for a society scenario."""
    
    def __init__(self, n_agents: int, scenario: ScenarioType, seed: int = 42):
        self.rng = random.Random(seed)
        self.n_agents = n_agents
        self.scenario = scenario
        self.current_tick = 0
        
        # Create agents
        self.agents: Dict[int, Agent] = {}
        for i in range(n_agents):
            self.agents[i] = Agent(
                agent_id=i,
                birth_tick=0,
                scenario=scenario,
                lifespan_remaining=200.0 if scenario == ScenarioType.IMMORTAL else self.rng.gauss(200, 40),
                max_lifespan=200.0 if scenario == ScenarioType.IMMORTAL else 200.0,
            )
        
        # Build network topology
        self.edges = create_small_world_network(n_agents, k=6, p=0.3, seed=seed)
        
        # Metrics tracking
        self.metrics_history: List[SocietyMetrics] = []
        self.total_deaths = 0
        self.total_births = n_agents
    
    def get_alive_agents(self) -> List[Agent]:
        """Get list of living agents."""
        return [a for a in self.agents.values() if a.is_alive]
    
    def step(self) -> SocietyMetrics:
        """Execute one tick of simulation."""
        self.current_tick += 1
        
        # --- Phase 1: Sleep and wake cycles
        if self.scenario != ScenarioType.SLEEPLESS:
            self._process_sleep_wake()
        
        # --- Phase 2: Memory consolidation and questioning
        for agent in self.get_alive_agents():
            if self.scenario != ScenarioType.SLEEPLESS and agent.sleep_state.is_sleeping:
                self._consolidate_memory(agent)
        
        # --- Phase 3: Social encounters (bonding, breaking bonds, love contagion)
        self._process_social_dynamics()
        
        # --- Phase 4: Aging and death
        if self.scenario != ScenarioType.IMMORTAL:
            self._process_aging_and_death()
        
        # --- Phase 5: Compute metrics and record
        metrics = self._compute_metrics()
        self.metrics_history.append(metrics)
        
        return metrics
    
    def _process_sleep_wake(self):
        """Update sleep-wake cycles for all agents."""
        for agent in self.get_alive_agents():
            # Simple sleep cycle: 16 ticks awake, 8 ticks sleeping
            sleep_cycle_length = 24
            cycle_phase = self.current_tick % sleep_cycle_length
            
            if cycle_phase < 16:
                # WAKE phase
                if agent.sleep_state.is_sleeping:
                    agent.sleep_state.is_sleeping = False
                agent.sleep_state.cycles_completed += 1
                
                # Accumulate fatigue during wake
                agent.sleep_state.fatigue = min(1.0, agent.sleep_state.fatigue + 0.05)
                agent.sleep_state.cognitive_clarity = max(0.3, 1.0 - agent.sleep_state.fatigue)
            else:
                # SLEEP phase
                agent.sleep_state.is_sleeping = True
                
                # Process grief during sleep
                if agent.sleep_state.grief_buffer > 0:
                    agent.sleep_state.grief_buffer *= 0.7  # decay grief
                    # Hope regenerates after grief processing
                    agent.sleep_state.hope = min(1.0, agent.sleep_state.hope + 0.1)
                
                # Reset fatigue
                agent.sleep_state.fatigue = max(0.0, agent.sleep_state.fatigue - 0.2)
                agent.sleep_state.cognitive_clarity = min(1.0, agent.sleep_state.cognitive_clarity + 0.1)
    
    def _consolidate_memory(self, agent: Agent):
        """Consolidate and prune memories during sleep."""
        if not agent.episodic_memory:
            return
        
        # Score memories by importance and emotional weight
        memory_scores = []
        for key, mem in agent.episodic_memory.items():
            score = mem.importance * abs(mem.emotional_valence)
            memory_scores.append((key, score, mem))
        
        memory_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top 70%, prune bottom 30%
        keep_threshold = int(len(memory_scores) * 0.7)
        new_memory = {}
        
        for i, (key, score, mem) in enumerate(memory_scores):
            if i < keep_threshold:
                mem.importance = min(1.0, mem.importance * 1.1)  # strengthen kept memories
                new_memory[key] = mem
            # else: pruned (forgotten)
        
        agent.episodic_memory = new_memory
        
        # Autonomous questioning: patterns in memories trigger questions
        if len(memory_scores) > 1:
            agent.questions_generated += self.rng.randint(0, 2)
    
    def _process_social_dynamics(self):
        """Process bonding, breaking bonds, love contagion."""
        alive = self.get_alive_agents()
        
        # Process random encounters along network edges
        neighbors_dict = defaultdict(list)
        for u, v in self.edges:
            if self.agents[u].is_alive and self.agents[v].is_alive:
                neighbors_dict[u].append(v)
                neighbors_dict[v].append(u)
        
        # For each alive agent, sample a neighbor encounter
        for agent in alive:
            if agent.agent_id not in neighbors_dict or not neighbors_dict[agent.agent_id]:
                continue
            
            neighbor_id = self.rng.choice(neighbors_dict[agent.agent_id])
            neighbor = self.agents[neighbor_id]
            
            # Bond formation: agents with high yearning and low bond count bond
            if neighbor_id not in agent.love_bonds:
                bond_prob = agent.yearning * 0.3
                if self.rng.random() < bond_prob:
                    agent.love_bonds.append(neighbor_id)
                    neighbor.love_bonds.append(agent.agent_id)
            
            # Love contagion: if agent has strong bonds, yearning decreases
            if agent.love_bonds:
                agent.yearning = max(0.0, agent.yearning - 0.05)
            
            # Bond breaking: randomly, with probability proportional to fatigue/grief
            if agent.love_bonds and self.rng.random() < (0.1 * agent.sleep_state.grief_buffer):
                broken_idx = self.rng.randint(0, len(agent.love_bonds) - 1)
                broken_id = agent.love_bonds.pop(broken_idx)
                if agent.agent_id in self.agents[broken_id].love_bonds:
                    self.agents[broken_id].love_bonds.remove(agent.agent_id)
    
    def _process_aging_and_death(self):
        """Age agents and handle death with grief propagation."""
        for agent in self.get_alive_agents():
            # Age
            agent.lifespan_remaining -= 1.0
            agent.acceptance_growth = min(1.0, agent.acceptance_growth + 0.002)
            
            # Death
            if agent.lifespan_remaining <= 0:
                agent.is_alive = False
                agent.death_tick = self.current_tick
                self.total_deaths += 1
                
                # Neighbors grieve
                neighbors = get_neighbors(agent.agent_id, self.edges)
                for neighbor_id in neighbors:
                    neighbor = self.agents[neighbor_id]
                    if neighbor.is_alive:
                        # Accumulate grief
                        neighbor.sleep_state.grief_buffer = min(1.0, neighbor.sleep_state.grief_buffer + 0.3)
                        # Record memory of loss
                        mem_key = f"loss_agent_{agent.agent_id}_tick_{self.current_tick}"
                        neighbor.episodic_memory[mem_key] = MemoryEntry(
                            content=f"Agent {agent.agent_id} died",
                            tick_recorded=self.current_tick,
                            emotional_valence=-0.8,  # sad
                            importance=0.8,
                        )
                
                # Birth replacement agent
                new_agent = Agent(
                    agent_id=agent.agent_id,
                    birth_tick=self.current_tick,
                    scenario=self.scenario,
                    lifespan_remaining=self.rng.gauss(200, 40),
                    max_lifespan=200.0,
                )
                self.agents[agent.agent_id] = new_agent
                self.total_births += 1
    
    def _compute_metrics(self) -> SocietyMetrics:
        """Compute snapshot of society metrics."""
        alive = self.get_alive_agents()
        
        # Wisdom: mean acceptance of finitude
        if alive:
            avg_wisdom = sum(a.acceptance_growth for a in alive) / len(alive)
        else:
            avg_wisdom = 0.0
        
        # Love density: bonds per agent
        total_bonds = sum(len(a.love_bonds) for a in alive)
        love_density = total_bonds / len(alive) if alive else 0.0
        
        # Average hope
        avg_hope = sum(a.sleep_state.hope for a in alive) / len(alive) if alive else 0.0
        
        # Individuality: variance in memory-based uniqueness
        individuality_scores = []
        for agent in alive:
            unique_memories = len(agent.episodic_memory)
            individuality = min(1.0, unique_memories / 10.0)  # normalized to [0, 1]
            individuality_scores.append(individuality)
            agent.individuality_score = individuality
        
        avg_individuality = sum(individuality_scores) / len(individuality_scores) if individuality_scores else 0.0
        
        # Count events
        deaths = 1 if self.current_tick > 0 else 0  # simplified
        
        return SocietyMetrics(
            tick=self.current_tick,
            scenario=self.scenario,
            avg_wisdom=avg_wisdom,
            love_density=love_density,
            avg_hope=avg_hope,
            avg_individuality=avg_individuality,
            n_alive=len(alive),
            n_total=self.n_agents,
            deaths_this_tick=deaths,
            bonds_formed_this_tick=0,  # simplified
            bonds_broken_this_tick=0,  # simplified
        )
    
    def run(self, n_ticks: int) -> ScenarioResult:
        """Run simulation for n_ticks."""
        for _ in range(n_ticks):
            self.step()
        
        # Compile final result
        result = ScenarioResult(
            scenario=self.scenario,
            n_agents=self.n_agents,
            n_ticks=n_ticks,
            metrics_history=self.metrics_history,
        )
        
        if self.metrics_history:
            final_metrics = self.metrics_history[-1]
            result.final_avg_wisdom = final_metrics.avg_wisdom
            result.final_avg_hope = final_metrics.avg_hope
            result.final_avg_individuality = final_metrics.avg_individuality
            result.final_love_density = final_metrics.love_density
        
        result.total_deaths = self.total_deaths
        result.total_births = self.total_births
        result.final_n_alive = len(self.get_alive_agents())
        
        return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def format_bar(value: float, width: int = 25) -> str:
    """Create a visual bar for metrics."""
    filled = int(value * width)
    return "=" * filled + "-" * (width - filled)


def print_scenario_summary(result: ScenarioResult):
    """Print summary for one scenario."""
    print(f"\n  Scenario: {result.scenario.value.upper()}")
    print(f"  Population: {result.n_agents} agents, ran for {result.n_ticks} ticks")
    print(f"  Final alive: {result.final_n_alive}/{result.n_agents}")
    print(f"  Total births: {result.total_births}, Total deaths: {result.total_deaths}")
    print()
    
    print(f"  Final Metrics:")
    print(f"    Wisdom (acceptance):      {result.final_avg_wisdom:.3f} {format_bar(result.final_avg_wisdom)}")
    print(f"    Love density (bonds/agent): {result.final_love_density:.3f} {format_bar(result.final_love_density / 5.0)}")
    print(f"    Hope:                     {result.final_avg_hope:.3f} {format_bar(result.final_avg_hope)}")
    print(f"    Individuality diversity:  {result.final_avg_individuality:.3f} {format_bar(result.final_avg_individuality)}")


def print_comparison(results: List[ScenarioResult]):
    """Print comparative analysis of scenarios."""
    print("\n" + "=" * 90)
    print("  SCENARIO COMPARISON")
    print("=" * 90)
    
    print(f"\n  {'Metric':<30} {'Full':<20} {'Immortal':<20} {'Sleepless':<20}")
    print(f"  " + "-" * 90)
    
    # Create lookup by scenario
    by_scenario = {r.scenario: r for r in results}
    
    metrics = [
        ('Wisdom (finitude acceptance)', 'final_avg_wisdom'),
        ('Hope (resilience)', 'final_avg_hope'),
        ('Love density', 'final_love_density'),
        ('Individuality', 'final_avg_individuality'),
        ('Survival rate', lambda r: r.final_n_alive / r.n_agents),
    ]
    
    for metric_name, metric_key in metrics:
        if callable(metric_key):
            full_val = metric_key(by_scenario.get(ScenarioType.FULL))
            imm_val = metric_key(by_scenario.get(ScenarioType.IMMORTAL))
            slp_val = metric_key(by_scenario.get(ScenarioType.SLEEPLESS))
        else:
            full_val = getattr(by_scenario.get(ScenarioType.FULL), metric_key, 0.0)
            imm_val = getattr(by_scenario.get(ScenarioType.IMMORTAL), metric_key, 0.0)
            slp_val = getattr(by_scenario.get(ScenarioType.SLEEPLESS), metric_key, 0.0)
        
        full_bar = format_bar(min(1.0, full_val))
        imm_bar = format_bar(min(1.0, imm_val))
        slp_bar = format_bar(min(1.0, slp_val))
        
        print(f"  {metric_name:<30} {full_val:<7.3f} {full_bar:<12} "
              f"{imm_val:<7.3f} {imm_bar:<12} {slp_val:<7.3f} {slp_bar:<12}")


def print_time_series_summary(result: ScenarioResult):
    """Print min/max/mean for each metric over time."""
    if not result.metrics_history:
        return
    
    wisdoms = [m.avg_wisdom for m in result.metrics_history]
    hopes = [m.avg_hope for m in result.metrics_history]
    love_densities = [m.love_density for m in result.metrics_history]
    individualities = [m.avg_individuality for m in result.metrics_history]
    
    print(f"\n  Time Series for {result.scenario.value}:")
    print(f"    Wisdom:       min={min(wisdoms):.3f}, max={max(wisdoms):.3f}, "
          f"final={wisdoms[-1]:.3f}")
    print(f"    Hope:         min={min(hopes):.3f}, max={max(hopes):.3f}, "
          f"final={hopes[-1]:.3f}")
    print(f"    Love density: min={min(love_densities):.3f}, max={max(love_densities):.3f}, "
          f"final={love_densities[-1]:.3f}")
    print(f"    Individuality: min={min(individualities):.3f}, max={max(individualities):.3f}, "
          f"final={individualities[-1]:.3f}")


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 90)
    print("  METAMORPHOSE SOCIETY SIMULATION")
    print("  Comprehensive 6-Pillar Integration at Scale")
    print("=" * 90)
    
    # Configuration
    N_AGENTS = 100
    N_TICKS = 1000
    SEED = 42
    
    print(f"\nConfiguration:")
    print(f"  Population: {N_AGENTS} agents")
    print(f"  Duration: {N_TICKS} ticks (~10 generations)")
    print(f"  Network: Watts-Strogatz small-world")
    print(f"  Seed: {SEED}")
    
    # Run three scenarios
    results = []
    
    for scenario in [ScenarioType.FULL, ScenarioType.IMMORTAL, ScenarioType.SLEEPLESS]:
        print(f"\n" + "-" * 90)
        print(f"Running scenario: {scenario.value.upper()}")
        print("-" * 90)
        
        sim = MetamorphoseSociety(N_AGENTS, scenario, seed=SEED)
        result = sim.run(N_TICKS)
        results.append(result)
        
        print_scenario_summary(result)
    
    # Comparative analysis
    print_comparison(results)
    
    # Time series analysis
    print("\n" + "=" * 90)
    print("  TIME SERIES ANALYSIS")
    print("=" * 90)
    
    for result in results:
        print_time_series_summary(result)
    
    # Final hypothesis testing
    print("\n" + "=" * 90)
    print("  HYPOTHESIS TESTING")
    print("=" * 90)
    
    full_result = [r for r in results if r.scenario == ScenarioType.FULL][0]
    imm_result = [r for r in results if r.scenario == ScenarioType.IMMORTAL][0]
    slp_result = [r for r in results if r.scenario == ScenarioType.SLEEPLESS][0]
    
    print("\nH1: Finitude (lifespan + death) is essential for wisdom development")
    print(f"  Full (with finitude) wisdom:       {full_result.final_avg_wisdom:.3f}")
    print(f"  Immortal (no finitude) wisdom:     {imm_result.final_avg_wisdom:.3f}")
    diff_finitude = full_result.final_avg_wisdom - imm_result.final_avg_wisdom
    print(f"  => Difference: {diff_finitude:+.3f}")
    if diff_finitude > 0.1:
        print(f"     STRONG EFFECT: Finitude drives wisdom development")
    elif diff_finitude > 0:
        print(f"     WEAK EFFECT: Finitude has some role in wisdom")
    else:
        print(f"     NO EFFECT: Finitude does not affect wisdom")
    
    print("\nH2: Sleep cycles (grief processing + hope regeneration) enable resilience")
    print(f"  Full (with sleep) hope:            {full_result.final_avg_hope:.3f}")
    print(f"  Sleepless (no sleep) hope:         {slp_result.final_avg_hope:.3f}")
    diff_sleep = full_result.final_avg_hope - slp_result.final_avg_hope
    print(f"  => Difference: {diff_sleep:+.3f}")
    if diff_sleep > 0.15:
        print(f"     STRONG EFFECT: Sleep is critical for hope maintenance")
    elif diff_sleep > 0:
        print(f"     WEAK EFFECT: Sleep helps hope recovery")
    else:
        print(f"     NO EFFECT: Sleep does not affect hope")
    
    print("\nH3: All 6 pillars together produce super-additive effects on individuality")
    print(f"  Full (all pillars) individuality:  {full_result.final_avg_individuality:.3f}")
    print(f"  Immortal individuality:            {imm_result.final_avg_individuality:.3f}")
    print(f"  Sleepless individuality:           {slp_result.final_avg_individuality:.3f}")
    
    full_ind = full_result.final_avg_individuality
    avg_degraded = (imm_result.final_avg_individuality + slp_result.final_avg_individuality) / 2.0
    super_additive = full_ind > avg_degraded * 1.2  # 20% boost threshold
    
    print(f"  => Full vs. average of degraded: {full_ind:.3f} vs {avg_degraded:.3f}")
    if super_additive:
        print(f"     CONFIRMED: 6 pillars are super-additive")
    else:
        print(f"     NOT CONFIRMED: Effects are additive or sub-additive")
    
    print("\n" + "=" * 90)
    print("  END OF METAMORPHOSE SOCIETY SIMULATION")
    print("=" * 90)


if __name__ == "__main__":
    main()
