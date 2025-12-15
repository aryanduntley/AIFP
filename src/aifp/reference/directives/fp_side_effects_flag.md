# fp_side_effects_flag

## Purpose

The `fp_side_effects_flag` directive detects, isolates, and flags side effects in functions to ensure transparent handling within FP boundaries. It scans function bodies for side-effecting operations (I/O, mutation, global state access, logging) and either wraps them in effect functions, refactors them to pure equivalents, or explicitly documents them. This maintains functional purity while allowing necessary effectful operations at controlled boundaries.

**Category**: Side Effects
**Type**: FP Core
**Priority**: Critical
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`scan_for_effects`**: Analyze function body for side-effecting operations (I/O, mutations, logging, external calls).

### Branches

1. **`io_found`** → **`wrap_in_io_function`**
   - **Condition**: Detects I/O operations (file read/write, network calls, console output)
   - **Action**: Isolate I/O into dedicated effect functions at boundaries
   - **Details**: Separate pure logic from I/O effects
   - **Output**: Pure core function + I/O effect wrapper

2. **`global_mutation`** → **`refactor_to_pure`**
   - **Condition**: Detects global variable mutation or external state modification
   - **Action**: Refactor to pass state explicitly as parameters
   - **Details**: Eliminate global dependencies, make state explicit
   - **Output**: Pure function with explicit state parameters

3. **`logging_detected`** → **`redirect_to_logger_function`**
   - **Condition**: Detects logging statements within function
   - **Action**: Extract logging to effect boundary or return log data
   - **Details**: Convert inline logging to data return for external handling
   - **Output**: Pure function returning computation + log data

4. **`hidden_side_effect`** → **`flag_and_document`**
   - **Condition**: Detects side effects that cannot be easily isolated
   - **Action**: Flag function as impure, document side effects
   - **Details**: Add metadata indicating side effects present
   - **Output**: Documented impure function with effect description

5. **`no_effects`** → **`mark_as_clean`**
   - **Condition**: No side effects detected
   - **Action**: Mark function as pure and side-effect-free
   - **Output**: Pure function confirmation

6. **Fallback** → **`prompt_user`**
   - **Condition**: Side effects unclear or require domain knowledge
   - **Action**: Request user clarification on effect handling

### Error Handling
- **On failure**: Prompt user with side effect analysis details
- **Low confidence** (< 0.7): Request user review before refactoring

---

## Refactoring Strategies

### Strategy 1: I/O Isolation - File Operations
Separate file I/O from pure business logic.

**Before (Python - Non-Compliant)**:
```python
def process_user_data(filename):
    """Impure: mixes I/O with logic."""
    with open(filename, 'r') as f:
        data = f.read()

    lines = data.split('\n')
    users = [parse_user_line(line) for line in lines]
    active_users = [u for u in users if u['active']]

    with open('output.txt', 'w') as f:
        for user in active_users:
            f.write(f"{user['name']}\n")

    return len(active_users)
```

**After (Python - Compliant)**:
```python
# Pure business logic (no I/O)
def filter_active_users(users: list[dict]) -> list[dict]:
    """Pure function: filters active users."""
    return [u for u in users if u['active']]

def format_user_names(users: list[dict]) -> str:
    """Pure function: formats user names."""
    return '\n'.join(u['name'] for u in users)

# I/O boundary (effect functions)
def read_users_from_file(filename: str) -> list[dict]:
    """Effect: reads user data from file."""
    with open(filename, 'r') as f:
        data = f.read()
    lines = data.split('\n')
    return [parse_user_line(line) for line in lines]

def write_names_to_file(filename: str, content: str) -> None:
    """Effect: writes content to file."""
    with open(filename, 'w') as f:
        f.write(content)

# Composition at boundary
def process_user_data_pure(filename: str) -> int:
    """Orchestration with explicit I/O boundaries."""
    # Effect: read
    users = read_users_from_file(filename)

    # Pure: transform
    active_users = filter_active_users(users)
    output_content = format_user_names(active_users)

    # Effect: write
    write_names_to_file('output.txt', output_content)

    return len(active_users)
```

### Strategy 2: Global State Elimination
Convert global state access to explicit parameters.

**Before (Python - Non-Compliant)**:
```python
# Global state (bad!)
DATABASE_CONNECTION = create_connection()

def get_user(user_id):
    """Impure: accesses global database connection."""
    cursor = DATABASE_CONNECTION.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()
```

**After (Python - Compliant)**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class DatabaseConfig:
    connection_string: str
    timeout: int

# Pure function: generates query
def create_user_query(user_id: int) -> tuple[str, tuple]:
    """Pure: constructs SQL query."""
    return ("SELECT * FROM users WHERE id = ?", (user_id,))

# Effect function: executes query
def execute_query(
    config: DatabaseConfig,
    query: str,
    params: tuple
) -> Optional[dict]:
    """Effect: executes database query (explicit dependency)."""
    connection = create_connection(config)
    cursor = connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    connection.close()
    return result

# Orchestration
def get_user(user_id: int, config: DatabaseConfig) -> Optional[dict]:
    """Get user with explicit database dependency."""
    query, params = create_user_query(user_id)
    return execute_query(config, query, params)
```

### Strategy 3: Logging Extraction
Convert inline logging to data return for external handling.

**Before (Python - Non-Compliant)**:
```python
import logging

def calculate_discount(price, user_type):
    """Impure: side effect via logging."""
    logging.info(f"Calculating discount for {user_type}")

    if user_type == "premium":
        discount = price * 0.20
        logging.info(f"Applied premium discount: {discount}")
        return discount
    else:
        discount = price * 0.10
        logging.info(f"Applied standard discount: {discount}")
        return discount
```

**After (Python - Compliant)**:
```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class DiscountResult:
    amount: float
    user_type: str
    log_messages: tuple[str, ...]

def calculate_discount_pure(
    price: float,
    user_type: Literal["premium", "standard"]
) -> DiscountResult:
    """Pure: returns computation + log data."""
    logs = [f"Calculating discount for {user_type}"]

    if user_type == "premium":
        discount = price * 0.20
        logs.append(f"Applied premium discount: {discount}")
    else:
        discount = price * 0.10
        logs.append(f"Applied standard discount: {discount}")

    return DiscountResult(
        amount=discount,
        user_type=user_type,
        log_messages=tuple(logs)
    )

# Effect boundary: handle logging
def calculate_discount_with_logging(
    price: float,
    user_type: Literal["premium", "standard"]
) -> float:
    """Orchestration: computation + logging effect."""
    result = calculate_discount_pure(price, user_type)

    # Effect: log messages
    import logging
    for message in result.log_messages:
        logging.info(message)

    return result.amount
```

### Strategy 4: Console I/O Isolation
Separate input/output from computation logic.

**Before (Python - Non-Compliant)**:
```python
def interactive_calculator():
    """Impure: mixes I/O with logic."""
    while True:
        operation = input("Enter operation (+, -, *, /) or 'quit': ")
        if operation == 'quit':
            print("Goodbye!")
            break

        a = float(input("Enter first number: "))
        b = float(input("Enter second number: "))

        if operation == '+':
            result = a + b
        elif operation == '-':
            result = a - b
        elif operation == '*':
            result = a * b
        elif operation == '/':
            result = a / b if b != 0 else float('inf')

        print(f"Result: {result}")
```

**After (Python - Compliant)**:
```python
from typing import Literal
from dataclasses import dataclass

Operation = Literal['+', '-', '*', '/']

@dataclass(frozen=True)
class Calculation:
    operation: Operation
    operand_a: float
    operand_b: float

@dataclass(frozen=True)
class CalculationResult:
    value: float
    error: str | None = None

# Pure calculation logic
def calculate(calc: Calculation) -> CalculationResult:
    """Pure: performs calculation without I/O."""
    match calc.operation:
        case '+':
            return CalculationResult(value=calc.operand_a + calc.operand_b)
        case '-':
            return CalculationResult(value=calc.operand_a - calc.operand_b)
        case '*':
            return CalculationResult(value=calc.operand_a * calc.operand_b)
        case '/':
            if calc.operand_b == 0:
                return CalculationResult(
                    value=float('inf'),
                    error="Division by zero"
                )
            return CalculationResult(value=calc.operand_a / calc.operand_b)

# I/O boundary
def interactive_calculator_pure():
    """Effect boundary: handles I/O separately from logic."""
    while True:
        operation = input("Enter operation (+, -, *, /) or 'quit': ")
        if operation == 'quit':
            print("Goodbye!")
            break

        a = float(input("Enter first number: "))
        b = float(input("Enter second number: "))

        # Pure computation
        calc = Calculation(operation=operation, operand_a=a, operand_b=b)
        result = calculate(calc)

        # I/O: display result
        if result.error:
            print(f"Error: {result.error}")
        print(f"Result: {result.value}")
```

### Strategy 5: HTTP Request Isolation (TypeScript)
Separate HTTP side effects from data transformation.

**Before (TypeScript - Non-Compliant)**:
```typescript
async function fetchAndProcessUser(userId: number) {
  // Side effect: HTTP request
  const response = await fetch(`/api/users/${userId}`);
  const data = await response.json();

  // Pure logic mixed with effects
  return {
    id: data.id,
    name: data.name.toUpperCase(),
    age: data.age,
    isAdult: data.age >= 18
  };
}
```

**After (TypeScript - Compliant)**:
```typescript
interface RawUser {
  id: number;
  name: string;
  age: number;
}

interface ProcessedUser {
  id: number;
  name: string;
  age: number;
  isAdult: boolean;
}

// Pure transformation
function processUser(raw: RawUser): ProcessedUser {
  return {
    id: raw.id,
    name: raw.name.toUpperCase(),
    age: raw.age,
    isAdult: raw.age >= 18
  };
}

// Effect: HTTP request
async function fetchUser(userId: number): Promise<RawUser> {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}

// Composition at boundary
async function fetchAndProcessUser(userId: number): Promise<ProcessedUser> {
  const rawUser = await fetchUser(userId);  // Effect
  return processUser(rawUser);  // Pure
}
```

---

## Examples

### Example 1: Random Number Generation

**Non-Compliant**:
```python
import random

def generate_id():
    """Impure: uses random (non-deterministic side effect)."""
    return random.randint(1000, 9999)
```

**Compliant**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RandomSource:
    """Explicit random source for dependency injection."""
    seed: int | None = None

def generate_id(source: RandomSource) -> int:
    """Pure-ish: takes random source as explicit dependency."""
    import random
    if source.seed is not None:
        random.seed(source.seed)
    return random.randint(1000, 9999)

# Alternative: return generator, defer evaluation
def create_id_generator(min_val: int, max_val: int):
    """Returns generator function (delays effect)."""
    return lambda: random.randint(min_val, max_val)
```

### Example 2: Time-Dependent Logic

**Non-Compliant**:
```python
from datetime import datetime

def is_business_hours():
    """Impure: depends on current time (side effect)."""
    now = datetime.now()
    return 9 <= now.hour < 17
```

**Compliant**:
```python
from datetime import datetime

def is_business_hours(current_time: datetime) -> bool:
    """Pure: time passed explicitly as parameter."""
    return 9 <= current_time.hour < 17

# Usage: caller provides time (effect at boundary)
if is_business_hours(datetime.now()):
    print("Open for business")
```

### Example 3: Caching (Mutable State)

**Non-Compliant**:
```python
# Global mutable cache (side effect!)
_cache = {}

def expensive_calculation(n):
    """Impure: mutates global cache."""
    if n in _cache:
        return _cache[n]
    result = n ** 2  # Expensive computation
    _cache[n] = result
    return result
```

**Compliant** (Using functools.lru_cache for pure memoization):
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n: int) -> int:
    """Pure with memoization: deterministic, no visible side effects."""
    return n ** 2
```

---

## Edge Cases

### Edge Case 1: Unavoidable Side Effects
**Scenario**: Function must perform side effect (e.g., write to database)
**Issue**: Cannot make pure without breaking functionality
**Handling**:
- Mark function as explicitly impure with metadata
- Document side effects clearly
- Isolate to boundary layer (repository/adapter pattern)
- Separate pure business logic from effect execution

**Example**:
```python
# AIFP_SIDE_EFFECTS
# Effects: database write
# Purity: impure (necessary effect at boundary)
def save_user_to_db(user: User, db_connection) -> bool:
    """Effect function: saves user to database."""
    try:
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (user.name, user.email)
        )
        db_connection.commit()
        return True
    except Exception as e:
        db_connection.rollback()
        return False
```

### Edge Case 2: Hidden Side Effects in Libraries
**Scenario**: Third-party library function has hidden side effects
**Issue**: Side effects not visible in function signature
**Handling**:
- Wrap library functions to make effects explicit
- Document known library side effects
- Use fp_wrapper_generation for automatic wrapping
- Test for side effects in library code

### Edge Case 3: Observer/Event Pattern
**Scenario**: Function registers callbacks or emits events
**Issue**: Event emission is a side effect
**Handling**:
- Return event data instead of emitting directly
- Use event sourcing pattern (return events for external dispatcher)
- Document observer pattern usage

**Example**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class UserCreatedEvent:
    user_id: int
    timestamp: float
    user_data: dict

# Pure: returns event instead of emitting
def create_user_event(user_id: int, user_data: dict) -> UserCreatedEvent:
    """Pure: constructs event data without side effects."""
    import time
    return UserCreatedEvent(
        user_id=user_id,
        timestamp=time.time(),
        user_data=user_data
    )

# Effect boundary: emit event
def handle_user_creation(user_id: int, user_data: dict):
    """Effect: creates and emits event."""
    event = create_user_event(user_id, user_data)
    event_bus.emit(event)  # Side effect at boundary
```

### Edge Case 4: Stateful Iterators/Generators
**Scenario**: Generator maintains internal state
**Issue**: State mutation is technically a side effect
**Handling**:
- Accept generators as having managed state
- Ensure generators are deterministic given same input
- Document generator state behavior

### Edge Case 5: Performance-Critical Side Effects
**Scenario**: Eliminating side effect severely impacts performance
**Issue**: Pure refactoring introduces unacceptable overhead
**Handling**:
- Document performance trade-off
- Consider using controlled mutable state with clear boundaries
- Use profiling to validate performance claims
- Apply optimization directives if refactoring viable

---

## Database Operations

### Flag Function with Side Effects

```sql
-- Mark function as having side effects
UPDATE functions
SET
    has_side_effects = 1,
    side_effects_json = '{
        "types": ["io_file_write", "logging"],
        "description": "Writes processed data to file and logs progress",
        "isolated": true
    }',
    purity_level = 'impure',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'process_and_save_data' AND file_id = ?;
```

### Query Functions with Side Effects

```sql
-- Find functions with side effects
SELECT f.id, f.name, f.file_id, f.side_effects_json
FROM functions f
WHERE f.has_side_effects = 1
  AND json_extract(f.side_effects_json, '$.isolated') = 0
ORDER BY f.call_count DESC;
```

---

## Related Directives

### FP Directives
- **fp_purity**: Enforces pure functions, works with side effect detection
- **fp_io_isolation**: Specialized directive for I/O side effect isolation
- **fp_logging_safety**: Handles logging side effects specifically
- **fp_side_effect_detection**: Sister directive focusing on detection over flagging

### Project Directives
- **project_compliance_check**: Validates side effect handling
- **project_update_db**: Records side effect metadata

---

## Helper Functions

### `detect_side_effects(function_body) -> list[SideEffect]`
Scans function body for side-effecting operations.

**Signature**:
```python
def detect_side_effects(function_body: ASTNode) -> list[SideEffect]:
    """
    Analyzes function AST for side effects:
    - I/O operations (file, network, console)
    - Global variable mutations
    - Logging calls
    - Random number generation
    - Time-dependent calls
    Returns list of detected side effects with locations.
    """
```

### `classify_side_effect(operation) -> SideEffectType`
Classifies type of side effect detected.

**Signature**:
```python
def classify_side_effect(operation: ASTNode) -> SideEffectType:
    """
    Categories: io_file, io_network, io_console, global_mutation,
    logging, random, time_dependent, database, external_api.
    Returns side effect classification.
    """
```

### `suggest_isolation_strategy(side_effect) -> IsolationStrategy`
Recommends refactoring approach for side effect.

**Signature**:
```python
def suggest_isolation_strategy(
    side_effect: SideEffect
) -> IsolationStrategy:
    """
    Suggests: boundary_isolation, dependency_injection,
    data_return, effect_wrapper, or document_only.
    Returns recommended isolation strategy.
    """
```

---

## Testing

### Test 1: I/O Detection
```python
def test_detect_file_io():
    source = """
def read_config():
    with open('config.txt', 'r') as f:
        return f.read()
"""

    effects = fp_side_effects_flag.detect(source)

    assert len(effects) > 0
    assert any(e.type == 'io_file' for e in effects)
    assert any('open' in e.operation for e in effects)
```

### Test 2: Logging Detection
```python
def test_detect_logging():
    source = """
import logging

def process_data(data):
    logging.info("Processing started")
    result = transform(data)
    logging.info(f"Processed {len(result)} items")
    return result
"""

    effects = fp_side_effects_flag.detect(source)

    assert any(e.type == 'logging' for e in effects)
    assert len([e for e in effects if e.type == 'logging']) == 2
```

### Test 3: Global Mutation Detection
```python
def test_detect_global_mutation():
    source = """
counter = 0

def increment():
    global counter
    counter += 1
    return counter
"""

    effects = fp_side_effects_flag.detect(source)

    assert any(e.type == 'global_mutation' for e in effects)
    assert any('counter' in e.description for e in effects)
```

---

## Common Mistakes

### Mistake 1: Hidden Console I/O
**Problem**: Forgetting that print() is a side effect

**Solution**: Extract print to boundary or return data for external display

```python
# ❌ Bad: Hidden side effect
def calculate_and_display(x, y):
    result = x + y
    print(f"Result: {result}")  # Side effect!
    return result

# ✅ Good: Pure calculation, separate display
def calculate(x: int, y: int) -> int:
    return x + y

def display_result(result: int) -> None:
    """Effect boundary: display output."""
    print(f"Result: {result}")
```

### Mistake 2: Mutable Default Arguments
**Problem**: Mutable defaults are shared state (side effect)

**Solution**: Use None and create new instance inside function

```python
# ❌ Bad: Mutable default (hidden state)
def append_item(item, lst=[]):
    lst.append(item)  # Mutates shared default!
    return lst

# ✅ Good: Immutable default, explicit copy
def append_item(item: int, lst: list[int] | None = None) -> list[int]:
    if lst is None:
        lst = []
    return lst + [item]  # Returns new list
```

### Mistake 3: Exception Side Effects
**Problem**: Raising exceptions is technically a side effect

**Solution**: Use Result types for explicit error handling

```python
# ❌ Impure: Exception side effect
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero")  # Side effect!
    return a / b

# ✅ Pure: Result type
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Ok:
    value: float

@dataclass(frozen=True)
class Err:
    error: str

Result = Union[Ok, Err]

def divide(a: float, b: float) -> Result:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)
```

---

## Roadblocks

### Roadblock 1: Hidden Side Effect
**Issue**: Side effect not immediately visible (library function, closure)
**Resolution**: Wrap or isolate, document behavior

### Roadblock 2: Untracked I/O
**Issue**: I/O operation not detected by scanner
**Resolution**: Use dedicated I/O handler, manual review

### Roadblock 3: Performance Trade-off
**Issue**: Side effect isolation introduces unacceptable overhead
**Resolution**: Document trade-off, use controlled mutable state with clear boundaries

### Roadblock 4: Necessary Database Operation
**Issue**: Function must write to database (unavoidable effect)
**Resolution**: Isolate to boundary layer, separate pure logic from effect execution

---

## Integration Points

### With `fp_purity`
Side effects flag works with purity directive to enforce pure functions.

### With `fp_io_isolation`
Specialized isolation for I/O side effects.

### With `fp_logging_safety`
Handles logging side effects specifically.

### With `project_compliance_check`
Validates that side effects are properly documented and isolated.

---

## Intent Keywords

- `side effects`
- `io`
- `mutation`
- `impure`
- `effect isolation`
- `logging`

---

## Confidence Threshold

**0.7** - High confidence required to avoid false positives in side effect detection.

---

## Notes

- All I/O is considered a side effect (file, network, console, database)
- Logging is a side effect and should be isolated or extracted
- Global state access/mutation is a side effect
- Random number generation is non-deterministic (side effect)
- Time-dependent functions are side effects
- Exceptions can be considered control flow side effects
- Side effects should be pushed to program boundaries (main, handlers)
- Pure functions can call other pure functions safely
- Effect functions should be clearly marked and documented
- Use Result types instead of exceptions for pure error handling
- Memoization is acceptable for pure functions (no visible side effect)
