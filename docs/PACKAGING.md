# PyPI Packaging Setup for human-persona

This document describes the PyPI packaging configuration for the human-persona library.

## Overview

The `human-persona` package is a language and culture-agnostic framework for AI to behave humanly. The publishable package consists of:

- **core/** - Main library containing HumanPersonaBase and supporting modules
- **config/** - JSON configuration files for different languages and domains

## Package Structure

```
human-persona/
├── core/                    # Main library (publishable)
│   ├── __init__.py         # Exports main classes
│   ├── base_persona.py
│   ├── timing_controller.py
│   ├── style_variator.py
│   ├── emotion_state_machine.py
│   ├── context_referencer.py
│   ├── escalation_detector.py
│   ├── inner_outer_bridge.py
│   └── inner_shell/        # Inner shell research modules
│       ├── __init__.py
│       ├── finitude_engine.py
│       ├── incompleteness_model.py
│       ├── autonomous_questioner.py
│       ├── integration.py
│       └── api.py
├── config/                 # Configuration data (publishable)
│   ├── __init__.py        # Makes config a proper package
│   ├── schema.json        # JSON schema for validation
│   ├── en.json
│   ├── en_customer_support.json
│   ├── es.json
│   ├── es_sales.json
│   ├── ja.json
│   ├── ja_business.json
│   └── ja_freelancer.json
├── pyproject.toml         # PEP 517/518 build configuration
├── MANIFEST.in            # Include data files in distribution
└── README.md
```

## Configuration Files

### pyproject.toml

The `pyproject.toml` is the modern Python packaging configuration file (PEP 517/518):

#### Key Settings

- **name**: `human-persona` - Package name on PyPI
- **version**: `0.2.0` - Bumped from 0.1.0 to reflect inner shell additions
- **requires-python**: `>=3.10` - Minimum Python version
- **authors**: Rintaro Matsumoto (matsumotoinla@gmail.com)
- **license**: AGPL-3.0-or-later

#### Package Discovery

```toml
[tool.setuptools]
packages = ["core", "config"]

[tool.setuptools.package-data]
config = ["*.json"]
```

This configuration:
- Includes `core/` and `config/` packages in the distribution
- Includes all `*.json` files from the `config/` directory as package data
- Automatically finds subpackages (e.g., `core.inner_shell`)

#### Dependencies

```toml
requires-python = ">=3.10"
```

**Core library has no external dependencies** — it uses only the Python standard library.

#### Optional Dependencies

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.1.0"]
research = ["matplotlib>=3.7", "numpy>=1.24"]
```

- **dev**: Testing and linting tools (for development)
- **research**: Experimental/research features (matplotlib, numpy)

Install with: `pip install human-persona[dev]` or `pip install human-persona[research]`

#### Classifiers

Properly classified for PyPI discovery:
- Development Status :: 4 - Beta
- Intended Audience :: Developers, Science/Research
- Topic :: Scientific/Engineering :: Artificial Intelligence

### MANIFEST.in

The `MANIFEST.in` file ensures data files are included in source distributions:

```
recursive-include config *.json
include README.md
include LICENSE
include CONTRIBUTING.md
```

## Installation

### From PyPI (after publishing)

```bash
# Basic installation
pip install human-persona

# With development tools
pip install human-persona[dev]

# With research dependencies
pip install human-persona[research]

# Both
pip install human-persona[dev,research]
```

### From Source

```bash
# Development install (editable)
pip install -e .

# With dev dependencies
pip install -e ".[dev]"
```

## Package Exports

### core/__init__.py

Main package exports all key classes for easy importing:

```python
from core import (
    HumanPersonaBase,
    TimingController,
    StyleVariator,
    EmotionStateMachine,
    EmotionState,
    ContextReferencer,
    EscalationDetector,
    InnerOuterBridge,
    inner_shell,
)
```

### core/inner_shell/__init__.py

Inner shell module exports research components:

```python
from core.inner_shell import (
    FinitudeEngine,
    IncompletenessModel,
    AutonomousQuestioner,
    InnerShellIntegration,
    # ... and related data classes
)
```

### config/__init__.py

Configuration package declaration (minimal, as configs are JSON files).

## Building and Publishing

### Build Distribution

```bash
# Install build tools
pip install build

# Build wheel and source distribution
python -m build
```

This creates:
- `dist/human_persona-0.2.0-py3-none-any.whl` (wheel)
- `dist/human_persona-0.2.0.tar.gz` (source distribution)

### Publish to PyPI

```bash
# Install twine
pip install twine

# Upload to PyPI (requires credentials)
twine upload dist/human_persona-0.2.0*

# Upload to TestPyPI first (recommended)
twine upload --repository testpypi dist/human_persona-0.2.0*
```

## Verification

### Check Package Metadata

```bash
# Validate pyproject.toml
pip install build
python -m build --sdist --wheel --outdir /tmp/dist

# Check metadata
twine check /tmp/dist/*
```

### Test Installation

```bash
# Create a virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from wheel
pip install dist/human_persona-0.2.0-py3-none-any.whl

# Test imports
python -c "from core import HumanPersonaBase, inner_shell; print('OK')"
```

## Version Management

The version in `pyproject.toml` follows semantic versioning:

- **0.2.0** - Current (includes inner shell research)
  - Major: 0 (pre-1.0, breaking changes OK)
  - Minor: 2 (new features: inner shell)
  - Patch: 0 (no patch releases yet)

When updating:
- Patch version (0.2.1): Bug fixes only
- Minor version (0.3.0): New features (backwards compatible)
- Major version (1.0.0): Breaking changes or stability milestone

## Configuration Files Access

When installed, configuration files are accessible via package data:

```python
import importlib.resources
from pathlib import Path

# Python 3.10+
try:
    # Try Python 3.9+ API
    from importlib.resources import files
    config_dir = files('config')
except ImportError:
    # Fallback for older Python
    import pkg_resources
    config_dir = Path(pkg_resources.resource_filename('config', ''))

# Access a config file
ja_config = config_dir / 'ja.json'
```

Or manually:

```python
import json
from importlib import resources

# Load a config file
config_text = resources.read_text('config', 'ja.json')
config = json.loads(config_text)
```

## Excluded from Package

The following directories are NOT included in the PyPI package:

- **experiments/** - Research/experimental code
- **benchmarks/** - Performance benchmarks
- **tests/** - Test code (can be included separately if needed)
- **humanize/** - Legacy pipeline (deprecated)
- **articles/** - Documentation articles
- **docs/** - Documentation files
- **.github/** - GitHub CI/CD workflows

These are available on GitHub but not in the PyPI distribution.

## Next Steps

1. **Create GitHub Release** - Tag the commit with version: `git tag v0.2.0`
2. **Build Distribution** - `python -m build`
3. **Publish to PyPI** - `twine upload dist/*`
4. **Update Documentation** - Link to PyPI package page

## References

- [PEP 517 - A build-system independent format](https://www.python.org/dev/peps/pep-0517/)
- [PEP 518 - Specifying build system requirements](https://www.python.org/dev/peps/pep-0518/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [Python Packaging Guide](https://packaging.python.org/)
