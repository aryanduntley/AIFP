# Directive: fp_purity_caching_analysis

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Cache safety verification

---

## Purpose

The `fp_purity_caching_analysis` directive analyzes caching strategies to ensure cached results don't violate purity guarantees or cross state boundaries. This directive acts as a **safety validator** for memoization and caching, preventing incorrect optimizations that could compromise functional programming principles.

Purity caching analysis provides **safety guarantees for performance optimizations**, ensuring:
- **Cache Correctness**: Cached values are deterministic and safe to reuse
- **Purity Preservation**: Caching doesn't introduce impurity or side effects
- **State Isolation**: Cache doesn't leak state across purity boundaries
- **Referential Transparency**: Cached function remains referentially transparent
- **No Hidden State**: Cache state doesn't create hidden dependencies

This directive works in tandem with `fp_memoization` and `fp_purity` to ensure performance optimizations don't compromise correctness.

---

## When to Apply

This directive applies when:
- **Before applying memoization** - Verify function is safe to cache
- **Validating cache implementations** - Ensure cache doesn't violate purity
- **Auditing performance optimizations** - Check caching doesn't introduce bugs
- **Cross-boundary caching** - Verify cache isolation between modules/contexts
- **Shared cache analysis** - Ensure shared caches don't create dependencies
- **Called by project directives**:
  - `fp_memoization` - Validates caching safety before applying
  - `project_compliance_check` - Audits all caching for purity violations
  - Works with `fp_purity` - Cache correctness depends on function purity

---

## Workflow

### Trunk: analyze_cache_candidates

Analyzes functions and caching strategies to detect purity violations or unsafe cache patterns.

**Steps**:
1. **Identify cached functions** - Find all functions with memoization/caching
2. **Verify function purity** - Ensure cached function is pure (deterministic, no side effects)
3. **Analyze cache key generation** - Verify cache keys capture all dependencies
4. **Check cache scope** - Ensure cache doesn't cross purity boundaries
5. **Verify referential transparency** - Cached function behaves identically to uncached
6. **Evaluate cache safety** - Classify as safe, unsafe, or uncertain

### Branches

**Branch 1: If impure_function_cached**
- **Then**: `reject_caching`
- **Details**: Caching impure function violates correctness
  - Impure function (side effects, non-deterministic) cannot be safely cached
  - Remove memoization decorator
  - Flag as compliance violation
  - Document why caching unsafe
- **Result**: Returns error with explanation

**Branch 2: If incomplete_cache_key**
- **Then**: `fix_cache_key_generation`
- **Details**: Cache key doesn't capture all dependencies
  - Identify missing dependencies in cache key
  - Update cache key to include all parameters
  - Include closure variables if function uses them
  - Ensure cache key uniquely identifies computation
- **Result**: Returns corrected cache key

**Branch 3: If cross_boundary_cache**
- **Then**: `isolate_cache_scope`
- **Details**: Cache shared across purity boundaries
  - Separate cache instances for different contexts
  - Ensure cache doesn't leak state between boundaries
  - Use scoped caches instead of global
  - Document cache lifetime and scope
- **Result**: Returns isolated cache design

**Branch 4: If mutable_cache_values**
- **Then**: `enforce_immutable_cache`
- **Details**: Cached values are mutable (dangerous)
  - Cached values must be immutable to prevent accidental modification
  - Deep-copy mutable values before caching
  - Or: enforce immutability at type level
  - Document immutability requirement
- **Result**: Returns immutable cache strategy

**Branch 5: If safe_cache**
- **Then**: `mark_safe`
- **Details**: Caching is safe and correct
  - Function is pure
  - Cache key captures all dependencies
  - Cache scope is appropriate
  - Immutable values cached
- **Result**: Caching approved

**Fallback**: `prompt_user`
- **Details**: Uncertain about cache safety
  - Present analysis findings to user
  - Ask: "Is this caching strategy safe?"
  - Log uncertainty to notes table
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Safe Memoization (Passes):**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """
    Calculate Fibonacci number with safe caching.

    ✅ SAFE BECAUSE:
    - Pure function (deterministic, no side effects)
    - Cache key is complete (only parameter: n)
    - Immutable input (int)
    - Immutable output (int)
    - Referentially transparent
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Analysis:
# - Function: Pure ✓
# - Cache key: Complete (n) ✓
# - Immutability: int (immutable) ✓
# - Scope: Function-local ✓
# VERDICT: SAFE TO CACHE
```

**Why Compliant**:
- Function is pure (same input → same output)
- Cache key captures all dependencies (just `n`)
- Input and output are immutable
- No side effects or external state

---

**Safe Manual Cache (Passes):**
```python
class MemoizedCalculator:
    """
    Calculator with safe manual caching.

    Demonstrates proper cache isolation and immutability.
    """
    def __init__(self):
        # Cache isolated to instance (not global)
        self._cache: dict[tuple[int, int], int] = {}

    def calculate(self, a: int, b: int) -> int:
        """
        Calculate result with safe caching.

        ✅ SAFE BECAUSE:
        - Pure calculation
        - Complete cache key (a, b)
        - Immutable types
        - Instance-scoped cache
        """
        # Generate cache key from all parameters
        cache_key = (a, b)

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Compute (expensive pure function)
        result = self._expensive_pure_calculation(a, b)

        # Cache immutable result
        self._cache[cache_key] = result

        return result

    def _expensive_pure_calculation(self, a: int, b: int) -> int:
        """Pure calculation (deterministic)."""
        return sum(range(a * b))

# Analysis:
# - Function: Pure ✓
# - Cache key: Complete (a, b) ✓
# - Immutability: int (immutable) ✓
# - Scope: Instance-level (isolated) ✓
# VERDICT: SAFE TO CACHE
```

**Why Compliant**:
- Pure function cached
- Cache key includes all parameters
- Cache scoped to instance (not global)
- Immutable values cached

---

**Safe with Immutable Objects (Passes):**
```python
from dataclasses import dataclass
from functools import lru_cache

@dataclass(frozen=True)  # Immutable!
class Point:
    x: float
    y: float

@lru_cache(maxsize=128)
def distance_from_origin(point: Point) -> float:
    """
    Calculate distance from origin with safe caching.

    ✅ SAFE BECAUSE:
    - Pure function
    - Immutable input (frozen dataclass is hashable)
    - Cache key automatically correct (point hashed correctly)
    - Immutable output (float)
    """
    return (point.x ** 2 + point.y ** 2) ** 0.5

# Analysis:
# - Function: Pure ✓
# - Cache key: Complete (point) ✓
# - Immutability: frozen dataclass ✓
# - Hashability: frozen dataclass is hashable ✓
# VERDICT: SAFE TO CACHE
```

**Why Compliant**:
- Immutable input type (frozen dataclass)
- Hashable for cache key
- Pure function
- No state leakage

---

### ❌ Non-Compliant Code

**Caching Impure Function (Violation):**
```python
# ❌ VIOLATION: Caching impure function (incorrect results!)
from functools import lru_cache
import random

@lru_cache(maxsize=128)  # ← UNSAFE CACHE
def generate_random_number(seed: int) -> int:
    """
    Generate random number (IMPURE - non-deterministic).

    ❌ UNSAFE BECAUSE:
    - Non-deterministic (random.randint returns different values)
    - Caching breaks randomness (returns same "random" value)
    - Violates function contract
    """
    random.seed(seed)
    return random.randint(1, 100)

# Problem: First call cached, subsequent calls return same value
result1 = generate_random_number(42)  # Random value (e.g., 73)
result2 = generate_random_number(42)  # Returns 73 again (cached!)
# Expected: Different random value, Got: Same cached value
```

**Why Non-Compliant**:
- Function is impure (non-deterministic)
- Caching breaks intended behavior
- Returns stale "random" value
- Violates correctness

**Resolution**: Remove caching from impure function:
```python
# ✅ FIXED: Remove cache from impure function
def generate_random_number(seed: int) -> int:
    """Generate random number (no caching - impure)."""
    random.seed(seed)
    return random.randint(1, 100)

# Now works correctly
result1 = generate_random_number(42)  # Random value
result2 = generate_random_number(42)  # Different random value
```

---

**Incomplete Cache Key (Violation):**
```python
# ❌ VIOLATION: Cache key doesn't capture all dependencies
from functools import lru_cache

# Global state (hidden dependency!)
discount_rate = 0.1

@lru_cache(maxsize=128)  # ← UNSAFE: cache key doesn't include discount_rate
def calculate_price(base_price: float) -> float:
    """
    Calculate price with discount.

    ❌ UNSAFE BECAUSE:
    - Depends on global discount_rate
    - Cache key only includes base_price
    - Changing discount_rate doesn't invalidate cache
    - Returns incorrect cached values
    """
    return base_price * (1 - discount_rate)

# Problem: Cache doesn't account for discount_rate changes
discount_rate = 0.1
price1 = calculate_price(100)  # 90.0 (cached with discount=0.1)

discount_rate = 0.2  # Change global discount
price2 = calculate_price(100)  # 90.0 (cached! Should be 80.0)
# Expected: 80.0, Got: 90.0 (stale cache)
```

**Why Non-Compliant**:
- Cache key incomplete (missing discount_rate)
- Function depends on global state
- Cache returns incorrect results after state change
- Violates purity

**Resolution**: Include all dependencies in cache key:
```python
# ✅ FIXED: Complete cache key + pure function
@lru_cache(maxsize=128)
def calculate_price(base_price: float, discount_rate: float) -> float:
    """
    Calculate price with discount (pure function).

    ✅ SAFE: All dependencies in parameters, complete cache key.
    """
    return base_price * (1 - discount_rate)

# Now works correctly
price1 = calculate_price(100, 0.1)  # 90.0 (cached with both params)
price2 = calculate_price(100, 0.2)  # 80.0 (different cache key)
```

---

**Mutable Cached Values (Violation):**
```python
# ❌ VIOLATION: Caching mutable objects (dangerous!)
from functools import lru_cache

@lru_cache(maxsize=128)  # ← UNSAFE: caches mutable list
def get_default_config() -> list[str]:
    """
    Get default configuration.

    ❌ UNSAFE BECAUSE:
    - Returns mutable list
    - Caller can modify cached value
    - Subsequent callers get modified version
    - Cache pollution
    """
    return ['setting1', 'setting2', 'setting3']

# Problem: Modifying return value affects cache
config1 = get_default_config()  # ['setting1', 'setting2', 'setting3']
config1.append('malicious_setting')  # Modify cached value!

config2 = get_default_config()  # ['setting1', 'setting2', 'setting3', 'malicious_setting']
# Expected: ['setting1', 'setting2', 'setting3']
# Got: Modified version with 'malicious_setting'
```

**Why Non-Compliant**:
- Cached value is mutable
- Callers can modify cached object
- Cache pollution affects other callers
- Violates referential transparency

**Resolution**: Return immutable values or deep copy:
```python
# ✅ FIXED: Return immutable tuple
from functools import lru_cache

@lru_cache(maxsize=128)
def get_default_config() -> tuple[str, ...]:
    """
    Get default configuration (immutable).

    ✅ SAFE: Returns immutable tuple, cannot be modified.
    """
    return ('setting1', 'setting2', 'setting3')

# Now safe
config1 = get_default_config()  # Immutable tuple
# config1.append('x')  # Error: tuple has no append method

# ✅ Alternative: Deep copy mutable values
from functools import lru_cache
from copy import deepcopy

@lru_cache(maxsize=128)
def _get_default_config_cached() -> list[str]:
    """Internal cached function."""
    return ['setting1', 'setting2', 'setting3']

def get_default_config() -> list[str]:
    """
    Get default configuration (deep copy).

    ✅ SAFE: Returns deep copy, modifications don't affect cache.
    """
    return deepcopy(_get_default_config_cached())
```

---

**Global Shared Cache (Violation):**
```python
# ❌ VIOLATION: Global cache shared across contexts
GLOBAL_CACHE = {}  # ← UNSAFE: shared global state

def process_user_data(user_id: int, context: str) -> dict:
    """
    Process user data with global cache.

    ❌ UNSAFE BECAUSE:
    - Global cache shared across all contexts
    - Cache key doesn't include context
    - Leaks data between contexts (security issue!)
    """
    cache_key = user_id  # Missing context!

    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]

    # Expensive calculation (context-dependent)
    result = expensive_calculation(user_id, context)

    GLOBAL_CACHE[cache_key] = result
    return result

# Problem: Cache leaks between contexts
admin_result = process_user_data(123, 'admin')  # Cached
user_result = process_user_data(123, 'user')    # Returns admin result! (wrong!)
```

**Why Non-Compliant**:
- Global cache shared across contexts
- Cache key doesn't capture context
- Data leakage between contexts
- Security vulnerability

**Resolution**: Scope cache appropriately or include context in key:
```python
# ✅ FIXED: Include context in cache key
from functools import lru_cache

@lru_cache(maxsize=128)
def process_user_data(user_id: int, context: str) -> dict:
    """
    Process user data with complete cache key.

    ✅ SAFE: Cache key includes both user_id and context.
    """
    # Cache key automatically includes both parameters
    result = expensive_calculation(user_id, context)
    return result

# Now works correctly
admin_result = process_user_data(123, 'admin')  # Cached with ('admin',)
user_result = process_user_data(123, 'user')    # Different cache entry

# ✅ Alternative: Context-scoped caches
class ContextCache:
    """Separate cache per context."""
    def __init__(self):
        self._caches: dict[str, dict] = {}

    def get_cache(self, context: str) -> dict:
        """Get cache for specific context (isolated)."""
        if context not in self._caches:
            self._caches[context] = {}
        return self._caches[context]
```

---

## Edge Cases

### Edge Case 1: Caching Functions with Closures

**Issue**: Cached function captures variables from outer scope

**Handling**:
```python
# ❌ Bad: Closure variable not in cache key
def create_multiplier(factor: int):
    @lru_cache(maxsize=128)  # ← UNSAFE: factor not in cache key
    def multiply(x: int) -> int:
        return x * factor  # Captures factor from closure

    return multiply

mult2 = create_multiplier(2)
mult3 = create_multiplier(3)

result1 = mult2(5)  # 10 (cached)
result2 = mult3(5)  # 10 (cached! Should be 15)
# Problem: Cache shared between closures with different factors

# ✅ Good: Include closure variables in cache key
def create_multiplier(factor: int):
    @lru_cache(maxsize=128)
    def multiply(x: int, _factor: int = factor) -> int:
        """Include factor in cache key via default parameter."""
        return x * _factor

    return multiply
```

**Directive Action**: Include closure variables in cache key or avoid caching closures.

---

### Edge Case 2: Time-Dependent Functions

**Issue**: Function depends on current time (non-deterministic)

**Handling**:
```python
# ❌ Bad: Caching time-dependent function
from datetime import datetime

@lru_cache(maxsize=128)  # ← UNSAFE: non-deterministic
def get_greeting(name: str) -> str:
    hour = datetime.now().hour  # Non-deterministic!
    if hour < 12:
        return f"Good morning, {name}"
    else:
        return f"Good afternoon, {name}"

# Problem: Returns stale greeting
greeting1 = get_greeting("Alice")  # "Good morning, Alice" (at 10 AM, cached)
# ... time passes to 2 PM ...
greeting2 = get_greeting("Alice")  # "Good morning, Alice" (cached! Wrong!)

# ✅ Good: Remove cache or make time explicit parameter
def get_greeting(name: str, hour: int) -> str:
    """Pure function with time as explicit parameter."""
    if hour < 12:
        return f"Good morning, {name}"
    else:
        return f"Good afternoon, {name}"

# Usage: Pass current time explicitly
greeting = get_greeting("Alice", datetime.now().hour)
```

**Directive Action**: Remove caching from time-dependent functions or make time an explicit parameter.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Must verify function is pure before allowing cache
  - `fp_immutability` - Cached values must be immutable
- **Triggers**:
  - `fp_memoization` - Validates safety before applying memoization
- **Called By**:
  - `project_compliance_check` - Audits all caching for safety
  - `fp_memoization` - Consults before caching functions
- **Escalates To**: None

---

## Helper Functions Used

- `analyze_function_purity(func_id: int) -> bool` - Checks if function is pure
- `detect_cache_key_dependencies(ast: AST) -> list[Dependency]` - Finds all dependencies
- `verify_cache_scope(cache: Cache) -> ScopeAnalysis` - Checks cache isolation
- `detect_mutable_cached_values(func: Function) -> bool` - Checks immutability
- `update_functions_table(func_id: int, cache_safe: bool)` - Updates project.db

---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `cache_safety = 'verified'` for safe caching
- **`functions`**: Sets `cache_safety = 'unsafe'` for violations
- **`notes`**: Logs cache safety issues with `note_type = 'compliance'`

---

## Testing

How to verify this directive is working:

1. **Cache impure function** → Directive rejects
   ```python
   # Input
   @lru_cache
   def random_func(): return random.random()

   # Output: ERROR - Function is impure, cannot cache
   ```

2. **Cache pure function with complete key** → Directive approves
   ```python
   @lru_cache
   def pure_func(x, y): return x + y
   # ✅ Safe to cache
   ```

3. **Check database** → Verify `functions.cache_safety = 'verified'`
   ```sql
   SELECT name, cache_safety, purity_level
   FROM functions
   WHERE name = 'pure_func';
   -- Expected: cache_safety='verified', purity_level='pure'
   ```

---

## Common Mistakes

- ❌ **Caching impure functions** - Breaks correctness completely
- ❌ **Incomplete cache keys** - Returns wrong results after state changes
- ❌ **Caching mutable values** - Allows cache pollution
- ❌ **Global shared caches** - Creates cross-context dependencies
- ❌ **Caching functions with side effects** - Side effects only happen once

---

## Roadblocks and Resolutions

### Roadblock 1: impure_function_cached
**Issue**: Attempting to cache non-deterministic or side-effecting function
**Resolution**: Remove caching, make function pure first

### Roadblock 2: incomplete_cache_key
**Issue**: Cache key doesn't capture all dependencies
**Resolution**: Include all parameters and closure variables in cache key

### Roadblock 3: mutable_cache_values
**Issue**: Cached values can be modified by callers
**Resolution**: Return immutable types or deep copy on cache retrieval

### Roadblock 4: cross_boundary_cache
**Issue**: Cache shared across security/context boundaries
**Resolution**: Use scoped caches or include context in cache key

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-cache-analysis)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#optimization)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for safe caching validation*
