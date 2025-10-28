# Directive: fp_docstring_enforcement

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Ensures all functions are documented

---

## Purpose

The `fp_docstring_enforcement` directive ensures all functions have clear, structured docstrings that document purpose, parameters, return values, and behavior. This directive provides **documentation completeness** making code self-explanatory and maintainable.

Docstring enforcement provides **documentation quality**, enabling:
- **Self-Documenting Code**: Purpose clear from docstring
- **Parameter Documentation**: All parameters explained
- **Return Value Documentation**: What function returns
- **AI Understanding**: Context for AI reasoning
- **Maintainability**: Future developers understand code

This directive acts as a **documentation guardian** ensuring no function is undocumented.

---

## When to Apply

This directive applies when:
- **Writing new functions** - Add docstring on creation
- **Refactoring existing code** - Add or update docstrings
- **Code review** - Check docstring completeness
- **Project compliance** - Verify all functions documented
- **Called by project directives**:
  - `project_file_write` - Enforce docstrings before writing
  - `project_compliance_check` - Check documentation coverage
  - Works with `fp_metadata_annotation` - Complements metadata

---

## Workflow

### Trunk: check_docstring_presence

Validates that all functions have complete, well-structured docstrings.

**Steps**:
1. **Parse function** - Extract function signature
2. **Check docstring presence** - Function has docstring?
3. **Validate completeness** - Has purpose, params, return?
4. **Check format** - Follows standard format?
5. **Verify accuracy** - Docstring matches signature?
6. **Generate if missing** - Auto-generate docstring template

### Branches

**Branch 1: If docstring_missing**
- **Then**: `generate_docstring`
- **Details**: Function has no docstring
  - Analyze function signature
  - Generate purpose from name
  - Document all parameters
  - Document return type
  - Add examples if complex
  - Insert docstring
- **Result**: Returns function with docstring

**Branch 2: If docstring_incomplete**
- **Then**: `complete_docstring`
- **Details**: Docstring present but incomplete
  - Missing parameter documentation
  - Missing return documentation
  - Missing purpose description
  - Add missing sections
  - Preserve existing content
- **Result**: Returns complete docstring

**Branch 3: If docstring_outdated**
- **Then**: `update_docstring`
- **Details**: Function changed, docstring stale
  - Parameters added or removed
  - Return type changed
  - Purpose evolved
  - Update docstring to match
  - Mark as updated
- **Result**: Returns updated docstring

**Branch 4: If docstring_compliant**
- **Then**: `mark_compliant`
- **Details**: Docstring is complete and accurate
  - Has purpose description
  - All parameters documented
  - Return value documented
  - Format correct
  - Matches function signature
- **Result**: Function passes check

**Fallback**: `prompt_user`
- **Details**: Complex function needing user explanation
  - Purpose unclear from name
  - Complex behavior
  - Ask user to write docstring
- **Result**: User provides docstring

---

## Examples

### ✅ Compliant Code

**Complete Docstring (Passes):**

```python
def calculate_total(items: list[float], tax_rate: float) -> float:
    """Calculate total price including tax.

    Sums all item prices and applies the given tax rate to compute
    the final total amount.

    Args:
        items: List of item prices to sum
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

    Returns:
        Total price including tax

    Examples:
        >>> calculate_total([10.0, 20.0], 0.08)
        32.4
    """
    subtotal = sum(items)
    tax = subtotal * tax_rate
    return subtotal + tax

# ✅ Complete docstring
# ✅ Purpose clearly explained
# ✅ All parameters documented
# ✅ Return value documented
# ✅ Example provided
```

**Why Compliant**:
- Purpose clearly described
- All parameters documented with types
- Return value documented
- Example shows usage
- Format is standard

---

**Result Type Documented (Passes):**

```python
def divide_safe(a: float, b: float) -> Result[float, str]:
    """Safely divide two numbers.

    Performs division with zero-check, returning Result type
    for error handling.

    Args:
        a: Numerator (dividend)
        b: Denominator (divisor)

    Returns:
        Ok(result) if successful
        Err(message) if division by zero

    Examples:
        >>> divide_safe(10.0, 2.0)
        Ok(5.0)
        >>> divide_safe(10.0, 0.0)
        Err("Division by zero")
    """
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

# ✅ Result type documented
# ✅ Both success and error cases explained
# ✅ Examples show both paths
```

**Why Compliant**:
- Result type both cases documented
- Error conditions explained
- Examples show success and error
- Clear error messages

---

**Pure Function Documented (Passes):**

```python
def map_transform(items: list[int], func: Callable[[int], int]) -> list[int]:
    """Apply transformation function to each item.

    Pure functional map operation that transforms each element
    in the list using the provided function. Does not mutate
    the input list.

    Args:
        items: Input list of integers
        func: Pure transformation function to apply

    Returns:
        New list with transformed elements

    Notes:
        This is a pure function - same inputs produce same outputs.
        The input list is not modified.

    Examples:
        >>> map_transform([1, 2, 3], lambda x: x * 2)
        [2, 4, 6]
    """
    return [func(item) for item in items]

# ✅ Purity explicitly documented
# ✅ Immutability noted
# ✅ Higher-order function explained
```

**Why Compliant**:
- Purity explicitly mentioned
- Immutability documented
- Higher-order function clearly explained
- Examples show usage

---

### ❌ Non-Compliant Code

**Missing Docstring (Violation):**

```python
# ❌ VIOLATION: No docstring
def calculate_total(items: list[float], tax_rate: float) -> float:
    subtotal = sum(items)
    tax = subtotal * tax_rate
    return subtotal + tax

# Problem:
# - No docstring at all
# - Purpose unclear
# - Parameters not documented
# - Return value not explained
# - Future maintainers confused
```

**Why Non-Compliant**:
- No docstring present
- Purpose unclear
- Parameters undocumented
- Return value undocumented

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Complete docstring added
def calculate_total(items: list[float], tax_rate: float) -> float:
    """Calculate total price including tax.

    Sums all item prices and applies the given tax rate.

    Args:
        items: List of item prices to sum
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

    Returns:
        Total price including tax
    """
    subtotal = sum(items)
    tax = subtotal * tax_rate
    return subtotal + tax

# Clear documentation
```

---

**Incomplete Docstring (Violation):**

```python
# ❌ VIOLATION: Incomplete docstring
def process_payment(amount: float, card: str, cvv: str) -> bool:
    """Process payment."""
    # Implementation...
    return True

# Problem:
# - Purpose too vague ("Process payment" - how?)
# - Parameters not documented
# - Return value not explained (what does True/False mean?)
# - No error conditions mentioned
```

**Why Non-Compliant**:
- Purpose too vague
- No parameter documentation
- Return value not explained
- Error cases not documented

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Complete documentation
def process_payment(amount: float, card: str, cvv: str) -> Result[bool, str]:
    """Process credit card payment transaction.

    Validates card details and processes payment through payment gateway.
    Returns Result type for error handling.

    Args:
        amount: Payment amount in dollars
        card: Credit card number (will be validated)
        cvv: Card CVV security code

    Returns:
        Ok(True) if payment successful
        Err(message) if payment failed or validation error

    Examples:
        >>> process_payment(50.00, "4111111111111111", "123")
        Ok(True)
        >>> process_payment(50.00, "invalid", "123")
        Err("Invalid card number")
    """
    # Implementation...
    pass

# Complete documentation
# Error cases explained
```

---

**Outdated Docstring (Violation):**

```python
# ❌ VIOLATION: Docstring doesn't match signature
def calculate_total(items: list[float], tax_rate: float, discount: float) -> float:
    """Calculate total price.

    Args:
        items: List of item prices
        tax_rate: Tax rate as decimal

    Returns:
        Total price
    """
    subtotal = sum(items)
    tax = subtotal * tax_rate
    discount_amount = subtotal * discount
    return subtotal + tax - discount_amount

# Problem:
# - Missing 'discount' parameter in docstring
# - Function signature changed but docstring didn't
# - Docstring outdated
```

**Why Non-Compliant**:
- Docstring missing new parameter (discount)
- Stale documentation
- Misleading

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Docstring updated
def calculate_total(items: list[float], tax_rate: float, discount: float) -> float:
    """Calculate total price including tax and discount.

    Sums item prices, applies tax, then subtracts discount.

    Args:
        items: List of item prices to sum
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)
        discount: Discount rate as decimal (e.g., 0.10 for 10%)

    Returns:
        Total price after tax and discount
    """
    subtotal = sum(items)
    tax = subtotal * tax_rate
    discount_amount = subtotal * discount
    return subtotal + tax - discount_amount

# Docstring matches signature
```

---

**Vague Purpose (Violation):**

```python
# ❌ VIOLATION: Vague, unhelpful docstring
def process_data(data):
    """Process the data."""
    # Implementation...
    pass

# Problem:
# - "Process the data" is too vague
# - What kind of processing?
# - What does it return?
# - No parameter documentation
# - Not helpful
```

**Why Non-Compliant**:
- Purpose too vague
- No specific information
- Not helpful to maintainers

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Specific, clear purpose
def process_data(data: list[dict]) -> list[dict]:
    """Validate and normalize user data records.

    Checks each record for required fields, converts data types,
    and removes invalid entries.

    Args:
        data: List of raw user data dictionaries

    Returns:
        List of validated and normalized user records

    Examples:
        >>> process_data([{'name': 'Alice', 'age': '30'}])
        [{'name': 'Alice', 'age': 30}]
    """
    # Implementation...
    pass

# Clear, specific purpose
```

---

## Docstring Format Standards

### Python (Google Style)

```python
def function_name(param1: type1, param2: type2) -> return_type:
    """Short one-line summary.

    Longer description providing more detail about what the
    function does and how it works.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this exception is raised

    Examples:
        >>> function_name(arg1, arg2)
        result
    """
    pass
```

### JavaScript (JSDoc)

```javascript
/**
 * Short one-line summary.
 *
 * Longer description providing more detail.
 *
 * @param {type1} param1 - Description of first parameter
 * @param {type2} param2 - Description of second parameter
 * @returns {returnType} Description of return value
 * @example
 * functionName(arg1, arg2);
 * // result
 */
function functionName(param1, param2) {
    // Implementation
}
```

### Required Sections

| Section | Required | Description |
|---------|----------|-------------|
| **Summary** | ✅ Yes | One-line description of purpose |
| **Description** | ⚠️ If complex | Detailed explanation |
| **Args/Params** | ✅ Yes | All parameters documented |
| **Returns** | ✅ Yes | Return value explained |
| **Raises** | ⚠️ If throws | Exceptions documented |
| **Examples** | ⚠️ If complex | Usage examples |

---

## Edge Cases

### Edge Case 1: Private Functions

**Issue**: Do private functions need docstrings?

**Handling**:
```python
# Private helper (still needs docstring)
def _validate_input(value: int) -> bool:
    """Validate that input is positive integer.

    Private helper function for input validation.

    Args:
        value: Integer to validate

    Returns:
        True if valid, False otherwise
    """
    return isinstance(value, int) and value > 0

# Even private functions need documentation
# Future maintainers benefit from clear docs
```

**Directive Action**: All functions need docstrings, including private ones.

---

### Edge Case 2: One-Line Functions

**Issue**: Very simple functions - still need full docstring?

**Handling**:
```python
# Simple one-liner
def add(x: int, y: int) -> int:
    """Add two integers.

    Args:
        x: First integer
        y: Second integer

    Returns:
        Sum of x and y
    """
    return x + y

# Even simple functions need proper documentation
# Consistency is important
```

**Directive Action**: All functions need complete docstrings regardless of simplicity.

---

### Edge Case 3: Lambda Functions

**Issue**: Lambdas don't support docstrings

**Handling**:
```python
# Lambdas can't have docstrings
# ❌ Not possible
add = lambda x, y: x + y  # No way to add docstring

# ✅ Convert to named function
def add(x: int, y: int) -> int:
    """Add two integers."""
    return x + y

# Named functions support docstrings
```

**Directive Action**: Convert lambdas to named functions if documentation needed.

---

## Related Directives

- **Depends On**: None
- **Triggers**:
  - `fp_metadata_annotation` - Complements metadata
  - `fp_function_indexing` - Indexed functions need docstrings
- **Called By**:
  - `project_file_write` - Enforce docstrings before writing
  - `project_compliance_check` - Check documentation coverage
- **Escalates To**: None

---

## Helper Functions Used

- `check_docstring_presence(func: Function) -> bool` - Function has docstring?
- `parse_docstring(docstring: str) -> DocstringInfo` - Extract sections
- `validate_docstring_completeness(func: Function, docstring: DocstringInfo) -> bool` - Check completeness
- `generate_docstring_template(func: Function) -> str` - Auto-generate docstring
- `update_functions_table(func_id: int, has_docstring: bool)` - Update database

---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `has_docstring = 1` for documented functions
- **`notes`**: Logs missing docstrings with `note_type = 'documentation'`

---

## Testing

How to verify this directive is working:

1. **Function without docstring** → Directive generates template
   ```python
   # Before: def add(x, y): return x + y
   # After: Has complete docstring
   ```

2. **Check documentation coverage**
   ```sql
   SELECT COUNT(*) as total,
          SUM(CASE WHEN has_docstring = 1 THEN 1 ELSE 0 END) as documented
   FROM functions;
   ```

3. **Find undocumented functions**
   ```sql
   SELECT name, file_id
   FROM functions
   WHERE has_docstring = 0;
   ```

---

## Common Mistakes

- ❌ **No docstring** - Function completely undocumented
- ❌ **Vague purpose** - "Process data" not helpful
- ❌ **Missing parameters** - Not all params documented
- ❌ **Outdated docstring** - Function changed but doc didn't
- ❌ **No examples** - Complex functions without usage examples

---

## Roadblocks and Resolutions

### Roadblock 1: docstring_missing
**Issue**: Function has no docstring
**Resolution**: Generate complete docstring template from function signature and insert

### Roadblock 2: docstring_incomplete
**Issue**: Docstring missing parameter or return documentation
**Resolution**: Analyze function signature and add missing sections

### Roadblock 3: docstring_outdated
**Issue**: Function signature changed but docstring not updated
**Resolution**: Re-generate docstring sections that don't match signature

### Roadblock 4: complex_function_unclear
**Issue**: Complex function purpose unclear from name
**Resolution**: Prompt user to provide purpose description and examples

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-docstring-enforcement)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#meta-reflection)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for docstring enforcement*
