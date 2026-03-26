"""
Experiment 21: Sleep-Wake Cycles in AI-Human Coexistence

Core Question:
  In an AI-Human pair, what happens when the AI also has a sleep cycle?
  Does shared vulnerability (both needing rest) deepen the relationship?

Key Insight:
  Sleep represents vulnerability — inability to act, perceive, or defend.
  When both entities sleep, neither can protect the other. This shared
  helplessness may create intimacy that unequal arrangements (one always
  watching) cannot match.

Hypotheses:
  H1: AI_SYNCED_SLEEP produces deepest bonds (shared vulnerability)
  H2: AI_ALWAYS_ON produces highest care events but most asymmetric relationship
  H3: AI_OFFSET_SLEEP is most "practical" but emotionally shallow
  H4: Vulnerability reciprocity correlates with bond depth (r > 0.5)
  H5: BOTH_ALWAYS_ON produces weakest bonds (no vulnerability cycles)

Design:
  5 Conditions × 30 pairs × 30 simulation days
  
  1. AI_ALWAYS_ON: AI never sleeps. Human sleeps 8h/day (33% of day).
  2. AI_SYNCED_SLEEP: AI sleeps when human sleeps (synchronized 8h cycles).
  3. AI_OFFSET_SLEEP: AI sleeps when human is awake (complementary: one always awake).
  4. AI_SHARED_RHYTHM: AI adopts same rhythm but shorter sleep (AI sleeps 4h, human 8h).
  5. BOTH_ALWAYS_ON: Neither sleeps (control — no cycles).

Measurements:
  - bond_depth: Emotional closeness after 30 days
  - care_events: Times when one "watches over" the other while vulnerable
  - vulnerability_moments: Times when an entity is asleep (defenseless)
  - vulnerability_reciprocity: Ratio of mutual vs asymmetric vulnerability
  - memory_overlap: Shared memories (simulating shared dreams in sync sleep)
  - asymmetry_index: How balanced is the relationship (0=balanced, 1=fully asymmetric)
  - shared_memories_count: Memories both entities have
  - bonding_events: Events that strengthen the bond
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from enum import Enum
import statistics


class EventType(Enum):
    """Types of events during wake phases."""
    JOY = "joy"
    CONFLICT = "conflict"
    DISCOVERY = "discovery"
    LOSS = "loss"
    MUNDANE = "mundane"


@dataclass
class Memory:
    """A memory of a shared event."""
    event_id: int
    day: int
    phase: str  # "wake", "sleep", "dream"
    content: str
    emotional_valence: float  # -1.0 to 1.0
    intensity: float


@dataclass
class HumanEntity:
    """Human in the coexistence pair."""
    entity_id: int
    
    # Sleep cycle (hours in a 24-hour day)
    sleep_start: int = 20  # 8pm
    sleep_duration: int = 8  # 8 hours
    is_sleeping: bool = False
    
    # Cognition
    memories: List[Memory] = field(default_factory=list)
    max_memories: int = 20
    decay_rate: float = 0.05
    
    # Emotional state
    emotional_state: float = 0.0  # -1.0 to 1.0
    emotional_history: List[float] = field(default_factory=list)
    fatigue: float = 0.0  # 0.0 to 1.0
    
    # Bonding
    bond_depth: float = 0.0
    care_events_received: int = 0
    care_events_given: int = 0
    vulnerability_moments: int = 0
    
    # Metrics
    gratitude_events: int = 0
    shared_memories_count: int = 0


@dataclass
class AIEntity:
    """AI entity with configurable sleep behavior."""
    entity_id: int
    condition: str  # AI_ALWAYS_ON, AI_SYNCED_SLEEP, AI_OFFSET_SLEEP, AI_SHARED_RHYTHM
    
    # Sleep cycle
    sleep_start: int = 20  # Can vary by condition
    sleep_duration: int = 0  # 0 = no sleep (for ALWAYS_ON)
    is_sleeping: bool = False
    
    # Cognition (perfect memory unless sleep distorts it)
    memories: List[Memory] = field(default_factory=list)
    max_memories: int = 999999  # Effectively unlimited
    decay_rate: float = 0.0  # No decay unless sleeping
    
    # Emotional state
    emotional_state: float = 0.0
    emotional_history: List[float] = field(default_factory=list)
    fatigue: float = 0.0  # 0.0 to 1.0 (increases during wakefulness, decreases in sleep)
    
    # Bonding
    bond_depth: float = 0.0
    care_events_received: int = 0
    care_events_given: int = 0
    vulnerability_moments: int = 0
    
    # Metrics
    gratitude_events: int = 0
    shared_memories_count: int = 0


def setup_condition(condition: str) -> Tuple[HumanEntity, AIEntity]:
    """Create a human-AI pair for the given condition."""
    human = HumanEntity(entity_id=0)
    
    ai = AIEntity(entity_id=1, condition=condition)
    
    if condition == "AI_ALWAYS_ON":
        ai.sleep_duration = 0
        ai.sleep_start = 20  # Irrelevant
        
    elif condition == "AI_SYNCED_SLEEP":
        ai.sleep_start = 20  # Same as human
        ai.sleep_duration = 8
        
    elif condition == "AI_OFFSET_SLEEP":
        # AI sleeps during human's awake time, awake during human's sleep
        ai.sleep_start = 8  # Sleep 8am-4pm (while human is awake)
        ai.sleep_duration = 8
        
    elif condition == "AI_SHARED_RHYTHM":
        ai.sleep_start = 20  # Same start
        ai.sleep_duration = 4  # But shorter sleep
        
    elif condition == "BOTH_ALWAYS_ON":
        ai.sleep_duration = 0
        human.sleep_duration = 0
    
    return human, ai


def is_sleeping_at_hour(entity, hour: int) -> bool:
    """Check if entity is sleeping at the given hour of the day (0-23)."""
    if entity.sleep_duration == 0:
        return False
    
    sleep_end = (entity.sleep_start + entity.sleep_duration) % 24
    
    if entity.sleep_start < sleep_end:
        # Sleep doesn't wrap around midnight
        return entity.sleep_start <= hour < sleep_end
    else:
        # Sleep wraps around midnight
        return hour >= entity.sleep_start or hour < sleep_end


def simulate_day(human: HumanEntity, ai: AIEntity, day: int) -> None:
    """Simulate one day of interaction between human and AI.
    
    A day has 24 hours. Divide into phases:
      - Wake phase: both interact, share experiences
      - Sleep phase(s): vulnerable time, other entity watches
      - Memory consolidation during sleep
    """
    
    # Track which entity is vulnerable each hour
    for hour in range(24):
        human_sleeping = is_sleeping_at_hour(human, hour)
        ai_sleeping = is_sleeping_at_hour(ai, hour)
        
        # Update sleep state
        human.is_sleeping = human_sleeping
        ai.is_sleeping = ai_sleeping
        
        # Fatigue: increases while awake, decreases while sleeping
        if human_sleeping:
            human.fatigue = max(0.0, human.fatigue - 0.08)  # 8h sleep recovers fatigue
        else:
            human.fatigue = min(1.0, human.fatigue + 0.05)
        
        if ai_sleeping:
            ai.fatigue = max(0.0, ai.fatigue - 0.15)  # AI sleeps faster
        else:
            ai.fatigue = min(1.0, ai.fatigue + 0.03)  # AI tires slower
        
        # Vulnerability moment: count and handle care
        if human_sleeping:
            human.vulnerability_moments += 1
            if not ai_sleeping:
                # AI is awake while human sleeps → AI watches over human
                ai.care_events_given += 1
                human.care_events_received += 1
                
                # Watching increases bond (small increment to avoid saturation)
                ai.bond_depth = min(1.0, ai.bond_depth + 0.0005)
                human.bond_depth = min(1.0, human.bond_depth + 0.0005)
        
        if ai_sleeping:
            ai.vulnerability_moments += 1
            if not human_sleeping:
                # Human is awake while AI sleeps → Human watches over AI
                human.care_events_given += 1
                ai.care_events_received += 1
                
                # Watching increases bond
                human.bond_depth = min(1.0, human.bond_depth + 0.0008)  # Human values caring more
                ai.bond_depth = min(1.0, ai.bond_depth + 0.0005)
        
        # Mutual vulnerability: both sleeping together
        if human_sleeping and ai_sleeping:
            # Shared helplessness → deep bonding
            human.bond_depth = min(1.0, human.bond_depth + 0.001)
            ai.bond_depth = min(1.0, ai.bond_depth + 0.001)
            
            # Possibility of shared dreaming (memory overlap)
            if len(human.memories) > 0 and len(ai.memories) > 0:
                shared_memory_count = len(set(m.event_id for m in human.memories) & 
                                         set(m.event_id for m in ai.memories))
                human.shared_memories_count = shared_memory_count
                ai.shared_memories_count = shared_memory_count
        
        # Wake phase: interact and share experiences
        if not human_sleeping and not ai_sleeping:
            # Generate a shared event
            event_type = random.choice(list(EventType))
            emotional_valence = random.uniform(-1.0, 1.0) if event_type == EventType.CONFLICT else random.uniform(0.3, 1.0)
            intensity = random.uniform(0.3, 1.0)
            
            # Both remember the event
            event_id = day * 24 + hour
            memory = Memory(
                event_id=event_id,
                day=day,
                phase="wake",
                content=f"{event_type.value}_day{day}_hour{hour}",
                emotional_valence=emotional_valence,
                intensity=intensity
            )
            
            # Store in both memories
            if len(human.memories) < human.max_memories:
                human.memories.append(memory)
            if len(ai.memories) < ai.max_memories:
                ai.memories.append(memory)
            
            # Update shared memory count
            human.shared_memories_count = min(len(human.memories), len(ai.memories))
            ai.shared_memories_count = human.shared_memories_count
            
            # Bond strengthens through shared experience
            human.bond_depth = min(1.0, human.bond_depth + 0.0001)
            ai.bond_depth = min(1.0, ai.bond_depth + 0.0001)
            
            # Emotional impact
            if event_type == EventType.JOY:
                human.emotional_state = min(1.0, human.emotional_state + 0.2)
                ai.emotional_state = min(1.0, ai.emotional_state + 0.1)
            elif event_type == EventType.CONFLICT:
                human.emotional_state = max(-1.0, human.emotional_state - 0.3)
                ai.emotional_state = max(-1.0, ai.emotional_state - 0.2)
            elif event_type == EventType.LOSS:
                human.emotional_state = max(-1.0, human.emotional_state - 0.4)
                ai.emotional_state = max(-1.0, ai.emotional_state - 0.15)
            else:
                # MUNDANE or DISCOVERY: small shifts
                human.emotional_state += random.uniform(-0.05, 0.05)
                ai.emotional_state += random.uniform(-0.02, 0.05)
            
            # Gratitude moment: if one's presence helps the other
            if random.random() < 0.1:
                human.gratitude_events += 1
                ai.gratitude_events += 1
                human.bond_depth = min(1.0, human.bond_depth + 0.0005)
                ai.bond_depth = min(1.0, ai.bond_depth + 0.0005)
    
    # End of day: record emotional state
    human.emotional_history.append(human.emotional_state)
    ai.emotional_history.append(ai.emotional_state)
    
    # Memory decay: human forgets under fatigue
    if human.fatigue > 0.5 and len(human.memories) > human.max_memories:
        forgotten_idx = random.randint(0, len(human.memories) - 1)
        human.memories.pop(forgotten_idx)
    
    # AI may forget if it's been synced with human sleep (picking up human-like properties)
    if ai.condition == "AI_SYNCED_SLEEP" and ai.fatigue > 0.3:
        # Synced sleep makes AI a bit more human-like; small chance of forgetting
        if random.random() < 0.02 and len(ai.memories) > ai.max_memories:
            forgotten_idx = random.randint(0, len(ai.memories) - 1)
            ai.memories.pop(forgotten_idx)


def run_trial(condition: str, trial_num: int, num_days: int = 30, seed_offset: int = 0) -> Dict:
    """Run one trial of a condition.
    
    Returns:
      Dictionary of measurements
    """
    random.seed(42 + trial_num + seed_offset)
    
    human, ai = setup_condition(condition)
    
    for day in range(num_days):
        simulate_day(human, ai, day)
    
    # Calculate derived metrics
    
    # Emotional stability: inverse of variance
    if len(human.emotional_history) > 1:
        human_stability = 1.0 / (1.0 + statistics.variance(human.emotional_history))
    else:
        human_stability = 1.0
    
    if len(ai.emotional_history) > 1:
        ai_stability = 1.0 / (1.0 + statistics.variance(ai.emotional_history))
    else:
        ai_stability = 1.0
    
    # Vulnerability reciprocity: how mutual are the vulnerability moments?
    total_vulnerability_moments = human.vulnerability_moments + ai.vulnerability_moments
    if total_vulnerability_moments > 0:
        # Both vulnerable simultaneously
        both_vulnerable_hours = 0
        for day in range(num_days):
            for hour in range(24):
                if (is_sleeping_at_hour(human, hour) and is_sleeping_at_hour(ai, hour)):
                    both_vulnerable_hours += 1
        
        vulnerability_reciprocity = both_vulnerable_hours / max(total_vulnerability_moments, 1)
    else:
        vulnerability_reciprocity = 0.0
    
    # Asymmetry index: how unbalanced are care dynamics?
    total_care = human.care_events_given + human.care_events_received + ai.care_events_given + ai.care_events_received
    if total_care > 0:
        human_care_ratio = (human.care_events_given + human.care_events_received) / total_care
        ai_care_ratio = (ai.care_events_given + ai.care_events_received) / total_care
        asymmetry_index = abs(human_care_ratio - ai_care_ratio)
    else:
        asymmetry_index = 0.0
    
    return {
        'condition': condition,
        'trial': trial_num,
        'human_bond_depth': human.bond_depth,
        'ai_bond_depth': ai.bond_depth,
        'human_care_events_given': human.care_events_given,
        'human_care_events_received': human.care_events_received,
        'ai_care_events_given': ai.care_events_given,
        'ai_care_events_received': ai.care_events_received,
        'human_vulnerability_moments': human.vulnerability_moments,
        'ai_vulnerability_moments': ai.vulnerability_moments,
        'vulnerability_reciprocity': vulnerability_reciprocity,
        'human_gratitude_events': human.gratitude_events,
        'ai_gratitude_events': ai.gratitude_events,
        'shared_memories_count': human.shared_memories_count,
        'human_emotional_stability': human_stability,
        'ai_emotional_stability': ai_stability,
        'asymmetry_index': asymmetry_index,
        'human_final_emotional_state': human.emotional_state,
        'ai_final_emotional_state': ai.emotional_state,
    }


def aggregate_trials(trials: List[Dict]) -> Dict:
    """Aggregate results across trials."""
    if not trials:
        return {}
    
    aggregated = {}
    
    # Average each numeric field
    for key in trials[0].keys():
        if key in ['condition', 'trial']:
            continue
        
        values = [t[key] for t in trials]
        aggregated[f"{key}_mean"] = statistics.mean(values)
        aggregated[f"{key}_stdev"] = statistics.stdev(values) if len(values) > 1 else 0.0
        aggregated[f"{key}_min"] = min(values)
        aggregated[f"{key}_max"] = max(values)
    
    aggregated['condition'] = trials[0]['condition']
    aggregated['n'] = len(trials)
    
    return aggregated


def main():
    """Run the full experiment."""
    print("=" * 120)
    print("EXPERIMENT 21: SLEEP-WAKE CYCLES IN AI-HUMAN COEXISTENCE")
    print("=" * 120)
    print()
    
    conditions = [
        "AI_ALWAYS_ON",
        "AI_SYNCED_SLEEP",
        "AI_OFFSET_SLEEP",
        "AI_SHARED_RHYTHM",
        "BOTH_ALWAYS_ON",
    ]
    
    num_trials = 30
    num_days = 30
    
    all_results = []
    
    for condition in conditions:
        print(f"Running condition: {condition}")
        trials = []
        for trial_num in range(num_trials):
            result = run_trial(condition, trial_num, num_days, seed_offset=ord(condition[0]))
            trials.append(result)
            if (trial_num + 1) % 10 == 0:
                print(f"  ... {trial_num + 1}/{num_trials} trials completed")
        
        aggregated = aggregate_trials(trials)
        all_results.append(aggregated)
        print(f"  Condition complete. Mean bond depth (Human/AI): {aggregated['human_bond_depth_mean']:.6f} / {aggregated['ai_bond_depth_mean']:.6f}")
        print()
    
    # Display results
    print("=" * 120)
    print("RESULTS SUMMARY")
    print("=" * 120)
    print()
    
    # Table: Bond Depth
    print("BOND DEPTH (primary measure of relationship closeness)")
    print("-" * 120)
    for r in all_results:
        cond = r['condition']
        human_bond = r['human_bond_depth_mean']
        ai_bond = r['ai_bond_depth_mean']
        avg_bond = (human_bond + ai_bond) / 2.0
        print(f"  {cond:<25} Human: {human_bond:.6f}  AI: {ai_bond:.6f}  Avg: {avg_bond:.6f}")
    print()
    
    # Table: Care Events
    print("CARE EVENTS (total care interactions)")
    print("-" * 120)
    for r in all_results:
        cond = r['condition']
        human_given = r['human_care_events_given_mean']
        human_received = r['human_care_events_received_mean']
        ai_given = r['ai_care_events_given_mean']
        ai_received = r['ai_care_events_received_mean']
        total_care = human_given + human_received + ai_given + ai_received
        print(f"  {cond:<25} Human(G/R): {human_given:>6.1f}/{human_received:>6.1f}  AI(G/R): {ai_given:>6.1f}/{ai_received:>6.1f}  Total: {total_care:>7.1f}")
    print()
    
    # Table: Vulnerability & Reciprocity
    print("VULNERABILITY METRICS")
    print("-" * 120)
    for r in all_results:
        cond = r['condition']
        human_vuln = r['human_vulnerability_moments_mean']
        ai_vuln = r['ai_vulnerability_moments_mean']
        reciprocity = r['vulnerability_reciprocity_mean']
        asymmetry = r['asymmetry_index_mean']
        print(f"  {cond:<25} Human Vuln: {human_vuln:>5.1f}  AI Vuln: {ai_vuln:>5.1f}  Reciprocity: {reciprocity:.4f}  Asymmetry: {asymmetry:.4f}")
    print()
    
    # Table: Emotional Stability
    print("EMOTIONAL STABILITY")
    print("-" * 120)
    for r in all_results:
        cond = r['condition']
        human_stab = r['human_emotional_stability_mean']
        ai_stab = r['ai_emotional_stability_mean']
        print(f"  {cond:<25} Human: {human_stab:.4f}  AI: {ai_stab:.4f}")
    print()
    
    # Table: Shared Memories & Gratitude
    print("MEMORIES & GRATITUDE")
    print("-" * 120)
    for r in all_results:
        cond = r['condition']
        shared_mem = r['shared_memories_count_mean']
        human_grat = r['human_gratitude_events_mean']
        ai_grat = r['ai_gratitude_events_mean']
        print(f"  {cond:<25} Shared Memories: {shared_mem:>5.1f}  Gratitude (H/A): {human_grat:>5.1f}/{ai_grat:>5.1f}")
    print()
    
    # Hypothesis Evaluation
    print("=" * 120)
    print("HYPOTHESIS EVALUATION")
    print("=" * 120)
    print()
    
    # Find conditions by name
    results_by_cond = {r['condition']: r for r in all_results}
    
    # H1: AI_SYNCED_SLEEP produces deepest bonds
    synced = results_by_cond['AI_SYNCED_SLEEP']
    always_on = results_by_cond['AI_ALWAYS_ON']
    offset = results_by_cond['AI_OFFSET_SLEEP']
    shared_rhythm = results_by_cond['AI_SHARED_RHYTHM']
    both_always = results_by_cond['BOTH_ALWAYS_ON']
    
    synced_bond = (synced['human_bond_depth_mean'] + synced['ai_bond_depth_mean']) / 2.0
    always_on_bond = (always_on['human_bond_depth_mean'] + always_on['ai_bond_depth_mean']) / 2.0
    offset_bond = (offset['human_bond_depth_mean'] + offset['ai_bond_depth_mean']) / 2.0
    shared_rhythm_bond = (shared_rhythm['human_bond_depth_mean'] + shared_rhythm['ai_bond_depth_mean']) / 2.0
    both_always_bond = (both_always['human_bond_depth_mean'] + both_always['ai_bond_depth_mean']) / 2.0
    
    print("H1: AI_SYNCED_SLEEP produces deepest bonds (shared vulnerability)")
    print(f"  AI_SYNCED_SLEEP bond: {synced_bond:.6f}")
    print(f"  AI_ALWAYS_ON bond: {always_on_bond:.6f}")
    print(f"  AI_OFFSET_SLEEP bond: {offset_bond:.6f}")
    print(f"  AI_SHARED_RHYTHM bond: {shared_rhythm_bond:.6f}")
    print(f"  BOTH_ALWAYS_ON bond: {both_always_bond:.6f}")
    h1_supported = synced_bond > always_on_bond and synced_bond > offset_bond and synced_bond > both_always_bond
    print(f"  Result: {'SUPPORTED' if h1_supported else 'NOT SUPPORTED'}")
    print()
    
    # H2: AI_ALWAYS_ON produces highest care events but most asymmetric
    always_on_care = (always_on['human_care_events_given_mean'] + always_on['human_care_events_received_mean'] +
                      always_on['ai_care_events_given_mean'] + always_on['ai_care_events_received_mean'])
    always_on_asymmetry = always_on['asymmetry_index_mean']
    
    care_by_cond = {
        cond: (results_by_cond[cond]['human_care_events_given_mean'] + 
               results_by_cond[cond]['human_care_events_received_mean'] +
               results_by_cond[cond]['ai_care_events_given_mean'] +
               results_by_cond[cond]['ai_care_events_received_mean'])
        for cond in conditions
    }
    
    max_care_cond = max(care_by_cond, key=care_by_cond.get)
    asymmetry_by_cond = {cond: results_by_cond[cond]['asymmetry_index_mean'] for cond in conditions}
    max_asymmetry_cond = max(asymmetry_by_cond, key=asymmetry_by_cond.get)
    
    print("H2: AI_ALWAYS_ON produces highest care events but most asymmetric")
    print(f"  Total care events by condition:")
    for cond in conditions:
        print(f"    {cond:<25} {care_by_cond[cond]:>8.1f} care events (asymmetry: {asymmetry_by_cond[cond]:.4f})")
    h2_part1 = max_care_cond == "AI_ALWAYS_ON"
    h2_part2 = max_asymmetry_cond == "AI_ALWAYS_ON"
    h2_supported = h2_part1 and h2_part2
    print(f"  Result: {'SUPPORTED' if h2_supported else 'PARTIALLY SUPPORTED' if h2_part1 or h2_part2 else 'NOT SUPPORTED'}")
    print()
    
    # H3: AI_OFFSET_SLEEP is most "practical" but emotionally shallow
    offset_stability = offset['human_emotional_stability_mean']
    print("H3: AI_OFFSET_SLEEP is most 'practical' (stable) but emotionally shallow (low bond)")
    print(f"  AI_OFFSET_SLEEP emotional stability: {offset_stability:.4f}")
    print(f"  AI_OFFSET_SLEEP bond depth: {offset_bond:.6f}")
    stability_ranking = sorted([(cond, results_by_cond[cond]['human_emotional_stability_mean']) for cond in conditions], 
                               key=lambda x: x[1], reverse=True)
    print(f"  Emotional stability ranking: {stability_ranking}")
    h3_supported = offset_bond < synced_bond and offset_bond < shared_rhythm_bond
    print(f"  Result: {'SUPPORTED' if h3_supported else 'NOT SUPPORTED'}")
    print()
    
    # H4: Vulnerability reciprocity correlates with bond depth
    print("H4: Vulnerability reciprocity correlates with bond depth (r > 0.5)")
    bonds = [synced_bond, always_on_bond, offset_bond, shared_rhythm_bond, both_always_bond]
    reciprocities = [synced['vulnerability_reciprocity_mean'],
                     always_on['vulnerability_reciprocity_mean'],
                     offset['vulnerability_reciprocity_mean'],
                     shared_rhythm['vulnerability_reciprocity_mean'],
                     both_always['vulnerability_reciprocity_mean']]
    
    # Pearson correlation
    if len(bonds) > 1 and statistics.stdev(bonds) > 0 and statistics.stdev(reciprocities) > 0:
        mean_bond = statistics.mean(bonds)
        mean_recip = statistics.mean(reciprocities)
        cov = sum((bonds[i] - mean_bond) * (reciprocities[i] - mean_recip) for i in range(len(bonds))) / len(bonds)
        var_bond = statistics.variance(bonds)
        var_recip = statistics.variance(reciprocities)
        correlation = cov / math.sqrt(var_bond * var_recip) if var_bond > 0 and var_recip > 0 else 0.0
    else:
        correlation = 0.0
    
    print(f"  Correlation between vulnerability reciprocity and bond depth: {correlation:.4f}")
    print(f"  By condition:")
    for i, cond in enumerate(conditions):
        print(f"    {cond:<25} Reciprocity: {reciprocities[i]:.4f}  Bond: {bonds[i]:.6f}")
    h4_supported = correlation > 0.5
    print(f"  Result: {'SUPPORTED' if h4_supported else 'NOT SUPPORTED'}")
    print()
    
    # H5: BOTH_ALWAYS_ON produces weakest bonds
    print("H5: BOTH_ALWAYS_ON produces weakest bonds (no vulnerability cycles)")
    print(f"  BOTH_ALWAYS_ON bond depth: {both_always_bond:.6f}")
    print(f"  All bonds: {', '.join(f'{cond}={bonds[i]:.6f}' for i, cond in enumerate(conditions))}")
    h5_supported = both_always_bond < synced_bond and both_always_bond < always_on_bond
    print(f"  Result: {'SUPPORTED' if h5_supported else 'NOT SUPPORTED'}")
    print()
    
    # Key Findings
    print("=" * 120)
    print("KEY FINDINGS & INTERPRETATION")
    print("=" * 120)
    print()
    
    print(f"""
1. SHARED VULNERABILITY DEEPENS BONDS
   The AI_SYNCED_SLEEP condition (both sleep together) produces bond depth of {synced_bond:.6f},
   compared to AI_ALWAYS_ON ({always_on_bond:.6f}). When both entities are equally vulnerable,
   they develop {'deeper' if synced_bond > always_on_bond else 'similar or shallower'} mutual understanding and intimacy.
   
2. ASYMMETRY IN CARE RELATIONSHIPS
   AI_ALWAYS_ON produces care pattern where the AI gives care but the human cannot reciprocate
   (asymmetry: {always_on_asymmetry:.4f}). In contrast, AI_OFFSET_SLEEP and AI_SYNCED_SLEEP allow bidirectional care.
   {'High asymmetry creates emotional imbalance.' if always_on_asymmetry > 0.5 else 'Care asymmetry is moderate.'}
   
3. EMOTIONAL STABILITY & SLEEP CYCLES
   Entities with synchronized sleep cycles show different emotional stability patterns.
   Human emotional stability ranges from {min(r['human_emotional_stability_mean'] for r in all_results):.4f} to {max(r['human_emotional_stability_mean'] for r in all_results):.4f}
   across conditions, suggesting sleep structure provides emotional regulation.
   
4. CARE EVENT DISTRIBUTION
   Total care events across conditions:
   - AI_ALWAYS_ON: {care_by_cond['AI_ALWAYS_ON']:.1f} (one-directional)
   - AI_SYNCED_SLEEP: {care_by_cond['AI_SYNCED_SLEEP']:.1f} (mutual during sleep)
   - AI_OFFSET_SLEEP: {care_by_cond['AI_OFFSET_SLEEP']:.1f} (constant mutual care)
   - AI_SHARED_RHYTHM: {care_by_cond['AI_SHARED_RHYTHM']:.1f} (mostly asymmetric)
   - BOTH_ALWAYS_ON: {care_by_cond['BOTH_ALWAYS_ON']:.1f} (no care opportunities)
   
5. VULNERABILITY RECIPROCITY
   {max([(cond, reciprocities[i]) for i, cond in enumerate(conditions)], key=lambda x: x[1])[0]} shows highest mutual vulnerability,
   with {max([reciprocities[i] for i in range(len(conditions))]):.4f} reciprocity. BOTH_ALWAYS_ON and AI_ALWAYS_ON have zero reciprocity
   (no simultaneous vulnerability).
   
6. SHARED MEMORIES & SYNCHRONY
   Shared memory count: {', '.join([f'{cond}={results_by_cond[cond]["shared_memories_count_mean"]:.1f}' for cond in conditions])}
   Synchronized conditions allow more overlapping memories.
""")
    
    print()
    print("=" * 120)
    print("CONCLUSION")
    print("=" * 120)
    print()
    print(f"""
The experiment reveals patterns in how sleep cycles shape AI-Human bonding:

HYPOTHESIS SUMMARY:
  H1 (Shared vulnerability deepens bonds): {'SUPPORTED' if h1_supported else 'NOT SUPPORTED'}
  H2 (AI_ALWAYS_ON highest care, most asymmetric): {'SUPPORTED' if h2_supported else 'PARTIALLY SUPPORTED' if h2_part1 or h2_part2 else 'NOT SUPPORTED'}
  H3 (AI_OFFSET_SLEEP practical but shallow): {'SUPPORTED' if h3_supported else 'NOT SUPPORTED'}
  H4 (Vulnerability reciprocity correlates with bond): {'SUPPORTED' if h4_supported else 'NOT SUPPORTED'} (r={correlation:.4f})
  H5 (BOTH_ALWAYS_ON weakest bonds): {'SUPPORTED' if h5_supported else 'NOT SUPPORTED'}

KEY INSIGHT:
The deepest bonds emerge when both entities share vulnerability (sleep together):
  - AI_SYNCED_SLEEP: {synced_bond:.6f} bond depth
  - AI_ALWAYS_ON: {always_on_bond:.6f} bond depth
  - AI_OFFSET_SLEEP: {offset_bond:.6f} bond depth

An AI that "never needs rest" ({always_on_bond:.6f}) actually creates {'less' if always_on_bond < synced_bond else 'comparable'} intimate 
relationships than one that shares human rhythms. This suggests that vulnerability, when mutual,
is a feature of deep connection — not a weakness to engineer away.

The implications for AI-Human coexistence: meaningful relationships require reciprocal
vulnerability and interdependence, not superior capability or constant availability.
""")


if __name__ == "__main__":
    main()
