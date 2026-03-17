# I built an open-source framework for human-like AI communication (language-agnostic base class)

**Target**: r/MachineLearning

---

Hey r/MachineLearning,

I've been working on an open-source Python framework called **human-persona** that tackles a problem I haven't seen addressed systematically: the *paralinguistic* side of human-like AI communication.

## The motivation

Jones & Bergen's 2024 PNAS paper showed that GPT-4.5, when instructed to adopt a human-like persona, was identified as human by **73% of evaluators**—exceeding the recognition rate of actual human participants. The key insight: the bottleneck for human-like AI isn't semantic understanding anymore. It's timing, stylistic variation, emotional dynamics, and contextual referencing.

While building AI-powered business communication tools, I kept hitting the same wall: the LLM output is semantically correct, but it *feels* like AI. Instant replies, perfectly uniform tone, no emotional arc across a conversation, never referencing what was said before.

## What I built

**HumanPersonaBase** is a language-agnostic base class that decomposes human-like behavior into 5 orthogonal components:

1. **TimingController** — Gaussian-distributed response delays, platform-aware (chat: 30-180s, email: 1-8h), night queuing
2. **StyleVariator** — Rotates between 5 stylistic patterns (confirmation, empathy, deferral, transition, uncertainty) with history-weighted selection to prevent repetition
3. **EmotionStateMachine** — 5-state FSM (FORMAL → WARMING → TENSE → RELIEVED → TRUSTED) with Callable-based triggers, not string parsing
4. **ContextReferencer** — Topic-based conversation tracking for natural back-references
5. **EscalationDetector** — Keyword-based human handoff with automatic emotion state chaining (complaint detected → emotion shifts to TENSE)

The framework doesn't generate text. It provides the behavioral layer that wraps around any LLM — when to reply, what tone to use, what emotional state to convey, and when to hand off to a human.

## The design principle

The base class is culture- and language-independent. All language/culture-specific parameters (templates, keywords, timing profiles, formality levels) are injected through JSON configuration. You can create a Japanese business persona or an English support agent just by writing a config file — no code changes needed.

This follows Hall's (1976) high/low-context culture framework. A `context_level` parameter (0.0–1.0) controls indirect expression rates, silence tolerance, and ambiguity insertion.

## Current state

- Core framework is implemented and published on GitHub
- Paper draft in progress (planned arXiv submission)
- Evaluation experiments being designed
- Looking for contributors to build derived personas for other languages

## Links

- **Repo**: [github.com/RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)
- **License**: MIT
- **Ethics**: Full guidelines included — prohibited uses explicitly listed (fraud, impersonation, election interference, etc.)

Would love feedback from the community, especially on:
- The component decomposition — does the 5-component split make sense?
- Evaluation methodology — how would you rigorously measure "human-likeness" beyond Turing test pass rates?
- Cross-cultural validation — anyone interested in building derived personas for their language?

Thanks for reading.
