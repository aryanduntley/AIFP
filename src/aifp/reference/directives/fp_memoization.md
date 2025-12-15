# fp_memoization

## Purpose

The `fp_memoization` directive enables performance optimization of pure functions through caching of previously computed results. It identifies pure functions that benefit from memoization, applies appropriate caching strategies, and validates that only pure functions are memoized to maintain correctness. Memoization leverages function purity to trade memory for speed, dramatically improving performance for expensive computations with repeated inputs.

**Category**: Optimization
**Type**: FP Auxiliary
**Priority**: Medium
**Confidence Threshold**: 0.8

---

## Workflow

### Trunk
**`analyze_memoization_candidates`**: Identify pure functions that would benefit from result caching.

### Branches

1. **`expensive_pure_function`** → **`apply_memoization`**
   - **Condition**: Pure function with expensive computation and likely repeated calls
   - **Action**: Apply memoization decorator or caching wrapper
   - **Details**: Cache results by input parameters, return cached for repeated inputs
   - **Output**: Memoized function

2. **`recursive_function`** → **`apply_recursive_memoization`**
   - **Condition**: Pure recursive function (e.g., fibonacci, factorial)
   - **Action**: Apply memoization to cache recursive sub-results
   - **Details**: Dramatically improves recursive algorithm performance
   - **Output**: Memoized recursive function

3. **`impure_function`** → **`reject_memoization`**
   - **Condition**: Function has side effects or is non-deterministic
   - **Action**: Block memoization and warn user
   - **Details**: Memoizing impure functions leads to incorrect behavior
   - **Output**: Memoization rejection warning

4. **`cache_strategy_selection`** → **`choose_cache_policy`**
   - **Condition**: Memoization candidate identified
   - **Action**: Select appropriate cache policy (LRU, unbounded, TTL)
   - **Details**: Based on input space size and access patterns
   - **Output**: Cache policy recommendation

5. **Fallback** → **`document_analysis`**
   - **Condition**: Function analyzed but memoization not recommended
   - **Action**: Document why memoization not beneficial

### Error Handling
- **On failure**: Log memoization application failure
- **Low confidence** (< 0.8): Request manual review before applying memoization

---

## Refactoring Strategies

### Strategy 1: Basic Function Memoization

Apply memoization decorator to expensive pure functions.

**Before (No Caching)**:
```python
def calculate_expensive_result(x: int, y: int) -> float:
    """Expensive pure computation."""
    # Simulate expensive calculation
    result = 0.0
    for i in range(1000000):
        result += (x ** 2 + y ** 2) ** 0.5
    return result

# Called multiple times with same inputs - wasteful!
result1 = calculate_expensive_result(5, 10)
result2 = calculate_expensive_result(5, 10)  # Recomputes unnecessarily
result3 = calculate_expensive_result(5, 10)  # Recomputes again
```

**After (Memoized)**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_expensive_result(x: int, y: int) -> float:
    """
    Expensive pure computation with memoization.

    Pure function: Deterministic, no side effects.
    Memoized: Results cached by input parameters.

    Cache: LRU with max 128 entries.
    """
    result = 0.0
    for i in range(1000000):
        result += (x ** 2 + y ** 2) ** 0.5
    return result

# First call computes and caches
result1 = calculate_expensive_result(5, 10)  # Computes

# Subsequent calls return cached result - instant!
result2 = calculate_expensive_result(5, 10)  # Cached
result3 = calculate_expensive_result(5, 10)  # Cached
```

**Performance Impact**:
- First call: ~2 seconds (computation)
- Subsequent calls: ~0.0001 seconds (cache lookup)
- 20,000x speedup for cached calls

---

### Strategy 2: Recursive Function Memoization

Memoization dramatically improves recursive algorithms.

**Before (Exponential Time Complexity)**:
```python
def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number. Pure but slow!"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Extremely slow for larger n due to repeated calculations
result = fibonacci(35)  # Takes ~5 seconds
# fibonacci(35) calls fibonacci(34) and fibonacci(33)
# fibonacci(34) calls fibonacci(33) and fibonacci(32)
# fibonacci(33) is computed TWICE (and many more times deeper)
```

**After (Linear Time with Memoization)**:
```python
from functools import lru_cache

@lru_cache(maxsize=None)  # Unbounded cache for small input space
def fibonacci(n: int) -> int:
    """
    Calculate nth Fibonacci number with memoization.

    Pure function: Deterministic recursive computation.
    Memoized: Each fibonacci(n) computed only once.

    Time Complexity: O(n) instead of O(2^n)
    Space Complexity: O(n) for cache
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Dramatically faster with memoization
result = fibonacci(35)  # Takes ~0.0001 seconds (2000x faster!)
result = fibonacci(100)  # Still instant!
```

**Performance Comparison**:
```
Without memoization:
- fibonacci(35): ~5 seconds
- fibonacci(40): ~60 seconds
- fibonacci(45): ~10 minutes

With memoization:
- fibonacci(35): ~0.0001 seconds
- fibonacci(40): ~0.0001 seconds
- fibonacci(100): ~0.0001 seconds
```

---

### Strategy 3: Manual Memoization for Complex Cases

Custom memoization for functions with complex cache key requirements.

**Before (Complex Parameters)**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    id: int
    name: str
    roles: tuple[str, ...]

def calculate_user_permissions(user: User, resource: str) -> set[str]:
    """Pure but can't use default memoization (unhashable types in complex cases)."""
    # Expensive permission calculation
    permissions = set()

    # Complex logic based on roles
    for role in user.roles:
        permissions.update(get_role_permissions(role, resource))

    return permissions
```

**After (Custom Cache Key)**:
```python
from functools import lru_cache
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    id: int
    name: str
    roles: tuple[str, ...]  # Tuple is hashable

@lru_cache(maxsize=256)
def _calculate_user_permissions_cached(
    user_id: int,
    roles: tuple[str, ...],
    resource: str
) -> frozenset[str]:
    """
    Internal cached implementation with hashable parameters.

    Pure function: Deterministic permission calculation.
    Memoized: Results cached by user_id, roles, and resource.
    """
    permissions = set()

    for role in roles:
        permissions.update(get_role_permissions(role, resource))

    return frozenset(permissions)  # Return immutable

def calculate_user_permissions(user: User, resource: str) -> frozenset[str]:
    """
    Calculate user permissions with memoization.

    Wrapper that converts User to hashable cache key.
    """
    return _calculate_user_permissions_cached(
        user.id,
        user.roles,
        resource
    )
```

---

### Strategy 4: Cache Policy Selection

Choose appropriate cache policy based on usage patterns.

**LRU Cache (Limited Size)**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)  # Keep most recent 128 results
def transform_data(data: tuple[int, ...]) -> tuple[int, ...]:
    """
    Transform data with LRU cache.

    Memoized: Keeps 128 most recently used results.
    Use when: Large input space, limited memory, locality of reference.
    """
    return tuple(x * 2 for x in data)
```

**Unbounded Cache (Small Input Space)**:
```python
@lru_cache(maxsize=None)  # Cache all results
def factorial(n: int) -> int:
    """
    Calculate factorial with unbounded cache.

    Memoized: Caches all results forever.
    Use when: Small input space (0-1000), results reused frequently.
    """
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

**TTL Cache (Time-Limited)**:
```python
from cachetools import TTLCache, cached

# Cache expires after 60 seconds
cache = TTLCache(maxsize=100, ttl=60)

@cached(cache)
def fetch_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Fetch exchange rate with TTL cache.

    Memoized: Results valid for 60 seconds.
    Use when: Data changes over time but acceptable to be slightly stale.

    Note: This is for pure computation of cached data source,
    actual fetching should be in IO function.
    """
    # In practice, this would call pure calculation on cached exchange data
    # The I/O fetch would be separate
    return get_cached_rate(from_currency, to_currency)
```

---

### Strategy 5: Conditional Memoization

Apply memoization only when beneficial.

**Before (Always Memoize)**:
```python
@lru_cache(maxsize=128)
def simple_addition(a: int, b: int) -> int:
    """Memoization overhead not worth it for simple operations."""
    return a + b  # Too simple to benefit from caching
```

**After (Conditional Memoization)**:
```python
def simple_addition(a: int, b: int) -> int:
    """Simple operation - no memoization needed."""
    return a + b  # Direct computation faster than cache lookup

@lru_cache(maxsize=128)
def complex_calculation(a: int, b: int) -> float:
    """
    Complex calculation that benefits from memoization.

    Memoized: Expensive computation worth caching.
    """
    # Expensive computation
    result = 0.0
    for i in range(10000):
        result += (a ** i + b ** i) ** 0.5
    return result
```

**When to Memoize**:
- ✅ Computation time > 10ms
- ✅ Function called repeatedly with same inputs
- ✅ Input space manageable
- ✅ Memory available for cache
- ❌ Trivial operations (< 1ms)
- ❌ Rarely repeated inputs
- ❌ Huge input space
- ❌ Memory constrained

---

## Examples

### Example 1: Dynamic Programming with Memoization

**Longest Common Subsequence**:
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def lcs_length(s1: str, s2: str) -> int:
    """
    Calculate length of longest common subsequence.

    Pure recursive function with memoization.
    Time Complexity: O(m*n) instead of O(2^(m+n))

    Args:
        s1: First string
        s2: Second string

    Returns:
        Length of LCS

    Examples:
        >>> lcs_length("ABCDGH", "AEDFHR")
        3  # "ADH"

    Memoization Impact:
        - Without: O(2^(m+n)) - exponential
        - With: O(m*n) - polynomial
    """
    if not s1 or not s2:
        return 0

    if s1[0] == s2[0]:
        return 1 + lcs_length(s1[1:], s2[1:])

    return max(
        lcs_length(s1[1:], s2),
        lcs_length(s1, s2[1:])
    )
```

### Example 2: Memoization in Data Processing Pipeline

```python
from functools import lru_cache
from dataclasses import dataclass

@dataclass(frozen=True)
class DataPoint:
    value: float
    category: str

@lru_cache(maxsize=1000)
def expensive_transform(data: tuple[DataPoint, ...]) -> tuple[DataPoint, ...]:
    """
    Expensive data transformation with memoization.

    Pure function: Deterministic transformation.
    Memoized: Caches results for repeated pipelines.

    Use case: When same data subsets are processed multiple times
    in different pipeline branches.
    """
    # Simulate expensive transformation
    result = []
    for point in data:
        transformed_value = complex_calculation(point.value)
        result.append(DataPoint(
            value=transformed_value,
            category=point.category
        ))
    return tuple(result)

@lru_cache(maxsize=10000)
def complex_calculation(value: float) -> float:
    """Memoized helper for expensive per-value computation."""
    # Expensive per-value calculation
    result = value
    for _ in range(1000):
        result = (result ** 2 + value) ** 0.5
    return result
```

---

## Edge Cases

### Edge Case 1: Mutable Arguments
**Scenario**: Function takes mutable arguments (lists, dicts)
**Issue**: Mutable types not hashable, can't be cache keys
**Handling**:
- Convert to immutable types (tuple, frozenset)
- Use custom cache key function
- Reject memoization if conversion not possible

**Example**:
```python
# Convert list to tuple for caching
def process_items_memoized(items: list[int]) -> int:
    return _process_items_cached(tuple(items))

@lru_cache(maxsize=128)
def _process_items_cached(items: tuple[int, ...]) -> int:
    """Internal cached implementation with hashable tuple."""
    return sum(x * 2 for x in items)
```

### Edge Case 2: Large Result Values
**Scenario**: Function returns large data structures
**Issue**: Cache consumes excessive memory
**Handling**:
- Use smaller cache size
- Consider caching only frequently accessed results
- Use weakref for large objects

### Edge Case 3: Random or Time-Dependent Functions
**Scenario**: Function uses randomness or current time
**Issue**: Not truly pure, memoization incorrect
**Handling**:
- Reject memoization
- Refactor to pure function with time/seed as parameter
- Make randomness/time explicit input

### Edge Case 4: Functions with Many Parameters
**Scenario**: Function has 10+ parameters
**Issue**: Large cache key overhead, unlikely to have cache hits
**Handling**:
- Group parameters into composite types
- Reduce parameters if possible
- May not benefit from memoization

### Edge Case 5: Recursive Functions with Multiple Paths
**Scenario**: Recursive function with multiple recursive calls
**Issue**: Cache may not help if paths don't overlap
**Handling**:
- Analyze call patterns
- Apply memoization anyway for safety
- Measure actual performance improvement

---

## Database Operations

### Record Memoization Metadata

```sql
-- Update function with memoization metadata
UPDATE functions
SET
    is_memoized = 1,
    memoization_metadata = json_set(
        COALESCE(memoization_metadata, '{}'),
        '$.cache_policy', 'lru',
        '$.max_size', 128,
        '$.hit_rate', NULL  -- Populated during runtime monitoring
    ),
    optimization_level = 'memoized',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'calculate_expensive_result' AND file_id = ?;
```

---

## Related Directives

### FP Directives
- **fp_purity**: Only pure functions can be safely memoized
- **fp_immutability**: Memoization works best with immutable data
- **fp_recursion_enforcement**: Recursive functions benefit most from memoization

### Project Directives
- **project_compliance_check**: Validates memoization only applied to pure functions
- **project_update_db**: Records memoization metadata

---

## Helper Functions

### `identify_memoization_candidates(function) -> bool`
Analyzes whether function would benefit from memoization.

**Signature**:
```python
def identify_memoization_candidates(
    function: FunctionDef,
    call_frequency: int,
    avg_execution_time_ms: float
) -> bool:
    """
    Determines if function is good memoization candidate.
    Returns True if memoization likely to improve performance.
    """
```

### `select_cache_policy(function) -> str`
Recommends cache policy based on function characteristics.

**Signature**:
```python
def select_cache_policy(
    function: FunctionDef,
    input_space_size: int,
    access_pattern: str
) -> str:
    """
    Recommends cache policy (lru, unbounded, ttl).
    Returns policy name with recommended parameters.
    """
```

---

## Testing

### Test 1: Memoization Correctness
```python
def test_memoized_function_correctness():
    @lru_cache(maxsize=128)
    def double(x):
        return x * 2

    # Memoized results must be identical to non-memoized
    assert double(5) == 10
    assert double(5) == 10  # Cached
    assert double(10) == 20
```

### Test 2: Cache Hit Rate
```python
def test_cache_effectiveness():
    @lru_cache(maxsize=128)
    def expensive_func(x):
        return x ** 2

    # Clear cache
    expensive_func.cache_clear()

    # First call - cache miss
    result1 = expensive_func(5)

    # Check cache info
    info = expensive_func.cache_info()
    assert info.hits == 0
    assert info.misses == 1

    # Second call - cache hit
    result2 = expensive_func(5)

    info = expensive_func.cache_info()
    assert info.hits == 1
    assert info.misses == 1
```

### Test 3: Performance Improvement
```python
import time

def test_memoization_performance():
    @lru_cache(maxsize=None)
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    # Measure memoized performance
    start = time.time()
    result = fibonacci(35)
    memoized_time = time.time() - start

    assert memoized_time < 0.01  # Should be nearly instant
```

---

## Common Mistakes

### Mistake 1: Memoizing Impure Functions
**Problem**: Caching function with side effects

**Solution**: Only memoize pure functions

```python
# ❌ Bad: memoizing impure function
@lru_cache(maxsize=128)
def get_user(user_id):
    return database.fetch(user_id)  # Side effect! Results can change!

# ✅ Good: only memoize pure functions
@lru_cache(maxsize=128)
def calculate_user_score(activity_count, rating):
    """Pure calculation - safe to memoize."""
    return activity_count * rating * 1.5
```

### Mistake 2: Unbounded Cache on Large Input Space
**Problem**: Memory exhaustion from unlimited caching

**Solution**: Use LRU cache with appropriate size

```python
# ❌ Bad: unbounded cache for large input space
@lru_cache(maxsize=None)
def process_image(image_data: bytes):
    # Huge input space - will consume all memory!
    pass

# ✅ Good: bounded LRU cache
@lru_cache(maxsize=100)
def process_small_config(config_key: str):
    # Small input space - bounded cache appropriate
    pass
```

### Mistake 3: Memoizing Trivial Operations
**Problem**: Cache overhead exceeds computation cost

**Solution**: Only memoize expensive operations

```python
# ❌ Bad: memoizing trivial operation
@lru_cache(maxsize=128)
def add(a, b):
    return a + b  # Cache lookup slower than computation!

# ✅ Good: memoize expensive operation
@lru_cache(maxsize=128)
def complex_transform(data):
    """Expensive multi-step transformation."""
    # Worth the cache overhead
    return expensive_calculation(data)
```

---

## Roadblocks

### Roadblock 1: Mutable Parameters
**Issue**: Function parameters not hashable for cache keys
**Resolution**: Convert to immutable types or use custom key function

### Roadblock 2: Memory Constraints
**Issue**: Cache consumes too much memory
**Resolution**: Reduce cache size, use LRU policy, measure memory usage

### Roadblock 3: Low Cache Hit Rate
**Issue**: Memoization not improving performance (few repeated inputs)
**Resolution**: Remove memoization if hit rate < 10%, analyze access patterns

---

## Integration Points

### With `fp_purity`
Only pure functions can be safely memoized.

### With `fp_immutability`
Immutable parameters enable correct memoization.

### With `project_compliance_check`
Validates memoization correctness during compliance checks.

---

## Intent Keywords

- `memoization`
- `caching`
- `optimization`
- `performance`
- `pure functions`

---

## Confidence Threshold

**0.8** - Very high confidence required before applying memoization.

---

## Notes

- Only pure functions can be memoized
- Memoization trades memory for speed
- Most beneficial for recursive functions
- LRU cache for large input spaces
- Unbounded cache for small input spaces
- Measure performance improvement
- Consider cache hit rate
- Mutable parameters require conversion to immutable
- Cache overhead for trivial operations not worth it
- AIFP leverages purity for safe aggressive memoization

