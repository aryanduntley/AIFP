# Directive: fp_ownership_safety

**Type**: FP
**Level**: 1
**Parent Directive**: None
**Priority**: CRITICAL - Memory safety and concurrency

---

## Purpose

The `fp_ownership_safety` directive **applies borrow or copy semantics to data passed between functions**, preventing shared mutability and ensuring safe data ownership. This directive is **vital for concurrency safety** because:

- **Prevents shared mutable state**: No two functions mutate the same data
- **Memory safety**: Clear ownership prevents use-after-free bugs
- **Concurrency correctness**: Independent copies enable safe parallelism
- **AI reasoning**: Explicit ownership makes data flow transparent
- **Rust-inspired safety**: Brings ownership concepts to dynamic languages

This directive enforces:
- **Copy semantics** - Data copied when passed (default safe choice)
- **Borrow semantics** - Data borrowed read-only (performance optimization)
- **Move semantics** - Ownership transferred (previous owner can't access)
- **No shared mutability** - Data either copied or immutably borrowed

**Safety principle**: When in doubt, copy. Optimize to borrow only when safe.

---

## When to Apply

This directive applies when:
- **Data passed between functions** - Parameter passing analyzed
- **Shared references detected** - Multiple functions access same data
- **Mutation potential exists** - Data structure could be mutated
- **During compliance checks** - `project_compliance_check` scans ownership
- **Concurrent operations** - Parallel function execution planned
- **User requests safety** - "Ensure ownership safety", "Prevent shared mutation"

---

## Workflow

### Trunk: analyze_function_parameters

Analyzes how data is passed between functions.

**Steps**:
1. **Parse function signatures** - Extract parameter types
2. **Trace data flow** - Track how data moves between functions
3. **Detect sharing patterns** - Find potential shared references
4. **Route to safety strategy** - Apply copy, borrow, or move

### Branches

**Branch 1: If shared_reference_detected**
- **Then**: `apply_copy_semantics`
- **Details**: Copy data to prevent shared mutation
  - Shared reference patterns:
    ```python
    # ❌ Shared reference (dangerous)
    data = [1, 2, 3]
    result1 = process_a(data)  # Passes reference
    result2 = process_b(data)  # Same reference!

    # If either function mutates data, both see changes
    def process_a(items):
        items.append(4)  # Mutation affects original!
        return sum(items)
    ```
  - Copy semantics refactoring:
    ```python
    # ✅ Copy semantics (safe)
    from copy import deepcopy

    data = [1, 2, 3]
    result1 = process_a(deepcopy(data))  # Independent copy
    result2 = process_b(deepcopy(data))  # Independent copy

    # Each function gets its own copy
    # No shared mutation possible
    ```
  - Language-specific copying:
    - **Python**: Use `copy.deepcopy()` for nested structures, `list()` for shallow
    - **JavaScript**: Use `[...array]` or `Object.assign({}, obj)`
    - **TypeScript**: Same as JS, but types enforce immutability
    - **Rust**: `.clone()` method for owned copies
  - When to copy:
    - Data structure is mutable (list, dict, object)
    - Multiple functions receive same data
    - Functions might mutate (not pure)
    - Safety over performance
  - Update database:
    ```sql
    UPDATE functions
    SET side_effects_json = '{"ownership": "copy"}',
        updated_at = CURRENT_TIMESTAMP
    WHERE name = ? AND file_id = ?
    ```
- **Result**: Shared mutation prevented via copying

**Branch 2: If borrow_pattern_safe**
- **Then**: `approve_function`
- **Details**: Data borrowed read-only, no copies needed
  - Safe borrow patterns:
    ```python
    # ✅ Read-only borrow (safe, efficient)
    def calculate_average(items: list[int]) -> float:
        # Only reads items, never mutates
        return sum(items) / len(items)

    def calculate_max(items: list[int]) -> int:
        # Only reads items, never mutates
        return max(items)

    data = [1, 2, 3, 4, 5]
    avg = calculate_average(data)  # Borrow (read-only)
    maximum = calculate_max(data)  # Borrow (read-only)
    # No copies needed - both functions pure
    ```
  - Borrow is safe when:
    - Function is pure (no mutation)
    - Data structure is immutable (tuple, frozenset, frozen dataclass)
    - Function only reads data
    - No concurrent mutation risk
  - Verification:
    ```python
    def is_safe_to_borrow(func):
        # Check function purity
        if not is_pure_function(func):
            return False

        # Check if parameters are mutated
        ast = parse_function_ast(func)
        mutations = detect_mutations(ast)
        return len(mutations) == 0
    ```
  - Borrow annotation (type hints):
    ```python
    from typing import Sequence  # Immutable sequence protocol

    def process(items: Sequence[int]) -> int:
        # Sequence is read-only, borrow safe
        return sum(items)
    ```
  - Update database:
    ```sql
    UPDATE functions
    SET purity_level = 'pure',
        side_effects_json = '{"ownership": "borrow", "mutation": false}',
        updated_at = CURRENT_TIMESTAMP
    WHERE name = ? AND file_id = ?
    ```
- **Result**: Borrow validated as safe, no copy needed

**Branch 3: If immutable_data_structure**
- **Then**: `mark_safe_to_share`
- **Details**: Data structure is immutable, sharing is safe
  - Immutable structures:
    ```python
    # ✅ Immutable structures (always safe to share)
    from dataclasses import dataclass
    from typing import FrozenSet

    @dataclass(frozen=True)
    class Config:
        host: str
        port: int

    def connect(config: Config) -> Connection:
        # Config is immutable, safe to share
        return create_connection(config.host, config.port)

    def validate_config(config: Config) -> bool:
        # Also safe - config can't be mutated
        return config.port > 0

    # Single config instance shared safely
    config = Config(host="localhost", port=5432)
    conn = connect(config)  # Share (immutable)
    valid = validate_config(config)  # Share (immutable)
    ```
  - Immutable types in Python:
    - `tuple`, `frozenset`, `frozendict` (external library)
    - `@dataclass(frozen=True)`
    - `NamedTuple`
    - Primitives: `int`, `str`, `float`, `bool`
  - Immutable types in JavaScript:
    - Frozen objects: `Object.freeze(obj)`
    - Immutable.js library structures
  - Immutable types in TypeScript:
    - `readonly` modifier
    - `Readonly<T>` utility type
  - Compiler enforcement:
    ```python
    # Type checker prevents mutation
    @dataclass(frozen=True)
    class Point:
        x: int
        y: int

    p = Point(1, 2)
    p.x = 3  # Type error: frozen dataclass
    ```
- **Result**: Immutable sharing validated as safe

**Branch 4: If move_semantics_appropriate**
- **Then**: `transfer_ownership`
- **Details**: Transfer ownership, invalidate previous reference
  - Move semantics patterns:
    ```python
    # ✅ Move semantics (transfer ownership)
    # Python doesn't enforce, but pattern is clear

    def consume_data(data: list[int]) -> int:
        # Takes ownership, caller shouldn't use data after
        return sum(data)

    # Explicit move (clear intent)
    data = [1, 2, 3]
    result = consume_data(data)
    # Convention: Don't use 'data' after this point
    # (Python doesn't enforce, but code should follow)
    ```
  - Move semantics in Rust (enforcement):
    ```rust
    // Rust enforces move semantics
    fn consume_data(data: Vec<i32>) -> i32 {
        data.iter().sum()  // Takes ownership
    }

    let data = vec![1, 2, 3];
    let result = consume_data(data);
    // Compiler error if you try to use 'data' here
    ```
  - Simulating move in Python (convention):
    ```python
    # Python: Use naming conventions and type hints
    from typing import Final

    def move_and_process(data: list[int]) -> tuple[int, None]:
        result = sum(data)
        return result, None  # Return None as moved indicator

    data = [1, 2, 3]
    result, _ = move_and_process(data)
    # Convention: Don't use data after this
    ```
  - When to use move:
    - Function consumes data (no need to keep original)
    - Transferring ownership to avoid copy overhead
    - Resource management (file handles, connections)
- **Result**: Ownership transferred, no shared reference

**Branch 5: If concurrent_access_detected**
- **Then**: `enforce_copy_or_lock`
- **Details**: Concurrent access requires copying or synchronization
  - Concurrent access patterns:
    ```python
    # ❌ Dangerous: Concurrent access to shared data
    from concurrent.futures import ThreadPoolExecutor

    data = [1, 2, 3]

    def worker_a():
        data.append(4)  # Race condition!

    def worker_b():
        return sum(data)  # Race condition!

    with ThreadPoolExecutor() as executor:
        executor.submit(worker_a)
        executor.submit(worker_b)
    ```
  - Solution 1: Copy for each thread
    ```python
    # ✅ Copy per thread (safe)
    from copy import deepcopy

    data = [1, 2, 3]

    def worker_a(data_copy):
        data_copy.append(4)  # Independent copy
        return data_copy

    def worker_b(data_copy):
        return sum(data_copy)  # Independent copy

    with ThreadPoolExecutor() as executor:
        future_a = executor.submit(worker_a, deepcopy(data))
        future_b = executor.submit(worker_b, deepcopy(data))
    ```
  - Solution 2: Immutable sharing
    ```python
    # ✅ Immutable data (safe to share)
    data = (1, 2, 3)  # Tuple (immutable)

    def worker_a(data_ref):
        # Can't mutate, only read
        return data_ref + (4,)  # New tuple

    def worker_b(data_ref):
        return sum(data_ref)  # Read-only

    with ThreadPoolExecutor() as executor:
        executor.submit(worker_a, data)  # Safe to share
        executor.submit(worker_b, data)  # Safe to share
    ```
  - Solution 3: Message passing (no sharing)
    ```python
    # ✅ Message passing (actor model)
    import queue

    input_queue = queue.Queue()
    output_queue = queue.Queue()

    def worker():
        while True:
            data = input_queue.get()  # Receive copy
            result = process(data)
            output_queue.put(result)  # Send result
    ```
- **Result**: Concurrent safety ensured via copying or immutability

**Fallback**: `prompt_user`
- **Details**: Ownership pattern unclear, user decision needed
  - Ambiguous scenarios:
    - Complex data structure with nested references
    - Mixed mutable/immutable components
    - Performance-critical path (copy overhead)
  - Prompt example:
    ```
    Ownership safety unclear

    Function: process_data
    Parameter: data (type: dict[str, list[int]])

    Nested structure with mutable components.

    Recommended approach:
    1. Deep copy (safe, slower): deepcopy(data)
    2. Shallow copy (faster, less safe): {k: v for k, v in data.items()}
    3. Borrow (fastest, requires purity): pass by reference

    Choose approach (1-3):
    If choosing 3, confirm function is pure (y/n):
    ```
- **Result**: User clarifies ownership strategy

---

## Examples

### ✅ Compliant Usage

**Applying Copy Semantics:**
```python
# Initial code (non-compliant)
def process_pipeline(data):
    result1 = transform_a(data)  # Passes reference
    result2 = transform_b(data)  # Same reference!
    return combine(result1, result2)

def transform_a(items):
    items.append(999)  # Mutation! Affects caller's data
    return sum(items)

def transform_b(items):
    return len(items)  # Sees mutated data!

# AI calls: fp_ownership_safety()

# Workflow:
# 1. analyze_function_parameters:
#    - data passed to multiple functions
#    - transform_a mutates parameter
#    - Shared reference detected
#
# 2. shared_reference_detected: apply_copy_semantics
#    - Copy data before each function call
#
# Refactored code (compliant)
from copy import deepcopy

def process_pipeline(data: list[int]) -> any:
    result1 = transform_a(deepcopy(data))  # Independent copy
    result2 = transform_b(deepcopy(data))  # Independent copy
    return combine(result1, result2)

# Or: Make transform_a pure (better)
def transform_a_pure(items: list[int]) -> int:
    # No mutation - create new list if needed
    return sum(items + [999])

def process_pipeline_pure(data: list[int]) -> any:
    result1 = transform_a_pure(data)  # Borrow (pure function)
    result2 = transform_b(data)  # Borrow (pure function)
    return combine(result1, result2)

# Database update
UPDATE functions
SET side_effects_json = '{"ownership": "copy"}',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'process_pipeline';

# Result:
# ✅ No shared mutation
# ✅ Each function has independent data
# ✅ Concurrent execution safe
```

---

**Using Immutable Structures:**
```python
# Initial code (non-compliant)
class Config:
    def __init__(self, host, port):
        self.host = host
        self.port = port  # Mutable!

config = Config("localhost", 5432)

def connect(config):
    config.port = 9999  # Mutation! Changes shared config
    return create_connection(config.host, config.port)

# AI calls: fp_ownership_safety()

# Workflow:
# 1. analyze_function_parameters:
#    - config is mutable class instance
#    - Potential shared mutation
#
# 2. shared_reference_detected: apply_copy_semantics
#    - Or better: Make config immutable
#
# Refactored code (compliant)
from dataclasses import dataclass

@dataclass(frozen=True)  # Immutable!
class Config:
    host: str
    port: int

config = Config(host="localhost", port=5432)

def connect(config: Config) -> Connection:
    # Can't mutate config (frozen dataclass)
    # Safe to share
    return create_connection(config.host, config.port)

def validate(config: Config) -> bool:
    # Also safe - config is immutable
    return config.port > 0

# Single config instance shared safely
conn = connect(config)
valid = validate(config)

# Result:
# ✅ Immutable structure
# ✅ Safe to share without copying
# ✅ Compiler enforces immutability
```

---

**Safe Borrowing (Pure Functions):**
```python
# Initial code (analysis)
def calculate_statistics(data):
    total = sum(data)  # Read-only
    count = len(data)  # Read-only
    average = total / count
    return average

def find_max(data):
    return max(data)  # Read-only

# AI calls: fp_ownership_safety()

# Workflow:
# 1. analyze_function_parameters:
#    - Both functions only read data
#    - No mutations detected
#
# 2. borrow_pattern_safe: approve_function
#    - Both functions pure
#    - Safe to borrow (pass by reference)
#
# Validated code (compliant)
# No refactoring needed - borrowing is safe

data = [1, 2, 3, 4, 5]
avg = calculate_statistics(data)  # Borrow (efficient)
maximum = find_max(data)  # Borrow (efficient)

# Database update
UPDATE functions
SET purity_level = 'pure',
    side_effects_json = '{"ownership": "borrow", "mutation": false}',
    updated_at = CURRENT_TIMESTAMP
WHERE name IN ('calculate_statistics', 'find_max');

# Result:
# ✅ Borrow validated as safe
# ✅ No unnecessary copying
# ✅ Performance optimized
```

---

### ❌ Non-Compliant Usage

**Shared Mutable Reference:**
```python
# ❌ Shared mutable data
data = [1, 2, 3]

def add_to_list(items):
    items.append(4)  # Mutation

def process_list(items):
    return sum(items)

add_to_list(data)  # Mutates shared data
result = process_list(data)  # Sees mutation

# Why Non-Compliant:
# - data is mutable and shared
# - add_to_list mutates shared reference
# - process_list behavior depends on mutation order
```

**Corrected:**
```python
# ✅ Copy semantics
from copy import copy

data = [1, 2, 3]

def add_to_list(items: list[int]) -> list[int]:
    return items + [4]  # New list, no mutation

def process_list(items: list[int]) -> int:
    return sum(items)

new_data = add_to_list(copy(data))
result = process_list(copy(data))
```

---

## Edge Cases

### Edge Case 1: Nested Mutable Structures

**Issue**: Shallow copy insufficient for nested structures

**Handling**:
```python
# Nested structure
data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}

# ❌ Shallow copy (unsafe)
copy_data = data.copy()
copy_data["users"].append({"name": "Charlie"})  # Mutates original!

# ✅ Deep copy (safe)
from copy import deepcopy
copy_data = deepcopy(data)
copy_data["users"].append({"name": "Charlie"})  # Independent
```

**Directive Action**: Use deep copy for nested structures.

---

### Edge Case 2: Large Data Structures

**Issue**: Copying large data is expensive

**Handling**:
```python
# Large dataset
large_data = list(range(1_000_000))

# Option 1: Copy (safe but slow)
result = process(large_data.copy())

# Option 2: Ensure purity, borrow (fast)
def process_pure(data: list[int]) -> int:
    # Guaranteed pure, safe to borrow
    return sum(data)

result = process_pure(large_data)  # No copy needed
```

**Directive Action**: Prefer purity for performance, copy for safety.

---

### Edge Case 3: Circular References

**Issue**: Deep copy fails with circular references

**Handling**:
```python
# Circular reference
class Node:
    def __init__(self):
        self.next = None

a = Node()
b = Node()
a.next = b
b.next = a  # Circular!

# deepcopy handles this
from copy import deepcopy
copy_a = deepcopy(a)  # Works (handles cycles)
```

**Directive Action**: deepcopy handles circular references automatically.

---

## Related Directives

- **Called By**:
  - `fp_purity` - Part of purity enforcement
  - `fp_concurrency_safety` - Ensures thread-safe data access
  - `project_compliance_check` - Scans ownership patterns
- **Calls**:
  - `fp_borrow_check` - Validates borrow safety
  - Database helpers - Updates functions table
- **Related**:
  - `fp_immutability` - Immutable structures enable safe sharing
  - `fp_parallel_purity` - Ownership safety enables parallelism

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: UPDATE side_effects_json with ownership strategy
- **`notes`**: INSERT ownership safety decisions

---

## Testing

1. **Detect shared reference** → Multiple functions receive same data
   ```python
   shared_refs = detect_shared_references(process_pipeline)
   assert len(shared_refs) > 0
   ```

2. **Validate borrow safety** → Pure function allows borrowing
   ```python
   assert is_pure_function(calculate_average) == True
   ```

3. **Apply copy** → Data copied before passing
   ```python
   refactored = apply_copy_semantics(code)
   assert "deepcopy(" in refactored
   ```

---

## Common Mistakes

- ❌ **Shallow copy for nested structures** - Use deepcopy
- ❌ **Not checking function purity** - Only pure functions can safely borrow
- ❌ **Copying immutable data** - Unnecessary overhead
- ❌ **Ignoring concurrent access** - Must copy or use immutable data

---

## Roadblocks and Resolutions

### Roadblock 1: shared_mutation_risk
**Issue**: Multiple functions access same mutable data
**Resolution**: Duplicate or isolate data via copying

### Roadblock 2: unclear_borrowing
**Issue**: Unknown if function mutates parameter
**Resolution**: Default to copy semantics (safe), verify purity for borrow

---

## References

None
---

*Part of AIFP v1.0 - Core FP directive for ownership safety and preventing shared mutation*
