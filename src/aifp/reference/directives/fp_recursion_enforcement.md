# Directive: fp_recursion_enforcement

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Enforces FP-style iteration through recursion

---

## Purpose

The `fp_recursion_enforcement` directive transforms imperative loops (for, while) into pure recursive functions with tail-call optimization. This directive provides **functional iteration** that eliminates mutable loop counters and enables stack-safe recursion.

Recursion enforcement provides **FP-style iteration**, enabling:
- **No Mutable State**: Loop counters eliminated
- **Declarative Intent**: What to compute, not how to loop
- **Stack Safety**: Tail recursion optimized to iterative execution
- **Composability**: Recursive functions compose cleanly
- **Mathematical Clarity**: Recursive definitions match mathematical recurrence relations

This directive acts as a **loop eliminator** transforming imperative iteration into functional recursion.

**Important**: This directive is reference documentation for recursion patterns.
AI consults this when uncertain about converting imperative loops to recursion or complex recursive scenarios.

**FP recursion is baseline behavior**:
- AI writes recursive functions naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about converting imperative loops to recursive functions
- Complex recursion scenarios (mutual recursion, continuation-passing style)
- Edge cases with tail recursion optimization or stack depth concerns
- Need for detailed guidance on recursive patterns

**Context**:
- AI writes recursive functions as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_tail_recursion`, `fp_purity`, `fp_list_operations`) may reference this for guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: analyze_iteration_patterns

Scans code for imperative loops and converts them to tail-recursive functions.

**Steps**:
1. **Detect loops** - Find for/while loops
2. **Analyze loop variables** - Identify accumulator, counter, collection
3. **Check for side effects** - Ensure loop is pure
4. **Determine recursion pattern** - Tail recursive or accumulator-passing
5. **Generate recursive function** - Create pure recursive equivalent
6. **Apply tail-call optimization** - Mark for TCO if applicable

### Branches

**Branch 1: If for_loop_with_accumulator**
- **Then**: `convert_to_tail_recursion`
- **Details**: For loop accumulates result
  - Pattern: `for item in items: acc = f(acc, item)`
  - Convert to: Tail-recursive helper with accumulator
  - Base case: Empty collection returns accumulator
  - Recursive case: Process head, recurse on tail
  - Tail-call optimized
- **Result**: Returns tail-recursive function

**Branch 2: If while_loop**
- **Then**: `convert_to_conditional_recursion`
- **Details**: While loop with mutable condition
  - Pattern: `while condition: update_state()`
  - Convert to: Recursive function with condition check
  - Base case: Condition false, return result
  - Recursive case: Update state, recurse
  - Ensure termination guaranteed
- **Result**: Returns conditional recursive function

**Branch 3: If nested_loops**
- **Then**: `convert_to_nested_recursion`
- **Details**: Nested for/while loops
  - Pattern: `for x in xs: for y in ys: ...`
  - Convert to: Nested recursive functions
  - Outer recursion processes xs
  - Inner recursion processes ys
  - Can often flatten with cross product
- **Result**: Returns nested or flattened recursion

**Branch 4: If already_recursive**
- **Then**: `check_tail_recursion`
- **Details**: Code already uses recursion
  - Check if tail-recursive
  - Check if stack-safe
  - Optimize if not tail-recursive
  - Add @tail_recursive annotation
- **Result**: Returns optimized recursion

**Branch 5: If higher_order_applicable**
- **Then**: `convert_to_map_filter_reduce`
- **Details**: Loop matches map/filter/reduce pattern
  - Prefer higher-order functions over manual recursion
  - map: [f(x) for x in xs]
  - filter: [x for x in xs if p(x)]
  - reduce: fold(f, acc, xs)
  - More idiomatic than explicit recursion
- **Result**: Returns higher-order function call

**Fallback**: `prompt_user`
- **Details**: Complex loop pattern
  - Side effects present
  - Non-terminating loop
  - Dynamic iteration control
  - Ask user for guidance
- **Result**: User decides approach

---

## Examples

### ✅ Compliant Code

**Tail-Recursive Sum (Passes):**

```python
def sum_list(numbers: list[int]) -> int:
    """Sum list using tail recursion."""
    def sum_helper(nums: list[int], accumulator: int) -> int:
        # Base case: empty list
        if not nums:
            return accumulator
        # Recursive case: add head, recurse on tail
        head, *tail = nums
        return sum_helper(tail, accumulator + head)

    return sum_helper(numbers, 0)

# ✅ Tail-recursive
# ✅ No mutable state
# ✅ Stack-safe with TCO
# ✅ Accumulator-passing style
```

**Why Compliant**:
- Tail-recursive (recursive call is final operation)
- No mutable loop variables
- Pure function
- Stack-safe with tail-call optimization

---

**Recursive Factorial (Passes):**

```python
def factorial(n: int) -> int:
    """Calculate factorial using tail recursion."""
    def factorial_helper(n: int, accumulator: int) -> int:
        # Base case
        if n <= 1:
            return accumulator
        # Tail-recursive case
        return factorial_helper(n - 1, accumulator * n)

    return factorial_helper(n, 1)

# ✅ Tail-recursive
# ✅ Accumulator-passing
# ✅ No loop counter mutation
# ✅ Stack-safe
```

**Why Compliant**:
- Tail-recursive with accumulator
- No mutable state
- Base case guaranteed (n decreases)
- Stack-safe

---

**Recursive List Filter (Passes):**

```python
def filter_evens(numbers: list[int]) -> list[int]:
    """Filter even numbers using recursion."""
    # Base case: empty list
    if not numbers:
        return []

    head, *tail = numbers
    # Recursive case: include or skip head
    if head % 2 == 0:
        return [head] + filter_evens(tail)
    else:
        return filter_evens(tail)

# ✅ Pure recursive function
# ✅ No loops
# ✅ Declarative filtering
# ✅ Composable
```

**Why Compliant**:
- Pure recursion (no loops)
- No mutable accumulators
- Declarative pattern
- Functional style

---

**Recursive Map (Passes):**

```python
def map_double(numbers: list[int]) -> list[int]:
    """Double all numbers using recursion."""
    # Base case: empty list
    if not numbers:
        return []

    head, *tail = numbers
    # Recursive case: transform head, recurse on tail
    return [head * 2] + map_double(tail)

# ✅ Pure recursion
# ✅ No mutable state
# ✅ Declarative transformation
# ✅ FP style
```

**Why Compliant**:
- Recursive list transformation
- No loops or mutation
- Pure function
- Functional paradigm

---

### ❌ Non-Compliant Code

**Imperative For Loop (Violation):**

```python
# ❌ VIOLATION: Imperative for loop with mutable accumulator
def sum_list(numbers: list[int]) -> int:
    """Sum list using imperative loop."""
    total = 0  # ← Mutable accumulator
    for num in numbers:  # ← Imperative loop
        total += num  # ← Mutation each iteration
    return total

# Problem:
# - Uses imperative for loop
# - Mutable accumulator (total)
# - Not functional style
# - Should use recursion or reduce
```

**Why Non-Compliant**:
- Imperative for loop
- Mutable accumulator variable
- Not using recursion
- Violates FP principles

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Tail-recursive sum
def sum_list(numbers: list[int]) -> int:
    """Sum list using tail recursion."""
    def sum_helper(nums: list[int], acc: int) -> int:
        if not nums:
            return acc
        head, *tail = nums
        return sum_helper(tail, acc + head)

    return sum_helper(numbers, 0)

# Pure tail recursion
# No mutable state
# Stack-safe with TCO
```

---

**While Loop with Mutation (Violation):**

```python
# ❌ VIOLATION: While loop with mutable counter
def factorial(n: int) -> int:
    """Calculate factorial using while loop."""
    result = 1  # ← Mutable result
    counter = n  # ← Mutable counter

    while counter > 1:  # ← Imperative loop
        result *= counter  # ← Mutation
        counter -= 1  # ← Counter mutation

    return result

# Problem:
# - Imperative while loop
# - Two mutable variables (result, counter)
# - Not functional
# - Should use tail recursion
```

**Why Non-Compliant**:
- While loop with mutable state
- Multiple mutable variables
- Not recursive
- Not FP style

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Tail-recursive factorial
def factorial(n: int) -> int:
    """Calculate factorial using tail recursion."""
    def factorial_helper(n: int, acc: int) -> int:
        if n <= 1:
            return acc
        return factorial_helper(n - 1, acc * n)

    return factorial_helper(n, 1)

# Tail-recursive
# No mutable state
# Pure function
```

---

**Nested Loops (Violation):**

```python
# ❌ VIOLATION: Nested for loops
def cartesian_product(xs: list[int], ys: list[int]) -> list[tuple[int, int]]:
    """Generate cartesian product using nested loops."""
    result = []  # ← Mutable accumulator

    for x in xs:  # ← Outer loop
        for y in ys:  # ← Inner loop
            result.append((x, y))  # ← Mutation

    return result

# Problem:
# - Nested imperative loops
# - Mutable accumulator
# - Not using recursion or comprehension
# - Not functional
```

**Why Non-Compliant**:
- Nested for loops
- Mutable result list
- append() is mutation
- Should use recursion or list comprehension

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Recursive cartesian product
def cartesian_product(xs: list[int], ys: list[int]) -> list[tuple[int, int]]:
    """Generate cartesian product using recursion."""
    # Base case: empty first list
    if not xs:
        return []

    head, *tail = xs
    # Recursive case: pair head with all ys, recurse on tail
    pairs_with_head = [(head, y) for y in ys]
    pairs_with_tail = cartesian_product(tail, ys)
    return pairs_with_head + pairs_with_tail

# Pure recursion
# No mutable state
# Functional composition

# Or even better: Use comprehension (also FP)
def cartesian_product_v2(xs: list[int], ys: list[int]) -> list[tuple[int, int]]:
    """Generate cartesian product using comprehension."""
    return [(x, y) for x in xs for y in ys]
```

---

**Non-Tail Recursion (Violation):**

```python
# ❌ VIOLATION: Non-tail recursion (stack overflow risk)
def sum_list(numbers: list[int]) -> int:
    """Sum list using non-tail recursion."""
    # Base case
    if not numbers:
        return 0

    head, *tail = numbers
    # ❌ NOT tail-recursive: addition happens AFTER recursive call
    return head + sum_list(tail)  # ← Pending operation after recursion

# Problem:
# - Non-tail recursive (+ happens after recursion)
# - Stack frame kept alive for pending operation
# - Risk of stack overflow on large lists
# - Should use tail recursion with accumulator
```

**Why Non-Compliant**:
- Non-tail recursive
- Stack builds up with pending operations
- Not stack-safe
- Should use tail-call form

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Tail-recursive with accumulator
def sum_list(numbers: list[int]) -> int:
    """Sum list using tail recursion."""
    def sum_helper(nums: list[int], acc: int) -> int:
        if not nums:
            return acc
        head, *tail = nums
        # ✅ Tail-recursive: no pending operations
        return sum_helper(tail, acc + head)

    return sum_helper(numbers, 0)

# Tail-recursive
# Stack-safe
# No pending operations
```

---

## Edge Cases

### Edge Case 1: Infinite Recursion

**Issue**: Recursion without guaranteed termination

**Handling**:
```python
# ❌ Dangerous: No guaranteed base case
def countdown(n: int) -> int:
    if n == 0:  # What if n is negative?
        return 0
    return countdown(n - 1)

# ✅ Safe: Guaranteed termination
def countdown_safe(n: int) -> int:
    """Countdown with guaranteed termination."""
    if n <= 0:  # Catches negative numbers
        return 0
    return countdown_safe(n - 1)

# Always verify base case handles all inputs
```

**Directive Action**: Verify base case guarantees termination for all inputs.

---

### Edge Case 2: Large Lists (Stack Overflow)

**Issue**: Recursion on large lists may overflow stack

**Handling**:
```python
# Use tail recursion + TCO
@tail_recursive  # Compiler/interpreter optimizes to loop
def sum_large_list(numbers: list[int]) -> int:
    """Sum large list with TCO."""
    def sum_helper(nums: list[int], acc: int) -> int:
        if not nums:
            return acc
        head, *tail = nums
        return sum_helper(tail, acc + head)

    return sum_helper(numbers, 0)

# Or use fold/reduce (which is typically stack-safe)
from functools import reduce
def sum_large_list_v2(numbers: list[int]) -> int:
    """Sum using fold (stack-safe)."""
    return reduce(lambda acc, x: acc + x, numbers, 0)
```

**Directive Action**: Use tail recursion with TCO annotation or fold/reduce for large lists.

---

### Edge Case 3: Mutual Recursion

**Issue**: Two functions call each other recursively

**Handling**:
```python
# Mutual recursion: is_even/is_odd
def is_even(n: int) -> bool:
    """Check if number is even (mutual recursion)."""
    if n == 0:
        return True
    return is_odd(n - 1)

def is_odd(n: int) -> bool:
    """Check if number is odd (mutual recursion)."""
    if n == 0:
        return False
    return is_even(n - 1)

# Ensure both have proper base cases
# Both must guarantee termination
# TCO may not apply (language-dependent)
```

**Directive Action**: Support mutual recursion, verify both functions have base cases.

---

### Edge Case 4: Early Exit in Loop

**Issue**: Loop with break/continue/early return

**Handling**:
```python
# Imperative loop with early exit
def find_first_even(numbers: list[int]) -> int | None:
    for num in numbers:
        if num % 2 == 0:
            return num  # Early exit
    return None

# ✅ Recursive equivalent
def find_first_even_recursive(numbers: list[int]) -> int | None:
    """Find first even number using recursion."""
    # Base case: empty list
    if not numbers:
        return None

    head, *tail = numbers
    # Early exit equivalent: return immediately if match
    if head % 2 == 0:
        return head
    # Otherwise recurse
    return find_first_even_recursive(tail)

# Early exit becomes immediate return in base/recursive case
```

**Directive Action**: Convert early exits to immediate returns in recursive cases.

---

## Recursion Patterns

### Pattern 1: Accumulator-Passing Style

```python
# Template for accumulator-passing tail recursion
def process_list(items: list[T]) -> R:
    """Process list with accumulator."""
    def helper(items: list[T], acc: R) -> R:
        # Base case: empty list
        if not items:
            return acc

        head, *tail = items
        # Process head, update accumulator, tail recurse
        new_acc = combine(acc, head)
        return helper(tail, new_acc)

    return helper(items, initial_accumulator)
```

### Pattern 2: Direct Recursion

```python
# Template for direct recursion (when result builds backward)
def process_list(items: list[T]) -> list[R]:
    """Process list with direct recursion."""
    # Base case: empty list
    if not items:
        return []

    head, *tail = items
    # Process head, recurse on tail, combine
    return [transform(head)] + process_list(tail)
```

### Pattern 3: Conditional Recursion (While Loops)

```python
# Template for conditional recursion (while loop equivalent)
def process_until_condition(state: S) -> R:
    """Process until condition met."""
    # Base case: condition met
    if is_done(state):
        return extract_result(state)

    # Recursive case: update state, recurse
    new_state = update(state)
    return process_until_condition(new_state)
```

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Recursive functions must be pure
  - `fp_no_reassignment` - Recursion eliminates variable reassignment
- **Triggers**:
  - `fp_tail_recursion` - Optimize tail-recursive calls
- **Called By**:
  - `project_file_write` - Convert loops before writing
  - Works with `fp_chaining` - Recursive functions compose
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `is_recursive = 1`, `is_tail_recursive = 1` for recursive functions

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

1. **For loop detected** → Directive converts to tail recursion
   ```python
   # Before: for num in numbers: total += num
   # After: Tail-recursive helper with accumulator
   ```

2. **While loop detected** → Directive converts to conditional recursion
   ```python
   # Before: while n > 0: result *= n; n -= 1
   # After: Recursive function with base case
   ```

3. **Check database** → Verify recursion marked
   ```sql
   SELECT name, is_recursive, is_tail_recursive
   FROM functions
   WHERE is_recursive = 1;
   ```

---

## Common Mistakes

- ❌ **Non-tail recursion on large lists** - Stack overflow risk
- ❌ **Missing base case** - Infinite recursion
- ❌ **Base case doesn't handle all inputs** - Some inputs cause infinite recursion
- ❌ **Using recursion when map/filter/reduce better** - Less idiomatic
- ❌ **Not using accumulator for tail recursion** - Stack builds up

---

## Roadblocks and Resolutions

### Roadblock 1: for_loop_with_accumulator
**Issue**: Imperative for loop with mutable accumulator
**Resolution**: Convert to tail-recursive helper with accumulator parameter

### Roadblock 2: while_loop_mutation
**Issue**: While loop with mutable state
**Resolution**: Convert to conditional recursion with state as parameter

### Roadblock 3: non_tail_recursion
**Issue**: Recursion with pending operations (stack risk)
**Resolution**: Refactor to tail-recursive form with accumulator

### Roadblock 4: nested_loops
**Issue**: Nested for/while loops
**Resolution**: Convert to nested recursion or flatten with comprehension

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for tail-recursive loop elimination*
