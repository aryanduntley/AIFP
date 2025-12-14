# Directive: fp_error_pipeline

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Error handling composition

---

## Purpose

The `fp_error_pipeline` directive enables chaining of functions that may fail using monadic combinators like `map`, `flatMap`, and `bind`. This directive promotes **declarative, composable error handling pipelines** where multiple fallible operations are sequenced cleanly without nested try/catch blocks or imperative error checking.

Error pipelines transform **scattered error handling** into **linear, readable sequences**, enabling:
- **Clean Composition**: Chain fallible operations with flatMap
- **Early Exit**: Pipeline stops at first failure, propagates error
- **Type Safety**: Compiler ensures error handling at each step
- **Readability**: Linear flow instead of nested conditionals
- **Maintainability**: Easy to add/remove/reorder pipeline steps

This directive integrates `fp_result_types`, `fp_optionals`, and `fp_try_monad` into cohesive error handling flows using functional composition.

---

## When to Apply

This directive applies when:
- **Chaining multiple fallible operations** - Each step might fail
- **Multi-step validation pipelines** - Series of validation checks
- **Data transformation pipelines** - Parse → validate → transform → save
- **Converting nested try/catch** - Flatten to linear pipeline
- **Business logic workflows** - Sequential operations with error handling
- **Called by project directives**:
  - `project_file_write` - Validates error pipeline patterns
  - `project_compliance_check` - Scans for nested error handling
  - Integrates `fp_result_types`, `fp_optionals`, `fp_try_monad`

---

## Workflow

### Trunk: scan_function_chains

Scans code to detect sequential operations with mixed success/error flows that should be unified into error pipelines.

**Steps**:
1. **Parse function body** - Build call graph and control flow
2. **Identify sequential fallible operations** - Series of operations that can fail
3. **Identify nested try/catch** - Multi-level exception handling
4. **Identify imperative error checking** - if/else for error propagation
5. **Identify manual error propagation** - Passing errors up manually
6. **Evaluate compliance** - Classify as pipeline, needs-refactoring, or uncertain

### Branches

**Branch 1: If mixed_success_error_flows**
- **Then**: `standardize_to_error_pipeline`
- **Details**: Convert mixed error handling to unified pipeline
  - Extract each operation into separate function returning Result/Option/Try
  - Chain operations with flatMap for error propagation
  - Replace imperative checks with declarative pipeline
  - Single error path through entire flow
- **Result**: Returns unified error pipeline

**Branch 2: If try_catch_chain**
- **Then**: `convert_to_flatmap`
- **Details**: Convert sequential try/catch blocks to flatMap chain
  - Extract each try block into function returning Try
  - Chain with flatMap instead of sequential try/catch
  - Remove all catch blocks (errors propagate automatically)
  - Linear pipeline replaces nested structure
- **Result**: Returns flatMap-based pipeline

**Branch 3: If manual_error_handling**
- **Then**: `replace_with_declarative_pipeline`
- **Details**: Replace manual error checking with pipeline
  - Convert `if error: return error` to automatic flatMap propagation
  - Remove explicit error checking code
  - Let monad handle error flow
  - Cleaner, more maintainable code
- **Result**: Returns declarative error pipeline

**Branch 4: If compliant**
- **Then**: `mark_compliant`
- **Details**: Already using error pipelines correctly
  - Operations chained with flatMap
  - Clean error propagation
  - Mark as compliant
- **Result**: Code passes error pipeline check

**Fallback**: `prompt_user`
- **Details**: Uncertain about pipeline refactoring
  - Present findings to user
  - Ask: "Convert to error pipeline?"
  - Log uncertainty to notes table
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Result Pipeline (Passes):**
```python
from typing import Union

class Ok:
    def __init__(self, value):
        self.value = value

    def flatMap(self, f):
        """Chain with another Result-returning function."""
        return f(self.value)

    def map(self, f):
        """Transform success value."""
        try:
            return Ok(f(self.value))
        except Exception as e:
            return Err(str(e))

class Err:
    def __init__(self, error):
        self.error = error

    def flatMap(self, f):
        """Propagate error (skip operation)."""
        return self

    def map(self, f):
        """Propagate error (skip operation)."""
        return self

Result = Union[Ok, Err]

def parse_json(data: str) -> Result[dict]:
    """Parse JSON string."""
    try:
        return Ok(json.loads(data))
    except json.JSONDecodeError as e:
        return Err(f"JSON parse error: {e}")

def extract_user_field(data: dict) -> Result[dict]:
    """Extract user field from data."""
    if 'user' in data:
        return Ok(data['user'])
    else:
        return Err("Missing 'user' field")

def validate_email(user: dict) -> Result[dict]:
    """Validate user has valid email."""
    if 'email' not in user:
        return Err("Missing email field")

    email = user['email']
    if '@' not in email:
        return Err(f"Invalid email: {email}")

    return Ok(user)

def create_user_account(user: dict) -> Result[int]:
    """Create user account (simulated)."""
    # Simulate database insert returning user ID
    return Ok(12345)

def process_user_registration(json_data: str) -> Result[int]:
    """
    Process user registration with error pipeline.

    Clean, linear pipeline - each step might fail.
    Errors propagate automatically through flatMap.
    """
    return (
        parse_json(json_data)
        .flatMap(extract_user_field)
        .flatMap(validate_email)
        .flatMap(create_user_account)
    )

# Usage
result = process_user_registration('{"user": {"email": "test@example.com"}}')
match result:
    case Ok(user_id):
        print(f"User created with ID: {user_id}")
    case Err(error):
        print(f"Registration failed: {error}")
```

**Why Compliant**:
- Linear pipeline with flatMap
- Each step returns Result
- Errors propagate automatically
- No nested try/catch or if/else
- Readable and maintainable

---

**Option Pipeline (Passes):**
```python
def find_user_by_id(user_id: int) -> Option[User]:
    """Find user by ID."""
    # ... implementation
    pass

def get_user_email(user: User) -> Option[str]:
    """Get user's email (might not be set)."""
    return Option.from_nullable(user.email)

def normalize_email(email: str) -> Option[str]:
    """Normalize email to lowercase."""
    return Option.some(email.lower())

def send_welcome_email(email: str) -> Option[bool]:
    """Send welcome email."""
    # ... send email implementation
    return Option.some(True)

def welcome_new_user(user_id: int) -> Option[bool]:
    """
    Welcome new user with email pipeline.

    Each step might return None - pipeline handles gracefully.
    """
    return (
        find_user_by_id(user_id)
        .flatMap(get_user_email)
        .flatMap(normalize_email)
        .flatMap(send_welcome_email)
    )

# Usage
result = welcome_new_user(123)
if result.is_some():
    print("Welcome email sent!")
else:
    print("Could not send welcome email")
```

**Why Compliant**:
- Option pipeline with flatMap
- Handles absence gracefully
- No null checks
- Composable operations

---

### ❌ Non-Compliant Code

**Nested Try/Catch (Violation):**
```python
# ❌ VIOLATION: Nested exception handling
def process_user_registration(json_data: str) -> int:
    try:
        data = json.loads(json_data)
        try:
            user = data['user']
            try:
                if 'email' not in user:
                    raise ValueError("Missing email")

                if '@' not in user['email']:
                    raise ValueError(f"Invalid email: {user['email']}")

                try:
                    user_id = create_user_account(user)
                    return user_id
                except DatabaseError as e:
                    raise RuntimeError(f"Database error: {e}")
            except ValueError as e:
                raise RuntimeError(f"Validation error: {e}")
        except KeyError:
            raise RuntimeError("Missing user field")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON parse error: {e}")
```

**Why Non-Compliant**:
- Deeply nested try/catch blocks
- Difficult to read and maintain
- Complex error flow
- Not composable

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Error pipeline with flatMap
def process_user_registration(json_data: str) -> Result[int]:
    """
    Process user registration with clean error pipeline.

    Replaces nested try/catch with linear flatMap chain.
    """
    return (
        parse_json(json_data)
        .flatMap(extract_user_field)
        .flatMap(validate_email)
        .flatMap(create_user_account)
    )
```

---

**Manual Error Propagation (Violation):**
```python
# ❌ VIOLATION: Manual error checking and propagation
def process_order(order_data: dict) -> tuple[bool, str, Order]:
    # Validate customer
    valid, error, customer = validate_customer(order_data.get('customer'))
    if not valid:
        return False, error, None

    # Validate items
    valid, error, items = validate_items(order_data.get('items'))
    if not valid:
        return False, error, None

    # Calculate total
    valid, error, total = calculate_total(items)
    if not valid:
        return False, error, None

    # Create order
    valid, error, order = create_order(customer, items, total)
    if not valid:
        return False, error, None

    return True, "", order
```

**Why Non-Compliant**:
- Manual error checking at each step
- Repetitive `if not valid: return` pattern
- Tuple return for error signaling (not type-safe)
- Error-prone and verbose

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Declarative error pipeline
def validate_customer(customer_data: dict) -> Result[Customer]:
    """Validate customer data."""
    # ... implementation
    pass

def validate_items(items_data: list) -> Result[list[Item]]:
    """Validate order items."""
    # ... implementation
    pass

def calculate_total(items: list[Item]) -> Result[float]:
    """Calculate order total."""
    # ... implementation
    pass

def create_order(customer: Customer, items: list[Item], total: float) -> Result[Order]:
    """Create order."""
    # ... implementation
    pass

def process_order(order_data: dict) -> Result[Order]:
    """
    Process order with error pipeline.

    Clean, linear pipeline - no manual error checking.
    """
    customer_result = validate_customer(order_data.get('customer'))
    items_result = validate_items(order_data.get('items'))

    # Combine multiple Results, then continue pipeline
    return customer_result.flatMap(lambda customer:
        items_result.flatMap(lambda items:
            calculate_total(items).flatMap(lambda total:
                create_order(customer, items, total)
            )
        )
    )

# Usage
result = process_order(order_data)
match result:
    case Ok(order):
        print(f"Order created: {order.id}")
    case Err(error):
        print(f"Order failed: {error}")
```

---

**Mixed Error Handling Styles (Violation):**
```python
# ❌ VIOLATION: Mixing exceptions, nulls, and tuples
def register_user(data: dict) -> User:
    # Style 1: Exception
    if 'email' not in data:
        raise ValueError("Missing email")

    # Style 2: Null return (elsewhere in codebase)
    user = find_existing_user(data['email'])
    if user is not None:
        raise ValueError("User already exists")

    # Style 3: Tuple with bool flag (elsewhere)
    success, error_msg, validated = validate_email(data['email'])
    if not success:
        raise ValueError(error_msg)

    # Create user
    return create_user(validated)
```

**Why Non-Compliant**:
- Three different error handling styles
- Inconsistent error signaling
- Difficult to compose
- Maintenance nightmare

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Unified Result pipeline
def check_email_present(data: dict) -> Result[str]:
    """Check email field present."""
    if 'email' in data:
        return Ok(data['email'])
    else:
        return Err("Missing email")

def check_user_not_exists(email: str) -> Result[str]:
    """Check user doesn't exist."""
    user = find_existing_user(email)
    if user is None:
        return Ok(email)
    else:
        return Err("User already exists")

def validate_email_format(email: str) -> Result[str]:
    """Validate email format."""
    if '@' in email and '.' in email:
        return Ok(email)
    else:
        return Err(f"Invalid email format: {email}")

def create_user_account(email: str) -> Result[User]:
    """Create user account."""
    user = User(email=email)
    return Ok(user)

def register_user(data: dict) -> Result[User]:
    """
    Register user with unified error pipeline.

    Single error handling style throughout.
    """
    return (
        check_email_present(data)
        .flatMap(check_user_not_exists)
        .flatMap(validate_email_format)
        .flatMap(create_user_account)
    )
```

---

## Edge Cases

### Edge Case 1: Combining Multiple Pipelines

**Issue**: Need to combine results from parallel pipelines

**Handling**:
```python
# Parallel operations, then combine
def register_and_notify(user_data: dict, template_id: str) -> Result[tuple[User, Notification]]:
    """
    Register user and prepare notification in parallel, then combine.

    Uses applicative pattern to combine independent Results.
    """
    user_result = register_user(user_data)
    template_result = load_email_template(template_id)

    # Combine two Results
    return user_result.flatMap(lambda user:
        template_result.map(lambda template:
            (user, template)
        )
    )

# Then continue pipeline
result = (
    register_and_notify(user_data, "welcome")
    .flatMap(lambda pair: send_notification(pair[0], pair[1]))
)
```

**Directive Action**: Use flatMap to combine multiple pipeline results.

---

### Edge Case 2: Conditional Pipeline Steps

**Issue**: Some pipeline steps are conditional

**Handling**:
```python
# Conditional pipeline with identity for skip
def process_payment(payment_data: dict, apply_discount: bool) -> Result[Payment]:
    """
    Process payment with optional discount step.

    Uses conditional pipeline composition.
    """
    pipeline = (
        validate_payment_data(payment_data)
        .flatMap(calculate_base_amount)
    )

    # Conditional step
    if apply_discount:
        pipeline = pipeline.flatMap(apply_discount_code)

    # Continue pipeline
    return pipeline.flatMap(charge_payment)
```

**Directive Action**: Build pipeline conditionally, insert identity where steps are skipped.

---

### Edge Case 3: Pipeline with Logging/Side Effects

**Issue**: Need to log in pipeline without disrupting flow

**Handling**:
```python
# Pipeline with side effect tapping
class Result:
    def tap(self, f):
        """Execute side effect without changing value (useful for logging)."""
        match self:
            case Ok(value):
                f(value)  # Side effect
            case Err(error):
                pass  # Skip on error
        return self  # Return self for chaining

def process_with_logging(data: str) -> Result[int]:
    """
    Process with logging at each step.

    Uses tap() for side effects without disrupting pipeline.
    """
    return (
        parse_json(data)
        .tap(lambda d: log("Parsed JSON successfully"))
        .flatMap(extract_user_field)
        .tap(lambda u: log(f"Extracted user: {u['id']}"))
        .flatMap(validate_email)
        .tap(lambda u: log("Email validated"))
        .flatMap(create_user_account)
        .tap(lambda id: log(f"Created user ID: {id}"))
    )
```

**Directive Action**: Use `tap()` method for logging/side effects without breaking pipeline.

---

### Edge Case 4: Early Termination with Default

**Issue**: Pipeline should provide default value on any failure

**Handling**:
```python
# Pipeline with default fallback
def get_user_preference(user_id: int, key: str, default: str) -> str:
    """
    Get user preference with default fallback.

    Pipeline returns default on any step failure.
    """
    return (
        find_user_by_id(user_id)
        .flatMap(lambda user: get_preferences(user))
        .flatMap(lambda prefs: get_preference_value(prefs, key))
        .or_else(default)  # Fallback if any step fails
    )

# Usage
theme = get_user_preference(123, "theme", "light")
```

**Directive Action**: Use `or_else()` at pipeline end for default value on any failure.

---

## Related Directives

- **Depends On**:
  - `fp_result_types` - Pipeline chains Results
  - `fp_optionals` - Pipeline chains Options
  - `fp_try_monad` - Pipeline chains Try monads
  - `fp_monadic_composition` - General monad composition patterns
- **Triggers**:
  - `fp_chaining` - Function chaining patterns
  - `fp_side_effect_detection` - Isolate effects from pipeline logic
- **Called By**:
  - `project_file_write` - Validates error pipeline patterns
  - `project_compliance_check` - Scans for nested error handling
- **Escalates To**: None (integration directive)

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `error_handling_pattern = 'pipeline'` for pipeline functions
- **`functions`**: Updates `composition_style = 'flatmap'` for monadic chains
- **`interactions`**: Tracks pipeline dependencies (function call chains)
- **`notes`**: Logs pipeline refactoring with `note_type = 'refactoring'`

---

## Testing

How to verify this directive is working:

1. **Write nested error handling** → Directive detects and refactors to pipeline
   ```python
   # Input (nested try/catch)
   try:
       a = op1()
       try:
           b = op2(a)
           return b
       except: ...
   except: ...

   # Expected output (pipeline)
   return op1().flatMap(op2)
   ```

2. **Write flatMap pipeline** → Directive marks compliant
   ```python
   def process(x):
       return op1(x).flatMap(op2).flatMap(op3)
   # ✅ Already pipeline-based
   ```

3. **Check database** → Verify `functions.error_handling_pattern = 'pipeline'`
   ```sql
   SELECT name, error_handling_pattern, composition_style
   FROM functions
   WHERE name = 'process';
   -- Expected: error_handling_pattern='pipeline', composition_style='flatmap'
   ```

---

## Common Mistakes

- ❌ **Mixing map and flatMap incorrectly** - Use flatMap when function returns Result/Option
- ❌ **Nested pipelines** - Flatten with flatMap, don't nest
- ❌ **Breaking pipeline for side effects** - Use tap() for logging
- ❌ **Not handling errors at pipeline end** - Always use match or or_else()
- ❌ **Imperative error checking in pipeline** - Let monad handle propagation

---

## Roadblocks and Resolutions

### Roadblock 1: manual_error_handling
**Issue**: Imperative error checking instead of declarative pipeline
**Resolution**: Replace with flatMap chain, let monad handle error flow

### Roadblock 2: nested_try_catch
**Issue**: Multiple levels of exception handling
**Resolution**: Extract operations into functions, chain with flatMap

### Roadblock 3: mixed_error_styles
**Issue**: Different error handling patterns in same flow
**Resolution**: Unify under single Result/Option/Try pipeline

### Roadblock 4: side_effects_in_pipeline
**Issue**: Need logging or effects without breaking flow
**Resolution**: Use tap() method for effects, keep pipeline clean

---

## Integration with Project Directives

### Called by project_file_write

```
project_file_write
  └─ Calls fp_error_pipeline to validate error handling composition
      └─ Analyzes function for nested error handling
      └─ Returns: {refactored_code: "...", uses_pipeline: true}
  └─ If compliant: write file + update project.db
      └─ UPDATE functions SET error_handling_pattern = 'pipeline', composition_style = 'flatmap'
```

### Called by project_compliance_check

```
project_compliance_check
  └─ Queries project.db for all functions
  └─ For each function with error handling:
      └─ Calls fp_error_pipeline to verify pipeline usage
      └─ Collects violations (nested try/catch, manual checks)
  └─ Generates compliance report
  └─ Writes violations to notes table
```

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for composable error handling pipelines*
