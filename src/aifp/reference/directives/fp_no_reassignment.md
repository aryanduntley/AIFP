# Directive: fp_no_reassignment

**Type**: FP
**Level**: 1
**Parent Directive**: None
**Priority**: CRITICAL - Core immutability enforcement

---

## Purpose

The `fp_no_reassignment` directive **disallows variable reassignment** and enforces **single-assignment semantics** per scope, ensuring all variable bindings are immutable after initialization. This directive is **fundamental for functional purity** because:

- **Referential transparency**: Variables represent values, not changing state
- **Predictability**: Variable meaning doesn't change throughout scope
- **Concurrency safety**: No race conditions from reassignment
- **Easier reasoning**: Each binding has one clear value
- **AI-friendly**: Static analysis becomes trivial

This directive eliminates:
- **Variable reassignment** - `x = 5; x = 10;`  (reassigning x)
- **Increment/decrement** - `counter += 1` (modifying counter)
- **Loop counters** - `for i in range(n): i += 1` (mutating loop variable)
- **Accumulator mutation** - `result = []; result.append(x)` (modifying result)
- **Conditional reassignment** - `x = 1; if cond: x = 2` (reassigning based on condition)

**Refactoring principle**: Use new variable bindings or return new values instead of reassignment.

---

## When to Apply

This directive applies when:
- **Variable reassigned in scope** - Same variable assigned multiple times
- **Loop counter mutated** - Loop variable modified inside loop
- **Accumulator pattern detected** - Variable built up over time
- **During compliance checks** - `project_compliance_check` scans for reassignments
- **Before file write** - `project_file_write` validates single-assignment
- **User requests immutable bindings** - "Remove reassignment", "Make immutable"

---

## Workflow

### Trunk: track_variable_bindings

Tracks all variable bindings and identifies reassignments.

**Steps**:
1. **Parse function AST** - Extract all variable assignments
2. **Track binding scope** - Map variables to their assignments
3. **Detect reassignments** - Find variables assigned 2+ times
4. **Route to refactoring** - Create new bindings or functional patterns

### Branches

**Branch 1: If reassignment_detected**
- **Then**: `create_new_binding`
- **Details**: Replace reassignment with new variable binding
  - Reassignment patterns:
    ```python
    # ❌ Reassignment
    result = calculate_base(data)
    result = apply_tax(result)  # Reassignment!
    result = apply_discount(result)  # Reassignment again!
    return result
    ```
  - Refactoring strategy 1: New variable names
    ```python
    # ✅ New bindings (no reassignment)
    base_result = calculate_base(data)
    with_tax = apply_tax(base_result)
    with_discount = apply_discount(with_tax)
    return with_discount
    ```
  - Refactoring strategy 2: Function composition
    ```python
    # ✅ Composition (no intermediate variables)
    def process(data):
        return apply_discount(apply_tax(calculate_base(data)))

    # Or: Using pipe/compose
    from functools import reduce

    def pipe(*funcs):
        return reduce(lambda f, g: lambda x: g(f(x)), funcs)

    process = pipe(calculate_base, apply_tax, apply_discount)
    result = process(data)
    ```
  - Refactoring strategy 3: Intermediate tuple
    ```python
    # ✅ Tuple unpacking (functional style)
    def process(data):
        stage1 = calculate_base(data)
        stage2 = apply_tax(stage1)
        stage3 = apply_discount(stage2)
        return stage3
    ```
  - Choose strategy based on:
    - Number of reassignments (composition if many)
    - Readability (new names if few)
    - Performance (avoid unnecessary intermediate values)
  - Update database:
    ```sql
    UPDATE functions
    SET purity_level = 'pure',
        side_effects_json = '{"mutation": false, "reassignment": false}',
        updated_at = CURRENT_TIMESTAMP
    WHERE name = ? AND file_id = ?
    ```
- **Result**: Reassignment eliminated, bindings immutable

**Branch 2: If loop_counter_mutation**
- **Then**: `replace_with_recursion_or_map`
- **Details**: Replace loops with functional alternatives
  - Loop reassignment patterns:
    ```python
    # ❌ Loop with accumulator reassignment
    total = 0
    for item in items:
        total += item  # Reassignment in loop

    # ❌ Loop with counter mutation
    result = []
    for i in range(len(items)):
        result.append(items[i] * 2)  # Accumulator mutation
    ```
  - Refactoring strategy 1: Use reduce/fold
    ```python
    # ✅ Reduce (no reassignment)
    from functools import reduce

    total = reduce(lambda acc, item: acc + item, items, 0)

    # Or: Built-in sum
    total = sum(items)
    ```
  - Refactoring strategy 2: Use map/comprehension
    ```python
    # ✅ List comprehension (no accumulator)
    result = [item * 2 for item in items]

    # Or: Using map
    result = list(map(lambda x: x * 2, items))
    ```
  - Refactoring strategy 3: Tail recursion
    ```python
    # ✅ Tail recursion (functional)
    def sum_items(items: list[int], acc: int = 0) -> int:
        if not items:
            return acc
        return sum_items(items[1:], acc + items[0])

    total = sum_items(items)
    ```
  - Performance note: For large loops, prefer built-ins (sum, map) over recursion
- **Result**: Loop replaced with functional construct

**Branch 3: If accumulator_pattern**
- **Then**: `refactor_to_functional_fold`
- **Details**: Replace accumulator mutation with fold/reduce
  - Accumulator patterns:
    ```python
    # ❌ Accumulator mutation
    result = []
    for item in items:
        if item > threshold:
            result.append(item)  # Mutation

    # ❌ Dictionary accumulator
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1  # Mutation
    ```
  - Refactoring strategy 1: Filter/comprehension
    ```python
    # ✅ Filter (no mutation)
    result = [item for item in items if item > threshold]

    # Or: Using filter
    result = list(filter(lambda x: x > threshold, items))
    ```
  - Refactoring strategy 2: Reduce for complex accumulation
    ```python
    # ✅ Reduce (functional accumulation)
    from functools import reduce

    counts = reduce(
        lambda acc, item: {**acc, item: acc.get(item, 0) + 1},
        items,
        {}
    )

    # Note: Creates new dict each iteration (immutable)
    ```
  - Refactoring strategy 3: collections.Counter (Python)
    ```python
    # ✅ Built-in (optimized)
    from collections import Counter
    counts = Counter(items)  # Immutable result
    ```
  - Trade-off: Reduce with dict spreading can be slow for large datasets
  - Solution: Use built-ins when available (Counter, groupby, etc.)
- **Result**: Accumulator mutation eliminated

**Branch 4: If conditional_reassignment**
- **Then**: `use_conditional_expression`
- **Details**: Replace conditional reassignment with expression
  - Conditional reassignment patterns:
    ```python
    # ❌ Conditional reassignment
    status = "pending"
    if is_approved:
        status = "approved"  # Reassignment
    elif is_rejected:
        status = "rejected"  # Reassignment

    # ❌ With default
    discount = 0
    if total > 100:
        discount = 10  # Reassignment
    ```
  - Refactoring strategy 1: Ternary expression
    ```python
    # ✅ Ternary (single assignment)
    discount = 10 if total > 100 else 0

    # Or: Conditional expression (Python)
    status = (
        "approved" if is_approved else
        "rejected" if is_rejected else
        "pending"
    )
    ```
  - Refactoring strategy 2: Dictionary mapping
    ```python
    # ✅ Dictionary lookup (no conditionals)
    status_map = {
        (True, False): "approved",
        (False, True): "rejected",
        (False, False): "pending"
    }
    status = status_map[(is_approved, is_rejected)]
    ```
  - Refactoring strategy 3: Pattern matching (Python 3.10+)
    ```python
    # ✅ Pattern matching (structural matching)
    match (is_approved, is_rejected):
        case (True, _):
            status = "approved"
        case (_, True):
            status = "rejected"
        case _:
            status = "pending"
    ```
  - Choose strategy based on complexity and language features
- **Result**: Conditional reassignment replaced with expression

**Branch 5: If increment_decrement**
- **Then**: `replace_with_addition`
- **Details**: Replace increment/decrement with addition
  - Increment patterns:
    ```python
    # ❌ Increment operators
    counter += 1  # Reassignment
    counter -= 1  # Reassignment
    counter *= 2  # Reassignment
    ```
  - Refactoring:
    ```python
    # ✅ New binding with addition
    new_counter = counter + 1
    # Or: Return new value from function
    def increment(counter: int) -> int:
        return counter + 1

    new_counter = increment(counter)
    ```
  - For functional state threading:
    ```python
    # ✅ Functional state (immutable)
    @dataclass(frozen=True)
    class AppState:
        counter: int

    def increment_counter(state: AppState) -> AppState:
        return AppState(counter=state.counter + 1)

    # Usage
    state = AppState(counter=0)
    state = increment_counter(state)  # New state
    state = increment_counter(state)  # New state again
    ```
- **Result**: Increment replaced with new binding

**Branch 6: If no_reassignment**
- **Then**: `mark_as_compliant`
- **Details**: All bindings are single-assignment
  - Update database:
    ```sql
    UPDATE functions
    SET purity_level = 'pure',
        side_effects_json = '{"reassignment": false}',
        updated_at = CURRENT_TIMESTAMP
    WHERE name = ? AND file_id = ?
    ```
  - No refactoring needed
- **Result**: Function validated as immutable-binding

**Fallback**: `prompt_user`
- **Details**: Complex reassignment pattern, unclear how to refactor
  - Scenarios:
    - Complex state machine
    - Multi-variable interdependent updates
    - Performance-critical loop
  - Prompt example:
    ```
    Complex reassignment detected

    Function: process_data
    File: src/processor.py

    Variables reassigned:
    • state (line 15, 18, 22)
    • result (line 16, 20)

    This pattern is complex. Suggested refactoring:
    1. Functional state threading (immutable state objects)
    2. Return tuple of values instead of mutation
    3. Accept reassignment with user confirmation (not recommended)

    Choose refactoring approach (1-3):
    ```
- **Result**: User clarifies refactoring strategy

---

## Examples

### ✅ Compliant Usage

**Eliminating Reassignment:**
```python
# Initial code (non-compliant)
def calculate_price(base_price, quantity):
    price = base_price * quantity  # Initial assignment
    price = price * 1.08  # Reassignment (tax)
    price = price - (price * 0.1)  # Reassignment (discount)
    return price

# AI calls: fp_no_reassignment()

# Workflow:
# 1. track_variable_bindings:
#    - price assigned 3 times (lines 2, 3, 4)
#    - Reassignment detected
#
# 2. reassignment_detected: create_new_binding
#    - Strategy: New variable names
#
# Refactored code (compliant)
def calculate_price(base_price: float, quantity: int) -> float:
    subtotal = base_price * quantity  # Single assignment
    with_tax = subtotal * 1.08  # New variable
    with_discount = with_tax - (with_tax * 0.1)  # New variable
    return with_discount

# Or: Composition
def calculate_price(base_price: float, quantity: int) -> float:
    return (
        (base_price * quantity)  # Subtotal
        * 1.08  # Tax
        * 0.9  # Discount (1 - 0.1)
    )

# Database update
UPDATE functions
SET purity_level = 'pure',
    side_effects_json = '{"reassignment": false}',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'calculate_price';

# Result:
# ✅ No reassignment
# ✅ Each binding has single clear meaning
# ✅ Easier to reason about
```

---

**Replacing Loop with Reduce:**
```python
# Initial code (non-compliant)
def sum_prices(items):
    total = 0  # Initial
    for item in items:
        total += item.price  # Reassignment in loop
    return total

# AI calls: fp_no_reassignment()

# Workflow:
# 1. track_variable_bindings:
#    - total reassigned in loop (N times)
#    - Loop counter mutation pattern
#
# 2. loop_counter_mutation: replace_with_recursion_or_map
#    - Strategy: Use reduce/sum
#
# Refactored code (compliant)
def sum_prices(items: list[Item]) -> float:
    return sum(item.price for item in items)

# Or: Using reduce explicitly
from functools import reduce

def sum_prices(items: list[Item]) -> float:
    return reduce(lambda acc, item: acc + item.price, items, 0)

# Result:
# ✅ No reassignment
# ✅ Functional pattern (reduce)
# ✅ Declarative and concise
```

---

**Removing Accumulator Mutation:**
```python
# Initial code (non-compliant)
def filter_active_users(users):
    active = []  # Accumulator
    for user in users:
        if user.is_active:
            active.append(user)  # Mutation
    return active

# AI calls: fp_no_reassignment()

# Workflow:
# 1. track_variable_bindings:
#    - active mutated in loop (append)
#    - Accumulator pattern detected
#
# 2. accumulator_pattern: refactor_to_functional_fold
#    - Strategy: List comprehension
#
# Refactored code (compliant)
def filter_active_users(users: list[User]) -> list[User]:
    return [user for user in users if user.is_active]

# Or: Using filter
def filter_active_users(users: list[User]) -> list[User]:
    return list(filter(lambda u: u.is_active, users))

# Result:
# ✅ No accumulator mutation
# ✅ Functional filter pattern
# ✅ Immutable result
```

---

### ❌ Non-Compliant Usage

**Leaving Reassignment:**
```python
# ❌ Variable reassigned
def process(data):
    result = initial_transform(data)
    result = apply_rules(result)  # Reassignment
    result = finalize(result)  # Reassignment
    return result

# Why Non-Compliant:
# - result reassigned 2 times
# - Each reassignment changes meaning
# - Not immutable binding
```

**Corrected:**
```python
# ✅ New bindings
def process(data):
    initial = initial_transform(data)
    with_rules = apply_rules(initial)
    final = finalize(with_rules)
    return final
```

---

## Edge Cases

### Edge Case 1: Loop Variable (for loop)

**Issue**: Loop variable is implicitly reassigned each iteration

**Handling**:
```python
# Loop variable reassigned by loop construct
for i in range(10):
    print(i)  # i is reassigned each iteration

# Rule: Loop variable reassignment is acceptable
# (inherent to loop construct)
# BUT: Don't manually reassign inside loop
for i in range(10):
    i = i + 1  # ❌ Manual reassignment (don't do this)
```

**Directive Action**: Allow loop variable implicit reassignment, forbid manual reassignment inside loop.

---

### Edge Case 2: Exception Handler Variable

**Issue**: Exception variable used in except block

**Handling**:
```python
# Exception variable is implicitly assigned
try:
    risky_operation()
except ValueError as e:  # e assigned here
    handle_error(e)

# Rule: Exception variable assignment is acceptable
# (language construct, not user reassignment)
```

**Directive Action**: Allow exception variable assignment.

---

### Edge Case 3: With Statement Variable

**Issue**: Context manager variable assigned by with statement

**Handling**:
```python
# Context manager variable assigned
with open("file.txt") as f:  # f assigned here
    content = f.read()

# Rule: Context manager assignment is acceptable
# (language construct, single assignment per scope)
```

**Directive Action**: Allow context manager variable assignment.

---

## Related Directives

- **Called By**:
  - `fp_immutability` - Part of immutability enforcement
  - `project_compliance_check` - Scans for reassignments
  - `project_file_write` - Validates before writing
- **Calls**:
  - Database helpers - Updates functions table
  - `project_notes_log` - Logs refactoring decisions
- **Related**:
  - `fp_const_refactoring` - Enforces const declarations
  - `fp_state_elimination` - Eliminates global state

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: UPDATE purity_level, side_effects_json after refactoring
- **`notes`**: INSERT refactoring decisions

---

## Testing

1. **Detect reassignment** → Variable assigned 2+ times
   ```python
   def test():
       x = 5
       x = 10  # Reassignment

   assignments = track_assignments(test)
   assert len(assignments['x']) == 2
   ```

2. **Refactor to new binding** → New variable created
   ```python
   refactored = replace_reassignment_with_binding(code, 'x')
   assert 'x2 = 10' in refactored or 'new_x = 10' in refactored
   ```

3. **No reassignment** → Function compliant
   ```python
   def pure_func(x):
       y = x + 1
       return y

   result = fp_no_reassignment(pure_func)
   assert result.compliant == True
   ```

---

## Common Mistakes

- ❌ **Allowing increment operators** - `x += 1` is reassignment
- ❌ **Not detecting loop mutations** - Accumulator in loop is reassignment
- ❌ **Ignoring compound assignment** - `x *= 2` is reassignment
- ❌ **Missing conditional reassignment** - `if cond: x = y` is reassignment

---

## Roadblocks and Resolutions

### Roadblock 1: reassignment_found
**Issue**: Variable assigned multiple times in scope
**Resolution**: Replace with new variable name or composition

---

## References

None
---

*Part of AIFP v1.0 - Core FP directive for eliminating variable reassignment and ensuring single-assignment semantics*
