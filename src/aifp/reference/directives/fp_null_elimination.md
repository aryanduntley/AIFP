# Directive: fp_null_elimination

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: HIGH - Critical for null safety

---

## Purpose

The `fp_null_elimination` directive detects and eliminates all uses of `null`, `None`, `undefined`, and `nil` literals from the codebase, replacing them with safe functional constructs like Option or Result types. This directive is the **enforcer** that ensures complete null safety by hunting down and removing every null value.

Null elimination creates a **null-free zone** in your codebase, enabling:
- **Zero Null Pointer Exceptions**: No runtime null reference errors
- **Compiler-Enforced Safety**: Type system prevents null access
- **Explicit Absence**: Missing data handled through Option type
- **No Hidden Nulls**: All optionality visible in types
- **Fearless Refactoring**: No worry about breaking null checks

This directive **complements** `fp_optionals` (which introduces Option) by ensuring Option is actually used everywhere instead of nulls. They work together as a comprehensive null-safety system.

---

## When to Apply

This directive applies when:
- **After introducing Option types** - Remove remaining null literals
- **Auditing codebase for null usage** - Find and eliminate all nulls
- **Converting legacy code** - Systematically replace nulls with Options
- **Validating null-free compliance** - Ensure no nulls remain
- **Initializing variables** - Use Option.none() instead of null
- **Called by project directives**:
  - `project_file_write` - Validates no nulls before writing
  - `project_compliance_check` - Scans for null literal usage
  - Works with `fp_optionals` - Option introduction + null elimination

---

## Workflow

### Trunk: scan_literals

Scans entire codebase to detect null/undefined literal usage in any context.

**Steps**:
1. **Parse all code** - Build AST for comprehensive analysis
2. **Identify null literals** - Find `None`, `null`, `undefined`, `nil` in code
3. **Identify null assignments** - Variables initialized to null
4. **Identify null comparisons** - `x == null`, `x is None`, `x === undefined`
5. **Identify null returns** - Functions returning null directly
6. **Evaluate compliance** - Classify as null-free, has-nulls, or uncertain

### Branches

**Branch 1: If null_or_undefined_found**
- **Then**: `replace_with_safe_construct`
- **Details**: Replace null literals with appropriate safe types
  - Replace `None` returns with `Option.none()`
  - Replace `null` variables with `Option.none()`
  - Replace `undefined` with `Option.none()` or explicit Result
  - Update all usages to handle Option type
- **Result**: Returns null-free refactored code

**Branch 2: If null_assignment**
- **Then**: `convert_to_option_initialization`
- **Details**: Convert null variable initialization to Option
  - Replace `user = None` with `user = Option.none()`
  - Replace `value: int | None = None` with `value: Option[int] = Option.none()`
  - Update all references to use Option methods
- **Result**: Returns code with Option-based initialization

**Branch 3: If null_comparison**
- **Then**: `convert_to_option_check`
- **Details**: Convert null checks to Option pattern matching
  - Replace `if x is None:` with `match x: case None: ...`
  - Replace `x == null` with `x.is_none()` method call
  - Replace `x != null` with `x.is_some()` method call
  - Use declarative Option methods instead of comparisons
- **Result**: Returns code with Option-based checking

**Branch 4: If null_free**
- **Then**: `mark_compliant`
- **Details**: Code contains no null literals
  - All optionality handled via Option type
  - Mark as null-free compliant
- **Result**: Code passes null elimination check

**Fallback**: `prompt_user`
- **Details**: Uncertain about null replacement
  - Present findings to user
  - Ask: "Replace null with Option or Result?"
  - Log uncertainty to notes table
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**No Nulls (Passes):**
```python
from typing import Optional as Option

def find_user(user_id: int) -> Option[User]:
    """
    Find user by ID. Never returns null.

    Returns Option.some(user) if found, Option.none() if not found.
    """
    users = get_all_users()

    for user in users:
        if user.id == user_id:
            return Option.some(user)

    return Option.none()  # Not null!

# Usage with pattern matching (no null checks)
result = find_user(123)
match result:
    case Some(user):
        print(f"Found: {user.name}")
    case None:
        print("User not found")
```

**Why Compliant**:
- Zero null literals
- Uses Option.none() for absence
- No `is None` checks
- Type-safe handling

---

**Option Initialization (Passes):**
```python
from typing import Optional as Option

class UserSession:
    """User session with optional current user."""

    def __init__(self):
        # Not None - Option.none()!
        self.current_user: Option[User] = Option.none()
        self.last_activity: Option[datetime] = Option.none()

    def login(self, user: User):
        """Set current user."""
        self.current_user = Option.some(user)
        self.last_activity = Option.some(datetime.now())

    def get_user_name(self) -> str:
        """Get current user name or default."""
        return (
            self.current_user
            .map(lambda u: u.name)
            .or_else("Guest")
        )
```

**Why Compliant**:
- All optional fields use Option.none()
- No null initialization
- Declarative Option handling
- No null checks

---

### ❌ Non-Compliant Code

**Null Literal (Violation):**
```python
# ❌ VIOLATION: null literal in return
def find_user(user_id: int) -> User | None:
    users = get_all_users()

    for user in users:
        if user.id == user_id:
            return user

    return None  # ← NULL LITERAL!
```

**Why Non-Compliant**:
- Returns `None` (null literal)
- Not using Option type
- Hidden optionality
- Null pointer risk

**Refactored (Compliant):**
```python
# ✅ REFACTORED: No null, uses Option
from typing import Optional as Option

def find_user(user_id: int) -> Option[User]:
    """Find user. Returns Option, never null."""
    users = get_all_users()

    for user in users:
        if user.id == user_id:
            return Option.some(user)

    return Option.none()  # Safe alternative to null
```

---

**Null Assignment (Violation):**
```python
# ❌ VIOLATION: Variable initialized to None
class ShoppingCart:
    def __init__(self):
        self.discount_code = None  # ← NULL ASSIGNMENT
        self.gift_message = None   # ← NULL ASSIGNMENT
        self.items = []

    def apply_discount(self, code: str):
        if code:
            self.discount_code = code  # Still dealing with nulls
```

**Why Non-Compliant**:
- Fields initialized to None
- Implicit optionality
- Null checks required
- Null reference risk

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Option-based initialization
from typing import Optional as Option

class ShoppingCart:
    def __init__(self):
        self.discount_code: Option[str] = Option.none()  # No null!
        self.gift_message: Option[str] = Option.none()
        self.items: list[Item] = []

    def apply_discount(self, code: str):
        """Apply discount code."""
        self.discount_code = Option.some(code)  # Explicit presence

    def get_discount_amount(self) -> float:
        """Calculate discount. Returns 0.0 if no code."""
        return (
            self.discount_code
            .map(lambda code: calculate_discount(code))
            .or_else(0.0)
        )
```

---

**Null Comparison (Violation):**
```python
# ❌ VIOLATION: Null comparison check
def format_user_info(user: User | None) -> str:
    if user is None:  # ← NULL COMPARISON
        return "No user"

    if user.email is not None:  # ← NULL COMPARISON
        return f"{user.name} ({user.email})"
    else:
        return user.name
```

**Why Non-Compliant**:
- Imperative null checks (`is None`)
- Multiple null comparisons
- Verbose and error-prone
- Not composable

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Option pattern matching
from typing import Optional as Option

def format_user_info(user: Option[User]) -> str:
    """
    Format user info with Option handling.

    No null checks - uses pattern matching.
    """
    return user.match(
        some=lambda u: format_with_email(u),
        none=lambda: "No user"
    )

def format_with_email(user: User) -> str:
    """Format user with email if present."""
    return (
        user.email
        .map(lambda e: f"{user.name} ({e})")
        .or_else(user.name)
    )
```

---

**Null Default Parameter (Violation):**
```python
# ❌ VIOLATION: None as default parameter
def send_email(to: str, subject: str, body: str, cc: str | None = None):  # ← NULL DEFAULT
    if cc is not None:  # ← NULL CHECK
        # Send with CC
        pass
    else:
        # Send without CC
        pass
```

**Why Non-Compliant**:
- `None` as default parameter
- Requires null check in body
- Implicit optionality
- Not type-safe

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Option default parameter
from typing import Optional as Option

def send_email(
    to: str,
    subject: str,
    body: str,
    cc: Option[str] = Option.none()  # Option default, not None!
):
    """
    Send email with optional CC.

    No null checks - uses Option methods.
    """
    recipients = [to]

    cc.map(lambda c: recipients.append(c))

    send_email_effect(recipients, subject, body)
```

---

## Edge Cases

### Edge Case 1: API Returns Null

**Issue**: External API returns null values in JSON

**Handling**:
```python
# ❌ Bad: Let null propagate into codebase
def fetch_user_api(user_id: int) -> User | None:
    response = api.get(f"/users/{user_id}")
    return response.get("user")  # Might be None from API

# ✅ Good: Convert null at boundary to Option
def fetch_user_api(user_id: int) -> Option[User]:
    """
    Fetch user from API. Converts null to Option at boundary.

    API contract allows null, but we convert immediately.
    """
    response = api.get(f"/users/{user_id}")
    user_data = response.get("user")

    # Convert null at system boundary
    if user_data is None:
        return Option.none()
    else:
        return Option.some(parse_user(user_data))
```

**Directive Action**: Convert nulls to Options at system boundaries (API, database).

---

### Edge Case 2: Language Built-in Returns Null

**Issue**: Language built-ins return null (dict.get(), list.find(), etc.)

**Handling**:
```python
# ❌ Bad: Use dict.get() directly (returns None)
def get_config_value(key: str) -> str:
    return config.get(key) or "default"  # None becomes "default"

# ✅ Good: Wrap built-in with Option
def get_config_value(key: str) -> Option[str]:
    """
    Get config value. Wraps dict.get() in Option.

    Converts None to Option at usage point.
    """
    value = config.get(key)
    return Option.from_nullable(value)

# ✅ Better: Create Option-based dictionary wrapper
class OptionDict:
    """Dictionary that returns Options instead of None."""

    def __init__(self, data: dict):
        self._data = data

    def get(self, key: str) -> Option[any]:
        """Get value by key. Returns Option.none() if missing."""
        value = self._data.get(key)
        return Option.from_nullable(value)

# Usage
config = OptionDict({"api_key": "secret"})
api_key = config.get("api_key").or_else("default")
```

**Directive Action**: Wrap null-returning built-ins with Option-based wrappers.

---

### Edge Case 3: Database Nullable Columns

**Issue**: Database schema has nullable columns

**Handling**:
```python
# ❌ Bad: Allow None in domain models
@dataclass
class User:
    id: int
    name: str
    email: str | None  # ← Nullable from database
    phone: str | None  # ← Nullable from database

# ✅ Good: Use Option in domain models
from typing import Optional as Option

@dataclass
class User:
    id: int
    name: str
    email: Option[str]  # Option, not None
    phone: Option[str]  # Option, not None

# Database adapter converts None to Option
def fetch_user_from_db(user_id: int) -> Option[User]:
    """
    Fetch user from database. Converts DB nulls to Options.

    Database allows NULL, but domain model uses Option.
    """
    row = db.query("SELECT * FROM users WHERE id = ?", user_id).first()

    if row is None:
        return Option.none()

    return Option.some(User(
        id=row['id'],
        name=row['name'],
        email=Option.from_nullable(row['email']),  # Convert NULL
        phone=Option.from_nullable(row['phone'])   # Convert NULL
    ))
```

**Directive Action**: Convert database NULLs to Options in data adapter layer.

---

### Edge Case 4: Null in Third-Party Library Types

**Issue**: Third-party library types use null

**Handling**:
```python
# ❌ Bad: Let library nulls leak into code
import requests

def fetch_data(url: str) -> dict | None:
    response = requests.get(url)
    return response.json() if response.ok else None  # ← None leak

# ✅ Good: Adapter wraps library with Option
def fetch_data(url: str) -> Result[dict, str]:
    """
    Fetch data from URL. Wraps requests library.

    Library uses None, but we return Result.
    """
    try:
        response = requests.get(url)
        if response.ok:
            return Ok(response.json())
        else:
            return Err(f"HTTP {response.status_code}")
    except requests.RequestException as e:
        return Err(f"Request failed: {e}")
```

**Directive Action**: Create adapters that convert library nulls to Options/Results at boundaries.

---

## Related Directives

- **Depends On**:
  - `fp_optionals` - Must introduce Option types before eliminating nulls
- **Triggers**:
  - `fp_type_safety` - Null-free code enables stronger type checking
  - `fp_pattern_matching` - Options use pattern matching instead of null checks
- **Called By**:
  - `project_file_write` - Validates no nulls before writing
  - `project_compliance_check` - Scans for null literal violations
  - `fp_optionals` - Work together for complete null safety
- **Escalates To**:
  - `fp_wrapper_generation` - For wrapping null-returning external libraries

---

## Helper Functions Used

- `detect_null_literals(ast: AST) -> list[NullLiteral]` - Finds all null/None/undefined
- `detect_null_assignments(ast: AST) -> list[Assignment]` - Finds `x = None`
- `detect_null_comparisons(ast: AST) -> list[Comparison]` - Finds `x is None`, `x == null`
- `replace_nulls_with_option(code: str, nulls: list) -> str` - Refactors to Option
- `update_functions_table(func_id: int, null_free: bool)` - Updates project.db

---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `null_safety = 'null_free'` for compliant functions
- **`functions`**: Updates `type_annotations_json` to show Option usage
- **`notes`**: Logs null elimination issues with `note_type = 'compliance'`
- **`project`**: Sets `null_free_compliance = true` when entire project null-free

---

## Testing

How to verify this directive is working:

1. **Write code with null** → Directive detects and refactors
   ```python
   # Input (has null)
   def get_value(): return None

   # Expected output (null-free)
   def get_value() -> Option[str]:
       return Option.none()
   ```

2. **Write code without null** → Directive marks compliant
   ```python
   def get_value() -> Option[str]:
       return Option.none()
   # ✅ Already null-free
   ```

3. **Check database** → Verify `functions.null_safety = 'null_free'`
   ```sql
   SELECT name, null_safety, type_annotations_json
   FROM functions
   WHERE name = 'get_value';
   -- Expected: null_safety='null_free'
   ```

---

## Common Mistakes

- ❌ **Using `Optional[T]` type hint but still returning None** - Type hint alone insufficient
- ❌ **Null checks after Option introduced** - Should use Option methods, not `is None`
- ❌ **Mixing None and Option.none()** - Must be consistent, all Option or all null
- ❌ **Converting some nulls but not all** - Partial elimination defeats purpose
- ❌ **Forgetting system boundaries** - API/DB nulls must be converted immediately

---

## Roadblocks and Resolutions

### Roadblock 1: null_literal_in_code
**Issue**: Code contains None/null/undefined literals
**Resolution**: Replace with Option.none() or Option.some(value)

### Roadblock 2: external_library_returns_null
**Issue**: Third-party library returns null
**Resolution**: Create Option-based wrapper adapter at system boundary

### Roadblock 3: database_nullable_columns
**Issue**: Database schema allows NULL
**Resolution**: Convert NULLs to Options in data access layer

### Roadblock 4: api_returns_null
**Issue**: External API returns null in responses
**Resolution**: Convert to Option at API boundary in client code

---

## Integration with Project Directives

### Called by project_file_write

```
project_file_write
  └─ Calls fp_null_elimination (after fp_optionals)
      └─ Scans code for any remaining null literals
      └─ Returns: {refactored_code: "...", null_free: true}
  └─ If compliant: write file + update project.db
      └─ UPDATE functions SET null_safety = 'null_free'
```

### Called by project_compliance_check

```
project_compliance_check
  └─ Queries project.db for all functions
  └─ For each function:
      └─ Calls fp_null_elimination to verify no nulls
      └─ Collects violations (remaining null literals)
  └─ Generates compliance report
  └─ Writes violations to notes table
```

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-null-elimination)
- [Blueprint: Interactions](../../../docs/blueprints/blueprint_interactions.md#fp-project-integration)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#error-handling)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for complete null elimination*
