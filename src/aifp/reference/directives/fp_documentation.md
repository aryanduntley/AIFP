# fp_documentation

## Purpose

The `fp_documentation` directive enforces comprehensive documentation standards for functional programming code, ensuring every pure function, data type, and module is properly documented with signatures, examples, and purity guarantees. It establishes patterns for documenting function contracts, type constraints, error conditions, and usage examples that enable AI assistants and developers to understand code behavior without reading implementations.

**Category**: Code Quality
**Type**: FP Auxiliary
**Priority**: High
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`analyze_documentation_coverage`**: Scan codebase for documentation completeness and FP-specific annotations.

### Branches

1. **`function_doc_check`** → **`validate_docstring_completeness`**
   - **Condition**: Function defined without docstring or incomplete docstring
   - **Action**: Require docstring with signature, description, purity note, examples
   - **Details**: Every function must document inputs, outputs, purity level, side effects
   - **Output**: Complete function documentation

2. **`type_doc_check`** → **`document_adt_invariants`**
   - **Condition**: Data type, ADT, or type alias defined
   - **Action**: Document type purpose, invariants, construction patterns
   - **Details**: Explain when to use type, constraints, example usage
   - **Output**: Type documentation

3. **`module_doc_check`** → **`add_module_overview`**
   - **Condition**: Module/file without module-level docstring
   - **Action**: Add module docstring explaining purpose, exports, relationships
   - **Details**: High-level overview of module responsibility
   - **Output**: Module documentation

4. **`purity_annotation_check`** → **`add_purity_markers`**
   - **Condition**: Function purity not documented
   - **Action**: Add purity annotation: `Pure`, `IO`, `Unsafe`, `Eff`
   - **Details**: Explicit markers in docstring or type annotations
   - **Output**: Purity-annotated function

5. **Fallback** → **`generate_documentation`**
   - **Condition**: Missing documentation detected
   - **Action**: Generate documentation template for review

### Error Handling
- **On failure**: Log documentation gap and generate template
- **Low confidence** (< 0.7): Request user review of generated docs

---

## Refactoring Strategies

### Strategy 1: Pure Function Documentation Standard

Pure functions require comprehensive docstrings with signature, description, purity guarantee, and examples.

**Before (Incomplete Documentation)**:
```python
def calculate_discount(price, percentage):
    return price * (percentage / 100)
```

**After (Complete FP Documentation)**:
```python
def calculate_discount(price: float, percentage: float) -> float:
    """
    Calculate discount amount from price and percentage.

    Pure function: Deterministic, no side effects. Same inputs always produce
    same output. Safe for memoization and parallel execution.

    Args:
        price: Original price in dollars (must be >= 0)
        percentage: Discount percentage (0-100 range)

    Returns:
        Discount amount in dollars

    Raises:
        ValueError: If price < 0 or percentage not in 0-100 range

    Examples:
        >>> calculate_discount(100.0, 10.0)
        10.0

        >>> calculate_discount(250.0, 25.0)
        62.5

    Notes:
        - Input validation should be done by caller or wrapper
        - Returns 0 for 0% discount
        - Pure function: safe to cache results

    See Also:
        apply_discount: Applies discount to price
        validate_discount_parameters: Validates inputs
    """
    if price < 0:
        raise ValueError(f"Price must be non-negative, got {price}")
    if not (0 <= percentage <= 100):
        raise ValueError(f"Percentage must be 0-100, got {percentage}")

    return price * (percentage / 100)
```

**Documentation Components**:
1. **One-line summary**: Brief description
2. **Purity statement**: Explicit pure function declaration
3. **Args**: Parameter descriptions with constraints
4. **Returns**: Return value description with type
5. **Raises**: Exception conditions
6. **Examples**: Doctest-compatible examples
7. **Notes**: Additional context, caveats
8. **See Also**: Related functions

---

### Strategy 2: Effect Function Documentation

Functions with side effects must explicitly document effects and when they occur.

**Before (Hidden Effects)**:
```typescript
async function getUser(userId: number) {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}
```

**After (Effect-Documented)**:
```typescript
/**
 * Fetch user data from API.
 *
 * IMPURE: Performs network I/O. Not deterministic - network failures, timeouts,
 * or server errors can occur. Not safe for caching without additional logic.
 *
 * @param userId - User ID to fetch
 * @returns Promise resolving to user data
 *
 * @throws NetworkError - If network request fails
 * @throws TimeoutError - If request exceeds timeout
 * @throws NotFoundError - If user ID doesn't exist (404)
 *
 * @effects
 * - Network I/O: HTTP GET request to /api/users/{userId}
 * - Non-deterministic: Result depends on server state
 * - Async operation: Delays execution
 *
 * @example
 * ```typescript
 * const user = await getUserIO(123);
 * console.log(user.name);
 * ```
 *
 * @see {@link buildUserRequest} for pure request builder
 * @see {@link parseUserResponse} for pure response parser
 */
async function getUserIO(userId: number): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.status}`);
  }
  return response.json();
}
```

**Effect Documentation Requirements**:
- **IMPURE marker**: Explicit at top of docstring
- **Effects section**: Lists all side effects
- **Non-determinism**: Notes unpredictable behavior
- **Errors**: Documents possible failures
- **Alternative pure functions**: Links to pure components

---

### Strategy 3: Data Type Documentation

ADTs and types require documentation of purpose, invariants, and usage patterns.

**Before (Undocumented Type)**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Order:
    id: int
    status: str
    items: list
    total: float
```

**After (Fully Documented Type)**:
```python
from dataclasses import dataclass
from typing import Literal

# Type alias with documentation
OrderStatus = Literal["pending", "processing", "completed", "failed", "cancelled"]
"""
Order processing status.

Valid states:
- pending: Order created, awaiting payment
- processing: Payment received, being fulfilled
- completed: Order fulfilled and delivered
- failed: Order processing failed (payment, inventory, etc.)
- cancelled: Order cancelled by user or system

Transitions:
- pending -> processing (on payment)
- pending -> cancelled (on user action)
- processing -> completed (on fulfillment)
- processing -> failed (on error)
- Any -> cancelled (on cancellation)
"""

@dataclass(frozen=True)
class OrderItem:
    """
    Immutable order line item.

    Represents a single product in an order with quantity and pricing.

    Attributes:
        product_id: Unique product identifier
        quantity: Number of units (must be > 0)
        unit_price: Price per unit in dollars (must be >= 0)
        total_price: Calculated total (quantity * unit_price)

    Invariants:
        - quantity > 0
        - unit_price >= 0
        - total_price == quantity * unit_price
        - immutable (frozen dataclass)

    Examples:
        >>> item = OrderItem(product_id=123, quantity=2, unit_price=10.0)
        >>> item.total_price
        20.0

    Notes:
        - Use create_order_item() factory for validation
        - Immutable by design (frozen=True)
    """
    product_id: int
    quantity: int
    unit_price: float

    @property
    def total_price(self) -> float:
        """Calculate total price for this line item."""
        return self.quantity * self.unit_price

@dataclass(frozen=True)
class Order:
    """
    Immutable order representation.

    Represents a complete customer order with items, status, and pricing.

    Attributes:
        id: Unique order identifier
        status: Current order status (see OrderStatus)
        items: Tuple of order items (immutable)
        total: Total order price in dollars

    Invariants:
        - items is non-empty tuple
        - total == sum of all item.total_price
        - status is valid OrderStatus
        - immutable (frozen dataclass)

    Type Safety:
        OrderStatus ensures status is valid enum value.

    Examples:
        >>> items = (OrderItem(123, 2, 10.0), OrderItem(456, 1, 5.0))
        >>> order = Order(id=1, status="pending", items=items, total=25.0)
        >>> order.total
        25.0

    Factory Functions:
        - create_order(): Validates and constructs Order
        - calculate_order_total(): Computes total from items

    See Also:
        OrderItem: Individual line items
        OrderStatus: Valid status values
        create_order: Validated order factory
    """
    id: int
    status: OrderStatus
    items: tuple[OrderItem, ...]
    total: float
```

**Type Documentation Components**:
1. **Purpose statement**: What this type represents
2. **Attributes**: Each field with description and constraints
3. **Invariants**: Rules that must always hold
4. **Type safety notes**: How types enforce correctness
5. **Examples**: Usage examples with expected output
6. **Factory functions**: Construction helpers
7. **See Also**: Related types and functions

---

### Strategy 4: Module-Level Documentation

Every module needs a comprehensive overview docstring.

**Before (No Module Documentation)**:
```python
# user_service.py
from typing import Optional

def get_user(user_id: int) -> Optional[dict]:
    pass

def create_user(name: str, email: str) -> dict:
    pass

def delete_user(user_id: int) -> bool:
    pass
```

**After (Documented Module)**:
```python
"""
User management service.

This module provides pure functions for user data manipulation and I/O functions
for user persistence. All business logic functions are pure, with side effects
isolated to IO-suffixed functions.

Architecture:
    - Pure functions: User validation, transformation, business logic
    - Effect functions: Database I/O, API calls (suffixed with IO)
    - Separation: Pure core + effect shell pattern

Exports:
    Pure Functions:
        - validate_user_data: Validates user input
        - transform_user_for_display: Formats user for UI
        - calculate_user_tier: Determines user tier from activity

    Effect Functions:
        - getUserIO: Fetches user from database
        - createUserIO: Persists new user
        - deleteUserIO: Removes user from database

Types:
    - User: Immutable user data
    - UserTier: User tier enum
    - ValidationResult: Validation outcome

Example Usage:
    ```python
    # Pure validation
    validation = validate_user_data({"name": "Alice", "email": "alice@example.com"})

    if validation.is_ok:
        # Effect: save to database
        user = await createUserIO(validation.value)

        # Pure transformation
        display_user = transform_user_for_display(user)
        print(display_user)
    ```

Dependencies:
    - database: Database connection utilities
    - validation: General validation helpers
    - types: Common type definitions

See Also:
    - auth_service: Authentication logic
    - user_types: User-related type definitions

Notes:
    - All mutations isolated to IO functions
    - Pure functions safe for testing, caching, parallel execution
    - Follows FP core principles: purity, immutability, composition

Author: AIFP Team
Version: 1.0
"""

from typing import Optional
from dataclasses import dataclass

# ... rest of module code
```

**Module Documentation Sections**:
1. **Brief description**: Module purpose
2. **Architecture**: Design patterns used
3. **Exports**: Public API with categories
4. **Types**: Exported type definitions
5. **Example usage**: Common use cases
6. **Dependencies**: External dependencies
7. **See Also**: Related modules
8. **Notes**: Important caveats
9. **Metadata**: Author, version

---

### Strategy 5: Inline Documentation for Complex Logic

Complex algorithms or non-obvious logic require inline comments explaining the "why".

**Before (No Inline Comments)**:
```python
def calculate_compound_interest(principal, rate, time):
    return principal * (1 + rate) ** time
```

**After (Explained Logic)**:
```python
def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int
) -> float:
    """
    Calculate compound interest using the standard formula.

    Pure function: Deterministic mathematical calculation.

    Formula: A = P(1 + r)^t
    Where:
        A = final amount
        P = principal (initial amount)
        r = annual interest rate (as decimal)
        t = time in years

    Args:
        principal: Initial investment amount in dollars
        annual_rate: Annual interest rate as decimal (e.g., 0.05 for 5%)
        years: Investment duration in years

    Returns:
        Final amount including interest

    Examples:
        >>> calculate_compound_interest(1000.0, 0.05, 10)
        1628.89

    Notes:
        - Assumes annual compounding (not monthly or daily)
        - Does not account for inflation
        - Uses exact years (not day-count conventions)
    """
    # Standard compound interest formula: A = P(1 + r)^t
    # We use Python's exponentiation operator for (1 + r)^t
    growth_factor = (1 + annual_rate) ** years

    # Multiply principal by growth factor to get final amount
    final_amount = principal * growth_factor

    return final_amount
```

---

## Examples

### Example 1: Result Type Documentation

```python
from typing import Generic, TypeVar, Union
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class Ok(Generic[T]):
    """
    Success variant of Result type.

    Represents successful computation with a value.

    Type Parameters:
        T: Type of success value

    Attributes:
        value: The successful result value

    Examples:
        >>> result = Ok(42)
        >>> result.value
        42

        >>> result.is_ok
        True
    """
    value: T

    @property
    def is_ok(self) -> bool:
        """Check if result is success."""
        return True

    @property
    def is_err(self) -> bool:
        """Check if result is error."""
        return False

@dataclass(frozen=True)
class Err(Generic[E]):
    """
    Error variant of Result type.

    Represents failed computation with an error value.

    Type Parameters:
        E: Type of error value

    Attributes:
        error: The error value

    Examples:
        >>> result = Err("Division by zero")
        >>> result.error
        "Division by zero"

        >>> result.is_err
        True
    """
    error: E

    @property
    def is_ok(self) -> bool:
        """Check if result is success."""
        return False

    @property
    def is_err(self) -> bool:
        """Check if result is error."""
        return True

Result = Union[Ok[T], Err[E]]
"""
Result type for explicit error handling.

Alternative to exceptions that makes error handling explicit in type signatures.
Represents either success (Ok) or failure (Err).

Type Parameters:
    T: Type of success value
    E: Type of error value

Usage:
    ```python
    def divide(a: float, b: float) -> Result[float, str]:
        if b == 0:
            return Err("Division by zero")
        return Ok(a / b)

    result = divide(10, 2)
    if result.is_ok:
        print(f"Result: {result.value}")
    else:
        print(f"Error: {result.error}")
    ```

Benefits:
    - Forces error handling at call site
    - Makes errors explicit in function signature
    - No hidden control flow (unlike exceptions)
    - Composable with map, flatMap, etc.

See Also:
    - Option: For optional values (Some/None)
    - Either: General-purpose discriminated union

References:
    - Rust Result: https://doc.rust-lang.org/std/result/
    - Haskell Either: https://hackage.haskell.org/package/base/docs/Data-Either.html
"""
```

---

## Edge Cases

### Edge Case 1: Generated Code
**Scenario**: Code generated by tools or macros
**Issue**: Auto-generated code lacks documentation
**Handling**:
- Add module-level note about generation
- Document generator inputs
- Provide usage examples even if implementation generated

### Edge Case 2: Trivial Functions
**Scenario**: Very simple one-liners like getters
**Issue**: Extensive docs seem excessive
**Handling**:
- Minimal but complete docstring
- One-line summary sufficient
- Type hints often self-documenting

### Edge Case 3: Private Internal Functions
**Scenario**: Internal helper functions not in public API
**Issue**: Documentation overhead for private code
**Handling**:
- Still document but less verbosely
- Focus on why it exists, not extensive examples
- Can omit examples if obvious

### Edge Case 4: Gradual Typing
**Scenario**: Dynamic languages without type hints
**Issue**: Type documentation less precise
**Handling**:
- Document types in docstring
- Use type comments if supported
- Provide example usages showing types

### Edge Case 5: Legacy Code
**Scenario**: Existing code without documentation
**Issue**: Retroactive documentation is time-consuming
**Handling**:
- Document incrementally as code is touched
- Prioritize public API functions
- Use automated docstring generators as starting point

---

## Database Operations

### Record Documentation Coverage

```sql
-- Update function with documentation metadata
UPDATE functions
SET
    has_docstring = 1,
    docstring_completeness = 95,
    documentation_metadata = json_set(
        COALESCE(documentation_metadata, '{}'),
        '$.has_examples', 1,
        '$.has_purity_note', 1,
        '$.has_type_annotations', 1
    ),
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'calculate_discount' AND file_id = ?;

-- Record documentation violation
INSERT INTO notes (project_id, content, tags, created_at)
VALUES (
    1,
    'DOCUMENTATION: Function "process_data" missing docstring with purity annotation',
    '["fp_documentation", "violation", "code_quality"]',
    CURRENT_TIMESTAMP
);
```

---

## Related Directives

### FP Directives
- **fp_purity**: Documentation must state purity level
- **fp_naming_conventions**: Names should match documentation
- **fp_type_safety**: Type hints complement documentation

### Project Directives
- **project_compliance_check**: Validates documentation coverage
- **project_update_db**: Records documentation metadata

---

## Helper Functions

### `check_docstring_completeness(function) -> float`
Calculates documentation completeness score.

**Signature**:
```python
def check_docstring_completeness(function: FunctionDef) -> float:
    """
    Analyzes function docstring completeness.
    Returns score 0.0-1.0 based on presence of required sections.
    """
```

### `generate_docstring_template(function) -> str`
Generates documentation template for function.

**Signature**:
```python
def generate_docstring_template(function: FunctionDef) -> str:
    """
    Creates docstring template based on function signature.
    Returns template string for user to fill in.
    """
```

---

## Testing

### Test 1: Docstring Presence
```python
def test_all_functions_have_docstrings():
    module = import_module("my_module")

    for name, obj in inspect.getmembers(module, inspect.isfunction):
        assert obj.__doc__ is not None, f"Function {name} missing docstring"
```

### Test 2: Purity Documentation
```python
def test_pure_functions_documented():
    source = """
def calculate_total(items):
    \"""Calculate total price. Pure function.\"""
    return sum(item.price for item in items)
"""

    analysis = fp_documentation.analyze(source)

    assert analysis.has_purity_marker == True
```

### Test 3: Examples in Docstrings
```python
def test_functions_have_examples():
    source = """
def double(x):
    \"""
    Double the input value.

    Examples:
        >>> double(5)
        10
    \"""
    return x * 2
"""

    analysis = fp_documentation.analyze(source)

    assert analysis.has_examples == True
```

---

## Common Mistakes

### Mistake 1: Missing Purity Statements
**Problem**: Not stating whether function is pure

**Solution**: Explicit purity declaration

```python
# ❌ Bad: no purity statement
def calculate(x, y):
    """Calculate something."""
    return x + y

# ✅ Good: explicit purity
def calculate(x, y):
    """Calculate sum. Pure function: no side effects."""
    return x + y
```

### Mistake 2: Documenting "What" Not "Why"
**Problem**: Repeating obvious implementation details

**Solution**: Explain purpose and rationale

```python
# ❌ Bad: documents obvious
def is_even(n):
    """Returns True if n modulo 2 equals 0."""
    return n % 2 == 0

# ✅ Good: explains purpose
def is_even(n):
    """Check if number is even (divisible by 2). Pure predicate."""
    return n % 2 == 0
```

### Mistake 3: No Examples
**Problem**: Missing usage examples

**Solution**: Include doctests or example code

```python
# ❌ Bad: no examples
def filter_active(users):
    """Filter active users."""
    return [u for u in users if u.active]

# ✅ Good: with example
def filter_active(users):
    """
    Filter active users from list.

    Examples:
        >>> users = [User(active=True), User(active=False)]
        >>> filter_active(users)
        [User(active=True)]
    """
    return [u for u in users if u.active]
```

---

## Roadblocks

### Roadblock 1: Documentation Debt
**Issue**: Large codebase with no documentation
**Resolution**: Incremental documentation, prioritize public API

### Roadblock 2: Documentation Drift
**Issue**: Code changes but docs don't update
**Resolution**: Automated checks, code review requirements

### Roadblock 3: Over-Documentation
**Issue**: Too verbose, slows development
**Resolution**: Templates, focus on public API, automate where possible

---

## Integration Points

### With `fp_purity`
Documentation must accurately reflect purity status.

### With `fp_naming_conventions`
Function names should match documentation descriptions.

### With `project_compliance_check`
Documentation completeness checked during compliance.

---

## Intent Keywords

- `documentation`
- `docstrings`
- `comments`
- `examples`
- `purity annotation`

---

## Confidence Threshold

**0.7** - High confidence for documentation compliance.

---

## Notes

- Every public function needs docstring
- Purity status must be documented
- Include usage examples
- Document side effects explicitly
- Type hints complement docstrings
- Module-level documentation provides context
- Inline comments explain "why" not "what"
- Keep documentation in sync with code
- Use doctest format for examples
- AIFP requires explicit documentation for AI understanding

