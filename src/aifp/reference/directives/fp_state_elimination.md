# Directive: fp_state_elimination

**Type**: FP
**Level**: 1
**Parent Directive**: None
**Priority**: CRITICAL - Core purity enforcement

---

## Purpose

The `fp_state_elimination` directive **detects and removes reliance on global variables or hidden mutable structures**, ensuring all functions receive their dependencies explicitly as parameters. This directive is **fundamental for functional purity** because:

- **Referential transparency**: Functions with no global state are deterministic
- **Testability**: All dependencies are visible in function signatures
- **Concurrency safety**: No shared mutable state eliminates race conditions
- **AI reasoning**: Clear data flow makes code predictable for AI analysis

This directive works in tandem with `fp_purity` to eliminate all forms of hidden state:
- **Global variables** - Variables defined outside function scope
- **Module-level mutable state** - Counters, caches, configuration objects
- **Static/class variables** - State shared across instances
- **Singleton patterns** - Hidden global instances
- **Environment variables** - External configuration not passed explicitly

**Refactoring approach**: Convert global state access into explicit parameter passing.

---

## When to Apply

This directive applies when:
- **Function accesses global variable** - Reading or writing to module-level state
- **Function relies on implicit configuration** - Uses settings not passed as parameters
- **Code uses singletons or static state** - Shared mutable objects
- **During compliance checks** - `project_compliance_check` scans for global access
- **Before file write** - `project_file_write` validates functions are stateless
- **User requests stateless refactoring** - "Remove global state", "Make functions pure"

---

## Workflow

### Trunk: scan_scope

Scans function body for references to global or static variables.

**Steps**:
1. **Parse function AST** - Extract all variable references
2. **Identify scope** - Determine which variables are local vs global
3. **Detect global access** - Flag variables defined outside function
4. **Route to refactoring** - Inline or parameterize dependencies

### Branches

**Branch 1: If global_references**
- **Then**: `inline_dependencies`
- **Details**: Convert global variable access to explicit parameters
  - Identify all global variables accessed
  - Add parameters to function signature
  - Update function body to use parameters
  - Update all call sites
  - Example transformation:
    ```python
    # Before: Accesses global
    config = {"threshold": 100}

    def check_value(value):
        return value > config["threshold"]  # Global access

    # After: Explicit parameter
    def check_value(value: int, threshold: int) -> bool:
        return value > threshold  # Parameter

    # Call site updated
    result = check_value(150, config["threshold"])
    ```
  - SQL update:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Global access eliminated, function signature updated

**Branch 2: If mutable_static_data**
- **Then**: `convert_to_immutable`
- **Details**: Replace mutable global state with immutable constants
  - Mutable global patterns:
    ```python
    # ❌ Mutable global state
    counter = 0  # Module-level mutable variable

    def increment():
        global counter
        counter += 1
        return counter
    ```
  - Refactoring strategies:
    - **Strategy 1**: Make constant (if never changes)
      ```python
      # ✅ Immutable constant
      INITIAL_VALUE = 0

      def increment(current: int) -> int:
          return current + 1
      ```
    - **Strategy 2**: Pass as parameter (if changes)
      ```python
      # ✅ Explicit state parameter
      def increment(counter: int) -> int:
          return counter + 1

      # Call site
      counter = 0
      counter = increment(counter)
      ```
    - **Strategy 3**: Return new state (functional state)
      ```python
      # ✅ Functional state threading
      @dataclass(frozen=True)
      class AppState:
          counter: int

      def increment(state: AppState) -> AppState:
          return AppState(counter=state.counter + 1)
      ```
  - Choose strategy based on usage pattern
- **Result**: Mutable state converted to immutable constant or explicit parameter

**Branch 3: If singleton_pattern**
- **Then**: `dependency_injection`
- **Details**: Replace singleton access with dependency injection
  - Singleton patterns:
    ```python
    # ❌ Singleton pattern (hidden global state)
    class Database:
        _instance = None

        @classmethod
        def get_instance(cls):
            if cls._instance is None:
                cls._instance = Database()
            return cls._instance

    def get_user(user_id):
        db = Database.get_instance()  # Hidden dependency
        return db.query(f"SELECT * FROM users WHERE id={user_id}")
    ```
  - Refactored to dependency injection:
    ```python
    # ✅ Dependency injection (explicit parameter)
    def get_user(user_id: int, db: DatabaseConnection) -> dict:
        return db.query(f"SELECT * FROM users WHERE id={user_id}")

    # Call site (main/entry point)
    def main():
        db = create_database_connection()
        user = get_user(42, db)
    ```
  - Benefits:
    - Testability: Can inject mock database
    - Visibility: Dependency clear in signature
    - Purity: No hidden global state
- **Result**: Singleton eliminated, dependency passed explicitly

**Branch 4: If environment_variable_access**
- **Then**: `parameterize_config`
- **Details**: Convert environment variable reads to explicit parameters
  - Environment variable access:
    ```python
    # ❌ Environment variable (hidden dependency)
    import os

    def connect_database():
        host = os.getenv("DB_HOST")  # Hidden dependency
        port = os.getenv("DB_PORT")
        return create_connection(host, port)
    ```
  - Refactored:
    ```python
    # ✅ Explicit configuration parameter
    @dataclass(frozen=True)
    class DatabaseConfig:
        host: str
        port: int

    def connect_database(config: DatabaseConfig) -> Connection:
        return create_connection(config.host, config.port)

    # Configuration loaded at entry point
    def main():
        import os
        config = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432))
        )
        conn = connect_database(config)
    ```
  - Configuration loading isolated to entry point (I/O boundary)
- **Result**: Environment variables accessed explicitly at boundaries

**Branch 5: If import_side_effects**
- **Then**: `isolate_import_effects`
- **Details**: Flag imports that have side effects
  - Problematic imports:
    ```python
    # ❌ Import with side effect
    import logging
    logging.basicConfig(level=logging.INFO)  # Side effect at module level!

    # ❌ Import that modifies global state
    import sys
    sys.path.append("/custom/path")  # Modifies global
    ```
  - Resolution:
    - Move initialization to entry point (main function)
    - Warn user about import side effects
- **Result**: Import side effects documented, user notified

**Branch 6: If scope_clean**
- **Then**: `mark_compliant`
- **Details**: Function has no global state access
  - Update database:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
  - No refactoring needed
- **Result**: Function validated as stateless

**Fallback**: `prompt_user`
- **Details**: Uncertain about global dependencies
  - Scenarios requiring user input:
    - Complex data flow with unclear scope
    - Dynamic import or attribute access
    - Metaprogramming (eval, exec)
  - Prompt example:
    ```
    Unable to determine if function accesses global state

    Function: calculate_total
    File: src/billing/invoice.py

    Potential global references:
    • config (line 15)
    • TAX_RATE (line 18)

    Are these global variables? (y/n):
    If yes, should they be:
    1. Converted to parameters
    2. Made into immutable constants
    3. Left as-is (user confirmation required)
    ```
- **Result**: User clarifies ambiguity

---

## Examples

### ✅ Compliant Usage

**Eliminating Global Variable:**
```python
# Initial code (non-compliant)
DEBUG_MODE = True  # Global variable

def log_message(message):
    if DEBUG_MODE:  # Global access
        print(f"[DEBUG] {message}")
    return message

# AI calls: fp_state_elimination()

# Workflow:
# 1. scan_scope:
#    - Detects DEBUG_MODE is global variable
#    - Reference found on line 5
#
# 2. global_references: inline_dependencies
#    - Add debug_mode parameter
#    - Update function signature
#    - Update function body
#
# Refactored code (compliant)
def log_message(message: str, debug_mode: bool) -> str:
    if debug_mode:  # Parameter, not global
        print(f"[DEBUG] {message}")
    return message

# Call site updated
result = log_message("Starting process", debug_mode=DEBUG_MODE)

# Database updated
UPDATE functions
SET purity_level = 'pure',
    parameters = '["message: str", "debug_mode: bool"]',
    side_effects_json = '{"global_state": false}'
WHERE name = 'log_message'

# Result:
# ✅ Global access eliminated
# ✅ Function signature explicit
# ✅ Function now pure (deterministic given inputs)
```

---

**Converting Mutable Global to Immutable:**
```python
# Initial code (non-compliant)
cache = {}  # Mutable global state

def get_cached_value(key):
    if key in cache:
        return cache[key]
    value = expensive_computation(key)
    cache[key] = value  # Mutation of global
    return value

# AI calls: fp_state_elimination()

# Workflow:
# 1. scan_scope:
#    - Detects cache is mutable global
#    - Both read and write access
#
# 2. mutable_static_data: convert_to_immutable
#    - Strategy: Functional state threading
#    - Return new cache with updated value
#
# Refactored code (compliant)
@dataclass(frozen=True)
class CacheState:
    data: dict[str, Any]

def get_cached_value(key: str, cache: CacheState) -> tuple[Any, CacheState]:
    if key in cache.data:
        return cache.data[key], cache  # No mutation

    value = expensive_computation(key)
    new_data = {**cache.data, key: value}  # New dict
    new_cache = CacheState(data=new_data)
    return value, new_cache

# Call site (functional state threading)
cache = CacheState(data={})
value1, cache = get_cached_value("key1", cache)
value2, cache = get_cached_value("key2", cache)

# Result:
# ✅ No mutable global state
# ✅ Cache state explicit in signature
# ✅ Function pure (returns new state instead of mutating)
```

---

**Eliminating Singleton Pattern:**
```python
# Initial code (non-compliant)
class Logger:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance

    def log(self, message):
        print(f"[LOG] {message}")

def process_data(data):
    logger = Logger.get_instance()  # Hidden dependency
    logger.log("Processing data")
    return transform(data)

# AI calls: fp_state_elimination()

# Workflow:
# 1. scan_scope:
#    - Detects Logger.get_instance() is singleton access
#    - Hidden global state
#
# 2. singleton_pattern: dependency_injection
#    - Add logger parameter
#    - Update call sites
#
# Refactored code (compliant)
def log_message(message: str) -> None:
    print(f"[LOG] {message}")  # Simple function

def process_data(data: Any, log_fn: Callable[[str], None]) -> Any:
    log_fn("Processing data")  # Explicit dependency
    return transform(data)

# Call site
result = process_data(data, log_message)

# For testing: inject mock logger
def mock_logger(message: str) -> None:
    pass  # No-op for tests

test_result = process_data(test_data, mock_logger)

# Result:
# ✅ Singleton eliminated
# ✅ Logger passed explicitly
# ✅ Testable (can inject mocks)
```

---

### ❌ Non-Compliant Usage

**Leaving Global Access:**
```python
# ❌ Global variable accessed without refactoring
MAX_RETRIES = 3

def attempt_request(url):
    for i in range(MAX_RETRIES):  # Global access
        try:
            return fetch(url)
        except Exception:
            continue
    return None

# Why Non-Compliant:
# - MAX_RETRIES is global variable
# - Function depends on external state
# - Not pure (behavior changes if global changes)
```

**Corrected:**
```python
# ✅ Explicit parameter
def attempt_request(url: str, max_retries: int = 3) -> Optional[Response]:
    for i in range(max_retries):  # Parameter
        try:
            return fetch(url)
        except Exception:
            continue
    return None
```

---

## Edge Cases

### Edge Case 1: Constant vs Mutable Global

**Issue**: Global constant (immutable) vs mutable global variable

**Handling**:
```python
# Immutable constant (allowed)
MAX_CONNECTIONS = 100  # UPPERCASE convention, never reassigned
PI = 3.14159

# Mutable global (must refactor)
connection_pool = []  # List can be mutated

# Rule: If global is UPPERCASE and never mutated, it's a constant (acceptable)
if is_constant(variable_name):
    # Allow as constant
    mark_compliant()
else:
    # Refactor to parameter
    inline_dependencies()
```

**Directive Action**: Allow immutable constants, refactor mutable globals.

---

### Edge Case 2: Module-Level Configuration

**Issue**: Configuration loaded once at module import

**Handling**:
```python
# Module-level config load
import json
with open("config.json") as f:
    CONFIG = json.load(f)  # Side effect at import!

# Resolution:
# 1. Move to entry point
# 2. Pass as parameter
def main():
    import json
    with open("config.json") as f:
        config = json.load(f)

    # Pass config explicitly
    result = process_data(data, config)
```

**Directive Action**: Flag import-time side effects, suggest entry-point initialization.

---

### Edge Case 3: Closure Capturing Global

**Issue**: Closure captures global variable

**Handling**:
```python
# Closure captures global
threshold = 100

def create_filter():
    def filter_fn(x):
        return x > threshold  # Captures global
    return filter_fn

# Resolution: Pass captured value explicitly
def create_filter(threshold: int):
    def filter_fn(x: int) -> bool:
        return x > threshold  # Captures parameter, not global
    return filter_fn
```

**Directive Action**: Parameterize closure-captured globals.

---

## Related Directives

- **Called By**:
  - `fp_purity` - Eliminates global state as part of purity enforcement
  - `project_compliance_check` - Scans for global variable access
  - `project_file_write` - Validates stateless functions before writing
- **Calls**:
  - Database helpers - Updates functions table
  - `project_notes_log` - Logs refactoring decisions
- **Related**:
  - `fp_side_effect_detection` - Detects I/O side effects
  - `fp_immutability` - Ensures global constants are immutable

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: UPDATE purity_level, side_effects_json, parameters after refactoring
- **`notes`**: INSERT clarifications about global state elimination decisions

---

## Testing

1. **Detect global access** → Global reference identified
   ```python
   global_var = 10
   def use_global():
       return global_var + 5

   references = identify_global_references(use_global)
   assert "global_var" in references
   ```

2. **Refactor global to parameter** → Function signature updated
   ```python
   refactored = inline_dependencies(use_global)
   assert "global_var" in refactored.parameters
   ```

3. **Constant allowed** → No refactoring for immutable constants
   ```python
   MAX_SIZE = 100
   def check_size(value):
       return value < MAX_SIZE

   result = fp_state_elimination(check_size)
   assert result.compliant == True  # Constant allowed
   ```

---

## Common Mistakes

- ❌ **Treating constants as mutable globals** - Allow UPPERCASE constants
- ❌ **Not updating call sites** - Must propagate parameter changes
- ❌ **Ignoring closures** - Closures can capture global state
- ❌ **Not checking import side effects** - Module-level code can have side effects

---

## Roadblocks and Resolutions

### Roadblock 1: global_dependency
**Issue**: Function accesses global variable
**Resolution**: Pass as explicit parameter via inline_dependencies

### Roadblock 2: static_mutable_data
**Issue**: Global mutable state (list, dict, object)
**Resolution**: Refactor to immutable constant or functional state threading

### Roadblock 3: singleton_access
**Issue**: Function uses singleton pattern
**Resolution**: Replace with dependency injection

---

## References

None
---

*Part of AIFP v1.0 - Core FP directive for eliminating global state and ensuring stateless functions*
