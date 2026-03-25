# human-persona

**A language-agnostic framework for human-like AI communication.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)

---

## What is this?

`human-persona` provides a **base class** for making AI agents communicate
like humans. It handles the paralinguistic features that betray AI:
instant replies, uniform phrasing, static tone, and perfect precision.

The framework is language-agnostic. You bring your language, culture, and
domain — the base class provides the universal structure of human-like
communication.

```
HumanPersonaBase            ← This project (universal)
├── JapaneseFreelancer      ← Your derived class (language + domain)
├── EnglishSupportAgent     ← Another derived class
└── SpanishSalesRep         ← etc.
```

## Why?

Research shows that when AI is given proper persona instructions, it's
identified as human **73% of the time** — more than actual humans (63%).
The bottleneck isn't AI capability; it's **persona design**.

This project formalizes what makes AI communication human-like, based on
empirical analysis of the HumanLLMs/Human-Like-DPO-Dataset (10,884 samples).

## Quick Start

```python
from core import load_config, Platform
from personas.freelancer_ja import JapaneseFreelancerPersona

# Initialize
persona = JapaneseFreelancerPersona(
    config_path="config/ja.json",
    platform=Platform.CROWDSOURCING,
)

# Process a message
response = persona.process_message("納期はいつ頃になりますか？")

print(response.content)        # Natural Japanese response
print(response.delay_seconds)  # Simulated human response time
print(response.emotion_state)  # Current emotional state
```

## Core Modules

| Module | What it does |
|--------|-------------|
| `TimingController` | Simulates human response delays per platform |
| `StyleVariator` | Introduces linguistic variation (filler words, punctuation, rare typos) |
| `EmotionStateMachine` | Tracks emotional state across conversation lifetime |
| `ContextReferencer` | Generates natural back-references to earlier topics |
| `EscalationDetector` | Detects when to hand off to a human operator |

## Creating Your Own Persona

1. **Write a config file** — Copy `config/en.json` and customize:
   - Language and culture settings
   - Timing ranges for your platform
   - Style variation patterns in your language
   - Emotion state parameters

2. **Create a derived class** — See `personas/base_template.md`:
   - Implement `generate_raw_response()` (your response logic)
   - Implement `extract_topics()` (for back-referencing)
   - Optionally override `on_escalation()` and `post_process()`

3. **Test** — Run `python -m pytest tests/ -v`

## Project Structure

```
human-persona/
├── core/                    # Base class + modules
│   ├── base_persona.py      # HumanPersonaBase (abstract)
│   ├── timing_controller.py
│   ├── style_variator.py
│   ├── emotion_state_machine.py
│   ├── context_referencer.py
│   └── escalation_detector.py
├── config/                  # Persona configurations
│   ├── schema.json          # JSON Schema definition
│   ├── ja.json              # Japanese (high-context)
│   ├── en.json              # English (low-context)
│   └── es.json              # Spanish (mixed-context)
├── personas/                # Derived class examples
│   ├── base_template.md     # How to create your own
│   ├── freelancer_ja.py     # Japanese freelancer
│   └── customer_support_en.py
├── docs/                    # Documentation
│   ├── research.md          # Literature review
│   ├── design.md            # Architecture decisions
│   ├── ethics.md            # Ethics & responsible use
│   └── paper_draft.md       # Academic paper draft
├── analysis/                # DPO dataset analysis
│   ├── metrics.py           # Shared metrics module (7 metrics)
│   ├── dpo_parameter_extraction.py
│   └── results/             # Phase B analysis results
├── benchmarks/              # Pipeline evaluation
│   ├── dpo_benchmark.py     # 500-sample benchmark vs DPO dataset
│   └── results/             # Benchmark reports & scorecard
├── tests/
│   ├── test_dpo_analysis.py # DPO analysis tests (28 tests)
│   └── test_benchmark.py    # Benchmark tests (39 tests)
├── SKILL.md                 # Agent Skill entry point
└── README.md                # This file
```

## Ethics & Responsible Use

This project includes mandatory safeguards:
- **Escalation detection** is required, not optional
- **Human handoff** for negotiations, complaints, legal matters
- **No identity claims** — personas use roles, not fake identities

See [docs/ethics.md](docs/ethics.md) for full guidelines.

**Prohibited uses:** fraud, impersonation, emotional exploitation,
election interference, harassment, platform TOS violations.

## Benchmark

human-persona includes a statistical benchmark that evaluates pipeline output
against the [HumanLLMs/Human-Like-DPO-Dataset](https://huggingface.co/datasets/HumanLLMs/Human-Like-DPO-Dataset)
(10,884 samples).

**6 metrics** are measured and scored on a 0–1 scale
(1.0 = matches Human-Like distribution, 0.0 = matches Formal/AI distribution):

| Metric | Weight | Human-Like | Formal |
|--------|--------|-----------|--------|
| Sentence Length CV | 1.0 | 0.634 | 0.432 |
| Hedge Rate | 1.5 | 0.082 | 0.017 |
| Self-Correction Rate | 1.0 | 0.043 | 0.001 |
| Words/Sentence | 1.0 | 13.5 | 18.3 |
| Cushion Rate | 1.0 | 15.8% | 1.9% |
| Filler Rate | 1.5 | 0.334 | 0.101 |

### Running the benchmark

```bash
# Requires DEEPSEEK_API_KEY (OpenAI-compatible)
export DEEPSEEK_API_KEY=sk-...
python -m benchmarks.dpo_benchmark
```

Results are saved to `benchmarks/results/`:
- `benchmark_report.md` — Human-readable comparison table
- `scorecard.json` — Machine-readable scores for CI/CD regression testing

API responses are cached in `benchmarks/cache/` to minimize cost on re-runs.

## Research

This project aims to publish findings on arXiv and contribute to the
Anthropic Agent Skills ecosystem. See [docs/paper_draft.md](docs/paper_draft.md).

## License

MIT — see [LICENSE](LICENSE).

## Author

**The Author** — [GitHub](https://github.com/RintaroMatsumoto)
