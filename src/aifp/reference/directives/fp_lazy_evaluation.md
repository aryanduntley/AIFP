# Directive: fp_lazy_evaluation

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Performance optimization

---

## Purpose

The `fp_lazy_evaluation` directive transforms eager list processing into lazy evaluated sequences (streams, generators, iterators) where supported by the programming language. Lazy evaluation **defers computation until values are actually needed**, enabling efficient processing of large or infinite sequences without materializing entire collections in memory.

Lazy evaluation provides **performance and composability benefits**, enabling:
- **Memory Efficiency**: Process large datasets without loading all into memory
- **Infinite Sequences**: Define infinite data structures (computed on demand)
- **Composition**: Chain transformations without intermediate collections
- **Short-Circuiting**: Stop computation early when result found
- **Performance**: Avoid unnecessary computation for unused values

This directive complements `fp_lazy_computation` (lazy function evaluation) by focusing specifically on lazy data structure processing.

**Important**: This directive is reference documentation for lazy evaluation patterns.
AI consults this when uncertain about lazy sequences or complex stream processing scenarios.

**FP lazy evaluation is baseline behavior**:
- AI applies lazy evaluation naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about specific optimization or pattern decisions
- Complex scenarios requiring detailed guidance
- Edge cases with performance vs correctness tradeoffs
- Need for detailed guidance on implementation patterns

**Context**:
- AI applies this pattern as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives may reference this for guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: detect_eager_collections

Scans code to detect eager collection processing that could benefit from lazy evaluation.

**Steps**:
1. **Parse collection operations** - Find map, filter, reduce chains
2. **Identify eager materialization** - Collections built entirely before use
3. **Analyze data flow** - Trace how collections are consumed
4. **Identify early termination patterns** - take(N), find, any/all operations
5. **Evaluate lazy opportunity** - Classify as lazy-candidate, already-lazy, or eager-required
6. **Assess language support** - Check if language supports lazy sequences

### Branches

**Branch 1: If eager_collection_processing**
- **Then**: `convert_to_lazy_sequence`
- **Details**: Replace eager list with lazy stream/generator
  - Replace `[x*2 for x in items]` with `(x*2 for x in items)` (Python generator)
  - Replace `items.map(f).filter(g)` with `items.stream().map(f).filter(g)` (Java)
  - Replace array methods with lazy equivalents
  - Defer computation until iteration
- **Result**: Returns lazy sequence code

**Branch 2: If intermediate_collections**
- **Then**: `eliminate_intermediate_materialization`
- **Details**: Chain operations without creating intermediate lists
  - Replace `list1 = map(...); list2 = filter(list1)` with single lazy pipeline
  - Compose transformations without materializing
  - Single pass through data instead of multiple
- **Result**: Returns single-pass lazy pipeline

**Branch 3: If early_termination_possible**
- **Then**: `apply_lazy_short_circuit`
- **Details**: Use lazy evaluation to stop early
  - Replace `filter(pred, items)[0]` with `first(filter(pred, items))`
  - Replace `any([pred(x) for x in items])` with `any(pred(x) for x in items)`
  - Enable short-circuit evaluation for early exit
- **Result**: Returns short-circuiting lazy code

**Branch 4: If already_lazy**
- **Then**: `mark_compliant`
- **Details**: Code already uses lazy evaluation
  - Using generators, streams, or lazy sequences
  - No unnecessary materialization
  - Mark as compliant
- **Result**: Code passes lazy evaluation check

**Branch 5: If eager_required**
- **Then**: `document_rationale`
- **Details**: Eager evaluation required (e.g., need multiple passes, random access)
  - Document why lazy not applicable
  - No refactoring needed
- **Result**: Eager evaluation justified

**Fallback**: `prompt_user`
- **Details**: Uncertain about lazy conversion
  - Present findings to user
  - Ask: "Convert to lazy evaluation?"
  - Consider language limitations
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Lazy Generator (Python - Passes):**
```python
def process_large_file(filename: str):
    """
    Process large file lazily using generator.

    Memory efficient - only one line in memory at a time.
    """
    def read_lines():
        """Generator that yields lines one at a time."""
        with open(filename, 'r') as f:
            for line in f:
                yield line.strip()

    def parse_line(line: str) -> dict:
        """Parse line to dict."""
        parts = line.split(',')
        return {'name': parts[0], 'value': int(parts[1])}

    def is_valid(record: dict) -> bool:
        """Check if record is valid."""
        return record['value'] > 0

    # Lazy pipeline - no intermediate lists
    lines = read_lines()
    parsed = (parse_line(line) for line in lines)
    valid = (record for record in parsed if is_valid(record))

    # Only compute when iterating
    for record in valid:
        process_record(record)
```

**Why Compliant**:
- Generator expressions (lazy)
- No intermediate lists materialized
- Memory efficient for large files
- Single pass through data

---

**Lazy Stream (Java - Passes):**
```java
import java.util.stream.Stream;
import java.util.List;

public class LazyProcessing {
    /**
     * Process user list lazily using Stream API.
     *
     * Lazy evaluation - transformations composed, executed on demand.
     */
    public static void processUsers(List<User> users) {
        users.stream()
            .filter(user -> user.isActive())      // Lazy filter
            .map(user -> user.getEmail())         // Lazy map
            .filter(email -> email.contains("@")) // Lazy filter
            .limit(10)                            // Short-circuit at 10
            .forEach(email -> sendEmail(email));  // Terminal operation triggers evaluation
    }

    /**
     * Find first matching user lazily.
     *
     * Stops at first match - doesn't process entire list.
     */
    public static Optional<User> findFirstAdmin(List<User> users) {
        return users.stream()
            .filter(user -> user.hasRole("admin"))
            .findFirst();  // Short-circuits on first match
    }
}
```

**Why Compliant**:
- Stream API (lazy by default)
- Transformations composed without intermediate collections
- Short-circuiting with limit() and findFirst()
- Only computes what's needed

---

**Infinite Sequence (Haskell - Passes):**
```haskell
-- Lazy evaluation enables infinite lists
fibonacci :: [Integer]
fibonacci = 0 : 1 : zipWith (+) fibonacci (tail fibonacci)

-- Take first 10 Fibonacci numbers (lazy - only computes 10)
firstTenFib :: [Integer]
firstTenFib = take 10 fibonacci

-- Find first Fibonacci number > 1000 (lazy - stops when found)
firstFibOver1000 :: Integer
firstFibOver1000 = head $ filter (> 1000) fibonacci
```

**Why Compliant**:
- Infinite list defined (lazy evaluation required)
- Only computes values actually requested
- Short-circuits with head and take
- Composable transformations

---

### ❌ Non-Compliant Code

**Eager List Comprehension (Violation):**
```python
# ❌ VIOLATION: Eager list materialization
def process_large_dataset(items: list[int]) -> list[int]:
    # Step 1: Materialize entire list in memory
    doubled = [x * 2 for x in items]  # ← Eager: 100M items * 2 = 200M in memory

    # Step 2: Materialize another entire list
    filtered = [x for x in doubled if x > 100]  # ← Eager: Another copy

    # Step 3: Materialize third list
    squared = [x ** 2 for x in filtered]  # ← Eager: Third copy

    return squared[:10]  # Only need first 10, but computed all!
```

**Why Non-Compliant**:
- Three intermediate lists materialized
- Computes entire dataset even though only first 10 needed
- Memory inefficient (3 full copies)
- Performance waste for large datasets

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Lazy generator pipeline
def process_large_dataset(items: list[int]):
    """
    Process dataset lazily using generators.

    Memory efficient - no intermediate lists.
    """
    # Lazy pipeline - no materialization
    doubled = (x * 2 for x in items)
    filtered = (x for x in doubled if x > 100)
    squared = (x ** 2 for x in filtered)

    # Only compute first 10 (short-circuit)
    result = []
    for i, value in enumerate(squared):
        if i >= 10:
            break
        result.append(value)

    return result

# Or more concisely with itertools
from itertools import islice

def process_large_dataset_concise(items: list[int]):
    """Lazy processing with islice."""
    doubled = (x * 2 for x in items)
    filtered = (x for x in doubled if x > 100)
    squared = (x ** 2 for x in filtered)

    return list(islice(squared, 10))  # Only compute first 10
```

---

**Eager Any/All (Violation):**
```python
# ❌ VIOLATION: Builds entire list before checking
def has_valid_user(users: list[User]) -> bool:
    # Builds entire list of booleans in memory
    validations = [user.is_valid() for user in users]  # ← Eager

    # Then checks if any true
    return any(validations)  # Could have stopped at first True!
```

**Why Non-Compliant**:
- Materializes full list of validations
- Doesn't short-circuit on first True
- Wastes computation on all users even after finding valid one
- Memory inefficient

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Lazy generator with short-circuit
def has_valid_user(users: list[User]) -> bool:
    """
    Check if any user is valid using lazy evaluation.

    Short-circuits on first valid user found.
    """
    # Lazy generator - computes on demand
    validations = (user.is_valid() for user in users)

    # any() short-circuits on first True
    return any(validations)  # Stops at first valid user
```

---

**Eager Chaining (Java - Violation):**
```java
// ❌ VIOLATION: Materializing intermediate collections
public List<String> processUserEmails(List<User> users) {
    // Step 1: Collect to intermediate list
    List<User> activeUsers = users.stream()
        .filter(user -> user.isActive())
        .collect(Collectors.toList());  // ← Eager materialization

    // Step 2: Another intermediate list
    List<String> emails = activeUsers.stream()
        .map(user -> user.getEmail())
        .collect(Collectors.toList());  // ← Eager materialization

    // Step 3: Third materialization
    List<String> validEmails = emails.stream()
        .filter(email -> email.contains("@"))
        .collect(Collectors.toList());  // ← Eager materialization

    return validEmails;
}
```

**Why Non-Compliant**:
- Multiple intermediate collections created
- Three separate stream pipelines instead of one
- Unnecessary materialization at each step
- Memory and performance waste

**Refactored (Compliant):**
```java
// ✅ REFACTORED: Single lazy stream pipeline
public List<String> processUserEmails(List<User> users) {
    /**
     * Process user emails in single lazy pipeline.
     *
     * No intermediate collections - computes in one pass.
     */
    return users.stream()
        .filter(user -> user.isActive())         // Lazy
        .map(user -> user.getEmail())            // Lazy
        .filter(email -> email.contains("@"))    // Lazy
        .collect(Collectors.toList());           // Single materialization at end
}
```

---

## Edge Cases

### Edge Case 1: Multiple Passes Required

**Issue**: Need to iterate over data multiple times (lazy won't work)

**Handling**:
```python
# When multiple passes needed, eager may be required
def calculate_statistics(values: list[float]) -> dict:
    """
    Calculate statistics requiring multiple passes.

    Materialize once, then multiple passes.
    """
    # Materialize lazy sequence once if input is lazy
    values_list = list(values) if not isinstance(values, list) else values

    # Multiple passes on materialized list
    mean = sum(values_list) / len(values_list)
    variance = sum((x - mean) ** 2 for x in values_list) / len(values_list)

    return {'mean': mean, 'variance': variance}
```

**Directive Action**: Materialize once when multiple passes required, document rationale.

---

### Edge Case 2: Random Access Required

**Issue**: Need random access to elements (lazy sequences don't support indexing)

**Handling**:
```python
# Lazy sequences don't support random access
def get_nth_and_first(items):
    # ❌ Bad: Can't index lazy sequence
    # lazy_items = (x*2 for x in items)
    # return lazy_items[0], lazy_items[10]  # Error!

    # ✅ Good: Materialize if random access needed
    materialized = list(x*2 for x in items)
    return materialized[0], materialized[10]

# ✅ Alternative: Use itertools for specific operations
from itertools import islice

def get_first_and_eleventh(items):
    """Get specific elements from lazy sequence."""
    lazy_items = (x*2 for x in items)

    # Get first
    first = next(lazy_items)

    # Get 11th (skip 9, take 1)
    eleventh = next(islice(lazy_items, 9, 10))

    return first, eleventh
```

**Directive Action**: Materialize when random access required, or use specialized lazy operations.

---

### Edge Case 3: Side Effects in Lazy Operations

**Issue**: Side effects in lazy pipeline may not execute as expected

**Handling**:
```python
# ❌ Bad: Side effects in lazy pipeline (may not execute)
def process_with_logging(items: list[int]):
    def log_and_double(x):
        print(f"Processing {x}")  # Side effect
        return x * 2

    # Lazy - side effects only happen when consumed!
    lazy_result = (log_and_double(x) for x in items)

    # If never consumed, logging never happens
    # ...

# ✅ Good: Eager for side effects, or explicit consumption
def process_with_logging_correct(items: list[int]):
    def log_and_double(x):
        print(f"Processing {x}")  # Side effect
        return x * 2

    # Materialize immediately if side effects are important
    result = [log_and_double(x) for x in items]

    return result

# ✅ Alternative: Isolate side effects from lazy computation
def process_with_separate_logging(items: list[int]):
    """Separate pure computation from side effects."""
    # Pure lazy computation
    lazy_result = (x * 2 for x in items)

    # Consume and log explicitly
    for value in lazy_result:
        print(f"Result: {value}")  # Side effect at consumption point
```

**Directive Action**: Eager evaluation for side effects, or explicitly consume lazy sequence.

---

### Edge Case 4: Debugging Lazy Code

**Issue**: Lazy evaluation makes debugging harder (values not computed until consumed)

**Handling**:
```python
# Debugging lazy pipelines
def debug_lazy_pipeline(items: list[int]):
    """
    Debug lazy pipeline by materializing stages.

    Temporarily materialize for debugging, then restore laziness.
    """
    # DEBUGGING: Materialize intermediate stages
    doubled = list(x * 2 for x in items)
    print(f"Doubled: {doubled[:5]}")  # Inspect first 5

    filtered = list(x for x in doubled if x > 100)
    print(f"Filtered: {filtered[:5]}")  # Inspect first 5

    # PRODUCTION: Restore lazy evaluation
    # doubled = (x * 2 for x in items)
    # filtered = (x for x in doubled if x > 100)

    return filtered

# Alternative: Use logging at consumption point
def debug_with_tap(items: list[int]):
    """Debug by tapping into lazy stream."""
    def tap(label, value):
        """Side effect for debugging."""
        print(f"{label}: {value}")
        return value

    lazy_result = (tap("Doubled", x * 2) for x in items)
    filtered = (x for x in lazy_result if x > 100)

    return list(filtered)  # Logging happens during materialization
```

**Directive Action**: Temporarily materialize for debugging, use tap functions for inspection.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Lazy operations must be pure (no side effects)
  - `fp_immutability` - Lazy sequences require immutable data
- **Triggers**:
  - `fp_list_operations` - Lazy versions of map/filter/reduce
  - `fp_lazy_computation` - Lazy function evaluation (broader concept)
- **Called By**:
  - `project_file_write` - Validates lazy evaluation patterns
  - `project_compliance_check` - Scans for eager materialization
- **Escalates To**:
  - `fp_language_standardization` - For language-specific lazy constructs

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---


## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `evaluation_strategy = 'lazy'` for lazy functions
- **`functions`**: Updates `memory_efficiency = 'stream'` for streaming operations

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

1. **Write eager collection processing** → Directive suggests lazy alternative
   ```python
   # Input (eager)
   result = [x*2 for x in items][:10]

   # Suggested output (lazy)
   result = list(islice((x*2 for x in items), 10))
   ```

2. **Write lazy generator** → Directive marks compliant
   ```python
   result = (x*2 for x in items)
   # ✅ Already lazy
   ```

3. **Check database** → Verify `functions.evaluation_strategy = 'lazy'`
   ```sql
   SELECT name, evaluation_strategy, memory_efficiency
   FROM functions
   WHERE name = 'process_items';
   -- Expected: evaluation_strategy='lazy', memory_efficiency='stream'
   ```

---

## Common Mistakes

- ❌ **Materializing lazy sequences unintentionally** - list(generator) when not needed
- ❌ **Multiple iterations over lazy sequence** - Generator exhausts after first pass
- ❌ **Side effects in lazy operations** - May not execute until consumed
- ❌ **Lazy when random access needed** - Use eager for indexing/slicing
- ❌ **Forgetting to consume lazy sequence** - Work never done if not iterated

---

## Roadblocks and Resolutions

### Roadblock 1: eager_collection_processing
**Issue**: Eager list comprehension materializes entire collection
**Resolution**: Replace with generator expression for lazy evaluation

### Roadblock 2: intermediate_materialization
**Issue**: Multiple intermediate lists created in pipeline
**Resolution**: Chain operations lazily without materializing between steps

### Roadblock 3: language_lacks_lazy_support
**Issue**: Programming language doesn't have built-in lazy sequences
**Resolution**: Escalate to `fp_wrapper_generation` to implement lazy constructs

### Roadblock 4: multiple_passes_required
**Issue**: Algorithm needs multiple iterations over data
**Resolution**: Materialize once, document rationale, keep multiple passes

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for lazy sequence evaluation*
