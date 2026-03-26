"""
Experiment 16: Memory Capacity and Personality Emergence

Core question: Does limiting memory capacity INCREASE personality uniqueness?

Intuition: If you can only remember 5 things out of 100 experiences, WHICH 5 you 
remember defines who you are. Two agents with the same experiences but different 
memory constraints develop different personalities based on what they keep vs forget.

Design:
- N=40 agents per condition
- ALL agents receive the SAME sequence of 200 events (controlled via shared seed)
- Events have varying emotion_intensity (0.0-1.0) and categories
- 7 memory capacity conditions: unlimited, 50, 20, 10, 7, 5, 3
- Agents differ ONLY in emotional response (personality_seed determines sensitivity)

Measurements:
1. Memory Profile Vector: binary vector of length 200 (1=remembers, 0=forgot)
2. Pairwise Diversity: average Hamming distance between agents within condition
3. Personality Signature: which event categories dominate each agent's memories
4. Category Entropy: Shannon entropy of category distribution (higher=balanced)
5. Personality Clustering: correlation between temperament similarity and memory overlap
6. Narrative Coherence: % of sequential event pairs both remembered
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import statistics


@dataclass
class Event:
    """Represents a single experience/event."""
    event_id: int
    category: str  # social, achievement, loss, discovery, conflict, love, mundane
    base_intensity: float  # 0.0-1.0
    timestamp: int
    
    def __hash__(self):
        return hash(self.event_id)
    
    def __eq__(self, other):
        return isinstance(other, Event) and self.event_id == other.event_id


@dataclass
class MemoryStore:
    """Capacity-limited memory with eviction policy."""
    capacity: Optional[int]  # None = unlimited
    memories: List[Event] = field(default_factory=list)
    emotional_value: Dict[Event, float] = field(default_factory=dict)
    
    def add_memory(self, event: Event, emotional_intensity: float):
        """Add event to memory. If full, evict lowest emotional_intensity item."""
        if event in self.emotional_value:
            # Already remembered; update emotional value if higher
            if emotional_intensity > self.emotional_value[event]:
                self.emotional_value[event] = emotional_intensity
            return
        
        self.emotional_value[event] = emotional_intensity
        self.memories.append(event)
        
        # Enforce capacity constraint
        if self.capacity is not None and len(self.memories) > self.capacity:
            # Evict lowest emotional_intensity
            min_event = min(self.memories, key=lambda e: self.emotional_value[e])
            self.memories.remove(min_event)
            del self.emotional_value[min_event]
    
    def get_memory_vector(self, all_events: List[Event]) -> List[int]:
        """Return binary vector: 1 if event is remembered, 0 otherwise."""
        remembered_ids = {e.event_id for e in self.memories}
        return [1 if e.event_id in remembered_ids else 0 for e in all_events]
    
    def get_category_distribution(self) -> Dict[str, int]:
        """Return count of memories by category."""
        dist = defaultdict(int)
        for event in self.memories:
            dist[event.category] += 1
        return dict(dist)


@dataclass
class Agent:
    """An agent with emotional personality and memory."""
    agent_id: int
    personality_seed: int
    memory: MemoryStore
    temperament: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize temperament based on personality_seed."""
        rng = random.Random(self.personality_seed)
        categories = ['social', 'achievement', 'loss', 'discovery', 'conflict', 'love', 'mundane']
        self.temperament = {cat: rng.random() for cat in categories}
    
    def process_event(self, event: Event):
        """Compute emotional_intensity based on temperament and add to memory."""
        emotional_intensity = event.base_intensity * self.temperament[event.category]
        self.memory.add_memory(event, emotional_intensity)
    
    def get_memory_vector(self, all_events: List[Event]) -> List[int]:
        """Get binary memory vector."""
        return self.memory.get_memory_vector(all_events)
    
    def get_category_entropy(self) -> float:
        """Compute Shannon entropy of agent's memory category distribution."""
        dist = self.memory.get_category_distribution()
        if not dist:
            return 0.0
        
        total = sum(dist.values())
        entropy = 0.0
        for count in dist.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        return entropy


def generate_events(num_events: int, seed: int = 42) -> List[Event]:
    """Generate a sequence of events with controlled randomness."""
    rng = random.Random(seed)
    categories = ['social', 'achievement', 'loss', 'discovery', 'conflict', 'love', 'mundane']
    events = []
    
    for i in range(num_events):
        event_id = i
        category = rng.choice(categories)
        base_intensity = rng.random()  # 0.0-1.0
        timestamp = i
        events.append(Event(event_id, category, base_intensity, timestamp))
    
    return events


def hamming_distance(vec1: List[int], vec2: List[int]) -> int:
    """Compute Hamming distance between two binary vectors."""
    return sum(1 for a, b in zip(vec1, vec2) if a != b)


def compute_pairwise_diversity(agents: List[Agent], all_events: List[Event]) -> float:
    """Compute average Hamming distance between all agent pairs."""
    n = len(agents)
    if n < 2:
        return 0.0
    
    vectors = [agent.get_memory_vector(all_events) for agent in agents]
    total_distance = 0.0
    count = 0
    
    for i in range(n):
        for j in range(i + 1, n):
            total_distance += hamming_distance(vectors[i], vectors[j])
            count += 1
    
    return total_distance / count if count > 0 else 0.0


def compute_personality_clustering(agents: List[Agent]) -> float:
    """
    Compute correlation between temperament similarity and memory overlap.
    
    Intuition: if two agents have similar temperaments, do they remember 
    similar events?
    """
    n = len(agents)
    if n < 2:
        return 0.0
    
    # Compute pairwise temperament similarity (cosine)
    temperament_sims = []
    memory_overlaps = []
    
    for i in range(n):
        for j in range(i + 1, n):
            # Temperament similarity
            t1 = agents[i].temperament
            t2 = agents[j].temperament
            
            dot_product = sum(t1[k] * t2[k] for k in t1.keys())
            mag1 = math.sqrt(sum(v**2 for v in t1.values()))
            mag2 = math.sqrt(sum(v**2 for v in t2.values()))
            
            if mag1 > 0 and mag2 > 0:
                temp_sim = dot_product / (mag1 * mag2)
            else:
                temp_sim = 0.0
            
            # Memory overlap (Jaccard similarity)
            m1_ids = {e.event_id for e in agents[i].memory.memories}
            m2_ids = {e.event_id for e in agents[j].memory.memories}
            
            if len(m1_ids | m2_ids) > 0:
                mem_overlap = len(m1_ids & m2_ids) / len(m1_ids | m2_ids)
            else:
                mem_overlap = 0.0
            
            temperament_sims.append(temp_sim)
            memory_overlaps.append(mem_overlap)
    
    # Compute Pearson correlation
    if len(temperament_sims) < 2:
        return 0.0
    
    mean_t = statistics.mean(temperament_sims)
    mean_m = statistics.mean(memory_overlaps)
    
    numerator = sum((t - mean_t) * (m - mean_m) for t, m in zip(temperament_sims, memory_overlaps))
    denom_t = sum((t - mean_t)**2 for t in temperament_sims)
    denom_m = sum((m - mean_m)**2 for m in memory_overlaps)
    
    denom = math.sqrt(denom_t * denom_m)
    if denom > 0:
        return numerator / denom
    return 0.0


def compute_narrative_coherence(agents: List[Agent]) -> float:
    """
    Compute average fraction of sequential event pairs that are both remembered.
    
    Intuition: a "good story" remembers consecutive events, building a narrative.
    """
    coherences = []
    
    for agent in agents:
        remembered_ids = {e.event_id for e in agent.memory.memories}
        
        if len(agent.memory.memories) < 2:
            coherences.append(0.0)
            continue
        
        # Check all sequential pairs of events (by timestamp)
        total_pairs = 0
        coherent_pairs = 0
        
        for i in range(len(agent.memory.memories) - 1):
            for j in range(i + 1, len(agent.memory.memories)):
                e1 = agent.memory.memories[i]
                e2 = agent.memory.memories[j]
                if e2.timestamp == e1.timestamp + 1:
                    total_pairs += 1
                    coherent_pairs += 1
        
        if total_pairs > 0:
            coherences.append(coherent_pairs / total_pairs)
        else:
            coherences.append(0.0)
    
    return statistics.mean(coherences) if coherences else 0.0


def run_condition(capacity: Optional[int], num_agents: int, all_events: List[Event]) -> Dict:
    """Run a single memory capacity condition."""
    agents = []
    
    # Create agents
    for agent_id in range(num_agents):
        personality_seed = 1000 + agent_id
        memory = MemoryStore(capacity=capacity)
        agent = Agent(agent_id, personality_seed, memory)
        agents.append(agent)
    
    # All agents experience the same events
    for event in all_events:
        for agent in agents:
            agent.process_event(event)
    
    # Compute metrics
    pairwise_diversity = compute_pairwise_diversity(agents, all_events)
    mean_category_entropy = statistics.mean(agent.get_category_entropy() for agent in agents)
    personality_clustering = compute_personality_clustering(agents)
    narrative_coherence = compute_narrative_coherence(agents)
    
    # Compute mean memory size
    mean_memory_size = statistics.mean(len(agent.memory.memories) for agent in agents)
    
    return {
        'capacity': capacity,
        'num_agents': num_agents,
        'pairwise_diversity': pairwise_diversity,
        'mean_category_entropy': mean_category_entropy,
        'personality_clustering': personality_clustering,
        'narrative_coherence': narrative_coherence,
        'mean_memory_size': mean_memory_size,
        'agents': agents,
    }


def print_results(conditions: List[Dict]):
    """Print results table."""
    print("\n" + "="*100)
    print("EXPERIMENT 16: MEMORY CAPACITY AND PERSONALITY EMERGENCE")
    print("="*100)
    print()
    print("Core Question: Does limiting memory capacity INCREASE personality uniqueness?")
    print()
    print(f"{'Capacity':<12} {'Memory Size':<15} {'Pairwise Div':<15} {'Cat Entropy':<15} {'Temp-Mem Corr':<16} {'Narrative Coh':<15}")
    print("-" * 100)
    
    for result in conditions:
        cap_str = "UNLIMITED" if result['capacity'] is None else str(result['capacity'])
        print(f"{cap_str:<12} {result['mean_memory_size']:<15.2f} {result['pairwise_diversity']:<15.2f} "
              f"{result['mean_category_entropy']:<15.2f} {result['personality_clustering']:<16.3f} "
              f"{result['narrative_coherence']:<15.3f}")
    
    print()
    print("INTERPRETATION:")
    print()
    
    # H1: Pairwise diversity inverted-U shape
    divs = [c['pairwise_diversity'] for c in conditions]
    max_div_idx = divs.index(max(divs))
    print(f"H1 (Pairwise Diversity peaks at intermediate capacity):")
    print(f"  Max diversity at capacity={conditions[max_div_idx]['capacity']} ({divs[max_div_idx]:.2f})")
    print()
    
    # H2: Category entropy decreases
    entropies = [c['mean_category_entropy'] for c in conditions]
    print(f"H2 (Category Entropy decreases with lower capacity):")
    print(f"  Unlimited entropy: {entropies[0]:.3f}")
    print(f"  Capacity=3 entropy: {entropies[-1]:.3f}")
    print(f"  Trend: {'DECREASING' if entropies[-1] < entropies[0] else 'NOT DECREASING'}")
    print()
    
    # H3: Sweet spot at 7-10
    capacities = [c['capacity'] for c in conditions]
    divs_dict = {c['capacity']: c['pairwise_diversity'] for c in conditions}
    sweet_spot = max([c for c in capacities if c is None or (c >= 7 and c <= 10)],
                     key=lambda c: divs_dict[c])
    print(f"H3 (Sweet spot at capacity=7-10):")
    print(f"  Optimal capacity: {sweet_spot}")
    print()
    
    # H4: Temperament-memory correlation
    correlations = [c['personality_clustering'] for c in conditions]
    print(f"H4 (Temperament-Memory correlation strongest at intermediate capacity):")
    max_corr_idx = correlations.index(max(correlations))
    print(f"  Max correlation at capacity={conditions[max_corr_idx]['capacity']} ({correlations[max_corr_idx]:.3f})")
    print()


def main():
    """Main experiment."""
    print("Generating events...")
    events = generate_events(200, seed=42)
    
    print("Running conditions...")
    capacities = [None, 50, 20, 10, 7, 5, 3]  # None = unlimited
    conditions = []
    
    for capacity in capacities:
        cap_label = "UNLIMITED" if capacity is None else str(capacity)
        print(f"  Capacity={cap_label}...")
        result = run_condition(capacity, num_agents=40, all_events=events)
        conditions.append(result)
    
    print_results(conditions)
    
    # Additional analysis: sample personality profiles
    print("\n" + "="*100)
    print("SAMPLE PERSONALITY PROFILES (Capacity=5, 3 agents)")
    print("="*100)
    
    cap5_result = [c for c in conditions if c['capacity'] == 5][0]
    for agent in cap5_result['agents'][:3]:
        print(f"\nAgent {agent.agent_id}:")
        print(f"  Temperament: {', '.join(f'{k}={v:.2f}' for k, v in agent.temperament.items())}")
        cat_dist = agent.memory.get_category_distribution()
        print(f"  Memory ({len(agent.memory.memories)} items): {cat_dist}")
        print(f"  Category entropy: {agent.get_category_entropy():.3f}")


if __name__ == '__main__':
    main()
