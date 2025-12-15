# fp_type_safety

## Purpose

The `fp_type_safety` directive verifies that all function signatures include explicit type information and that return types are deterministic. It enforces strong typing discipline within FP code by detecting missing type annotations, inferring types where possible, and ensuring type consistency across function boundaries. This ensures AI-generated code is type-safe, self-documenting, and easier to reason about.

**Category**: Type System
**Type**: FP Core
**Priority**: High
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`check_function_signatures`**: Scan all function definitions for type annotations on parameters and return types.

### Branches

1. **`missing_types`** → **`infer_and_insert`**
   - **Condition**: Function parameters or return type lack type annotations
   - **Action**: Use AI-assisted type inference to determine types and insert annotations
   - **Details**: Analyze function body, call sites, and usage patterns
   - **Output**: Fully typed function signature

2. **`type_conflict`** → **`prompt_user`**
   - **Condition**: Inferred types conflict with existing annotations or usage
   - **Action**: Request user clarification on correct types
   - **Details**: Present conflicting type evidence for resolution

3. **`inconsistent_return_type`** → **`unify_return_paths`**
   - **Condition**: Multiple return statements with incompatible types
   - **Action**: Unify return types using union types or common supertype
   - **Details**: Create discriminated union if needed
   - **Output**: Consistent return type annotation

4. **`fully_typed`** → **`mark_compliant`**
   - **Condition**: Function has complete, consistent type annotations
   - **Action**: Mark as type-safe and record in database
   - **Output**: Compliance confirmation

5. **Fallback** → **`prompt_user`**
   - **Condition**: Type inference fails or ambiguous
   - **Action**: Request explicit type annotations from user

### Error Handling
- **On failure**: Prompt user with type analysis details
- **Low confidence** (< 0.7): Request user review before inserting types

---

## Refactoring Strategies

### Strategy 1: Add Parameter Type Annotations
Infer and add missing parameter types based on usage.

**Before (Python - Non-Compliant)**:
```python
def calculate_total(items, tax_rate):
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    return subtotal * (1 + tax_rate)
```

**After (Python - Compliant)**:
```python
from typing import TypedDict

class Item(TypedDict):
    price: float
    quantity: int

def calculate_total(items: list[Item], tax_rate: float) -> float:
    """Calculate total price with tax."""
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    return subtotal * (1 + tax_rate)
```

### Strategy 2: Add Return Type Annotations
Analyze return statements to determine and annotate return types.

**Before (TypeScript - Non-Compliant)**:
```typescript
function parseConfig(raw) {  // Missing types
  try {
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}
```

**After (TypeScript - Compliant)**:
```typescript
interface Config {
  apiKey: string;
  timeout: number;
}

function parseConfig(raw: string): Config | null {
  try {
    return JSON.parse(raw) as Config;
  } catch (e) {
    return null;
  }
}
```

### Strategy 3: Generic Type Parameters
Add generic constraints for polymorphic functions.

**Before (Python - Non-Compliant)**:
```python
def first_element(items):
    if not items:
        return None
    return items[0]
```

**After (Python - Compliant)**:
```python
from typing import TypeVar, Sequence, Optional

T = TypeVar('T')

def first_element(items: Sequence[T]) -> Optional[T]:
    """Return first element of sequence, or None if empty."""
    if not items:
        return None
    return items[0]
```

### Strategy 4: Discriminated Union Return Types
Use tagged unions for functions with multiple return variants.

**Before (Python - Non-Compliant)**:
```python
def divide(a, b):
    if b == 0:
        return {"error": "Division by zero"}
    return {"result": a / b}
```

**After (Python - Compliant)**:
```python
from dataclasses import dataclass
from typing import Union, Literal

@dataclass(frozen=True)
class DivisionSuccess:
    kind: Literal["success"] = "success"
    result: float

@dataclass(frozen=True)
class DivisionError:
    kind: Literal["error"] = "error"
    message: str

DivisionResult = Union[DivisionSuccess, DivisionError]

def divide(a: float, b: float) -> DivisionResult:
    """Divide a by b, returning Result type."""
    if b == 0:
        return DivisionError(message="Division by zero")
    return DivisionSuccess(result=a / b)
```

### Strategy 5: Rust Type Safety (Native)
Leverage Rust's compile-time type safety.

**Before (Rust - Less Explicit)**:
```rust
fn process_data(data) -> _ {  // Invalid: missing types
    data.len()
}
```

**After (Rust - Compliant)**:
```rust
fn process_data(data: &[i32]) -> usize {
    data.len()
}

// With generic for flexibility
fn process_data_generic<T>(data: &[T]) -> usize {
    data.len()
}
```

---

## Examples

### Example 1: API Response Handler

**Non-Compliant**:
```python
def handle_response(response):
    if response['status'] == 200:
        return response['data']
    else:
        raise Exception(response['error'])
```

**Compliant**:
```python
from dataclasses import dataclass
from typing import TypedDict, Union, Literal

class ApiResponse(TypedDict):
    status: int
    data: dict
    error: str

@dataclass(frozen=True)
class Success:
    kind: Literal["success"] = "success"
    data: dict

@dataclass(frozen=True)
class Failure:
    kind: Literal["failure"] = "failure"
    error: str

Result = Union[Success, Failure]

def handle_response(response: ApiResponse) -> Result:
    """Parse API response into Result type."""
    if response['status'] == 200:
        return Success(data=response['data'])
    else:
        return Failure(error=response['error'])
```

### Example 2: Data Transformation Pipeline

**Non-Compliant** (TypeScript):
```typescript
function transformData(data) {
  return data
    .filter(item => item.active)
    .map(item => item.value)
    .reduce((sum, val) => sum + val, 0);
}
```

**Compliant** (TypeScript):
```typescript
interface DataItem {
  active: boolean;
  value: number;
}

function transformData(data: DataItem[]): number {
  return data
    .filter((item: DataItem): boolean => item.active)
    .map((item: DataItem): number => item.value)
    .reduce((sum: number, val: number): number => sum + val, 0);
}
```

### Example 3: Higher-Order Function

**Compliant** (Python with precise types):
```python
from typing import Callable, TypeVar, Sequence

T = TypeVar('T')
U = TypeVar('U')

def map_fn(
    fn: Callable[[T], U],
    items: Sequence[T]
) -> list[U]:
    """Map function over sequence with full type safety."""
    return [fn(item) for item in items]

# Usage with type inference
def double(x: int) -> int:
    return x * 2

result: list[int] = map_fn(double, [1, 2, 3])  # Type-safe!
```

---

## Edge Cases

### Edge Case 1: Dynamic Type Widening
**Scenario**: Function accepts multiple types but lacks union annotation
**Issue**: Type checker cannot verify correctness
**Handling**:
- Add explicit Union type annotation
- Consider creating separate functions for each type
- Use generics if behavior is type-agnostic

**Example**:
```python
# ❌ Bad: Implicit any type
def format_value(value):
    if isinstance(value, int):
        return f"{value:,}"
    elif isinstance(value, float):
        return f"{value:.2f}"
    else:
        return str(value)

# ✅ Good: Explicit union type
from typing import Union

def format_value(value: Union[int, float, str]) -> str:
    """Format value based on type."""
    if isinstance(value, int):
        return f"{value:,}"
    elif isinstance(value, float):
        return f"{value:.2f}"
    else:
        return str(value)
```

### Edge Case 2: Callback Types
**Scenario**: Function accepts callback but callback signature unclear
**Issue**: Callback type not specified, unsafe calls possible
**Handling**:
- Use `Callable[[ArgType], ReturnType]` annotation
- Specify exact callback signature
- Use Protocol for complex callback interfaces

**Example**:
```python
from typing import Callable

# ✅ Good: Precise callback type
def retry_operation(
    operation: Callable[[], bool],
    max_attempts: int
) -> bool:
    """Retry operation until success or max attempts reached."""
    for attempt in range(max_attempts):
        if operation():
            return True
    return False
```

### Edge Case 3: Recursive Type Definitions
**Scenario**: Type references itself (e.g., tree structures)
**Issue**: Forward references and cyclic definitions
**Handling**:
- Use string forward references (`'TreeNode'`)
- Use `typing.ForwardRef` in Python
- Use proper type aliasing

**Example**:
```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class TreeNode:
    value: int
    left: Optional[TreeNode] = None  # Forward reference
    right: Optional[TreeNode] = None

def tree_height(node: Optional[TreeNode]) -> int:
    """Calculate height of tree with recursive type."""
    if node is None:
        return 0
    left_height = tree_height(node.left)
    right_height = tree_height(node.right)
    return 1 + max(left_height, right_height)
```

### Edge Case 4: Complex Generic Constraints
**Scenario**: Generic function requires multiple type constraints
**Issue**: Type bounds become complex and hard to express
**Handling**:
- Use TypeVar with bounds
- Use Protocol for structural typing
- Document type constraints clearly

**Example**:
```python
from typing import TypeVar, Protocol

class Comparable(Protocol):
    def __lt__(self, other: Comparable) -> bool: ...

T = TypeVar('T', bound=Comparable)

def find_min(items: list[T]) -> Optional[T]:
    """Find minimum element in list (requires comparable type)."""
    if not items:
        return None
    min_item = items[0]
    for item in items[1:]:
        if item < min_item:
            min_item = item
    return min_item
```

### Edge Case 5: Type Narrowing in Conditionals
**Scenario**: Type narrows based on runtime checks (type guards)
**Issue**: Type checker may not understand narrowing
**Handling**:
- Use `isinstance` checks for automatic narrowing
- Use `TypeGuard` for custom type guards
- Add explicit type assertions when safe

**Example** (TypeScript):
```typescript
type User = { type: 'user'; name: string };
type Admin = { type: 'admin'; name: string; permissions: string[] };
type Account = User | Admin;

function isAdmin(account: Account): account is Admin {
  return account.type === 'admin';
}

function getPermissions(account: Account): string[] {
  if (isAdmin(account)) {
    // Type narrowed to Admin
    return account.permissions;
  }
  return [];
}
```

---

## Database Operations

### Insert Type Safety Metadata

```sql
-- Update function with type information
UPDATE functions
SET
    has_type_annotations = 1,
    parameter_types = '["items: list[Item]", "tax_rate: float"]',
    return_type = 'float',
    type_safety_level = 'fully_typed',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'calculate_total' AND file_id = ?;
```

### Query Functions Missing Type Annotations

```sql
-- Find functions without complete type information
SELECT f.id, f.name, f.file_id, f.parameter_types, f.return_type
FROM functions f
WHERE f.has_type_annotations = 0
   OR f.parameter_types IS NULL
   OR f.return_type IS NULL
ORDER BY f.complexity_score DESC;
```

---

## Related Directives

### FP Directives
- **fp_type_inference**: Assists with inferring missing types
- **fp_generic_constraints**: Adds constraints to generic type parameters
- **fp_runtime_type_check**: Adds runtime validation when static types insufficient
- **fp_adt**: Defines algebraic data types for type-safe domain modeling

### Project Directives
- **project_compliance_check**: Validates type annotation completeness
- **project_update_db**: Records type safety transformations

---

## Helper Functions

### `extract_type_from_usage(function_def, param_name) -> Type`
Infers parameter type from usage patterns within function body.

**Signature**:
```python
def extract_type_from_usage(
    function_def: FunctionDefinition,
    param_name: str
) -> Type:
    """
    Analyzes how parameter is used to infer its type.
    Looks at method calls, operators, and context.
    """
```

### `infer_return_type(function_body) -> Type`
Analyzes all return statements to infer consistent return type.

**Signature**:
```python
def infer_return_type(function_body: ASTNode) -> Type:
    """
    Examines all return statements to determine return type.
    Creates Union type if multiple distinct types returned.
    """
```

### `validate_type_consistency(function_def) -> list[TypeError]`
Checks for type inconsistencies in function definition.

**Signature**:
```python
def validate_type_consistency(
    function_def: FunctionDefinition
) -> list[TypeError]:
    """
    Validates that:
    - Return statements match declared return type
    - Parameter usage matches declared types
    - No implicit type widening occurs
    """
```

---

## Testing

### Test 1: Missing Type Detection
```python
def test_detect_missing_types():
    source = """
def add(a, b):
    return a + b
"""

    issues = fp_type_safety.check(source)

    assert len(issues) == 3  # 2 params + 1 return type missing
    assert any('parameter a' in issue for issue in issues)
    assert any('parameter b' in issue for issue in issues)
    assert any('return type' in issue for issue in issues)
```

### Test 2: Type Inference
```python
def test_infer_parameter_types():
    source = """
def calculate_total(items, tax_rate):
    subtotal = sum(item['price'] for item in items)
    return subtotal * (1 + tax_rate)
"""

    result = fp_type_safety.refactor(source, language="python")

    # Should infer list type for items
    assert "items: list" in result or "items: Sequence" in result
    # Should infer numeric type for tax_rate
    assert "tax_rate: float" in result
    # Should infer float return
    assert "-> float" in result
```

### Test 3: Type Conflict Detection
```python
def test_detect_type_conflicts():
    source = """
def process(value: int) -> str:
    if value > 0:
        return value  # Type error: returning int, declared str
    return "zero"
"""

    issues = fp_type_safety.check(source)

    assert len(issues) > 0
    assert any('type conflict' in issue.lower() for issue in issues)
    assert any('return type' in issue.lower() for issue in issues)
```

---

## Common Mistakes

### Mistake 1: Overly Broad Types
**Problem**: Using `Any` or overly generic types defeats type safety

**Solution**: Use specific types or constrained generics

```python
# ❌ Bad: Too broad
from typing import Any

def process(data: Any) -> Any:
    return data['key']

# ✅ Good: Specific types
from typing import TypedDict

class DataDict(TypedDict):
    key: str
    value: int

def process(data: DataDict) -> str:
    return data['key']
```

### Mistake 2: Ignoring Type Errors
**Problem**: Using type: ignore comments to suppress valid errors

**Solution**: Fix the underlying type issue

```python
# ❌ Bad: Suppressing type error
def get_value(data: dict) -> int:
    return data.get('value')  # type: ignore  # Returns Optional[int]!

# ✅ Good: Handle optional properly
from typing import Optional

def get_value(data: dict) -> Optional[int]:
    return data.get('value')
```

### Mistake 3: Missing Generic Constraints
**Problem**: Generic function without proper constraints

**Solution**: Add type bounds or protocols

```python
# ❌ Bad: Unconstrained generic
from typing import TypeVar

T = TypeVar('T')

def find_max(items: list[T]) -> T:
    return max(items)  # T might not be comparable!

# ✅ Good: Constrained generic
from typing import TypeVar, Protocol

class Comparable(Protocol):
    def __lt__(self, other: Comparable) -> bool: ...

T = TypeVar('T', bound=Comparable)

def find_max(items: list[T]) -> T:
    """Find maximum element (T must be comparable)."""
    return max(items)
```

---

## Roadblocks

### Roadblock 1: Missing Annotation
**Issue**: Function parameters or return type lack type annotations
**Resolution**: Infer types from usage or request user to provide explicit types

### Roadblock 2: Type Mismatch
**Issue**: Declared type conflicts with actual usage or return statements
**Resolution**: Resolve via type inference or prompt user for correct type

### Roadblock 3: Complex Generic Type
**Issue**: Generic type requires complex bounds or constraints
**Resolution**: Use Protocol for structural typing or simplify generic constraints

### Roadblock 4: Dynamic Type Requirement
**Issue**: Function genuinely requires dynamic typing (e.g., metaprogramming)
**Resolution**: Use Union types, document dynamic behavior, add runtime checks

---

## Integration Points

### With `fp_type_inference`
Type safety directive uses type inference to fill missing annotations.

### With `fp_runtime_type_check`
When static types insufficient, add runtime type validation.

### With `fp_adt`
Algebraic Data Types enable type-safe discriminated unions.

### With `project_compliance_check`
Validates that all functions have complete type annotations.

---

## Intent Keywords

- `type`
- `annotation`
- `signature`
- `type safety`
- `type check`
- `typed`

---

## Confidence Threshold

**0.7** - High confidence required for automatic type insertion to avoid incorrect annotations.

---

## Notes

- Python requires `mypy` or `pyright` for static type checking
- TypeScript has built-in type checking at compile time
- Rust enforces type safety at compile time (no runtime overhead)
- Always prefer explicit types over inferred types for clarity
- Use `typing` module in Python 3.9+ for cleaner syntax (list[int] vs List[int])
- Generic types enable code reuse without sacrificing type safety
- Discriminated unions (tagged unions) enable exhaustive pattern matching
- Type annotations serve as inline documentation
- Static type checking catches bugs before runtime
