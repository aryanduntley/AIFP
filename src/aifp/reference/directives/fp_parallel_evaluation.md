# Directive: fp_parallel_evaluation

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: HIGH - Concurrency and performance

---

## Purpose

The `fp_parallel_evaluation` directive automatically executes independent pure expressions in parallel to improve throughput. This directive leverages **functional programming's safety guarantees** (purity, immutability) to enable fearless parallelization without locks, race conditions, or concurrency bugs.

Parallel evaluation provides **automatic concurrency benefits**, enabling:
- **Improved Throughput**: Execute independent operations concurrently
- **CPU Utilization**: Use multiple cores effectively
- **Reduced Latency**: Complete operations faster
- **Safe Parallelism**: Pure functions guarantee thread safety
- **No Manual Synchronization**: No locks, mutexes, or semaphores needed

This directive is **uniquely powerful in FP** - purity and immutability mean parallel execution is always safe. Imperative code requires complex synchronization; FP code parallelizes trivially.

---

## When to Apply

This directive applies when:
- **Independent pure computations** - Multiple operations that don't depend on each other
- **Data parallelism** - Apply same operation to many items (map over collection)
- **Pipeline parallelism** - Concurrent stages in data pipeline
- **Expensive operations** - Long-running computations benefit from parallelism
- **Multi-core utilization** - Maximize CPU usage
- **Called by project directives**:
  - `project_file_write` - Suggest parallelization opportunities
  - Works with `fp_purity` - Only parallelize pure functions
  - Works with `fp_lazy_evaluation` - Combine lazy + parallel for optimal performance

---

## Workflow

### Trunk: detect_independent_expressions

Scans code to identify independent pure expressions that can be parallelized.

**Steps**:
1. **Parse function body** - Build dependency graph
2. **Identify pure computations** - Only pure functions can be parallelized safely
3. **Analyze dependencies** - Find operations with no data dependencies
4. **Estimate cost** - Parallelization overhead only worth it for expensive operations
5. **Check data parallelism** - Map operations over collections
6. **Evaluate parallelization benefit** - Classify as parallelize, keep-sequential, or uncertain

### Branches

**Branch 1: If independent_pure_operations**
- **Then**: `parallelize_operations`
- **Details**: Run independent operations concurrently
  - Multiple computations that don't depend on each other
  - Use thread pool or async/await
  - Wait for all to complete
  - Return combined results
- **Result**: Returns parallel execution code

**Branch 2: If data_parallel_map**
- **Then**: `parallelize_map_operation`
- **Details**: Parallel map over collection
  - `map(f, items)` → `parallel_map(f, items)`
  - Each item processed independently
  - Use thread pool or multiprocessing
  - Combine results in order
- **Result**: Returns parallel map code

**Branch 3: If pipeline_stages_independent**
- **Then**: `parallelize_pipeline`
- **Details**: Concurrent pipeline stages
  - Producer-consumer pattern
  - Each stage runs concurrently
  - Data flows through pipeline
  - Overlap computation and I/O
- **Result**: Returns parallel pipeline code

**Branch 4: If sequential_required**
- **Then**: `keep_sequential`
- **Details**: Operations must execute sequentially
  - Data dependencies between operations
  - Order matters
  - Not safe to parallelize
- **Result**: Keep sequential execution

**Branch 5: If overhead_not_worth_it**
- **Then**: `keep_sequential_for_performance`
- **Details**: Parallelization overhead > benefit
  - Operations too cheap (< 1ms)
  - Collection too small (< 1000 items)
  - Thread creation cost not justified
- **Result**: Keep sequential for better performance

**Fallback**: `prompt_user`
- **Details**: Uncertain about parallelization
  - Possible dependencies
  - Cost-benefit unclear
  - Ask user for guidance
- **Result**: User decides

---

## Examples

### ✅ Compliant Code

**Parallel Independent Operations (Passes):**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_user_data(user_id: int) -> dict:
    """
    Process user data with parallel independent operations.

    Three expensive operations run concurrently.
    """
    # Three independent pure computations (expensive)
    def fetch_profile(uid: int) -> dict:
        """Pure: fetch and parse profile data."""
        data = expensive_profile_fetch(uid)
        return parse_profile(data)

    def fetch_orders(uid: int) -> list:
        """Pure: fetch and process order history."""
        data = expensive_orders_fetch(uid)
        return process_orders(data)

    def fetch_preferences(uid: int) -> dict:
        """Pure: fetch and parse preferences."""
        data = expensive_prefs_fetch(uid)
        return parse_preferences(data)

    # Sequential (slow):
    # profile = fetch_profile(user_id)  # 2 seconds
    # orders = fetch_orders(user_id)    # 3 seconds
    # prefs = fetch_preferences(user_id)  # 1 second
    # Total: 6 seconds

    # Parallel (fast):
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all three operations concurrently
        future_profile = executor.submit(fetch_profile, user_id)
        future_orders = executor.submit(fetch_orders, user_id)
        future_prefs = executor.submit(fetch_preferences, user_id)

        # Wait for all to complete
        profile = future_profile.result()  # 2 seconds
        orders = future_orders.result()    # 3 seconds (overlaps)
        prefs = future_prefs.result()      # 1 second (overlaps)
        # Total: 3 seconds (max of three, not sum)

    return {
        'profile': profile,
        'orders': orders,
        'preferences': prefs
    }

# 2x speedup from parallelization!
```

**Why Compliant**:
- Three independent pure operations
- No data dependencies
- Run concurrently
- Safe (pure functions)
- Significant speedup

---

**Parallel Map (Passes):**
```python
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable

def parallel_map(f: Callable, items: Iterable, max_workers: int = 4):
    """
    Parallel map operation.

    Apply pure function f to all items concurrently.
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(f, items))

def expensive_transformation(x: int) -> int:
    """
    Expensive pure transformation.

    Takes 100ms per item.
    """
    # Simulate expensive computation
    import time
    time.sleep(0.1)
    return x ** 2 + x + 1

# Sequential (slow):
# items = range(100)
# results = [expensive_transformation(x) for x in items]
# Total: 100 items * 100ms = 10 seconds

# Parallel (fast):
items = range(100)
results = parallel_map(expensive_transformation, items, max_workers=10)
# Total: 100 items / 10 workers * 100ms = 1 second
# 10x speedup!

# Safe because expensive_transformation is pure
```

**Why Compliant**:
- Data parallelism (map operation)
- Pure function (safe to parallelize)
- Significant speedup
- No synchronization needed

---

**Parallel Pipeline (Passes):**
```python
from queue import Queue
from threading import Thread

def parallel_pipeline(data_stream):
    """
    Parallel pipeline with concurrent stages.

    Stage 1 → Stage 2 → Stage 3 (all running concurrently)
    """
    # Queues for inter-stage communication
    stage1_to_stage2 = Queue(maxsize=10)
    stage2_to_stage3 = Queue(maxsize=10)
    results = []

    def stage1_worker():
        """Stage 1: Expensive parsing (pure)."""
        for item in data_stream:
            parsed = expensive_parse(item)  # 100ms
            stage1_to_stage2.put(parsed)
        stage1_to_stage2.put(None)  # Sentinel

    def stage2_worker():
        """Stage 2: Expensive validation (pure)."""
        while True:
            item = stage1_to_stage2.get()
            if item is None:
                stage2_to_stage3.put(None)
                break
            validated = expensive_validate(item)  # 100ms
            stage2_to_stage3.put(validated)

    def stage3_worker():
        """Stage 3: Expensive transformation (pure)."""
        while True:
            item = stage2_to_stage3.get()
            if item is None:
                break
            transformed = expensive_transform(item)  # 100ms
            results.append(transformed)

    # Start all stages concurrently
    t1 = Thread(target=stage1_worker)
    t2 = Thread(target=stage2_worker)
    t3 = Thread(target=stage3_worker)

    t1.start()
    t2.start()
    t3.start()

    # Wait for completion
    t1.join()
    t2.join()
    t3.join()

    return results

# Sequential: 100 items * (100ms + 100ms + 100ms) = 30 seconds
# Parallel pipeline: ~10 seconds (stages overlap)
# 3x speedup from pipeline parallelism!
```

**Why Compliant**:
- Pipeline parallelism
- Stages run concurrently
- Pure functions (safe)
- Significant throughput improvement

---

### ❌ Non-Compliant Code

**Parallelizing Impure Function (Violation):**
```python
# ❌ VIOLATION: Parallelizing impure function (race condition!)
from concurrent.futures import ThreadPoolExecutor

counter = 0  # ← Shared mutable state

def increment_counter(x: int) -> int:
    """
    Impure function (modifies global state).

    ❌ NOT SAFE TO PARALLELIZE
    """
    global counter
    counter += x  # ← RACE CONDITION when parallel!
    return counter

# Problem: Parallel execution with race condition
items = [1, 2, 3, 4, 5]
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(increment_counter, items))

# Expected: counter = 15 (1+2+3+4+5)
# Actual: counter = ??? (race condition, unpredictable)
# Results may be: [1, 3, 6, 7, 8] or [2, 2, 5, 9, 14] or any random order!
```

**Why Non-Compliant**:
- Impure function (modifies global state)
- Race condition on counter
- Unpredictable results
- NOT SAFE to parallelize

**Resolution**: Make function pure:
```python
# ✅ FIXED: Pure function (safe to parallelize)
def transform(x: int) -> int:
    """Pure transformation (no shared state)."""
    return x * 2

items = [1, 2, 3, 4, 5]
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(transform, items))
# Results: [2, 4, 6, 8, 10] (always correct, safe)
```

---

**Parallelizing with Data Dependencies (Violation):**
```python
# ❌ VIOLATION: Parallelizing dependent operations
from concurrent.futures import ThreadPoolExecutor

def process_sequence(data: list[int]) -> list[int]:
    """
    Process with data dependencies.

    ❌ NOT SAFE TO PARALLELIZE (wrong results!)
    """
    def step1(x):
        return x + 10

    def step2(x):
        return step1(x) * 2  # ← Depends on step1

    def step3(x):
        return step2(x) - 5  # ← Depends on step2

    # Problem: Trying to parallelize dependent operations
    with ThreadPoolExecutor(max_workers=3) as executor:
        # All submitted at once (WRONG - dependencies ignored!)
        f1 = executor.submit(step1, data[0])
        f2 = executor.submit(step2, data[0])  # Needs step1 result!
        f3 = executor.submit(step3, data[0])  # Needs step2 result!

        # Results will be wrong (dependencies not respected)
        return [f1.result(), f2.result(), f3.result()]
```

**Why Non-Compliant**:
- Operations have data dependencies
- step2 depends on step1, step3 depends on step2
- Parallelizing breaks dependency chain
- Wrong results

**Resolution**: Keep sequential or pipeline:
```python
# ✅ FIXED: Sequential (respects dependencies)
def process_sequence(data: list[int]) -> list[int]:
    """Process with sequential dependencies."""
    def step1(x):
        return x + 10

    def step2(x):
        return x * 2

    def step3(x):
        return x - 5

    # Sequential: respects dependencies
    result1 = step1(data[0])
    result2 = step2(result1)  # Uses result1
    result3 = step3(result2)  # Uses result2

    return [result1, result2, result3]
```

---

**Parallelizing Cheap Operations (Anti-Pattern):**
```python
# ❌ ANTI-PATTERN: Parallelization overhead > benefit
from concurrent.futures import ThreadPoolExecutor

def cheap_operation(x: int) -> int:
    """Very cheap operation (1 microsecond)."""
    return x * 2

# Small collection + cheap operation = parallelization not worth it
items = [1, 2, 3, 4, 5]  # Only 5 items

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(cheap_operation, items))

# Thread creation/coordination overhead: ~1 millisecond per thread
# Actual computation: 5 * 1 microsecond = 5 microseconds
# Overhead >> computation time (1000x overhead!)
# SLOWER than sequential!
```

**Why Non-Compliant**:
- Operation too cheap (1 microsecond)
- Collection too small (5 items)
- Parallelization overhead dominates
- Slower than sequential execution

**Resolution**: Keep sequential for cheap operations:
```python
# ✅ FIXED: Sequential for cheap operations
def cheap_operation(x: int) -> int:
    """Very cheap operation."""
    return x * 2

items = [1, 2, 3, 4, 5]
results = [cheap_operation(x) for x in items]  # Sequential (faster)

# Rule of thumb:
# - Parallelize if operation > 10ms AND collection > 100 items
# - Otherwise: sequential is faster
```

---

## Edge Cases

### Edge Case 1: Ordering Requirements

**Issue**: Results must be in original order

**Handling**:
```python
# Parallel map preserves order
from concurrent.futures import ThreadPoolExecutor

def parallel_map_ordered(f, items):
    """Parallel map that preserves order."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        # executor.map preserves order (built-in)
        return list(executor.map(f, items))

# Results in same order as input (guaranteed)
```

**Directive Action**: Use executor.map() which preserves order automatically.

---

### Edge Case 2: Resource Limits

**Issue**: Too many parallel workers exhaust resources

**Handling**:
```python
# Limit parallelism to avoid resource exhaustion
import multiprocessing

def parallel_process(items, f):
    """Parallel processing with resource limits."""
    # Use CPU count as max workers (reasonable limit)
    max_workers = min(multiprocessing.cpu_count(), len(items))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(f, items))
```

**Directive Action**: Limit max_workers to CPU count or reasonable constant.

---

### Edge Case 3: I/O-Bound vs CPU-Bound

**Issue**: Different parallelism strategies for I/O vs CPU

**Handling**:
```python
# I/O-bound: Use ThreadPoolExecutor (threads)
from concurrent.futures import ThreadPoolExecutor

def parallel_io_bound(urls, fetch):
    """Parallel I/O operations (threads efficient)."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        return list(executor.map(fetch, urls))

# CPU-bound: Use ProcessPoolExecutor (processes, avoid GIL)
from concurrent.futures import ProcessPoolExecutor

def parallel_cpu_bound(items, compute):
    """Parallel CPU operations (processes for true parallelism)."""
    with ProcessPoolExecutor(max_workers=4) as executor:
        return list(executor.map(compute, items))
```

**Directive Action**: Threads for I/O, processes for CPU-bound operations.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Only parallelize pure functions (safety requirement)
  - `fp_immutability` - Immutable data enables safe parallelism
- **Triggers**:
  - May trigger `fp_cost_analysis` - Estimate if parallelization worth overhead
- **Called By**:
  - `project_file_write` - Suggest parallelization opportunities
- **Conflicts With**:
  - Cheap operations - Parallelization overhead not worth it
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `parallelization = 'parallel'` for parallelized functions
- **`functions`**: Sets `concurrency_safe = true` for pure functions
- **`notes`**: Logs parallelization with `note_type = 'optimization'`

---

## Testing

How to verify this directive is working:

1. **Independent pure operations** → Directive suggests parallelization
   ```python
   # Input
   a = expensive1()
   b = expensive2()
   c = expensive3()

   # Suggested: Parallel execution
   ```

2. **Dependent operations** → Directive keeps sequential
   ```python
   # Input
   a = op1()
   b = op2(a)  # Depends on a

   # Kept sequential (dependencies)
   ```

3. **Check database** → Verify parallelization marked
   ```sql
   SELECT name, parallelization, concurrency_safe
   FROM functions
   WHERE parallelization = 'parallel';
   ```

---

## Common Mistakes

- ❌ **Parallelizing impure functions** - Race conditions, unpredictable results
- ❌ **Ignoring data dependencies** - Wrong results when dependencies broken
- ❌ **Parallelizing cheap operations** - Overhead > benefit
- ❌ **No resource limits** - Thread/process exhaustion
- ❌ **Wrong executor type** - Threads for CPU-bound (GIL limits), processes for I/O (overhead)

---

## Roadblocks and Resolutions

### Roadblock 1: impure_function
**Issue**: Function has side effects, not safe to parallelize
**Resolution**: Make function pure first, then parallelize

### Roadblock 2: data_dependencies
**Issue**: Operations have dependencies, must execute in order
**Resolution**: Keep sequential or use pipeline parallelism

### Roadblock 3: overhead_dominates
**Issue**: Parallelization overhead > benefit for cheap operations
**Resolution**: Keep sequential, mark as "not worth parallelizing"

### Roadblock 4: resource_limits
**Issue**: Too many parallel workers exhaust system resources
**Resolution**: Limit max_workers to CPU count or reasonable constant

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for safe automatic parallelization*
