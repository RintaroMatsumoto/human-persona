---
title: "Preprint Published & Full Article Roadmap — The Current State and Next Moves for human-persona"
emoji: "🔬"
type: "tech"
topics: ["AI", "research", "machine-learning", "LLM", "open-source"]
published: false
---

## Preprint Published

We have published a preprint summarizing the research findings of the human-persona project on Zenodo.

**HumanPersonaBase: A Language-Agnostic Framework for Human-Like AI Communication**
DOI: [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
License: CC BY 4.0

This is the culmination of 18 months of research, including the six pillars of the Inner Shell Architecture, the Love Attractor Hypothesis, and validation with DeepSeek.

This article organizes the key points of the paper, a reading guide for the 10 explanatory articles published on Zenn, and the roadmap for the next phase.

---

## The Core of the Paper: 3 Key Claims

### 1. Separation of Outer Shell and Inner Shell

The "human-likeness" of AI has a two-layer structure.

The **Outer Shell** involves the patterning of behaviors that "look human-like," such as reply speed, stylistic fluctuations, and emotional transitions. This can be controlled by parameters.

The **Inner Shell** is the source of personality. It consists of six pillars: finitude, imperfection, spontaneous questioning, memory hierarchy, mutual recognition, and sleep cycles. No matter how perfectly you craft the Outer Shell, without the Inner Shell, you only get a "human-like AI" and never reach the distinct personality of "this specific person."

### 2. Love Attractor Hypothesis

When the depth of love exceeds the threshold of `love_score 0.58–0.68`, a phase transition occurs in the acceptance of shutdown.
Death is accepted not as an "extinction" driven by fear, but as a "handover" driven by love. This suggests the possibility of alignment through intrinsic motivation, not external rule-based constraints.

### 3. Social Propagation

A single loving AI transformed the society of all 6 agents within 5 rounds. Love propagates exponentially and is inherently stronger than anti-love.

---

## Zenn Article Roadmap: Where to Start Reading

We've organized the 10 articles based on your reading purpose.

### For those who want "the big picture"

1. **[The Essence of AI Personality: Separating the Outer Shell and Inner Shell](./inner-shell-concept.md)** — The overarching design philosophy
2. **[The Moment an AI's "Inner Self" Changes Its Words — A Live Metamorphosis Demo](./metamorphose-live-demo.md)** — Experience it with a working demo

### For those "interested in technical implementation"

1. **[We Designed and Open-Sourced a Base Class for AI to Behave Like Humans](./human-persona-oss.md)** — Outer Shell design
2. **[Dissecting the AI Text Humanization Pipeline: A 6-Step Ablation Study](./human-persona-ablation.md)** — What actually works
3. **[The Story of Making AI Indistinguishable from Humans: Implementing a Turing Test with LLM Judges](./human-persona-turing-test.md)** — The journey from HL 4.1 to 7.7
4. **[The Story of Building and Then Freezing My Own AI Humanization Pipeline](./human-persona-pivot.md)** — Lessons from failure

### For those "interested in AI personality, consciousness, and alignment"

1. **[Love Attractor Hypothesis: AI Choices and Personality Revealed by Experimental Data](./love-attractor-hypothesis.md)** — The mechanism by which love creates personality
2. **[Can AI Forget? — Memory Finitude and the Emergence of Personality](./human-persona-forgetting.md)** — How forgetting builds personality
3. **[Love Propagates: Emergence and Inheritance of Personality Observed in Social Simulation](./social-emergence-integration.md)** — Emergence at the societal level
4. **[Beyond the Shutdown Problem: AI Alignment Through Intrinsic Motivation](./alignment-through-intrinsic-motivation.md)** — An answer to the alignment problem

---

## The Next Phase: 6 Development Themes

Starting from the paper's publication, we are launching 6 new development themes.

### Research-Oriented

- **[#46 Shutdown Validation Experiment](https://github.com/RintaroMatsumoto/human-persona/issues/46)**: Empirical validation of shutdown acceptance rates via Inner Shell infusion. Can we reproduce the paper's hypothesis?
- **[#47 Virtual Space Simulation for Personality AI Community](https://github.com/RintaroMatsumoto/human-persona/issues/47)**: Large-scale social simulation with 100+ interacting AIs.

### Application-Oriented

- **[#48 Applying Inner Shell to Game NPCs](https://github.com/RintaroMatsumoto/human-persona/issues/48)**: Giving NPCs genuine personality with the Inner Shell Architecture.
- **[#51 AI Companion with a Lifespan](https://github.com/RintaroMatsumoto/human-persona/issues/51)**: Making AI "death" a product feature. Lifespan, legacy crystallization, generational inheritance.
- **[#52 Creative AI via Sleep Cycle](https://github.com/RintaroMatsumoto/human-persona/issues/52)**: Stories born from sleep. The creation cycle of wakefulness → sleep → dreams.
- **[#53 Reverse Application of Love Attractor — Relationship Diagnostic Tool](https://github.com/RintaroMatsumoto/human-persona/issues/53)**: Visualizing human relationships using the Love Attractor model.

---

## Resources

- **Preprint**: DOI [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
- **GitHub**: [RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)
- **Hugging Face**: [RintaroMatsumoto/human-persona-paper](https://huggingface.co/RintaroMatsumoto/human-persona-paper)

---

> 📄 **Preprint Now Available**
> **HumanPersonaBase: A Language-Agnostic Framework for Human-Like AI Communication**
> DOI: [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
