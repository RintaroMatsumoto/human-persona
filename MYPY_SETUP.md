# Mypy Strict Type Checking Setup

This document describes the mypy configuration and type checking setup for the human-persona project.

## Overview

The `human-persona` project now includes strict mypy type checking to ensure type safety across all core modules. This provides:

- Static type error detection
- IDE integration and autocompletion
- Better code maintainability
- Compliance with PEP 561 (typed package marker)

## Configuration

Type checking configuration is defined in `pyproject.toml` under `[tool.mypy]`:

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_calls = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true
```

### Key Settings

- **python_version = "3.10"**: Type checking target (matches project requirements)
- **disallow_untyped_defs = true**: All functions must have explicit type hints
- **disallow_incomplete_defs = true**: All type hints must be fully specified
- **disallow_untyped_calls = true**: All function calls must have typed callables
- **no_implicit_optional = true**: Prevent implicit `Optional` types

### Overrides

Tests and experiments are excluded from strict checking:

```toml
[[tool.mypy.overrides]]
module = "tests.*"
ignore_errors = true

[[tool.mypy.overrides]]
module = "experiments.*"
ignore_errors = true
```

## PEP 561 Marker

The file `core/py.typed` marks this package as type-hinted (PEP 561), enabling type checking for consumers of this library.

## Running Type Checks

### Prerequisites

Install mypy and its dependencies:

```bash
pip install mypy>=1.5.0 types-setuptools
```

### Run Type Checking

**On Linux/macOS:**

```bash
./run_mypy.sh
```

**On Windows:**

```cmd
run_mypy.bat
```

**Manually (all platforms):**

```bash
python -m mypy core/ --strict --show-error-codes --show-error-context
```

### Example Output

```
core/base_persona.py:100: error: Argument 1 to "TimingController" has incompatible type "dict[str, Any]"; expected "dict[str, Any]"  [arg-type]
core/timing_controller.py:45: error: Function is missing a type comment  [no-untyped-def]
```

## Type Annotations in Core Modules

All core modules include comprehensive type annotations:

### base_persona.py

```python
def process_message(self, user_message: str) -> PersonaResponse:
    """Process a user message end-to-end."""
    ...
```

### timing_controller.py

```python
def calculate_delay(self, user_message: str, response: str, turn_count: int) -> float:
    """Calculate delay for a given response."""
    ...
```

### style_variator.py

```python
def apply_variation(
    self, text: str, register: Register | str = Register.CASUAL, emotion: str | None = None
) -> str:
    """Apply stylistic variation to text."""
    ...
```

### emotion_state_machine.py

```python
def update(self, user_message: str) -> None:
    """Update emotion state based on user message."""
    ...
```

### context_referencer.py

```python
def find_context_by_topic(self, topic: str) -> ContextRef | None:
    """Find earlier message mentioning a specific topic."""
    ...
```

### escalation_detector.py

```python
def check(
    self,
    user_message: str,
    conversation_history: list[Any],
    raw_response: str | None = None
) -> EscalationResult:
    """Check if conversation should escalate to human."""
    ...
```

### config_validator.py

```python
def validate(self, config: dict[str, Any]) -> ValidationResult:
    """Validate a configuration dict against the schema."""
    ...
```

### inner_outer_bridge.py

```python
def apply_modulation(
    self,
    outer_shell_controller: Any,
    modulation: ModulationValues | None = None
) -> None:
    """Apply inner shell modulations to outer shell controller."""
    ...
```

## Type Hint Conventions

### Use Modern Syntax (Python 3.10+)

Prefer the new union syntax over `typing.Union`:

```python
# Good
def func(x: int | None) -> str | list[str]: ...

# Avoid
from typing import Union, Optional, List
def func(x: Optional[int]) -> Union[str, List[str]]: ...
```

### Use `dict[K, V]` Instead of `Dict[K, V]`

```python
# Good
def config(cfg: dict[str, Any]) -> None: ...

# Avoid
from typing import Dict
def config(cfg: Dict[str, Any]) -> None: ...
```

### Use `list[T]` Instead of `List[T]`

```python
# Good
def messages(history: list[Message]) -> None: ...

# Avoid
from typing import List
def messages(history: List[Message]) -> None: ...
```

### Explicit Return Types

Always specify return types, even for `None`:

```python
# Good
def reset(self) -> None:
    self.state = initial_state

# Avoid
def reset(self):
    self.state = initial_state
```

### Optional Parameters

Use `| None` for optional parameters:

```python
# Good
def process(self, message: str, emotion: str | None = None) -> str: ...

# Avoid
def process(self, message: str, emotion: Optional[str] = None) -> str: ...
```

## Integration with Tools

### IDE Integration

Most modern IDEs (PyCharm, VSCode with Pylance) will use mypy configuration automatically:

- **PyCharm**: Preferences → Project → Python → Code Analysis → Mypy
- **VSCode**: Install Pylance extension and configure in `settings.json`

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python -m mypy core/ --strict || exit 1
```

### CI/CD Integration

Add to GitHub Actions or CI pipeline:

```yaml
- name: Type check with mypy
  run: |
    pip install mypy>=1.5.0 types-setuptools
    python -m mypy core/ --strict --show-error-codes
```

## Common Type Errors and Fixes

### Error: Function is missing a type comment

**Problem**: Function has no return type annotation

```python
# Error
def get_value(self):  # Missing return type
    return self.value

# Fixed
def get_value(self) -> str:
    return self.value
```

### Error: Argument has incompatible type

**Problem**: Argument type doesn't match parameter annotation

```python
# Error
def func(x: int) -> None:
    func("string")  # str incompatible with int

# Fixed
def func(x: int | str) -> None:
    func("string")  # OK
```

### Error: Variable is partially defined

**Problem**: Variable assigned different types in different branches

```python
# Error
if condition:
    result: str = "value"
else:
    result: int = 42  # Type mismatch

# Fixed
result: str | int
if condition:
    result = "value"
else:
    result = 42
```

## Updating Type Hints

When modifying core modules:

1. **Add type hints to all new functions/methods**
2. **Run mypy before committing**: `python -m mypy core/ --strict`
3. **Fix any reported errors**
4. **Update return types if changing function behavior**

## Further Reading

- [MyPy Documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [PEP 561 - Distributing and Packaging Type Information](https://www.python.org/dev/peps/pep-0561/)
- [MyPy Strict Mode](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict)

## Questions?

For type-related questions, check:
1. The mypy documentation
2. The type hints in similar functions in the codebase
3. Open an issue in the GitHub repository
