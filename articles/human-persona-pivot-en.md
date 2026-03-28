---
title: "The Story of Building and Then Freezing My Own AI Humanization Pipeline"
emoji: "🔬"
type: "tech"
topics: ["AI", "research", "machine-learning", "LLM", "open-source"]
published: false
---

## What Happened

In [human-persona](https://github.com/RintaroMatsumoto/human-persona), the `core/` directory contains a base class composed of four components: TimingController, StyleVariator, EmotionStateMachine, and ContextReferencer. It's a language- and culture-agnostic framework designed for human-like AI communication.

One day, I wrote a **simple pipeline for integrating this framework into an actual production environment**. `humanize/pipeline.py` — a post-processing pipeline consisting of three stages: filler injection, typo injection, and rhythm variation.

I wrote it. I tested it. It passed benchmarks.

**And then I froze it.**

This article is about why I froze the code I wrote myself.

## What Was pipeline.py Doing?

The mechanism was simple:

```python
class HumanizePipeline:
    def __call__(self, text: str, strength: float = 0.4) -> str:
        sentences = self._split(text)
        sentences = self._inject_fillers(sentences, strength)
        sentences = self._inject_typos(sentences, strength)
        sentences = self._vary_rhythm(sentences, strength)
        return self._join(sentences)
```

1.  **Filler Injection**: Probabilistically inserting phrases like "Actually," or "To be honest," at the beginning of sentences.
2.  **Typo Injection**: Intentional typos like "ですが" → "でうすが".
3.  **Rhythm Variation**: Inserting short commentary sentences ("This is important.") to vary sentence length.

I fixed a bug in Japanese period handling (double periods `。。`), and the DPO benchmark scores were fine.

Everything seemed to be going smoothly.

## The First Anomaly: The Absence of Register

The moment I lined up Before/After texts from real use cases, I noticed something was off.

The pipeline **processed all text identically**. Business emails, casual chats, official documents—all received the same fillers, the same typo rate, the same rhythm.

This is fundamentally wrong.

There was no distinction for **register** (formal / business / casual / friendly) from linguistics. "To be honest," might be appropriate in a business email, but inserting the same filler in a contract would be fatal. In a casual chat, it would conversely be too formal.

## The Fatal Flaw: Japanese Honorific System

Next, I found an even more serious problem. Japanese honorifics have three layers:

*   **Respect Language (sonkeigo)**: Elevates the other party's actions ("ご覧になる", "いらっしゃる").
*   **Humble Language (kenjougo)**: Humbles one's own actions ("拝見する", "参る").
*   **Polite Language (teineigo)**: Makes sentence endings polite ("です", "ます").

pipeline.py made no distinction between these. It treated Japanese formality with a single scalar value: `formality_default: 0.7`.

This made it impossible to differentiate between appropriate usage like "対応いたします" (humble language) and unnatural, excessive humility like "対応させていただきます". It couldn't choose appropriately between "ご検討くださいませ" (respect language) and "検討します" (polite language only).

It was a problem that any native Japanese speaker would find jarring immediately.

## The Real Problem: I Hadn't Read My Own Code

Now for the most painful fact.

`core/base_persona.py` already had a design to address these issues:

*   `EmotionStateMachine` automatically adjusts formality based on conversation phase.
*   `StyleVariator` holds five stylistic patterns and prevents consecutive repetition of the same pattern via weight decay.
*   `config/ja.json` defines parameters like `context_level: 0.85` (high-context culture) and `formality_default: 0.7`.

**pipeline.py was built while completely ignoring this existing architecture.**

Why did I ignore it? To be honest, because "I wanted something quick and dirty." It was faster to write a 3-stage post-processor than to understand the core/ pipeline (emotion update → generation → style variation → context reference → ambiguity → post-processing → delay).

It was faster. And it was wrong.

## The Trap of Automated Evaluation

There was another overlooked problem.

In the Ablation Study, I used a DPO benchmark to measure the contribution of each step:

*   Filler Injection: ~60%
*   Typo Injection: ~25%
*   Rhythm Variation: ~15%

The scores were good. But this evaluation itself was the problem.

**The automated evaluation was only detecting superficial features.** If there were fillers, it was "human-like"; if there were typos, it was "human-like". But that's not "human-likeness". Human-likeness lies in the appropriate use of honorifics, natural referencing of context, and consistent emotional transitions.

These are not reflected in DPO scores.

## The Pivot: Prompt-Level Control

So what to do? I organized two facts:

**Fact 1**: For one-off text generation (proposals, emails, etc.), neither emotional transition nor context accumulation is necessary. Incorporating persona instructions into the LLM's system prompt is more effective than a post-processing pipeline.

**Fact 2**: The core/ architecture of human-persona becomes truly necessary in the phase of **continuous conversation**. In a 5- or 10-exchange interaction with a client, where emotions change, previous context is referenced, and response timing naturally varies—this cannot be controlled by prompts alone.

In other words, pipeline.py **was solving the wrong problem**.

Humanizing one-off text was sufficiently handled by prompt-level instructions:

```
Style and Persona:
- Polite language base (です・ます体). Avoid excessive use of respect language.
  - OK: 「対応いたします」
  - Avoid: 「対応させていただきます」
- Opening sentence: Max 20 characters. Gets straight to the point.
- Ratio of short to long sentences: Approximately 1:3.
```

I A/B tested this prompt with the DeepSeek API. The results were clear:

| Aspect | Old (Generic Prompt) | New (Persona Prompt) |
|---|---|---|
| Opening | 「案件内容を拝見しました。」 (Formulaic) | 9 characters, cuts to the core of the matter |
| Honorifics | Excessive use of 「させていただきます」 | 「です・ます」 base |
| Sentence Length Variation | Uniform (parallel sentences of 3-4 lines) | Mix of short and explanatory sentences |
| CTA | 「ご検討のほど、よろしくお願いいたします」 | 「商品数を教えてください」 (Invites dialogue) |

I also confirmed its effectiveness through Human Eval (visual assessment).

## Lessons Learned

### 1. Read the Existing Architecture

Before writing new code, read **all** of the project's existing design. "It takes too long to read" is not an excuse. Rewriting code you wrote without reading it takes far more time.

### 2. Don't Over-Trust Automated Evaluation

Even if DPO benchmark scores are good, they might only be measuring superficial feature matching. Especially for subjective qualities like "human-likeness", Human Eval (human visual assessment) is essential.

### 3. Identify the Problem Scope

"Making AI output human-like" seems like one problem, but it's actually two distinct problems:

*   **One-off Text**: Sufficiently controlled at the prompt level. A post-processing pipeline is over-engineering.
*   **Continuous Conversation**: Insufficient with prompts alone. Requires EmotionStateMachine, ContextReferencer, TimingController. It breaks down beyond 5 exchanges.

pipeline.py was trying to solve the former problem with tools for the latter—and it wasn't even using those tools correctly.

### 4. Freezing Isn't Bad

"Throwing away code you wrote" doesn't feel good. But it's far better than continuing down the wrong path. I froze pipeline.py, but the insights gained here (the importance of the honorific system, the need for register, the limits of automated evaluation) will directly inform the next design.

## Current Status and Next Steps

*   `humanize/pipeline.py`: **Frozen**. Saved but not used in production.
*   One-off text generation: **Migrated to prompt-level persona control**. Includes numerical constraints and platform-specific tone adjustments.
*   Continuous conversation: **Not started**. Planning a full-scale redesign leveraging the core/ foundation.

Open Issues:
*   [#10 Implementation of Register System](https://github.com/RintaroMatsumoto/human-persona/issues/10)
*   [#11 Japanese Honorific Subsystem](https://github.com/RintaroMatsumoto/human-persona/issues/11)
*   [#14 Full-scale Human Eval](https://github.com/RintaroMatsumoto/human-persona/issues/14)

Repository: [github.com/RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)

---

Previous Articles:
*   [I Designed and Open-Sourced a Base Class for AI to Behave Like Humans](./human-persona-oss.md)
*   [Dissecting an AI Text Humanization Pipeline: A 6-Step Ablation Study](./human-persona-ablation.md)
*   [The Story of Making AI Indistinguishable from Humans: Implementing a Turing Test with LLM Judges](./human-persona-turing-test.md)

---

> 📄 **This article's research is formally published as a preprint**
> **HumanPersonaBase: A Language-Agnostic Framework for Human-Like AI Communication**
> DOI: [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
