[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

# human-persona

**A language-agnostic framework for human-like AI communication.**

## What is this?

human-persona provides a reusable base class (`HumanPersonaBase`) that decomposes human-like communication into five orthogonal, independently testable components. It does not generate text—it provides the **behavioral layer** (timing, tone, emotion, context, safety) that wraps around any LLM.

The base class is culture- and language-independent. Specific languages, cultures, and use cases are defined through JSON configuration files or Python subclasses.

## Why?

Jones & Bergen (2024) showed that GPT-4.5, when given a human-like persona, was identified as human by **73% of evaluators**—surpassing the recognition rate of actual human participants. The bottleneck for human-like AI has shifted from semantic understanding to **paralinguistic features**: response timing, stylistic variation, emotional dynamics, and contextual referencing.

Yet there is no reusable, language-agnostic framework for these behaviors. Existing implementations are ad hoc, language-specific, and tightly coupled to platforms. human-persona fills this gap.

## Architecture

```
HumanPersonaBase (base class) ← this repository
│
│  + TimingController        – response delay (platform-aware, Gaussian)
│  + StyleVariator           – stylistic variation (anti-uniformity)
│  + EmotionStateMachine     – emotional arc (FORMAL → WARMING → TRUSTED)
│  + ContextReferencer       – conversation history & back-referencing
│  + EscalationDetector      – human handoff (complaints, negotiation, calls)
│
├── JapaneseBusinessPersona       (derived via config)
├── EnglishCustomerSupportPersona
└── SpanishSalesPersona
```

Each component is an independent dataclass with its own `from_config()` factory. The base class composes them and provides a single `process_message()` entry point.

## Quick Start

```python
from core.base_persona import HumanPersonaBase

# Load a persona from a JSON config
persona = HumanPersonaBase.from_config_file("config/ja_business.json")

# Process a user message
response = persona.process_message(
    "Can we discuss the deadline?",
    topics=["deadline", "consultation"]
)

# Use the behavioral parameters
print(f"Delay:   {response.delay_seconds:.0f}s")
print(f"Emotion: {response.emotion_state.value}")
print(f"Style:   {response.style_used.value}")

# Inject context into your LLM system prompt
context = persona.get_system_prompt_context()
# → {"emotion_state": "warming", "tone": {...}, "recent_topics": [...]}
```

### Configuration example

```json
{
  "name": "EnglishSupport",
  "language": "en",
  "culture": {
    "context_level": 0.3,
    "formality_default": 0.5
  },
  "platform": "chat",
  "style": {
    "uncertainty_rate": 0.1,
    "style_patterns": [
      {
        "type": "confirmation",
        "templates": ["Just to confirm, you mean ...?", "So if I understand correctly, ..."],
        "weight": 1.2
      },
      {
        "type": "empathy",
        "templates": ["I totally understand.", "That sounds frustrating."]
      },
      {
        "type": "uncertain",
        "templates": ["I think ...", "Probably ...", "If I'm not mistaken, ..."]
      }
    ]
  }
}
```

See `config/schema.json` for the full configuration schema.

## Project Structure

```
human-persona/
├── SKILL.md                       # Agent Skill entry point
├── README.md                      # This file
├── CONTRIBUTING.md                 # How to contribute
├── core/                          # Base class implementation
│   ├── base_persona.py            # HumanPersonaBase
│   ├── timing_controller.py       # Response delay control
│   ├── style_variator.py          # Stylistic variation
│   ├── emotion_state_machine.py   # Emotion state model
│   ├── context_referencer.py      # Context tracking
│   └── escalation_detector.py     # Human handoff detection
├── config/                        # Derived class configuration
│   └── schema.json                # JSON Schema for persona configs
├── personas/                      # Example derived personas
├── docs/                          # Documentation
│   ├── research.md                # Literature review
│   ├── design.md                  # Architecture & design decisions
│   ├── ethics.md                  # Ethics guidelines
│   └── paper_draft.md             # Paper draft
└── tests/                         # Tests
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Creating derived personas (JSON config + PR)
- Branch naming conventions (`persona/{lang}-{use}`)
- Code style (type annotations + docstrings required)
- Ethics review checklist

## Ethics

This is a dual-use technology. We take this seriously.

**Permitted uses**: customer support, sales, language learning, AI UX research.

**Prohibited uses**: fraud, impersonation, emotional exploitation, election interference, harassment, platform TOS violations.

See [docs/ethics.md](docs/ethics.md) for the full guidelines.

## Theoretical Foundation

- Jones & Bergen (2024). "A Turing test of whether AI chatbots are behaviorally similar to humans." *PNAS*.
- Hall, E.T. (1976). *Beyond Culture*. Anchor Books.
- Nguyen et al. (2016). "Computational Sociolinguistics: A Survey." *Computational Linguistics*.
- Mitchell, M. (2025). "The Turing Test and our shifting conceptions of intelligence." *Science*.

## License

MIT License

## Author

Rintaro Matsumoto ([@RintaroMatsumoto](https://github.com/RintaroMatsumoto))

---

## Japanese Documentation

日本語ドキュメントは [docs/ja/README.ja.md](docs/ja/README.ja.md) を参照してください。

設計思想・アーキテクチャの詳細は [docs/design.md](docs/design.md)（日本語）に記載されています。
