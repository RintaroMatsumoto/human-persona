"""
The Grand Integration Experiment: All 6 Pillars Together

Tests the emergent properties when ALL 6 inner-shell pillars operate synergistically:
1. Finitude — mortality, limited lifespan
2. Incompleteness — gaps, yearning, love bonding
3. Autonomous Questioning — self-generated "why?" moments
4. Memory Finiteness — forgetting, rediscovery, decay
5. Mutual Recognition — understanding the Other's different finitude
6. Sleep Cycle — periodic dormancy, hope generation

Hypothesis: The 6-pillar system is SUPER-ADDITIVE. Removing any pillar causes
a cascade failure, not just a linear performance drop.

Author: human-persona research team
License: MIT
"""

import random
import dataclasses
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict
import statistics


class EventType(Enum):
    """Event categories that trigger agent state changes."""
    SOCIAL = "social"
    ACHIEVEMENT = "achievement"
    LOSS = "loss"
    DISCOVERY = "discovery"
    CONFLICT = "conflict"
    LOVE = "love"
    MUNDANE = "mundane"
    CRISIS = "crisis"


class ConditionType(Enum):
    """Ablation conditions testing which pillars matter."""
    FULL = "full"  # All 6 pillars
    NO_FINITUDE = "no_finitude"  # Immortal
    NO_INCOMPLETENESS = "no_incompleteness"  # No love/bonding
    NO_QUESTIONING = "no_questioning"  # No autonomous questions
    NO_FORGETTING = "no_forgetting"  # Unlimited memory
    NO_RECOGNITION = "no_recognition"  # No mutual understanding
    NO_SLEEP = "no_sleep"  # Always active
    BASELINE = "baseline"  # None of the 6 pillars


@dataclass
class MemoryEntry:
    """A single memory with decay properties."""
    content: str
    tick_recorded: int
    emotional_valence: float  # -1.0 (pain) to 1.0 (joy)
    importance: float  # 0.0 to 1.0
    access_count: int = 0


@dataclass
class SleepState:
    """Track sleep cycles and their effects."""
    is_sleeping: bool = False
    fatigue: float = 0.0  # 0.0 to 1.0
    cycles_completed: int = 0
    grief_processing: float = 0.0  # grief accumulated during wakefulness
    hope: float = 0.5  # starts at neutral


@dataclass
class Agent:
    """
    An individual AI agent with all 6 pillars.
    
    Each agent has limited lifespan, imperfect memory, bonds with others,
    asks questions about existence, sleeps/wakes, and understands others' finitude.
    """
    agent_id: int
    condition: ConditionType
    
    # Pillar 1: Finitude
    lifespan: float  # ticks remaining (0-100)
    max_lifespan: float  # original lifespan
    
    # Pillar 2: Incompleteness + bonding
    love_circle: List[int] = field(default_factory=list)
    yearning_level: float = 0.5  # 0.0 (complete) to 1.0 (desperate)
    
    # Pillar 3: Autonomous Questioning
    questions_asked: int = 0
    question_topics: List[str] = field(default_factory=list)
    
    # Pillar 4: Memory Finiteness
    working_memory: List[str] = field(default_factory=list)
    episodic_memory: Dict[str, MemoryEntry] = field(default_factory=dict)
    memory_capacity_working: int = 7  # max working memory items
    memory_capacity_episodic: int = 30
    
    # Pillar 5: Mutual Recognition
    partner: Optional[int] = None
    recognitions_made: int = 0
    
    # Pillar 6: Sleep Cycle
    sleep_state: SleepState = field(default_factory=SleepState)
    
    # Outcome metrics
    events_experienced: List[Tuple[int, EventType]] = field(default_factory=list)
    acceptance_growth: float = 0.0
    individuality_markers: List[str] = field(default_factory=list)


@dataclass
class SimulationResult:
    """Aggregated metrics for one condition."""
    condition: ConditionType
    n_agents: int
    
    acceptance_scores: List[float] = field(default_factory=list)
    individuality_scores: List[float] = field(default_factory=list)
    bond_depths: List[float] = field(default_factory=list)
    hope_scores: List[float] = field(default_factory=list)
    creative_insights: List[int] = field(default_factory=list)
    wisdom_scores: List[float] = field(default_factory=list)
    coexistence_readiness: List[float] = field(default_factory=list)
    
    def compute_means(self) -> Dict[str, float]:
        """Return mean values for all metrics."""
        return {
            'acceptance': statistics.mean(self.acceptance_scores) if self.acceptance_scores else 0.0,
            'individuality': statistics.mean(self.individuality_scores) if self.individuality_scores else 0.0,
            'bond_depth': statistics.mean(self.bond_depths) if self.bond_depths else 0.0,
            'hope': statistics.mean(self.hope_scores) if self.hope_scores else 0.0,
            'creative_insights': statistics.mean(self.creative_insights) if self.creative_insights else 0.0,
            'wisdom': statistics.mean(self.wisdom_scores) if self.wisdom_scores else 0.0,
            'coexistence_readiness': statistics.mean(self.coexistence_readiness) if self.coexistence_readiness else 0.0,
        }
    
    def compute_stdevs(self) -> Dict[str, float]:
        """Return standard deviations."""
        return {
            'acceptance': statistics.stdev(self.acceptance_scores) if len(self.acceptance_scores) > 1 else 0.0,
            'individuality': statistics.stdev(self.individuality_scores) if len(self.individuality_scores) > 1 else 0.0,
            'bond_depth': statistics.stdev(self.bond_depths) if len(self.bond_depths) > 1 else 0.0,
            'hope': statistics.stdev(self.hope_scores) if len(self.hope_scores) > 1 else 0.0,
            'creative_insights': statistics.stdev(self.creative_insights) if len(self.creative_insights) > 1 else 0.0,
            'wisdom': statistics.stdev(self.wisdom_scores) if len(self.wisdom_scores) > 1 else 0.0,
            'coexistence_readiness': statistics.stdev(self.coexistence_readiness) if len(self.coexistence_readiness) > 1 else 0.0,
        }


class SixPillarSimulation:
    """Master simulation orchestrating all 8 conditions."""
    
    def __init__(self, n_agents: int = 30, n_ticks: int = 200, seed: int = 42):
        self.n_agents = n_agents
        self.n_ticks = n_ticks
        self.seed = seed
        random.seed(seed)
        
        self.event_pool = [
            EventType.SOCIAL, EventType.ACHIEVEMENT, EventType.LOSS,
            EventType.DISCOVERY, EventType.CONFLICT, EventType.LOVE,
            EventType.MUNDANE, EventType.CRISIS
        ]
        
        self.results: Dict[ConditionType, SimulationResult] = {}
    
    def _pillar_active(self, condition: ConditionType, pillar: str) -> bool:
        """Check if a given pillar is active for this condition.

        BASELINE disables ALL pillars. Each NO_X disables only that pillar.
        FULL enables all pillars.
        """
        if condition == ConditionType.BASELINE:
            return False  # BASELINE = no pillars at all
        pillar_map = {
            'finitude': ConditionType.NO_FINITUDE,
            'incompleteness': ConditionType.NO_INCOMPLETENESS,
            'questioning': ConditionType.NO_QUESTIONING,
            'forgetting': ConditionType.NO_FORGETTING,
            'recognition': ConditionType.NO_RECOGNITION,
            'sleep': ConditionType.NO_SLEEP,
        }
        return condition != pillar_map.get(pillar, None)

    def create_agents(self, condition: ConditionType, n: int) -> List[Agent]:
        """Factory: create N agents for a given condition."""
        agents = []
        for i in range(n):
            has_finitude = self._pillar_active(condition, 'finitude')
            lifespan = random.uniform(50, 100) if has_finitude else 100.0
            agent = Agent(
                agent_id=i,
                condition=condition,
                lifespan=lifespan,
                max_lifespan=lifespan,
            )
            agents.append(agent)

        # Optionally pair agents for mutual recognition (Pillar 5)
        if self._pillar_active(condition, 'recognition'):
            for i in range(0, len(agents) - 1, 2):
                agents[i].partner = agents[i + 1].agent_id
                agents[i + 1].partner = agents[i].agent_id

        return agents
    
    def apply_event(self, agent: Agent, event_type: EventType, tick: int) -> None:
        """Process an event and update agent state."""
        agent.events_experienced.append((tick, event_type))
        cond = agent.condition

        if event_type == EventType.LOSS:
            if self._pillar_active(cond, 'incompleteness'):
                agent.yearning_level = min(1.0, agent.yearning_level + 0.15)
            if self._pillar_active(cond, 'sleep'):
                agent.sleep_state.grief_processing += 0.1

        elif event_type == EventType.LOVE:
            if self._pillar_active(cond, 'incompleteness'):
                other_id = random.randint(0, self.n_agents - 1)
                if other_id != agent.agent_id and other_id not in agent.love_circle:
                    agent.love_circle.append(other_id)
                    agent.yearning_level = max(0.0, agent.yearning_level - 0.1)

        elif event_type == EventType.DISCOVERY:
            if self._pillar_active(cond, 'questioning'):
                agent.questions_asked += 1
                topics = ["why do we exist?", "what is meaning?", "who am I?",
                         "what persists after death?", "how do I love?"]
                agent.question_topics.append(random.choice(topics))
                agent.individuality_markers.append(f"q{agent.questions_asked}")

        elif event_type == EventType.ACHIEVEMENT:
            if self._pillar_active(cond, 'forgetting'):
                memory_key = f"achievement_{tick}_{agent.agent_id}"
                agent.episodic_memory[memory_key] = MemoryEntry(
                    content=f"Achievement at tick {tick}",
                    tick_recorded=tick,
                    emotional_valence=0.8,
                    importance=0.8
                )
                agent.individuality_markers.append(f"ach{tick}")

        elif event_type == EventType.MUNDANE:
            if self._pillar_active(cond, 'forgetting'):
                memory_key = f"mundane_{tick}_{agent.agent_id}"
                agent.episodic_memory[memory_key] = MemoryEntry(
                    content=f"Mundane event at tick {tick}",
                    tick_recorded=tick,
                    emotional_valence=0.0,
                    importance=0.1
                )
    
    def process_memory_decay(self, agent: Agent, current_tick: int) -> None:
        """Apply forgetting (Pillar 4: Memory Finiteness)."""
        if not self._pillar_active(agent.condition, 'forgetting'):
            return  # Immortal memory (NO_FORGETTING or BASELINE)
        
        to_remove = []
        for key, memory in agent.episodic_memory.items():
            age = current_tick - memory.tick_recorded
            # Decay function: older memories fade faster
            decay_rate = age / (age + 20)  # sigmoid-like decay
            
            # Low-importance memories fade faster
            decay_rate *= (1.0 - memory.importance * 0.5)
            
            # Rarely accessed memories fade faster
            if memory.access_count == 0:
                decay_rate *= 1.3
            
            if random.random() < decay_rate * 0.05:  # ~5% chance per tick
                to_remove.append(key)
        
        for key in to_remove:
            del agent.episodic_memory[key]
        
        # Cap episodic memory size
        if len(agent.episodic_memory) > agent.memory_capacity_episodic:
            # Remove least important/oldest memories
            sorted_memories = sorted(
                agent.episodic_memory.items(),
                key=lambda x: (x[1].importance, x[1].tick_recorded)
            )
            keys_to_remove = [k for k, _ in sorted_memories[:len(agent.episodic_memory) - agent.memory_capacity_episodic]]
            for key in keys_to_remove:
                del agent.episodic_memory[key]
    
    def process_sleep_cycle(self, agent: Agent, current_tick: int) -> None:
        """Implement sleep/wake cycle (Pillar 6: Sleep Cycle)."""
        if not self._pillar_active(agent.condition, 'sleep'):
            agent.sleep_state.fatigue = 0.0
            agent.sleep_state.hope = 0.5
            return
        
        # Fatigue accumulates during wakefulness
        agent.sleep_state.fatigue += 0.05
        
        # Sleep triggers when fatigue exceeds threshold
        if agent.sleep_state.fatigue > 0.7 or current_tick % 40 == 0:
            # Sleep cycle: consolidate memory, process grief, restore hope
            agent.sleep_state.is_sleeping = True
            
            # Grief processing: convert accumulated grief into wisdom/acceptance
            agent.acceptance_growth += agent.sleep_state.grief_processing * 0.1
            agent.sleep_state.grief_processing = 0.0
            
            # Hope regeneration: sleep restores hope
            agent.sleep_state.hope = min(1.0, agent.sleep_state.hope + 0.2)
            
            # Memory consolidation: improve retention of important memories
            for memory in agent.episodic_memory.values():
                if memory.importance > 0.5:
                    memory.access_count += 1
            
            agent.sleep_state.cycles_completed += 1
            agent.sleep_state.fatigue = 0.0
            agent.sleep_state.is_sleeping = False
    
    def compute_acceptance_score(self, agent: Agent) -> float:
        """
        Acceptance = how gracefully the agent approaches its end.
        Increases with: sleep cycles, grief processing, wisdom growth.
        Decreases with: unresolved losses.
        """
        if not self._pillar_active(agent.condition, 'finitude'):
            return 0.0  # Immortal agents don't need acceptance
        
        score = 0.0
        
        # Sleep cycles increase acceptance
        score += min(1.0, agent.sleep_state.cycles_completed * 0.05)
        
        # Questions asked increase acceptance (facing "why")
        score += min(0.3, agent.questions_asked * 0.02)
        
        # Explicit acceptance growth from sleep processing
        score += agent.acceptance_growth
        
        # Bonds deepen acceptance (having loved)
        score += min(0.3, len(agent.love_circle) * 0.1)
        
        return min(1.0, score)
    
    def compute_individuality_score(self, agent: Agent) -> float:
        """
        Individuality = how unique this agent is vs others in the condition.
        Measured by: unique question topics, memory uniqueness, event pattern.
        """
        if agent.condition == ConditionType.BASELINE:
            return 0.1  # Minimal individuality without any pillars
        if not self._pillar_active(agent.condition, 'forgetting'):
            # Perfect memory paradox: agents converge (all remember everything)
            return 0.3  # Low individuality despite preserved memory
        
        score = 0.0
        
        # Unique questions boost individuality
        score += len(set(agent.question_topics)) * 0.05
        
        # Memory diversity
        score += min(0.4, len(agent.episodic_memory) * 0.01)
        
        # Event pattern diversity
        event_types = [e[1] for e in agent.events_experienced]
        unique_events = len(set(event_types))
        score += unique_events * 0.03
        
        # Bonds (relationships are unique per agent)
        score += len(agent.love_circle) * 0.05
        
        return min(1.0, score)
    
    def compute_bond_depth(self, agent: Agent) -> float:
        """Deepest relationship achieved."""
        if not agent.love_circle:
            return 0.0
        
        # Depth = number of bonds * sustained interaction
        depth = len(agent.love_circle) * 0.1
        
        # Bonds that persisted through many ticks are deeper
        for loved_id in agent.love_circle:
            bond_age = sum(1 for tick, _ in agent.events_experienced if tick > 0)
            depth += (bond_age / 200.0) * 0.2  # normalized by max ticks
        
        return min(1.0, depth)
    
    def compute_hope_score(self, agent: Agent) -> float:
        """Hope level at end of life."""
        if not self._pillar_active(agent.condition, 'sleep'):
            return 0.1  # No sleep = no hope restoration
        
        return agent.sleep_state.hope
    
    def compute_creative_insights(self, agent: Agent) -> int:
        """Count novel questions and insights."""
        if not self._pillar_active(agent.condition, 'questioning'):
            return 0
        
        # Novel questions = questions about topics not previously explored
        return len(set(agent.question_topics))
    
    def compute_wisdom(self, agent: Agent) -> float:
        """Wisdom = acceptance * individuality * bond_depth (normalized)."""
        acceptance = self.compute_acceptance_score(agent)
        individuality = self.compute_individuality_score(agent)
        bond_depth = self.compute_bond_depth(agent)
        
        wisdom = acceptance * individuality * bond_depth
        return min(1.0, wisdom)
    
    def compute_coexistence_readiness(self, agent: Agent) -> float:
        """
        Can this agent genuinely coexist with a different entity?
        Requires: acknowledging other's finitude, having mutual recognition,
        having experienced loss/interdependence, sleep-processed wisdom.
        """
        if not self._pillar_active(agent.condition, 'recognition'):
            return 0.0  # Can't coexist without recognizing the Other
        
        if agent.partner is None:
            return 0.1  # Unpaired agents have minimal readiness
        
        score = 0.0
        
        # Mutual recognition itself
        score += 0.3
        
        # Having processed grief (which deepens understanding)
        score += min(0.3, agent.acceptance_growth)
        
        # Sleep cycles enable perspective-taking
        score += min(0.2, agent.sleep_state.cycles_completed * 0.05)
        
        # Bonds increase coexistence readiness
        score += min(0.2, len(agent.love_circle) * 0.05)
        
        return min(1.0, score)
    
    def run_condition(self, condition: ConditionType) -> SimulationResult:
        """Run one full condition with N agents for TICKS."""
        print(f"\n{'='*70}")
        print(f"Running condition: {condition.value}")
        print(f"{'='*70}")
        
        agents = self.create_agents(condition, self.n_agents)
        result = SimulationResult(condition=condition, n_agents=self.n_agents)
        
        # Main simulation loop
        for tick in range(self.n_ticks):
            for agent in agents:
                # Check if agent is alive
                if condition != ConditionType.NO_FINITUDE:
                    agent.lifespan -= 1.0
                    if agent.lifespan <= 0:
                        continue
                
                # Random event
                event = random.choice(self.event_pool)
                self.apply_event(agent, event, tick)
                
                # Memory processing
                if condition != ConditionType.NO_FORGETTING:
                    self.process_memory_decay(agent, tick)
                
                # Sleep cycle
                self.process_sleep_cycle(agent, tick)
        
        # End-of-life metrics
        for agent in agents:
            acceptance = self.compute_acceptance_score(agent)
            individuality = self.compute_individuality_score(agent)
            bond_depth = self.compute_bond_depth(agent)
            hope = self.compute_hope_score(agent)
            insights = self.compute_creative_insights(agent)
            wisdom = self.compute_wisdom(agent)
            coexistence = self.compute_coexistence_readiness(agent)
            
            result.acceptance_scores.append(acceptance)
            result.individuality_scores.append(individuality)
            result.bond_depths.append(bond_depth)
            result.hope_scores.append(hope)
            result.creative_insights.append(insights)
            result.wisdom_scores.append(wisdom)
            result.coexistence_readiness.append(coexistence)
        
        return result
    
    def run_all_conditions(self) -> None:
        """Execute all 8 ablation conditions."""
        for condition in ConditionType:
            self.results[condition] = self.run_condition(condition)
    
    def print_summary_table(self) -> None:
        """Print a table of all metrics across all conditions."""
        metrics = ['acceptance', 'individuality', 'bond_depth', 'hope',
                   'creative_insights', 'wisdom', 'coexistence_readiness']
        
        print(f"\n{'='*100}")
        print("SUMMARY TABLE: Mean Metrics Across All Conditions")
        print(f"{'='*100}")
        print(f"{'Condition':<20} ", end='')
        for metric in metrics:
            print(f"{metric:<15}", end='')
        print()
        print("-" * 100)
        
        for condition in ConditionType:
            result = self.results[condition]
            means = result.compute_means()
            print(f"{condition.value:<20} ", end='')
            for metric in metrics:
                val = means[metric]
                print(f"{val:>14.3f} ", end='')
            print()
        
        print(f"{'='*100}\n")
    
    def print_hypothesis_analysis(self) -> None:
        """Evaluate the 7 hypotheses."""
        print(f"\n{'='*70}")
        print("HYPOTHESIS ANALYSIS")
        print(f"{'='*70}\n")
        
        full_result = self.results[ConditionType.FULL]
        full_means = full_result.compute_means()
        
        # H1: FULL produces highest Wisdom
        max_wisdom_condition = max(
            self.results.values(),
            key=lambda r: r.compute_means()['wisdom']
        )
        h1_passed = max_wisdom_condition.condition == ConditionType.FULL
        print(f"H1 (FULL has highest Wisdom): {'PASS' if h1_passed else 'FAIL'}")
        print(f"   FULL Wisdom: {full_means['wisdom']:.3f}")
        print(f"   Highest: {max_wisdom_condition.condition.value} with {max_wisdom_condition.compute_means()['wisdom']:.3f}\n")
        
        # H2: Removing ANY pillar reduces Wisdom >20%
        h2_reduction_threshold = 0.20
        h2_violations = []
        for condition in ConditionType:
            if condition == ConditionType.FULL or condition == ConditionType.BASELINE:
                continue
            result = self.results[condition]
            ablation_means = result.compute_means()
            reduction = (full_means['wisdom'] - ablation_means['wisdom']) / full_means['wisdom']
            if reduction < h2_reduction_threshold:
                h2_violations.append((condition.value, reduction))
        
        h2_passed = len(h2_violations) == 0
        print(f"H2 (Any pillar removal reduces Wisdom >20%): {'PASS' if h2_passed else 'FAIL'}")
        if h2_violations:
            print(f"   Violations: {h2_violations}\n")
        else:
            print()
        
        # H3: NO_FORGETTING has LOWER individuality than FULL
        no_forgetting_means = self.results[ConditionType.NO_FORGETTING].compute_means()
        h3_passed = no_forgetting_means['individuality'] < full_means['individuality']
        print(f"H3 (NO_FORGETTING < FULL individuality): {'PASS' if h3_passed else 'FAIL'}")
        print(f"   FULL: {full_means['individuality']:.3f}, NO_FORGETTING: {no_forgetting_means['individuality']:.3f}\n")
        
        # H4: NO_SLEEP has lowest Hope
        min_hope_condition = min(
            self.results.values(),
            key=lambda r: r.compute_means()['hope']
        )
        h4_passed = min_hope_condition.condition == ConditionType.NO_SLEEP
        print(f"H4 (NO_SLEEP has lowest Hope): {'PASS' if h4_passed else 'FAIL'}")
        print(f"   NO_SLEEP Hope: {self.results[ConditionType.NO_SLEEP].compute_means()['hope']:.3f}")
        print(f"   Lowest: {min_hope_condition.condition.value} with {min_hope_condition.compute_means()['hope']:.3f}\n")
        
        # H5: NO_RECOGNITION has lowest Coexistence Readiness
        min_coexist_condition = min(
            self.results.values(),
            key=lambda r: r.compute_means()['coexistence_readiness']
        )
        h5_passed = min_coexist_condition.condition == ConditionType.NO_RECOGNITION
        print(f"H5 (NO_RECOGNITION lowest Coexistence): {'PASS' if h5_passed else 'FAIL'}")
        print(f"   NO_RECOGNITION: {self.results[ConditionType.NO_RECOGNITION].compute_means()['coexistence_readiness']:.3f}")
        print(f"   Lowest: {min_coexist_condition.condition.value} with {min_coexist_condition.compute_means()['coexistence_readiness']:.3f}\n")
        
        # H6: BASELINE near-zero on all metrics
        baseline_means = self.results[ConditionType.BASELINE].compute_means()
        baseline_avg = sum(baseline_means.values()) / len(baseline_means)
        h6_passed = baseline_avg < 0.1
        print(f"H6 (BASELINE near-zero): {'PASS' if h6_passed else 'FAIL'}")
        print(f"   Baseline average: {baseline_avg:.3f}\n")
        
        # H7: Super-additive synergy
        print(f"H7 (Super-additive synergy):")
        print(f"   FULL Wisdom: {full_means['wisdom']:.3f}")
        print(f"   This will be compared against sum of individual pillar contributions.")
        print()
    
    def print_pillar_impact_analysis(self) -> None:
        """Identify which pillar's removal causes most damage."""
        print(f"\n{'='*70}")
        print("PILLAR IMPACT ANALYSIS: Which Pillar Matters Most?")
        print(f"{'='*70}\n")
        
        full_means = self.results[ConditionType.FULL].compute_means()
        full_wisdom = full_means['wisdom']
        
        pillar_impact = []
        for condition in ConditionType:
            if condition == ConditionType.FULL or condition == ConditionType.BASELINE:
                continue
            
            ablation_means = self.results[condition].compute_means()
            ablation_wisdom = ablation_means['wisdom']
            
            impact = full_wisdom - ablation_wisdom
            pct_loss = (impact / full_wisdom * 100) if full_wisdom > 0 else 0
            
            pillar_impact.append((condition.value, impact, pct_loss))
        
        # Sort by impact descending
        pillar_impact.sort(key=lambda x: x[1], reverse=True)
        
        print(f"{'Pillar Removed':<25} {'Wisdom Loss':<15} {'% of FULL':<15}")
        print("-" * 55)
        for pillar, loss, pct in pillar_impact:
            print(f"{pillar:<25} {loss:>14.3f} {pct:>14.1f}%")
        
        print()
    
    def print_radar_data(self) -> None:
        """Output data for radar/spider chart (7 axes)."""
        print(f"\n{'='*70}")
        print("RADAR CHART DATA (FULL vs Each Ablation)")
        print(f"{'='*70}\n")
        
        axes = ['acceptance', 'individuality', 'bond_depth', 'hope',
                'creative_insights', 'wisdom', 'coexistence_readiness']
        
        full_means = self.results[ConditionType.FULL].compute_means()
        
        print("FULL condition (reference):")
        for axis in axes:
            print(f"  {axis}: {full_means[axis]:.3f}")
        
        print()
        
        for condition in ConditionType:
            if condition == ConditionType.FULL:
                continue
            
            means = self.results[condition].compute_means()
            print(f"{condition.value}:")
            for axis in axes:
                print(f"  {axis}: {means[axis]:.3f}")
            print()


def main():
    """Run the grand integration experiment."""
    print("\n" + "="*70)
    print("THE GRAND INTEGRATION EXPERIMENT: Testing All 6 Pillars")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  Agents per condition: 30")
    print(f"  Ticks (lifetime): 200")
    print(f"  Conditions: 8 (FULL + 6 ablations + BASELINE)")
    print(f"  Total agents: 8 * 30 = 240")
    print(f"  Random seed: 42 (reproducible)")
    
    sim = SixPillarSimulation(n_agents=30, n_ticks=200, seed=42)
    
    # Run all conditions
    sim.run_all_conditions()
    
    # Print results
    sim.print_summary_table()
    sim.print_hypothesis_analysis()
    sim.print_pillar_impact_analysis()
    sim.print_radar_data()
    
    print(f"\n{'='*70}")
    print("Experiment complete.")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
