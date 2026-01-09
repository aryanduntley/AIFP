# Directive: fp_result_types

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: HIGH - Critical for error handling

---

## Purpose

The `fp_result_types` directive enforces the use of Result/Either types instead of exceptions for error propagation. This directive promotes **predictable, composable error handling** where errors are explicit values in the type system rather than control-flow interruptions.

Result types transform error handling from **exceptional control flow** to **normal data flow**, enabling:
- **Type Safety**: Compiler/type checker enforces handling of Error/Ok cases
- **Explicit Errors**: Function signatures show operations can fail
- **Composability**: Results chain with map/flatMap through pipelines
- **No Hidden Control Flow**: No try/catch blocks disrupting logic
- **Self-Documenting**: Return type shows what errors can occur

This directive complements `fp_optionals` (for absence) and `fp_try_monad` (for exception wrapping). Together, they create a complete functional error handling ecosystem.

**Important**: This directive is reference documentation for Result type patterns.
AI consults this when uncertain about error handling strategies or Result type usage.

**Result types are baseline behavior**:
- AI uses Result types naturally for error handling (enforced by system prompt)
- This directive provides detailed guidance for complex error scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about whether to use Result, Option, or Try for a scenario
- Complex error chaining or pipeline construction
- Need for patterns to replace exception-based error handling
- Edge cases with error recovery or transformation

**Context**:
- AI uses Result types as baseline error handling (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_optionals`, `fp_try_monad`, `fp_error_pipeline`) may reference this

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: analyze_exceptions

Scans function code to detect exception throws, try/catch blocks, and missing Result type usage.

**Steps**:
1. **Parse function body** - Extract all throw statements and try/catch blocks
2. **Identify throw statements** - Find `raise`, `throw`, `panic!` statements
3. **Identify exception catches** - Find try/catch, try/except blocks
4. **Identify error-prone operations** - File I/O, parsing, network calls without Result
5. **Evaluate compliance** - Classify as compliant, needs-refactoring, or uncertain

### Branches

**Branch 1: If throw_statement_found**
- **Then**: `replace_with_result_type`
- **Details**: Convert exception throws to Result type returns
  - Replace `raise ValueError("message")` with `return Err("message")`
  - Replace `throw new Error("message")` with `return Err("message")`
  - Update function signature to return `Result[T, E]`
  - Add Result type imports if needed
- **Result**: Returns refactored code with Result type

**Branch 2: If exception_catch_block**
- **Then**: `wrap_in_result_pattern`
- **Details**: Convert try/catch to Result-returning function
  - Extract try block code into separate function returning Result
  - Convert catch handler to Err variant
  - Chain with map/flatMap if needed
  - Remove try/catch control flow
- **Result**: Returns exception-free code with Result

**Branch 3: If nested_try_catch**
- **Then**: `flatten_using_functional_chain`
- **Details**: Convert nested error handling to Result pipeline
  - Extract each try block into separate function
  - Chain functions with flatMap
  - Handle all error cases in single pipeline
  - Remove nested try/catch complexity
- **Result**: Returns flat Result pipeline

**Branch 4: If compliant**
- **Then**: `mark_as_functional`
- **Details**: Function already uses Result types correctly
  - No exceptions thrown
  - Result type used properly
  - Mark as compliant
- **Result**: Function passes Result compliance check

**Fallback**: `prompt_user`
- **Details**: Uncertain about refactoring
  - Present findings to user
  - Ask: "Convert exception handling to Result type?"
  - Log uncertainty to notes table
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Result Return (Passes):**
```python
from typing import Union

class Ok:
    def __init__(self, value):
        self.value = value

class Err:
    def __init__(self, error):
        self.error = error

Result = Union[Ok, Err]

def divide(a: float, b: float) -> Result[float, str]:
    """
    Divide two numbers using Result type.

    Returns Ok(result) if successful, Err(message) if b is zero.
    Pure function with explicit error handling.
    """
    if b == 0:
        return Err("Division by zero")

    return Ok(a / b)

# Usage with pattern matching
result = divide(10, 2)
match result:
    case Ok(value):
        print(f"Result: {value}")
    case Err(error):
        print(f"Error: {error}")
```

**Why Compliant**:
- Returns `Result[float, str]` instead of raising exception
- Explicit `Ok()` and `Err()` variants
- No exceptions
- Type-safe error handling

---

**Result Pipeline (Passes):**
```python
def parse_int(s: str) -> Result[int, str]:
    """Parse string to int. Returns Err if invalid."""
    try:
        return Ok(int(s))
    except ValueError:
        return Err(f"Invalid integer: {s}")

def validate_positive(n: int) -> Result[int, str]:
    """Validate number is positive. Returns Err if not."""
    if n > 0:
        return Ok(n)
    else:
        return Err(f"Number must be positive, got {n}")

def double(n: int) -> Result[int, str]:
    """Double a number (always succeeds)."""
    return Ok(n * 2)

def process_input(s: str) -> Result[int, str]:
    """
    Process user input with Result chaining.

    Chains multiple operations that can fail.
    """
    return (
        parse_int(s)
        .flatMap(validate_positive)
        .flatMap(double)
    )

# Usage
result = process_input("5")
# Returns: Ok(10)

result = process_input("-5")
# Returns: Err("Number must be positive, got -5")

result = process_input("abc")
# Returns: Err("Invalid integer: abc")
```

**Why Compliant**:
- Chains Result operations declaratively
- No exceptions escape function boundaries
- Composable error handling
- Clear error propagation

---

### ❌ Non-Compliant Code

**Exception Throw (Violation):**
```python
# ❌ VIOLATION: Throws exception instead of returning Result
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero")  # ← Exception throw

    return a / b
```

**Why Non-Compliant**:
- Throws exception (hidden control flow)
- Error not visible in return type
- Caller must use try/catch
- Not composable in pipelines

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Returns Result type
def divide(a: float, b: float) -> Result[float, str]:
    """Divide a by b. Returns Err if b is zero."""
    if b == 0:
        return Err("Division by zero")

    return Ok(a / b)
```

---

**Try/Catch Block (Violation):**
```python
# ❌ VIOLATION: Uses try/catch for control flow
def read_config_file(path: str) -> dict:
    try:
        with open(path, 'r') as f:  # ← I/O in try block
            return json.load(f)
    except FileNotFoundError:
        return {}  # ← Hidden error case
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")  # ← Still throws!
```

**Why Non-Compliant**:
- Try/catch hides error handling
- Returns empty dict on error (ambiguous)
- Still throws exception in one case
- Not composable

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Returns Result with explicit errors
def read_config_file(path: str) -> Result[dict, str]:
    """
    Read and parse config file.

    Returns Ok(config) or Err(message) describing the failure.
    """
    # Separate I/O effect from parsing logic
    file_content = read_file_effect(path)

    if isinstance(file_content, Err):
        return file_content  # Propagate file read error

    # Parse JSON (pure function)
    return parse_json(file_content.value)

def read_file_effect(path: str) -> Result[str, str]:
    """Effect function: Read file contents."""
    try:
        with open(path, 'r') as f:
            return Ok(f.read())
    except FileNotFoundError:
        return Err(f"File not found: {path}")
    except IOError as e:
        return Err(f"IO error: {e}")

def parse_json(content: str) -> Result[dict, str]:
    """Pure function: Parse JSON string."""
    try:
        return Ok(json.loads(content))
    except json.JSONDecodeError as e:
        return Err(f"Invalid JSON: {e}")
```

---

**Nested Try/Catch (Violation):**
```python
# ❌ VIOLATION: Nested exception handling
def process_data(data: str) -> int:
    try:
        parsed = json.loads(data)
        try:
            value = int(parsed['value'])
            try:
                validated = validate(value)
                return validated
            except ValidationError as e:
                raise ValueError(f"Validation failed: {e}")
        except KeyError:
            raise ValueError("Missing 'value' key")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
```

**Why Non-Compliant**:
- Deeply nested try/catch blocks
- Complex control flow
- Difficult to reason about
- Not composable

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Flat Result pipeline
def process_data(data: str) -> Result[int, str]:
    """
    Process data through validation pipeline.

    Uses Result chaining for clean error propagation.
    """
    return (
        parse_json_data(data)
        .flatMap(extract_value_field)
        .flatMap(parse_to_int)
        .flatMap(validate_value)
    )

def parse_json_data(data: str) -> Result[dict, str]:
    """Parse JSON string."""
    try:
        return Ok(json.loads(data))
    except json.JSONDecodeError as e:
        return Err(f"Invalid JSON: {e}")

def extract_value_field(data: dict) -> Result[any, str]:
    """Extract 'value' field from dict."""
    if 'value' in data:
        return Ok(data['value'])
    else:
        return Err("Missing 'value' key")

def parse_to_int(value: any) -> Result[int, str]:
    """Convert value to integer."""
    try:
        return Ok(int(value))
    except (ValueError, TypeError):
        return Err(f"Cannot convert to int: {value}")

def validate_value(value: int) -> Result[int, str]:
    """Validate integer value."""
    if value >= 0:
        return Ok(value)
    else:
        return Err(f"Value must be non-negative: {value}")
```

---

## Edge Cases

### Edge Case 1: Multiple Error Types

**Issue**: Function can fail in different ways with different error types

**Handling**:
```python
# ❌ Bad: String error messages lose type information
def connect_database(url: str) -> Result[Connection, str]:
    # Hard to distinguish error types
    return Err("Connection failed")

# ✅ Good: Enum for error types
from enum import Enum

class DbError(Enum):
    INVALID_URL = "Invalid database URL"
    CONNECTION_TIMEOUT = "Connection timeout"
    AUTH_FAILED = "Authentication failed"
    UNKNOWN = "Unknown error"

def connect_database(url: str) -> Result[Connection, DbError]:
    """Connect to database with typed errors."""
    if not is_valid_url(url):
        return Err(DbError.INVALID_URL)

    connection = attempt_connect(url)

    if connection.timeout:
        return Err(DbError.CONNECTION_TIMEOUT)

    if not connection.authenticated:
        return Err(DbError.AUTH_FAILED)

    return Ok(connection)

# Usage with specific error handling
result = connect_database("invalid")
match result:
    case Err(DbError.INVALID_URL):
        print("Fix your URL")
    case Err(DbError.AUTH_FAILED):
        print("Check credentials")
    case Ok(conn):
        print("Connected!")
```

**Directive Action**: Use enums or ADTs for error types instead of strings.

---

### Edge Case 2: Early Return Patterns

**Issue**: Multiple validation steps with early returns

**Handling**:
```python
# ❌ Bad: Imperative early returns with exceptions
def validate_user(data: dict) -> User:
    if 'email' not in data:
        raise ValueError("Missing email")

    if not is_valid_email(data['email']):
        raise ValueError("Invalid email format")

    if 'age' not in data:
        raise ValueError("Missing age")

    if data['age'] < 18:
        raise ValueError("Must be 18 or older")

    return create_user(data)

# ✅ Good: Result pipeline with clear error flow
def validate_user(data: dict) -> Result[User, str]:
    """Validate user data. Returns Err on first validation failure."""
    return (
        check_has_email(data)
        .flatMap(lambda d: check_email_format(d))
        .flatMap(lambda d: check_has_age(d))
        .flatMap(lambda d: check_age_minimum(d))
        .map(lambda d: create_user(d))
    )

def check_has_email(data: dict) -> Result[dict, str]:
    """Check email field exists."""
    if 'email' in data:
        return Ok(data)
    else:
        return Err("Missing email")

# ... similar for other validations
```

**Directive Action**: Convert early returns/throws to Result pipeline.

---

### Edge Case 3: Combining Multiple Results

**Issue**: Need to combine results from multiple operations

**Handling**:
```python
# ❌ Bad: Nested result unwrapping
def process_order(order_id: str, user_id: str) -> Result[Order, str]:
    order_result = fetch_order(order_id)
    if isinstance(order_result, Err):
        return order_result

    user_result = fetch_user(user_id)
    if isinstance(user_result, Err):
        return user_result

    # Now have both values...
    return Ok(create_order(order_result.value, user_result.value))

# ✅ Good: Applicative functor pattern for combining Results
def process_order(order_id: str, user_id: str) -> Result[Order, str]:
    """
    Process order by combining order and user data.

    Uses applicative pattern to combine multiple Results.
    """
    return fetch_order(order_id).flatMap(lambda order:
        fetch_user(user_id).map(lambda user:
            create_order(order, user)
        )
    )

# ✅ Better: Dedicated combiner
def combine_results(r1: Result[A, E], r2: Result[B, E]) -> Result[tuple[A, B], E]:
    """Combine two Results into tuple if both Ok."""
    return r1.flatMap(lambda v1:
        r2.map(lambda v2: (v1, v2))
    )

def process_order(order_id: str, user_id: str) -> Result[Order, str]:
    """Process order using result combiner."""
    combined = combine_results(
        fetch_order(order_id),
        fetch_user(user_id)
    )

    return combined.map(lambda pair: create_order(pair[0], pair[1]))
```

**Directive Action**: Use flatMap chaining or applicative pattern for combining Results.

---

### Edge Case 4: Converting Exception-Heavy Libraries

**Issue**: Third-party libraries throw exceptions, need to wrap in Result

**Handling**:
```python
# ❌ Bad: Let exceptions propagate
def call_external_api(url: str) -> dict:
    return requests.get(url).json()  # Throws on network error or invalid JSON

# ✅ Good: Wrap exception-throwing code in Result
def call_external_api(url: str) -> Result[dict, str]:
    """
    Call external API with Result wrapping.

    Wraps exception-throwing requests library in Result type.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Ok(response.json())
    except requests.RequestException as e:
        return Err(f"API request failed: {e}")
    except json.JSONDecodeError as e:
        return Err(f"Invalid JSON response: {e}")

# Usage
result = call_external_api("https://api.example.com/data")
match result:
    case Ok(data):
        process_data(data)
    case Err(error):
        log_error(error)
```

**Directive Action**: Wrap exception-throwing external code in Result-returning wrapper functions.

---

## Related Directives

- **Depends On**: None (foundational error handling directive)
- **Triggers**:
  - `fp_optionals` - Result for errors, Option for absence (use both)
  - `fp_error_pipeline` - Results chain in error handling pipelines
  - `fp_try_monad` - Try is specialized Result for exception wrapping
- **Called By**:
  - `project_file_write` - Validates Result usage before file writes
  - `project_compliance_check` - Verifies exception elimination
  - `fp_monadic_composition` - Results are monads, compose with others
- **Escalates To**:
  - `fp_language_standardization` - For language-specific Result implementations

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `error_handling_pattern = 'result'` for compliant functions
- **`functions`**: Updates `type_annotations_json` with Result type info
- **`functions`**: Sets `exceptions_json = '[]'` (no exceptions thrown)
- **`interactions`**: Tracks Result chaining between functions (flatMap dependencies)

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

1. **Write function with exception** → Directive detects and refactors
   ```python
   # Input (exception)
   def parse(s): return int(s)  # Throws ValueError

   # Expected output (Result)
   def parse(s) -> Result[int, str]:
       try:
           return Ok(int(s))
       except ValueError as e:
           return Err(f"Parse error: {e}")
   ```

2. **Write function with Result** → Directive marks compliant
   ```python
   def parse(s) -> Result[int, str]:
       try:
           return Ok(int(s))
       except ValueError:
           return Err("Invalid integer")
   # ✅ Already compliant
   ```

3. **Check database** → Verify `functions.error_handling_pattern = 'result'`
   ```sql
   SELECT name, error_handling_pattern, exceptions_json
   FROM functions
   WHERE name = 'parse';
   -- Expected: error_handling_pattern='result', exceptions_json='[]'
   ```

---

## Common Mistakes

- ❌ **Throwing exceptions inside Result-returning functions** - Defeats purpose
- ❌ **Using Result for absence** - Use Option for missing data, Result for errors
- ❌ **Unwrapping Result without checking** - Use pattern matching or map/flatMap
- ❌ **String error messages only** - Use typed error enums for better handling
- ❌ **Mixing exceptions and Results** - Must eliminate all exception throws

---

## Roadblocks and Resolutions

### Roadblock 1: throw_usage
**Issue**: Function throws exception instead of returning Result
**Resolution**: Replace throw with Err return, update signature to Result[T, E]

### Roadblock 2: nested_try_catch
**Issue**: Deeply nested exception handling
**Resolution**: Flatten using functional error chain with flatMap

### Roadblock 3: external_library_exceptions
**Issue**: Third-party library throws exceptions
**Resolution**: Wrap in Result-returning adapter function

### Roadblock 4: mixed_error_handling
**Issue**: Some functions use Result, others throw exceptions
**Resolution**: Systematically convert all error-prone functions to Result

---

## Integration with Project Directives

### Called by project_file_write

```
project_file_write
  └─ Calls fp_result_types (among other FP directives)
      └─ Analyzes function for exception throws and Result usage
      └─ Returns: {refactored_code: "...", result_compliant: true}
  └─ If compliant: write file + update project.db
      └─ UPDATE functions SET error_handling_pattern = 'result', exceptions_json = '[]'
```

### Called by project_compliance_check

```
project_compliance_check
  └─ Queries project.db for all functions
  └─ For each function:
      └─ Calls fp_result_types to verify exception elimination
      └─ Collects violations (functions still throwing)
  └─ Generates compliance report
  └─ Writes violations to notes table
```

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for exception-free error handling*
