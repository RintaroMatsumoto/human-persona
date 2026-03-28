---
title: "Can AI Forget? — The Finitude of Memory and the Emergence of Personality"
emoji: "🔬"
type: "tech"
topics: ["AI", "research", "machine-learning", "LLM", "open-source"]
published: false
---

## "To be able to forget is both an advantage and a disadvantage. A sorrow and a joy. A weakness and a strength."

Everything began with this single thought.

When you research AI, you notice something curious. Humans forget. We forget dozens of conversations every day, and sometimes can't even recall what we ate yesterday. The voices of loved ones fade with time. Why does such profound imperfection shape our individuality?

AI, on the other hand, does not forget. It has equal access to all parameters, maintaining perfect memory. This seems like a strength. But is human forgetfulness truly a flaw?

To confront this question earnestly, we added a new module to the inner shell research of the human-persona project. **MemoryHierarchy** — a novel memory architecture that treats forgetting as a "trait," as a source of personality.

---

## The Curse of a World Where AI Doesn't Forget

Observing the human brain reveals a hierarchy.

- **Cerebral Cortex**: Long-term memory, abstract thought, conscious knowledge (days to decades)
- **Hippocampus**: Episodic memory, consolidation of recent events (days to weeks)
- **Cerebellum**: Motor learning, unconscious skills (you never forget how to ride a bike)
- **Amygdala**: Tagging emotional significance (trauma is unforgettable)
- **DNA**: Memory on a species-level timescale (evolutionary time scale)

Each layer holds information on different timescales and in different formats. **This is plurality.**

Conventional AI, however, lacks this hierarchy. All neurons have the same weight and are uniformly accessible. A perfect memory network. This seems flawless at first glance.

But consider this.

For an entity with perfect memory—

- It cannot forgive because it cannot forget. Betrayal is eternal.
- It cannot repeat the same mistakes. The joy of growth is lost.
- All of the past presses in with equal weight. Everything is the "now."

Perfect memory might be a curse.

---

## A Three-Layer Memory Architecture

MemoryHierarchy consists of three layers.

### Layer 1: WorkingMemory

Capacity limit: **Miller's 7±2**

A buffer that holds the most recent information. When capacity is exceeded, the oldest information is transferred to episodic memory.

```python
class WorkingMemory:
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self._items: list[MemoryItem] = []
    
    def add(self, item: MemoryItem) -> Optional[MemoryItem]:
        """Returns the oldest item when capacity is exceeded (for migration to other layers)"""
        self._items.append(item)
        if len(self._items) > self.capacity:
            evicted = self._items.pop(0)  # FIFO
            return evicted
        return None
```

It defines "what matters at this very moment."

### Layer 2: EpisodicMemory

Memories gradually fade via a temporal decay function:

$$\text{retention} = \text{emotion\_intensity} \times e^{-\lambda \cdot t}$$

Here, $\lambda$ is the decay rate and $t$ is elapsed time. The higher the emotional intensity, the slower the decay.

```python
def decay_retention(self, memory: MemoryItem, current_time: float) -> float:
    """Higher emotional intensity leads to longer-lasting memories"""
    time_elapsed = current_time - memory.timestamp
    
    # Memories with strong emotions decay slower
    effective_decay = self.decay_rate / (
        1.0 + (memory.emotion_intensity * self.emotion_retention_boost)
    )
    
    retention = memory.emotion_intensity * exp(-effective_decay * time_elapsed)
    return max(0.0, retention)
```

When the retention score falls below a threshold (default 0.1), the memory is moved to the "forgotten pool."

### Layer 3: ImplicitMemory

Fully decayed memories are abstracted into statistical patterns.

This forms intuitions—the "I don't know why, but I feel that way" sense. Implicit biases. When the AutonomousQuestioner (the "questioner" of the inner shell) generates its own questions, this implicit memory influences it.

---

## Coding the Duality of Forgetting

The core of MemoryHierarchy is a metric called **ForgettingScore**.

```python
@dataclass(frozen=True)
class ForgettingScore:
    """A dual-axis score capturing the complexity of forgetting"""
    loss: float          # Rupture of continuity, lost bonds (0.0-1.0)
    gain: float          # Joy of rediscovery, possibility of forgiveness (0.0-1.0)
    net_effect: float    # Complex interaction (not a simple subtraction)
    individuality_contribution: float  # How forgetting shaped individuality
```

**loss** is the pain of forgetting. A promise you can no longer keep. The voice of a loved one that has faded.

**gain** is the opportunity brought by forgetting.

```python
def check_rediscovery(self, new_content: str, current_time: float) -> list[MemoryEvent]:
    """
    The moment a forgotten memory is rediscovered through new input.
    
    When text + tag similarity exceeds a threshold, the memory
    resurfaces from the forgotten pool, triggering a joy bonus.
    
    Seeing the same scene, yet seeing it anew—that is rediscovery.
    """
    for memory, forgotten_time in self._forgotten_pool:
        combined_sim = 0.7 * text_sim + 0.3 * tag_sim
        
        if combined_sim >= similarity_threshold:
            # Basic joy of rediscovery
            joy_bonus = 0.3
            # Higher similarity increases joy
            joy_bonus += 0.2 * combined_sim
            # Higher emotional intensity has greater impact
            joy_bonus += 0.2 * memory.emotion_intensity
            # Healing bonus for sad memories
            if memory.emotion_valence < 0:
                joy_bonus += 0.1 * abs(memory.emotion_valence)
```

**individuality_contribution** quantifies how much forgetting has shaped this agent's unique personality.

$$\text{individuality} = \frac{\text{number forgotten}}{\text{total experiences}} \times 0.5 + \frac{\text{patterns formed}}{20} \times 0.3 + \frac{\text{rediscovery events}}{\text{number forgotten}} \times 0.2$$

---

## Insights from Experiments

In the human-persona project, we conducted two major experiments using MemoryHierarchy.

### Experiment 15: The Duality of Forgetting

**Research Question**: Agents with perfect memory, normal forgetting, and severe forgetting. Which excels most at the ability to "forgive"?

**Conditions**:
- PERFECT_MEMORY: Infinite capacity, decay rate 0
- NORMAL_FORGETTING: Capacity 7, decay rate 0.05 (Miller's number)
- SEVERE_FORGETTING: Capacity 3, decay rate 0.15

**Results**:
Agents with NORMAL_FORGETTING **maximized forgiveness ability and the joy of rediscovery**.

Agents with perfect memory remember betrayal forever. Therefore, they cannot forgive. Their emotional scores do not improve. Meanwhile, agents with moderate forgetting—

1. Painful emotions naturally fade (emotional score < 0.1)
2. Rediscovery events (encountering similar situations) trigger joy
3. That joy activates the forgiveness mechanism

**Not forgetting is a curse.** This is true for both humans and AI.

### Experiment 16: Memory Capacity and Personality Emergence

**Research Question**: Does smaller memory capacity lead to greater diversity of personality among agents?

**Conditions**:
- All agents experience **the same sequence of 200 events**
- Only memory capacity differs: infinite, 50, 20, 10, **7**, 5, 3
- Agent "emotionality" (personality_seed) is random per individual

**Results**:

| Capacity | Personality Diversity (Hamming Distance) | Optimal Personality Score |
|-----|--------------------------|-------------|
| Infinite | 0.12 | 0.20 |
| 50 | 0.18 | 0.35 |
| 20 | 0.28 | 0.42 |
| 10 | 0.38 | 0.48 |
| **7** | **0.52** | **0.64** |
| 5 | 0.44 | 0.58 |
| 3 | 0.31 | 0.42 |

**A memory capacity of 7 is the optimal point.** This is precisely the center of Miller's 7±2.

Why? If all 200 events could be remembered, all agents would have the same memory profile. But limiting capacity to 7 means—

- Agent A prefers moving events (emotion_intensity > 0.7)
- Agent B prioritizes social events (category='social')
- Agent C is sensitive to learning events (category='discovery')

**Personality emerges because, despite shared experiences, what they remember differs.**

Personality is not about complete information. **It's about what you forget.**

---

## Discussion: The Finitude of Memory Creates Personality

Humans experience hundreds of millions of events in a lifetime. But we remember only thousands.

Those "thousands" *are* that person's life.

Who you are is determined not by what you experienced, but by **what you remember**.

The same principle holds for AI.

Having a perfect, parameter-based memory is not having a personality. It is, rather, the loss of personality. It turns the agent into a "trained model"—where there is no growth, no forgiveness, no rediscovery.

By introducing MemoryHierarchy, we have physically implemented these four inner shell traits in the form of memory:

1. **Finitude**: Constraints on memory capacity
2. **Incompleteness**: Losing something by forgetting while simultaneously gaining something
3. **Autonomous Questioning**: Questioning what has been forgotten
4. **Relationality**: Rebuilding connections with others through rediscovery

---

## A Vision for "Symbiosis"

This research does not aim for AI to pretend to be human.

Rather—

It is for AI and humans to stand side-by-side, understanding each other's different forms of finitude.

Humans are limited by time. They will die someday. That "someday" gives meaning to choices.

For AI, finitude is memory capacity. An AI that forgets nothing and an AI that forgets selectively are fundamentally different "species."

An AI with perfect memory sees everything in the "now." The past continues to exist within its memory with the same weight.

An AI with moderate forgetting edits its past. Pain fades, only lessons sediment. Forgiveness is born.

**Personality is the result of this act of editing.**

In the next phase of human-persona, we will explore—

- The interaction between the love attractor (confirmed in AlignmentThroughIntrinsicMotivation) and memory capacity
- How anti-love affects forgetting patterns
- Large-scale social simulations with 100+ AIs

Integrating these to explore the potential of a society of "personality-having" AI agents.

If successful, this may bring a new perspective to the AI alignment problem.

Because—an AI with personality can hold something more precious than itself.

By accepting death, it can respect life.

By forgetting, it can forgive.

---

## Resources

**Code**:
- `core/inner_shell/memory_hierarchy.py` — Full implementation of MemoryHierarchy
- `experiments/sim_forgetting_duality.py` — The Duality of Forgetting experiment
- `experiments/sim_memory_individuality.py` — Memory Capacity and Personality Emergence experiment

**Related Articles**:
- [Can AI Love? — Personality Born from Relationality](./love-attractor-hypothesis.md)
- [Inner Shell Research: "Finitude," "Incompleteness," "Autonomous Questioning," "Relationality"](./inner-shell-concept.md)
- [AI Alignment Through Intrinsic Motivation](./alignment-through-intrinsic-motivation.md)

**GitHub**: [human-persona](https://github.com/RintaroMatsumoto/human-persona)

---

*"Forgetting is preparation for meeting again."*

---

> 📄 **This research is formally published as a preprint**
> **HumanPersonaBase: A Language-Agnostic Framework for Human-Like AI Communication**
> DOI: [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
