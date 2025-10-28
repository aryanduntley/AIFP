# fp_parallel_purity

## Purpose

The `fp_parallel_purity` directive validates that functions running in parallel are independent, side-effect-free, and operate on immutable data to protect functional integrity in parallel operations. It ensures that parallel tasks don't share mutable state, have no race conditions, and maintain deterministic behavior regardless of execution order or timing. This enables safe, efficient parallelism in functional codebases.

**Category**: Concurrency
**Type**: FP Core
**Priority**: High
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`inspect_parallel_tasks`**: Analyze parallel execution patterns for purity violations and shared state.

### Branches

1. **`shared_resource_detected`** → **`copy_or_lock_resource`**
   - **Condition**: Multiple parallel tasks access same mutable resource
   - **Action**: Create immutable copies or apply synchronization
   - **Details**: Prefer immutable copies for functional purity
   - **Output**: Isolated data for each parallel task

2. **`independent_tasks`** → **`approve_parallelism`**
   - **Condition**: All parallel tasks operate independently on immutable data
   - **Action**: Mark as safe for parallel execution
   - **Output**: Parallelism safety confirmation

3. **`impure_task`** → **`isolate_or_refactor`**
   - **Condition**: Parallel task contains side effects
   - **Action**: Isolate side effects or refactor to pure function
   - **Details**: Extract side effects to sequential boundaries
   - **Output**: Pure parallel tasks

4. **`data_dependency`** → **`restructure_pipeline`**
   - **Condition**: Parallel tasks have data dependencies
   - **Action**: Restructure to sequential or staged pipeline
   - **Details**: Ensure dependencies resolved before parallel execution
   - **Output**: Correct execution ordering

5. **Fallback** → **`prompt_user`**
   - **Condition**: Parallel safety unclear
   - **Action**: Request user clarification on parallel safety

### Error Handling
- **On failure**: Prompt user with parallel purity analysis
- **Low confidence** (< 0.7): Request review before approving parallelism

---

## Refactoring Strategies

### Strategy 1: Pure Parallel Map
Ensure map operations on collections are pure and independent.

**Before (Python - Potentially Unsafe)**:
```python
# Shared mutable accumulator (dangerous!)
results = []

def process_item(item):
    result = expensive_computation(item)
    results.append(result)  # Race condition!
    return result

from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    executor.map(process_item, items)
```

**After (Python - Pure Parallel Map)**:
```python
from concurrent.futures import ThreadPoolExecutor
from typing import Sequence

def process_item(item: dict) -> dict:
    """Pure function: no shared state, deterministic."""
    return expensive_computation(item)

def parallel_map_pure(
    func,
    items: Sequence,
    max_workers: int = 4
) -> list:
    """Pure parallel map: no shared state."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(func, items))

# Usage: pure and safe
results = parallel_map_pure(process_item, items)
```

### Strategy 2: Immutable Data Distribution
Copy data for each parallel task instead of sharing.

**Before (Python - Shared Mutable Data)**:
```python
import threading

config = {"multiplier": 2}  # Shared mutable state

def worker(data):
    # Reads shared config (potential race if config mutated)
    return [x * config["multiplier"] for x in data]

threads = [
    threading.Thread(target=worker, args=(chunk,))
    for chunk in data_chunks
]
```

**After (Python - Immutable Data)**:
```python
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor

@dataclass(frozen=True)
class Config:
    """Immutable configuration."""
    multiplier: int

def worker(data: list[int], config: Config) -> list[int]:
    """Pure: operates on immutable data."""
    return [x * config.multiplier for x in data]

def parallel_process(
    data_chunks: list[list[int]],
    config: Config
) -> list[list[int]]:
    """Pure parallel processing with immutable config."""
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(worker, chunk, config)
            for chunk in data_chunks
        ]
        return [f.result() for f in futures]

# Usage
config = Config(multiplier=2)
results = parallel_process(data_chunks, config)
```

### Strategy 3: Pure Parallel Reduce
Ensure reduction operations are associative and commutative.

**Before (Python - Order-Dependent)**:
```python
# Non-associative operation (order matters!)
def combine(a, b):
    return a - b  # a - b ≠ b - a

from concurrent.futures import ThreadPoolExecutor

# WRONG: parallel reduce with non-associative operation
with ThreadPoolExecutor() as executor:
    result = reduce(combine, executor.map(process, items))
```

**After (Python - Associative Operation)**:
```python
from functools import reduce
from concurrent.futures import ThreadPoolExecutor

def combine(a: float, b: float) -> float:
    """Associative: a + b == b + a."""
    return a + b

def parallel_sum(items: list[int]) -> int:
    """Pure parallel reduction with associative operation."""
    # Map phase: parallel
    with ThreadPoolExecutor() as executor:
        processed = list(executor.map(lambda x: x * 2, items))

    # Reduce phase: associative operation safe for parallel
    return reduce(combine, processed, 0)
```

### Strategy 4: Staged Pipeline for Dependencies
Convert dependent parallel tasks to staged pipeline.

**Before (Python - Hidden Dependencies)**:
```python
from concurrent.futures import ThreadPoolExecutor

def task_a(data):
    # Modifies shared data (dependency!)
    shared_results['a'] = process_a(data)

def task_b(data):
    # Depends on task_a result
    return process_b(data, shared_results['a'])

# WRONG: parallel execution with dependency
with ThreadPoolExecutor() as executor:
    executor.submit(task_a, data1)
    executor.submit(task_b, data2)  # May run before task_a!
```

**After (Python - Staged Pipeline)**:
```python
from concurrent.futures import ProcessPoolExecutor

def task_a(data: dict) -> dict:
    """Pure: returns result instead of mutating shared state."""
    return process_a(data)

def task_b(data: dict, a_result: dict) -> dict:
    """Pure: explicit dependency as parameter."""
    return process_b(data, a_result)

def staged_pipeline(data1: dict, data2: dict) -> dict:
    """Sequential stages with parallel work within each stage."""
    # Stage 1: task_a (sequential, dependency)
    a_result = task_a(data1)

    # Stage 2: task_b depends on a_result (sequential)
    b_result = task_b(data2, a_result)

    return b_result

# Or parallel independent tasks
def parallel_independent(data_list: list) -> list:
    """Parallel execution of independent tasks."""
    with ProcessPoolExecutor() as executor:
        # All tasks independent: safe parallel
        return list(executor.map(task_a, data_list))
```

### Strategy 5: Result Collection Without Shared State
Collect parallel results without shared mutable structures.

**Before (JavaScript/TypeScript - Shared Array)**:
```typescript
const results: number[] = [];  // Shared mutable state

async function processItems(items: number[]) {
  await Promise.all(items.map(async (item) => {
    const result = await processItem(item);
    results.push(result);  // Race condition!
  }));

  return results;
}
```

**After (TypeScript - Immutable Collection)**:
```typescript
async function processItem(item: number): Promise<number> {
  // Pure async function
  return await expensiveCalculation(item);
}

async function processItems(items: number[]): Promise<number[]> {
  // Collect results without shared mutable state
  const promises = items.map(processItem);
  return await Promise.all(promises);  // Returns new array
}
```

---

## Examples

### Example 1: Parallel File Processing

**Pure Parallel**:
```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def process_file_content(content: str) -> dict:
    """Pure: transforms file content."""
    lines = content.split('\n')
    word_count = sum(len(line.split()) for line in lines)
    return {'lines': len(lines), 'words': word_count}

def read_and_process(filepath: Path) -> dict:
    """Reads file and processes (I/O isolated to this function)."""
    content = filepath.read_text()
    return process_file_content(content)

def process_files_parallel(filepaths: list[Path]) -> list[dict]:
    """Pure parallel file processing."""
    with ProcessPoolExecutor() as executor:
        return list(executor.map(read_and_process, filepaths))
```

### Example 2: Pure Async Operations

**Pure Async (TypeScript)**:
```typescript
interface User {
  readonly id: number;
  readonly name: string;
}

// Pure async function
async function fetchUser(userId: number): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}

// Pure parallel fetch
async function fetchUsers(userIds: number[]): Promise<User[]> {
  // All operations independent: safe parallel
  return await Promise.all(userIds.map(fetchUser));
}
```

### Example 3: Parallel Data Transformation

**Pure Parallel (Rust)**:
```rust
use rayon::prelude::*;

fn transform_item(item: &i32) -> i32 {
    // Pure function: no side effects
    item * 2 + 1
}

fn parallel_transform(items: Vec<i32>) -> Vec<i32> {
    // Rayon's par_iter ensures safe parallelism
    items
        .par_iter()
        .map(transform_item)
        .collect()
}
```

---

## Edge Cases

### Edge Case 1: Non-Deterministic Timing
**Scenario**: Parallel task completion order unpredictable
**Issue**: Logic depends on completion order
**Handling**:
- Ensure operations are order-independent
- Collect all results before processing
- Use deterministic combination (associative, commutative)

### Edge Case 2: Nested Parallelism
**Scenario**: Parallel tasks spawn more parallel tasks
**Issue**: Resource exhaustion, complex dependencies
**Handling**:
- Limit parallelism depth
- Use work-stealing scheduler
- Flatten nested parallelism where possible

### Edge Case 3: Partial Results
**Scenario**: Some parallel tasks fail while others succeed
**Issue**: Incomplete result set
**Handling**:
- Use Result types to capture success/failure
- Collect all results including errors
- Process after all tasks complete

**Example**:
```python
from dataclasses import dataclass
from typing import Union
from concurrent.futures import ProcessPoolExecutor, as_completed

@dataclass(frozen=True)
class Success:
    value: int

@dataclass(frozen=True)
class Failure:
    error: str

Result = Union[Success, Failure]

def safe_process(item: int) -> Result:
    """Returns Result instead of raising."""
    try:
        return Success(value=item * 2)
    except Exception as e:
        return Failure(error=str(e))

def parallel_with_errors(items: list[int]) -> list[Result]:
    """Collects all results including failures."""
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(safe_process, item) for item in items]
        return [future.result() for future in as_completed(futures)]
```

### Edge Case 4: External Resource Limits
**Scenario**: Parallel tasks hit resource limits (DB connections, API rate limits)
**Issue**: Tasks fail due to concurrent resource access
**Handling**:
- Limit parallelism with thread/process pool size
- Use semaphores for resource allocation
- Queue tasks if resources limited

### Edge Case 5: Memory Overhead
**Scenario**: Copying data for each task consumes excessive memory
**Issue**: Memory exhaustion with large datasets
**Handling**:
- Use read-only shared memory where safe
- Process in chunks/batches
- Stream data instead of loading all

---

## Database Operations

### Record Parallel Purity Metadata

```sql
-- Update function with parallel purity info
UPDATE functions
SET
    is_parallel_safe = 1,
    parallelism_metadata = '{
        "pure_tasks": true,
        "shared_state": false,
        "deterministic": true,
        "associative_operations": true
    }',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'parallel_process' AND file_id = ?;

-- Record parallelism validation
INSERT INTO notes (project_id, content, tags, created_at)
VALUES (
    1,
    'Validated parallel_process for parallel purity: all tasks pure and independent',
    '["fp_parallel_purity", "concurrency", "validation"]',
    CURRENT_TIMESTAMP
);
```

---

## Related Directives

### FP Directives
- **fp_concurrency_safety**: General thread safety for concurrent operations
- **fp_purity**: Ensures functions are pure (prerequisite for safe parallelism)
- **fp_immutability**: Immutable data enables safe parallelism
- **fp_task_isolation**: Prevents cross-task data leakage

### Project Directives
- **project_compliance_check**: Validates parallel purity
- **project_update_db**: Records parallelism metadata

---

## Helper Functions

### `validate_parallel_tasks(tasks) -> list[PurityViolation]`
Validates all tasks in parallel block are pure.

**Signature**:
```python
def validate_parallel_tasks(
    tasks: list[FunctionDefinition]
) -> list[PurityViolation]:
    """
    Checks each task for:
    - Side effects
    - Shared mutable state access
    - Dependencies on other tasks
    Returns list of purity violations.
    """
```

### `detect_shared_state(parallel_block) -> list[SharedAccess]`
Identifies shared state accessed by multiple tasks.

**Signature**:
```python
def detect_shared_state(
    parallel_block: ASTNode
) -> list[SharedAccess]:
    """
    Analyzes variables accessed by multiple parallel tasks.
    Returns list of shared state accesses.
    """
```

### `check_operation_associativity(operation) -> bool`
Verifies reduction operation is associative.

**Signature**:
```python
def check_operation_associativity(operation: str) -> bool:
    """
    Checks if operation is safe for parallel reduce.
    Returns True if associative and commutative.
    """
```

---

## Testing

### Test 1: Pure Parallel Map
```python
def test_pure_parallel_map():
    def square(x):
        return x * x

    items = list(range(100))
    result = parallel_map_pure(square, items)

    # Deterministic result
    expected = [x * x for x in items]
    assert result == expected
```

### Test 2: No Shared State
```python
def test_no_shared_state():
    # Pure parallel tasks should not share mutable state
    results = []

    def pure_task(x):
        return x * 2  # Returns result, doesn't modify shared state

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(pure_task, range(10)))

    assert len(results) == 10
    assert all(r == i * 2 for i, r in enumerate(results))
```

### Test 3: Order Independence
```python
def test_order_independence():
    def process(x):
        return x + 1

    items = list(range(100))

    # Multiple runs should give same result
    result1 = parallel_map_pure(process, items)
    result2 = parallel_map_pure(process, items)

    assert result1 == result2
```

---

## Common Mistakes

### Mistake 1: Shared Mutable Accumulator
**Problem**: Parallel tasks append to shared list

**Solution**: Return results, collect after parallel execution

```python
# ❌ Bad: shared mutable list
results = []
def task(x):
    results.append(x * 2)  # Race condition!

# ✅ Good: return results
def task(x):
    return x * 2

results = parallel_map(task, items)
```

### Mistake 2: Non-Associative Reduce
**Problem**: Using order-dependent operation in parallel reduce

**Solution**: Ensure operation is associative and commutative

```python
# ❌ Bad: subtraction (not associative)
result = parallel_reduce(lambda a, b: a - b, items)

# ✅ Good: addition (associative)
result = parallel_reduce(lambda a, b: a + b, items)
```

### Mistake 3: Hidden Dependencies
**Problem**: Parallel tasks have hidden data dependencies

**Solution**: Make dependencies explicit, execute sequentially if needed

```python
# ❌ Bad: hidden dependency
def task_a():
    global state
    state = compute()

def task_b():
    return process(state)  # Depends on task_a!

# ✅ Good: explicit dependency
def task_a():
    return compute()

def task_b(state):
    return process(state)

# Sequential execution for dependencies
state = task_a()
result = task_b(state)
```

---

## Roadblocks

### Roadblock 1: Shared Resource
**Issue**: Multiple parallel tasks access shared mutable resource
**Resolution**: Isolate data (copy) or synchronize access

### Roadblock 2: Impure Task
**Issue**: Parallel task contains side effects
**Resolution**: Refactor to pure function or isolate effects

### Roadblock 3: Data Dependency
**Issue**: Tasks have dependencies on each other
**Resolution**: Restructure to sequential or staged pipeline

---

## Integration Points

### With `fp_concurrency_safety`
Parallel purity is specialized form of concurrency safety.

### With `fp_purity`
Pure functions are naturally safe for parallelism.

### With `project_compliance_check`
Validates parallel operations maintain purity.

---

## Intent Keywords

- `parallel`
- `thread safe`
- `concurrent`
- `parallel purity`
- `independent tasks`

---

## Confidence Threshold

**0.7** - High confidence required for parallel safety validation.

---

## Notes

- Pure functions are naturally thread-safe
- Immutable data eliminates race conditions
- Parallel map: ensure function is pure
- Parallel reduce: ensure operation associative and commutative
- No shared mutable state between parallel tasks
- Independent tasks: no data dependencies
- Order independence: result same regardless of execution order
- Resource limits: control parallelism with pool size
- Error handling: use Result types to capture all outcomes
- Memory: consider copying overhead for large data
