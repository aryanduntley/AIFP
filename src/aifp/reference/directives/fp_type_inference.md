# fp_type_inference

## Purpose

The `fp_type_inference` directive performs AI-assisted static-like type inference for dynamic languages when explicit type annotations are not present. It analyzes function bodies, call sites, usage patterns, and data flow to deduce likely input/output types, enabling soft type inference for dynamic contexts while maintaining functional programming discipline. This bridges the gap between dynamically typed languages and the type safety benefits of static typing.

**Category**: Type System
**Type**: FP Core
**Priority**: Medium
**Confidence Threshold**: 0.6

---

## Workflow

### Trunk
**`infer_types`**: Analyze function definitions, bodies, and call sites to deduce parameter and return types.

### Branches

1. **`ambiguous_types`** → **`prompt_user`**
   - **Condition**: Type inference produces multiple possible types with similar confidence
   - **Action**: Request user clarification on correct type
   - **Details**: Present inferred type candidates with reasoning

2. **`clear_pattern`** → **`store_in_metadata`**
   - **Condition**: Type inference produces high-confidence result
   - **Action**: Store inferred types in function metadata and database
   - **Details**: Record inference confidence and evidence

3. **`usage_based_inference`** → **`infer_from_operations`**
   - **Condition**: Type can be inferred from operations used on parameter
   - **Action**: Analyze operators, method calls, and built-in functions
   - **Details**: Build type constraints from usage patterns
   - **Output**: Inferred type based on operations

4. **`call_site_inference`** → **`infer_from_callers`**
   - **Condition**: Type can be inferred from how function is called
   - **Action**: Analyze arguments at call sites
   - **Details**: Collect argument types across all call sites
   - **Output**: Inferred type based on caller patterns

5. **Fallback** → **`mark_as_inferred`**
   - **Condition**: Inference completed with reasonable confidence
   - **Action**: Mark types as inferred (not explicit)

### Error Handling
- **On failure**: Prompt user for explicit type annotations
- **Low confidence** (< 0.6): Mark types as uncertain, request review

---

## Refactoring Strategies

### Strategy 1: Operation-Based Type Inference
Infer types from operations performed on parameters.

**Before (Python - Untyped)**:
```python
def calculate_area(width, height):
    return width * height
```

**Inference Process**:
- `width * height` → Both must support multiplication operator
- Result suggests numeric types (int, float)
- Return value is product → likely numeric

**Inferred Result**:
```python
# AIFP_INFERRED_TYPES
# Confidence: 0.85
# Evidence: multiplication operator, numeric return
def calculate_area(width: float, height: float) -> float:
    return width * height
```

### Strategy 2: Method Call-Based Inference
Infer types from method calls on parameters.

**Before (Python - Untyped)**:
```python
def process_text(text):
    return text.upper().strip()
```

**Inference Process**:
- `text.upper()` → text has `.upper()` method → likely str
- `.strip()` → confirms string type
- Return chained string methods → returns str

**Inferred Result**:
```python
# AIFP_INFERRED_TYPES
# Confidence: 0.95
# Evidence: string methods (.upper, .strip)
def process_text(text: str) -> str:
    return text.upper().strip()
```

### Strategy 3: Call Site Analysis
Infer types from how function is called throughout codebase.

**Before (JavaScript - Untyped)**:
```javascript
function calculateDiscount(price, percentage) {
  return price * (percentage / 100);
}

// Call sites:
calculateDiscount(100, 10);
calculateDiscount(49.99, 15);
calculateDiscount(200, 20);
```

**Inference Process**:
- All call sites pass numeric values
- First parameter: numbers (100, 49.99, 200)
- Second parameter: numbers (10, 15, 20)
- Return used as number in other calculations

**Inferred Result (TypeScript)**:
```typescript
// AIFP_INFERRED_TYPES
// Confidence: 0.90
// Evidence: call sites consistently use numbers
function calculateDiscount(price: number, percentage: number): number {
  return price * (percentage / 100);
}
```

### Strategy 4: Collection Type Inference
Infer container types from iteration and indexing patterns.

**Before (Python - Untyped)**:
```python
def sum_values(items):
    total = 0
    for item in items:
        total += item
    return total
```

**Inference Process**:
- `for item in items` → items is iterable
- `total += item` → item supports addition with int
- `total = 0` → accumulator is int
- Suggests `items` is sequence of numbers

**Inferred Result**:
```python
# AIFP_INFERRED_TYPES
# Confidence: 0.80
# Evidence: iteration, numeric addition
from typing import Sequence

def sum_values(items: Sequence[int | float]) -> int | float:
    total = 0
    for item in items:
        total += item
    return total
```

### Strategy 5: Return Type Inference from Control Flow
Infer return types by analyzing all return paths.

**Before (Python - Untyped)**:
```python
def find_user(user_id, database):
    for user in database:
        if user['id'] == user_id:
            return user
    return None
```

**Inference Process**:
- First return: `user` (dict with at least 'id' key)
- Second return: `None`
- Return type is `Optional[dict]` or specific User type

**Inferred Result**:
```python
# AIFP_INFERRED_TYPES
# Confidence: 0.75
# Evidence: dict access, Optional return pattern
from typing import Optional, TypedDict

class User(TypedDict):
    id: int
    # Additional fields would be inferred from usage

def find_user(user_id: int, database: list[User]) -> Optional[User]:
    for user in database:
        if user['id'] == user_id:
            return user
    return None
```

---

## Examples

### Example 1: String Manipulation Function

**Untyped**:
```python
def format_name(first, last):
    return f"{first.capitalize()} {last.capitalize()}"
```

**Inference Analysis**:
- `.capitalize()` method → both params are strings
- f-string interpolation → returns string
- No optional handling → both required

**Inferred**:
```python
# AIFP_INFERRED_TYPES (Confidence: 0.95)
def format_name(first: str, last: str) -> str:
    """Format full name with capitalization."""
    return f"{first.capitalize()} {last.capitalize()}"
```

### Example 2: Data Filtering Function

**Untyped (JavaScript)**:
```javascript
function filterActive(items) {
  return items.filter(item => item.active);
}
```

**Inference Analysis**:
- `.filter()` method → items is array
- `item.active` → items contain objects with `active` property
- Returns filtered array → same type as input

**Inferred (TypeScript)**:
```typescript
// AIFP_INFERRED_TYPES (Confidence: 0.85)
interface ItemWithActive {
  active: boolean;
  [key: string]: any;
}

function filterActive<T extends ItemWithActive>(items: T[]): T[] {
  return items.filter(item => item.active);
}
```

### Example 3: Numeric Calculation with Default

**Untyped**:
```python
def calculate_price(base, tax=0.1, discount=0):
    subtotal = base * (1 + tax)
    return subtotal - discount
```

**Inference Analysis**:
- Arithmetic operations → all numeric types
- Default values `0.1`, `0` → suggest float
- Return arithmetic expression → numeric

**Inferred**:
```python
# AIFP_INFERRED_TYPES (Confidence: 0.90)
def calculate_price(
    base: float,
    tax: float = 0.1,
    discount: float = 0
) -> float:
    """Calculate final price with tax and discount."""
    subtotal = base * (1 + tax)
    return subtotal - discount
```

### Example 4: Dictionary Access Pattern

**Untyped**:
```python
def get_user_email(user):
    return user.get('email', 'no-email@example.com')
```

**Inference Analysis**:
- `.get()` method → user is dict-like
- 'email' key access → dict with string keys
- Default string value → returns string
- `.get()` with default → safe access pattern

**Inferred**:
```python
# AIFP_INFERRED_TYPES (Confidence: 0.80)
from typing import TypedDict

class User(TypedDict, total=False):
    email: str

def get_user_email(user: User) -> str:
    """Get user email with fallback default."""
    return user.get('email', 'no-email@example.com')
```

---

## Edge Cases

### Edge Case 1: Polymorphic Functions
**Scenario**: Function works with multiple distinct types
**Issue**: Type inference produces union of many types
**Handling**:
- Use generic type variables for truly polymorphic functions
- Suggest refactoring into multiple specialized functions
- Document polymorphic behavior in comments

**Example**:
```python
# Function works with multiple types
def stringify(value):
    if isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        return ', '.join(str(v) for v in value)
    else:
        return str(value)

# Inferred with union type
from typing import Union

def stringify(value: Union[int, float, list, str]) -> str:
    """Convert various types to string representation."""
    if isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        return ', '.join(str(v) for v in value)
    else:
        return str(value)
```

### Edge Case 2: Insufficient Call Site Data
**Scenario**: Function defined but never called or called once
**Issue**: Cannot infer types from usage patterns
**Handling**:
- Rely on operation-based inference
- Check documentation or docstrings for type hints
- Flag for manual type annotation
- Use conservative `Any` type as fallback

### Edge Case 3: Type Changes Across Branches
**Scenario**: Variable type changes based on conditionals
**Issue**: Inconsistent types across code paths
**Handling**:
- Infer union type covering all branches
- Suggest type narrowing with type guards
- Flag potential type inconsistency issue

**Example**:
```python
def parse_value(raw):
    if raw.isdigit():
        return int(raw)  # Returns int
    else:
        return raw  # Returns str

# Inferred as union
def parse_value(raw: str) -> int | str:
    """Parse string to int if numeric, otherwise return as-is."""
    if raw.isdigit():
        return int(raw)
    else:
        return raw
```

### Edge Case 4: Generic Container Inference
**Scenario**: Empty container or container with mixed types
**Issue**: Cannot infer element type from empty container
**Handling**:
- Look for subsequent additions to container
- Check call sites for clues
- Use conservative `list[Any]` or request annotation

**Example**:
```python
# Empty list initialization
def collect_results():
    results = []  # Type unclear
    # ... later
    results.append(42)
    results.append(100)
    return results

# Inferred from usage
def collect_results() -> list[int]:
    """Collect numeric results."""
    results: list[int] = []
    # ... later
    results.append(42)
    results.append(100)
    return results
```

### Edge Case 5: Callback Type Inference
**Scenario**: Function accepts callback but signature unclear
**Issue**: Callback may have various signatures
**Handling**:
- Analyze how callback is invoked within function
- Infer parameter and return types from calls
- Use `Callable` with inferred signature

**Example**:
```python
def retry_operation(operation):
    for attempt in range(3):
        result = operation()  # Called with no args
        if result:
            return result
    return None

# Inferred callback type
from typing import Callable, Optional

def retry_operation(
    operation: Callable[[], bool]
) -> Optional[bool]:
    """Retry operation up to 3 times."""
    for attempt in range(3):
        result = operation()
        if result:
            return result
    return None
```

---

## Database Operations

### Store Inferred Type Metadata

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Query Functions Needing Type Inference

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Related Directives

### FP Directives
- **fp_type_safety**: Uses type inference to fill missing annotations
- **fp_runtime_type_check**: Adds runtime validation for inferred types
- **fp_generic_constraints**: Infers generic type bounds
- **fp_adt**: Infers discriminated union types from usage

### Project Directives
- **project_compliance_check**: Validates inferred types meet standards
- **project_update_db**: Records type inference results

---

## Helper Functions

### `infer_from_operations(param_usage) -> Type`
Infers type based on operations performed on parameter.

**Signature**:
```python
def infer_from_operations(param_usage: list[Operation]) -> Type:
    """
    Analyzes operations (method calls, operators, built-ins) to infer type.
    Returns inferred type with confidence score.
    """
```

### `infer_from_call_sites(function_name, project_files) -> dict[str, Type]`
Analyzes all call sites to infer parameter types.

**Signature**:
```python
def infer_from_call_sites(
    function_name: str,
    project_files: list[str]
) -> dict[str, Type]:
    """
    Scans project for function calls, collects argument types.
    Returns dict mapping parameter names to inferred types.
    """
```

### `unify_types(type_list) -> Type`
Unifies multiple type candidates into single type or union.

**Signature**:
```python
def unify_types(type_list: list[Type]) -> Type:
    """
    Takes multiple inferred types and unifies them.
    Returns union type if types incompatible, or common supertype.
    """
```

### `calculate_inference_confidence(evidence) -> float`
Calculates confidence score for type inference.

**Signature**:
```python
def calculate_inference_confidence(evidence: InferenceEvidence) -> float:
    """
    Computes confidence score (0.0-1.0) based on:
    - Number of call sites analyzed
    - Consistency of inferred types
    - Quality of evidence (operations, methods)
    Returns confidence score.
    """
```

---

## Testing

### Test 1: String Method Inference
```python
def test_infer_string_type():
    source = """
def process(text):
    return text.upper().strip()
"""

    result = fp_type_inference.infer(source)

    assert result['parameters']['text']['type'] == 'str'
    assert result['return_type']['type'] == 'str'
    assert result['parameters']['text']['confidence'] > 0.9
```

### Test 2: Numeric Operation Inference
```python
def test_infer_numeric_types():
    source = """
def calculate(a, b):
    return a * b + 10
"""

    result = fp_type_inference.infer(source)

    assert result['parameters']['a']['type'] in ['int', 'float', 'int | float']
    assert result['parameters']['b']['type'] in ['int', 'float', 'int | float']
    assert result['return_type']['type'] in ['int', 'float', 'int | float']
```

### Test 3: Call Site Inference
```python
def test_infer_from_call_sites():
    source = """
def format_message(name, age):
    return f"{name} is {age} years old"

# Call sites
format_message("Alice", 30)
format_message("Bob", 25)
"""

    result = fp_type_inference.infer(source, analyze_calls=True)

    assert result['parameters']['name']['type'] == 'str'
    assert result['parameters']['age']['type'] == 'int'
    assert result['parameters']['name']['confidence'] > 0.85
```

---

## Common Mistakes

### Mistake 1: Over-Specific Type Inference
**Problem**: Inferring overly specific types that limit flexibility

**Solution**: Use generic types or unions when appropriate

```python
# ❌ Too specific inference
def process_items(items):  # Used with [1, 2, 3] once
    return [item * 2 for item in items]

# Inferred too narrowly: list[int] (only from one call site)
# Better: list[int | float] or generic T

# ✅ Better inference with generics
from typing import TypeVar

T = TypeVar('T', int, float)

def process_items(items: list[T]) -> list[T]:
    return [item * 2 for item in items]
```

### Mistake 2: Ignoring Confidence Scores
**Problem**: Applying low-confidence inferences without validation

**Solution**: Only apply high-confidence inferences automatically

```python
# Check confidence before applying inference
if inference_result['confidence'] < 0.7:
    # Flag for manual review
    add_review_note(function, "Low confidence type inference")
else:
    # Apply inference automatically
    apply_inferred_types(function, inference_result)
```

### Mistake 3: Missing Union Types
**Problem**: Inferring single type when function handles multiple types

**Solution**: Detect polymorphic behavior and use union types

```python
# Function handles multiple types
def format_value(val):
    if isinstance(val, int):
        return f"{val:,}"
    elif isinstance(val, str):
        return val.upper()
    return str(val)

# ✅ Correct union inference
from typing import Union

def format_value(val: Union[int, str]) -> str:
    if isinstance(val, int):
        return f"{val:,}"
    elif isinstance(val, str):
        return val.upper()
    return str(val)
```

---

## Roadblocks

### Roadblock 1: Unclear Type
**Issue**: Type inference produces ambiguous or low-confidence result
**Resolution**: Request user clarification, document evidence gathered

### Roadblock 2: Inconsistent Type
**Issue**: Different code paths or call sites suggest different types
**Resolution**: Create union type or flag inconsistency for review

### Roadblock 3: No Usage Evidence
**Issue**: Function never called or insufficient operations to infer from
**Resolution**: Mark for manual annotation, use conservative Any type

### Roadblock 4: Complex Generic
**Issue**: Inference produces overly complex generic type
**Resolution**: Simplify to practical union type or request manual annotation

---

## Integration Points

### With `fp_type_safety`
Type inference provides missing types for type safety validation.

### With `fp_runtime_type_check`
Inferred types used to generate runtime type validation.

### With `project_compliance_check`
Validates that inferred types are reasonable and consistent.

### With Database
Stores inference confidence and evidence for future refinement.

---

## Intent Keywords

- `type inference`
- `deduce`
- `infer`
- `type deduction`
- `inferred types`
- `soft typing`

---

## Confidence Threshold

**0.6** - Moderate confidence acceptable as inferences are marked and reviewable.

---

## Notes

- Type inference is probabilistic and may require user validation
- Store confidence scores with all inferred types
- Prefer operation-based inference over call-site inference (more reliable)
- Mark inferred types distinctly from explicit annotations
- Re-run type inference when functions or call sites change
- Use inference as suggestion, not definitive truth
- Higher confidence thresholds (0.8+) allow automatic type annotation insertion
- Lower confidence (0.5-0.7) should flag for manual review
- Document inference method and evidence in metadata
- Type inference improves over time as more code is analyzed
