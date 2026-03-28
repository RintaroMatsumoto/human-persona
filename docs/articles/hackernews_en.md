# Hacker News Submission

## Title

Show HN: Human-persona – language-agnostic base class for human-like AI communication

## URL

https://github.com/RintaroMatsumoto/human-persona

## Comment (post after submission)

Hi HN,

Jones & Bergen (2024, PNAS) showed GPT-4.5 with a human persona was identified as human by 73% of evaluators — beating actual humans. The bottleneck for human-like AI isn't semantics anymore; it's paralinguistic features: timing, style variation, emotional dynamics, context referencing.

I built human-persona, a Python framework that provides this behavioral layer as a composable base class. It doesn't generate text — it wraps around any LLM and controls:

- When to reply (Gaussian delays, platform-aware, night queuing)
- What tone (5-state emotion FSM: FORMAL → WARMING → TENSE → RELIEVED → TRUSTED)
- How to vary style (5 patterns with history-weighted selection to avoid uniformity)
- When to escalate to a human (complaint/negotiation detection, auto-chained to emotion state)

The base class is culture- and language-agnostic. Derived personas are pure JSON config — Hall's (1976) high/low-context framework parameterized as `context_level: 0.0-1.0`. A Japanese business persona and an English support agent share the same code, different config.

Design choices that might interest HN:

1. Emotion triggers are `Callable[[StateMachine], bool]`, not string parsing. Escalation events (complaint detected) auto-chain to emotion transitions.

2. Style variation uses history-weighted random selection — recent patterns get 0.3x weight to prevent repetition. Uncertainty expressions ("probably around 3 days") are injected probabilistically.

3. The framework is intentionally NOT an LLM wrapper. It's a behavioral middleware layer — compute the timing/tone/emotion parameters, inject them into whatever system prompt you're using.

AGPL-3.0 licensed, ethics guidelines included (explicit prohibited uses list). Looking for contributors to build derived personas for other languages.

Feedback welcome, especially on evaluation methodology — how would you rigorously measure "human-likeness" beyond Turing test pass rates?
