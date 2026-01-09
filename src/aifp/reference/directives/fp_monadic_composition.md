# Directive: fp_monadic_composition

**Type**: FP Auxiliary
**Level**: 1 (Core Pattern)
**Parent Directive**: None
**Priority**: HIGH - Essential FP composition pattern

---

## Purpose

The `fp_monadic_composition` directive enforces the use of monadic bind/flatMap operations to chain functions that return Result/Option types, enabling composable error handling without nested if-checks. This directive provides **monad-based composition** that eliminates callback hell and enables declarative error pipelines.

Monadic composition provides **composable error handling**, enabling:
- **No Nested If-Checks**: Flat, linear error handling chains
- **Composability**: Chain fallible operations elegantly
- **Early Return Pattern**: Automatic short-circuiting on errors
- **Type Safety**: Compiler enforces error handling
- **Railway-Oriented Programming**: Success/failure tracks cleanly separated

This directive acts as a **composition enabler** transforming nested error handling into flat monadic pipelines.

**Important**: This directive is reference documentation for monadic composition patterns.
AI consults this when uncertain about flattening nested Result/Option chains or complex monad composition scenarios.

**FP monadic composition is baseline behavior**:
- AI writes monadic compositions naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about flattening nested Result/Option checks
- Complex monad composition scenarios (multiple flatMaps)
- Edge cases with mixed monad types or async/sync operations
- Need for detailed guidance on monadic error handling patterns

**Context**:
- AI writes monadic compositions as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_result_types`, `fp_optionals`, `fp_error_pipeline`) may reference this for guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: analyze_function_composition

Scans code for nested Result/Option handling and converts to flat monadic chains.

**Steps**:
1. **Detect fallible functions** - Find functions returning Result/Option
2. **Analyze call chains** - Identify sequential dependent calls
3. **Detect nested error checks** - Find nested if-checks for errors
4. **Design monadic chain** - Convert to flatMap/bind pipeline
5. **Generate composition** - Create monadic pipeline code
6. **Verify types** - Ensure type safety throughout chain

### Branches

**Branch 1: If error_handling_chain_detected**
- **Then**: `apply_monadic_composition`
- **Details**: Multiple fallible operations chained with error checks
  - Pattern: Nested if-checks for Result values
  - Convert to flatMap chain
  - Flatten nested structure
  - Automatic error propagation
- **Result**: Returns monadic pipeline

**Branch 2: If nested_option_result**
- **Then**: `flatten_with_bind`
- **Details**: Nested Option/Result types (Result[Option[T]])
  - Use bind/flatMap to flatten
  - Avoid nested type complexity
  - Clean composition
- **Result**: Returns flattened monad chain

**Branch 3: If already_monadic**
- **Then**: `mark_compliant`
- **Details**: Already using monadic composition
  - Code uses flatMap/bind
  - No nested error checks
  - Composable pipeline
- **Result**: Code passes check

**Branch 4: If low_confidence**
- **Then**: `prompt_user`
- **Details**: Unclear if monadic composition applies
  - Complex control flow
  - Mixed synchronous/asynchronous
  - Ask user for clarification
- **Result**: User provides guidance

**Fallback**: `prompt_user`
- **Details**: Complex composition pattern
  - Multiple error types
  - Non-linear dependencies
  - Ask user for approach
- **Result**: User decides strategy

---

## Examples

### ✅ Compliant Code

**Monadic Pipeline with flatMap (Passes):**

```python
# Python - monadic composition with flatMap

class Result:
    """Result monad with flatMap"""
    def flatMap(self, func):
        if isinstance(self, Ok):
            return func(self.value)
        return self  # Propagate error

class Ok(Result):
    def __init__(self, value):
        self.value = value

class Err(Result):
    def __init__(self, error):
        self.error = error

def parse_int(text: str) -> Result:
    """Parse string to integer."""
    try:
        return Ok(int(text))
    except ValueError:
        return Err(f"Not an integer: {text}")

def validate_positive(n: int) -> Result:
    """Validate number is positive."""
    if n > 0:
        return Ok(n)
    return Err(f"Not positive: {n}")

def calculate_square_root(n: int) -> Result:
    """Calculate square root."""
    import math
    return Ok(math.sqrt(n))

# ✅ Compliant: Monadic composition with flatMap
def process_number(text: str) -> Result:
    """
    Parse, validate, and calculate square root.

    Monadic composition - no nested if-checks.
    """
    return (
        parse_int(text)
        .flatMap(validate_positive)
        .flatMap(calculate_square_root)
    )

# Usage
result = process_number("16")
if isinstance(result, Ok):
    print(f"Result: {result.value}")  # 4.0
else:
    print(f"Error: {result.error}")
```

**Why Compliant**:
- Flat monadic composition
- No nested if-checks
- Automatic error propagation
- Clean pipeline structure

---

**Option Monad with bind (Passes):**

```python
# Option monad with monadic composition

class Option:
    """Option monad with bind/flatMap"""
    def bind(self, func):
        """Monadic bind (flatMap)"""
        if isinstance(self, Some):
            return func(self.value)
        return self  # Propagate None

class Some(Option):
    def __init__(self, value):
        self.value = value

class Nothing(Option):
    pass

def find_user(user_id: int) -> Option:
    """Find user by ID."""
    users = {1: {'name': 'Alice', 'email': 'alice@example.com'}}
    if user_id in users:
        return Some(users[user_id])
    return Nothing()

def get_email(user: dict) -> Option:
    """Extract email from user."""
    if 'email' in user:
        return Some(user['email'])
    return Nothing()

def validate_email(email: str) -> Option:
    """Validate email format."""
    if '@' in email and '.' in email.split('@')[1]:
        return Some(email)
    return Nothing()

# ✅ Compliant: Monadic composition with bind
def get_validated_email(user_id: int) -> Option:
    """
    Get validated email for user.

    Monadic composition - flat and composable.
    """
    return (
        find_user(user_id)
        .bind(get_email)
        .bind(validate_email)
    )

# Usage
result = get_validated_email(1)
if isinstance(result, Some):
    print(f"Email: {result.value}")
else:
    print("No valid email found")
```

**Why Compliant**:
- Option monad with bind
- No nested None checks
- Composable pipeline
- Clear data flow

---

### ❌ Non-Compliant Code

**Nested Error Checking (Violation):**

```python
# ❌ VIOLATION: Nested if-checks for error handling

def parse_int(text: str) -> Result:
    """Parse string to integer."""
    try:
        return Ok(int(text))
    except ValueError:
        return Err(f"Not an integer: {text}")

def validate_positive(n: int) -> Result:
    """Validate number is positive."""
    if n > 0:
        return Ok(n)
    return Err(f"Not positive: {n}")

def calculate_square_root(n: int) -> Result:
    """Calculate square root."""
    import math
    return Ok(math.sqrt(n))

# ❌ VIOLATION: Nested error checking
def process_number(text: str) -> Result:
    """Process number with nested checks."""
    result1 = parse_int(text)
    if isinstance(result1, Err):  # ← Nested check 1
        return result1

    num = result1.value
    result2 = validate_positive(num)
    if isinstance(result2, Err):  # ← Nested check 2
        return result2

    validated = result2.value
    result3 = calculate_square_root(validated)
    if isinstance(result3, Err):  # ← Nested check 3
        return result3

    return result3

# Problem:
# - Three levels of nested if-checks
# - Repetitive error propagation
# - Not composable
# - Hard to add new steps
# - Should use monadic composition
```

**Why Non-Compliant**:
- Nested if-checks for each step
- Manual error propagation
- Not composable
- Should use flatMap

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Monadic composition
def process_number(text: str) -> Result:
    """
    Process number with monadic composition.

    Flat, composable, automatic error propagation.
    """
    return (
        parse_int(text)
        .flatMap(validate_positive)
        .flatMap(calculate_square_root)
    )

# Clean, flat, composable
# Easy to add new steps
# Automatic error handling
```

---

**Nested None Checks (Violation):**

```python
# ❌ VIOLATION: Nested None checks for Option

def find_user(user_id: int) -> Option:
    """Find user."""
    users = {1: {'name': 'Alice', 'email': 'alice@example.com'}}
    if user_id in users:
        return Some(users[user_id])
    return Nothing()

def get_email(user: dict) -> Option:
    """Get email."""
    if 'email' in user:
        return Some(user['email'])
    return Nothing()

def validate_email(email: str) -> Option:
    """Validate email."""
    if '@' in email:
        return Some(email)
    return Nothing()

# ❌ VIOLATION: Nested None checking
def get_validated_email(user_id: int) -> Option:
    """Get validated email with nested checks."""
    user_result = find_user(user_id)
    if isinstance(user_result, Nothing):  # ← Nested check 1
        return Nothing()

    user = user_result.value
    email_result = get_email(user)
    if isinstance(email_result, Nothing):  # ← Nested check 2
        return Nothing()

    email = email_result.value
    validated = validate_email(email)
    if isinstance(validated, Nothing):  # ← Nested check 3
        return Nothing()

    return validated

# Problem:
# - Nested None checks
# - Manual propagation
# - Not composable
# - Should use monadic bind
```

**Why Non-Compliant**:
- Manual None checking
- Nested structure
- Not composable
- Should use bind/flatMap

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Monadic composition with bind
def get_validated_email(user_id: int) -> Option:
    """
    Get validated email with monadic composition.

    Flat, composable, automatic None propagation.
    """
    return (
        find_user(user_id)
        .bind(get_email)
        .bind(validate_email)
    )

# Clean and composable
```

---

**Mixed Error Handling Styles (Violation):**

```python
# ❌ VIOLATION: Mix of monadic and imperative error handling

def step1(x: int) -> Result:
    """Step 1."""
    return Ok(x * 2)

def step2(x: int) -> Result:
    """Step 2."""
    return Ok(x + 10)

def step3(x: int) -> Result:
    """Step 3."""
    if x > 100:
        return Err("Too large")
    return Ok(x)

# ❌ VIOLATION: Inconsistent error handling
def process(x: int) -> Result:
    """Process with mixed styles."""
    # Some monadic composition
    result = step1(x).flatMap(step2)

    # Then imperative check ← Inconsistent!
    if isinstance(result, Err):
        return result

    # Then monadic again
    return step3(result.value)

# Problem:
# - Mixes monadic and imperative styles
# - Inconsistent pattern
# - Should be fully monadic
```

**Why Non-Compliant**:
- Inconsistent error handling
- Mixes styles
- Should be fully monadic

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Consistent monadic composition
def process(x: int) -> Result:
    """
    Process with consistent monadic composition.

    All steps use flatMap - consistent style.
    """
    return (
        step1(x)
        .flatMap(step2)
        .flatMap(step3)
    )

# Consistent, clean, composable
```

---

## Edge Cases

### Edge Case 1: Multiple Error Types

**Issue**: Different functions return different error types

**Handling**:
```python
# Use unified error type or error conversion

class AppError:
    """Unified error type"""
    def __init__(self, message: str, error_type: str):
        self.message = message
        self.error_type = error_type

def parse_int(text: str) -> Result[int, AppError]:
    """Parse with unified error type."""
    try:
        return Ok(int(text))
    except ValueError:
        return Err(AppError(f"Parse error: {text}", "ParseError"))

def validate_range(n: int, min_val: int, max_val: int) -> Result[int, AppError]:
    """Validate with unified error type."""
    if min_val <= n <= max_val:
        return Ok(n)
    return Err(AppError(f"Out of range: {n}", "ValidationError"))

# ✅ Monadic composition with unified error type
def process(text: str) -> Result[int, AppError]:
    """Process with consistent error type."""
    return (
        parse_int(text)
        .flatMap(lambda n: validate_range(n, 0, 100))
    )
```

**Directive Action**: Use unified error type or convert errors at boundaries.

---

### Edge Case 2: Mixing Sync and Async

**Issue**: Some operations are async (return Promise/Future)

**Handling**:
```python
# Use async monad composition

class AsyncResult:
    """Async Result monad"""
    def __init__(self, future):
        self.future = future

    async def flatMap(self, func):
        """Async flatMap"""
        value = await self.future
        if isinstance(value, Err):
            return value
        return await func(value.value).future

# ✅ Async monadic composition
async def process_async(text: str) -> Result:
    """Process with async monadic composition."""
    return await (
        AsyncResult(parse_int_async(text))
        .flatMap(validate_async)
        .flatMap(calculate_async)
    )
```

**Directive Action**: Use async-aware monads for asynchronous operations.

---

### Edge Case 3: Accumulating Multiple Errors

**Issue**: Want to collect all errors, not stop at first

**Handling**:
```python
# Use Validation applicative instead of Result monad

class Validation:
    """Validation applicative - accumulates errors"""
    pass

class Valid(Validation):
    def __init__(self, value):
        self.value = value

class Invalid(Validation):
    def __init__(self, errors):
        self.errors = errors  # List of errors

# Applicative composition (not monadic)
def validate_all(data: dict) -> Validation:
    """Validate all fields, accumulate errors."""
    errors = []

    if 'name' not in data or not data['name']:
        errors.append("Name is required")

    if 'age' not in data or data['age'] < 0:
        errors.append("Age must be positive")

    if 'email' not in data or '@' not in data['email']:
        errors.append("Email is invalid")

    if errors:
        return Invalid(errors)

    return Valid(data)

# Note: This is applicative, not monadic
# Monads short-circuit, applicatives accumulate
```

**Directive Action**: Use Validation applicative for error accumulation (not monad).

---

## Monad Laws

### Law 1: Left Identity
```python
# return a >>= f  ≡  f a

# In code:
Ok(5).flatMap(lambda x: Ok(x * 2))
# Should equal:
Ok(5 * 2)
```

### Law 2: Right Identity
```python
# m >>= return  ≡  m

# In code:
Ok(5).flatMap(lambda x: Ok(x))
# Should equal:
Ok(5)
```

### Law 3: Associativity
```python
# (m >>= f) >>= g  ≡  m >>= (\x -> f x >>= g)

# In code:
Ok(5).flatMap(f).flatMap(g)
# Should equal:
Ok(5).flatMap(lambda x: f(x).flatMap(g))
```

---

## Common Monadic Operations

### flatMap / bind
```python
# Chain operations that return monads
result.flatMap(func)
```

### map
```python
# Transform value inside monad
result.map(lambda x: x * 2)
```

### getOrElse
```python
# Extract value or provide default
result.getOrElse(default_value)
```

### fold
```python
# Handle both success and failure cases
result.fold(
    on_error=lambda e: handle_error(e),
    on_success=lambda v: handle_success(v)
)
```

---

## Related Directives

- **Depends On**:
  - `fp_result_types` - Uses Result monad
  - `fp_optionals` - Uses Option monad
- **Triggers**:
  - `fp_error_pipeline` - Build error handling pipelines
- **Called By**:
  - `project_file_write` - Apply monadic composition
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `uses_monadic_composition = 1` for monadic functions
- **`interactions`**: Records monad composition chains

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

1. **Nested checks detected** → Directive converts to flatMap
   ```python
   # Before: if isinstance(r1, Err): return r1; if isinstance(r2, Err): return r2
   # After: r1.flatMap(f1).flatMap(f2)
   ```

2. **Monadic composition used** → Clean pipeline
   ```python
   result = op1(x).flatMap(op2).flatMap(op3)
   # Flat, composable, automatic error propagation
   ```

3. **Check database** → Verify monadic usage marked
   ```sql
   SELECT name, uses_monadic_composition
   FROM functions
   WHERE uses_monadic_composition = 1;
   ```

---

## Common Mistakes

- ❌ **Nested if-checks for Result/Option** - Not composable
- ❌ **Manual error propagation** - Repetitive and error-prone
- ❌ **Not using flatMap/bind** - Misses monadic benefits
- ❌ **Mixing monadic and imperative styles** - Inconsistent
- ❌ **Not implementing monad laws** - Invalid monad

---

## Roadblocks and Resolutions

### Roadblock 1: nested_error_handling
**Issue**: Multiple nested if-checks for error propagation
**Resolution**: Convert to monadic flatMap/bind chain

### Roadblock 2: mixed_monad_types
**Issue**: Different monad types in composition
**Resolution**: Convert to single monad type or use monad transformers

### Roadblock 3: async_sync_mix
**Issue**: Mix of synchronous and asynchronous operations
**Resolution**: Use async-aware monads or convert to consistent style

### Roadblock 4: multiple_error_accumulation
**Issue**: Need to collect multiple errors (not short-circuit)
**Resolution**: Use Validation applicative instead of Result monad

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for monadic function composition*
