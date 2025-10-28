# fp_concurrency_safety

## Purpose

The `fp_concurrency_safety` directive ensures thread safety in concurrent functional programming operations by analyzing parallel execution patterns to prevent race conditions, deadlocks, and shared mutable state. It validates that functions running concurrently are independent, side-effect-free, and operate on immutable data, maintaining functional purity across parallel workflows while enabling safe concurrent execution.

**Category**: Concurrency
**Type**: FP Core
**Priority**: Critical
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`analyze_parallel_flows`**: Examine concurrent execution patterns, parallel operations, and data sharing between tasks.

### Branches

1. **`shared_state`** → **`apply_lock_or_copy`**
   - **Condition**: Detects shared mutable state between concurrent tasks
   - **Action**: Either duplicate data for each task or apply synchronization
   - **Details**: Prefer immutable copies over locks for functional purity
   - **Output**: Isolated task data or synchronized access

2. **`immutable_flows`** → **`approve_concurrency`**
   - **Condition**: All concurrent tasks operate on immutable data
   - **Action**: Mark as concurrency-safe and approve parallel execution
   - **Output**: Concurrency safety confirmation

3. **`race_condition_detected`** → **`isolate_critical_section`**
   - **Condition**: Potential race condition in resource access
   - **Action**: Isolate critical section with explicit synchronization
   - **Details**: Use message passing or actor model if possible
   - **Output**: Race-free concurrent code

4. **`pure_parallel_map`** → **`optimize_for_parallelism`**
   - **Condition**: Pure map/filter/reduce operations on collections
   - **Action**: Enable parallel execution optimizations
   - **Details**: No synchronization needed for pure operations
   - **Output**: Optimized parallel code

5. **Fallback** → **`prompt_user`**
   - **Condition**: Concurrency safety unclear
   - **Action**: Request clarification on concurrent access patterns

### Error Handling
- **On failure**: Prompt user with concurrency analysis details
- **Low confidence** (< 0.7): Request review before enabling parallelism

---

## Refactoring Strategies

### Strategy 1: Immutable Data Isolation
Ensure each concurrent task operates on independent immutable data.

**Before (Python - Non-Compliant)**:
```python
import threading

# Shared mutable state (dangerous!)
results = []
lock = threading.Lock()

def process_item(item):
    # Race condition on shared list
    with lock:
        results.append(item * 2)

threads = [threading.Thread(target=process_item, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

**After (Python - Compliant)**:
```python
from concurrent.futures import ThreadPoolExecutor
from typing import Sequence

def process_item(item: int) -> int:
    """Pure function: no shared state."""
    return item * 2

def process_items_parallel(items: Sequence[int]) -> list[int]:
    """Concurrency-safe: pure function on immutable input."""
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_item, items))
    return results

# Usage: no shared mutable state
items = range(10)
results = process_items_parallel(items)
```

### Strategy 2: Message Passing Instead of Shared State
Use message queues for communication between concurrent tasks.

**Before (Python - Non-Compliant)**:
```python
import threading

shared_counter = 0
lock = threading.Lock()

def increment_counter():
    global shared_counter
    for _ in range(1000):
        with lock:
            shared_counter += 1  # Shared mutable state
```

**After (Python - Compliant)**:
```python
from queue import Queue
from threading import Thread
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class IncrementMessage:
    kind: Literal["increment"] = "increment"
    amount: int = 1

@dataclass(frozen=True)
class ResultMessage:
    kind: Literal["result"] = "result"
    value: int

def counter_actor(message_queue: Queue, result_queue: Queue):
    """Actor pattern: handles messages, maintains local state."""
    counter = 0
    while True:
        msg = message_queue.get()
        if isinstance(msg, IncrementMessage):
            counter += msg.amount
        elif msg is None:  # Sentinel to stop
            result_queue.put(ResultMessage(value=counter))
            break

def increment_via_messages(num_increments: int) -> int:
    """Concurrency-safe: no shared mutable state."""
    msg_queue = Queue()
    result_queue = Queue()

    # Start actor
    actor = Thread(target=counter_actor, args=(msg_queue, result_queue))
    actor.start()

    # Send messages (no shared state)
    for _ in range(num_increments):
        msg_queue.put(IncrementMessage(amount=1))

    # Signal completion
    msg_queue.put(None)
    actor.join()

    # Get result
    result = result_queue.get()
    return result.value
```

### Strategy 3: Parallel Map with Pure Functions
Leverage pure functions for safe parallelism.

**Before (JavaScript - Non-Compliant)**:
```javascript
// Shared mutable state in async operations
let total = 0;

async function processItems(items) {
  await Promise.all(items.map(async (item) => {
    const result = await expensiveCalculation(item);
    total += result;  // Race condition!
  }));
  return total;
}
```

**After (JavaScript - Compliant)**:
```javascript
// Pure functions, no shared state
async function processItem(item) {
  return await expensiveCalculation(item);
}

async function processItems(items) {
  // Parallel pure operations
  const results = await Promise.all(items.map(processItem));

  // Reduce after parallel work (pure operation)
  return results.reduce((sum, val) => sum + val, 0);
}
```

### Strategy 4: Rust Fearless Concurrency
Leverage Rust's ownership system for compile-time concurrency safety.

**Before (Rust - Potential Data Race)**:
```rust
use std::thread;
use std::sync::Arc;
use std::sync::Mutex;

fn unsafe_parallel_sum(data: Vec<i32>) -> i32 {
    let sum = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for chunk in data.chunks(10) {
        let sum_clone = Arc::clone(&sum);
        let chunk_owned = chunk.to_vec();

        let handle = thread::spawn(move || {
            let chunk_sum: i32 = chunk_owned.iter().sum();
            let mut total = sum_clone.lock().unwrap();
            *total += chunk_sum;  // Lock contention
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    *sum.lock().unwrap()
}
```

**After (Rust - Compliant)**:
```rust
use std::thread;

fn parallel_sum_pure(data: Vec<i32>) -> i32 {
    let chunk_size = data.len() / 4;
    let mut handles = vec![];

    // Split data into chunks (ownership transfer)
    let chunks: Vec<Vec<i32>> = data
        .chunks(chunk_size.max(1))
        .map(|chunk| chunk.to_vec())
        .collect();

    // Process each chunk independently (no shared state)
    for chunk in chunks {
        let handle = thread::spawn(move || {
            chunk.iter().sum::<i32>()  // Pure computation
        });
        handles.push(handle);
    }

    // Collect results (pure reduction)
    handles.into_iter()
        .map(|h| h.join().unwrap())
        .sum()
}
```

### Strategy 5: TypeScript Async/Await Safety
Ensure async operations don't share mutable state.

**Before (TypeScript - Non-Compliant)**:
```typescript
class DataProcessor {
  private cache: Map<string, any> = new Map();  // Shared mutable state

  async processItems(items: string[]): Promise<void> {
    // Race condition: parallel access to shared cache
    await Promise.all(items.map(async (item) => {
      const result = await fetchData(item);
      this.cache.set(item, result);  // Race condition!
    }));
  }
}
```

**After (TypeScript - Compliant)**:
```typescript
interface CacheEntry {
  readonly key: string;
  readonly value: any;
}

// Pure function: no shared state
async function fetchAndPair(item: string): Promise<CacheEntry> {
  const value = await fetchData(item);
  return { key: item, value };
}

async function processItems(items: string[]): Promise<Map<string, any>> {
  // Parallel pure operations
  const entries = await Promise.all(items.map(fetchAndPair));

  // Build result after parallel work (no race)
  return new Map(entries.map(e => [e.key, e.value]));
}
```

---

## Examples

### Example 1: Parallel Data Transformation

**Compliant (Python)**:
```python
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, Sequence, TypeVar

T = TypeVar('T')
U = TypeVar('U')

def parallel_map(
    fn: Callable[[T], U],
    items: Sequence[T],
    max_workers: int = 4
) -> list[U]:
    """
    Concurrency-safe parallel map with pure function.
    Safe because: fn must be pure, items immutable, no shared state.
    """
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fn, items))

# Usage with pure function
def expensive_transform(x: int) -> int:
    """Pure function: safe for parallelism."""
    return x ** 2 + 2 * x + 1

results = parallel_map(expensive_transform, range(1000))
```

### Example 2: Concurrent File Processing

**Compliant (Python)**:
```python
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class FileContent:
    path: str
    content: str
    line_count: int

def read_file_pure(filepath: Path) -> FileContent:
    """Pure effect: reads file independently, no shared state."""
    content = filepath.read_text()
    return FileContent(
        path=str(filepath),
        content=content,
        line_count=len(content.splitlines())
    )

def process_files_parallel(filepaths: list[Path]) -> list[FileContent]:
    """Concurrency-safe: each file read independently."""
    with ThreadPoolExecutor() as executor:
        return list(executor.map(read_file_pure, filepaths))
```

### Example 3: Async API Requests

**Compliant (TypeScript)**:
```typescript
interface User {
  readonly id: number;
  readonly name: string;
  readonly email: string;
}

// Pure async function: no shared state
async function fetchUser(userId: number): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}

// Concurrency-safe: independent async operations
async function fetchUsers(userIds: number[]): Promise<User[]> {
  return await Promise.all(userIds.map(fetchUser));
}

// Usage
const users = await fetchUsers([1, 2, 3, 4, 5]);
```

---

## Edge Cases

### Edge Case 1: Nested Parallelism
**Scenario**: Parallel operations spawn more parallel operations
**Issue**: Resource exhaustion, complex synchronization needs
**Handling**:
- Limit parallelism depth with explicit thread pool sizing
- Use work-stealing schedulers
- Flatten nested parallel operations where possible

**Example**:
```python
from concurrent.futures import ThreadPoolExecutor

def controlled_nested_parallelism(data: list[list[int]]) -> list[int]:
    """Control parallelism depth to avoid resource exhaustion."""
    def process_group(group: list[int]) -> int:
        # Inner parallelism uses same pool (work stealing)
        return sum(x * 2 for x in group)

    # Outer parallelism with controlled workers
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(process_group, data))
```

### Edge Case 2: Deadlock Prevention
**Scenario**: Multiple concurrent tasks wait for each other's resources
**Issue**: Deadlock causing system hang
**Handling**:
- Avoid locks in functional code (use immutable data)
- If locks necessary, acquire in consistent order
- Use timeout mechanisms
- Prefer message passing over shared locks

### Edge Case 3: Memory Consistency
**Scenario**: Changes in one thread not visible to others
**Issue**: Stale data reads, inconsistent state
**Handling**:
- Use immutable data structures (no visibility issues)
- For mutable state, use proper synchronization primitives
- Document memory model guarantees

### Edge Case 4: Exception Handling in Parallel Tasks
**Scenario**: One parallel task throws exception
**Issue**: Other tasks may continue with inconsistent state
**Handling**:
- Use Result types instead of exceptions
- Collect all results/errors before processing
- Use supervisor patterns for fault tolerance

**Example**:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Success:
    value: int

@dataclass(frozen=True)
class Error:
    error: str

Result = Union[Success, Error]

def safe_process(item: int) -> Result:
    """Returns Result instead of throwing."""
    try:
        if item < 0:
            return Error(error="Negative value")
        return Success(value=item * 2)
    except Exception as e:
        return Error(error=str(e))

def parallel_with_error_handling(items: list[int]) -> list[Result]:
    """Collect all results, including errors."""
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(safe_process, item) for item in items]
        return [future.result() for future in as_completed(futures)]
```

### Edge Case 5: Non-Deterministic Execution Order
**Scenario**: Parallel task completion order unpredictable
**Issue**: Results depend on execution timing
**Handling**:
- Ensure operations are commutative/associative
- Collect results before final reduction
- Document non-determinism if unavoidable

---

## Database Operations

### Record Concurrency Safety Analysis

```sql
-- Mark function as concurrency-safe
UPDATE functions
SET
    is_concurrency_safe = 1,
    concurrency_metadata = '{
        "safe_for_parallelism": true,
        "shared_state": false,
        "synchronization_required": false,
        "parallel_strategy": "pure_parallel_map"
    }',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'process_items_parallel' AND file_id = ?;

-- Record concurrency refactoring
INSERT INTO notes (project_id, content, tags, created_at)
VALUES (
    1,
    'Refactored process_items to eliminate shared mutable state for concurrency safety',
    '["fp_concurrency_safety", "parallelism", "refactoring"]',
    CURRENT_TIMESTAMP
);
```

### Query Functions for Concurrency Analysis

```sql
-- Find functions using parallelism without safety verification
SELECT f.id, f.name, f.file_id, f.concurrency_metadata
FROM functions f
WHERE (f.uses_parallelism = 1 OR f.uses_async = 1)
  AND (f.is_concurrency_safe = 0 OR f.concurrency_metadata IS NULL)
ORDER BY f.call_count DESC;
```

---

## Related Directives

### FP Directives
- **fp_purity**: Ensures concurrent functions are pure and deterministic
- **fp_immutability**: Immutable data structures eliminate race conditions
- **fp_parallel_purity**: Validates parallel task independence
- **fp_task_isolation**: Prevents cross-task data leakage

### Project Directives
- **project_compliance_check**: Validates concurrency safety
- **project_update_db**: Records concurrency analysis results

---

## Helper Functions

### `detect_shared_mutable_state(concurrent_block) -> list[SharedState]`
Identifies shared mutable state between concurrent tasks.

**Signature**:
```python
def detect_shared_mutable_state(
    concurrent_block: ASTNode
) -> list[SharedState]:
    """
    Analyzes concurrent code for shared mutable variables.
    Returns list of shared state locations with access patterns.
    """
```

### `analyze_race_conditions(function_def) -> list[RaceCondition]`
Detects potential race conditions in concurrent access.

**Signature**:
```python
def analyze_race_conditions(
    function_def: FunctionDefinition
) -> list[RaceCondition]:
    """
    Identifies race conditions in concurrent code.
    Returns list of potential races with affected variables.
    """
```

### `suggest_synchronization_strategy(shared_access) -> SyncStrategy`
Recommends synchronization approach for shared access.

**Signature**:
```python
def suggest_synchronization_strategy(
    shared_access: SharedAccess
) -> SyncStrategy:
    """
    Suggests: immutable_copy, message_passing, lock,
    atomic_operation, or refactor_to_pure.
    Returns recommended strategy.
    """
```

---

## Testing

### Test 1: Detect Shared Mutable State
```python
def test_detect_shared_state():
    source = """
import threading

shared_list = []
lock = threading.Lock()

def append_item(item):
    with lock:
        shared_list.append(item)
"""

    issues = fp_concurrency_safety.analyze(source)

    assert len(issues) > 0
    assert any('shared_list' in issue.variable for issue in issues)
    assert any('mutable' in issue.issue_type for issue in issues)
```

### Test 2: Approve Pure Parallel Operations
```python
def test_approve_pure_parallelism():
    source = """
from concurrent.futures import ThreadPoolExecutor

def square(x):
    return x * x

def parallel_squares(items):
    with ThreadPoolExecutor() as executor:
        return list(executor.map(square, items))
"""

    result = fp_concurrency_safety.analyze(source)

    assert result.is_safe is True
    assert result.strategy == "pure_parallel_map"
```

### Test 3: Detect Race Condition
```python
def test_detect_race_condition():
    source = """
counter = 0

def increment():
    global counter
    temp = counter
    counter = temp + 1  # Race condition!
"""

    issues = fp_concurrency_safety.analyze(source)

    assert any('race condition' in issue.description.lower() for issue in issues)
```

---

## Common Mistakes

### Mistake 1: Shared Mutable State in Closures
**Problem**: Closures capture mutable variables shared between threads

**Solution**: Use immutable captures or pass data explicitly

```python
# ❌ Bad: Shared mutable closure
def create_workers(items):
    results = []  # Shared mutable!

    def worker(item):
        results.append(item * 2)  # Race condition

    threads = [threading.Thread(target=worker, args=(item,)) for item in items]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results

# ✅ Good: Immutable data, pure functions
def create_workers_safe(items):
    def worker(item):
        return item * 2  # Pure function

    with ThreadPoolExecutor() as executor:
        return list(executor.map(worker, items))
```

### Mistake 2: Async State Mutation
**Problem**: Async operations mutate shared state

**Solution**: Return new state instead of mutating

```typescript
// ❌ Bad: Async mutation
class Cache {
  private data: Map<string, any> = new Map();

  async loadAll(keys: string[]): Promise<void> {
    await Promise.all(keys.map(async (key) => {
      const value = await fetch(key);
      this.data.set(key, value);  // Race condition!
    }));
  }
}

// ✅ Good: Return new immutable state
async function loadAll(keys: string[]): Promise<Map<string, any>> {
  const entries = await Promise.all(
    keys.map(async (key) => {
      const value = await fetch(key);
      return [key, value] as const;
    })
  );
  return new Map(entries);
}
```

### Mistake 3: Lock-Based Synchronization in FP
**Problem**: Using locks instead of immutable data

**Solution**: Prefer immutability and message passing

```python
# ❌ Bad: Lock-based FP (contradiction)
lock = threading.Lock()
def synchronized_add(x, y):
    with lock:
        return x + y  # Pure operation doesn't need lock!

# ✅ Good: Pure function (no synchronization needed)
def add(x: int, y: int) -> int:
    return x + y  # Pure, naturally thread-safe
```

---

## Roadblocks

### Roadblock 1: Race Condition
**Issue**: Concurrent access to shared mutable data
**Resolution**: Duplicate data or enforce immutability, use message passing

### Roadblock 2: Shared State
**Issue**: Multiple tasks access same mutable state
**Resolution**: Use immutable data structures, actor model, or explicit synchronization

### Roadblock 3: Deadlock Risk
**Issue**: Circular lock dependencies detected
**Resolution**: Eliminate locks via immutability, or acquire locks in consistent order

### Roadblock 4: Performance Trade-off
**Issue**: Immutable copies too expensive for large data
**Resolution**: Use structural sharing, lazy evaluation, or document trade-off

---

## Integration Points

### With `fp_purity`
Concurrent operations must be pure to be safely parallelizable.

### With `fp_immutability`
Immutable data eliminates most concurrency issues.

### With `fp_parallel_purity`
Specialized validation for parallel pure operations.

### With `project_compliance_check`
Validates concurrency safety across codebase.

---

## Intent Keywords

- `thread safe`
- `parallel`
- `concurrent`
- `race condition`
- `synchronization`
- `async`

---

## Confidence Threshold

**0.7** - High confidence required due to subtle concurrency bugs.

---

## Notes

- Pure functions are naturally thread-safe (no shared mutable state)
- Immutable data structures eliminate race conditions
- Prefer message passing over shared memory
- Python GIL limits true parallelism (use multiprocessing for CPU-bound)
- JavaScript event loop is single-threaded (async ≠ parallel)
- Rust ownership system prevents data races at compile time
- Always prefer immutability over locks in functional code
- Test concurrent code under load to expose race conditions
- Use ThreadSanitizer or similar tools to detect data races
- Document thread safety guarantees in function metadata
