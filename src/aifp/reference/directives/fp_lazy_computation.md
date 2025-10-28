# Directive: fp_lazy_computation

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Performance optimization

---

## Purpose

The `fp_lazy_computation` directive transforms eager calculations into lazy or deferred evaluations, computing values only when actually needed. Unlike `fp_lazy_evaluation` (which focuses on lazy sequences), this directive addresses **lazy function evaluation** and **on-demand computation** for expensive operations.

Lazy computation provides **performance optimization through deferral**, enabling:
- **Deferred Evaluation**: Delay expensive computations until results needed
- **Conditional Computation**: Avoid computing values that may not be used
- **Shared Computation**: Compute once when accessed, cache result
- **Performance**: Skip unnecessary work in conditional branches
- **Composability**: Build computation graphs evaluated on demand

This directive is particularly valuable for expensive calculations, configuration initialization, and resource-intensive operations that may not always be needed.

---

## When to Apply

This directive applies when:
- **Expensive computations may not be used** - Heavy calculations in conditional branches
- **Configuration/initialization overhead** - Loading resources that may not be needed
- **Default parameter values** - Computing defaults only when parameters not provided
- **Conditional data loading** - Load data only if validation passes
- **Building computation pipelines** - Compose operations, evaluate on demand
- **Called by project directives**:
  - `project_file_write` - Validates lazy computation patterns
  - Works with `fp_lazy_evaluation` - Lazy sequences vs lazy functions
  - Works with `fp_memoization` - Lazy + cache for optimal performance

---

## Workflow

### Trunk: analyze_computation_order

Scans code to detect eager computations that could be deferred for better performance.

**Steps**:
1. **Parse function body** - Build computation graph
2. **Identify expensive operations** - Heavy calculations, I/O, resource initialization
3. **Analyze usage patterns** - Determine if values always used
4. **Identify conditional branches** - Computations in if/else that may not execute
5. **Evaluate deferral opportunity** - Classify as defer-candidate, already-lazy, or eager-required
6. **Assess performance impact** - Estimate savings from lazy evaluation

### Branches

**Branch 1: If eager_expensive_computation**
- **Then**: `wrap_in_lazy_thunk`
- **Details**: Wrap eager computation in lazy thunk (function)
  - Replace `value = expensive_calc()` with `value_thunk = lambda: expensive_calc()`
  - Delay execution until value accessed
  - Wrap in Lazy monad for automatic evaluation tracking
  - Cache result after first evaluation (memoize)
- **Result**: Returns lazy-wrapped computation

**Branch 2: If conditional_computation**
- **Then**: `defer_until_needed`
- **Details**: Move computation inside conditional branch
  - Identify if computation only used in one branch
  - Move calculation to point of use
  - Avoid computing if branch not taken
- **Result**: Returns branch-local computation

**Branch 3: If default_parameter_computation**
- **Then**: `convert_to_lazy_default`
- **Details**: Replace eager default with lazy thunk
  - Replace `def func(x=expensive())` with `def func(x=None): x = x or lazy(expensive)`
  - Evaluate default only when needed
  - Use sentinel value + lazy evaluation
- **Result**: Returns lazy default parameter

**Branch 4: If already_lazy**
- **Then**: `mark_compliant`
- **Details**: Computation already deferred
  - Using thunks, lazy monads, or on-demand evaluation
  - Mark as compliant
- **Result**: Code passes lazy computation check

**Branch 5: If eager_required**
- **Then**: `document_rationale`
- **Details**: Eager evaluation necessary (e.g., initialization order dependencies)
  - Document why lazy not applicable
  - No refactoring needed
- **Result**: Eager computation justified

**Fallback**: `prompt_user`
- **Details**: Uncertain about lazy conversion
  - Present performance analysis to user
  - Ask: "Defer computation?"
  - Consider complexity vs benefit tradeoff
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Lazy Monad (Passes):**
```python
class Lazy:
    """
    Lazy computation monad.

    Wraps expensive computation, evaluates once on demand, caches result.
    """
    def __init__(self, thunk):
        """
        Initialize with thunk (parameterless function).

        Args:
            thunk: Function that computes the value when called
        """
        self._thunk = thunk
        self._evaluated = False
        self._value = None

    def value(self):
        """
        Force evaluation and return value.

        Computes on first call, returns cached value on subsequent calls.
        """
        if not self._evaluated:
            self._value = self._thunk()
            self._evaluated = True
        return self._value

    def map(self, f):
        """Map over lazy value (stays lazy)."""
        return Lazy(lambda: f(self.value()))

    def flatMap(self, f):
        """FlatMap over lazy value (stays lazy)."""
        return Lazy(lambda: f(self.value()).value())


def expensive_calculation(n: int) -> int:
    """Simulate expensive computation."""
    print(f"Computing expensive result for {n}")
    result = sum(range(n * 1000000))
    return result


def process_conditionally(condition: bool, n: int) -> int:
    """
    Process using lazy computation.

    Expensive calculation only happens if condition is True.
    """
    # Wrap expensive computation in Lazy (not evaluated yet)
    lazy_result = Lazy(lambda: expensive_calculation(n))

    if condition:
        # Force evaluation only when needed
        return lazy_result.value() * 2
    else:
        # Never computed if condition False
        return 0

# Usage
result = process_conditionally(False, 100)  # "Computing..." never printed
# Output: 0 (instant - no computation)

result = process_conditionally(True, 100)   # "Computing..." printed once
# Output: (expensive result) * 2
```

**Why Compliant**:
- Expensive computation wrapped in Lazy
- Only evaluates when value() called
- Caches result after first evaluation
- Avoids work in false branch

---

**Lazy Configuration (Passes):**
```python
class Config:
    """
    Application configuration with lazy initialization.

    Database, cache, and logging initialized only when accessed.
    """
    def __init__(self):
        # Lazy initialization - not computed until accessed
        self._database = Lazy(lambda: self._init_database())
        self._cache = Lazy(lambda: self._init_cache())
        self._logger = Lazy(lambda: self._init_logger())

    def _init_database(self):
        """Expensive database connection setup."""
        print("Initializing database connection...")
        # Simulate expensive connection
        import time
        time.sleep(1)
        return DatabaseConnection()

    def _init_cache(self):
        """Expensive cache setup."""
        print("Initializing cache...")
        return CacheConnection()

    def _init_logger(self):
        """Expensive logging setup."""
        print("Initializing logger...")
        return Logger()

    @property
    def database(self):
        """Get database (init on first access)."""
        return self._database.value()

    @property
    def cache(self):
        """Get cache (init on first access)."""
        return self._cache.value()

    @property
    def logger(self):
        """Get logger (init on first access)."""
        return self._logger.value()


# Usage
config = Config()  # Instant - nothing initialized
# No output

# Use only database
data = config.database.query("SELECT * FROM users")
# Output: "Initializing database connection..."
# Cache and logger never initialized (not needed)
```

**Why Compliant**:
- Resource initialization deferred
- Only accessed resources are initialized
- Significant startup time savings
- On-demand computation

---

**Lazy Default Parameters (Passes):**
```python
def process_data(data: list[int], transformer=None):
    """
    Process data with optional transformer.

    Default transformer computed lazily only if needed.
    """
    # Lazy default - only compute if transformer not provided
    if transformer is None:
        # Expensive default computation happens here (if needed)
        transformer = Lazy(lambda: build_default_transformer())

    # Use transformer
    if isinstance(transformer, Lazy):
        transformer = transformer.value()

    return [transformer(x) for x in data]


def build_default_transformer():
    """Expensive transformer construction."""
    print("Building default transformer...")
    # Expensive ML model loading, configuration, etc.
    return lambda x: x * 2


# Usage with custom transformer (default never computed)
result = process_data([1, 2, 3], lambda x: x + 1)
# Output: [2, 3, 4]
# "Building default transformer..." never printed

# Usage without transformer (default computed once)
result = process_data([1, 2, 3])
# Output: "Building default transformer..."
# Output: [2, 4, 6]
```

**Why Compliant**:
- Default parameter evaluated lazily
- Only computed when actually used
- Avoids unnecessary work when custom value provided

---

### ❌ Non-Compliant Code

**Eager Conditional Computation (Violation):**
```python
# ❌ VIOLATION: Expensive computation even when not used
def process_user(user: User, include_analytics: bool) -> dict:
    # Computed ALWAYS, even if include_analytics is False!
    analytics_data = calculate_complex_analytics(user)  # ← Eager: 5 seconds

    # Computed ALWAYS, even if include_analytics is False!
    ml_predictions = run_ml_model(user)  # ← Eager: 10 seconds

    result = {
        'user_id': user.id,
        'name': user.name
    }

    if include_analytics:
        # Only used here, but computed above regardless
        result['analytics'] = analytics_data
        result['predictions'] = ml_predictions

    return result

# Called with False - still spends 15 seconds computing unused data!
data = process_user(user, include_analytics=False)  # 15 seconds wasted
```

**Why Non-Compliant**:
- Expensive computations executed eagerly
- Values computed even when not used
- 15 seconds wasted on false branch
- Performance bottleneck

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Lazy computation with on-demand evaluation
def process_user(user: User, include_analytics: bool) -> dict:
    """
    Process user with lazy analytics computation.

    Analytics only computed if include_analytics is True.
    """
    result = {
        'user_id': user.id,
        'name': user.name
    }

    if include_analytics:
        # Compute only when needed (inside branch)
        analytics_data = calculate_complex_analytics(user)  # 5 seconds
        ml_predictions = run_ml_model(user)  # 10 seconds

        result['analytics'] = analytics_data
        result['predictions'] = ml_predictions

    return result

# Called with False - instant (0 seconds)
data = process_user(user, include_analytics=False)  # Instant!

# ✅ Alternative: Lazy monad for caching
def process_user_lazy(user: User, include_analytics: bool) -> dict:
    """Process user with lazy cached analytics."""
    # Wrap in Lazy (not computed yet)
    lazy_analytics = Lazy(lambda: calculate_complex_analytics(user))
    lazy_predictions = Lazy(lambda: run_ml_model(user))

    result = {
        'user_id': user.id,
        'name': user.name
    }

    if include_analytics:
        # Compute on demand, cache result
        result['analytics'] = lazy_analytics.value()
        result['predictions'] = lazy_predictions.value()

    return result
```

---

**Eager Default Parameter (Violation):**
```python
# ❌ VIOLATION: Default computed at function definition (always!)
def create_timestamp_default():
    """Expensive default computation."""
    print("Computing default timestamp...")
    return datetime.now()

def log_event(event: str, timestamp=create_timestamp_default()):  # ← EAGER!
    """
    Log event with timestamp.

    Default computed ONCE at function definition, not at call time!
    """
    print(f"{timestamp}: {event}")

# Problem: timestamp computed when function DEFINED, not when CALLED
log_event("Event 1")  # Uses old timestamp
time.sleep(5)
log_event("Event 2")  # Uses SAME old timestamp (computed at definition)!
```

**Why Non-Compliant**:
- Default parameter evaluated at function definition time
- Same value used for all calls (wrong for timestamps!)
- Expensive computation happens even if parameter provided
- Python gotcha: mutable defaults evaluated once

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Lazy default with None sentinel
def log_event(event: str, timestamp=None):
    """
    Log event with lazy default timestamp.

    Timestamp computed at call time if not provided.
    """
    if timestamp is None:
        # Compute default when needed (call time)
        timestamp = datetime.now()

    print(f"{timestamp}: {event}")

# Correct: fresh timestamp for each call
log_event("Event 1")  # Computes timestamp now
time.sleep(5)
log_event("Event 2")  # Computes NEW timestamp now

# ✅ Alternative: Lazy monad for expensive defaults
def log_event_lazy(event: str, timestamp: Lazy = None):
    """Log event with lazy timestamp."""
    if timestamp is None:
        # Lazy default
        timestamp = Lazy(lambda: datetime.now())

    # Force evaluation when needed
    ts_value = timestamp.value() if isinstance(timestamp, Lazy) else timestamp
    print(f"{ts_value}: {event}")
```

---

**Eager Initialization (Violation):**
```python
# ❌ VIOLATION: Eager resource initialization
class Application:
    def __init__(self):
        # All initialized immediately, even if not used!
        print("Initializing database...")
        self.database = Database.connect()  # ← Eager: 2 seconds

        print("Initializing cache...")
        self.cache = Cache.connect()  # ← Eager: 1 second

        print("Loading ML model...")
        self.ml_model = load_ml_model()  # ← Eager: 10 seconds

        print("Connecting to external API...")
        self.api_client = APIClient()  # ← Eager: 1 second

# Creating app takes 14 seconds, even for simple operations!
app = Application()  # 14 seconds
# Output:
# Initializing database...
# Initializing cache...
# Loading ML model...
# Connecting to external API...

# Simple operation doesn't need ML model or API, but paid initialization cost
result = app.database.query("SELECT 1")
```

**Why Non-Compliant**:
- All resources initialized eagerly at startup
- 14 second startup time even for simple operations
- ML model loaded even if never used
- Resources can't be initialized selectively

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Lazy resource initialization
class Application:
    def __init__(self):
        # Lazy initialization - compute on first access
        self._database = Lazy(lambda: self._init_database())
        self._cache = Lazy(lambda: self._init_cache())
        self._ml_model = Lazy(lambda: self._init_ml_model())
        self._api_client = Lazy(lambda: self._init_api_client())

    def _init_database(self):
        print("Initializing database...")
        return Database.connect()

    def _init_cache(self):
        print("Initializing cache...")
        return Cache.connect()

    def _init_ml_model(self):
        print("Loading ML model...")
        return load_ml_model()

    def _init_api_client(self):
        print("Connecting to external API...")
        return APIClient()

    @property
    def database(self):
        return self._database.value()

    @property
    def cache(self):
        return self._cache.value()

    @property
    def ml_model(self):
        return self._ml_model.value()

    @property
    def api_client(self):
        return self._api_client.value()

# Creating app is instant!
app = Application()  # Instant (0 seconds)
# No output

# Only database initialized (2 seconds)
result = app.database.query("SELECT 1")
# Output: "Initializing database..."
# ML model, cache, API never initialized (not needed)
```

---

## Edge Cases

### Edge Case 1: Evaluation Order Dependencies

**Issue**: Lazy computation has dependencies on evaluation order

**Handling**:
```python
# When computations have dependencies, maintain order
def calculate_with_dependencies(x: int) -> int:
    """
    Calculations with dependencies.

    Step 2 depends on Step 1 result.
    """
    # Step 1 (may not be needed)
    lazy_step1 = Lazy(lambda: expensive_step1(x))

    # Step 2 depends on step1 (also lazy)
    lazy_step2 = lazy_step1.map(lambda s1: expensive_step2(s1))

    # Both evaluate in correct order when step2 accessed
    return lazy_step2.value()
```

**Directive Action**: Chain lazy computations with map/flatMap to maintain dependencies.

---

### Edge Case 2: Side Effects in Lazy Computation

**Issue**: Side effects in lazy thunk may not execute as expected

**Handling**:
```python
# ❌ Bad: Side effect in lazy computation (surprising behavior)
def log_and_compute(x: int) -> Lazy:
    return Lazy(lambda: (print(f"Computing {x}"), x * 2)[1])

lazy_val = log_and_compute(5)  # No output (not evaluated)
# Side effect doesn't happen until forced

# ✅ Good: Separate pure computation from side effects
def compute_pure(x: int) -> int:
    """Pure computation (no side effects)."""
    return x * 2

def compute_with_logging(x: int) -> int:
    """Explicit side effect at evaluation time."""
    print(f"Computing {x}")  # Side effect happens immediately
    lazy_result = Lazy(lambda: compute_pure(x))
    return lazy_result.value()
```

**Directive Action**: Keep lazy computations pure, perform side effects at evaluation boundaries.

---

### Edge Case 3: Memory vs Computation Tradeoff

**Issue**: Caching lazy results uses memory

**Handling**:
```python
# Lazy with caching (memory cost)
lazy_val = Lazy(lambda: expensive_computation())
result1 = lazy_val.value()  # Computed and cached
result2 = lazy_val.value()  # Retrieved from cache (fast)

# Lazy without caching (recompute each time)
class LazyNoCache:
    """Lazy without caching - recompute each access."""
    def __init__(self, thunk):
        self._thunk = thunk

    def value(self):
        """Recompute each time."""
        return self._thunk()

lazy_no_cache = LazyNoCache(lambda: expensive_computation())
result1 = lazy_no_cache.value()  # Computed
result2 = lazy_no_cache.value()  # Computed again (no cache)

# Choose based on access patterns:
# - Single access or rare access: No cache needed
# - Multiple accesses: Cache worth the memory
```

**Directive Action**: Use cached Lazy for multiple accesses, uncached for single access.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Lazy computations must be pure
  - `fp_immutability` - Cached values must be immutable
- **Triggers**:
  - `fp_memoization` - Combine lazy + memoization for optimal performance
  - `fp_lazy_evaluation` - Lazy sequences (related concept)
- **Called By**:
  - `project_file_write` - Validates lazy computation patterns
  - Works with `fp_side_effect_detection` - Separate effects from lazy computations
- **Escalates To**: None

---

## Helper Functions Used

- `detect_expensive_computations(ast: AST) -> list[Computation]` - Finds heavy calculations
- `analyze_computation_usage(ast: AST) -> list[Usage]` - Determines if values always used
- `refactor_to_lazy(code: str, computations: list) -> str` - Wraps in lazy thunks
- `generate_lazy_monad_code(language: str) -> str` - Generates Lazy monad implementation
- `update_functions_table(func_id: int, uses_lazy: bool)` - Updates project.db

---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `evaluation_strategy = 'lazy_computation'` for lazy functions
- **`functions`**: Updates `performance_optimization = 'deferred'` for deferred computations
- **`notes`**: Logs lazy computation opportunities with `note_type = 'optimization'`

---

## Testing

How to verify this directive is working:

1. **Write eager expensive computation** → Directive suggests lazy wrapper
   ```python
   # Input (eager)
   result = expensive_calc() if condition else 0

   # Suggested output (lazy)
   lazy_result = Lazy(lambda: expensive_calc())
   result = lazy_result.value() if condition else 0
   ```

2. **Write lazy thunk** → Directive marks compliant
   ```python
   lazy_val = Lazy(lambda: expensive_calc())
   # ✅ Already lazy
   ```

3. **Check database** → Verify `functions.evaluation_strategy = 'lazy_computation'`
   ```sql
   SELECT name, evaluation_strategy, performance_optimization
   FROM functions
   WHERE name = 'process_data';
   -- Expected: evaluation_strategy='lazy_computation', performance_optimization='deferred'
   ```

---

## Common Mistakes

- ❌ **Side effects in lazy thunks** - May not execute when expected
- ❌ **Forgetting to force evaluation** - Passing Lazy object instead of value
- ❌ **Over-caching** - Wasting memory for single-use computations
- ❌ **Eager default parameters** - Using mutable defaults or function calls
- ❌ **No performance benefit** - Using lazy for cheap operations (overhead not worth it)

---

## Roadblocks and Resolutions

### Roadblock 1: eager_expensive_computation
**Issue**: Expensive computation executed eagerly even when not always needed
**Resolution**: Wrap in Lazy monad, evaluate on demand

### Roadblock 2: eager_default_parameter
**Issue**: Default parameter computed at function definition time
**Resolution**: Use None sentinel + lazy evaluation in function body

### Roadblock 3: eager_initialization
**Issue**: All resources initialized at startup
**Resolution**: Lazy initialization with property accessors

### Roadblock 4: evaluation_order_dependencies
**Issue**: Lazy computations have complex dependencies
**Resolution**: Chain with map/flatMap to maintain correct evaluation order

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-lazy-computation)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#optimization)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for lazy function evaluation and deferred computation*
