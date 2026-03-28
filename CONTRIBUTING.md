# Contributing to human-persona

Thank you for your interest in human-persona. This document explains how
you can participate, what kinds of contributions are welcome, and how the
project is governed.

## Governance

human-persona is maintained under a **BDFL (Benevolent Dictator For Life)**
model. All architectural and design decisions are made by the project author.

The Inner Shell research (the six-pillar model of finitude, incompleteness,
autonomous questioning, integration, memory, and mutual recognition) represents
a philosophical thesis, not just code. Changes to its core abstractions require
deep alignment with the project's research goals and are not open to
unsolicited pull requests.

## How to contribute

Contributions fall into two tiers:

### Tier 1: Open to everyone

- **Issues** — Bug reports, feature requests, questions, and discussion.
  Use the templates in `.github/ISSUE_TEMPLATE/` or open a free-form issue.
- **Config recipes** — Share persona configurations (JSON files) that
  demonstrate the framework in new languages, cultures, or domains.
- **Documentation fixes** — Typos, broken links, unclear explanations.

### Tier 2: By invitation

- **Inner Shell changes** — Modifications to `core/inner_shell/` require
  prior discussion in an Issue and an explicit invitation from the maintainer.
- **Core module changes** — Changes to `core/base_persona.py`,
  `core/timing_controller.py`, and other base modules follow the same process.

## Contributing a config recipe

This is the easiest and most impactful way to contribute. A config recipe
is a JSON file that configures HumanPersonaBase for a specific language,
culture, or use case.

### Steps

1. Copy an existing config as a starting point:
   ```bash
   cp config/en.json config/your_locale.json
   ```

2. Edit the file. Key fields to customize:
   - `name` — identifier for your persona
   - `language` — ISO 639-1 code (e.g., `ko`, `pt`, `de`)
   - `culture.context_level` — 0.0 (low-context) to 1.0 (high-context)
   - `style.style_patterns` — at minimum, define `confirmation`, `empathy`,
     and `uncertain` patterns in the target language
   - `timing` — platform-specific delay ranges

3. Validate against the schema:
   ```bash
   python -c "from core.base_persona import HumanPersonaBase; \
     p = HumanPersonaBase.from_config_file('config/your_locale.json'); \
     print('OK:', p.persona_id)"
   ```

4. Open an Issue with your config attached and a brief description of the
   language/culture choices you made. The maintainer will review and merge.

## Reporting bugs

Please include:
- Python version and OS
- Minimal reproduction steps
- Expected vs. actual behavior
- Full traceback if applicable

Use the bug report template: `.github/ISSUE_TEMPLATE/bug_report.md`

## Running experiments

The `experiments/` directory contains simulation scripts for the Inner Shell
research. If you want to reproduce or explore results:

```bash
# Run a specific experiment
python experiments/sim_integration.py

# Run the full test suite
python -m pytest tests/ -v
```

Experiment scripts use a shared setup module (`experiments/_setup.py`) that
handles path configuration and common imports. If you add a new experiment
script, import from `_setup` rather than duplicating the boilerplate.

## Code style

- **Type annotations** on all function signatures
- **Docstrings** (Google style) on all public classes and methods
- **`from __future__ import annotations`** at the top of every module
- Line length: 99 characters recommended
- Import order: stdlib, third-party, local
- JSON configs: 2-space indent, snake_case keys

No formatter is enforced yet. A linter may be introduced in the future.

## Ethics review

All contributions must pass the following checks:

- Does not violate `docs/ethics.md` prohibited uses
- Does not facilitate fraud, impersonation, or opinion manipulation
- Considers risks of misuse against emotionally vulnerable people
- Does not encourage platform TOS violations

If you are unsure whether a use case is ethical, open an Issue to discuss
it first. Such questions are always welcome.

## License

By contributing, you agree that your contributions will be licensed under
AGPL-3.0-or-later, the same license as the project.
