# Directive: fp_optionals

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: HIGH - Critical for null safety

---

## Purpose

The `fp_optionals` directive enforces the use of Option/Maybe types instead of null values or exceptions for handling missing or absent data. This directive promotes **predictable, explicit handling of optional values** throughout the codebase, eliminating null pointer exceptions and making data absence a first-class citizen in the type system.

Option types make optionality **visible in function signatures**, enabling:
- **Type Safety**: Compiler/type checker enforces handling of None/Some cases
- **Explicit Absence**: Missing data is explicit, not hidden as null
- **Composability**: Options chain with map/flatMap for clean data pipelines
- **No Surprises**: No runtime null pointer exceptions
- **Self-Documenting**: Function signature shows whether value might be absent

This directive complements `fp_null_elimination` (which removes null literals) and `fp_result_types` (which handles errors). Together, they create a comprehensive declarative error handling strategy.

---

## When to Apply

This directive applies when:
- **Writing functions that might return no value** - Use Option instead of null
- **Handling optional parameters** - Wrap in Option type
- **Database queries that might return nothing** - Return Option instead of null
- **Dictionary/map lookups** - Return Option for missing keys
- **Array/list element access** - Return Option for out-of-bounds
- **Called by project directives**:
  - `project_file_write` - Validates optional handling before writing
  - `project_compliance_check` - Scans for Option usage compliance
  - `fp_null_elimination` - Works together to remove all null usage

---

## Workflow

### Trunk: scan_for_null_usage

Scans function code to detect null returns, null checks, and missing Option type usage.

**Steps**:
1. **Parse function body** - Extract all return statements and conditionals
2. **Identify null returns** - Find `return null`, `return None`, `return undefined`
3. **Identify null checks** - Find `if x is None`, `if x == null`, `x === undefined`
4. **Identify nullable return types** - Functions with `Optional` or `?` annotations but not using Option type
5. **Evaluate compliance** - Classify as compliant, needs-refactoring, or uncertain

### Branches

**Branch 1: If null_detected**
- **Then**: `wrap_in_optional`
- **Details**: Convert null returns to Option type
  - Replace `return null` with `return Option.none()`
  - Replace `return value` with `return Option.some(value)`
  - Update function signature to return `Option[T]`
  - Add type imports if needed
- **Result**: Returns refactored code with Option type

**Branch 2: If implicit_null_check**
- **Then**: `convert_to_option_pattern`
- **Details**: Replace imperative null checks with declarative Option handling
  - Convert `if x is None: ... else: ...` to `x.map(lambda v: ...).or_else(...)`
  - Convert `x if x is not None else default` to `Option.from_nullable(x).or_else(default)`
  - Chain multiple checks with `flatMap`
- **Result**: Returns declarative Option-based code

**Branch 3: If throw_instead_of_optional**
- **Then**: `replace_exception_with_option`
- **Details**: Functions that throw on missing data should return Option
  - Convert `raise KeyError` to `return Option.none()`
  - Convert `raise ValueError("not found")` to `return Option.none()`
  - Update callers to handle Option return
- **Result**: Returns exception-free code with Option

**Branch 4: If compliant**
- **Then**: `mark_compliant`
- **Details**: Function already uses Option types correctly
  - No refactoring needed
  - Mark as compliant in analysis
- **Result**: Function passes Option compliance check

**Fallback**: `prompt_user`
- **Details**: Uncertain about refactoring
  - Present findings to user
  - Ask: "Convert null handling to Option type?"
  - Log uncertainty to notes table
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Option Return (Passes):**
```python
from typing import Optional as Option

def find_user_by_id(user_id: int) -> Option[User]:
    """
    Find user by ID using Option type.

    Returns Option.some(user) if found, Option.none() if not found.
    Pure function with explicit absence handling.
    """
    users = get_all_users()  # Pure function returning list

    for user in users:
        if user.id == user_id:
            return Option.some(user)

    return Option.none()

# Usage with pattern matching
result = find_user_by_id(123)
match result:
    case Some(user):
        print(f"Found: {user.name}")
    case None:
        print("User not found")
```

**Why Compliant**:
- Returns `Option[User]` instead of `User | None`
- Explicit `Option.some()` and `Option.none()`
- No null values
- Type-safe handling at call site

---

**Option with map/flatMap (Passes):**
```python
from typing import Optional as Option

def get_user_email(user_id: int) -> Option[str]:
    """
    Get user email using Option chaining.

    Chains multiple optional operations declaratively.
    """
    return (
        find_user_by_id(user_id)
        .flatMap(lambda user: user.email)  # email is Option[str]
        .map(lambda email: email.lower())   # Transform if present
    )

# Usage with or_else
email = get_user_email(123).or_else("no-reply@example.com")
```

**Why Compliant**:
- Chains Option operations declaratively
- No null checks
- Readable pipeline
- Type-safe transformations

---

### ❌ Non-Compliant Code

**Null Return (Violation):**
```python
# ❌ VIOLATION: Returns None instead of Option
def find_user_by_id(user_id: int) -> User | None:
    users = get_all_users()

    for user in users:
        if user.id == user_id:
            return user

    return None  # ← Null return (hidden optionality)
```

**Why Non-Compliant**:
- Returns `None` (null value)
- Optionality not explicit in handling
- Caller must remember to check for None
- Type hint shows `| None` but doesn't enforce safe handling

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Returns Option type
from typing import Optional as Option

def find_user_by_id(user_id: int) -> Option[User]:
    """Find user by ID. Returns Option.some(user) or Option.none()."""
    users = get_all_users()

    for user in users:
        if user.id == user_id:
            return Option.some(user)

    return Option.none()
```

---

**Imperative Null Check (Violation):**
```python
# ❌ VIOLATION: Imperative null checking
def get_user_name(user_id: int) -> str:
    user = find_user_by_id(user_id)  # Returns User | None

    if user is not None:  # ← Imperative null check
        return user.name
    else:
        return "Unknown"
```

**Why Non-Compliant**:
- Imperative if/else for null checking
- Not composable
- Verbose and error-prone
- Missing type safety

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Declarative Option handling
def get_user_name(user_id: int) -> str:
    """Get user name with Option chaining."""
    return (
        find_user_by_id(user_id)
        .map(lambda user: user.name)
        .or_else("Unknown")
    )
```

---

**Exception on Missing (Violation):**
```python
# ❌ VIOLATION: Throws exception for missing data
def get_config_value(key: str) -> str:
    config = load_config()

    if key not in config:
        raise KeyError(f"Config key '{key}' not found")  # ← Exception

    return config[key]
```

**Why Non-Compliant**:
- Throws exception for normal case (missing key)
- Forces caller to use try/catch
- Not composable in pipelines
- Violates FP error handling

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Returns Option for missing key
def get_config_value(key: str) -> Option[str]:
    """Get config value. Returns Option.none() if key missing."""
    config = load_config()

    if key in config:
        return Option.some(config[key])
    else:
        return Option.none()

# Usage with default
value = get_config_value("api_key").or_else("default_key")
```

---

## Edge Cases

### Edge Case 1: Nested Options

**Issue**: Function returns `Option[Option[T]]` (nested Options)

**Handling**:
```python
# ❌ Bad: Nested Options are confusing
def find_user_preference(user_id: int, key: str) -> Option[Option[str]]:
    user = find_user_by_id(user_id)  # Returns Option[User]
    return user.map(lambda u: u.preferences.get(key))  # Returns Option[Option[str]]

# ✅ Good: Flatten with flatMap
def find_user_preference(user_id: int, key: str) -> Option[str]:
    """Find user preference. Flattens nested Options."""
    return (
        find_user_by_id(user_id)
        .flatMap(lambda u: u.preferences.get(key))  # flatMap flattens
    )
```

**Directive Action**: Use `flatMap` instead of `map` when inner operation returns Option.

---

### Edge Case 2: Optional Parameters

**Issue**: Function parameters might be absent

**Handling**:
```python
# ❌ Bad: Uses None for optional parameters
def format_name(first: str, middle: str | None, last: str) -> str:
    if middle is not None:
        return f"{first} {middle} {last}"
    return f"{first} {last}"

# ✅ Good: Uses Option for optional parameters
def format_name(first: str, middle: Option[str], last: str) -> str:
    """Format name with optional middle name."""
    middle_part = middle.map(lambda m: f" {m}").or_else("")
    return f"{first}{middle_part} {last}"
```

**Directive Action**: Convert optional parameters from `T | None` to `Option[T]`.

---

### Edge Case 3: Collections with Missing Elements

**Issue**: Array access might be out of bounds

**Handling**:
```python
# ❌ Bad: Returns None or raises IndexError
def get_first_item(items: list[T]) -> T | None:
    if len(items) > 0:
        return items[0]
    return None

# ✅ Good: Returns Option
def get_first_item(items: list[T]) -> Option[T]:
    """Get first item from list. Returns Option.none() if empty."""
    if len(items) > 0:
        return Option.some(items[0])
    return Option.none()

# ✅ Better: Use helper function
def head(items: list[T]) -> Option[T]:
    """Functional head operation returning Option."""
    return Option.some(items[0]) if items else Option.none()
```

**Directive Action**: Wrap collection access in Option type.

---

### Edge Case 4: Multiple Options to Combine

**Issue**: Need to combine multiple Option values

**Handling**:
```python
# ❌ Bad: Nested if statements
def combine_values(opt1: Option[int], opt2: Option[int]) -> int:
    if opt1.is_some():
        if opt2.is_some():
            return opt1.unwrap() + opt2.unwrap()
    return 0

# ✅ Good: Use applicative functor pattern
def combine_values(opt1: Option[int], opt2: Option[int]) -> Option[int]:
    """
    Combine two Options using applicative pattern.

    Returns Some(sum) if both present, None otherwise.
    """
    return opt1.flatMap(lambda v1:
        opt2.map(lambda v2: v1 + v2)
    )

# Usage
result = combine_values(Option.some(3), Option.some(5))
# Returns: Option.some(8)

result = combine_values(Option.some(3), Option.none())
# Returns: Option.none()
```

**Directive Action**: Use `flatMap` chaining or applicative pattern for combining Options.

---

## Related Directives

- **Depends On**: None (foundational error handling directive)
- **Triggers**:
  - `fp_null_elimination` - Removes null literals after Option types introduced
  - `fp_result_types` - Option for absence, Result for errors (use both)
  - `fp_error_pipeline` - Options chain with flatMap in pipelines
- **Called By**:
  - `project_file_write` - Validates Option usage before file writes
  - `project_compliance_check` - Verifies project-wide Option compliance
  - `fp_monadic_composition` - Options are monads, compose with other monads
- **Escalates To**:
  - `fp_language_standardization` - For language-specific Option implementations

---

## Helper Functions Used

- `detect_null_returns(ast: AST) -> list[NullReturn]` - Finds null return statements
- `detect_null_checks(ast: AST) -> list[NullCheck]` - Finds imperative null checks
- `refactor_to_option(code: str, violations: list) -> str` - Refactors to Option type
- `generate_option_imports(language: str) -> str` - Generates language-specific Option imports
- `update_functions_table(func_id: int, option_compliant: bool)` - Updates project.db

---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `error_handling_pattern = 'option'` for compliant functions
- **`functions`**: Updates `type_annotations_json` with Option type info
- **`notes`**: Logs Option compliance issues with `note_type = 'compliance'`
- **`interactions`**: Tracks Option chaining between functions (flatMap dependencies)

---

## Testing

How to verify this directive is working:

1. **Write function with null return** → Directive detects and refactors
   ```python
   # Input (null return)
   def find_item(key): return items.get(key) or None

   # Expected output (Option)
   def find_item(key) -> Option[Item]:
       result = items.get(key)
       return Option.some(result) if result else Option.none()
   ```

2. **Write function with Option** → Directive marks compliant
   ```python
   def find_item(key) -> Option[Item]:
       return Option.from_nullable(items.get(key))
   # ✅ Already compliant, no changes
   ```

3. **Check database** → Verify `functions.error_handling_pattern = 'option'`
   ```sql
   SELECT name, error_handling_pattern, type_annotations_json
   FROM functions
   WHERE name = 'find_item';
   -- Expected: error_handling_pattern='option'
   ```

---

## Common Mistakes

- ❌ **Using `Optional[T]` type hint but returning None** - Type hint alone doesn't provide safety
- ❌ **Unwrapping Option with `.unwrap()` without checking** - Defeats purpose of Option
- ❌ **Returning `Option[None]`** - Should return `Option.none()` not `Option.some(None)`
- ❌ **Using Option for errors** - Use Result/Either for operations that can fail
- ❌ **Mixing null and Option** - Must eliminate all nulls when using Options

---

## Roadblocks and Resolutions

### Roadblock 1: null_return
**Issue**: Function returns null instead of Option
**Resolution**: Replace with Option.some() / Option.none() pattern

### Roadblock 2: implicit_null_check
**Issue**: Imperative if/else for null checking
**Resolution**: Convert to declarative Option.map() / Option.or_else() pattern

### Roadblock 3: language_lacks_option
**Issue**: Programming language doesn't have built-in Option type
**Resolution**: Escalate to `fp_wrapper_generation` to create Option implementation

### Roadblock 4: exception_for_absence
**Issue**: Function throws exception for missing data instead of returning Option
**Resolution**: Replace exception with Option.none() return

---

## Integration with Project Directives

### Called by project_file_write

```
project_file_write
  └─ Calls fp_optionals (among other FP directives)
      └─ Analyzes function for null returns and Option usage
      └─ Returns: {refactored_code: "...", option_compliant: true}
  └─ If compliant: write file + update project.db
      └─ UPDATE functions SET error_handling_pattern = 'option'
```

### Called by project_compliance_check

```
project_compliance_check
  └─ Queries project.db for all functions
  └─ For each function:
      └─ Calls fp_optionals to verify Option compliance
      └─ Collects violations
  └─ Generates compliance report
  └─ Writes violations to notes table
```

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-error-handling)
- [Blueprint: Interactions](../../../docs/blueprints/blueprint_interactions.md#fp-project-integration)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#error-handling)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for null-safe optional value handling*
