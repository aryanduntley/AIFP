# fp_runtime_type_check

## Purpose

The `fp_runtime_type_check` directive adds runtime type validation guards and assertions to ensure type correctness when static typing is unavailable or insufficient. It injects defensive runtime checks at function boundaries to maintain type safety in dynamically typed environments, during type erasure scenarios, or when interfacing with untyped external code. This provides a safety net for type correctness beyond compile-time checks.

**Category**: Type System
**Type**: FP Core
**Priority**: Medium
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`insert_type_checks`**: Analyze function signatures and insert runtime type validation at boundaries.

### Branches

1. **`type_missing`** → **`insert_runtime_assert`**
   - **Condition**: Function parameter lacks type annotation or receives Any type
   - **Action**: Insert runtime type check at function entry
   - **Details**: Validate parameter types match expected types
   - **Output**: Function with runtime type guards

2. **`type_mismatch`** → **`raise_validation_warning`**
   - **Condition**: Runtime type check detects type violation
   - **Action**: Raise TypeError with descriptive message
   - **Details**: Include expected vs. actual type information

3. **`external_boundary`** → **`wrap_with_validation`**
   - **Condition**: Function interfaces with external/untyped code
   - **Action**: Wrap external calls with type validation
   - **Details**: Validate inputs before external call, outputs after
   - **Output**: Type-safe wrapper around external code

4. **`generic_type_erasure`** → **`add_generic_checks`**
   - **Condition**: Generic types erased at runtime (Python, Java)
   - **Action**: Add explicit runtime checks for generic constraints
   - **Details**: Validate container element types
   - **Output**: Runtime-validated generic operations

5. **`typed_properly`** → **`mark_compliant`**
   - **Condition**: Static types sufficient, no runtime checks needed
   - **Action**: Mark as type-safe
   - **Output**: Compliance confirmation

6. **Fallback** → **`mark_compliant`**
   - **Condition**: No additional runtime checks required
   - **Action**: Mark as compliant

### Error Handling
- **On failure**: Prompt user with type validation analysis
- **Low confidence** (< 0.7): Request review before inserting checks

---

## Refactoring Strategies

### Strategy 1: Parameter Type Validation
Add runtime checks for function parameters.

**Before (Python - No Runtime Validation)**:
```python
def calculate_discount(price: float, percentage: float) -> float:
    """Type hints present but not enforced at runtime."""
    return price * (percentage / 100)

# Runtime: accepts anything!
result = calculate_discount("100", "10")  # Type error not caught!
```

**After (Python - Runtime Validation)**:
```python
def calculate_discount(price: float, percentage: float) -> float:
    """Type hints enforced with runtime validation."""
    # Runtime type checks
    if not isinstance(price, (int, float)):
        raise TypeError(f"price must be numeric, got {type(price).__name__}")
    if not isinstance(percentage, (int, float)):
        raise TypeError(f"percentage must be numeric, got {type(percentage).__name__}")

    return price * (percentage / 100)

# Runtime: catches type errors
result = calculate_discount("100", "10")  # TypeError raised!
```

### Strategy 2: Return Type Validation
Validate return values match declared types.

**Before (Python - Unvalidated Return)**:
```python
def get_user_age(user_id: int) -> int:
    """Returns age, but no runtime guarantee."""
    user = fetch_user(user_id)
    return user.get('age')  # Might return None or string!
```

**After (Python - Validated Return)**:
```python
def get_user_age(user_id: int) -> int:
    """Returns age with runtime validation."""
    if not isinstance(user_id, int):
        raise TypeError(f"user_id must be int, got {type(user_id).__name__}")

    user = fetch_user(user_id)
    age = user.get('age')

    # Validate return type
    if not isinstance(age, int):
        raise TypeError(f"Expected int return, got {type(age).__name__}")

    return age
```

### Strategy 3: Generic Container Validation
Check element types in generic containers.

**Before (Python - Type Erasure)**:
```python
from typing import List

def sum_numbers(numbers: List[int]) -> int:
    """Type hint not enforced at runtime."""
    return sum(numbers)

# Runtime: accepts list of any type
result = sum_numbers([1, "2", 3])  # TypeError only during sum()!
```

**After (Python - Runtime Element Validation)**:
```python
from typing import List

def sum_numbers(numbers: List[int]) -> int:
    """Type hint enforced with element validation."""
    if not isinstance(numbers, list):
        raise TypeError(f"numbers must be list, got {type(numbers).__name__}")

    # Validate each element
    for i, num in enumerate(numbers):
        if not isinstance(num, int):
            raise TypeError(f"numbers[{i}] must be int, got {type(num).__name__}")

    return sum(numbers)

# Runtime: catches type errors immediately
result = sum_numbers([1, "2", 3])  # TypeError at validation!
```

### Strategy 4: External API Boundary Validation
Validate data from external sources.

**Before (Python - Trusting External Data)**:
```python
import requests

def fetch_user_data(user_id: int) -> dict:
    """Assumes API returns correct structure."""
    response = requests.get(f"/api/users/{user_id}")
    return response.json()  # No validation!
```

**After (Python - Boundary Validation)**:
```python
import requests
from typing import TypedDict

class UserData(TypedDict):
    id: int
    name: str
    email: str

def validate_user_data(data: dict) -> UserData:
    """Runtime validation of external data structure."""
    required_fields = {'id': int, 'name': str, 'email': str}

    for field, expected_type in required_fields.items():
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(data[field], expected_type):
            raise TypeError(
                f"Field {field} must be {expected_type.__name__}, "
                f"got {type(data[field]).__name__}"
            )

    return data  # type: ignore (validated)

def fetch_user_data(user_id: int) -> UserData:
    """Fetches and validates user data."""
    if not isinstance(user_id, int):
        raise TypeError(f"user_id must be int, got {type(user_id).__name__}")

    response = requests.get(f"/api/users/{user_id}")
    raw_data = response.json()

    # Validate external data
    return validate_user_data(raw_data)
```

### Strategy 5: TypeScript Runtime Validation (using library)
Add runtime validation in TypeScript.

**Before (TypeScript - Compile-Time Only)**:
```typescript
interface User {
  id: number;
  name: string;
  age: number;
}

function processUser(user: User): string {
  // Type only checked at compile time
  return `${user.name} is ${user.age} years old`;
}

// Runtime: accepts anything!
const fakeUser = { id: "123", name: 123, age: "30" };
processUser(fakeUser as User);  // Type error at runtime!
```

**After (TypeScript - Runtime Validation with Zod)**:
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.number(),
  name: z.string(),
  age: z.number(),
});

type User = z.infer<typeof UserSchema>;

function processUser(user: unknown): string {
  // Runtime validation
  const validatedUser = UserSchema.parse(user);  // Throws if invalid

  return `${validatedUser.name} is ${validatedUser.age} years old`;
}

// Runtime: catches type errors
const fakeUser = { id: "123", name: 123, age: "30" };
processUser(fakeUser);  // ZodError thrown!
```

---

## Examples

### Example 1: Union Type Validation

**Runtime Validation**:
```python
from typing import Union

def format_value(value: Union[int, str]) -> str:
    """Format value with runtime type validation."""
    if not isinstance(value, (int, str)):
        raise TypeError(
            f"value must be int or str, got {type(value).__name__}"
        )

    if isinstance(value, int):
        return f"{value:,}"
    else:
        return value.upper()
```

### Example 2: Optional Type Validation

**Runtime Validation**:
```python
from typing import Optional

def get_user_name(user: Optional[dict]) -> str:
    """Get user name with runtime validation."""
    if user is not None and not isinstance(user, dict):
        raise TypeError(f"user must be dict or None, got {type(user).__name__}")

    if user is None:
        return "Guest"

    # Validate 'name' field
    name = user.get('name')
    if name is not None and not isinstance(name, str):
        raise TypeError(f"user['name'] must be str, got {type(name).__name__}")

    return name or "Anonymous"
```

### Example 3: Callable Type Validation

**Runtime Validation**:
```python
from typing import Callable
import inspect

def apply_operation(
    data: list,
    operation: Callable[[int], int]
) -> list:
    """Apply operation with callable validation."""
    if not callable(operation):
        raise TypeError("operation must be callable")

    # Validate signature (advanced)
    sig = inspect.signature(operation)
    if len(sig.parameters) != 1:
        raise TypeError("operation must accept exactly 1 parameter")

    return [operation(item) for item in data]
```

---

## Edge Cases

### Edge Case 1: Performance Impact
**Scenario**: Runtime checks add overhead to hot paths
**Issue**: Type validation slows down critical functions
**Handling**:
- Profile before optimizing
- Use `__debug__` flag to disable checks in production
- Apply checks only at API boundaries
- Consider decorator pattern for optional validation

**Example**:
```python
import os

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

def typecheck(func):
    """Decorator for optional runtime type checking."""
    if not DEBUG:
        return func  # Skip validation in production

    def wrapper(*args, **kwargs):
        # Perform expensive validation only in debug mode
        validate_types(func, args, kwargs)
        return func(*args, **kwargs)
    return wrapper

@typecheck
def expensive_calculation(x: float, y: float) -> float:
    return x ** y
```

### Edge Case 2: Complex Type Validation
**Scenario**: Nested generic types or complex unions
**Issue**: Validation logic becomes unwieldy
**Handling**:
- Use validation libraries (Pydantic, Zod)
- Extract validation to dedicated functions
- Validate incrementally (layer by layer)

### Edge Case 3: Type Coercion vs. Validation
**Scenario**: Should invalid types be coerced or rejected?
**Issue**: Unclear whether to convert or raise error
**Handling**:
- Prefer strict validation (no coercion)
- Document coercion policy if applied
- Separate validation from coercion functions

**Example**:
```python
# Strict validation (no coercion)
def add_strict(a: int, b: int) -> int:
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Arguments must be int")
    return a + b

# With coercion (explicit)
def add_coerce(a, b) -> int:
    try:
        return int(a) + int(b)
    except (TypeError, ValueError) as e:
        raise TypeError(f"Cannot coerce arguments to int: {e}")
```

### Edge Case 4: Recursive Type Validation
**Scenario**: Nested data structures require deep validation
**Issue**: Validation must traverse entire structure
**Handling**:
- Implement recursive validation
- Set maximum depth to prevent infinite recursion
- Cache validated structures

### Edge Case 5: Duck Typing vs. Strict Typing
**Scenario**: Python's duck typing philosophy conflicts with strict checks
**Issue**: Overly strict checks reject valid duck-typed objects
**Handling**:
- Use Protocol/ABC for structural typing
- Check for required methods/attributes, not exact type
- Document when strict typing necessary

---

## Database Operations

### Record Runtime Type Check Metadata

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Query Functions Needing Runtime Validation

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Related Directives

### FP Directives
- **fp_type_safety**: Provides static type annotations that runtime checks enforce
- **fp_type_inference**: Infers types that can be validated at runtime
- **fp_generic_constraints**: Generic constraints need runtime validation after erasure

### Project Directives
- **project_compliance_check**: Validates runtime type check coverage
- **project_update_db**: Records validation metadata

---

## Helper Functions

### `generate_type_validator(type_annotation) -> str`
Generates runtime validation code for a type annotation.

**Signature**:
```python
def generate_type_validator(type_annotation: Any) -> str:
    """
    Converts type annotation to runtime check code.
    Handles: primitives, unions, generics, optionals.
    Returns validation code string.
    """
```

### `insert_parameter_checks(function_def) -> FunctionDefinition`
Inserts runtime checks at function entry.

**Signature**:
```python
def insert_parameter_checks(
    function_def: FunctionDefinition
) -> FunctionDefinition:
    """
    Adds isinstance checks for each parameter.
    Returns modified function with validation code.
    """
```

### `validate_container_elements(container, element_type) -> bool`
Runtime validation for generic container element types.

**Signature**:
```python
def validate_container_elements(
    container: list | tuple | set,
    element_type: type
) -> bool:
    """
    Checks all elements match expected type.
    Returns True if valid, raises TypeError otherwise.
    """
```

---

## Testing

### Test 1: Parameter Validation
```python
def test_parameter_validation():
    def add(a: int, b: int) -> int:
        if not isinstance(a, int) or not isinstance(b, int):
            raise TypeError("Arguments must be int")
        return a + b

    # Valid
    assert add(5, 3) == 8

    # Invalid
    with pytest.raises(TypeError):
        add("5", 3)
```

### Test 2: Return Type Validation
```python
def test_return_validation():
    def get_age() -> int:
        result = fetch_data()  # Might return wrong type
        if not isinstance(result, int):
            raise TypeError(f"Expected int, got {type(result).__name__}")
        return result

    # Should raise if fetch_data returns non-int
    with pytest.raises(TypeError):
        get_age()  # Assuming fetch_data returns string
```

### Test 3: Generic Container Validation
```python
def test_container_validation():
    def sum_list(items: list[int]) -> int:
        if not all(isinstance(x, int) for x in items):
            raise TypeError("All elements must be int")
        return sum(items)

    # Valid
    assert sum_list([1, 2, 3]) == 6

    # Invalid
    with pytest.raises(TypeError):
        sum_list([1, "2", 3])
```

---

## Common Mistakes

### Mistake 1: Checking Type Instead of Protocol
**Problem**: Checking exact type instead of capability

**Solution**: Check for required methods/attributes

```python
# ❌ Bad: overly strict
def process(items):
    if not isinstance(items, list):
        raise TypeError("Must be list")

# ✅ Good: duck typing
def process(items):
    if not hasattr(items, '__iter__'):
        raise TypeError("Must be iterable")
```

### Mistake 2: Validating in Hot Paths
**Problem**: Runtime checks slow down performance-critical code

**Solution**: Validate at boundaries only, use debug mode

```python
# ❌ Bad: validation in loop
def process_items(items):
    results = []
    for item in items:
        if not isinstance(item, int):  # Check every iteration!
            raise TypeError()
        results.append(item * 2)
    return results

# ✅ Good: validate once
def process_items(items):
    # Validate before loop
    if not all(isinstance(x, int) for x in items):
        raise TypeError("All items must be int")

    return [item * 2 for item in items]
```

### Mistake 3: Inconsistent Error Messages
**Problem**: Type errors lack context

**Solution**: Include parameter name, expected and actual types

```python
# ❌ Bad: vague error
if not isinstance(age, int):
    raise TypeError("Wrong type")

# ✅ Good: descriptive error
if not isinstance(age, int):
    raise TypeError(
        f"Parameter 'age' must be int, got {type(age).__name__}"
    )
```

---

## Roadblocks

### Roadblock 1: No Type Info
**Issue**: Function lacks type annotations
**Resolution**: Add type annotations first, then generate runtime checks

### Roadblock 2: Dynamic Violation
**Issue**: Runtime type check detects violation
**Resolution**: Log or raise descriptive error with context

### Roadblock 3: Performance Cost
**Issue**: Validation overhead unacceptable
**Resolution**: Use debug-only checks, validate at boundaries only

---

## Integration Points

### With `fp_type_safety`
Runtime checks enforce static type annotations.

### With `fp_type_inference`
Inferred types can be validated at runtime.

### With `project_compliance_check`
Validates runtime check coverage at API boundaries.

---

## Intent Keywords

- `runtime type`
- `validation`
- `assert type`
- `type guard`
- `isinstance`

---

## Confidence Threshold

**0.7** - High confidence for inserting runtime checks.

---

## Notes

- Runtime checks complement static typing, not replace
- Python type hints are not enforced without runtime checks
- Validate at API boundaries (external interfaces)
- Use `__debug__` flag for optional production checks
- Validation libraries (Pydantic, Zod) provide robust validation
- Type erasure (Python generics, Java) requires runtime validation
- Duck typing valid alternative to strict type checks
- Performance: validate once, not repeatedly
- Include context in error messages (parameter name, expected/actual type)
- Runtime checks catch integration errors with untyped code
