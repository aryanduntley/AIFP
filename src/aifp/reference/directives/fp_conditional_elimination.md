# fp_conditional_elimination

## Purpose

The `fp_conditional_elimination` directive refactors imperative conditionals (if/else/switch statements) into declarative functional expressions using mapping structures, pattern matching, ternary operators, or expression-based control flow. It removes imperative control structures and promotes declarative, expression-based logic that is more composable, testable, and aligned with functional programming principles.

**Category**: Control Flow
**Type**: FP Core
**Priority**: Medium
**Confidence Threshold**: 0.6

---

## Workflow

### Trunk
**`analyze_branching_logic`**: Scan functions for imperative conditional statements that can be converted to expressions.

### Branches

1. **`imperative_if_else`** → **`convert_to_expression`**
   - **Condition**: Detects if/else used as statement rather than expression
   - **Action**: Convert to ternary, expression, or mapping structure
   - **Details**: Transform statement-based branching to value-returning expressions
   - **Output**: Expression-based conditional logic

2. **`switch_detected`** → **`replace_with_match`**
   - **Condition**: Detects switch/case statement
   - **Action**: Replace with pattern matching or dispatch table
   - **Details**: Convert switch to match expression or object mapping
   - **Output**: Declarative dispatch structure

3. **`nested_if_expression`** → **`flatten_to_match`**
   - **Condition**: Nested if/else that returns values
   - **Action**: Convert to pattern matching with guards
   - **Details**: Extract patterns, create match expression
   - **Output**: Flat pattern match structure

4. **`boolean_expression`** → **`simplify_to_operator`**
   - **Condition**: If/else returning boolean values
   - **Action**: Simplify to boolean expression
   - **Details**: Use logical operators instead of conditionals
   - **Output**: Simplified boolean expression

5. **`already_declarative`** → **`mark_as_declarative`**
   - **Condition**: Already using expression-based control flow
   - **Action**: Mark as compliant
   - **Output**: Compliance confirmation

6. **Fallback** → **`prompt_user`**
   - **Condition**: Conditional cannot be safely converted
   - **Action**: Request user guidance on conversion strategy

### Error Handling
- **On failure**: Prompt user with branching analysis details
- **Low confidence** (< 0.6): Request review before transformation

---

## Refactoring Strategies

### Strategy 1: If/Else to Ternary Expression
Convert simple if/else statements to ternary expressions.

**Before (Python - Imperative)**:
```python
def get_status(age):
    if age >= 18:
        status = "adult"
    else:
        status = "minor"
    return status
```

**After (Python - Declarative)**:
```python
def get_status(age: int) -> str:
    """Declarative: expression-based conditional."""
    return "adult" if age >= 18 else "minor"
```

### Strategy 2: Switch/Case to Dispatch Table
Replace switch statements with dispatch tables (object/dict mapping).

**Before (JavaScript - Imperative Switch)**:
```javascript
function getDiscount(customerType) {
  let discount;
  switch (customerType) {
    case 'premium':
      discount = 0.20;
      break;
    case 'regular':
      discount = 0.10;
      break;
    case 'guest':
      discount = 0.0;
      break;
    default:
      discount = 0.0;
  }
  return discount;
}
```

**After (JavaScript - Declarative Dispatch)**:
```javascript
const DISCOUNT_RATES = {
  premium: 0.20,
  regular: 0.10,
  guest: 0.0
};

function getDiscount(customerType) {
  return DISCOUNT_RATES[customerType] ?? 0.0;
}
```

### Strategy 3: Multiple Returns to Expression
Convert multiple return statements to single expression.

**Before (TypeScript - Multiple Returns)**:
```typescript
function classifyNumber(n: number): string {
  if (n < 0) {
    return 'negative';
  } else if (n === 0) {
    return 'zero';
  } else {
    return 'positive';
  }
}
```

**After (TypeScript - Single Expression)**:
```typescript
function classifyNumber(n: number): string {
  return n < 0 ? 'negative' : n === 0 ? 'zero' : 'positive';
}

// Or with pattern matching (TypeScript 5.0+)
function classifyNumber(n: number): string {
  return match(n)
    .when(x => x < 0, () => 'negative')
    .when(x => x === 0, () => 'zero')
    .otherwise(() => 'positive');
}
```

### Strategy 4: Nested If/Else to Functional Composition
Replace nested conditionals with function composition.

**Before (Python - Nested Imperative)**:
```python
def calculate_price(base_price, is_member, is_holiday):
    if is_member:
        if is_holiday:
            final_price = base_price * 0.70  # 30% off
        else:
            final_price = base_price * 0.90  # 10% off
    else:
        if is_holiday:
            final_price = base_price * 0.95  # 5% off
        else:
            final_price = base_price
    return final_price
```

**After (Python - Declarative Composition)**:
```python
def calculate_price(base_price: float, is_member: bool, is_holiday: bool) -> float:
    """Declarative price calculation using functional composition."""
    discount = (
        0.30 if is_member and is_holiday else
        0.10 if is_member else
        0.05 if is_holiday else
        0.0
    )
    return base_price * (1 - discount)
```

### Strategy 5: Boolean Logic Simplification
Replace if/else returning booleans with direct expressions.

**Before (Python - Unnecessary Conditional)**:
```python
def is_eligible(age, has_license):
    if age >= 18 and has_license:
        return True
    else:
        return False
```

**After (Python - Direct Boolean Expression)**:
```python
def is_eligible(age: int, has_license: bool) -> bool:
    """Direct boolean expression (no conditional needed)."""
    return age >= 18 and has_license
```

### Strategy 6: Dispatch Table with Functions
Map values to behavior (functions) instead of data.

**Before (Python - Imperative Operation Selection)**:
```python
def calculate(operation, a, b):
    if operation == 'add':
        result = a + b
    elif operation == 'subtract':
        result = a - b
    elif operation == 'multiply':
        result = a * b
    elif operation == 'divide':
        result = a / b if b != 0 else 0
    else:
        result = 0
    return result
```

**After (Python - Declarative Dispatch Table)**:
```python
from typing import Callable

def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a: float, b: float) -> float:
    return a * b

def divide(a: float, b: float) -> float:
    return a / b if b != 0 else 0.0

OPERATIONS: dict[str, Callable[[float, float], float]] = {
    'add': add,
    'subtract': subtract,
    'multiply': multiply,
    'divide': divide,
}

def calculate(operation: str, a: float, b: float) -> float:
    """Declarative: dispatch table maps operation to function."""
    op_func = OPERATIONS.get(operation, lambda x, y: 0.0)
    return op_func(a, b)
```

---

## Examples

### Example 1: HTTP Status Code Handling

**Before (Imperative)**:
```python
def get_status_message(code):
    if code == 200:
        return "OK"
    elif code == 404:
        return "Not Found"
    elif code == 500:
        return "Internal Server Error"
    else:
        return "Unknown Status"
```

**After (Declarative)**:
```python
HTTP_MESSAGES = {
    200: "OK",
    404: "Not Found",
    500: "Internal Server Error",
}

def get_status_message(code: int) -> str:
    """Declarative status message lookup."""
    return HTTP_MESSAGES.get(code, "Unknown Status")
```

### Example 2: Grade Calculation

**Before (TypeScript - Imperative)**:
```typescript
function getGrade(score: number): string {
  if (score >= 90) {
    return 'A';
  } else if (score >= 80) {
    return 'B';
  } else if (score >= 70) {
    return 'C';
  } else if (score >= 60) {
    return 'D';
  } else {
    return 'F';
  }
}
```

**After (TypeScript - Declarative)**:
```typescript
const GRADE_THRESHOLDS = [
  { min: 90, grade: 'A' },
  { min: 80, grade: 'B' },
  { min: 70, grade: 'C' },
  { min: 60, grade: 'D' },
  { min: 0, grade: 'F' },
];

function getGrade(score: number): string {
  return GRADE_THRESHOLDS.find(t => score >= t.min)?.grade ?? 'F';
}
```

### Example 3: State Machine

**Before (Imperative)**:
```python
def next_state(current_state, action):
    if current_state == 'idle':
        if action == 'start':
            return 'running'
        else:
            return 'idle'
    elif current_state == 'running':
        if action == 'pause':
            return 'paused'
        elif action == 'stop':
            return 'idle'
        else:
            return 'running'
    elif current_state == 'paused':
        if action == 'resume':
            return 'running'
        elif action == 'stop':
            return 'idle'
        else:
            return 'paused'
```

**After (Declarative State Machine)**:
```python
from typing import Literal

State = Literal['idle', 'running', 'paused']
Action = Literal['start', 'pause', 'resume', 'stop']

STATE_TRANSITIONS: dict[tuple[State, Action], State] = {
    ('idle', 'start'): 'running',
    ('running', 'pause'): 'paused',
    ('running', 'stop'): 'idle',
    ('paused', 'resume'): 'running',
    ('paused', 'stop'): 'idle',
}

def next_state(current_state: State, action: Action) -> State:
    """Declarative state machine using transition table."""
    return STATE_TRANSITIONS.get((current_state, action), current_state)
```

### Example 4: Validation Logic

**Before (Imperative)**:
```javascript
function validateUser(user) {
  if (!user.name) {
    return { valid: false, error: 'Name required' };
  }
  if (!user.email) {
    return { valid: false, error: 'Email required' };
  }
  if (user.age < 13) {
    return { valid: false, error: 'Must be 13 or older' };
  }
  return { valid: true };
}
```

**After (Declarative)**:
```javascript
const VALIDATIONS = [
  { check: u => u.name, error: 'Name required' },
  { check: u => u.email, error: 'Email required' },
  { check: u => u.age >= 13, error: 'Must be 13 or older' },
];

function validateUser(user) {
  const failure = VALIDATIONS.find(v => !v.check(user));
  return failure
    ? { valid: false, error: failure.error }
    : { valid: true };
}
```

---

## Edge Cases

### Edge Case 1: Side Effects in Conditionals
**Scenario**: Conditional branches contain side effects
**Issue**: Cannot convert to expression safely
**Handling**:
- Separate side effects from conditional logic
- Return effect data for external execution
- Document why imperative conditional necessary

**Example**:
```python
# ❌ Cannot convert: side effects
def process(x):
    if x > 0:
        log_positive(x)  # Side effect!
        return x * 2
    else:
        log_negative(x)  # Side effect!
        return 0

# ✅ Separate effects from logic
def calculate_result(x):
    """Pure: no side effects."""
    return x * 2 if x > 0 else 0

def log_calculation(x):
    """Effect boundary."""
    if x > 0:
        log_positive(x)
    else:
        log_negative(x)

def process(x):
    """Orchestrate pure logic and effects."""
    result = calculate_result(x)
    log_calculation(x)
    return result
```

### Edge Case 2: Complex Conditional Logic
**Scenario**: Multiple interdependent conditions
**Issue**: Expression becomes unreadable
**Handling**:
- Keep imperative conditional if clearer
- Extract to multiple small functions
- Use pattern matching for complex cases

### Edge Case 3: Performance-Critical Branching
**Scenario**: Hot path with tight performance requirements
**Issue**: Dispatch table lookup slower than direct conditional
**Handling**:
- Profile before optimizing
- Use direct conditionals if measurably faster
- Document performance trade-off

### Edge Case 4: Mutation in Branches
**Scenario**: Each branch mutates different variables
**Issue**: Cannot express as pure expression
**Handling**:
- Refactor to return new values instead of mutating
- Use immutable updates
- Convert to expression-based logic

**Example**:
```python
# ❌ Mutation prevents expression conversion
def update_stats(stats, event):
    if event == 'click':
        stats['clicks'] += 1
    elif event == 'view':
        stats['views'] += 1

# ✅ Immutable update as expression
def update_stats(stats: dict, event: str) -> dict:
    """Returns new stats dict (immutable)."""
    increments = {'click': {'clicks': 1}, 'view': {'views': 1}}
    increment = increments.get(event, {})

    return {
        'clicks': stats.get('clicks', 0) + increment.get('clicks', 0),
        'views': stats.get('views', 0) + increment.get('views', 0),
    }
```

### Edge Case 5: Early Exit Optimization
**Scenario**: Conditional provides early exit optimization
**Issue**: Converting to expression evaluates all branches
**Handling**:
- Keep imperative conditional for early exit
- Use short-circuit evaluation where possible
- Document optimization rationale

---

## Database Operations

### Record Conditional Elimination

```sql
-- Update function with declarative control flow
UPDATE functions
SET
    control_flow_style = 'declarative',
    uses_expressions = 1,
    complexity_score = 1,  -- Reduced
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'get_status' AND file_id = ?;
```

### Query Functions with Imperative Conditionals

```sql
-- Find functions using imperative control flow
SELECT f.id, f.name, f.file_id, f.control_flow_style
FROM functions f
WHERE f.control_flow_style IN ('if_else', 'switch_case')
  AND f.complexity_score < 5  -- Simple enough to convert
ORDER BY f.complexity_score;
```

---

## Related Directives

### FP Directives
- **fp_pattern_matching**: Alternative expression-based control flow
- **fp_guard_clauses**: Complementary for validation logic
- **fp_purity**: Eliminates side effects that prevent expression conversion

### Project Directives
- **project_compliance_check**: Validates declarative control flow usage
- **project_update_db**: Records conditional elimination transformations

---

## Helper Functions

### `is_expression_convertible(conditional) -> bool`
Determines if conditional can be safely converted to expression.

**Signature**:
```python
def is_expression_convertible(conditional: ASTNode) -> bool:
    """
    Checks if conditional has:
    - No side effects in branches
    - Consistent return types
    - No complex control flow (loops, nested returns)
    Returns True if safe to convert.
    """
```

### `extract_dispatch_table(switch_statement) -> dict`
Extracts dispatch table from switch/case statement.

**Signature**:
```python
def extract_dispatch_table(
    switch_statement: ASTNode
) -> dict[Any, Any]:
    """
    Parses switch cases to create dispatch mapping.
    Returns dict mapping case values to results.
    """
```

### `simplify_to_expression(if_else) -> str`
Converts if/else to equivalent expression.

**Signature**:
```python
def simplify_to_expression(if_else: ASTNode) -> str:
    """
    Transforms if/else to ternary or expression form.
    Returns expression code string.
    """
```

---

## Testing

### Test 1: If/Else to Ternary
```python
def test_convert_to_ternary():
    source = """
def get_status(age):
    if age >= 18:
        return "adult"
    else:
        return "minor"
"""

    result = fp_conditional_elimination.refactor(source)

    assert 'if age >= 18' not in result
    assert '"adult" if age >= 18 else "minor"' in result
```

### Test 2: Switch to Dispatch Table
```python
def test_switch_to_dispatch():
    source = """
def get_discount(type):
    if type == 'premium':
        return 0.20
    elif type == 'regular':
        return 0.10
    else:
        return 0.0
"""

    result = fp_conditional_elimination.refactor(source)

    assert 'DISCOUNT' in result or 'discount' in result.lower()
    assert '.get(' in result
```

### Test 3: Boolean Expression Simplification
```python
def test_simplify_boolean():
    source = """
def is_valid(x, y):
    if x > 0 and y > 0:
        return True
    else:
        return False
"""

    result = fp_conditional_elimination.refactor(source)

    assert 'return x > 0 and y > 0' in result
    assert 'if ' not in result
```

---

## Common Mistakes

### Mistake 1: Converting Conditionals with Side Effects
**Problem**: Expression evaluates all branches (side effects execute)

**Solution**: Keep imperative form or separate side effects

```python
# ❌ Bad: side effects in ternary (both execute!)
result = log_success(x) if x > 0 else log_failure(x)  # Both may execute!

# ✅ Good: imperative form for side effects
if x > 0:
    log_success(x)
else:
    log_failure(x)
```

### Mistake 2: Unreadable Nested Ternaries
**Problem**: Chained ternaries become cryptic

**Solution**: Use dispatch table or keep if/else

```python
# ❌ Bad: nested ternary (hard to read)
result = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'F'

# ✅ Good: dispatch table or if/elif
GRADES = [(90, 'A'), (80, 'B'), (70, 'C'), (0, 'F')]
result = next(grade for threshold, grade in GRADES if score >= threshold)
```

### Mistake 3: Type Mismatches in Expressions
**Problem**: Branches return incompatible types

**Solution**: Ensure consistent return types or use union types

```python
# ❌ Bad: type mismatch
result = 42 if condition else "error"  # int | str

# ✅ Good: consistent types
result = 42 if condition else 0
error = None if condition else "error"
```

---

## Roadblocks

### Roadblock 1: Imperative Branching
**Issue**: Conditional uses statements, not expressions
**Resolution**: Refactor to expression-based control or dispatch table

### Roadblock 2: Side Effects in Branches
**Issue**: Branches contain side effects preventing expression conversion
**Resolution**: Separate pure logic from effects

### Roadblock 3: Complex Nested Logic
**Issue**: Deeply nested conditionals too complex for expression
**Resolution**: Use pattern matching, guard clauses, or keep imperative form

---

## Integration Points

### With `fp_pattern_matching`
Pattern matching is the preferred declarative alternative for complex conditionals.

### With `fp_guard_clauses`
Guard clauses handle validation, conditional elimination handles value selection.

### With `fp_purity`
Pure functions enable safe conditional-to-expression conversion.

---

## Intent Keywords

- `if elimination`
- `declarative control`
- `expression`
- `ternary`
- `dispatch table`

---

## Confidence Threshold

**0.6** - Moderate confidence as conversion is generally safe for pure conditionals.

---

## Notes

- Expressions are more composable than statements
- Dispatch tables enable data-driven control flow
- Ternary operators ideal for simple if/else
- Pattern matching best for complex conditionals
- Side effects prevent expression conversion
- Keep imperative form if expression unreadable
- Declarative control flow is easier to test
- Expression-based logic is more functional
- Dispatch tables separate data from behavior
- Boolean expressions should be direct (no if/else for true/false)
