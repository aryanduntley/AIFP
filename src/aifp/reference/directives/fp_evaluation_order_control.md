# Directive: fp_evaluation_order_control

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: LOW - Ensures deterministic evaluation in complex expressions

---

## Purpose

The `fp_evaluation_order_control` directive ensures consistent, deterministic evaluation order for expressions and function calls. This directive provides **evaluation predictability** that guarantees identical outputs for identical inputs, even in parallel or lazy-evaluation contexts.

Evaluation order control provides **deterministic execution**, enabling:
- **Reproducible Results**: Same code always produces same output
- **No Race Conditions**: Parallel evaluation doesn't affect results
- **Explicit Sequencing**: Evaluation order is clear from code structure
- **Debug Predictability**: Easier to reason about execution flow
- **Multi-Language Consistency**: Same semantics across languages

This directive acts as a **determinism guardian** ensuring evaluation order never affects program correctness.

---

## When to Apply

This directive applies when:
- **Multiple expressions evaluated** - Order could affect result
- **Side effects present** - Even in IO boundaries
- **Parallel execution** - Multiple threads evaluate expressions
- **Lazy evaluation** - Deferred computation order matters
- **Cross-language code** - Different default evaluation orders
- **Called by project directives**:
  - `project_file_write` - Ensure written code has deterministic evaluation
  - Works with `fp_purity` - Pure functions should have no order dependency
  - Works with `fp_parallel_evaluation` - Parallel code must be order-independent

---

## Workflow

### Trunk: check_evaluation_sequence

Analyzes code expressions to identify evaluation order dependencies and ensures deterministic execution.

**Steps**:
1. **Parse expression tree** - Build AST of all subexpressions
2. **Identify evaluation points** - Function calls, operators, lazy constructs
3. **Check for order dependency** - Does order affect result?
4. **Verify determinism** - Is order guaranteed by language spec?
5. **Flag non-deterministic patterns** - Unspecified evaluation order
6. **Reorder if needed** - Make order explicit

### Branches

**Branch 1: If non_deterministic_order**
- **Then**: `reorder_for_consistency`
- **Details**: Expression evaluation order is unspecified
  - Pattern: `f(g(), h())` - g() and h() order unspecified in some languages
  - Reorder to explicit sequence: `temp1 = g(); temp2 = h(); f(temp1, temp2)`
  - Make evaluation order left-to-right and explicit
  - Eliminate ambiguity
- **Result**: Returns reordered code

**Branch 2: If parallel_evaluation_detected**
- **Then**: `verify_order_independence`
- **Details**: Code uses parallel execution
  - Pattern: Parallel map, concurrent futures
  - Verify functions are pure (no order dependency)
  - Ensure result aggregation is order-independent
  - Use commutative/associative operations only
- **Result**: Returns verified parallel code

**Branch 3: If lazy_evaluation**
- **Then**: `ensure_consistent_forcing`
- **Details**: Lazy expressions with forcing order
  - Pattern: Generators, thunks, lazy sequences
  - Ensure forcing order is deterministic
  - Document when expressions are evaluated
  - Avoid relying on side effects in lazy contexts
- **Result**: Returns deterministic lazy code

**Branch 4: If already_deterministic**
- **Then**: `mark_as_deterministic`
- **Details**: Evaluation order is guaranteed
  - Language specifies left-to-right
  - Or code explicitly sequences operations
  - Order doesn't affect result (pure functions)
  - Already compliant
- **Result**: Code passes check

**Fallback**: `prompt_user`
- **Details**: Complex evaluation order pattern
  - Unclear if order matters
  - Language-specific edge case
  - Ask user for guidance
- **Result**: User decides approach

---

## Examples

### ✅ Compliant Code

**Explicit Evaluation Order (Passes):**

```python
# ✅ Good: Explicit left-to-right evaluation
def calculate_result(x: int, y: int) -> int:
    """Calculate with explicit evaluation order."""
    # Step 1: Evaluate first operation
    step1 = expensive_operation_1(x)

    # Step 2: Evaluate second operation
    step2 = expensive_operation_2(y)

    # Step 3: Combine results
    return step1 + step2

# Evaluation order is clear and deterministic
# No ambiguity about which operation runs first
# Easy to understand and maintain
```

**Why Compliant**:
- Explicit sequencing with intermediate variables
- Clear evaluation order (step1, then step2, then combine)
- No reliance on language-specific evaluation order
- Self-documenting code flow

---

**Pure Functions (Order-Independent) (Passes):**

```python
# ✅ Good: Pure functions with no evaluation order dependency
def add(x: int, y: int) -> int:
    """Pure addition - order doesn't matter."""
    return x + y

# Call with multiple subexpressions
result = add(multiply(2, 3), multiply(4, 5))

# Even though multiply() calls could evaluate in any order,
# result is always the same because:
# 1. multiply() is pure (no side effects)
# 2. add() is commutative (a + b == b + a)
# 3. No order dependency

# Compliant because order doesn't affect result
```

**Why Compliant**:
- All functions are pure
- No side effects
- Operations are order-independent
- Result is always deterministic

---

**Explicit Parallel Evaluation (Passes):**

```python
from concurrent.futures import ProcessPoolExecutor
from functools import reduce

# ✅ Good: Explicit parallel evaluation with order-independent aggregation
def parallel_sum(numbers: list[int]) -> int:
    """Sum numbers in parallel with deterministic result."""
    # Each worker computes partial sum (order doesn't matter for addition)
    def chunk_sum(chunk: list[int]) -> int:
        return reduce(lambda acc, x: acc + x, chunk, 0)

    # Split into chunks
    chunk_size = len(numbers) // 4
    chunks = [numbers[i:i+chunk_size] for i in range(0, len(numbers), chunk_size)]

    # Parallel evaluation of chunks
    with ProcessPoolExecutor() as executor:
        partial_sums = list(executor.map(chunk_sum, chunks))

    # Combine results (addition is associative and commutative)
    return sum(partial_sums)

# Evaluation order of chunks doesn't matter
# Final result is always deterministic
# Addition is order-independent
```

**Why Compliant**:
- Parallel evaluation explicitly documented
- Aggregation operation (sum) is commutative and associative
- Result is order-independent
- Deterministic despite parallel execution

---

**Language-Guaranteed Order (Passes):**

```python
# ✅ Good: Python guarantees left-to-right evaluation
def process_data(x: int) -> int:
    """Python evaluates arguments left-to-right."""
    return compute(
        operation_a(x),  # Evaluated first
        operation_b(x),  # Evaluated second
        operation_c(x)   # Evaluated third
    )

# Python language specification guarantees left-to-right
# evaluation of function arguments.
# This is deterministic and compliant.
```

**Why Compliant**:
- Python specification guarantees evaluation order
- Left-to-right is well-defined
- Deterministic by language design
- No ambiguity

---

### ❌ Non-Compliant Code

**Unspecified Evaluation Order (Violation):**

```python
# ❌ VIOLATION: Evaluation order undefined (in some languages)
def calculate_result(x: int) -> int:
    """Evaluation order of arguments is unspecified."""
    return compute(
        operation_a(x),  # Which order?
        operation_b(x),  # These could evaluate in any order
        operation_c(x)   # depending on language/compiler
    )

# Problem:
# - If operations have side effects, result varies
# - If operations are expensive, unclear which runs first
# - C/C++ don't specify argument evaluation order
# - JavaScript doesn't specify object property evaluation order
# - Not portable across languages
```

**Why Non-Compliant**:
- Relies on unspecified evaluation order
- Different languages may evaluate differently
- Not portable
- Could be non-deterministic with side effects

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Explicit evaluation order
def calculate_result(x: int) -> int:
    """Explicit left-to-right evaluation."""
    # Make order explicit
    result_a = operation_a(x)  # First
    result_b = operation_b(x)  # Second
    result_c = operation_c(x)  # Third

    return compute(result_a, result_b, result_c)

# Now evaluation order is explicit and deterministic
# Works the same in all languages
```

---

**Non-Deterministic Dictionary Iteration (Violation):**

```python
# ❌ VIOLATION: Dictionary iteration order was unspecified (Python < 3.7)
def process_config(config: dict) -> list[str]:
    """Process config keys."""
    results = []
    for key in config:  # ← Order was unspecified in Python < 3.7
        results.append(process_key(key))
    return results

# Problem:
# - Before Python 3.7, dict iteration order was not guaranteed
# - Results could vary between runs
# - Not deterministic
# - Order-dependent results
```

**Why Non-Compliant**:
- Relies on implementation detail (dict order)
- Non-deterministic in older Python versions
- Results vary between runs
- Not explicitly ordered

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Explicit sort for deterministic order
def process_config(config: dict) -> list[str]:
    """Process config keys in deterministic order."""
    # Sort keys for deterministic iteration
    results = []
    for key in sorted(config.keys()):  # ← Explicit alphabetical order
        results.append(process_key(key))
    return results

# Or better yet, use list comprehension
def process_config_v2(config: dict) -> list[str]:
    """Process config keys in deterministic order."""
    return [process_key(key) for key in sorted(config.keys())]

# Now order is explicit and deterministic
```

---

**Short-Circuit Evaluation Dependency (Violation):**

```python
# ❌ VIOLATION: Relies on short-circuit evaluation with side effects
def validate_and_process(data: str) -> bool:
    """Validate and process data."""
    # ❌ Side effect in condition
    return is_valid(data) and process_data(data) and save_result(data)

# Problem:
# - If is_valid() returns False, process_data() never runs
# - Relies on short-circuit evaluation order
# - Side effects in boolean expression
# - Order determines which side effects occur
# - Not clear which functions run
```

**Why Non-Compliant**:
- Side effects in boolean expressions
- Behavior depends on short-circuit evaluation
- Unclear which functions execute
- Not explicit about control flow

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Explicit control flow
def validate_and_process(data: str) -> bool:
    """Validate and process data with explicit control flow."""
    # Step 1: Validate
    if not is_valid(data):
        return False

    # Step 2: Process
    if not process_data(data):
        return False

    # Step 3: Save
    if not save_result(data):
        return False

    return True

# Explicit sequence of operations
# Clear which functions run and when
# No reliance on short-circuit evaluation
```

---

**Parallel Race Condition (Violation):**

```python
from concurrent.futures import ThreadPoolExecutor

# ❌ VIOLATION: Race condition with order-dependent operations
results = []

def process_item(item: int) -> None:
    """Process item and append result."""
    result = expensive_computation(item)
    results.append(result)  # ← Race condition!

# Parallel execution
with ThreadPoolExecutor() as executor:
    executor.map(process_item, range(100))

# Problem:
# - Multiple threads append to same list
# - Final order is non-deterministic
# - Race condition on shared state
# - Results vary between runs
```

**Why Non-Compliant**:
- Shared mutable state in parallel context
- Non-deterministic ordering
- Race condition
- Results vary

**Refactored (Compliant):**

```python
from concurrent.futures import ThreadPoolExecutor

# ✅ REFACTORED: Pure functions with deterministic aggregation
def process_item(item: int) -> int:
    """Process item (pure function)."""
    return expensive_computation(item)

# Parallel execution with deterministic result collection
with ThreadPoolExecutor() as executor:
    # map() returns results in input order
    results = list(executor.map(process_item, range(100)))

# Results are in deterministic order matching input order
# No shared state
# No race conditions
```

---

## Edge Cases

### Edge Case 1: Lazy Evaluation with Side Effects

**Issue**: Lazy evaluation order affects side effects

**Handling**:
```python
# ❌ Problematic: Side effect in lazy generator
def generate_items():
    for i in range(10):
        print(f"Generating {i}")  # Side effect!
        yield i

gen = generate_items()
# When does printing happen? Non-deterministic!

# ✅ Better: Separate side effects from generation
def log_generation(i: int) -> None:
    """Log generation event."""
    print(f"Generating {i}")

def generate_items_pure() -> list[int]:
    """Generate items without side effects."""
    items = list(range(10))
    # Log separately at explicit point
    for i in items:
        log_generation(i)
    return items
```

**Directive Action**: Avoid side effects in lazy contexts; make evaluation points explicit.

---

### Edge Case 2: Language-Specific Evaluation Order

**Issue**: Different languages have different evaluation order rules

**Handling**:
```python
# C/C++: Argument evaluation order is unspecified
# f(g(), h()) - could be g() then h(), or h() then g()

# Python: Left-to-right guaranteed
# f(g(), h()) - always g() then h()

# JavaScript: Left-to-right for function args, but property access unspecified
# {a: f(), b: g()} - order of f() and g() unspecified

# AIFP Standard: Always make order explicit
result_g = g()
result_h = h()
f(result_g, result_h)

# Works consistently across all languages
```

**Directive Action**: Use explicit sequencing for cross-language compatibility.

---

### Edge Case 3: Short-Circuit Operators

**Issue**: && and || short-circuit evaluation

**Handling**:
```python
# Short-circuit is deterministic but can be unclear
# ✅ Compliant IF no side effects
def is_valid_and_processable(data: str) -> bool:
    """Pure predicate with short-circuit."""
    return len(data) > 0 and data[0].isalpha()
    # Short-circuit prevents index error
    # No side effects, so deterministic

# ❌ Non-compliant if side effects
def process_if_valid(data: str) -> bool:
    return is_valid(data) and process(data)  # process() has side effect
    # Side effect only happens if is_valid() is True
    # Unclear when process() runs

# ✅ Better: Explicit control flow
def process_if_valid_explicit(data: str) -> bool:
    if is_valid(data):
        return process(data)
    return False
```

**Directive Action**: Allow short-circuit for pure predicates; require explicit control flow for side effects.

---

### Edge Case 4: Parallel Aggregation Order

**Issue**: Parallel results need deterministic aggregation

**Handling**:
```python
from concurrent.futures import ProcessPoolExecutor

# ❌ Order-dependent aggregation
def parallel_process_bad(items: list[int]) -> list[int]:
    with ProcessPoolExecutor() as executor:
        # as_completed() returns results in non-deterministic order!
        futures = [executor.submit(process, item) for item in items]
        return [f.result() for f in as_completed(futures)]

# ✅ Order-independent or explicitly ordered
def parallel_process_good(items: list[int]) -> list[int]:
    with ProcessPoolExecutor() as executor:
        # map() returns results in input order
        return list(executor.map(process, items))

# ✅ Or use commutative/associative aggregation
def parallel_sum(items: list[int]) -> int:
    with ProcessPoolExecutor() as executor:
        # Order doesn't matter for sum (commutative + associative)
        return sum(executor.map(process, items))
```

**Directive Action**: Use order-preserving aggregation or commutative/associative operations.

---

## Language-Specific Evaluation Order

### Python

```python
# Python guarantees left-to-right evaluation for:
# - Function arguments: f(a(), b(), c()) - always a, b, c
# - Operators: a + b + c - always left-to-right
# - Comparison chains: a < b < c - evaluates b once
# - Dict/set literals (3.7+): {a(): b()} - a() then b()

# ✅ Can rely on left-to-right in Python
result = compute(step1(), step2(), step3())  # Deterministic
```

### JavaScript

```javascript
// JavaScript guarantees left-to-right for:
// - Function arguments: f(a(), b(), c()) - always a, b, c
// - Operators: a + b + c - always left-to-right

// ❌ Unspecified order:
// - Object properties: {a: f(), b: g()} - order unspecified
// - Use explicit sequencing for cross-engine consistency

// ✅ Explicit order
const result1 = f();
const result2 = g();
const obj = {a: result1, b: result2};
```

### C/C++

```c
// ❌ C/C++ does NOT guarantee argument evaluation order
// f(g(), h()) - could be g() then h() OR h() then g()

// ✅ Always use explicit sequencing
int result_g = g();
int result_h = h();
f(result_g, result_h);
```

### Rust

```rust
// Rust guarantees left-to-right evaluation for most contexts

// ✅ Deterministic
let result = compute(operation_a(), operation_b(), operation_c());

// Function arguments evaluated left-to-right
// Match patterns evaluated top-to-bottom
```

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Pure functions are order-independent
- **Triggers**:
  - `fp_parallel_evaluation` - Parallel code needs order independence
- **Called By**:
  - `project_file_write` - Ensure written code is deterministic
  - Works with `fp_lazy_evaluation` - Control lazy forcing order
- **Escalates To**: None

---

## Helper Functions Used

- `parse_evaluation_order(ast: AST) -> EvaluationOrder` - Determine evaluation sequence
- `check_order_dependency(expr: Expression) -> bool` - Check if order affects result
- `verify_language_guarantees(language: str, expr: Expression) -> bool` - Check language spec
- `reorder_for_determinism(code: str) -> str` - Make evaluation order explicit
- `update_functions_table(func_id: int, is_deterministic: bool)` - Update database

---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `is_deterministic = 1` for functions with guaranteed evaluation order
- **`notes`**: Logs evaluation order issues with `note_type = 'determinism'`

---

## Testing

How to verify this directive is working:

1. **Non-deterministic order detected** → Directive makes it explicit
   ```python
   # Before: f(g(), h())
   # After: temp1 = g(); temp2 = h(); f(temp1, temp2)
   ```

2. **Parallel evaluation** → Directive verifies order independence
   ```python
   # Ensures aggregation operation is commutative/associative
   ```

3. **Check database** → Verify determinism marked
   ```sql
   SELECT name, is_deterministic
   FROM functions
   WHERE is_deterministic = 1;
   ```

---

## Common Mistakes

- ❌ **Assuming evaluation order when unspecified** - Not portable
- ❌ **Side effects in short-circuit expressions** - Unclear when effects occur
- ❌ **Non-deterministic parallel aggregation** - Results vary between runs
- ❌ **Relying on dict iteration order** - Only guaranteed in Python 3.7+
- ❌ **Lazy evaluation with side effects** - Unclear when side effects happen

---

## Roadblocks and Resolutions

### Roadblock 1: order_variation
**Issue**: Expression evaluation order varies between languages
**Resolution**: Use explicit sequencing with intermediate variables for cross-language consistency

### Roadblock 2: parallel_non_determinism
**Issue**: Parallel execution produces different results on each run
**Resolution**: Ensure all operations are pure and aggregation is order-independent (commutative/associative)

### Roadblock 3: lazy_side_effects
**Issue**: Side effects in lazy contexts execute at unpredictable times
**Resolution**: Separate side effects from lazy computation; make evaluation points explicit

### Roadblock 4: short_circuit_side_effects
**Issue**: Side effects only occur when short-circuit doesn't trigger
**Resolution**: Use explicit control flow (if statements) instead of boolean operators with side effects

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-evaluation-order-control)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#optimization)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for deterministic evaluation order control*
