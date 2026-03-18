[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

# human-persona

> A language-agnostic framework for human-like AI communication.

**HumanPersonaBase** is a base class that gives AI agents human-like communication patterns — independent of language, culture, or platform.

## Why

GPT-4.5 was judged human **73% of the time** when given a persona prompt (Jones & Bergen, 2024).
The bottleneck is no longer language understanding — it's **paralinguistic features, emotional expression, and persona design**.

This project provides the engineering infrastructure to close that gap.

## Architecture

```
HumanPersonaBase          ← this repo
├── timing_controller     reply delay by platform (Gaussian, not uniform)
├── style_variator        expression variation + filler injection
├── emotion_state_machine dynamic emotional arc (FORMAL → WARMING → TRUSTED)
├── context_referencer     prior context awareness
└── escalation_detector   human handoff triggers

JapaneseBusinessPersona       ← derived (config/ja.json)
EnglishCasualDirectPersona    ← derived (config/en.json)
SpanishWarmProfessionalPersona ← derived (config/es.json)
```

Each component is an independent dataclass with its own `from_config()` factory. The base class composes them and provides a single `process_message()` entry point that generates human-like text via the Anthropic API.

## Benchmark

LLM-judged evaluation across 10 scenarios (ja/en, 5 each × 5 runs):

| Metric | v1 (skeleton) | v5 (current) | Δ |
|---|---|---|---|
| Human Likeness (1-10) | 4.1 | **7.7** | +88% |
| Style Variation Rate (lower=better) | 0.64 | **0.36** | -44% |
| Timing Naturalness (1-10) | 4.1 | **5.5** | +34% |

Key improvements: filler word injection (`えーと` / `Hmm`), tone mirroring, message structure randomization, config-driven banned phrases, greeting/progress report variation.

Run the benchmark yourself:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python tests/turing_test.py              # standard
python tests/turing_test.py --verbose    # with generated text + judge reasoning
python tests/turing_test.py --no-judge   # offline (timing/style stats only)
```

## Quick Start

```python
import os
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

from core.base_persona import HumanPersonaBase

persona = HumanPersonaBase.from_config_file("config/ja.json")
response = persona.process_message("初めまして、案件を拝見しました。")

print(response.content)          # 生成されたテキスト
print(response.delay_seconds)    # 返信遅延（秒）
print(response.emotion_state)    # 感情状態
print(response.style_used)       # 使用した文体パターン
```

### Configuration example

```json
{
  "name": "EnglishCasualDirect",
  "language": "en",
  "culture": {
    "culture_context": "low",
    "context_level": 0.25,
    "formality_default": 0.3
  },
  "platform": "chat",
  "style": {
    "uncertainty_rate": 0.10,
    "style_patterns": [
      {"type": "confirmation", "templates": ["Got it, so ___ right?"], "weight": 1.0},
      {"type": "empathy", "templates": ["I totally get that."], "weight": 0.8},
      {"type": "uncertain", "templates": ["I think it's ___, but don't quote me."], "weight": 0.6}
    ]
  },
  "human_likeness_rules": {
    "banned_phrases": ["Thanks for reaching out", "moving along well"],
    "greeting_openers": ["Hi!", "Hey there!", "Oh cool!", ""],
    "initial_contact_angles": ["Ask about timeline", "Express interest in details"],
    "progress_report_alternatives": ["Things are coming together", "On track so far"]
  }
}
```

See `config/schema.json` for the full configuration schema.

## Project Structure

```
human-persona/
├── core/                          # Base class implementation
│   ├── base_persona.py            # HumanPersonaBase + text generation
│   ├── timing_controller.py       # Response delay control
│   ├── style_variator.py          # Stylistic variation + fillers
│   ├── emotion_state_machine.py   # Emotion state model
│   ├── context_referencer.py       # Context tracking
│   └── escalation_detector.py     # Human handoff detection
├── config/                        # Persona configurations
│   ├── schema.json                # JSON Schema
│   ├── ja.json                    # Japanese (high-context)
│   ├── en.json                    # English (low-context)
│   └── es.json                    # Spanish (high-context)
├── personas/                      # Persona documentation
├── tests/
│   ├── turing_test.py             # LLM-judge benchmark
│   └── human_samples/             # DPO reference dataset
├── docs/
│   ├── research.md                # Literature review
│   ├── design.md                  # Architecture decisions
│   └── ethics.md                  # Ethics guidelines
├── articles/                      # Zenn articles
├── SKILL.md                       # Agent Skill entry point
├── CONTRIBUTING.md
└── README.md
```

## Ethics

✅ **Legitimate use**: customer support, sales automation, language learning, AI UX research
❌ **Prohibited**: fraud, impersonation, emotional manipulation, election interference, platform TOS violations

See [docs/ethics.md](docs/ethics.md) for full guidelines.

## Theoretical Foundation

- Jones, C. R. & Bergen, B. K. (2024). "A Turing test of whether AI chatbots are behaviorally similar to humans." *PNAS*.
- Hall, E. T. (1976). *Beyond Culture*. Anchor Books.
- Nguyen, D. et al. (2016). "Computational Sociolinguistics: A Survey." *Computational Linguistics*.
- Mitchell, M. (2025). "The Turing Test and our shifting conceptions of intelligence." *Science*.
- Brown, P. & Levinson, S. C. (1987). *Politeness: Some universals in language usage*. Cambridge University Press.

## Roadmap

- [x] Base class implementation (5 components)
- [x] ja/en/es persona configs
- [x] LLM-judge benchmark (v5: HL=7.7, SV=0.36)
- [x] Filler injection + tone mirroring + structure variation
- [x] Config-driven human_likeness_rules
- [ ] Human evaluation UI ([#5](https://github.com/RintaroMatsumoto/human-persona/issues/5))
- [ ] arXiv paper

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on creating derived personas, code style, and ethics review.

## License

MIT — use freely, contribute back.

## Author

Rintaro Matsumoto ([@RintaroMatsumoto](https://github.com/RintaroMatsumoto))
