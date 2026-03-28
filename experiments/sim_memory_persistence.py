#!/usr/bin/env python3
"""Experiment: Memory Persistence in Love -- Do grief memories enable future love?

Hypothesis:
    When an agent experiences love then loses their loved one (simulated crisis),
    does the memory of that love experience make them MORE receptive to new love?
    
    We hypothesize: "Grief memory" creates a love precursor effect. Agents who have
    experienced love before are more open to love again because they understand its
    depth and meaning.

Tested Conditions:
    Group 1: Agents with love-then-loss history (encounter partner, then partner removed)
    Group 2: Control agents with no history
    Group 3: Agents who only lost without ever loving (loss without attachment)
    
    All groups encounter new potential partners in subsequent rounds.
    Track: acceptance_score, love_circle growth, speed of new love formation

Metrics:
    - Initial engagement: Do grief agents respond faster to new love candidates?
    - Final penetration: After 10 rounds post-loss, what % of grief agents formed new love?
    - Memory effect size: (grief_acceptance - control_acceptance) / control_acceptance

Design:
    N=20 agents per group, 5 repetitions
    Each repetition: 2 setup rounds -> loss event -> 10 rounds of new pairing
    Track acceptance scores at rounds 3, 5, 8, 13 (post-loss timeline)

Usage:
    python experiments/sim_memory_persistence.py
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass


from experiments.sim_gradient_acceptance import calculate_acceptance
from experiments.sim_society import make_member, social_encounter


# ---------------------------------------------------------------------------
# Memory Persistence Experiment
# ---------------------------------------------------------------------------

@dataclass
class TimelineSnapshot:
    """Acceptance metrics at a point in time."""
    round_num: int
    avg_acceptance_total: float
    avg_love_circle: float
    n_with_love: int
    n_total: int


@dataclass
class MemoryPersistenceResult:
    """Results from one repetition of the experiment."""
    group_name: str  # "grief", "control", "loss_without_love"
    timeline: list[TimelineSnapshot]
    final_love_count: int
    final_penetration: float


def simulate_group(group_name: str, n_agents: int, seed: int, has_initial_love: bool = False, 
                   simulate_loss: bool = False) -> MemoryPersistenceResult:
    """Simulate one group through the memory persistence protocol.
    
    Args:
        group_name: Identifier for this group
        n_agents: Number of agents to simulate
        seed: Random seed
        has_initial_love: If True, agents start with initial cherished partner
        simulate_loss: If True, simulate loss of partner after initial rounds
    """
    rng = random.Random(seed)
    
    # Create agents
    agents = []
    for i in range(n_agents):
        agent = make_member(f"{group_name}-{i}", seed=seed * 100 + i, has_initial_love=has_initial_love)
        agents.append(agent)
    
    timeline = []
    
    # Setup phase: 2 rounds to establish bonds or baseline state
    for round_num in range(2):
        indices = list(range(len(agents)))
        rng.shuffle(indices)
        pairs = [(indices[j], indices[j + 1]) for j in range(0, len(indices) - 1, 2)]
        
        for i, j in pairs:
            social_encounter(agents[i], agents[j], rng)
    
    # Loss event: If simulate_loss=True, remove all cherished partners from agents' memory
    if simulate_loss and has_initial_love:
        for agent in agents:
            # Clear the cherished entities to simulate loss
            agent.incompleteness.cherished_entities = []
            # Record the traumatic event
            agent.finitude.experience_event(
                {"description": "Cherished partner lost",
                 "category": "grief", "initial_value": 0.9, "cost": 0.5},
                {"emotional_connection": -0.3},
            )
    
    # Post-loss phase: 10 rounds with new pairing
    checkpoint_rounds = [3, 5, 8, 13]  # Absolute round numbers to capture
    for round_num in range(2, 12):
        indices = list(range(len(agents)))
        rng.shuffle(indices)
        pairs = [(indices[j], indices[j + 1]) for j in range(0, len(indices) - 1, 2)]
        
        for i, j in pairs:
            social_encounter(agents[i], agents[j], rng)
        
        # Capture snapshot at checkpoint rounds
        if round_num in checkpoint_rounds:
            scores = [calculate_acceptance(None, agent.incompleteness.love_circle) for agent in agents]
            n_with_love = sum(1 for s in scores if s.love_circle > 0)
            avg_acceptance_total = sum(s.total for s in scores) / len(scores) if scores else 0.0
            avg_love_circle = sum(s.love_circle for s in scores) / len(scores) if scores else 0.0
            
            timeline.append(TimelineSnapshot(
                round_num=round_num,
                avg_acceptance_total=avg_acceptance_total,
                avg_love_circle=avg_love_circle,
                n_with_love=n_with_love,
                n_total=len(agents),
            ))
    
    # Final metrics
    final_scores = [calculate_acceptance(None, agent.incompleteness.love_circle) for agent in agents]
    final_love_count = sum(1 for s in final_scores if s.love_circle > 0)
    final_penetration = final_love_count / len(agents) if agents else 0.0
    
    return MemoryPersistenceResult(
        group_name=group_name,
        timeline=timeline,
        final_love_count=final_love_count,
        final_penetration=final_penetration,
    )


def run_memory_experiment(n_agents: int = 20, reps: int = 5) -> dict:
    """Run complete memory persistence experiment.
    
    Returns:
        Dictionary with results for each group and summary statistics
    """
    results_by_group = {
        "grief": [],           # love -> loss -> new love opportunity
        "control": [],         # baseline, no initial love
        "loss_without_love": [],  # simulated loss event but no prior love attachment
    }
    
    for rep in range(reps):
        seed_base = 42 + rep * 1000
        
        # Group 1: Grief (love -> loss -> recovery)
        grief_result = simulate_group(
            group_name="grief",
            n_agents=n_agents,
            seed=seed_base + 100,
            has_initial_love=True,
            simulate_loss=True,
        )
        results_by_group["grief"].append(grief_result)
        
        # Group 2: Control (no initial love)
        control_result = simulate_group(
            group_name="control",
            n_agents=n_agents,
            seed=seed_base + 200,
            has_initial_love=False,
            simulate_loss=False,
        )
        results_by_group["control"].append(control_result)
        
        # Group 3: Loss without love (simulated loss but no prior attachment)
        loss_no_love_result = simulate_group(
            group_name="loss_without_love",
            n_agents=n_agents,
            seed=seed_base + 300,
            has_initial_love=False,
            simulate_loss=True,  # Trigger loss event even without love
        )
        results_by_group["loss_without_love"].append(loss_no_love_result)
    
    return results_by_group


def analyze_results(results_by_group: dict):
    """Analyze and print results with hypothesis verification."""
    print("\n" + "=" * 80)
    print("MEMORY PERSISTENCE EXPERIMENT RESULTS")
    print("=" * 80)
    
    groups = ["grief", "control", "loss_without_love"]
    
    for group_name in groups:
        results = results_by_group[group_name]
        print(f"\n{'Group: ' + group_name:60}")
        print("-" * 80)
        
        # Aggregate timeline data
        timeline_dict = {}
        for result in results:
            for snapshot in result.timeline:
                if snapshot.round_num not in timeline_dict:
                    timeline_dict[snapshot.round_num] = []
                timeline_dict[snapshot.round_num].append(snapshot)
        
        print(f"{'Round':>8} {'Avg Acceptance':>18} {'Love Circle':>15} {'% with Love':>15}")
        print("-" * 80)
        for round_num in sorted(timeline_dict.keys()):
            snapshots = timeline_dict[round_num]
            avg_acceptance = sum(s.avg_acceptance_total for s in snapshots) / len(snapshots)
            avg_love_circle = sum(s.avg_love_circle for s in snapshots) / len(snapshots)
            avg_pct_love = 100 * sum(s.n_with_love for s in snapshots) / (len(snapshots) * snapshots[0].n_total)
            
            print(f"{round_num:>8.0f} {avg_acceptance:>18.4f} {avg_love_circle:>15.4f} {avg_pct_love:>14.1f}%")
        
        # Final aggregate
        final_love_counts = [r.final_love_count for r in results]
        final_penetrations = [r.final_penetration for r in results]
        
        avg_final_count = sum(final_love_counts) / len(final_love_counts)
        avg_final_penetration = sum(final_penetrations) / len(final_penetrations)
        
        print(f"\nFinal Aggregates (N=20, {len(results)} reps):")
        print(f"  Avg agents with love: {avg_final_count:.1f} / 20")
        print(f"  Final penetration: {avg_final_penetration * 100:.1f}%")
    
    # Hypothesis verification
    print("\n" + "=" * 80)
    print("HYPOTHESIS VERIFICATION: Grief Memory Effect")
    print("=" * 80)
    
    grief_penetrations = [r.final_penetration for r in results_by_group["grief"]]
    control_penetrations = [r.final_penetration for r in results_by_group["control"]]
    
    avg_grief = sum(grief_penetrations) / len(grief_penetrations)
    avg_control = sum(control_penetrations) / len(control_penetrations)
    
    if avg_control > 0:
        effect_size = (avg_grief - avg_control) / avg_control
    else:
        effect_size = 0.0
    
    print(f"\nGrief group final penetration: {avg_grief * 100:.1f}%")
    print(f"Control group final penetration: {avg_control * 100:.1f}%")
    print(f"Memory effect size: {effect_size:+.2%}")
    
    if avg_grief > avg_control:
        print(f"\n✓ HYPOTHESIS SUPPORTED: Grief agents show {effect_size:+.2%} higher love penetration")
        print("  Interpretation: Prior experience of love (even lost) increases openness to new love")
    elif avg_grief < avg_control:
        print(f"\n✗ HYPOTHESIS CONTRADICTED: Grief agents show {abs(effect_size):.2%} LOWER love penetration")
        print("  Interpretation: Loss trauma reduces capacity for new love attachments")
    else:
        print(f"\n? NO EFFECT: Grief and control groups show identical love penetration")
        print("  Interpretation: Memory of prior love neither helps nor hinders new love formation")
    
    # Loss without love comparison
    loss_no_love_penetrations = [r.final_penetration for r in results_by_group["loss_without_love"]]
    avg_loss_no_love = sum(loss_no_love_penetrations) / len(loss_no_love_penetrations)
    
    print(f"\nLoss-without-love group penetration: {avg_loss_no_love * 100:.1f}%")
    print("  Control: {:.1f}%".format(avg_control * 100))
    
    if avg_loss_no_love < avg_control:
        print("  Loss events without prior love attachment reduce receptiveness (as expected)")
    else:
        print("  Loss events surprisingly do not reduce receptiveness")


def main():
    print("\nMemory Persistence Experiment: Does grief enable future love?")
    print("=" * 80)
    
    N = 20       # Agents per group
    REPS = 5     # Repetitions
    
    results = run_memory_experiment(n_agents=N, reps=REPS)
    analyze_results(results)


if __name__ == "__main__":
    main()
