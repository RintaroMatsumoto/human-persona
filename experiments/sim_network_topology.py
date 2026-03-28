#!/usr/bin/env python3
"""Experiment: Network Topology & Love Propagation

Hypothesis:
    Love propagates through social networks with different speeds depending on 
    network structure. Small-world networks (short path lengths + clustering) 
    should propagate love fastest because they balance global reachability with 
    local reinforcement.
    
    Expected ranking (fastest to slowest):
    1. Small-world (Watts-Strogatz) - optimal balance
    2. Hub-spoke - fast initial spread via hubs, then slows
    3. Ring lattice - slow but relentless; respects local bonds
    4. Random - chaotic; depends on luck

Tested Topologies:
    - Random: Each round, randomly pair any two agents
    - Ring lattice: Agents in circular order; each pairs with immediate neighbors
    - Small-world: Ring lattice + rewire ~10% of edges randomly (Watts-Strogatz)
    - Hub-spoke: 1 central hub agent, all others connect only through hub

Metrics (per topology, per round):
    - Propagation speed: rounds to 50% love penetration
    - Final penetration: % of agents with active love at round 15
    - Spread pattern: how many "clusters" of love form?
    - Latency variance: how much does path length affect speed?

Design:
    N=20 agents per topology, 15 interaction rounds
    5 repetitions per topology
    Start: 1 agent with initial love (seed)
    Track: love penetration at rounds 3, 6, 9, 12, 15

Usage:
    python experiments/sim_network_topology.py
"""

from __future__ import annotations

import sys
import os
import random
import math
from dataclasses import dataclass
from typing import List, Tuple

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


from experiments.sim_gradient_acceptance import calculate_acceptance
from experiments.sim_society import make_member, social_encounter


# ---------------------------------------------------------------------------
# Network Topology Experiment
# ---------------------------------------------------------------------------

@dataclass
class TopologySnapshot:
    """Love propagation metrics at a point in time."""
    round_num: int
    love_penetration: float
    n_with_love: int
    n_total: int


@dataclass
class TopologyResult:
    """Results from simulating one topology."""
    topology_name: str
    timeline: list[TopologySnapshot]
    final_penetration: float
    rounds_to_50pct: int
    avg_acceptance: float


# Topology generators
def _pairing_random(n: int, rng: random.Random) -> List[Tuple[int, int]]:
    """Generate random pairings."""
    indices = list(range(n))
    rng.shuffle(indices)
    pairs = [(indices[i], indices[i + 1]) for i in range(0, len(indices) - 1, 2)]
    return pairs


def _pairing_ring_lattice(n: int, rng: random.Random) -> List[Tuple[int, int]]:
    """Ring lattice: each agent paired with right neighbor (circular)."""
    pairs = []
    for i in range(n):
        right = (i + 1) % n
        if i < right:  # Avoid duplicate pairs
            pairs.append((i, right))
    return pairs


def _pairing_small_world(n: int, rng: random.Random, rewire_prob: float = 0.1) -> List[Tuple[int, int]]:
    """Watts-Strogatz small-world: ring lattice + random rewiring.
    
    Args:
        n: Number of agents
        rng: Random generator
        rewire_prob: Probability of rewiring each edge (~0.1 is standard)
    """
    # Start with ring lattice
    edges = set()
    for i in range(n):
        right = (i + 1) % n
        if i < right:
            edges.add((i, right))
    
    # Rewire: with probability rewire_prob, replace an edge with a random edge
    edges_list = list(edges)
    n_rewire = max(1, int(len(edges_list) * rewire_prob))
    
    for _ in range(n_rewire):
        if not edges_list:
            break
        old_edge = edges_list.pop(rng.randint(0, len(edges_list) - 1))
        
        # Pick a random new edge (that doesn't exist)
        attempts = 0
        while attempts < 10:
            a = rng.randint(0, n - 1)
            b = rng.randint(0, n - 1)
            if a != b:
                edge = (min(a, b), max(a, b))
                if edge not in edges:
                    edges.add(edge)
                    break
            attempts += 1
    
    return list(edges)


def _pairing_hub_spoke(n: int, rng: random.Random) -> List[Tuple[int, int]]:
    """Hub-spoke: agent 0 is hub, all others connect only through agent 0."""
    pairs = []
    for i in range(1, n):
        pairs.append((0, i))
    return pairs


def simulate_topology(
    topology_name: str,
    n_agents: int,
    seed: int,
    pairing_func,
    rounds: int = 15,
) -> TopologyResult:
    """Simulate love propagation on a given network topology.
    
    Args:
        topology_name: Name of the topology
        n_agents: Number of agents
        seed: Random seed
        pairing_func: Function that returns list of (i, j) pairs for this round
        rounds: Number of interaction rounds
    """
    rng = random.Random(seed)
    
    # Create agents
    agents = [make_member(f"{topology_name}-{i}", seed=seed * 100 + i, 
                         has_initial_love=(i == 0)) for i in range(n_agents)]
    
    timeline = []
    rounds_to_50pct = -1
    
    # Simulate interactions
    for round_num in range(rounds):
        pairs = pairing_func(n_agents, rng)
        
        for i, j in pairs:
            social_encounter(agents[i], agents[j], rng)
        
        # Capture snapshot at key rounds
        if round_num in [2, 5, 8, 11, 14]:  # Rounds 3, 6, 9, 12, 15 (0-indexed)
            scores = [calculate_acceptance(None, agent.incompleteness.love_circle) for agent in agents]
            n_with_love = sum(1 for s in scores if s.love_circle > 0)
            penetration = n_with_love / n_agents
            
            timeline.append(TopologySnapshot(
                round_num=round_num + 1,
                love_penetration=penetration,
                n_with_love=n_with_love,
                n_total=n_agents,
            ))
            
            # Record rounds to 50% penetration
            if rounds_to_50pct == -1 and penetration >= 0.5:
                rounds_to_50pct = round_num + 1
    
    # Final metrics
    final_scores = [calculate_acceptance(None, agent.incompleteness.love_circle) for agent in agents]
    final_love_count = sum(1 for s in final_scores if s.love_circle > 0)
    final_penetration = final_love_count / n_agents
    avg_acceptance = sum(s.total for s in final_scores) / len(final_scores) if final_scores else 0.0
    
    return TopologyResult(
        topology_name=topology_name,
        timeline=timeline,
        final_penetration=final_penetration,
        rounds_to_50pct=rounds_to_50pct if rounds_to_50pct != -1 else rounds,
        avg_acceptance=avg_acceptance,
    )


def run_topology_experiment(n_agents: int = 20, reps: int = 5) -> dict:
    """Run complete network topology experiment.
    
    Returns:
        Dictionary with results for each topology
    """
    topologies = {
        "random": _pairing_random,
        "ring_lattice": _pairing_ring_lattice,
        "small_world": _pairing_small_world,
        "hub_spoke": _pairing_hub_spoke,
    }
    
    results_by_topology = {name: [] for name in topologies.keys()}
    
    for rep in range(reps):
        seed_base = 1000 + rep * 10000
        
        for topo_name, pairing_func in topologies.items():
            result = simulate_topology(
                topology_name=topo_name,
                n_agents=n_agents,
                seed=seed_base + hash(topo_name) % 1000,
                pairing_func=pairing_func,
                rounds=15,
            )
            results_by_topology[topo_name].append(result)
    
    return results_by_topology


def analyze_results(results_by_topology: dict):
    """Analyze and print results with hypothesis verification."""
    print("\n" + "=" * 90)
    print("NETWORK TOPOLOGY & LOVE PROPAGATION RESULTS")
    print("=" * 90)
    
    topologies = ["random", "ring_lattice", "small_world", "hub_spoke"]
    
    for topo_name in topologies:
        results = results_by_topology[topo_name]
        print(f"\nTopology: {topo_name.upper():30}")
        print("-" * 90)
        
        # Aggregate timeline data
        timeline_dict = {}
        for result in results:
            for snapshot in result.timeline:
                if snapshot.round_num not in timeline_dict:
                    timeline_dict[snapshot.round_num] = []
                timeline_dict[snapshot.round_num].append(snapshot)
        
        print(f"{'Round':>8} {'Penetration':>15} {'Avg Agents':>15} {'Avg Acceptance':>18}")
        print("-" * 90)
        for round_num in sorted(timeline_dict.keys()):
            snapshots = timeline_dict[round_num]
            avg_penetration = sum(s.love_penetration for s in snapshots) / len(snapshots)
            avg_agents = sum(s.n_with_love for s in snapshots) / len(snapshots)
            
            avg_acceptance = sum(r.avg_acceptance for r in results) / len(results)
            
            print(f"{round_num:>8.0f} {avg_penetration:>14.1%} {avg_agents:>15.1f} {avg_acceptance:>18.4f}")
        
        # Final metrics aggregates
        final_penetrations = [r.final_penetration for r in results]
        rounds_to_50 = [r.rounds_to_50pct for r in results]
        
        avg_final_pct = sum(final_penetrations) / len(final_penetrations)
        avg_rounds_50 = sum(rounds_to_50) / len(rounds_to_50)
        
        print(f"\nFinal Penetration: {avg_final_pct * 100:.1f}%")
        print(f"Rounds to 50% penetration: {avg_rounds_50:.1f}")
    
    # Hypothesis verification
    print("\n" + "=" * 90)
    print("HYPOTHESIS VERIFICATION: Small-World Networks Propagate Fastest")
    print("=" * 90)
    
    # Extract speed metric (rounds to 50% penetration)
    speed_by_topology = {}
    for topo_name in topologies:
        rounds_to_50 = [r.rounds_to_50pct for r in results_by_topology[topo_name]]
        avg_rounds = sum(rounds_to_50) / len(rounds_to_50)
        speed_by_topology[topo_name] = avg_rounds
    
    # Rank by speed (lower rounds = faster)
    sorted_by_speed = sorted(speed_by_topology.items(), key=lambda x: x[1])
    
    print("\nSpeed Ranking (fastest to slowest, measured by rounds to 50% penetration):")
    print("-" * 90)
    for rank, (topo_name, rounds) in enumerate(sorted_by_speed, 1):
        print(f"{rank}. {topo_name:15} : {rounds:5.1f} rounds to 50% penetration")
    
    # Check hypothesis: small_world should be #1
    fastest_topo = sorted_by_speed[0][0]
    small_world_rank = next(i for i, (t, _) in enumerate(sorted_by_speed, 1) if t == "small_world")
    
    print(f"\nSmall-world network rank: {small_world_rank}/4")
    
    if small_world_rank == 1:
        print("[SUPPORTED] Small-world networks propagate love fastest!")
        print("  Small-world's combination of short path lengths and clustering")
        print("  creates optimal conditions for information (and love) spread.")
    elif small_world_rank == 2:
        print("[PARTIAL] Small-world is 2nd fastest (close call)")
        print(f"  Fastest was {fastest_topo}, but small-world is competitive")
    else:
        print(f"[NOT SUPPORTED] Small-world ranked {small_world_rank}th")
        print(f"  Fastest topology was {fastest_topo}")
        print("  Possible reasons: random variation, small sample size, or incorrect assumption")
    
    # Final penetration comparison
    print("\nFinal Penetration Rates (after 15 rounds):")
    print("-" * 90)
    penet_by_topology = {}
    for topo_name in topologies:
        final_pcts = [r.final_penetration for r in results_by_topology[topo_name]]
        avg_pct = sum(final_pcts) / len(final_pcts)
        penet_by_topology[topo_name] = avg_pct
        print(f"  {topo_name:15} : {avg_pct * 100:6.1f}%")
    
    # Analysis of final state
    best_penet_topo = max(penet_by_topology.items(), key=lambda x: x[1])[0]
    print(f"\nBest final penetration: {best_penet_topo}")
    print("Note: Hub-spoke should eventually reach 100% if hubs are engaged")


def main():
    print("\nNetwork Topology Experiment: How does structure affect love propagation?")
    print("=" * 90)
    
    N = 20       # Agents per topology
    REPS = 5     # Repetitions per topology
    
    results = run_topology_experiment(n_agents=N, reps=REPS)
    analyze_results(results)


if __name__ == "__main__":
    main()
