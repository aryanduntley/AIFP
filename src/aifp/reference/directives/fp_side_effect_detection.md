# Directive: fp_side_effect_detection

**Type**: FP
**Level**: 1
**Parent Directive**: None
**Priority**: CRITICAL - Core purity enforcement

---

## Purpose

The `fp_side_effect_detection` directive **scans function bodies for I/O operations, print statements, logging, or mutation** and isolates effects via wrappers or dedicated effect functions. This directive is **essential for maintaining functional purity** because:

- **Predictability**: Side-effect-free functions are deterministic and testable
- **Composability**: Pure functions compose safely without hidden interactions
- **Concurrency safety**: No side effects means parallel execution is safe
- **AI reasoning**: Clear separation of logic and effects aids AI understanding

This directive detects and isolates:
- **I/O operations** - File read/write, network calls, database queries
- **Console output** - print(), console.log(), cout, etc.
- **Logging** - logger.info(), logging.debug(), etc.
- **Mutations** - Modifying passed data structures
- **Random number generation** - Non-deterministic operations
- **System calls** - Time, environment, process operations

**Isolation approach**: Separate pure logic from side-effecting operations via effect boundaries.

---

## When to Apply

This directive applies when:
- **Function contains I/O** - File operations, network requests, database access
- **Function prints/logs** - Console output, logging statements
- **Function mutates data** - Modifies passed arguments or external state
- **During compliance checks** - `project_compliance_check` scans for side effects
- **Before file write** - `project_file_write` validates functions are pure
- **User requests isolation** - "Separate I/O from logic", "Make function pure"

---

## Workflow

### Trunk: scan_for_side_effects

Scans function AST for side-effecting operations.

**Steps**:
1. **Parse function body** - Extract all operations
2. **Identify side effects** - Match against known side-effect patterns
3. **Classify effect type** - I/O, logging, mutation, etc.
4. **Route to isolation** - Wrap or extract effects

### Branches

**Branch 1: If io_operations_found**
- **Then**: `wrap_in_effect_function`
- **Details**: Isolate I/O operations into dedicated effect functions
  - I/O patterns detected:
    ```python
    # File I/O
    open(), read(), write(), with open(...)

    # Network I/O
    requests.get(), urllib.request.urlopen(), http.client

    # Database I/O
    cursor.execute(), connection.query(), db.insert()
    ```
  - Refactoring strategy:
    ```python
    # ❌ Before: Logic mixed with I/O
    def process_file(filename):
        with open(filename) as f:  # I/O
            data = f.read()
        processed = transform(data)  # Pure logic
        return processed

    # ✅ After: Separated logic and I/O
    # Pure logic (no side effects)
    def transform_data(data: str) -> str:
        return transform(data)

    # I/O boundary (side effects isolated)
    def process_file(filename: str) -> str:
        with open(filename) as f:
            data = f.read()
        return transform_data(data)
    ```
  - Update database:
    ```sql
    -- Mark pure function
    UPDATE functions
    SET purity_level = 'pure',
        side_effects_json = '{"io": false, "mutation": false}',
        updated_at = CURRENT_TIMESTAMP
    WHERE name = 'transform_data';

    -- Mark effectful function
    UPDATE functions
    SET purity_level = 'effectful',
        side_effects_json = '{"io": true, "mutation": false}',
        updated_at = CURRENT_TIMESTAMP
    WHERE name = 'process_file';
    ```
- **Result**: Logic separated from I/O, pure function created

**Branch 2: If logging_detected**
- **Then**: `redirect_to_logger_function`
- **Details**: Extract logging to separate function or effect handler
  - Logging patterns:
    ```python
    print(), logging.info(), logger.debug(), console.log()
    ```
  - Refactoring strategies:
    - **Strategy 1**: Pass logger as parameter
      ```python
      # ❌ Before: Logging mixed in
      def calculate_total(items):
          print(f"Calculating total for {len(items)} items")  # Side effect
          return sum(items)

      # ✅ After: Logger passed explicitly
      def calculate_total(items: list[int], log_fn: Callable[[str], None]) -> int:
          log_fn(f"Calculating total for {len(items)} items")
          return sum(items)

      # Call with real logger
      calculate_total([1, 2, 3], lambda msg: print(msg))

      # Call with no-op (testing)
      calculate_total([1, 2, 3], lambda msg: None)
      ```
    - **Strategy 2**: Remove logging (pure version)
      ```python
      # ✅ Pure function (no logging)
      def calculate_total(items: list[int]) -> int:
          return sum(items)

      # Logging wrapper (separate)
      def calculate_total_with_logging(items: list[int]) -> int:
          print(f"Calculating total for {len(items)} items")
          return calculate_total(items)
      ```
    - **Strategy 3**: Return tuple (value + log messages)
      ```python
      # ✅ Return log messages instead of printing
      def calculate_total(items: list[int]) -> tuple[int, list[str]]:
          log_messages = [f"Calculating total for {len(items)} items"]
          total = sum(items)
          return total, log_messages

      # Caller handles logging
      result, logs = calculate_total([1, 2, 3])
      for log in logs:
          print(log)
      ```
  - Choose strategy based on logging requirements
- **Result**: Logging isolated or parameterized

**Branch 3: If mutation_detected**
- **Then**: `refactor_to_immutable`
- **Details**: Replace mutation with new data structure creation
  - Mutation patterns:
    ```python
    list.append(), dict[key] = value, obj.field = value, arr[i] = x
    ```
  - Refactoring:
    ```python
    # ❌ Before: Mutates input
    def add_item(items: list, item: int) -> list:
        items.append(item)  # Mutation!
        return items

    # ✅ After: Creates new list
    def add_item(items: list, item: int) -> list:
        return items + [item]  # New list

    # Or using list comprehension/spread
    def add_item(items: list, item: int) -> list:
        return [*items, item]
    ```
  - Update database:
    ```sql
    UPDATE functions
    SET purity_level = 'pure',
        side_effects_json = '{"mutation": false}',
        updated_at = CURRENT_TIMESTAMP
    WHERE name = 'add_item'
    ```
- **Result**: Mutation eliminated, function returns new data

**Branch 4: If random_number_generation**
- **Then**: `parameterize_random_seed`
- **Details**: Make non-deterministic operations deterministic
  - Random patterns:
    ```python
    random.randint(), random.choice(), uuid.uuid4(), time.time()
    ```
  - Refactoring:
    ```python
    # ❌ Before: Non-deterministic
    import random

    def get_random_id():
        return random.randint(1000, 9999)  # Different each call

    # ✅ After: Deterministic with seed
    def get_random_id(seed: int) -> int:
        rng = random.Random(seed)
        return rng.randint(1000, 9999)  # Same output for same seed

    # Or: Pass value explicitly
    def process_with_id(id: int, data: Any) -> Any:
        # ID passed explicitly, not generated
        return transform(data, id)
    ```
  - For truly random needs, isolate at I/O boundary:
    ```python
    # Pure logic (deterministic)
    def process_data(data: Any, id: int) -> Any:
        return transform(data, id)

    # I/O boundary (generates random ID)
    def main():
        import random
        id = random.randint(1000, 9999)  # Generated at boundary
        result = process_data(data, id)  # Pure logic
    ```
- **Result**: Randomness parameterized or isolated

**Branch 5: If side_effects_isolated**
- **Then**: `update_side_effects_json`
- **Details**: Record which side effects are present/absent
  - Update functions table:
    ```sql
    UPDATE functions
    SET side_effects_json = '{
      "io": false,
      "mutation": false,
      "logging": false,
      "random": false,
      "system_calls": false
    }',
    purity_level = 'pure',
    updated_at = CURRENT_TIMESTAMP
    WHERE name = ? AND file_id = ?
    ```
  - Links to project_update_db for database synchronization
  - side_effects_json provides detailed effect analysis
- **Result**: Database updated with effect analysis

**Branch 6: If low_confidence**
- **Then**: `prompt_user`
- **Details**: Unable to determine if operation is side effect
  - Ambiguous cases:
    - Dynamic attribute access: `getattr(obj, 'method')()`
    - Imported functions with unknown behavior
    - Language-specific quirks
  - Prompt user:
    ```
    Unable to determine if operation has side effects

    Function: process_data
    File: src/processor.py
    Line 42: result = obj.process()

    Does obj.process() have side effects? (y/n):
    If yes, what type:
    1. I/O (file, network, database)
    2. Logging/printing
    3. Mutation
    4. Other
    ```
- **Result**: User clarifies ambiguous operations

**Fallback**: `mark_as_pure_if_none_found`
- **Details**: No side effects detected, function is pure
  - Update database:
    ```sql
    UPDATE functions
    SET purity_level = 'pure',
        side_effects_json = 'null',
        updated_at = CURRENT_TIMESTAMP
    WHERE name = ? AND file_id = ?
    ```
  - No refactoring needed
- **Result**: Function validated as pure

---

## Examples

### ✅ Compliant Usage

**Isolating File I/O:**
```python
# Initial code (non-compliant)
def process_config(filename):
    with open(filename) as f:  # I/O side effect
        config = json.load(f)
    validated = validate_config(config)  # Pure
    return validated

# AI calls: fp_side_effect_detection()

# Workflow:
# 1. scan_for_side_effects:
#    - Detects open() call (file I/O)
#    - Detects json.load() (I/O)
#
# 2. io_operations_found: wrap_in_effect_function
#    - Separate pure validation from I/O
#    - Create pure function for validation
#
# Refactored code (compliant)
# Pure logic (no side effects)
def validate_config(config: dict) -> dict:
    # Validation logic here
    return config if is_valid(config) else raise_error()

# I/O boundary (side effects)
def load_config(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)

# Main orchestration
def process_config(filename: str) -> dict:
    config = load_config(filename)  # I/O
    return validate_config(config)   # Pure

# Database updates
UPDATE functions
SET purity_level = 'pure', side_effects_json = '{"io": false}'
WHERE name = 'validate_config';

UPDATE functions
SET purity_level = 'effectful', side_effects_json = '{"io": true}'
WHERE name = 'load_config';

# Result:
# ✅ Pure logic separated from I/O
# ✅ validate_config is testable without files
# ✅ Clear effect boundaries
```

---

**Eliminating Print Statements:**
```python
# Initial code (non-compliant)
def calculate_total(items):
    print(f"Processing {len(items)} items")  # Side effect
    total = sum(item.price * item.quantity for item in items)
    print(f"Total: {total}")  # Side effect
    return total

# AI calls: fp_side_effect_detection()

# Workflow:
# 1. scan_for_side_effects:
#    - Detects print() calls (logging side effect)
#
# 2. logging_detected: redirect_to_logger_function
#    - Strategy: Pass logger as parameter
#
# Refactored code (compliant)
def calculate_total(
    items: list[Item],
    log_fn: Callable[[str], None] = lambda _: None  # Default no-op
) -> float:
    log_fn(f"Processing {len(items)} items")
    total = sum(item.price * item.quantity for item in items)
    log_fn(f"Total: {total}")
    return total

# Production: with logging
result = calculate_total(items, print)

# Testing: without logging
result = calculate_total(items)  # Uses no-op default

# Or: Pure version
def calculate_total_pure(items: list[Item]) -> float:
    return sum(item.price * item.quantity for item in items)

# Result:
# ✅ Logging parameterized (dependency injection)
# ✅ Testable without side effects
# ✅ Can be pure with no-op logger
```

---

**Removing Mutation:**
```python
# Initial code (non-compliant)
def filter_active_users(users: list[User]) -> list[User]:
    result = []
    for user in users:
        if user.is_active:
            result.append(user)  # Mutation of result list
    return result

# AI calls: fp_side_effect_detection()

# Workflow:
# 1. scan_for_side_effects:
#    - Detects list.append() (mutation)
#
# 2. mutation_detected: refactor_to_immutable
#    - Use list comprehension (no mutation)
#
# Refactored code (compliant)
def filter_active_users(users: list[User]) -> list[User]:
    return [user for user in users if user.is_active]  # No mutation

# Or using filter()
def filter_active_users(users: list[User]) -> list[User]:
    return list(filter(lambda u: u.is_active, users))

# Database update
UPDATE functions
SET purity_level = 'pure',
    side_effects_json = '{"mutation": false}',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'filter_active_users';

# Result:
# ✅ No mutation
# ✅ Pure function (same input → same output)
# ✅ Safe for concurrent use
```

---

### ❌ Non-Compliant Usage

**Leaving I/O Mixed with Logic:**
```python
# ❌ I/O not isolated
def validate_and_save(data):
    # Logic
    if not is_valid(data):
        raise ValueError("Invalid")

    # I/O (should be separated!)
    with open("output.txt", "w") as f:
        f.write(str(data))

    return True

# Why Non-Compliant:
# - Validation logic mixed with file I/O
# - Cannot test validation without file system
# - Function has hidden side effect
```

**Corrected:**
```python
# ✅ Separated logic and I/O
def validate(data: Any) -> bool:
    if not is_valid(data):
        raise ValueError("Invalid")
    return True

def save_to_file(data: Any, filename: str) -> None:
    with open(filename, "w") as f:
        f.write(str(data))

# Main orchestration
def validate_and_save(data: Any) -> None:
    validate(data)  # Pure
    save_to_file(data, "output.txt")  # I/O
```

---

## Edge Cases

### Edge Case 1: Pure Function Calling Impure Function

**Issue**: Pure function calls impure helper

**Handling**:
```python
# Function appears pure but calls impure helper
def process(data):
    return helper(data)  # helper() has I/O!

def helper(data):
    with open("log.txt", "a") as f:
        f.write(f"Processing {data}")
    return transform(data)

# Resolution: Mark both as impure, refactor both
```

**Directive Action**: Scan transitive dependencies, propagate impurity.

---

### Edge Case 2: Conditional Side Effects

**Issue**: Side effect only in some code paths

**Handling**:
```python
# Side effect only if condition true
def process(data, debug=False):
    result = transform(data)
    if debug:
        print(f"Result: {result}")  # Conditional side effect
    return result

# Resolution: Still impure (has side effect in some paths)
# Refactor to pass logger
```

**Directive Action**: Any side effect makes function impure.

---

### Edge Case 3: Hidden I/O in Library Call

**Issue**: Library function has hidden I/O

**Handling**:
```python
# Library call with hidden I/O
import requests

def get_data(url):
    return requests.get(url).json()  # Hidden network I/O

# Resolution: Mark as effectful
UPDATE functions
SET purity_level = 'effectful',
    side_effects_json = '{"io": true, "network": true}'
WHERE name = 'get_data';
```

**Directive Action**: Flag library calls with known side effects.

---

## Related Directives

- **Called By**:
  - `fp_purity` - Part of purity enforcement
  - `project_compliance_check` - Scans for side effects
  - `project_file_write` - Validates before writing
- **Calls**:
  - `project_update_db` - Updates functions table
  - `fp_io_isolation` - Escalates complex I/O isolation
  - `fp_logging_safety` - Handles logging-specific refactoring
- **Related**:
  - `fp_state_elimination` - Eliminates global state
  - `fp_immutability` - Eliminates mutation

---

## Helper Functions Used

- `parse_function_ast(code: str) -> AST` - Parse function
- `detect_io_operations(ast: AST) -> list[IOOp]` - Find I/O calls
- `detect_mutations(ast: AST) -> list[Mutation]` - Find mutations
- `detect_logging(ast: AST) -> list[LogCall]` - Find print/log calls
- `is_pure_library_function(func_name: str) -> bool` - Check library purity

---

## Database Operations

This directive updates the following tables:

- **`functions`**: UPDATE purity_level, side_effects_json after refactoring
- **`notes`**: INSERT clarifications about side effect isolation

---

## Testing

1. **Detect I/O** → I/O operation identified
   ```python
   def read_file(filename):
       with open(filename) as f:
           return f.read()

   io_ops = detect_io_operations(read_file)
   assert len(io_ops) > 0
   ```

2. **Detect logging** → Print statement found
   ```python
   def log_process():
       print("Processing")

   logs = detect_logging(log_process)
   assert len(logs) > 0
   ```

3. **No side effects** → Function marked pure
   ```python
   def add(x, y):
       return x + y

   result = fp_side_effect_detection(add)
   assert result.purity_level == 'pure'
   ```

---

## Common Mistakes

- ❌ **Ignoring transitive side effects** - Calling impure function makes caller impure
- ❌ **Not checking library functions** - Some libraries have hidden I/O
- ❌ **Treating conditional side effects as pure** - Any side effect makes function impure
- ❌ **Missing mutation in loops** - Mutation inside loop is still mutation

---

## Roadblocks and Resolutions

### Roadblock 1: untracked_side_effect
**Issue**: Side effect not in known patterns
**Resolution**: Use effect wrapper or prompt user

### Roadblock 2: logging_in_function
**Issue**: Print/log statements mixed with logic
**Resolution**: Route through functional logger (parameterize or separate)

### Roadblock 3: hidden_io
**Issue**: Library function has hidden I/O
**Resolution**: Escalate to fp_io_isolation directive

### Roadblock 4: language_specific_io
**Issue**: Language-specific I/O pattern
**Resolution**: Use fp_cross_language_wrappers

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-helpers)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#purity)
- [JSON Definition](../../../docs/directives-json/directives-fp-core.json)
- [Database Schema](../../../docs/db-schema/schemaExampleProject.sql#functions-table)

---

*Part of AIFP v1.0 - Core FP directive for detecting and isolating side effects*
