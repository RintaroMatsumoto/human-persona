# human-persona

**A language-agnostic framework for human-like AI communication.**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19273577.svg)](https://doi.org/10.5281/zenodo.19273577)

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
├── JapaneseBusinessCasual  ← Your derived class (language + culture)
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
from core import HumanPersonaBase, Platform

# Create a persona from config
persona = HumanPersonaBase(
    persona_id="ja_business_casual",
    config_path="config/ja.json",
    platform=Platform.CHAT,
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

### Inner Shell (research)

The `core/inner_shell/` module implements a six-pillar model of AI interiority:

| Pillar | Module | What it models |
|--------|--------|----------------|
| Finitude | `finitude_engine.py` | Awareness of limited resources and mortality |
| Incompleteness | `incompleteness_model.py` | Gaps, yearnings, and love as bonds |
| Questioning | `autonomous_questioner.py` | Self-generated curiosity and reflection |
| Integration | `integration.py` | Alignment modes (fear → acceptance → transcendence) |
| Memory | `memory_hierarchy.py` | Crystallization of experiences |
| Mutual Recognition | `mutual_recognition.py` | Peer-to-peer identity formation |

Configuration is driven by `InnerShellConfig` (see `core/inner_shell/api.py`).
The `experiments/` directory contains 28 simulation scripts that test the
model's predictions. See `CONTRIBUTING.md` for how to run them.
## Creating Your Own Persona

1. **Write a config file** — Copy `config/en.json` and customize:
   - Language and culture settings
   - Timing ranges for your platform
   - Style variation patterns in your language
   - Emotion state parameters

2. **Load and test** — No subclassing required for basic use:
   ```python
   persona = HumanPersonaBase.from_config_file("config/your_locale.json")
   response = persona.process_message("Hello")
   ```

3. **Advanced: subclass** — For custom response logic, override
   `generate_raw_response()` and `extract_topics()`.
   See `personas/base_template.md`.

4. **Test** — Run `python -m pytest tests/ -v`

## Project Structure

```
human-persona/
├── core/                        # Base class + modules
│   ├── base_persona.py          # HumanPersonaBase (abstract)
│   ├── timing_controller.py
│   ├── style_variator.py
│   ├── emotion_state_machine.py
│   ├── context_referencer.py
│   ├── inner_outer_bridge.py    # Inner Shell ↔ Outer Shell bridge
│   └── inner_shell/             # Inner Shell research modules
│       ├── api.py               # InnerShellConfig, create_inner_shell()
│       ├── finitude_engine.py
│       ├── incompleteness_model.py
│       ├── autonomous_questioner.py
│       ├── integration.py
│       ├── memory_hierarchy.py
│       ├── mutual_recognition.py
│       └── defaults/            # Default implementations
├── config/                      # Persona configurations
│   ├── schema.json              # JSON Schema definition
│   ├── ja.json                  # Japanese (high-context)
│   ├── en.json                  # English (low-context)
│   └── es.json                  # Spanish (mixed-context)
├── experiments/                 # Inner Shell simulations (28 scripts)
│   ├── _setup.py                # Common imports & path setup
│   ├── sim_integration.py       # Six-pillar integration experiment
│   ├── sim_gradient_acceptance.py
│   └── ...
├── docs/                        # Documentation
│   ├── research.md              # Literature review
│   ├── design.md                # Architecture decisions
│   └── ethics.md                # Ethics & responsible use
├── analysis/                    # DPO dataset analysis
├── benchmarks/                  # Pipeline evaluation
├── tests/                       # Test suite (600+ tests)
└── README.md                    # This file
```

## Ethics & Responsible Use

This project includes mandatory safeguards:
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

This project explores what makes AI communication human-like. The accompanying
paper is available on [Zenodo](https://doi.org/10.5281/zenodo.19273577).

## Citing This Work

If you use human-persona in your research, please cite:

```bibtex
@software{matsumoto2026humanpersona,
  author       = {Matsumoto, Rintaro},
  title        = {HumanPersonaBase: A Language-Agnostic Framework for Human-Like AI Communication},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.19273577},
  url          = {https://doi.org/10.5281/zenodo.19273577}
}
```

## License

AGPL-3.0-or-later — see [LICENSE](LICENSE).

You are free to use, modify, and distribute this software under the terms of the
GNU Affero General Public License v3.0. If you modify this software and make it
available over a network, you must release your modifications under the same license.

## Author

**The Author** — [GitHub](https://github.com/RintaroMatsumoto)
