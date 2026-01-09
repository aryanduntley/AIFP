# Directive: fp_no_oop

**Type**: FP Core
**Level**: 1 (Critical)
**Parent Directive**: None
**Priority**: CRITICAL - Required for all FP compliance

---

## Purpose

The `fp_no_oop` directive prohibits object-oriented programming (OOP) constructs in AIFP codebases. This includes classes, inheritance, polymorphism, encapsulation, and stateful methods. Instead, AIFP enforces a **functional procedural** paradigm using pure functions, immutable data structures, and explicit data flow.

This directive is **core to AIFP's philosophy** - OOP introduces hidden state, mutable objects, and complex inheritance hierarchies that make code harder to reason about, test, and parallelize. By eliminating OOP, AIFP ensures:
- **Simplicity**: Functions operate on data; no object hierarchies
- **Explicitness**: All state passed as parameters, no hidden `self`/`this`
- **Testability**: No complex object setup; functions test in isolation
- **Composability**: Functions compose naturally; objects require adapters
- **Predictability**: No method overrides or dynamic dispatch surprises
- **Parallelizability**: No shared object state means safe concurrency

When applied, this directive analyzes code for:
1. **Class definitions** (`class Foo:`)
2. **Inheritance** (`class Bar(Foo):`)
3. **Instance methods** (methods with `self`)
4. **Instance state** (`self.attribute`)
5. **Constructors and initializers** (`__init__`, `__new__`)
6. **Abstract base classes and protocols**
7. **Polymorphism patterns** (method overriding, duck typing)

If OOP constructs are detected, the directive refactors code into flat, functional modules or prompts the user for guidance.

**Important**: This directive is reference documentation for no-OOP patterns.
AI consults this when uncertain about OOP alternatives or refactoring complex class hierarchies.

**No-OOP is baseline behavior**:
- AI writes functional code naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex OOP refactoring scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about functional alternatives to classes
- Complex class hierarchy refactoring decisions
- Need for patterns to replace inheritance or polymorphism
- Library integration requiring OOP wrappers

**Context**:
- AI writes function-based code as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_wrapper_generation`) may reference this for OOP wrapping guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: scan_code_for_oop

Scans code for OOP constructs and patterns.

**Steps**:
1. **Parse AST** - Build abstract syntax tree of code
2. **Detect class definitions** - Find `class` keyword usage
3. **Detect inheritance** - Find base classes and super() calls
4. **Detect instance methods** - Find methods with `self` parameter
5. **Detect instance state** - Find `self.attribute` patterns
6. **Detect OOP patterns** - Find polymorphism, encapsulation
7. **Classify violations** - Categorize OOP usage by severity

### Branches

**Branch 1: If class_detected**
- **Then**: `refactor_to_module_function`
- **Details**: Convert class to module with functions
  - Extract methods as standalone functions
  - Convert instance state to function parameters
  - Move class-level constants to module-level constants
  - Replace constructors with data creation functions
  - Use frozen dataclasses for data structures (no methods)
- **Result**: Returns refactored code with no classes

**Branch 2: If method_with_state**
- **Then**: `convert_to_pure_function`
- **Details**: Convert stateful methods to pure functions
  - Remove `self` parameter
  - Add instance state as explicit parameters
  - Remove side effects (mutations of `self`)
  - Return new state instead of modifying
- **Result**: Returns pure functions with explicit state

**Fallback**: `mark_as_compliant`
- **Details**: No OOP constructs detected
  - Code uses only functions and data structures
  - No classes, methods, or inheritance
- **Result**: Code passes OOP elimination check

---

## Examples

### ✅ Compliant Code

**Functional Module (No Classes):**
```python
"""Calculator module - pure functional style."""
from dataclasses import dataclass

@dataclass(frozen=True)
class CalculatorState:
    """Immutable state (data only, no methods)."""
    memory: float
    last_result: float

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def store_result(state: CalculatorState, result: float) -> CalculatorState:
    """Store result in memory. Returns new state."""
    return CalculatorState(memory=result, last_result=state.last_result)

# Usage (functional style)
state = CalculatorState(memory=0.0, last_result=0.0)
result = add(5, 3)
new_state = store_result(state, result)
```

**Why Compliant**:
- Uses frozen dataclass for data (no methods)
- All functions are standalone (no `self`)
- State passed explicitly
- No inheritance or polymorphism

---

**Pure Functions (No Object State):**
```python
"""User management - pure functional style."""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class User:
    """Immutable user data (no methods)."""
    id: int
    name: str
    email: str
    is_active: bool

def create_user(id: int, name: str, email: str) -> User:
    """Create a new user."""
    return User(id=id, name=name, email=email, is_active=True)

def deactivate_user(user: User) -> User:
    """Deactivate user. Returns new user."""
    return User(id=user.id, name=user.name, email=user.email, is_active=False)

def update_email(user: User, new_email: str) -> User:
    """Update email. Returns new user."""
    return User(id=user.id, name=user.name, email=new_email, is_active=user.is_active)

# Usage
user = create_user(1, "Alice", "alice@example.com")
deactivated = deactivate_user(user)
updated = update_email(user, "alice@newdomain.com")
```

**Why Compliant**:
- Dataclass has no methods (data only)
- Functions operate on data immutably
- No hidden state
- No inheritance

---

### ❌ Non-Compliant Code

**OOP Class with Methods:**
```python
# ❌ VIOLATION: OOP class with methods and state
class Calculator:
    """Calculator using OOP."""

    def __init__(self):
        self.memory = 0.0  # ← Instance state
        self.last_result = 0.0

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        self.last_result = a + b  # ← Mutates state
        return self.last_result

    def store_result(self, result: float):
        """Store result in memory."""
        self.memory = result  # ← Mutates state

# Usage
calc = Calculator()
result = calc.add(5, 3)  # Hidden state mutation
```

**Why Non-Compliant**:
- Uses class with methods
- Hidden state (`self.memory`, `self.last_result`)
- Mutations of instance state
- Not functional

**Refactored (Functional):**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class CalculatorState:
    """Immutable state (data only)."""
    memory: float
    last_result: float

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def store_result(state: CalculatorState, result: float) -> CalculatorState:
    """Store result. Returns new state."""
    return CalculatorState(memory=result, last_result=state.last_result)

# Usage
state = CalculatorState(memory=0.0, last_result=0.0)
result = add(5, 3)
new_state = store_result(state, result)
```

---

**OOP Inheritance:**
```python
# ❌ VIOLATION: Inheritance hierarchy
class Animal:
    def __init__(self, name: str):
        self.name = name

    def make_sound(self) -> str:
        raise NotImplementedError

class Dog(Animal):  # ← Inheritance
    def make_sound(self) -> str:
        return "Woof"

class Cat(Animal):  # ← Inheritance
    def make_sound(self) -> str:
        return "Meow"

# Polymorphism
animals = [Dog("Buddy"), Cat("Whiskers")]
for animal in animals:
    print(animal.make_sound())  # Dynamic dispatch
```

**Why Non-Compliant**:
- Class inheritance hierarchy
- Polymorphism via method overriding
- Dynamic dispatch
- Hidden complexity

**Refactored (Functional):**
```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class Animal:
    """Immutable animal data (no methods)."""
    name: str
    type: Literal["dog", "cat"]

def make_sound(animal: Animal) -> str:
    """Pure function with pattern matching."""
    match animal.type:
        case "dog":
            return "Woof"
        case "cat":
            return "Meow"
        case _:
            return "Unknown"

# Usage
animals = (
    Animal(name="Buddy", type="dog"),
    Animal(name="Whiskers", type="cat"),
)
sounds = tuple(make_sound(a) for a in animals)
```

---

**OOP Encapsulation:**
```python
# ❌ VIOLATION: Private state and getters/setters
class BankAccount:
    def __init__(self, balance: float):
        self._balance = balance  # ← "Private" state

    def get_balance(self) -> float:  # ← Getter
        return self._balance

    def deposit(self, amount: float):  # ← Mutator
        if amount > 0:
            self._balance += amount  # ← Mutation

    def withdraw(self, amount: float) -> bool:  # ← Mutator
        if amount <= self._balance:
            self._balance -= amount  # ← Mutation
            return True
        return False

# Usage
account = BankAccount(100.0)
account.deposit(50.0)
```

**Why Non-Compliant**:
- Encapsulated state
- Getters/setters
- Mutations
- Hidden state changes

**Refactored (Functional):**
```python
from dataclasses import dataclass
from returns.result import Result, Success, Failure

@dataclass(frozen=True)
class BankAccount:
    """Immutable account data."""
    balance: float

def deposit(account: BankAccount, amount: float) -> Result[BankAccount, str]:
    """Deposit amount. Returns new account or error."""
    if amount <= 0:
        return Failure("Amount must be positive")
    return Success(BankAccount(balance=account.balance + amount))

def withdraw(account: BankAccount, amount: float) -> Result[BankAccount, str]:
    """Withdraw amount. Returns new account or error."""
    if amount > account.balance:
        return Failure("Insufficient funds")
    return Success(BankAccount(balance=account.balance - amount))

# Usage
account = BankAccount(balance=100.0)
result = deposit(account, 50.0)
match result:
    case Success(new_account):
        print(f"New balance: {new_account.balance}")
    case Failure(error):
        print(f"Error: {error}")
```

---

## Edge Cases

### Edge Case 1: Dataclasses with Methods

**Issue**: Dataclasses can have methods (not allowed)

**Handling**:
```python
# ❌ Dataclass with methods
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_from_origin(self) -> float:  # ← Method not allowed
        return (self.x ** 2 + self.y ** 2) ** 0.5

# ✅ Dataclass data only, function separate
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    """Point data (no methods)."""
    x: float
    y: float

def distance_from_origin(point: Point) -> float:
    """Calculate distance from origin."""
    return (point.x ** 2 + point.y ** 2) ** 0.5
```

**Directive Action**: Frozen dataclasses allowed for data structures ONLY. No methods.

---

### Edge Case 2: Third-Party OOP Libraries

**Issue**: External libraries use OOP (can't refactor)

**Handling**:
```python
# ✅ Wrap OOP library in functional interface
import requests  # OOP library

def http_get(url: str) -> Result[str, str]:
    """Functional wrapper for requests.get()."""
    try:
        response = requests.get(url)  # OOP call isolated
        response.raise_for_status()
        return Success(response.text)
    except Exception as e:
        return Failure(str(e))

# Usage (functional style)
result = http_get("https://api.example.com/data")
```

**Directive Action**: Isolate OOP library calls in effect wrappers. Escalate to `fp_wrapper_generation`.

---

### Edge Case 3: Protocols and Abstract Base Classes

**Issue**: Python typing uses Protocols (looks like OOP)

**Handling**:
```python
# ❌ Protocol with methods (not allowed for implementation)
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

# ✅ Use type unions or callbacks instead
from typing import Callable

DrawFunction = Callable[[Canvas], Canvas]

def draw_circle(canvas: Canvas) -> Canvas:
    """Draw circle on canvas."""
    return add_shape(canvas, Circle(radius=10))
```

**Directive Action**: Avoid Protocols for code structure. Use function types and composition.

---

### Edge Case 4: Exception Classes

**Issue**: Python exceptions are classes

**Handling**:
```python
# ❌ Custom exception class
class InvalidInputError(Exception):
    pass

# ✅ Use Result types instead of exceptions
from returns.result import Result, Success, Failure

def validate_input(value: int) -> Result[int, str]:
    """Validate input. Returns Result."""
    if value < 0:
        return Failure("Value must be non-negative")
    return Success(value)
```

**Directive Action**: Use Result/Either types. Avoid exceptions. When necessary, use standard library exceptions only.

---

## Related Directives

- **Depends On**: None (foundational directive)
- **Works With**:
  - `fp_purity` - OOP often introduces impurity; eliminating OOP helps purity
  - `fp_immutability` - OOP objects are often mutable; eliminating OOP helps immutability
  - `fp_state_elimination` - OOP encapsulates state; eliminating OOP removes hidden state
- **Called By**:
  - `project_file_write` - Validates no OOP before writing files
  - `project_compliance_check` - Project-wide OOP elimination verification
- **Escalates To**:
  - `fp_wrapper_generation` - For wrapping OOP libraries
  - `fp_inheritance_flattening` - For flattening complex class hierarchies

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Marks functions as OOP-free with `oop_compliant = true`

**Tracking** (Optional - Disabled by Default):

If tracking is enabled:
- **`tracking_notes`** (user_preferences.db): Logs FP analysis with `note_type='fp_analysis'`

Only occurs when `fp_flow_tracking` is enabled via `tracking_toggle`.
Token overhead: ~5% per file write.
Most users will never enable this. It's for AIFP development and debugging only.

**Note**: When tracking is enabled, use helper functions from user_preferences helpers (e.g., `add_tracking_note`, `get_tracking_notes`, `search_tracking_notes`) to log FP analysis data. Never write SQL directly.
---
---

## Testing

How to verify this directive is working:

1. **Write class with methods** → Directive detects and refactors
   ```python
   # Input (OOP)
   class Calc:
       def add(self, a, b): return a + b

   # Expected output (functional)
   def add(a: int, b: int) -> int: return a + b
   ```

2. **Write pure functions** → Directive marks compliant
   ```python
   def add(a: int, b: int) -> int: return a + b
   # ✅ No OOP, compliant
   ```

3. **Write dataclass with methods** → Directive removes methods
   ```python
   # Input (dataclass with methods)
   @dataclass
   class Point:
       x: int
       def distance(self): return abs(self.x)

   # Expected output (data only)
   @dataclass(frozen=True)
   class Point:
       x: int

   def distance(point: Point) -> int:
       return abs(point.x)
   ```

---

## Common Mistakes

- ❌ **Using dataclasses with methods** - Dataclasses should be data only
- ❌ **Assuming static methods are functional** - Still part of class namespace
- ❌ **Creating factory classes** - Use factory functions instead
- ❌ **Using `self` parameter** - Functions should not have `self`
- ❌ **Inheriting from non-frozen dataclasses** - No inheritance allowed

---

## Roadblocks and Resolutions

### Roadblock 1: oop_construct
**Issue**: Class definition detected
**Resolution**: Flatten class into module with functions and frozen dataclass for data

### Roadblock 2: stateful_method
**Issue**: Method with `self` and instance state
**Resolution**: Convert to stateless function with state passed as parameters

---

## References

None
---

*Part of AIFP v1.0 - Critical FP Core directive for OOP elimination*
