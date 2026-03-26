# Quick Start: Type Checking in human-persona

## TL;DR

All core modules now have strict type checking. Here's what you need to know:

### Check Types (No Installation Required)
```bash
python verify_types.py
```

### Install & Run Full Check
```bash
pip install mypy>=1.5.0 types-setuptools
python -m mypy core/ --strict
```

## 5-Minute Overview

### What Changed?

All 8 core modules now have complete type annotations:
- `base_persona.py` - Base persona class
- `timing_controller.py` - Response timing
- `style_variator.py` - Linguistic variation
- `emotion_state_machine.py` - Emotion tracking
- `context_referencer.py` - Conversation memory
- `escalation_detector.py` - Escalation detection
- `config_validator.py` - Config validation
- `inner_outer_bridge.py` - Inner/outer shell bridge

### What Do I Do?

**When writing new code:**
1. Add type hints to all parameters: `param: str`
2. Add return types: `-> str`
3. Use modern syntax: `int | None` (not `Optional[int]`)
4. Run `python verify_types.py` before committing

**Example:**
```python
def process(self, message: str, emotion: str | None = None) -> dict[str, Any]:
    """Process a message with optional emotion."""
    result: dict[str, Any] = {}
    # implementation
    return result
```

## Type Syntax Cheat Sheet

### Parameters & Returns
```python
# Simple types
param: int
param: str
param: bool

# Optional values
param: int | None

# Multiple types
param: int | str

# Collections
param: list[str]
param: dict[str, int]
param: tuple[str, int]

# Return type
def func() -> str:
    return "value"

# Return optional
def func() -> str | None:
    return None

# Return dict
def func() -> dict[str, Any]:
    return {}
```

## File Structure

```
human-persona/
├── core/
│   ├── base_persona.py       ← Fully typed
│   ├── timing_controller.py  ← Fully typed
│   ├── style_variator.py     ← Fully typed
│   ├── emotion_state_machine.py  ← Fully typed
│   ├── context_referencer.py ← Fully typed
│   ├── escalation_detector.py   ← Fully typed
│   ├── config_validator.py   ← Fully typed
│   ├── inner_outer_bridge.py ← Fully typed
│   └── py.typed              ← PEP 561 marker
├── pyproject.toml            ← Mypy config added
├── verify_types.py           ← Quick type check
├── run_mypy.sh              ← Linux/macOS script
├── run_mypy.bat             ← Windows script
├── MYPY_SETUP.md            ← Full documentation
├── TYPE_CHECKING_CHECKLIST.md ← Developer guide
├── TYPE_CHECKING_SUMMARY.md ← Implementation details
├── IMPLEMENTATION_REPORT.md  ← Full report
└── QUICK_START_TYPING.md    ← This file
```

## Most Important Rules

1. **All functions must have return types** (even `None`)
2. **All parameters must have types** (no bare `param`)
3. **Use modern syntax** (`int | None`, not `Optional[int]`)
4. **Run verify_types.py** before committing
5. **Check MYPY_SETUP.md** if you're unsure

## Common Examples

### Function with Types
```python
def calculate_delay(self, text: str, turns: int) -> float:
    """Calculate response delay."""
    delay = len(text) * 0.01 + turns * 0.5
    return delay
```

### Method with Optional Parameter
```python
def apply_emotion(self, text: str, emotion: str | None = None) -> str:
    """Apply emotion to text."""
    if emotion is None:
        emotion = "neutral"
    return f"{emotion}: {text}"
```

### Class with Types
```python
from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str
    timestamp: float

class MyClass:
    def __init__(self, config: dict[str, Any]) -> None:
        self.messages: list[Message] = []
    
    def add_message(self, msg: Message) -> None:
        self.messages.append(msg)
```

### Enum with Types
```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    COMPLETE = "complete"

def set_status(self, status: Status) -> None:
    self.status = status
```

## Troubleshooting

### "Missing return type"
```python
# Wrong
def get_name(self):
    return "Alice"

# Right
def get_name(self) -> str:
    return "Alice"
```

### "Missing parameter type"
```python
# Wrong
def greet(self, name):
    return f"Hello {name}"

# Right
def greet(self, name: str) -> str:
    return f"Hello {name}"
```

### "Untyped parameter"
```python
# Wrong
def func(self, *, optional_param=None):
    pass

# Right
def func(self, *, optional_param: int | None = None) -> None:
    pass
```

## IDE Setup

### PyCharm
1. Settings → Project → Python → Code Analysis
2. Enable "Mypy"
3. Check "Run mypy in strict mode"

### VSCode
1. Install "Pylance" extension
2. Set in settings.json:
   ```json
   {
     "pylance.typeCheckingMode": "strict"
   }
   ```

## Running Checks

### Before Committing
```bash
python verify_types.py
```

### Full Check (After Installing)
```bash
python -m mypy core/ --strict
```

### Specific Module
```bash
python -m mypy core/base_persona.py --strict
```

## Documentation Files

| File | Purpose |
|------|---------|
| `MYPY_SETUP.md` | Complete mypy guide |
| `TYPE_CHECKING_CHECKLIST.md` | Developer checklist |
| `TYPE_CHECKING_SUMMARY.md` | Implementation details |
| `IMPLEMENTATION_REPORT.md` | Full report with metrics |
| `QUICK_START_TYPING.md` | This file (quick reference) |

## Key Points to Remember

✓ Type hints are required for all new code  
✓ Use `int | None` instead of `Optional[int]`  
✓ Use `list[T]` instead of `List[T]`  
✓ Always add `-> ReturnType` to functions  
✓ Run `verify_types.py` before committing  
✓ Check MYPY_SETUP.md for detailed guidance  

## Getting Help

1. **Quick check**: `python verify_types.py`
2. **Documentation**: Read `MYPY_SETUP.md`
3. **Examples**: Look at typed code in `core/`
4. **Issues**: Check `TYPE_CHECKING_CHECKLIST.md` troubleshooting

---

**Status**: All core modules fully typed ✅  
**Coverage**: 100% type annotation coverage  
**Target**: Python 3.10+  

Start typing! 🚀
