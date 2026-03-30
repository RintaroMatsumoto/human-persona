---
title: "Day 0 — The First Commit"
emoji: "🦋"
type: "idea"
topics: ["AI", "Metamorphose", "research-journal", "InnerShell"]
published: false
---

## The Question

Can AI responses be made more human-like?

I want to build something practical. When an AI sends a message, can it feel a little more natural? The timing of replies, variation in writing style, the flow of emotion — can those structures be extracted and turned into a framework? Years of experience in simulation system development have given me some intuition for modeling human behavior.

The direction is set. I fire up Claude Code.

---

## Writing Code

The first instruction is clear: "Research and develop a universal Agent Skill called 'human-persona.' Design a base class independent of language and culture." There's also a plan to feed in real-world operational data from a business tool I'm running separately. The aim is a practical tool.

Claude Code generates `core/base_persona.py`. The `HumanPersonaBase` class — a base class integrating five components.

**EmotionStateMachine** — Formalizes emotion as a finite state machine. FORMAL → WARMING → TENSE → RELIEVED → TRUSTED. A model of the typical emotional flow in business communication. A state machine rather than a scalar value, because it makes "which phase am I in?" explicit.

**StyleVariator** — Introduces variation in writing style. Five patterns: confirmation, empathy, hedging, pivot, and uncertainty. A decay weight on recent history prevents the same pattern from repeating. Uncertainty expressions are injected probabilistically — excessive certainty is a telltale sign of AI.
**TimingController** — Controls reply speed. Normal-distribution-based delay generation. Platform-specific profiles: crowdsourcing messages get 5–15 minutes. Active hours are 9 AM to 9 PM. An instant reply at 3 AM raises suspicion.

**EscalationDetector** — Detects situations that should be handed off to a human. "Rate," "compensation," "discount," "complaint." Compensation negotiations and complaints are not for AI to handle.

**ContextReferencer** — References prior context. Topic-based tracking that determines when to refer back to past conversation threads. Full-text retention is too costly, so it focuses on topic extraction.

`process_message()` does not generate response text. It only calculates human-likeness parameters — delay, style, emotional state. Crafting the words is the LLM's job. A division of labor with AI is assumed from the start.

---

## The First Design Review

Reviewing the generated code. Three issues surface.

`@dataclass` inheritance has field-ordering traps — a regular class is safer. The `process_message()` return value is always an empty string, which should be made explicit in the docstring to avoid confusing anyone building a derived class. Event types are still string literals — they should be Enums.

Then a more fundamental problem becomes visible. `EmotionStateMachine`'s `_evaluate_trigger` evaluates trigger conditions by string parsing. Processing `"exchange_count >= 3"` via string splitting is fragile. Moreover, when `EscalationDetector` detects a COMPLAINT, it doesn't reach `EmotionStateMachine` — inter-component coordination is broken.

The fix is decided: change triggers from string parsing to `Callable`, and chain-fire `problem_detected` to `EmotionStateMachine` when escalation is detected. The fix goes in. The diff checks out. The design is complete.
---

## 2,817 Lines

At the commit stage, git complains about an unconfigured identity. An email address is requested. SSH keys turn out to be unregistered on GitHub, requiring manual public key registration — the road to the first commit is longer than writing the code.

In the afternoon, the first commit lands.

```
feat: initial implementation of HumanPersonaBase

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

20 files, 2,817 lines. Ambitious for a first commit. The base class, five core modules, a config schema, design docs, ethics guidelines, a paper draft, a Zenn article, even a Reddit post draft — all included. It feels like dumping everything in my head at once.

Seventeen minutes later, a second commit adds the Zenn article. Write it, ship it.

`docs/ethics.md` is there from the beginning. A technology that makes AI behave more like humans carries obvious risks of misuse. I didn't want to put that off.

The roadmap in the design doc lists v0.2 for emotion-driven reply speed variation, v0.3 for a learning loop and A/B testing, v1.0 for automatic persona generation. The config example is named `JapaneseBusiness`. Straightforwardly building a work tool.