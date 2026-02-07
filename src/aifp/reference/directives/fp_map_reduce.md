# Directive: fp_map_reduce

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: HIGH - Core aggregation pattern

---

## Purpose

The `fp_map_reduce` directive standardizes use of `reduce` (fold) for aggregations instead of mutable accumulators. This directive promotes **pure aggregation patterns** that eliminate shared mutable state, making code safer, more composable, and easier to reason about.

Map-reduce provides **functional aggregation**, enabling:
- **No Mutable Accumulators**: Replace imperative counters/sums with pure functions
- **Composability**: Reducer functions compose elegantly
- **Parallelizability**: Pure reducers can run in parallel (map-reduce paradigm)
- **Clear Intent**: Reducer function documents aggregation logic
- **Type Safety**: Explicit accumulator and element types

This directive is fundamental to functional data processing and is the basis of distributed computing frameworks (Hadoop, Spark).

**Important**: This directive is reference documentation for map/reduce patterns.
AI consults this when uncertain about converting imperative aggregations to functional reduce operations or complex fold scenarios.

**FP map/reduce is baseline behavior**:
- AI writes functional map/reduce operations naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about converting imperative aggregations to functional reduce
- Complex fold/reduce scenarios (left fold vs right fold, custom accumulators)
- Edge cases with stateful accumulators or nested reductions
- Need for detailed guidance on map/reduce composition patterns

**Context**:
- AI writes functional map/reduce operations as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_list_operations`, `fp_purity`, `fp_immutability`) may reference this for guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: scan_for_aggregations

Scans code to detect aggregation patterns that should use reduce instead of mutable accumulators.

**Steps**:
1. **Parse loop constructs** - Identify aggregation loops
2. **Detect accumulator patterns** - Variables that accumulate values
3. **Classify aggregation type** - Sum, product, concat, merge, custom
4. **Verify combiner purity** - Ensure combining function is pure
5. **Check for built-ins** - Use built-in (sum, max, etc.) when available
6. **Generate reduce equivalent** - Convert to reduce or built-in

### Branches

**Branch 1: If simple_sum**
- **Then**: `use_builtin_sum`
- **Details**: Simple summation pattern
  - Pattern: `acc = 0; for x in items: acc += x`
  - Convert to: `result = sum(items)`
  - Built-in is more efficient than reduce
- **Result**: Returns sum() call

**Branch 2: If simple_aggregation**
- **Then**: `use_builtin_function`
- **Details**: Simple aggregation with built-in
  - max, min, any, all, len, etc.
  - Use built-in instead of manual reduce
  - More readable and efficient
- **Result**: Returns built-in function call

**Branch 3: If custom_aggregation**
- **Then**: `convert_to_reduce`
- **Details**: Custom aggregation logic
  - Pattern: `acc = init; for x in items: acc = combine(acc, x)`
  - Convert to: `result = reduce(combine, items, init)`
  - Pure combining function
- **Result**: Returns reduce-based code

**Branch 4: If associative_operation**
- **Then**: `optimize_for_parallel`
- **Details**: Associative reducer can parallelize
  - Operation like `+`, `*`, `max`, `min` (associative)
  - Document potential for parallel execution
  - Enable parallel reduce if available
- **Result**: Returns parallel-ready reduce

**Branch 5: If already_using_reduce**
- **Then**: `mark_compliant`
- **Details**: Already using reduce or built-in
  - Functional aggregation
  - No mutable accumulator
  - Mark as compliant
- **Result**: Code passes check

**Fallback**: `prompt_user`
- **Details**: Complex aggregation pattern
  - Multiple accumulators
  - Conditional aggregation logic
  - Ask user for reduce strategy
- **Result**: User provides conversion guidance

---

## Examples

### ✅ Compliant Code

**Built-in Sum (Passes):**
```python
def calculate_total(prices: list[float]) -> float:
    """
    Calculate total of prices using built-in sum.

    Functional aggregation - no mutable accumulator.
    """
    return sum(prices)

# Simple, clear, functional
# Usage
total = calculate_total([10.50, 25.00, 15.75])
# Returns: 51.25
```

**Why Compliant**:
- Uses built-in sum (efficient)
- No mutable accumulator
- Clear and concise
- Functional style

---

**Custom Reduce (Passes):**
```python
from functools import reduce

def calculate_product(numbers: list[int]) -> int:
    """
    Calculate product using reduce.

    Functional aggregation with pure combiner.
    """
    return reduce(lambda acc, x: acc * x, numbers, 1)

# Pure combining function
# Usage
product = calculate_product([2, 3, 4, 5])
# Returns: 120
```

**Why Compliant**:
- Uses reduce for custom aggregation
- Pure combiner function
- No mutable state
- Functional style

---

**Complex Aggregation (Passes):**
```python
from functools import reduce

def merge_dictionaries(dicts: list[dict]) -> dict:
    """
    Merge list of dictionaries using reduce.

    Functional merge - no mutation of accumulators.
    """
    def merge_two(acc: dict, d: dict) -> dict:
        """Pure merge function (returns new dict)."""
        return {**acc, **d}  # Immutable merge

    return reduce(merge_two, dicts, {})

# Pure combining function
# Usage
result = merge_dictionaries([
    {'a': 1, 'b': 2},
    {'c': 3},
    {'b': 5, 'd': 4}
])
# Returns: {'a': 1, 'b': 5, 'c': 3, 'd': 4}
```

**Why Compliant**:
- Uses reduce for complex aggregation
- Pure merge function (immutable)
- No mutation
- Functional style

---

**Map-Reduce Pipeline (Passes):**
```python
from functools import reduce

def calculate_weighted_average(items: list[dict]) -> float:
    """
    Calculate weighted average using map-reduce.

    Map: Extract (value, weight) pairs
    Reduce: Combine into weighted sum
    """
    # Map: Extract values and weights
    pairs = [(item['value'], item['weight']) for item in items]

    # Reduce: Calculate weighted sum and total weight
    def combine(acc, pair):
        value, weight = pair
        return (acc[0] + value * weight, acc[1] + weight)

    weighted_sum, total_weight = reduce(combine, pairs, (0, 0))

    return weighted_sum / total_weight if total_weight > 0 else 0

# Pure map-reduce pipeline
# Usage
items = [
    {'value': 90, 'weight': 0.3},
    {'value': 80, 'weight': 0.5},
    {'value': 95, 'weight': 0.2}
]
avg = calculate_weighted_average(items)
# Returns: 85.5
```

**Why Compliant**:
- Map-reduce pattern
- Pure combining function
- No mutable accumulator
- Clear data flow

---

### ❌ Non-Compliant Code

**Mutable Sum Accumulator (Violation):**
```python
# ❌ VIOLATION: Mutable accumulator for sum
def calculate_total(prices: list[float]) -> float:
    """Calculate total using imperative loop."""
    total = 0  # ← Mutable accumulator
    for price in prices:  # ← Imperative loop
        total += price  # ← Mutation
    return total

# Problem:
# - Mutable accumulator
# - Imperative loop
# - Not composable
# - Should use sum() or reduce
```

**Why Non-Compliant**:
- Mutable accumulator (total)
- Imperative aggregation
- Should use built-in sum()

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Built-in sum
def calculate_total(prices: list[float]) -> float:
    """Calculate total using sum."""
    return sum(prices)

# Functional, concise, clear
```

---

**Mutable Dictionary Merge (Violation):**
```python
# ❌ VIOLATION: Mutating accumulator dictionary
def merge_dictionaries(dicts: list[dict]) -> dict:
    """Merge dictionaries using imperative loop."""
    result = {}  # ← Mutable accumulator
    for d in dicts:  # ← Imperative loop
        result.update(d)  # ← MUTATION!
    return result

# Problem:
# - Mutates result dictionary
# - Imperative pattern
# - Not functional
# - Should use reduce with immutable merge
```

**Why Non-Compliant**:
- Mutates accumulator (.update())
- Imperative aggregation
- Not functional

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Functional reduce with immutable merge
from functools import reduce

def merge_dictionaries(dicts: list[dict]) -> dict:
    """Merge dictionaries using reduce."""
    return reduce(lambda acc, d: {**acc, **d}, dicts, {})

# Functional, immutable, composable
```

---

**Multiple Mutable Accumulators (Violation):**
```python
# ❌ VIOLATION: Multiple mutable accumulators
def analyze_numbers(numbers: list[int]) -> dict:
    """Analyze numbers using imperative loops."""
    total = 0  # ← Mutable accumulator 1
    count = 0  # ← Mutable accumulator 2
    max_val = float('-inf')  # ← Mutable accumulator 3

    for num in numbers:  # ← Imperative loop
        total += num  # ← Mutation 1
        count += 1  # ← Mutation 2
        if num > max_val:  # ← Conditional mutation
            max_val = num  # ← Mutation 3

    return {
        'average': total / count if count > 0 else 0,
        'max': max_val
    }

# Problem:
# - Three mutable accumulators
# - Imperative aggregation
# - Not composable
# - Should use reduce or built-ins
```

**Why Non-Compliant**:
- Multiple mutable accumulators
- Imperative pattern
- Should use reduce or built-ins

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Functional with built-ins and reduce
from functools import reduce

def analyze_numbers(numbers: list[int]) -> dict:
    """Analyze numbers using functional aggregation."""
    if not numbers:
        return {'average': 0, 'max': float('-inf')}

    # Use built-ins where applicable
    total = sum(numbers)
    count = len(numbers)
    max_val = max(numbers)

    return {
        'average': total / count,
        'max': max_val
    }

# Or with single reduce for all stats
def analyze_numbers_v2(numbers: list[int]) -> dict:
    """Analyze numbers with single reduce."""
    def combine(acc, num):
        return {
            'total': acc['total'] + num,
            'count': acc['count'] + 1,
            'max': max(acc['max'], num)
        }

    init = {'total': 0, 'count': 0, 'max': float('-inf')}
    stats = reduce(combine, numbers, init)

    return {
        'average': stats['total'] / stats['count'] if stats['count'] > 0 else 0,
        'max': stats['max']
    }

# Functional, no mutations
```

---

## Edge Cases

### Edge Case 1: Empty Collections

**Issue**: Reduce on empty collection needs initial value

**Handling**:
```python
# Always provide initial value for reduce
from functools import reduce

# ❌ Bad: No initial value (error on empty list)
def product(numbers: list[int]) -> int:
    return reduce(lambda acc, x: acc * x, numbers)
    # Error on empty list!

# ✅ Good: With initial value
def product_safe(numbers: list[int]) -> int:
    """Calculate product with safe initial value."""
    return reduce(lambda acc, x: acc * x, numbers, 1)
    # Returns 1 for empty list (identity element)

# Usage
result = product_safe([])  # Returns: 1 (safe)
result = product_safe([2, 3, 4])  # Returns: 24
```

**Directive Action**: Always provide initial value to reduce for empty collection safety.

---

### Edge Case 2: Non-Associative Operations

**Issue**: Order matters for non-associative operations

**Handling**:
```python
# Division is non-associative
# (a / b) / c ≠ a / (b / c)

# Reduce respects left-to-right order
from functools import reduce

def divide_all(numbers: list[float]) -> float:
    """
    Divide all numbers left-to-right.

    Non-associative operation - order matters.
    """
    if not numbers:
        return 0
    return reduce(lambda acc, x: acc / x, numbers)

# (((a / b) / c) / d)  ← Left-to-right
# Usage
result = divide_all([100, 2, 5])
# Returns: 10.0  (((100 / 2) / 5) = 10)
```

**Directive Action**: Document when operation is non-associative (can't parallelize).

---

### Edge Case 3: Parallel Reduce

**Issue**: Associative operations can parallelize

**Handling**:
```python
# Associative operations support parallel reduce
from concurrent.futures import ThreadPoolExecutor
from functools import reduce

def parallel_reduce(items: list, combine, identity):
    """
    Parallel reduce for associative operations.

    Splits list into chunks, reduces each in parallel, combines results.
    """
    if len(items) <= 1000:
        # Too small for parallelism overhead
        return reduce(combine, items, identity)

    # Split into chunks
    chunk_size = len(items) // 4
    chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]

    # Reduce each chunk in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        chunk_results = list(executor.map(
            lambda chunk: reduce(combine, chunk, identity),
            chunks
        ))

    # Combine chunk results
    return reduce(combine, chunk_results, identity)

# Only works for associative operations!
# sum, product, max, min, or, and, etc.

# Usage
numbers = list(range(10000))
total = parallel_reduce(numbers, lambda acc, x: acc + x, 0)
# Parallel reduction for large datasets
```

**Directive Action**: Enable parallel reduce for associative operations.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Reducer functions must be pure
  - `fp_immutability` - Accumulators should be immutable
- **Triggers**:
  - `fp_parallel_evaluation` - Associative reducers can parallelize
  - `fp_list_operations` - Reduce is core list operation
- **Called By**:
  - `project_file_write` - Validate reduce usage
  - Works with `fp_lazy_evaluation` - Lazy reduce for large datasets
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `aggregation_style = 'reduce'` for functions using reduce
- **`functions`**: Sets `mutable_accumulators = 0` when eliminated

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

1. **Mutable accumulator** → Directive converts to reduce
   ```python
   # Input
   total = 0
   for x in items: total += x

   # Output
   total = sum(items)
   ```

2. **Using reduce** → Directive marks compliant
   ```python
   from functools import reduce
   total = reduce(lambda acc, x: acc + x, items, 0)
   # ✅ Functional
   ```

3. **Check database** → Verify reduce style marked
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Common Mistakes

- ❌ **No initial value for reduce** - Fails on empty collections
- ❌ **Using reduce for simple sum** - Use built-in sum() instead
- ❌ **Mutating accumulator in reducer** - Violates purity
- ❌ **Non-associative operations in parallel reduce** - Wrong results
- ❌ **Complex reduce logic** - Extract to named function for clarity

---

## Roadblocks and Resolutions

### Roadblock 1: mutable_accumulator
**Issue**: Loop uses mutable variable to accumulate values
**Resolution**: Convert to reduce with pure combining function

### Roadblock 2: simple_builtin_case
**Issue**: Aggregation has built-in (sum, max, etc.)
**Resolution**: Use built-in instead of reduce (more efficient and readable)

### Roadblock 3: multiple_accumulators
**Issue**: Loop maintains multiple mutable accumulators
**Resolution**: Use single reduce with tuple/dict accumulator, or multiple built-ins

### Roadblock 4: non_pure_combiner
**Issue**: Combining function has side effects
**Resolution**: Make combiner pure before converting to reduce

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for functional aggregation with reduce*
