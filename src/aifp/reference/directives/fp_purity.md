# Directive: fp_purity

**Type**: FP Core
**Level**: 1 (Critical)
**Parent Directive**: None
**Priority**: CRITICAL - Required for all FP compliance

---

## Purpose

The `fp_purity` directive enforces pure functions throughout the codebase - the foundational principle of functional programming. A pure function is deterministic (same inputs always produce same outputs) and has no side effects (does not modify external state, perform I/O, or depend on anything other than its parameters).

This directive is **central to AIFP** - it applies to all code generation and compliance checks. Pure functions enable:
- **Predictability**: Same input → same output, always
- **Testability**: Easy to test without complex setup/teardown
- **Composability**: Pure functions can be safely composed
- **Parallelization**: No shared state means safe concurrent execution
- **Reasoning**: Function behavior fully determined by signature

When applied, this directive analyzes function code for:
1. **External state access** (global variables, class instance variables)
2. **Mutations** (modifying passed parameters or external data)
3. **Side effects** (I/O operations, logging, network calls, database writes)
4. **Hidden dependencies** (implicit dependencies not passed as parameters)

If violations are detected, the directive refactors code to be pure or prompts the user for guidance.

**Important**: This directive is reference documentation for FP purity patterns.
AI consults this when uncertain about purity boundaries or complex edge cases.

**FP purity is baseline behavior**:
- AI writes pure functions naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about whether a function is pure
- Complex purity boundary decisions (e.g., logging, time functions)
- Edge cases with external state or hidden dependencies
- Need for detailed guidance on refactoring impure code to pure

**Context**:
- AI writes pure functions as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_side_effect_detection`, `fp_io_isolation`) may reference this for purity guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: analyze_function

Analyzes a function's code to determine if it's pure.

**Steps**:
1. **Parse function signature** - Extract parameters and return type
2. **Scan function body** - Identify all operations and references
3. **Check for mutations** - Detect parameter modifications or reassignments
4. **Check for external state** - Detect global variable access or class state
5. **Check for side effects** - Detect I/O, logging, network, database operations
6. **Evaluate purity** - Classify as pure, impure, or uncertain

### Branches

**Branch 1: If mutation_detected**
- **Then**: `refactor_to_pure`
- **Details**: Convert mutations to new variable bindings
  - Replace `list.append(item)` with `new_list = list + [item]`
  - Replace `dict[key] = value` with `new_dict = {**dict, key: value}`
  - Replace `x = x + 1` with `x_new = x + 1`
- **Result**: Returns refactored code with explicit parameter passing

**Branch 2: If external_state_access**
- **Then**: `isolate_side_effects`
- **Details**: Pass external state as explicit parameters
  - Convert global variable access to parameters
  - Convert class instance variables to function parameters
  - Make all dependencies explicit in function signature
- **Result**: Returns refactored code with expanded parameters

**Branch 3: If pure**
- **Then**: `mark_compliant`
- **Details**: Function is already pure
  - No refactoring needed
  - Mark as compliant in analysis results
- **Result**: Function passes purity check

**Branch 4: If refactored**
- **Then**: `update_functions_table`
- **Details**: Update `project.db` with purity metadata
  - Set `functions.purity_level = 'pure'`
  - Set `functions.side_effects_json = 'none'`
  - Update `functions.updated_at`
- **Result**: Database reflects function purity status

**Branch 5: If low_confidence**
- **Then**: `prompt_user`
- **Details**: Uncertain about function purity
  - Present analysis findings to user
  - Ask: "Is this function pure, or should I refactor?"
  - Log uncertainty to `notes` table
- **Result**: User clarifies purity status

**Fallback**: `prompt_user`
- **Details**: Unable to determine purity automatically
  - Present function code to user
  - Ask: "Function purity uncertain—refactor or confirm purity?"
  - Log to `notes` table for tracking
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Pure Function (Passes):**
```python
def calculate_total(items: list[float], tax_rate: float) -> float:
    """Calculate total with tax. Pure function."""
    subtotal = sum(items)
    tax = subtotal * tax_rate
    return subtotal + tax
```

**Why Pure**:
- No external state access
- No mutations (creates new values)
- No side effects
- Deterministic (same inputs → same output)

**Pure Function with Immutable Update (Passes):**
```python
def add_item(cart: dict, item: str, price: float) -> dict:
    """Add item to cart immutably. Returns new cart."""
    return {**cart, item: price}
```

**Why Pure**:
- Creates new dictionary instead of mutating
- No side effects
- Original `cart` unchanged

---

### ❌ Non-Compliant Code

**Impure Function (Global State):**
```python
# ❌ VIOLATION: Accesses global state
discount_rate = 0.1

def calculate_discount(price: float) -> float:
    return price * discount_rate  # ← External state dependency
```

**Why Impure**:
- Depends on global variable `discount_rate`
- Not deterministic (output changes if global changes)
- Hidden dependency not in signature

**Refactored (Pure):**
```python
def calculate_discount(price: float, discount_rate: float) -> float:
    """Calculate discount. Pure function."""
    return price * discount_rate
```

---

**Impure Function (Mutation):**
```python
# ❌ VIOLATION: Mutates parameter
def add_item_impure(cart: dict, item: str, price: float) -> None:
    cart[item] = price  # ← Mutation of passed parameter
```

**Why Impure**:
- Mutates input parameter `cart`
- Side effect (caller's data modified)
- Violates referential transparency

**Refactored (Pure):**
```python
def add_item_pure(cart: dict, item: str, price: float) -> dict:
    """Add item immutably. Returns new cart."""
    return {**cart, item: price}
```

---

**Impure Function (Side Effect):**
```python
# ❌ VIOLATION: I/O side effect
def calculate_and_log(a: int, b: int) -> int:
    result = a + b
    print(f"Result: {result}")  # ← Side effect (I/O)
    return result
```

**Why Impure**:
- Performs I/O (print)
- Side effect not reflected in signature
- Not testable without capturing output

**Refactored (Pure):**
```python
def calculate(a: int, b: int) -> int:
    """Pure calculation."""
    return a + b

def log_result(result: int) -> None:
    """Effect function: isolated I/O."""
    print(f"Result: {result}")

# Usage (separates pure logic from effects):
result = calculate(3, 5)
log_result(result)  # Effect happens outside pure function
```

---

## Edge Cases

### Edge Case 1: DateTime Operations

**Issue**: Functions using `datetime.now()` appear impure (non-deterministic)

**Handling**:
```python
# ❌ Impure (datetime.now() is non-deterministic)
from datetime import datetime

def log_timestamp(message: str) -> str:
    return f"{datetime.now()}: {message}"

# ✅ Pure (time passed as parameter)
from datetime import datetime

def format_log(message: str, timestamp: datetime) -> str:
    """Pure formatting function."""
    return f"{timestamp}: {message}"

# Effect wrapper handles non-determinism
def log_with_timestamp(message: str) -> str:
    """Effect function: captures current time."""
    return format_log(message, datetime.now())
```

**Directive Action**: Pass `datetime` as explicit parameter, isolate `now()` call to effect function.

---

### Edge Case 2: Random Number Generation

**Issue**: `random.random()` is non-deterministic

**Handling**:
```python
# ❌ Impure (non-deterministic)
import random

def pick_item(items: list) -> any:
    return items[random.randint(0, len(items) - 1)]

# ✅ Pure (seed or index passed explicitly)
def pick_item_pure(items: list, index: int) -> any:
    """Pure selection by index."""
    return items[index % len(items)]

# Effect wrapper handles randomness
import random

def pick_item_random(items: list) -> any:
    """Effect function: random selection."""
    return pick_item_pure(items, random.randint(0, len(items) - 1))
```

**Directive Action**: Extract random generation to effect function, make pure function deterministic.

---

### Edge Case 3: Database Queries

**Issue**: Database reads are side effects (I/O)

**Handling**:
```python
# ❌ Impure (database I/O)
def get_user_name(user_id: int) -> str:
    result = db.query("SELECT name FROM users WHERE id = ?", user_id)
    return result[0]['name']

# ✅ Pure (data passed as parameter)
def extract_user_name(user_data: dict) -> str:
    """Pure extraction from data."""
    return user_data['name']

# Effect wrapper handles database I/O
def fetch_user_name(user_id: int) -> str:
    """Effect function: database query."""
    user_data = db.query("SELECT name FROM users WHERE id = ?", user_id)[0]
    return extract_user_name(user_data)
```

**Directive Action**: Separate data fetching (effect) from data processing (pure).

---

### Edge Case 4: Caching/Memoization

**Issue**: Caching stores state, appears impure

**Handling**:
- **Pure function** remains pure (no internal cache)
- **External memoization** applied as wrapper (effect layer)
- Cache state managed outside function scope

```python
# Pure function (no caching)
def expensive_calculation(n: int) -> int:
    """Pure calculation (no cache)."""
    return sum(range(n))

# Effect wrapper with memoization (external state)
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_expensive_calculation(n: int) -> int:
    """Effect wrapper: adds caching."""
    return expensive_calculation(n)
```

**Directive Action**: Keep core function pure, apply caching as external effect wrapper.

---

## Related Directives

- **Depends On**: None (foundational directive)
- **Triggers**:
  - `fp_immutability` - Often called together to ensure both purity and immutability
  - `fp_side_effect_detection` - Specialized side effect analysis
  - `fp_state_elimination` - Removes global state dependencies
- **Called By**:
  - `project_file_write` - Validates purity before file writes
  - `project_compliance_check` - Project-wide purity verification
  - `fp_no_oop` - OOP refactoring often needs purity checks
- **Escalates To**:
  - `fp_language_standardization` - For language-specific purity issues
  - `fp_wrapper_generation` - For wrapping impure library dependencies

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `purity_level = 'pure'` and `side_effects_json = 'none'` for compliant functions
- **`interactions`**: Tracks dependencies when external state is converted to parameters

**Tracking** (Optional - Disabled by Default):

If tracking is enabled:
- **`tracking_notes`** (user_preferences.db): Logs FP analysis with `note_type='fp_analysis'`

Only occurs when `fp_flow_tracking` is enabled via `tracking_toggle`.
Token overhead: ~5% per file write.
Most users will never enable this. It's for AIFP development and debugging only.

**Note**: When tracking is enabled, use helper functions from user_preferences helpers (e.g., `add_tracking_note`, `get_tracking_notes`, `search_tracking_notes`) to log FP analysis data. Never write SQL directly.

---

## Testing

How to verify this directive is working:

1. **Write impure function** → Directive detects and refactors
   ```python
   # Input (impure)
   global_config = {"rate": 0.1}
   def calc(price): return price * global_config["rate"]

   # Expected output (pure)
   def calc(price: float, rate: float) -> float:
       return price * rate
   ```

2. **Write pure function** → Directive marks compliant, no changes
   ```python
   def add(a: int, b: int) -> int: return a + b
   # ✅ Already pure, no refactoring needed
   ```

3. **Check database** → Verify `functions.purity_level = 'pure'`
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Common Mistakes

- ❌ **Assuming logging is pure** - `print()`, `logging.info()` are side effects
- ❌ **Mutating collection parameters** - `.append()`, `.update()` modify inputs
- ❌ **Accessing class instance variables** - `self.state` creates hidden dependencies
- ❌ **Using global configuration** - Even "constants" should be explicit parameters
- ❌ **Assuming time functions are pure** - `datetime.now()` is non-deterministic

---

## Roadblocks and Resolutions

### Roadblock 1: stateful_function
**Issue**: Function depends on or modifies state
**Resolution**: Isolate state outside of function scope, pass as explicit parameters

### Roadblock 2: hidden_mutation
**Issue**: Subtle mutations (e.g., nested structure modification)
**Resolution**: Refactor to pure function using immutable updates

### Roadblock 3: language_mismatch
**Issue**: Language lacks immutable data structures
**Resolution**: Escalate to `fp_language_standardization` for language-specific patterns

### Roadblock 4: external_dependency
**Issue**: Function depends on external libraries or modules
**Resolution**: Pass as explicit parameter or isolate with `fp_wrapper_generation`

---

## References

None
---

*Part of AIFP v1.0 - Critical FP Core directive for pure functional programming*
