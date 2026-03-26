---
title: "HumanPersonaBase: A Language-Agnostic Framework for Human-like AI Communication"
published: false
description: "An open-source Python framework that makes AI communication feel human — timing, emotion, style variation, and context referencing as composable components."
tags: python, ai, opensource, nlp
cover_image:
---

## The Problem: AI Sounds Like AI

GPT-4.5, when given a human-like persona, was identified as human by **73% of evaluators** — surpassing the recognition rate of actual humans (Jones & Bergen, 2024, *PNAS*).

The bottleneck for human-like AI has shifted. Semantic understanding is solved. What gives AI away now is **how** it communicates:

- **Instant replies** — humans don't respond in 2 seconds
- **Uniform tone** — same polished style every single time
- **Flat emotion** — no emotional arc across a conversation
- **No memory** — never references what was said before
- **Too perfect** — "I'll finish in exactly 3 days" feels robotic

These are *paralinguistic features* — a separate layer from language understanding.

## The Solution: A Behavioral Base Class

I built **[human-persona](https://github.com/RintaroMatsumoto/human-persona)**, an open-source Python framework that provides the behavioral layer for human-like AI communication. It doesn't generate text — it tells your LLM *when* to reply, *what tone* to use, and *what emotional state* to convey.

The framework decomposes human-like behavior into 4 orthogonal components:

### 1. TimingController

Gaussian-distributed response delays, not uniform random. Platform-aware: chat (30-180s), email (1-8h). Night queuing prevents 3 AM responses.

```python
def calculate_delay(self, platform: Platform) -> float:
    profile = self.profiles[platform]
    midpoint = (profile.min_seconds + profile.max_seconds) / 2
    spread = (profile.max_seconds - profile.min_seconds) / 4
    return clamp(random.gauss(midpoint, spread), profile.min_seconds, profile.max_seconds)
```

### 2. EmotionStateMachine

A 5-state FSM that models the emotional trajectory of professional relationships:

```
FORMAL → WARMING → TENSE → RELIEVED → TRUSTED
```

Transitions use `Callable[[EmotionStateMachine], bool]` — no fragile string parsing:

```python
Transition(FORMAL, WARMING, lambda sm: sm.exchange_count >= 3)
Transition(WARMING, TENSE, lambda sm: sm._last_event == "problem_detected")
```

### 3. StyleVariator

Rotates between 5 patterns (confirmation, empathy, deferral, transition, uncertainty) with history-weighted selection. Prevents the same pattern from repeating. Probabilistically inserts uncertainty expressions — "probably around 3 days" beats "exactly 3 days."

### 4. ContextReferencer

Topic-based conversation tracking. Knows when to add "as you mentioned earlier..." style back-references.

## The Design Principle: Culture-Agnostic Base Class

The base class contains no language or culture. All specifics are injected through JSON configuration:

```json
{
  "name": "JapaneseBusiness",
  "language": "ja",
  "culture": {
    "context_level": 0.8,
    "formality_default": 0.7
  },
  "style": {
    "uncertainty_rate": 0.2,
    "style_patterns": [
      { "type": "confirmation", "templates": ["...ということですよね？"] }
    ]
  }
}
```

This follows Hall's (1976) high/low-context culture framework. A Japanese business persona (high-context, indirect) and an English support agent (low-context, direct) use the same base class with different parameters.

## Quick Start

```python
from core.base_persona import HumanPersonaBase

persona = HumanPersonaBase.from_config_file("config/ja_business.json")
response = persona.process_message("Can we discuss the deadline?")

print(response.delay_seconds)    # 45.2 (not instant)
print(response.emotion_state)    # EmotionState.WARMING
print(response.style_used)       # StyleType.CONFIRMATION

# Inject into your LLM system prompt
context = persona.get_system_prompt_context()
```

## What's Next

- Evaluation experiments (automated Turing test methodology)
- arXiv paper: "HumanPersonaBase: A Language-Agnostic Framework for Human-like AI Communication in Professional Contexts"
- Community-driven derived personas for more languages

## Links

- **GitHub**: [github.com/RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)
- **License**: MIT
- **Ethics**: Full guidelines included — fraud, impersonation, and election interference explicitly prohibited

Contributions welcome — especially derived personas for languages beyond Japanese and English. Open an issue or PR.
