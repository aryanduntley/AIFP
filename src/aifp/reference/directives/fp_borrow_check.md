# Directive: fp_borrow_check

**Type**: FP
**Level**: 2
**Parent Directive**: None
**Priority**: MEDIUM - Advanced ownership validation

---

## Purpose

The `fp_borrow_check` directive **implements lightweight borrow-checking** to warn if references outlive their data source, emulating Rust-style borrow semantics in dynamic languages. This directive is **important for memory safety** because:

- **Prevents dangling references**: Ensures borrowed data remains valid
- **Validates lifetime constraints**: References don't outlive their source
- **Enables safe sharing**: Read-only borrows are safe when properly scoped
- **Catches use-after-free**: Detects references to freed/released data
- **AI-assisted safety**: Brings compile-time safety concepts to runtime checking

This directive validates:
- **Borrow lifetime** - Reference doesn't outlive data source
- **Scope boundaries** - Borrowed data valid within borrow scope
- **Closure captures** - Closures don't capture dangling references
- **Return references** - Returned references have valid lifetime
- **Multiple borrows** - Multiple read-only borrows are safe

**Safety principle**: References must not outlive the data they reference.

---

## When to Apply

This directive applies when:
- **Function returns reference** - Reference to parameter or local data
- **Closure captures data** - Lambda/closure captures external reference
- **Reference passed between scopes** - Data borrowed across function boundaries
- **During compliance checks** - `project_compliance_check` validates lifetimes
- **User requests borrow validation** - "Check borrow safety", "Validate lifetimes"
- **Advanced ownership patterns** - Complex data sharing scenarios

---

## Workflow

### Trunk: analyze_borrow_scope

Analyzes reference lifetimes and borrow scopes.

**Steps**:
1. **Trace data sources** - Identify where data is created
2. **Track references** - Map references to their sources
3. **Analyze lifetimes** - Determine if references outlive sources
4. **Route to validation** - Check borrow safety

### Branches

**Branch 1: If dangling_reference**
- **Then**: `error_borrow_violation`
- **Details**: Reference outlives its data source (dangerous)
  - Dangling reference patterns:
    ```python
    # ❌ Dangling reference (dangerous)
    def create_reference():
        local_data = [1, 2, 3]
        return local_data  # Returns reference to local
        # In languages with explicit memory management,
        # local_data would be freed, reference dangles

    # Python: GC prevents actual dangling, but pattern is unsafe
    # In C++/Rust: This would be a dangling pointer

    # ❌ Closure captures reference that will be invalid
    def create_closure():
        data = [1, 2, 3]
        def closure():
            return data  # Captures reference
        del data  # Data deleted!
        return closure()  # Dangling reference
    ```
  - Detection strategy:
    - Track variable scope and lifetime
    - Identify references that escape scope
    - Warn when reference outlives source
  - Error handling:
    ```python
    # Detect dangling reference
    if reference_escapes_scope(func):
        raise BorrowCheckError(
            f"Reference outlives data source in {func.name}",
            suggestion="Return owned data (copy) instead of reference"
        )
    ```
  - Refactoring to fix:
    ```python
    # ✅ Return copy (owned data)
    def create_data():
        local_data = [1, 2, 3]
        return local_data.copy()  # Returns copy, not reference

    # ✅ Or: Use immutable data (safe to share)
    def create_data():
        local_data = (1, 2, 3)  # Tuple (immutable)
        return local_data  # Safe to return
    ```
- **Result**: Borrow violation flagged, user warned
  - Note: Logging to notes table only occurs if `fp_flow_tracking` is enabled (disabled by default)

**Branch 2: If safe_borrow**
- **Then**: `mark_compliant`
- **Details**: Borrow is safe, reference lifetime valid
  - Safe borrow patterns:
    ```python
    # ✅ Safe borrow: Reference used within valid scope
    def process_data(data):
        # data is parameter, valid for function lifetime
        total = sum(data)  # Borrow within scope
        return total  # Returns value, not reference

    # ✅ Safe closure: Captures value, not reference
    def create_closure(value):
        def closure():
            return value * 2  # Captures value
        return closure  # Safe (value captured)

    # ✅ Safe reference: Doesn't escape scope
    def calculate(items):
        ref = items  # Reference to parameter
        result = len(ref)  # Used within scope
        return result  # Returns computed value, not ref
    ```
  - Validation criteria:
    - Reference used only within valid scope
    - Reference doesn't escape to outer scope
    - Returned values are copies or primitives
    - Closures capture values, not references
  - Update database:
    ```sql
    UPDATE functions
    SET side_effects_json = '{"borrow_safe": true}',
        updated_at = CURRENT_TIMESTAMP
    WHERE name = ? AND file_id = ?
    ```
- **Result**: Borrow validated as safe

**Branch 3: If closure_captures_reference**
- **Then**: `validate_closure_lifetime`
- **Details**: Ensure closure doesn't capture dangling reference
  - Closure capture patterns:
    ```python
    # ❌ Dangerous closure capture
    def create_adder(increment):
        temp_list = [increment]  # Local list
        def add(x):
            return x + temp_list[0]  # Captures reference to temp_list
        return add  # Closure escapes, but temp_list might be invalid

    # ✅ Safe closure: Capture value
    def create_adder(increment):
        value = increment  # Primitive value
        def add(x):
            return x + value  # Captures value (safe)
        return add

    # ✅ Safe closure: Capture immutable
    def create_processor(config):
        frozen_config = tuple(config)  # Immutable copy
        def process(data):
            return apply_config(data, frozen_config)  # Safe
        return process
    ```
  - Validation strategy:
    - Identify what closure captures
    - Check if captured data outlives closure
    - Ensure captured data is immutable or copied
  - Refactoring:
    - Capture primitives instead of references
    - Copy mutable data before capture
    - Use immutable data structures
- **Result**: Closure capture validated or fixed

**Branch 4: If returned_reference**
- **Then**: `validate_return_lifetime`
- **Details**: Ensure returned reference has valid lifetime
  - Return reference patterns:
    ```python
    # ❌ Returning reference to local (dangerous in C++)
    # Python: Safe due to GC, but pattern is anti-FP
    def get_first(items):
        if items:
            return items[0]  # Returns reference to element
        return None

    # ✅ Return copy or value
    def get_first(items):
        if items:
            # For immutable types (int, str), this is already a value
            # For mutable types, return copy
            return items[0] if is_immutable(items[0]) else copy(items[0])
        return None

    # ✅ Return new data
    def create_list():
        return [1, 2, 3]  # Returns new list (owned by caller)
    ```
  - Validation rules:
    - Returned data must be owned by caller
    - Don't return references to locals
    - Immutable returns are safe
  - Language differences:
    - **Python/JS**: GC prevents true dangling, but pattern matters
    - **Rust**: Compiler enforces lifetime rules
    - **C++**: Manual memory management, critical to check
- **Result**: Return value validated

**Branch 5: If multiple_borrows**
- **Then**: `check_aliasing`
- **Details**: Validate multiple borrows don't conflict
  - Multiple borrow patterns:
    ```python
    # ✅ Multiple read-only borrows (safe)
    def analyze_data(data):
        stats1 = calculate_mean(data)  # Read-only borrow
        stats2 = calculate_median(data)  # Read-only borrow
        stats3 = calculate_mode(data)  # Read-only borrow
        return combine(stats1, stats2, stats3)

    # ❌ Mutable and immutable borrow conflict
    def process(data):
        total = sum(data)  # Read-only borrow
        data.append(5)  # Mutable borrow - conflict!
        return total
    ```
  - Aliasing rules (Rust-inspired):
    - Multiple read-only borrows: OK
    - One mutable borrow: OK (exclusive)
    - Mutable + read-only borrow: NOT OK (conflict)
  - Validation:
    ```python
    def check_borrow_conflicts(func):
        borrows = analyze_borrows(func)
        for var, borrow_list in borrows.items():
            mutable_borrows = [b for b in borrow_list if b.is_mutable]
            readonly_borrows = [b for b in borrow_list if not b.is_mutable]

            if mutable_borrows and readonly_borrows:
                raise BorrowConflict(
                    f"Conflicting borrows of {var}: "
                    f"{len(mutable_borrows)} mutable, {len(readonly_borrows)} readonly"
                )
    ```
- **Result**: Borrow aliasing validated

**Fallback**: `prompt_user`
- **Details**: Borrow pattern unclear, user decision needed
  - Complex scenarios:
    - Nested closures with multiple captures
    - Recursive data structures
    - Async/concurrent borrows
  - Prompt example:
    ```
    Borrow lifetime unclear

    Function: create_processor
    Line 15: closure captures 'data'

    Unable to determine if 'data' remains valid
    for the lifetime of returned closure.

    Is 'data' guaranteed to outlive closure? (y/n):
    If no, recommend:
    1. Capture copy of data
    2. Use immutable data structure
    3. Accept risk (not recommended)

    Your choice (1-3):
    ```
- **Result**: User clarifies borrow safety

---

## Examples

### ✅ Compliant Usage

**Validating Safe Borrow:**
```python
# Initial code (analysis)
def calculate_statistics(data):
    # data is parameter, valid for function lifetime
    mean = sum(data) / len(data)  # Borrow within scope
    max_val = max(data)  # Borrow within scope
    min_val = min(data)  # Borrow within scope
    return {"mean": mean, "max": max_val, "min": min_val}

# AI calls: fp_borrow_check()

# Workflow:
# 1. analyze_borrow_scope:
#    - data borrowed 3 times (sum, max, min)
#    - All borrows within function scope
#    - No references escape
#
# 2. safe_borrow: mark_compliant
#    - All borrows valid
#    - Returns computed values, not references
#
# Validated code (compliant)
# No changes needed - borrow pattern is safe

# Database update
UPDATE functions
SET side_effects_json = '{"borrow_safe": true}',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'calculate_statistics';

# Result:
# ✅ Borrow pattern validated
# ✅ All references within valid scope
# ✅ No lifetime issues
```

---

**Fixing Dangling Reference:**
```python
# Initial code (non-compliant)
def create_data_reference():
    local_data = [1, 2, 3]
    return local_data  # In C++, this would dangle

def process():
    data_ref = create_data_reference()
    # In managed languages (Python/JS), this is OK (GC)
    # But pattern is anti-FP (hidden allocation)
    return sum(data_ref)

# AI calls: fp_borrow_check()

# Workflow:
# 1. analyze_borrow_scope:
#    - local_data created in function scope
#    - Reference returned to caller
#    - Potential dangling reference pattern
#
# 2. dangling_reference: error_borrow_violation
#    - Warn about pattern (even if GC safe)
#    - Recommend explicit ownership
#
# Refactored code (compliant)
# Strategy 1: Explicit copy
def create_data_copy():
    local_data = [1, 2, 3]
    return local_data.copy()  # Explicit copy

# Strategy 2: Immutable (safe to share)
def create_data_immutable():
    local_data = (1, 2, 3)  # Tuple
    return local_data  # Safe (immutable)

# Strategy 3: Document ownership transfer
def create_data_owned():
    """Creates and returns owned data."""
    return [1, 2, 3]  # Caller owns data

# Result:
# ✅ Ownership explicit
# ✅ No dangling reference risk
# ✅ Clear data ownership semantics
# Note: Analysis may be logged if fp_flow_tracking is enabled (disabled by default)
```

---

**Validating Closure Captures:**
```python
# Initial code (analysis)
def create_multiplier(factor):
    # factor is parameter, captured by closure
    def multiply(x):
        return x * factor  # Captures factor
    return multiply

multiplier = create_multiplier(5)
result = multiplier(10)  # Uses captured factor

# AI calls: fp_borrow_check()

# Workflow:
# 1. analyze_borrow_scope:
#    - Closure captures 'factor'
#    - factor is primitive (int)
#
# 2. closure_captures_reference: validate_closure_lifetime
#    - factor is primitive value (copied, not referenced)
#    - Safe to capture
#
# Validated code (compliant)
# No changes needed - primitive capture is safe

# Result:
# ✅ Closure capture safe (value, not reference)
# ✅ No lifetime issues
```

---

**Fixing Unsafe Closure:**
```python
# Initial code (non-compliant)
def create_processor(config):
    temp_data = list(config)  # Mutable list
    def process(x):
        return x in temp_data  # Captures reference to temp_data
    return process
    # temp_data lifetime ends, but closure still references it

# AI calls: fp_borrow_check()

# Workflow:
# 1. analyze_borrow_scope:
#    - Closure captures temp_data (mutable list)
#    - temp_data local to create_processor
#    - Closure escapes, temp_data might be invalid
#
# 2. closure_captures_reference: validate_closure_lifetime
#    - Unsafe: mutable reference captured
#    - Recommend immutable capture
#
# Refactored code (compliant)
def create_processor(config):
    # Freeze data (immutable)
    frozen_data = tuple(config)  # Immutable tuple
    def process(x):
        return x in frozen_data  # Safe capture
    return process

# Or: Copy at capture time
def create_processor(config):
    data_copy = list(config)  # Copy
    def process(x):
        return x in data_copy  # Captures copy (safe)
    return process

# Result:
# ✅ Closure captures immutable or copy
# ✅ No dangling reference
# ✅ Safe lifetime
```

---

### ❌ Non-Compliant Usage

**Returning Reference to Local:**
```python
# ❌ Returns reference to local (anti-pattern)
def create_buffer():
    buffer = []
    for i in range(10):
        buffer.append(i)
    return buffer  # Pattern suggests local ownership issue

# Why Non-Compliant:
# - In C++, buffer would be freed (dangling pointer)
# - In Python, GC saves us, but pattern is unclear
# - Ownership semantics ambiguous
```

**Corrected:**
```python
# ✅ Clear ownership transfer
def create_buffer():
    """Creates and returns new buffer (caller owns)."""
    return [i for i in range(10)]  # Ownership explicit
```

---

## Edge Cases

### Edge Case 1: Iterator Invalidation

**Issue**: Iterator invalidated by mutation

**Handling**:
```python
# ❌ Iterator invalidation
items = [1, 2, 3]
for item in items:
    if item == 2:
        items.remove(item)  # Mutates during iteration!

# ✅ Fixed: Iterate over copy
items = [1, 2, 3]
for item in items.copy():
    if item == 2:
        items.remove(item)
```

**Directive Action**: Warn about mutation during iteration.

---

### Edge Case 2: Async/Await Lifetime

**Issue**: Reference lifetime across await points

**Handling**:
```python
# ❌ Potential issue
async def process(data):
    ref = data[0]  # Reference to element
    await async_operation()  # Suspension point
    return ref  # ref might be invalid if data changed

# ✅ Copy before await
async def process(data):
    value = data[0]  # Copy value
    await async_operation()
    return value  # Safe
```

**Directive Action**: Warn about borrows across await.

---

### Edge Case 3: Weakref/Finalizer

**Issue**: Weak reference might become invalid

**Handling**:
```python
import weakref

# ❌ Weakref might be None
obj = SomeObject()
weak = weakref.ref(obj)

def use_weakref():
    return weak().value  # weak() might return None!

# ✅ Check validity
def use_weakref():
    obj = weak()
    if obj is None:
        raise ValueError("Object no longer exists")
    return obj.value
```

**Directive Action**: Enforce None checks for weak references.

---

## Related Directives

- **Called By**:
  - `fp_ownership_safety` - Validates borrow safety
  - `project_compliance_check` - Scans borrow patterns
- **Calls**:
  - Database helpers - Updates functions table
  - `project_notes_log` - Logs lifetime issues
- **Related**:
  - `fp_immutability` - Immutable data enables safe borrowing
  - `fp_concurrency_safety` - Borrow safety critical for concurrency

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: UPDATE side_effects_json with borrow_safe flag
- **`notes`**: INSERT borrow violations and lifetime warnings (only if `fp_flow_tracking` enabled - disabled by default)

---

## Testing

1. **Detect dangling reference** → Reference outlives source
   ```python
   def bad_func():
       local = [1, 2, 3]
       return local  # Pattern suggests dangling

   escaped = detect_escaped_references(bad_func)
   assert len(escaped) > 0
   ```

2. **Validate safe borrow** → All references within scope
   ```python
   def safe_func(data):
       return sum(data)

   result = fp_borrow_check(safe_func)
   assert result.borrow_safe == True
   ```

3. **Closure capture check** → Validates what closure captures
   ```python
   def create_closure():
       data = [1, 2, 3]
       return lambda: data

   valid = validate_closure_captures(create_closure())
   assert valid == True or valid == False  # Depends on data type
   ```

---

## Common Mistakes

- ❌ **Not checking return references** - Returned refs might outlive data
- ❌ **Ignoring closure captures** - Closures can capture dangling refs
- ❌ **Assuming GC solves everything** - Pattern still matters for reasoning
- ❌ **Not validating iterator lifetime** - Mutation during iteration

---

## Roadblocks and Resolutions

### Roadblock 1: dangling_reference
**Issue**: Reference outlives data source
**Resolution**: Use copy or shorter scope

### Roadblock 2: borrow_lifetime_conflict
**Issue**: Unclear if reference valid for required lifetime
**Resolution**: Restructure code for ownership clarity

---

## References

None
---

*Part of AIFP v1.0 - Advanced FP directive for borrow checking and lifetime validation*
