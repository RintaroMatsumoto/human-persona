# Type Checking Checklist for Developers

Use this checklist when adding or modifying code in the `core/` modules.

## Before You Start

- [ ] Read `MYPY_SETUP.md` for type annotation conventions
- [ ] Understand Python 3.10+ type syntax (use `|` not `Union`)
- [ ] Know the project targets Python 3.10+

## For New Functions

- [ ] Add parameter type annotations to all arguments
- [ ] Add return type hint (even if `None`)
- [ ] Use modern syntax: `int | None` not `Optional[int]`
- [ ] Use modern syntax: `dict[str, Any]` not `Dict[str, Any]`
- [ ] Avoid bare `Any` unless necessary (add comment if you must)
- [ ] Write docstring with Args and Returns sections

### Example Template

```python
def new_function(self, param1: str, param2: int | None = None) -> dict[str, Any]:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1 and its purpose.
        param2: Optional. Description of param2.
    
    Returns:
        Description of the returned value and its structure.
    """
    # Implementation here
    return {}
```

## For New Classes

- [ ] Add type hints to all `__init__` parameters
- [ ] Type all instance attributes in `__init__`
- [ ] Add return type to all methods (including properties)
- [ ] Use dataclasses for data-holding classes
- [ ] Use Enum for enumerated types

### Example Template

```python
from dataclasses import dataclass

@dataclass
class MyData:
    """Brief description of this data class."""
    field1: str
    field2: int | None = None

class MyClass:
    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize MyClass."""
        self.field1: str = config.get('field1', 'default')
        self.field2: list[str] = []
    
    def method(self, arg: str) -> str:
        """Do something with arg."""
        return arg.upper()
```

## Before Committing

- [ ] Run verification: `python verify_types.py`
- [ ] All core modules show "All functions typed ✓"
- [ ] No "missing return types" or "untyped parameters" warnings
- [ ] If modifying an existing file, check all new code has types
- [ ] Run your local tests to ensure functionality

## When Modifying Existing Code

- [ ] If changing a function signature, update type hints
- [ ] If adding new parameters, type them
- [ ] If changing return type, update the annotation
- [ ] Don't remove type hints (make them more general if needed)

## Common Type Patterns

### Optional Values
```python
# Modern (preferred)
value: int | None = None

# Also acceptable
value: int = None  # If explicitly optional
```

### Collections
```python
# Modern (preferred)
items: list[str]
mapping: dict[str, int]
pair: tuple[str, int]

# Avoid
from typing import List, Dict, Tuple
items: List[str]
mapping: Dict[str, int]
pair: Tuple[str, int]
```

### Union Types
```python
# Modern (preferred)
value: int | str
result: str | list[str]

# Avoid
from typing import Union
value: Union[int, str]
result: Union[str, List[str]]
```

### Callable Types
```python
from typing import Callable

# Function that takes int, returns str
handler: Callable[[int], str]

# Function with multiple args
operation: Callable[[int, int], int]
```

### Generic Types
```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value: T = value
    
    def get(self) -> T:
        return self.value
```

## Type Checking Command Reference

### Quick Check (No Installation Required)
```bash
python verify_types.py
```

### Full Mypy Check (After Installation)
```bash
python -m mypy core/ --strict --show-error-codes
```

### Check Single Module
```bash
python -m mypy core/base_persona.py --strict
```

### Install Mypy
```bash
pip install mypy>=1.5.0 types-setuptools
```

## Troubleshooting

### "Function is missing a type comment"
**Solution**: Add return type hint
```python
# Before
def get_value(self):
    return self.value

# After
def get_value(self) -> str:
    return self.value
```

### "Argument has incompatible type"
**Solution**: Update parameter or return type to accept both
```python
# Before
def process(self, value: int) -> None:
    process("string")  # Error: str incompatible with int

# After
def process(self, value: int | str) -> None:
    process("string")  # OK
```

### "Variable is partially defined"
**Solution**: Define variable with union type before branching
```python
# Before
if condition:
    result: str = "value"
else:
    result: int = 42  # Error: type changed

# After
result: str | int
if condition:
    result = "value"
else:
    result = 42
```

### "Implicit Optional detected"
**Solution**: Explicitly type as Optional or use `| None`
```python
# Before
def method(self, value: str = None) -> None:  # Error: implicit Optional

# After
def method(self, value: str | None = None) -> None:
    ...
```

## Type Annotations Best Practices

1. **Be Specific**: Use specific types, avoid bare `Any`
   ```python
   # Good
   data: dict[str, int]
   
   # Avoid
   data: Any
   ```

2. **Use Union for Multiple Types**: Don't use `Any`
   ```python
   # Good
   value: int | str
   
   # Avoid
   value: Any
   ```

3. **Dataclasses for Data**: Use `@dataclass` for data holders
   ```python
   @dataclass
   class Message:
       role: str
       content: str
   ```

4. **Enums for Choices**: Use `Enum` for fixed sets
   ```python
   class Status(Enum):
       PENDING = "pending"
       COMPLETE = "complete"
   ```

5. **Type Aliases for Complex Types**: Define reusable types
   ```python
   MessageDict = dict[str, str | int]
   
   def process(msg: MessageDict) -> None:
       ...
   ```

## Continuous Improvement

- [ ] Review mypy errors weekly
- [ ] Update type hints when refactoring
- [ ] Run full check before major releases
- [ ] Keep Python version up to date
- [ ] Stay updated on typing improvements

## Getting Help

1. Check `MYPY_SETUP.md` for comprehensive documentation
2. Review existing typed code in core/ for examples
3. Check [MyPy documentation](https://mypy.readthedocs.io/)
4. Ask in project GitHub issues for complex cases

## Quick Reference: File Locations

- **Configuration**: `pyproject.toml`
- **Marker file**: `core/py.typed`
- **Documentation**: `MYPY_SETUP.md`
- **Quick check**: `verify_types.py`
- **Linux/macOS**: `run_mypy.sh`
- **Windows**: `run_mypy.bat`
- **This checklist**: `TYPE_CHECKING_CHECKLIST.md`
- **Summary**: `TYPE_CHECKING_SUMMARY.md`
