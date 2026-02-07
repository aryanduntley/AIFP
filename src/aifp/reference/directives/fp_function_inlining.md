# Directive: fp_function_inlining

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: LOW - Micro-optimization

---

## Purpose

The `fp_function_inlining` directive identifies trivial or single-call functions and inlines them into their call sites when beneficial. Inlining eliminates function call overhead for small pure functions while maintaining code correctness and readability.

Function inlining provides **micro-optimization benefits**, enabling:
- **Reduced Call Overhead**: Eliminate function call/return costs
- **Better Compiler Optimization**: Enable further optimizations across inline boundaries
- **Reduced Stack Usage**: Fewer stack frames for simple operations
- **Performance**: Faster execution for hot paths with trivial functions
- **Maintained Purity**: Inlining doesn't change behavior (for pure functions)

This directive is **conservative** - it only inlines when clearly beneficial and doesn't harm readability. Unlike imperative inlining, FP inlining is **always safe** for pure functions (referential transparency).

**Important**: This directive is reference documentation for function inlining optimization patterns.
AI consults this when uncertain about inlining decisions or complex inlining scenarios.

**FP function inlining is baseline behavior**:
- AI applies function inlining naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about whether to inline specific functions
- Complex inlining scenarios (recursive functions, closures, hot paths)
- Edge cases with code size vs performance tradeoffs
- Need for detailed guidance on inlining decisions

**Context**:
- AI applies function inlining as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_constant_folding`, `fp_purity`) may reference this for guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: analyze_call_graph

Analyzes function call graph to identify inlining opportunities.

**Steps**:
1. **Build call graph** - Map all function calls in codebase
2. **Identify trivial functions** - Functions with 1-3 simple operations
3. **Count call sites** - Determine how many times each function called
4. **Measure function size** - Estimate cost of inlining vs calling
5. **Analyze hot paths** - Identify performance-critical call sites
6. **Evaluate inlining benefit** - Classify as inline-candidate, keep-as-is, or uncertain

### Branches

**Branch 1: If trivial_single_call_function**
- **Then**: `inline_function`
- **Details**: Inline function called only once
  - Replace call site with function body
  - Substitute parameters with arguments
  - Eliminate function definition
  - Reduce code size and call overhead
- **Result**: Returns inlined code

**Branch 2: If hot_path_micro_function**
- **Then**: `inline_in_hot_path`
- **Details**: Inline small function in performance-critical loop
  - Keep function definition (may be called elsewhere)
  - Inline at hot path call sites only
  - Preserve function for readability elsewhere
  - Targeted optimization for performance
- **Result**: Returns selectively inlined code

**Branch 3: If trivial_wrapper**
- **Then**: `inline_wrapper`
- **Details**: Inline function that just wraps another function
  - Replace `def wrapper(x): return target(x)` calls with direct `target(x)` calls
  - Eliminate unnecessary indirection
  - Keep target function
- **Result**: Returns unwrapped calls

**Branch 4: If constant_function**
- **Then**: `replace_with_constant`
- **Details**: Replace function calls with constant value
  - `def get_max(): return 100` → replace `get_max()` with `100`
  - Stronger than inlining (removes function entirely)
  - See `fp_constant_folding` for related optimizations
- **Result**: Returns constant values

**Branch 5: If keep_as_function**
- **Then**: `document_rationale`
- **Details**: Don't inline - maintain as function
  - Function provides important abstraction
  - Improves readability
  - Called multiple times (inlining would increase code size)
  - Not performance-critical
- **Result**: Function kept separate

**Fallback**: `prompt_user`
- **Details**: Uncertain about inlining
  - Present analysis (call count, size, performance impact)
  - Ask: "Inline this function?"
  - Consider readability vs performance tradeoff
- **Result**: User decides

---

## Examples

### ✅ Compliant Code

**Kept as Function (Passes):**
```python
def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate Euclidean distance between two points.

    KEPT AS FUNCTION BECAUSE:
    - Called 15 times (inlining would increase code size)
    - Provides clear abstraction (readability)
    - Not in hot path (not performance-critical)
    - Complexity justifies function (sqrt, multiple operations)
    """
    dx = x2 - x1
    dy = y2 - y1
    return (dx * dx + dy * dy) ** 0.5

# Called multiple times
dist1 = calculate_distance(0, 0, 3, 4)
dist2 = calculate_distance(1, 1, 4, 5)
# ... 13 more calls

# VERDICT: Keep as function (abstraction + reuse)
```

**Why Compliant**:
- Function called multiple times
- Provides valuable abstraction
- Inlining would increase code size
- Readability benefit outweighs performance cost

---

**Inlined Trivial Function (Passes):**
```python
# BEFORE: Single-use trivial helper
def double(x: int) -> int:
    """Double a number (trivial, single-use)."""
    return x * 2

def process_value(value: int) -> int:
    """Process value."""
    doubled = double(value)  # Only call site
    return doubled + 10

# AFTER: Inlined (call overhead eliminated)
def process_value(value: int) -> int:
    """Process value."""
    doubled = value * 2  # Inlined (no function call)
    return doubled + 10

# VERDICT: Inline (trivial + single use)
```

**Why Compliant**:
- Function called only once
- Trivial operation (just x * 2)
- No abstraction value
- Inlining improves performance without readability loss

---

**Selectively Inlined in Hot Path (Passes):**
```python
def is_even(n: int) -> bool:
    """Check if number is even."""
    return n % 2 == 0

# BEFORE: Function call in hot loop
def count_even_numbers(numbers: list[int]) -> int:
    """Count even numbers (hot path)."""
    count = 0
    for num in numbers:  # Hot loop (millions of iterations)
        if is_even(num):  # Function call overhead
            count += 1
    return count

# AFTER: Inlined in hot path only
def count_even_numbers(numbers: list[int]) -> int:
    """Count even numbers (optimized)."""
    count = 0
    for num in numbers:  # Hot loop
        if num % 2 == 0:  # Inlined (no call overhead)
            count += 1
    return count

# is_even() kept elsewhere for readability
user_input = get_user_number()
if is_even(user_input):  # Not inlined (not hot path, readability value)
    print("Even number entered")

# VERDICT: Selective inlining (performance-critical path only)
```

**Why Compliant**:
- Inlined only in hot path
- Function kept for readability elsewhere
- Targeted optimization
- Best of both worlds

---

### ❌ Non-Compliant Code

**Overly Aggressive Inlining (Violation):**
```python
# ❌ VIOLATION: Inlining complex function called many times
# BEFORE:
def validate_email(email: str) -> bool:
    """Validate email format (complex logic)."""
    if not email:
        return False
    if '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    if '.' not in parts[1]:
        return False
    return True

# ❌ AFTER: Inlined everywhere (BAD)
def register_user(email: str):
    # Inlined validation (repeated code!)
    if not email:
        return False
    if '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    if '.' not in parts[1]:
        return False
    # ... rest of registration

def update_email(email: str):
    # Same validation inlined again!
    if not email:
        return False
    if '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    if '.' not in parts[1]:
        return False
    # ... rest of update

# Problem:
# - Code duplication (increases size)
# - Maintenance burden (change validation in 10+ places)
# - Loss of abstraction
# - No performance benefit (not in hot path)
```

**Why Non-Compliant**:
- Complex function inlined (not trivial)
- Called many times (code bloat)
- Loses abstraction
- Maintenance nightmare
- No performance benefit

**Resolution**: Keep as function:
```python
# ✅ FIXED: Keep as function (abstraction value)
def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    if '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    if '.' not in parts[1]:
        return False
    return True

def register_user(email: str):
    if not validate_email(email):  # Function call (clear abstraction)
        return False
    # ... rest

def update_email(email: str):
    if not validate_email(email):  # Reused function
        return False
    # ... rest
```

---

**Inlining for Premature Optimization (Violation):**
```python
# ❌ VIOLATION: Inlining without profiling
# BEFORE:
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# ❌ AFTER: Inlined everywhere (premature optimization)
def calculate_total(items: list[int]) -> int:
    """Calculate total."""
    total = 0
    for item in items:
        total = total + item  # Inlined add() - but why?
    return total

# Problem:
# - No evidence function call was bottleneck
# - Function call overhead negligible for add()
# - Lost abstraction for no proven benefit
# - Premature optimization
```

**Why Non-Compliant**:
- No profiling showing bottleneck
- Trivial function but not in hot path
- Lost abstraction for no benefit
- Premature optimization

**Resolution**: Keep function unless profiling shows benefit:
```python
# ✅ FIXED: Keep function (no proven bottleneck)
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def calculate_total(items: list[int]) -> int:
    """Calculate total."""
    total = 0
    for item in items:
        total = add(total, item)  # Keep function call
    return total

# Profile first, optimize if proven bottleneck
```

---

## Edge Cases

### Edge Case 1: Inlining with Side Effects

**Issue**: Inlining impure function changes behavior

**Handling**:
```python
# ❌ Bad: Inlining function with side effects (changes behavior!)
# BEFORE:
call_count = 0

def log_and_increment(x: int) -> int:
    global call_count
    call_count += 1
    print(f"Call #{call_count}: {x}")
    return x + 1

result = log_and_increment(5) + log_and_increment(5)

# ❌ AFTER: Inlined (WRONG - changes behavior)
call_count = 0
result = (call_count := call_count + 1, print(f"Call #{call_count}: 5"), 5 + 1)[2] + \
         (call_count := call_count + 1, print(f"Call #{call_count}: 5"), 5 + 1)[2]
# Evaluation order may change, side effects may execute differently

# ✅ Good: DON'T inline impure functions
# Keep function as-is (side effects require function boundary)
```

**Directive Action**: NEVER inline impure functions (violates `fp_purity`).

---

### Edge Case 2: Inlining with Type Complexity

**Issue**: Inlining loses type information

**Handling**:
```python
# BEFORE:
def cast_to_user(data: dict) -> User:
    """Cast dict to User type (type annotation value)."""
    return User(**data)

# Keep as function (type annotation provides documentation value)
user = cast_to_user({"name": "Alice", "email": "alice@example.com"})

# DON'T inline:
# user = User(**{"name": "Alice", "email": "alice@example.com"})
# (loses type documentation)
```

**Directive Action**: Keep function when type annotation provides documentation value.

---

### Edge Case 3: Recursive Functions

**Issue**: Can't inline recursive functions

**Handling**:
```python
# Recursive function cannot be inlined
def factorial(n: int) -> int:
    """Calculate factorial recursively."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)  # Recursive call

# NEVER inline recursive functions (infinite expansion)
```

**Directive Action**: Never inline recursive functions.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Only inline pure functions (impure inlining changes behavior)
- **Triggers**:
  - `fp_constant_folding` - May follow inlining to evaluate constants
- **Called By**:
  - `project_compliance_check` - Performance optimization audits
- **Conflicts With**:
  - Readability goals - Conservative approach to preserve abstractions
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `optimization_level = 'inlined'` for inlined functions

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

1. **Trivial single-use function** → Directive suggests inlining
   ```python
   # Input
   def double(x): return x * 2
   result = double(5)  # Only call

   # Suggested: Inline to result = 5 * 2
   ```

2. **Complex multi-use function** → Directive keeps as function
   ```python
   def complex_calc(x, y, z): # ... 20 lines
   # Multiple call sites

   # Kept as function (complexity + reuse)
   ```

3. **Check database** → Verify inlining decisions logged
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Common Mistakes

- ❌ **Inlining complex functions** - Loses abstraction, increases code size
- ❌ **Inlining impure functions** - Changes behavior (side effect ordering)
- ❌ **Inlining without profiling** - Premature optimization
- ❌ **Inlining recursive functions** - Impossible (infinite expansion)
- ❌ **Over-inlining for micro-optimizations** - Compiler often does this automatically

---

## Roadblocks and Resolutions

### Roadblock 1: complex_function
**Issue**: Function too complex to inline without readability loss
**Resolution**: Keep as function, document abstraction value

### Roadblock 2: impure_function
**Issue**: Function has side effects, inlining would change behavior
**Resolution**: Never inline impure functions (consult `fp_purity`)

### Roadblock 3: compiler_already_inlines
**Issue**: Modern compilers inline trivial functions automatically
**Resolution**: Document that optimization may be redundant, let compiler decide

### Roadblock 4: recursive_function
**Issue**: Recursive function cannot be inlined
**Resolution**: Keep as recursive function, mark as non-inlinable

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for safe function inlining optimization*
