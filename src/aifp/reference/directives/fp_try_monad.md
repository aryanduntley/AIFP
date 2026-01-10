# Directive: fp_try_monad

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Specialized Result type

---

## Purpose

The `fp_try_monad` directive encourages safe evaluation of code that may fail by wrapping potentially dangerous operations in Try monads. Try is a specialized form of Result that captures exceptions and converts them to Success/Failure values, enabling **exception-free error handling** while maintaining compatibility with exception-throwing code.

Try monads provide a **bridge between exception-based and functional error handling**, enabling:
- **Exception Capture**: Automatically catches exceptions and wraps in Failure
- **Safe Evaluation**: Risky operations evaluated safely without try/catch
- **Composability**: Try values chain with map/flatMap like Result
- **Gradual Migration**: Convert exception code incrementally
- **No Surprises**: All failures explicit in Try type

This directive complements `fp_result_types` (explicit error returns) by providing a way to **wrap exception-throwing code** from legacy systems or third-party libraries in functional error handling.

**Important**: This directive is reference documentation for Try monad patterns.
AI consults this when uncertain about wrapping exceptions or complex Try monad scenarios.

**FP Try monads are baseline behavior**:
- AI uses Try monads naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about wrapping exception-throwing code in Try monads
- Complex Try monad scenarios (nested exceptions, exception translation)
- Edge cases with mixed exception/Result error handling
- Need for detailed guidance on exception capture patterns

**Context**:
- AI uses Try monads as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_result_types`, `fp_error_pipeline`) may reference this for guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow (continuing from header)
  - `project_file_write` - Validates Try usage for risky operations
  - `project_compliance_check` - Scans for unsafe operation wrapping
  - Works with `fp_result_types` - Try is specialized Result for exceptions

---

## Workflow

### Trunk: identify_risky_calls

Scans code to detect operations that might throw exceptions and should be wrapped in Try.

**Steps**:
1. **Parse function body** - Build AST for analysis
2. **Identify exception-prone operations** - Division, parsing, type conversion, I/O
3. **Identify external library calls** - Third-party functions that might throw
4. **Identify explicit throws** - `raise`, `throw` statements
5. **Identify try/catch blocks** - Imperative exception handling
6. **Evaluate compliance** - Classify as Try-wrapped, unchecked, or uncertain

### Branches

**Branch 1: If unchecked_operation**
- **Then**: `wrap_in_try_monad`
- **Details**: Wrap risky operation in Try for safe evaluation
  - Replace `int(s)` with `Try(lambda: int(s))`
  - Replace `a / b` with `Try(lambda: a / b)`
  - Replace `file.read()` with `Try(lambda: file.read())`
  - Returns Success(value) or Failure(exception)
- **Result**: Returns code with Try-wrapped operations

**Branch 2: If explicit_throw**
- **Then**: `replace_with_try`
- **Details**: Convert throw statement to Try.failure
  - Replace `raise ValueError("msg")` with `return Try.failure(ValueError("msg"))`
  - Replace `throw new Error("msg")` with `return Try.failure(Error("msg"))`
  - Update function signature to return Try[T]
- **Result**: Returns exception-free code with Try

**Branch 3: If try_catch_block**
- **Then**: `convert_to_try_monad`
- **Details**: Convert try/catch to Try-based evaluation
  - Extract try block into lambda
  - Wrap in Try monad
  - Remove catch block (Try handles automatically)
  - Chain with map/flatMap if needed
- **Result**: Returns declarative Try-based code

**Branch 4: If safe**
- **Then**: `mark_safe`
- **Details**: Operation cannot fail or already wrapped
  - Pure calculation with no failure modes
  - Already using Try monad correctly
  - Mark as compliant
- **Result**: Code passes Try safety check

**Fallback**: `prompt_user`
- **Details**: Uncertain about wrapping
  - Present findings to user
  - Ask: "Wrap operation in Try monad?"
  - Log uncertainty to notes table
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Try-Wrapped Division (Passes):**
```python
from functools import reduce

class Try:
    """Try monad for safe exception handling."""

    @staticmethod
    def of(thunk):
        """
        Evaluate thunk safely. Returns Success or Failure.

        Captures any exception and wraps in Failure.
        """
        try:
            return Success(thunk())
        except Exception as e:
            return Failure(e)

class Success:
    def __init__(self, value):
        self.value = value

    def map(self, f):
        """Apply f to success value."""
        return Try.of(lambda: f(self.value))

    def flatMap(self, f):
        """Apply f returning Try."""
        try:
            return f(self.value)
        except Exception as e:
            return Failure(e)

    def or_else(self, default):
        """Return value (ignore default)."""
        return self.value

class Failure:
    def __init__(self, exception):
        self.exception = exception

    def map(self, f):
        """Propagate failure."""
        return self

    def flatMap(self, f):
        """Propagate failure."""
        return self

    def or_else(self, default):
        """Return default value."""
        return default

def safe_divide(a: float, b: float) -> Try[float]:
    """
    Divide a by b safely using Try monad.

    Automatically captures ZeroDivisionError.
    """
    return Try.of(lambda: a / b)

# Usage
result = safe_divide(10, 2)
print(result.or_else(0))  # 5.0

result = safe_divide(10, 0)
print(result.or_else(0))  # 0 (failure handled)
```

**Why Compliant**:
- Division wrapped in Try monad
- No explicit try/catch
- Automatic exception capture
- Composable error handling

---

**Try Pipeline (Passes):**
```python
def parse_int(s: str) -> Try[int]:
    """Parse string to int safely."""
    return Try.of(lambda: int(s))

def validate_positive(n: int) -> Try[int]:
    """Validate number is positive."""
    if n > 0:
        return Success(n)
    else:
        return Failure(ValueError(f"Not positive: {n}"))

def double(n: int) -> Try[int]:
    """Double number safely."""
    return Try.of(lambda: n * 2)

def process_number(s: str) -> Try[int]:
    """
    Process number string through Try pipeline.

    Chains multiple Try-wrapped operations.
    """
    return (
        parse_int(s)
        .flatMap(validate_positive)
        .flatMap(double)
    )

# Usage
result = process_number("5")
print(result.or_else(0))  # 10

result = process_number("abc")
print(result.or_else(0))  # 0 (parse failure)

result = process_number("-5")
print(result.or_else(0))  # 0 (validation failure)
```

**Why Compliant**:
- All operations wrapped in Try
- Chained with flatMap
- No exceptions escape
- Declarative error handling

---

### ❌ Non-Compliant Code

**Unchecked Division (Violation):**
```python
# ❌ VIOLATION: Division without Try wrapping
def calculate_average(numbers: list[float]) -> float:
    total = sum(numbers)
    count = len(numbers)
    return total / count  # ← Can throw ZeroDivisionError!
```

**Why Non-Compliant**:
- Division not wrapped in Try
- ZeroDivisionError can crash program
- Not safe for empty lists
- Not composable

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Division wrapped in Try
def calculate_average(numbers: list[float]) -> Try[float]:
    """
    Calculate average safely. Returns Failure if empty list.

    Uses Try to capture division by zero.
    """
    total = sum(numbers)
    count = len(numbers)

    return Try.of(lambda: total / count)

# Usage with default
avg = calculate_average([1, 2, 3]).or_else(0.0)  # 2.0
avg = calculate_average([]).or_else(0.0)         # 0.0 (safe)
```

---

**Explicit Throw (Violation):**
```python
# ❌ VIOLATION: Throwing exception instead of Try
def parse_config(data: str) -> dict:
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")  # ← Throws exception
```

**Why Non-Compliant**:
- Throws exception explicitly
- Callers must use try/catch
- Not composable in pipelines
- Violates FP error handling

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Returns Try instead of throwing
def parse_config(data: str) -> Try[dict]:
    """
    Parse JSON config safely. Returns Try wrapping json.loads.

    Automatically captures JSONDecodeError in Failure.
    """
    return Try.of(lambda: json.loads(data))

# Usage in pipeline
config = (
    parse_config(data)
    .map(lambda c: c.get("settings", {}))
    .or_else({})
)
```

---

**Try/Catch Block (Violation):**
```python
# ❌ VIOLATION: Imperative try/catch
def read_file_content(path: str) -> str:
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""  # Hidden error case
    except IOError as e:
        raise RuntimeError(f"IO error: {e}")  # Still throws!
```

**Why Non-Compliant**:
- Imperative try/catch control flow
- Hides some errors (returns "")
- Still throws in other cases
- Not composable

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Returns Try monad
def read_file_content(path: str) -> Try[str]:
    """
    Read file content safely. Returns Try.

    Automatically captures all file read exceptions.
    """
    def read_operation():
        with open(path, 'r') as f:
            return f.read()

    return Try.of(read_operation)

# Usage with default
content = read_file_content("config.txt").or_else("")

# Usage with error handling
result = read_file_content("config.txt")
match result:
    case Success(content):
        process_content(content)
    case Failure(error):
        log_error(f"Failed to read file: {error}")
```

---

## Edge Cases

### Edge Case 1: Multiple Exception Types

**Issue**: Operation can throw different exception types

**Handling**:
```python
# Try automatically captures all exceptions
def parse_and_validate(data: str) -> Try[dict]:
    """
    Parse and validate data. Try captures any exception.

    Can throw:
    - json.JSONDecodeError (parsing)
    - ValueError (validation)
    - KeyError (missing fields)

    All captured automatically by Try.
    """
    def operation():
        parsed = json.loads(data)  # JSONDecodeError
        if 'id' not in parsed:
            raise KeyError("Missing 'id'")  # KeyError
        if parsed['id'] < 0:
            raise ValueError("Invalid ID")  # ValueError
        return parsed

    return Try.of(operation)

# All exceptions captured in Failure
result = parse_and_validate('{"id": -1}')
# Returns: Failure(ValueError("Invalid ID"))
```

**Directive Action**: Try captures all exception types automatically.

---

### Edge Case 2: Asynchronous Operations

**Issue**: Try needs to work with async/await code

**Handling**:
```python
# AsyncTry for asynchronous operations
class AsyncTry:
    """Try monad for async operations."""

    @staticmethod
    async def of(async_thunk):
        """
        Evaluate async thunk safely.

        Captures exceptions in async context.
        """
        try:
            value = await async_thunk()
            return Success(value)
        except Exception as e:
            return Failure(e)

async def fetch_data_safely(url: str) -> Try[dict]:
    """
    Fetch data from URL using AsyncTry.

    Wraps aiohttp in Try monad.
    """
    async def fetch_operation():
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    return await AsyncTry.of(fetch_operation)

# Usage
result = await fetch_data_safely("https://api.example.com/data")
data = result.or_else({})
```

**Directive Action**: Use AsyncTry for async operations that might throw.

---

### Edge Case 3: Partial Function Application

**Issue**: Try with partially applied functions

**Handling**:
```python
# Try works with partial application
from functools import partial

def divide_by(divisor: float, dividend: float) -> float:
    """Divide dividend by divisor (might throw)."""
    return dividend / divisor

# Partially apply divisor
divide_by_2 = partial(divide_by, 2.0)

# Wrap in Try for safe evaluation
def safe_divide_by_2(dividend: float) -> Try[float]:
    """Safely divide by 2."""
    return Try.of(lambda: divide_by_2(dividend))

# Usage
result = safe_divide_by_2(10)  # Success(5.0)
```

**Directive Action**: Try wraps curried/partial functions seamlessly.

---

### Edge Case 4: Recovering from Failure

**Issue**: Need to retry operation or provide fallback on failure

**Handling**:
```python
def fetch_with_retry(url: str, retries: int = 3) -> Try[dict]:
    """
    Fetch data with retry on failure.

    Uses Try.recover to attempt multiple times.
    """
    result = Try.of(lambda: requests.get(url).json())

    for _ in range(retries):
        if isinstance(result, Failure):
            # Retry on failure
            result = Try.of(lambda: requests.get(url).json())
        else:
            break

    return result

# Alternative: Fallback chain
def fetch_from_primary_or_backup(primary_url: str, backup_url: str) -> Try[dict]:
    """
    Fetch from primary, fallback to backup on failure.

    Chains Try operations with recovery.
    """
    primary = Try.of(lambda: requests.get(primary_url).json())

    if isinstance(primary, Success):
        return primary
    else:
        # Fallback to backup
        return Try.of(lambda: requests.get(backup_url).json())
```

**Directive Action**: Chain Try operations with fallback/retry logic.

---

## Related Directives

- **Depends On**:
  - `fp_result_types` - Try is specialized Result for exception wrapping
- **Triggers**:
  - `fp_error_pipeline` - Try values chain in error pipelines
  - `fp_monadic_composition` - Try is a monad, composes with others
- **Called By**:
  - `project_file_write` - Validates Try usage for risky operations
  - `project_compliance_check` - Scans for unsafe exception-prone code
  - `fp_side_effect_detection` - Try wraps effectful operations
- **Escalates To**:
  - `fp_wrapper_generation` - For wrapping exception-heavy libraries

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `error_handling_pattern = 'try_monad'` for Try-using functions
- **`functions`**: Updates `exception_safety = 'try_wrapped'` for risky operations
- **`interactions`**: Tracks Try chaining between functions (flatMap dependencies)

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

1. **Write risky operation without Try** → Directive detects and wraps
   ```python
   # Input (unsafe)
   def parse(s): return int(s)  # Can throw

   # Expected output (Try-wrapped)
   def parse(s) -> Try[int]:
       return Try.of(lambda: int(s))
   ```

2. **Write operation with Try** → Directive marks compliant
   ```python
   def parse(s) -> Try[int]:
       return Try.of(lambda: int(s))
   # ✅ Already Try-safe
   ```

3. **Check database** → Verify `functions.error_handling_pattern = 'try_monad'`
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Common Mistakes

- ❌ **Unwrapping Try without handling Failure** - Use or_else() or pattern matching
- ❌ **Using Try for normal errors** - Use Result for explicit error types
- ❌ **Nested Try monads** - Use flatMap to flatten Try[Try[T]] to Try[T]
- ❌ **Try for pure operations** - Only wrap exception-prone code
- ❌ **Ignoring Failure cases** - Always handle both Success and Failure

---

## Roadblocks and Resolutions

### Roadblock 1: unwrapped_error_prone_call
**Issue**: Risky operation not wrapped in Try
**Resolution**: Wrap operation with Try.of(lambda: operation())

### Roadblock 2: unhandled_exception
**Issue**: Exception thrown instead of captured in Try
**Resolution**: Convert throw to Try.failure return

### Roadblock 3: imperative_try_catch
**Issue**: Using try/catch instead of Try monad
**Resolution**: Replace try/catch with Try.of wrapping

### Roadblock 4: async_exception_handling
**Issue**: Async operations need exception safety
**Resolution**: Use AsyncTry variant for async/await code

---

## Integration with Project Directives

### Called by project_file_write

```
project_file_write
  └─ Calls fp_try_monad for exception-prone operations
      └─ Analyzes code for risky operations
      └─ Returns: {refactored_code: "...", try_safe: true}
  └─ If compliant: write file + update project.db
      └─ UPDATE functions SET error_handling_pattern = 'try_monad', exception_safety = 'try_wrapped'
```

### Called by project_compliance_check

```
project_compliance_check
  └─ Queries project.db for all functions
  └─ For each function:
      └─ Calls fp_try_monad to verify risky operations wrapped
      └─ Collects violations (unwrapped exception-prone code)
  └─ Generates compliance report
  └─ Writes violations to notes table
```

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for safe exception handling with Try monad*
