# Directive: fp_list_operations

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: HIGH - Core FP transformation pattern

---

## Purpose

The `fp_list_operations` directive refactors imperative loops into declarative list transformations using `map`, `filter`, and `reduce`. This directive is fundamental to functional programming, replacing **imperative iteration** with **declarative transformations** that express intent clearly and compose elegantly.

List operations provide **core FP patterns**, enabling:
- **Declarative Code**: Express what to do, not how to do it
- **Composability**: Chain operations without intermediate variables
- **Readability**: Clear intent (map = transform, filter = select, reduce = aggregate)
- **No Mutation**: Avoid loop counters and mutable accumulators
- **Parallelizability**: Pure operations can be parallelized automatically

This directive is often the **first step in FP conversion** - replacing for/while loops with functional list operations.

**Important**: This directive is reference documentation for functional list operation patterns.
AI consults this when uncertain about converting loops to functional operations or complex list transformation scenarios.

**FP list operations are baseline behavior**:
- AI writes functional list operations naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about converting imperative loops to functional operations
- Complex list transformation scenarios (nested loops, multiple operations)
- Edge cases with stateful aggregations or mixed patterns
- Need for detailed guidance on map/filter/reduce usage

**Context**:
- AI writes functional list operations as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_purity`, `fp_immutability`, `fp_recursion_enforcement`) may reference this for guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: analyze_loops

Scans code to detect imperative loops that can be converted to functional list operations.

**Steps**:
1. **Parse loop constructs** - Identify for/while loops
2. **Analyze loop body** - Determine operation type (transform, filter, aggregate)
3. **Check for mutations** - Identify mutable accumulators
4. **Classify operation** - Map, filter, reduce, or combination
5. **Verify purity** - Ensure loop body is pure
6. **Generate functional equivalent** - Convert to map/filter/reduce

### Branches

**Branch 1: If transform_loop**
- **Then**: `convert_to_map`
- **Details**: Loop transforms each element
  - Pattern: `for x in items: result.append(f(x))`
  - Convert to: `result = map(f, items)` or `[f(x) for x in items]`
  - Pure transformation of each element
- **Result**: Returns map-based code

**Branch 2: If filter_loop**
- **Then**: `convert_to_filter`
- **Details**: Loop selects elements based on condition
  - Pattern: `for x in items: if pred(x): result.append(x)`
  - Convert to: `result = filter(pred, items)` or `[x for x in items if pred(x)]`
  - Pure predicate selection
- **Result**: Returns filter-based code

**Branch 3: If aggregate_loop**
- **Then**: `convert_to_reduce`
- **Details**: Loop combines elements into single value
  - Pattern: `acc = init; for x in items: acc = combine(acc, x)`
  - Convert to: `result = reduce(combine, items, init)`
  - Pure aggregation function
- **Result**: Returns reduce-based code

**Branch 4: If chained_operations**
- **Then**: `convert_to_pipeline`
- **Details**: Loop performs multiple operations
  - Pattern: Multiple transformations/filters in sequence
  - Convert to: Chained map/filter operations
  - Clean pipeline of transformations
- **Result**: Returns pipeline code

**Branch 5: If already_functional**
- **Then**: `mark_compliant`
- **Details**: Already using map/filter/reduce
  - No imperative loops
  - Functional style
  - Mark as compliant
- **Result**: Code passes check

**Fallback**: `prompt_user`
- **Details**: Complex loop not easily convertible
  - Multiple mutations
  - Complex control flow
  - Ask user for guidance
- **Result**: User decides conversion strategy

---

## Examples

### ✅ Compliant Code

**Map Operation (Passes):**
```python
# Functional map - transforms each element
def double_values(numbers: list[int]) -> list[int]:
    """
    Double all numbers using map.

    Functional transformation - pure, composable.
    """
    return list(map(lambda x: x * 2, numbers))

# Or with list comprehension (also functional)
def double_values_v2(numbers: list[int]) -> list[int]:
    """Double all numbers using list comprehension."""
    return [x * 2 for x in numbers]

# Usage
result = double_values([1, 2, 3, 4, 5])
# Returns: [2, 4, 6, 8, 10]
```

**Why Compliant**:
- Declarative transformation
- No mutation
- Pure function
- Clear intent

---

**Filter Operation (Passes):**
```python
# Functional filter - selects elements
def get_even_numbers(numbers: list[int]) -> list[int]:
    """
    Get even numbers using filter.

    Functional selection - pure predicate.
    """
    return list(filter(lambda x: x % 2 == 0, numbers))

# Or with list comprehension
def get_even_numbers_v2(numbers: list[int]) -> list[int]:
    """Get even numbers using comprehension."""
    return [x for x in numbers if x % 2 == 0]

# Usage
result = get_even_numbers([1, 2, 3, 4, 5, 6])
# Returns: [2, 4, 6]
```

**Why Compliant**:
- Declarative selection
- Pure predicate
- No mutation
- Clear filtering logic

---

**Reduce Operation (Passes):**
```python
from functools import reduce

# Functional reduce - aggregates elements
def sum_numbers(numbers: list[int]) -> int:
    """
    Sum all numbers using reduce.

    Functional aggregation - pure combiner.
    """
    return reduce(lambda acc, x: acc + x, numbers, 0)

# For sum specifically, use built-in
def sum_numbers_v2(numbers: list[int]) -> int:
    """Sum using built-in (preferred for sum)."""
    return sum(numbers)

# Usage
result = sum_numbers([1, 2, 3, 4, 5])
# Returns: 15
```

**Why Compliant**:
- Declarative aggregation
- Pure combiner function
- No mutable accumulator
- Functional reduction

---

**Chained Operations (Passes):**
```python
# Functional pipeline - chained operations
def process_numbers(numbers: list[int]) -> int:
    """
    Process numbers: filter evens, double them, sum.

    Functional pipeline - composable operations.
    """
    evens = filter(lambda x: x % 2 == 0, numbers)
    doubled = map(lambda x: x * 2, evens)
    total = sum(doubled)
    return total

# Or as one-liner
def process_numbers_v2(numbers: list[int]) -> int:
    """Process numbers in functional pipeline."""
    return sum(map(lambda x: x * 2, filter(lambda x: x % 2 == 0, numbers)))

# Or with comprehension
def process_numbers_v3(numbers: list[int]) -> int:
    """Process numbers with comprehension."""
    return sum(x * 2 for x in numbers if x % 2 == 0)

# Usage
result = process_numbers([1, 2, 3, 4, 5, 6])
# Returns: 24 (2*2 + 4*2 + 6*2 = 4 + 8 + 12 = 24)
```

**Why Compliant**:
- Functional pipeline
- Chained operations
- No intermediate mutations
- Clear data flow

---

### ❌ Non-Compliant Code

**Imperative Transform Loop (Violation):**
```python
# ❌ VIOLATION: Imperative loop for transformation
def double_values(numbers: list[int]) -> list[int]:
    """Double all numbers using imperative loop."""
    result = []  # ← Mutable accumulator
    for num in numbers:  # ← Imperative loop
        result.append(num * 2)  # ← Mutation
    return result

# Problem:
# - Imperative loop structure
# - Mutable result list
# - Explicit append calls
# - Not composable
```

**Why Non-Compliant**:
- Imperative loop (not declarative)
- Mutation of result list
- Verbose and unclear intent
- Should use map

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Functional map
def double_values(numbers: list[int]) -> list[int]:
    """Double all numbers using map."""
    return [x * 2 for x in numbers]

# Clear, concise, functional
```

---

**Imperative Filter Loop (Violation):**
```python
# ❌ VIOLATION: Imperative loop for filtering
def get_positive_numbers(numbers: list[int]) -> list[int]:
    """Get positive numbers using imperative loop."""
    result = []  # ← Mutable accumulator
    for num in numbers:  # ← Imperative loop
        if num > 0:  # ← Conditional
            result.append(num)  # ← Mutation
    return result

# Problem:
# - Imperative loop
# - Mutable accumulator
# - Manual conditional logic
# - Not composable
```

**Why Non-Compliant**:
- Imperative filtering
- Mutation
- Verbose
- Should use filter

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Functional filter
def get_positive_numbers(numbers: list[int]) -> list[int]:
    """Get positive numbers using filter."""
    return [x for x in numbers if x > 0]

# Or with filter function
def get_positive_numbers_v2(numbers: list[int]) -> list[int]:
    """Get positive numbers using filter."""
    return list(filter(lambda x: x > 0, numbers))

# Clear, functional filtering
```

---

**Imperative Reduce Loop (Violation):**
```python
# ❌ VIOLATION: Imperative loop for aggregation
def calculate_product(numbers: list[int]) -> int:
    """Calculate product using imperative loop."""
    result = 1  # ← Mutable accumulator
    for num in numbers:  # ← Imperative loop
        result *= num  # ← Mutation
    return result

# Problem:
# - Imperative accumulation
# - Mutable result variable
# - Manual state management
# - Not composable
```

**Why Non-Compliant**:
- Imperative aggregation
- Mutable accumulator
- Not functional
- Should use reduce

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Functional reduce
from functools import reduce

def calculate_product(numbers: list[int]) -> int:
    """Calculate product using reduce."""
    return reduce(lambda acc, x: acc * x, numbers, 1)

# Clear, functional aggregation
```

---

**Mixed Operations Loop (Violation):**
```python
# ❌ VIOLATION: Mixed operations in single loop
def process_scores(scores: list[int]) -> float:
    """Process scores: filter passing, double, average."""
    passing = []  # ← Mutable accumulator 1
    for score in scores:  # ← Imperative loop
        if score >= 60:  # ← Filter logic
            passing.append(score)  # ← Mutation

    doubled = []  # ← Mutable accumulator 2
    for score in passing:  # ← Another loop
        doubled.append(score * 2)  # ← Mutation

    total = 0  # ← Mutable accumulator 3
    for score in doubled:  # ← Third loop
        total += score  # ← Mutation

    return total / len(doubled) if doubled else 0

# Problem:
# - Three separate imperative loops
# - Multiple mutable accumulators
# - Not composable
# - Verbose and unclear
```

**Why Non-Compliant**:
- Multiple imperative loops
- Many mutable accumulators
- Should be functional pipeline

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Functional pipeline
def process_scores(scores: list[int]) -> float:
    """Process scores: filter, double, average."""
    passing = [s for s in scores if s >= 60]  # Filter
    doubled = [s * 2 for s in passing]  # Map
    return sum(doubled) / len(doubled) if doubled else 0  # Reduce

# Or as one expression
def process_scores_v2(scores: list[int]) -> float:
    """Process scores in functional pipeline."""
    doubled = [s * 2 for s in scores if s >= 60]
    return sum(doubled) / len(doubled) if doubled else 0

# Clear, functional, composable
```

---

## Edge Cases

### Edge Case 1: Early Termination Loops

**Issue**: Loop breaks early based on condition

**Handling**:
```python
# Imperative loop with break
def find_first_even(numbers: list[int]) -> int:
    for num in numbers:
        if num % 2 == 0:
            return num  # Early return
    return None

# Functional equivalent with filter + next
def find_first_even_functional(numbers: list[int]) -> int:
    """Find first even number functionally."""
    evens = filter(lambda x: x % 2 == 0, numbers)
    return next(evens, None)  # Get first or None

# Or with generator expression (lazy)
def find_first_even_v2(numbers: list[int]) -> int:
    """Find first even with generator."""
    return next((x for x in numbers if x % 2 == 0), None)
```

**Directive Action**: Use `next()` with filter/generator for early termination.

---

### Edge Case 2: Index-Based Operations

**Issue**: Loop uses index, not just value

**Handling**:
```python
# Imperative loop with index
def add_indices(numbers: list[int]) -> list[int]:
    result = []
    for i, num in enumerate(numbers):
        result.append(num + i)
    return result

# Functional with enumerate
def add_indices_functional(numbers: list[int]) -> list[int]:
    """Add indices using enumerate."""
    return [num + i for i, num in enumerate(numbers)]

# Or with map
def add_indices_v2(numbers: list[int]) -> list[int]:
    """Add indices using map."""
    return list(map(lambda pair: pair[1] + pair[0], enumerate(numbers)))
```

**Directive Action**: Use `enumerate()` with comprehension or map.

---

### Edge Case 3: Nested Loops

**Issue**: Nested loops for cartesian product or nested iteration

**Handling**:
```python
# Imperative nested loops
def cartesian_product(list1: list[int], list2: list[int]) -> list[tuple]:
    result = []
    for x in list1:
        for y in list2:
            result.append((x, y))
    return result

# Functional with nested comprehension
def cartesian_product_functional(list1: list[int], list2: list[int]) -> list[tuple]:
    """Cartesian product using comprehension."""
    return [(x, y) for x in list1 for y in list2]

# Or with itertools.product
from itertools import product

def cartesian_product_v2(list1: list[int], list2: list[int]) -> list[tuple]:
    """Cartesian product using itertools."""
    return list(product(list1, list2))
```

**Directive Action**: Use nested comprehensions or `itertools` for nested operations.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Map/filter/reduce functions must be pure
  - `fp_immutability` - Operations return new collections, don't mutate
- **Triggers**:
  - `fp_lazy_evaluation` - Lazy versions of list operations
  - `fp_map_reduce` - Specialized reduce operations
  - `fp_data_filtering` - Advanced filtering patterns
- **Called By**:
  - `project_file_write` - Validate functional patterns
  - `project_compliance_check` - Detect imperative loops
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `coding_style = 'functional'` for functions using list operations
- **`functions`**: Updates `loop_count = 0` when imperative loops eliminated

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

1. **Imperative loop** → Directive converts to functional
   ```python
   # Input
   result = []
   for x in items: result.append(x*2)

   # Output
   result = [x*2 for x in items]
   ```

2. **Functional list ops** → Directive marks compliant
   ```python
   result = list(map(lambda x: x*2, items))
   # ✅ Already functional
   ```

3. **Check database** → Verify functional style marked
   ```sql
   SELECT name, coding_style, loop_count
   FROM functions
   WHERE coding_style = 'functional';
   ```

---

## Common Mistakes

- ❌ **Using imperative loops instead of map/filter** - Verbose, not composable
- ❌ **Mixing imperative and functional styles** - Inconsistent, confusing
- ❌ **Not using comprehensions** - More Pythonic than map/filter for simple cases
- ❌ **Forgetting lazy evaluation** - Use generators for large datasets
- ❌ **Over-nesting comprehensions** - Extract to separate functions for readability

---

## Roadblocks and Resolutions

### Roadblock 1: transform_loop
**Issue**: Imperative loop transforming each element
**Resolution**: Convert to map or list comprehension

### Roadblock 2: filter_loop
**Issue**: Imperative loop selecting elements
**Resolution**: Convert to filter or filtered comprehension

### Roadblock 3: aggregate_loop
**Issue**: Imperative loop combining elements
**Resolution**: Convert to reduce or use built-in aggregation (sum, max, etc.)

### Roadblock 4: complex_loop
**Issue**: Loop with complex logic (multiple operations, side effects)
**Resolution**: Break into multiple functional operations or keep imperative with documentation

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for functional list transformations*
