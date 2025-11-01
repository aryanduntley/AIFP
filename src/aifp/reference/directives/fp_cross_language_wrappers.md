# Directive: fp_cross_language_wrappers

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Enables FP compliance for non-FP libraries

---

## Purpose

The `fp_cross_language_wrappers` directive automatically generates pure functional wrappers around language-specific and third-party libraries to maintain AIFP FP compliance across language boundaries. This directive provides **FP isolation** for non-functional external code.

Cross-language wrappers provide **purity preservation**, enabling:
- **FP Compliance**: Wrap impure libraries with pure interfaces
- **Side Effect Isolation**: Contain I/O and mutations in wrapper layer
- **Consistent API**: Uniform functional interfaces across languages
- **Dependency Safety**: External libraries don't violate FP principles
- **Testability**: Pure wrappers are easy to test and mock

This directive acts as an **adapter layer** between pure functional code and impure external libraries.

**Real-world examples**: See [examples/wrappers/](../../../examples/wrappers/) for working wrapper implementations. As AIFP develops, this folder will contain reference implementations for common libraries.

---

## When to Apply

This directive applies when:
- **External library usage** - Using non-FP third-party libraries
- **Language standard library** - Wrapping impure built-in functions
- **Cross-language interop** - Calling code from another language
- **I/O operations** - Database, network, file system interactions
- **Impure API detected** - Library violates FP principles
- **Called by project directives**:
  - `project_file_write` - Generate wrappers when external deps detected
  - Works with `fp_io_isolation` - Wrappers isolate I/O effects
  - Works with `fp_language_standardization` - Standardize wrapper names

---

## Workflow

### Trunk: detect_foreign_imports

Scans code for external library usage and generates FP-compliant wrapper modules.

**Steps**:
1. **Scan imports** - Identify external library imports
2. **Analyze API** - Determine if library is FP-compliant
3. **Detect impurities** - Find side effects, mutations, exceptions
4. **Design wrapper interface** - Create pure functional API
5. **Generate wrapper code** - Implement wrapper module
6. **Update imports** - Replace direct library usage with wrapper

### Branches

**Branch 1: If nonstandard_library**
- **Then**: `generate_cross_language_wrapper`
- **Details**: External library violates FP principles
  - Library has side effects (I/O, mutations, exceptions)
  - Wrap impure functions with pure interfaces
  - Use Result types for error handling
  - Pass dependencies explicitly as parameters
  - Generate wrapper module with FP-compliant API
- **Result**: Returns wrapper module code

**Branch 2: If known_fp_library**
- **Then**: `validate_compatibility`
- **Details**: Library claims to be FP-compliant
  - Verify library follows FP principles
  - Check for hidden side effects
  - Validate purity claims
  - If compliant: allow direct usage
  - If not compliant: generate wrapper
- **Result**: Returns validation result

**Branch 3: If builtin_impure**
- **Then**: `wrap_builtin_function`
- **Details**: Language built-in violates FP
  - Example: Python's `open()`, JavaScript's `fetch()`
  - Create pure wrapper with explicit effect management
  - Use dependency injection for testability
  - Return Result types for errors
- **Result**: Returns wrapped built-in

**Branch 4: If already_wrapped**
- **Then**: `mark_as_supported`
- **Details**: Library already has FP wrapper
  - Wrapper module exists
  - Interface is FP-compliant
  - No direct library usage
- **Result**: Code passes check

**Fallback**: `prompt_user`
- **Details**: Unable to generate wrapper automatically
  - Complex library API
  - Unclear purity boundaries
  - Ask user for wrapper strategy
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**File System Wrapper (Passes):**

```python
# fp_file_system.py - Pure wrapper for file I/O

from typing import Union
from pathlib import Path

class Ok:
    def __init__(self, value):
        self.value = value

class Err:
    def __init__(self, error):
        self.error = error

Result = Union[Ok, Err]

def read_file(path: str) -> Result[str, str]:
    """
    Pure wrapper for file reading.

    Returns Result type instead of raising exceptions.
    Side effect isolated to this function boundary.

    AIFP Wrapper: Wraps Python built-in open()
    """
    try:
        with open(path, 'r') as f:
            content = f.read()
        return Ok(content)
    except IOError as e:
        return Err(f"Failed to read file: {e}")
    except Exception as e:
        return Err(f"Unexpected error: {e}")

def write_file(path: str, content: str) -> Result[None, str]:
    """
    Pure wrapper for file writing.

    Returns Result type for success/failure.
    Side effect isolated to this function boundary.

    AIFP Wrapper: Wraps Python built-in open()
    """
    try:
        with open(path, 'w') as f:
            f.write(content)
        return Ok(None)
    except IOError as e:
        return Err(f"Failed to write file: {e}")
    except Exception as e:
        return Err(f"Unexpected error: {e}")

# Usage in pure functional code
def process_file(input_path: str, output_path: str) -> Result[str, str]:
    """Pure function using wrapped file I/O"""
    read_result = read_file(input_path)
    if isinstance(read_result, Err):
        return read_result

    content = read_result.value
    processed = content.upper()  # Pure transformation

    write_result = write_file(output_path, processed)
    if isinstance(write_result, Err):
        return write_result

    return Ok("File processed successfully")
```

**Why Compliant**:
- Impure built-ins wrapped with pure interface
- Result types for error handling (no exceptions)
- Side effects isolated to wrapper boundary
- Easy to test with mocked wrapper

---

**HTTP Client Wrapper (Passes):**

```python
# fp_http_client.py - Pure wrapper for HTTP requests

from typing import Union, Dict, Any
import requests  # External library (impure)

Result = Union['Ok', 'Err']

class Ok:
    def __init__(self, value):
        self.value = value

class Err:
    def __init__(self, error):
        self.error = error

def http_get(url: str, headers: Dict[str, str] = None) -> Result[Dict[str, Any], str]:
    """
    Pure wrapper for HTTP GET.

    Wraps requests.get() with pure interface.
    Returns Result type for success/failure.

    AIFP Wrapper: Wraps requests library (impure)
    """
    try:
        response = requests.get(url, headers=headers or {}, timeout=30)
        if response.status_code >= 400:
            return Err(f"HTTP {response.status_code}: {response.text}")
        return Ok({
            'status': response.status_code,
            'headers': dict(response.headers),
            'body': response.text
        })
    except requests.RequestException as e:
        return Err(f"Request failed: {e}")
    except Exception as e:
        return Err(f"Unexpected error: {e}")

def http_post(url: str, data: Dict[str, Any], headers: Dict[str, str] = None) -> Result[Dict[str, Any], str]:
    """
    Pure wrapper for HTTP POST.

    Wraps requests.post() with pure interface.

    AIFP Wrapper: Wraps requests library (impure)
    """
    try:
        response = requests.post(url, json=data, headers=headers or {}, timeout=30)
        if response.status_code >= 400:
            return Err(f"HTTP {response.status_code}: {response.text}")
        return Ok({
            'status': response.status_code,
            'headers': dict(response.headers),
            'body': response.text
        })
    except requests.RequestException as e:
        return Err(f"Request failed: {e}")
    except Exception as e:
        return Err(f"Unexpected error: {e}")

# Usage
def fetch_user_data(user_id: int) -> Result[Dict[str, Any], str]:
    """Pure function using wrapped HTTP client"""
    url = f"https://api.example.com/users/{user_id}"
    result = http_get(url)

    if isinstance(result, Err):
        return result

    return Ok(result.value['body'])
```

**Why Compliant**:
- External impure library wrapped
- All side effects isolated
- Result types throughout
- Testable with wrapper mocks

---

**Database Wrapper (Passes):**

```python
# fp_database.py - Pure wrapper for database operations

from typing import Union, List, Dict, Any
import sqlite3  # Impure built-in

Result = Union['Ok', 'Err']

class Ok:
    def __init__(self, value):
        self.value = value

class Err:
    def __init__(self, error):
        self.error = error

# Pure wrapper interface - dependency injection pattern
def db_query(connection_string: str, sql: str, params: tuple = ()) -> Result[List[Dict[str, Any]], str]:
    """
    Pure wrapper for database query.

    Takes connection string as explicit parameter (dependency injection).
    Returns Result type for success/failure.

    AIFP Wrapper: Wraps sqlite3 (impure built-in)
    """
    try:
        conn = sqlite3.connect(connection_string)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return Ok(rows)
    except sqlite3.Error as e:
        return Err(f"Database error: {e}")
    except Exception as e:
        return Err(f"Unexpected error: {e}")

def db_execute(connection_string: str, sql: str, params: tuple = ()) -> Result[int, str]:
    """
    Pure wrapper for database write operations.

    Returns row count on success.

    AIFP Wrapper: Wraps sqlite3 (impure built-in)
    """
    try:
        conn = sqlite3.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        row_count = cursor.rowcount
        conn.commit()
        conn.close()
        return Ok(row_count)
    except sqlite3.Error as e:
        return Err(f"Database error: {e}")
    except Exception as e:
        return Err(f"Unexpected error: {e}")

# Usage with dependency injection
def get_user_by_id(db_conn: str, user_id: int) -> Result[Dict[str, Any], str]:
    """Pure function - database dependency passed explicitly"""
    sql = "SELECT * FROM users WHERE id = ?"
    result = db_query(db_conn, sql, (user_id,))

    if isinstance(result, Err):
        return result

    rows = result.value
    if not rows:
        return Err(f"User {user_id} not found")

    return Ok(rows[0])
```

**Why Compliant**:
- Database side effects isolated
- Dependency injection (connection passed as parameter)
- Result types for all operations
- Pure functional interface

---

### ❌ Non-Compliant Code

**Direct Library Usage (Violation):**

```python
# ❌ VIOLATION: Direct use of impure library
import requests  # Impure library

def fetch_user(user_id: int):
    """Fetch user data from API."""
    url = f"https://api.example.com/users/{user_id}"
    response = requests.get(url)  # ← Direct impure call, raises exceptions
    return response.json()  # ← Can throw exceptions

# Problem:
# - Direct use of impure library
# - No error handling (exceptions thrown)
# - Side effects not isolated
# - Not FP-compliant
# - Hard to test (no wrapper to mock)
```

**Why Non-Compliant**:
- Direct impure library usage
- Exceptions instead of Result types
- Side effects not isolated
- Cannot mock for testing

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Wrapped with FP interface
from fp_http_client import http_get, Result, Ok, Err

def fetch_user(user_id: int) -> Result[dict, str]:
    """
    Fetch user data using FP wrapper.

    Uses fp_http_client wrapper for FP compliance.
    """
    url = f"https://api.example.com/users/{user_id}"
    result = http_get(url)

    if isinstance(result, Err):
        return Err(f"Failed to fetch user: {result.error}")

    response = result.value
    import json
    try:
        data = json.loads(response['body'])
        return Ok(data)
    except json.JSONDecodeError as e:
        return Err(f"Invalid JSON: {e}")
```

---

**Hidden Global State (Violation):**

```python
# ❌ VIOLATION: Library with hidden global state
import random  # Uses global RNG state

def generate_random_numbers(count: int) -> list[int]:
    """Generate random numbers."""
    return [random.randint(1, 100) for _ in range(count)]  # ← Impure!

# Problem:
# - Uses global random state
# - Not deterministic
# - Side effects hidden
# - Cannot reproduce results
# - Not testable
```

**Why Non-Compliant**:
- Hidden global state (RNG seed)
- Non-deterministic
- Impure function
- Cannot test reliably

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Explicit RNG state
import random as stdlib_random

def generate_random_numbers(seed: int, count: int) -> list[int]:
    """
    Generate random numbers with explicit seed.

    AIFP Wrapper: Wraps random module with explicit state.
    Deterministic - same seed produces same output.
    """
    rng = stdlib_random.Random(seed)  # Explicit state
    return [rng.randint(1, 100) for _ in range(count)]

# Usage
numbers1 = generate_random_numbers(42, 5)  # [81, 14, 3, 94, 35]
numbers2 = generate_random_numbers(42, 5)  # [81, 14, 3, 94, 35] - same!

# Deterministic, testable, pure (given same seed)
```

---

**Exception-Throwing Library (Violation):**

```python
# ❌ VIOLATION: Direct use of exception-throwing library
import json

def parse_json(text: str):
    """Parse JSON string."""
    return json.loads(text)  # ← Throws JSONDecodeError

# Problem:
# - Throws exceptions (not FP)
# - No error type in signature
# - Caller must use try/except
# - Not composable
```

**Why Non-Compliant**:
- Exceptions instead of Result types
- Not FP-compliant error handling
- Forces imperative error handling

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Result-based wrapper
import json
from typing import Union, Any

Result = Union['Ok', 'Err']

class Ok:
    def __init__(self, value):
        self.value = value

class Err:
    def __init__(self, error):
        self.error = error

def parse_json(text: str) -> Result[Any, str]:
    """
    Parse JSON with FP error handling.

    AIFP Wrapper: Wraps json.loads with Result type.
    """
    try:
        data = json.loads(text)
        return Ok(data)
    except json.JSONDecodeError as e:
        return Err(f"JSON parse error: {e}")
    except Exception as e:
        return Err(f"Unexpected error: {e}")

# Usage - composable
def process_json_file(content: str) -> Result[dict, str]:
    """Process JSON file content"""
    parse_result = parse_json(content)
    if isinstance(parse_result, Err):
        return parse_result

    data = parse_result.value
    # ... continue processing
    return Ok(data)
```

---

## Edge Cases

### Edge Case 1: Library with Callbacks

**Issue**: Library uses callbacks (imperative pattern)

**Handling**:
```python
# Impure library with callbacks
def fetch_async(url, callback):
    """Async fetch with callback (impure)"""
    # ... library implementation

# ✅ AIFP Wrapper: Convert to Result-returning function
from concurrent.futures import Future
from typing import Union

def fetch_sync(url: str) -> Result[str, str]:
    """
    Sync wrapper for async library.

    AIFP Wrapper: Converts callback-based to Result-based.
    """
    future = Future()

    def callback(error, result):
        if error:
            future.set_exception(error)
        else:
            future.set_result(result)

    try:
        fetch_async(url, callback)
        result = future.result(timeout=30)
        return Ok(result)
    except Exception as e:
        return Err(str(e))
```

**Directive Action**: Convert callback-based APIs to Result-returning functions.

---

### Edge Case 2: Library with Side-Effect Constructors

**Issue**: Library object constructors have side effects

**Handling**:
```python
# ❌ Library with side-effect constructor
class Database:
    def __init__(self, connection_string):
        self.conn = connect(connection_string)  # ← Side effect!

# ✅ AIFP Wrapper: Factory function with Result
def create_database(connection_string: str) -> Result[Database, str]:
    """
    Create database connection with error handling.

    AIFP Wrapper: Wraps side-effect constructor.
    """
    try:
        db = Database(connection_string)
        return Ok(db)
    except Exception as e:
        return Err(f"Connection failed: {e}")
```

**Directive Action**: Wrap constructors with factory functions returning Result.

---

### Edge Case 3: Stateful Library Objects

**Issue**: Library maintains mutable internal state

**Handling**:
```python
# ❌ Stateful library (impure)
class Counter:
    def __init__(self):
        self.count = 0  # Mutable state

    def increment(self):
        self.count += 1  # Mutation!
        return self.count

# ✅ AIFP Wrapper: Pure functional interface
def increment_counter(current_count: int) -> int:
    """
    Pure increment function.

    AIFP Wrapper: Replaces stateful object with pure function.
    """
    return current_count + 1

# Usage - pure and immutable
count1 = 0
count2 = increment_counter(count1)  # 1
count3 = increment_counter(count2)  # 2
# count1 is still 0 (immutable)
```

**Directive Action**: Replace stateful objects with pure functions passing state explicitly.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Wrappers must be as pure as possible
  - `fp_io_isolation` - Wrappers isolate side effects
- **Triggers**:
  - `fp_language_standardization` - Standardize wrapper names
  - `fp_result_types` - Use Result types in wrappers
- **Called By**:
  - `project_file_write` - Generate wrappers when external deps detected
- **Escalates To**: None

---

## Helper Functions Used

- `detect_external_imports(code: str) -> list[str]` - Find library imports
- `analyze_library_purity(library: str) -> bool` - Check if library is FP-compliant
- `generate_wrapper_module(library: str, functions: list) -> str` - Create wrapper code
- `update_imports(code: str, old_import: str, new_import: str) -> str` - Replace imports
- `update_files_table(file_id: int, is_wrapper: bool)` - Update database

---

## Database Operations

This directive updates the following tables:

- **`files`**: Sets `is_wrapper = 1` for generated wrapper modules
- **`functions`**: Marks wrapped functions with `wraps_library = 'library_name'`
- **`notes`**: Logs wrapper generation with `note_type = 'wrapper'`

---

## Testing

How to verify this directive is working:

1. **External library detected** → Directive generates wrapper
   ```python
   # Direct import: import requests
   # After wrapper: from fp_http_client import http_get
   ```

2. **Wrapper uses Result types** → FP-compliant error handling
   ```python
   result = http_get(url)
   if isinstance(result, Err):
       # Handle error
   ```

3. **Check database** → Verify wrappers tracked
   ```sql
   SELECT path, is_wrapper
   FROM files
   WHERE is_wrapper = 1;
   ```

---

## Common Mistakes

- ❌ **Direct impure library usage** - Violates FP principles
- ❌ **Incomplete wrapper** - Some functions wrapped, some not
- ❌ **Leaky abstraction** - Wrapper exposes impure library details
- ❌ **No error handling** - Wrapper doesn't convert exceptions
- ❌ **Hidden dependencies** - Not passing dependencies explicitly

---

## Roadblocks and Resolutions

### Roadblock 1: foreign_library_detected
**Issue**: Code uses external impure library
**Resolution**: Generate FP wrapper module with Result types and explicit dependencies

### Roadblock 2: builtin_impure
**Issue**: Language built-in violates FP principles
**Resolution**: Create pure wrapper with dependency injection

### Roadblock 3: stateful_library
**Issue**: Library maintains mutable internal state
**Resolution**: Replace with pure functions passing state explicitly

### Roadblock 4: callback_based_api
**Issue**: Library uses callbacks instead of return values
**Resolution**: Convert to synchronous Result-returning functions

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-cross-language-wrappers)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#language-adaptation)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)
- [Wrapper Examples](../../../examples/wrappers/) - Real-world wrapper implementations (populated during development)

---

*Part of AIFP v1.0 - FP Auxiliary directive for pure functional library wrappers*
