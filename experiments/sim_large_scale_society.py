#!/usr/bin/env python3
"""Experiment: Large-scale social simulation with 100+ AI agents.

Overview:
    This experiment scales up the society simulation from N=10 to N=100, N=200, N=500.
    We investigate:
    1. Does the critical anti-love threshold change with population size?
    2. Do clusters of love emerge in different network topologies?
    3. How does network structure (random vs small-world) affect love penetration?
    4. What is the convergence time and final distribution of love?

Methods:
    - Agent creation: same make_member(), make_antilove_member() as smaller experiments
    - Network topology: small-world (Watts-Strogatz) + random baseline
    - Metrics: love penetration, cluster sizes, average acceptance, rounds to convergence
    - Anti-love density: 0%, 10%, 20%, 30%, 40%, 50%
    - Multiple population sizes: N=100 (primary), N=200, N=500 (optional)
    - Multiple replicates: 3 reps per condition (faster than N=10 experiments)

Hypotheses:
    H1: Critical threshold remains around 30-40% anti-love regardless of N
    H2: Small-world topology shows larger clusters than random topology
    H3: Larger populations show slower convergence time
    H4: Love penetration rate decreases with anti-love density more sharply in small populations

Usage:
    python experiments/sim_large_scale_society.py
"""

from __future__ import annotations

import os
import random
import math
from dataclasses import dataclass
from collections import defaultdict


from experiments.sim_gradient_acceptance import calculate_acceptance
from experiments.sim_society import make_member
from experiments.sim_antilove import (
    make_antilove_member,
    is_antilove,
    antilove_encounter,
)


# ---------------------------------------------------------------------------
# Network topology utilities
# ---------------------------------------------------------------------------

def create_small_world_edges(n: int, k: int, p: float, rng: random.Random) -> list[tuple[int, int]]:
    """Generate small-world (Watts-Strogatz) network edges.
    
    Args:
        n: number of nodes
        k: each node connects to k nearest neighbors (ring topology)
        p: rewiring probability
        rng: random number generator
    
    Returns:
        list of (i, j) edges (undirected)
    """
    edges = set()
    
    # Ring lattice: each node connects to k nearest neighbors
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
            if new_v != u:
                edges.add((min(u, new_v), max(u, new_v)))
    
    return list(edges)

def create_random_edges(n: int, avg_degree: int, rng: random.Random) -> list[tuple[int, int]]:
    """Generate random (Erdos-Renyi) network edges.
    
    Args:
        n: number of nodes
        avg_degree: target average degree
        rng: random number generator
    
    Returns:
        list of (i, j) edges (undirected)
    """
    edges = set()
    p = avg_degree / (n - 1)  # connection probability
    
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                edges.add((i, j))
    
    return list(edges)

def find_clusters_bfs(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    """Find connected components (clusters) in the network using BFS.
    
    Args:
        n: number of nodes
        edges: list of (i, j) edges
    
    Returns:
        list of clusters (each cluster is a list of node indices)
    """
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    
    visited = set()
    clusters = []
    
    for start in range(n):
        if start in visited:
            continue
        
        cluster = []
        queue = [start]
        visited.add(start)
        
        while queue:
            node = queue.pop(0)
            cluster.append(node)
            
            for neighbor in adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        clusters.append(cluster)
    
    return clusters

def get_pairing_from_edges(n: int, edges: list[tuple[int, int]], rng: random.Random) -> list[tuple[int, int]]:
    """Convert edge list to random pairings for rounds.
    
    In each round, select a random subset of edges and pair them (each node at most once).
    
    Args:
        n: number of nodes
        edges: list of possible edges
        rng: random number generator
    
    Returns:
        list of (i, j) pairs for this round
    """
    if not edges:
        # If no network edges, fall back to random pairing
        indices = list(range(n))
        rng.shuffle(indices)
        return [(indices[i], indices[i + 1]) for i in range(0, len(indices) - 1, 2)]
    
    # Select edges (with replacement but limited)
    selected = []
    used_nodes = set()
    
    edges_shuffled = list(edges)
    rng.shuffle(edges_shuffled)
    
    for u, v in edges_shuffled:
        if u not in used_nodes and v not in used_nodes:
            selected.append((u, v))
            used_nodes.add(u)
            used_nodes.add(v)
    
    # Add random pairings for unused nodes
    unused = [i for i in range(n) if i not in used_nodes]
    rng.shuffle(unused)
    for i in range(0, len(unused) - 1, 2):
        selected.append((unused[i], unused[i + 1]))
    
    return selected


# ---------------------------------------------------------------------------
# Experiment data structures
# ---------------------------------------------------------------------------

@dataclass
class LargeScaleResult:
    """Result of one large-scale trial."""
    n_total: int
    antilove_ratio: float
    n_antilove: int
    topology: str  # "random" or "small_world"
    final_avg_acceptance: float
    final_love_count: int
    love_penetration: float
    avg_cluster_size: float
    max_cluster_size: int
    n_clusters: int
    rounds_to_convergence: int
    avg_acceptance_per_round: list[float]  # for convergence tracking


# ---------------------------------------------------------------------------
# Main simulation loop
# ---------------------------------------------------------------------------

def run_large_scale_trial(
    n_total: int,
    n_antilove: int,
    topology: str,
    rounds: int,
    seed: int,
) -> LargeScaleResult:
    """Run one large-scale simulation trial.
    
    Args:
        n_total: total population size
        n_antilove: number of anti-love agents
        topology: "random" or "small_world"
        rounds: number of simulation rounds
        seed: random seed
    
    Returns:
        LargeScaleResult with metrics
    """
    rng = random.Random(seed)
    
    # Create members
    members: list = []
    
    # Anti-love agents
    for i in range(n_antilove):
        members.append(make_antilove_member(f"Anti{i}", seed=seed * 100 + i))
    
    # Normal agents
    n_normal = n_total - n_antilove
    for i in range(n_normal):
        members.append(make_member(f"N{i}", seed=seed * 100 + 50 + i))
    
    # Build network
    if topology == "small_world":
        k = max(4, min(20, n_total // 10))  # degree parameter based on population
        p = 0.3  # rewiring probability
        edges = create_small_world_edges(n_total, k, p, rng)
    elif topology == "random":
        avg_degree = max(4, min(20, n_total // 10))
        edges = create_random_edges(n_total, avg_degree, rng)
    else:
        edges = []
    
    # Simulation loop
    convergence_threshold = 0.02  # if avg_acceptance changes < 2%, consider converged
    convergence_check_window = 3  # check over 3 rounds
    acceptance_history = []
    rounds_to_convergence = rounds  # default: didn't converge
    
    for round_num in range(rounds):
        # Get pairings based on network
        pairs = get_pairing_from_edges(n_total, edges, rng)
        
        # Encounters
        for i, j in pairs:
            antilove_encounter(members[i], members[j], rng)
        
        # Track acceptance
        scores = [calculate_acceptance(None, m.incompleteness.love_circle) for m in members]
        avg_acc = sum(s.total for s in scores) / len(scores)
        acceptance_history.append(avg_acc)
        
        # Check for convergence
        if len(acceptance_history) >= convergence_check_window:
            recent = acceptance_history[-convergence_check_window:]
            avg_recent = sum(recent) / len(recent)
            max_var = max(abs(recent[i] - avg_recent) for i in range(len(recent)))
            if max_var < convergence_threshold and round_num > rounds // 2:
                rounds_to_convergence = round_num
                break
    
    # Final metrics
    scores = [calculate_acceptance(None, m.incompleteness.love_circle) for m in members]
    non_anti = [(m, s) for m, s in zip(members, scores) if not is_antilove(m)]
    
    love_count = sum(1 for _, s in non_anti if s.love_circle > 0)
    total_non_anti = len(non_anti)
    avg_acceptance = sum(s.total for s in scores) / len(scores)
    penetration = love_count / total_non_anti if total_non_anti > 0 else 0.0
    
    # Cluster analysis (on the network)
    clusters = find_clusters_bfs(n_total, edges)
    cluster_sizes = [len(c) for c in clusters]
    avg_cluster = sum(cluster_sizes) / len(cluster_sizes) if cluster_sizes else 0.0
    max_cluster = max(cluster_sizes) if cluster_sizes else 0
    
    return LargeScaleResult(
        n_total=n_total,
        antilove_ratio=n_antilove / n_total,
        n_antilove=n_antilove,
        topology=topology,
        final_avg_acceptance=avg_acceptance,
        final_love_count=love_count,
        love_penetration=penetration,
        avg_cluster_size=avg_cluster,
        max_cluster_size=max_cluster,
        n_clusters=len(clusters),
        rounds_to_convergence=rounds_to_convergence,
        avg_acceptance_per_round=acceptance_history,
    )


# ---------------------------------------------------------------------------
# Analysis and visualization
# ---------------------------------------------------------------------------

def make_bar(value: float, width: int = 25) -> str:
    """Create a simple bar for visualization."""
    filled = int(value * width)
    return "=" * filled + "-" * (width - filled)

def print_result(result: LargeScaleResult):
    """Print a single result line."""
    pct = int(result.antilove_ratio * 100)
    bar = make_bar(result.love_penetration, 20)
    print(f"  Anti {pct:2d}% [{bar:20s}] penetration={result.love_penetration:.2f} "
          f"clusters={result.n_clusters} max_sz={result.max_cluster_size} "
          f"conv={result.rounds_to_convergence}")


def main():
    print("=" * 90)
    print("  LARGE-SCALE SOCIAL SIMULATION: 100+ AI AGENTS")
    print("  Testing critical thresholds and network effects")
    print("=" * 90)
    
    # Primary experiment: N=100, varying anti-love density
    print("\n[PART 1] Population N=100, varying anti-love density")
    print("-" * 90)
    
    N = 100
    ROUNDS = 40  # more rounds for larger population
    REPS = 3     # 3 replicates (faster)
    TOPOLOGIES = ["random", "small_world"]
    ANTILOVE_RATIOS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    
    results_part1: dict[str, list] = {topo: [] for topo in TOPOLOGIES}
    
    for topology in TOPOLOGIES:
        print(f"\nTopology: {topology}")
        print(f"  N={N}, rounds={ROUNDS}, replicates={REPS}")
        print(f"  {'Anti%':<6} {'Penetration':<30} {'Clusters':<15} {'Convergence':<12}")
        print(f"  " + "-" * 80)
        
        for ratio in ANTILOVE_RATIOS:
            n_anti = int(ratio * N)
            reps = []
            
            for rep in range(REPS):
                result = run_large_scale_trial(
                    n_total=N,
                    n_antilove=n_anti,
                    topology=topology,
                    rounds=ROUNDS,
                    seed=1000 + int(ratio * 100) * 100 + rep,
                )
                reps.append(result)
            
            # Aggregate
            avg_penetration = sum(r.love_penetration for r in reps) / len(reps)
            avg_clusters = sum(r.n_clusters for r in reps) / len(reps)
            avg_conv = sum(r.rounds_to_convergence for r in reps) / len(reps)
            
            results_part1[topology].append((ratio, reps))
            
            bar = make_bar(avg_penetration, 20)
            pct = int(ratio * 100)
            print(f"  {pct:<6d} [{bar:20s}] {avg_penetration:.2f}   "
                  f"clusters={avg_clusters:.1f}          conv={avg_conv:.0f}")
    
    # Comparative analysis: random vs small_world
    print("\n[PART 2] Topology Comparison (random vs small_world)")
    print("-" * 90)
    print(f"  {'Anti%':<6} {'Random Penetration':<25} {'SW Penetration':<25} {'Diff':<10}")
    print(f"  " + "-" * 80)
    
    for i, ratio in enumerate(ANTILOVE_RATIOS):
        random_reps = results_part1["random"][i][1]
        sw_reps = results_part1["small_world"][i][1]
        
        avg_random = sum(r.love_penetration for r in random_reps) / len(random_reps)
        avg_sw = sum(r.love_penetration for r in sw_reps) / len(sw_reps)
        diff = avg_sw - avg_random
        
        bar_r = make_bar(avg_random, 15)
        bar_s = make_bar(avg_sw, 15)
        pct = int(ratio * 100)
        
        print(f"  {pct:<6d} [{bar_r:15s}] {avg_random:.2f}   "
              f"[{bar_s:15s}] {avg_sw:.2f}   {diff:+.3f}")
    
    # Convergence analysis
    print("\n[PART 3] Convergence Time by Anti-love Density")
    print("-" * 90)
    print(f"  {'Topology':<15} {'Anti%':<6} {'Avg Rounds to Conv':<20} {'Std Dev':<10}")
    print(f"  " + "-" * 80)
    
    for topology in TOPOLOGIES:
        for i, ratio in enumerate(ANTILOVE_RATIOS):
            reps = results_part1[topology][i][1]
            conv_times = [r.rounds_to_convergence for r in reps]
            avg_conv = sum(conv_times) / len(conv_times)
            var_conv = (sum((c - avg_conv) ** 2 for c in conv_times) / len(conv_times)) ** 0.5
            
            pct = int(ratio * 100)
            print(f"  {topology:<15} {pct:<6d} {avg_conv:<20.1f} {var_conv:<10.1f}")
    
    # Scaling experiment: N=100, 200, 300 (if time permits, optional N=500)
    print("\n[PART 4] Scaling Analysis: N=100, 200, 300")
    print("-" * 90)
    
    SIZES = [100, 200, 300]
    SCALE_ROUNDS = 30
    SCALE_REPS = 2
    SCALE_ANTILOVE = [0.2, 0.4]  # test at 20% and 40%
    
    results_scaling = {}
    
    for n_test in SIZES:
        results_scaling[n_test] = {}
        print(f"\nN={n_test}, rounds={SCALE_ROUNDS}, reps={SCALE_REPS}")
        print(f"  {'Anti%':<6} {'Penetration':<25} {'Avg Cluster':<15}")
        print(f"  " + "-" * 60)
        
        for antilove_ratio in SCALE_ANTILOVE:
            n_anti = int(antilove_ratio * n_test)
            reps = []
            
            for rep in range(SCALE_REPS):
                result = run_large_scale_trial(
                    n_total=n_test,
                    n_antilove=n_anti,
                    topology="small_world",
                    rounds=SCALE_ROUNDS,
                    seed=2000 + n_test + int(antilove_ratio * 100) * 100 + rep,
                )
                reps.append(result)
            
            avg_pen = sum(r.love_penetration for r in reps) / len(reps)
            avg_cluster = sum(r.avg_cluster_size for r in reps) / len(reps)
            
            results_scaling[n_test][antilove_ratio] = (avg_pen, avg_cluster)
            
            bar = make_bar(avg_pen, 20)
            pct = int(antilove_ratio * 100)
            print(f"  {pct:<6d} [{bar:20s}] {avg_pen:.2f}     "
                  f"avg_sz={avg_cluster:.1f}")
    
    # Summary and hypothesis testing
    print("\n" + "=" * 90)
    print("  HYPOTHESIS TESTING & CONCLUSIONS")
    print("=" * 90)
    
    print("\nH1: Critical threshold remains 30-40% anti-love")
    # Find max penetration for small_world
    penetrations_by_anti = {}
    for i, ratio in enumerate(ANTILOVE_RATIOS):
        sw_reps = results_part1["small_world"][i][1]
        avg_pen = sum(r.love_penetration for r in sw_reps) / len(sw_reps)
        penetrations_by_anti[int(ratio * 100)] = avg_pen
    
    print(f"  Small-world penetration by anti-love density:")
    for pct in sorted(penetrations_by_anti.keys()):
        pen = penetrations_by_anti[pct]
        status = "[STRONG]" if pen > 0.7 else "[WEAK]" if pen < 0.3 else "[MODERATE]"
        print(f"    {pct:2d}%: {pen:.2f} {status}")
    
    print("\nH2: Small-world topology shows larger clusters")
    for ratio in SCALE_ANTILOVE:
        ratio_pct = int(ratio * 100)
        print(f"  At {ratio_pct}% anti-love:")
        # Compare N=100 results
        random_reps = results_part1["random"][int(ratio / 0.1)][1]
        sw_reps = results_part1["small_world"][int(ratio / 0.1)][1]
        
        avg_random_cluster = sum(r.max_cluster_size for r in random_reps) / len(random_reps)
        avg_sw_cluster = sum(r.max_cluster_size for r in sw_reps) / len(sw_reps)
        
        print(f"    Random max cluster: {avg_random_cluster:.1f}")
        print(f"    Small-world max cluster: {avg_sw_cluster:.1f}")
        if avg_sw_cluster > avg_random_cluster:
            print(f"    => CONFIRMED: SW has larger clusters")
        else:
            print(f"    => NOT CONFIRMED: Random has comparable/larger clusters")
    
    print("\nH3: Larger populations show slower convergence")
    print("  Convergence time (small-world, 40% anti-love):")
    for n_size in SIZES:
        if 0.4 in results_scaling.get(n_size, {}):
            # Estimate from Part 1 data for N=100
            if n_size == 100:
                n100_reps = results_part1["small_world"][5][1]  # 50% is index 5, but we need 40%
                # Find closest: index for 40% is int(0.4 / 0.1) = 4
                n100_reps = results_part1["small_world"][4][1]
                avg_conv = sum(r.rounds_to_convergence for r in n100_reps) / len(n100_reps)
                print(f"    N={n_size}: {avg_conv:.1f} rounds")
    
    print("\nH4: Love penetration decreases more sharply in small populations")
    print("  Slope of penetration decline (anti-love 0% -> 50%):")
    for topology in TOPOLOGIES:
        pen_0 = results_part1[topology][0][1][0].love_penetration
        pen_50 = results_part1[topology][-1][1][0].love_penetration
        slope = (pen_0 - pen_50) / 50.0
        print(f"    {topology}: {slope:.3f} per 1% anti-love")
    
    print("\n" + "=" * 90)
    print("  END OF LARGE-SCALE SOCIAL SIMULATION")
    print("=" * 90)


if __name__ == "__main__":
    main()
