# fp_naming_conventions

## Purpose

The `fp_naming_conventions` directive establishes consistent naming standards for functional programming code to enhance readability, maintainability, and AI comprehension. It enforces naming patterns that make function purity, side effects, and data flow explicit through function and variable names. This enables developers and AI assistants to quickly understand code intent and behavior by reading function signatures alone.

**Category**: Code Quality
**Type**: FP Auxiliary
**Priority**: High
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`analyze_naming_patterns`**: Scan codebase for naming consistency and FP alignment.

### Branches

1. **`pure_function_naming`** → **`validate_verb_noun_pattern`**
   - **Condition**: Function is pure (no side effects)
   - **Action**: Ensure name uses verb-noun pattern without imperative language
   - **Details**: Pure functions should use descriptive verbs: `calculate`, `transform`, `filter`, `map`, `reduce`, `find`, `validate`
   - **Output**: Pure function naming validation

2. **`impure_function_naming`** → **`enforce_effect_suffix`**
   - **Condition**: Function has side effects (I/O, mutations, external state)
   - **Action**: Add suffix or prefix indicating effects: `IO`, `Eff`, `Unsafe`
   - **Details**: Make side effects explicit in name: `readFileIO`, `writeToDBEff`, `unsafeMutate`
   - **Output**: Effect-indicating name

3. **`data_structure_naming`** → **`use_descriptive_nouns`**
   - **Condition**: Defining data types, records, or ADTs
   - **Action**: Use clear, descriptive nouns in PascalCase
   - **Details**: `UserProfile`, `OrderResult`, `PaymentStatus`
   - **Output**: Validated data type name

4. **`variable_naming`** → **`ensure_immutability_clarity`**
   - **Condition**: Variable or constant declaration
   - **Action**: Use descriptive names, avoid abbreviations, prefer `const` naming style
   - **Details**: `processedUsers` not `pUsers`, `totalAmount` not `amt`
   - **Output**: Clear variable name

5. **Fallback** → **`suggest_rename`**
   - **Condition**: Name unclear or violates FP conventions
   - **Action**: Suggest better name following FP patterns

### Error Handling
- **On failure**: Log naming violation and suggest alternative
- **Low confidence** (< 0.7): Flag for manual review

---

## Refactoring Strategies

### Strategy 1: Pure Function Naming - Verb-Noun Pattern

Pure functions should use clear verb-noun combinations that describe the transformation.

**Before (Poor Naming)**:
```python
# Unclear, looks like a procedure
def do_thing(data):
    return [x * 2 for x in data]

# Too abbreviated
def proc(x):
    return x + 10

# Misleading (sounds impure)
def update_user(user):
    # Actually pure! Returns new user
    return {**user, 'validated': True}
```

**After (FP Naming)**:
```python
# Clear transformation verb + noun
def double_values(numbers: list[int]) -> list[int]:
    """Pure: transforms numbers by doubling each."""
    return [x * 2 for x in numbers]

# Descriptive transformation
def increment_by_ten(value: int) -> int:
    """Pure: adds 10 to value."""
    return value + 10

# Clarifies pure behavior
def validate_user(user: dict) -> dict:
    """Pure: returns validated user (new dict)."""
    return {**user, 'validated': True}
```

**Good Pure Function Verbs**:
- `calculate`, `compute` - Numeric operations
- `transform`, `convert` - Data transformations
- `filter`, `find`, `select` - Collection operations
- `map`, `reduce`, `fold` - Collection transformations
- `validate`, `check`, `verify` - Validation
- `parse`, `format`, `encode`, `decode` - Data conversion
- `build`, `create`, `construct` - Object construction

---

### Strategy 2: Effect-Bearing Function Naming

Functions with side effects must indicate this in their names.

**Before (Hidden Effects)**:
```typescript
// Looks pure but has I/O side effect
function getUser(userId: number): User {
  const response = fetch(`/api/users/${userId}`);  // I/O!
  return response.json();
}

// Mutation hidden in name
function processOrder(order: Order): Order {
  order.status = 'processed';  // Mutation!
  database.save(order);  // I/O!
  return order;
}
```

**After (Explicit Effects)**:
```typescript
// Suffix indicates I/O effect
async function getUserIO(userId: number): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}

// Alternative: Eff suffix
async function fetchUserEff(userId: number): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}

// Prefix shows unsafe operation
function unsafeProcessOrder(order: Order): Order {
  order.status = 'processed';
  database.save(order);
  return order;
}

// Or split into pure + effect
function markOrderProcessed(order: Order): Order {
  // Pure: returns new order
  return {...order, status: 'processed'};
}

async function saveOrderIO(order: Order): Promise<void> {
  // Effect: I/O only
  await database.save(order);
}
```

**Effect Naming Conventions**:
- **`IO` suffix**: I/O operations (files, network, database)
- **`Eff` suffix**: General side effects
- **`Unsafe` prefix**: Mutations, unsafe operations
- **`Mut` suffix**: Explicit mutations

---

### Strategy 3: Data Type Naming - Descriptive Nouns

ADTs, records, and types use PascalCase descriptive nouns.

**Before (Poor Type Names)**:
```python
from dataclasses import dataclass

# Too generic
@dataclass
class Data:
    value: int

# Abbreviations unclear
@dataclass
class UsrPrf:
    nm: str
    em: str

# Type suffix redundant
@dataclass
class UserType:
    name: str
```

**After (FP Type Naming)**:
```python
from dataclasses import dataclass
from typing import Literal

# Clear, descriptive noun
@dataclass(frozen=True)
class UserProfile:
    """Immutable user profile data."""
    name: str
    email: str
    age: int

# Domain-specific name
@dataclass(frozen=True)
class PaymentResult:
    """Result of payment processing."""
    success: bool
    transaction_id: str | None
    error_message: str | None

# Enum/Literal with clear states
OrderStatus = Literal["pending", "processing", "completed", "failed"]

@dataclass(frozen=True)
class Order:
    """Immutable order representation."""
    id: int
    status: OrderStatus
    items: tuple[str, ...]
```

**Type Naming Rules**:
- PascalCase for types: `UserAccount`, `OrderItem`
- Avoid `Type` suffix: `User` not `UserType`
- Use domain language: `Invoice`, `Receipt`, `Transaction`
- Descriptive nouns, not verbs

---

### Strategy 4: Variable Naming - Clarity and Immutability

Variables should be descriptive, avoid abbreviations, and suggest immutability.

**Before (Poor Variable Names)**:
```javascript
// Abbreviations unclear
const usr = getUser();
const amt = calculateTotal(items);
const tmp = processData(input);

// Generic names
const data = fetchOrders();
const result = transform(values);
const x = compute(y);

// Misleading (sounds mutable)
let total = 0;
for (const item of items) {
  total += item.price;  // Mutation!
}
```

**After (FP Variable Naming)**:
```javascript
// Descriptive, full words
const currentUser = getUser();
const totalAmount = calculateTotal(items);
const processedData = processData(input);

// Specific, domain-relevant
const customerOrders = fetchOrders();
const transformedValues = transform(values);
const computedScore = compute(input);

// Immutable, functional style
const totalAmount = items.reduce(
  (sum, item) => sum + item.price,
  0
);

// Or use clear intermediate names
const itemPrices = items.map(item => item.price);
const totalAmount = itemPrices.reduce((sum, price) => sum + price, 0);
```

**Variable Naming Rules**:
- Full words, not abbreviations: `user` not `usr`
- camelCase for variables: `totalAmount`, `processedUsers`
- Descriptive: `filteredActiveUsers` not `filtered`
- Avoid generic: `userData` not `data`
- Prefer `const`: Suggests immutability

---

### Strategy 5: Boolean Naming - Predicates and Flags

Booleans should use predicate names (questions) that clearly indicate true/false meaning.

**Before (Ambiguous Booleans)**:
```python
# Unclear meaning
active = check_status(user)
valid = process(data)
flag = compute(value)

# Ambiguous
def filter_users(users, admin):  # admin what? is admin? has admin?
    pass
```

**After (Clear Predicates)**:
```python
# Clear question form
is_active = check_user_status(user)
is_valid = validate_data(data)
has_permission = check_permission(user, resource)

# Function parameters
def filter_users(users: list[User], is_admin_required: bool) -> list[User]:
    """Filter users based on admin status requirement."""
    if is_admin_required:
        return [u for u in users if u.is_admin]
    return users

# Predicate function naming
def is_even(number: int) -> bool:
    """Returns True if number is even."""
    return number % 2 == 0

def has_valid_email(user: User) -> bool:
    """Returns True if user has valid email."""
    return '@' in user.email and '.' in user.email
```

**Boolean Naming Patterns**:
- `is_*`: State checks (`is_active`, `is_valid`)
- `has_*`: Possession checks (`has_permission`, `has_data`)
- `can_*`: Capability checks (`can_access`, `can_edit`)
- `should_*`: Conditional logic (`should_retry`, `should_cache`)

---

## Examples

### Example 1: API Function Naming

**Before (Inconsistent)**:
```typescript
// Inconsistent naming patterns
function get(id: number) { /* fetch from API */ }
function save(data: User) { /* save to API */ }
function del(id: number) { /* delete from API */ }
function proc(input: any) { /* process something */ }
```

**After (Consistent FP Naming)**:
```typescript
// Pure functions: descriptive verbs
function buildUserRequest(id: number): Request {
  return {url: `/users/${id}`, method: 'GET'};
}

function validateUserData(data: User): Result<User, string> {
  if (!data.email) return Err('Email required');
  return Ok(data);
}

// Effect functions: IO suffix
async function fetchUserIO(id: number): Promise<User> {
  const response = await fetch(`/users/${id}`);
  return response.json();
}

async function saveUserIO(user: User): Promise<void> {
  await fetch(`/users/${user.id}`, {
    method: 'PUT',
    body: JSON.stringify(user)
  });
}

async function deleteUserIO(id: number): Promise<void> {
  await fetch(`/users/${id}`, {method: 'DELETE'});
}
```

### Example 2: Data Transformation Pipeline

**Before (Generic Names)**:
```python
def step1(data):
    return [x for x in data if x > 0]

def step2(data):
    return [x * 2 for x in data]

def step3(data):
    return sum(data)

result = step3(step2(step1(input_data)))
```

**After (Descriptive FP Names)**:
```python
def filter_positive_numbers(numbers: list[int]) -> list[int]:
    """Pure: filters positive numbers from list."""
    return [n for n in numbers if n > 0]

def double_values(numbers: list[int]) -> list[int]:
    """Pure: doubles each number in list."""
    return [n * 2 for n in numbers]

def sum_numbers(numbers: list[int]) -> int:
    """Pure: calculates sum of numbers."""
    return sum(numbers)

# Clear pipeline with descriptive names
positive_numbers = filter_positive_numbers(input_data)
doubled_numbers = double_values(positive_numbers)
total_sum = sum_numbers(doubled_numbers)
```

---

## Edge Cases

### Edge Case 1: Generic Utility Functions
**Scenario**: Utility functions like `map`, `filter`, `reduce`
**Issue**: Generic names acceptable for reusable utilities
**Handling**:
- Generic names OK for higher-order functions
- Specialized versions should be descriptive
- Document generic utilities clearly

**Example**:
```python
# Generic utility: acceptable
def map_over(func, items):
    return [func(item) for item in items]

# Specialized version: descriptive
def map_users_to_emails(users):
    return [user.email for user in users]
```

### Edge Case 2: Callback Function Naming
**Scenario**: Anonymous functions, callbacks, event handlers
**Issue**: Short names acceptable in limited scope
**Handling**:
- Single-letter names OK in very short lambdas: `x => x * 2`
- Named callbacks should be descriptive
- Event handlers should indicate event: `on_click`, `handle_submit`

### Edge Case 3: Type Parameter Naming
**Scenario**: Generic type parameters in typed languages
**Issue**: Single-letter conventions (`T`, `U`, `K`, `V`)
**Handling**:
- Follow language conventions: `T` for type, `K`/`V` for key/value
- Use descriptive names for domain generics: `TUser`, `TRequest`
- Document type constraints

### Edge Case 4: Legacy Code Interop
**Scenario**: Interfacing with legacy code using different naming
**Issue**: Mixing naming conventions at boundaries
**Handling**:
- Adapter layer uses FP naming
- Document legacy interface
- Convert at boundary

### Edge Case 5: Mathematical Functions
**Scenario**: Math operations with standard names
**Issue**: Standard abbreviations (`sin`, `cos`, `sqrt`)
**Handling**:
- Use standard math names
- Document behavior clearly
- Avoid creating new abbreviations

---

## Database Operations

### Record Naming Compliance

```sql
-- Update function metadata with naming analysis
UPDATE functions
SET
    name_compliant = 1,
    naming_metadata = json_set(
        COALESCE(naming_metadata, '{}'),
        '$.pattern', 'verb_noun',
        '$.purity_indicator', 'pure',
        '$.effect_suffix', NULL
    ),
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'calculate_total' AND file_id = ?;
```

---

## Related Directives

### FP Directives
- **fp_purity**: Pure functions should have pure-indicating names
- **fp_side_effect_detection**: Effect names must match actual side effects
- **fp_documentation**: Names should align with docstring descriptions

### Project Directives
- **project_compliance_check**: Validates naming consistency
- **project_update_db**: Records naming metadata

---

## Helper Functions

### `analyze_function_name(function_name, is_pure) -> dict`
Analyzes function name for FP compliance.

**Signature**:
```python
def analyze_function_name(
    function_name: str,
    is_pure: bool
) -> dict:
    """
    Analyzes function name compliance with FP conventions.
    Returns analysis with compliance score and suggestions.
    """
```

### `suggest_better_name(current_name, function_metadata) -> list[str]`
Suggests improved names based on function behavior.

**Signature**:
```python
def suggest_better_name(
    current_name: str,
    function_metadata: dict
) -> list[str]:
    """
    Generates naming suggestions based on function analysis.
    Returns ranked list of better names.
    """
```

---

## Testing

### Test 1: Pure Function Naming
```python
def test_pure_function_naming():
    source = """
def transform_users(users):
    return [format_user(u) for u in users]
"""

    analysis = fp_naming_conventions.analyze(source)

    assert analysis.compliant == True
    assert 'verb_noun' in analysis.pattern
```

### Test 2: Effect Function Naming
```python
def test_effect_function_naming():
    source_bad = """
def get_user(user_id):
    return database.fetch(user_id)  # I/O but no indicator!
"""

    analysis = fp_naming_conventions.analyze(source_bad)

    assert analysis.compliant == False
    assert 'missing_effect_indicator' in analysis.violations
    assert 'getUserIO' in analysis.suggestions
```

### Test 3: Variable Naming
```python
def test_variable_naming():
    source = """
const processedUsers = users.filter(u => u.active);
"""

    analysis = fp_naming_conventions.analyze(source)

    assert analysis.compliant == True
    assert 'descriptive' in analysis.qualities
```

---

## Common Mistakes

### Mistake 1: Generic Names
**Problem**: Using `data`, `result`, `value` everywhere

**Solution**: Use specific, domain-relevant names

```python
# ❌ Bad: generic
data = fetch_data()
result = process(data)

# ✅ Good: specific
customer_orders = fetch_customer_orders()
validated_orders = validate_orders(customer_orders)
```

### Mistake 2: Abbreviations
**Problem**: Over-abbreviating: `usr`, `ord`, `proc`

**Solution**: Use full words for clarity

```python
# ❌ Bad: abbreviated
usr = get_usr(id)
ord = proc_ord(usr)

# ✅ Good: full words
user = get_user(user_id)
order = process_order(user)
```

### Mistake 3: Hidden Side Effects
**Problem**: Pure-sounding names for impure functions

**Solution**: Add effect indicators

```python
# ❌ Bad: hidden I/O
def get_user(user_id):
    return database.fetch(user_id)

# ✅ Good: explicit effect
async def fetchUserIO(user_id):
    return await database.fetch(user_id)
```

---

## Roadblocks

### Roadblock 1: Inconsistent Naming
**Issue**: Mixed naming conventions across codebase
**Resolution**: Gradual refactoring, start with new code, document standards

### Roadblock 2: Legacy Conventions
**Issue**: Existing code uses different conventions
**Resolution**: Adapter layer, isolate legacy naming to boundaries

### Roadblock 3: Team Disagreement
**Issue**: Team prefers different naming style
**Resolution**: Document rationale, start with consensus subset

---

## Integration Points

### With `fp_purity`
Pure function names should reflect pure behavior.

### With `fp_documentation`
Function names should match documentation descriptions.

### With `project_compliance_check`
Naming conventions validated during compliance checks.

---

## Intent Keywords

- `naming`
- `conventions`
- `readability`
- `function names`
- `variable names`

---

## Confidence Threshold

**0.7** - High confidence required for naming compliance validation.

---

## Notes

- Clear naming reduces cognitive load
- Names should indicate purity and side effects
- Avoid abbreviations unless universally understood
- Use verb-noun for functions, nouns for types
- Boolean predicates use question form
- Effect-bearing functions need indicators (IO, Eff, Unsafe)
- Consistency across codebase improves maintainability
- Domain-specific names better than generic
- Full words preferred over abbreviations
- AIFP makes code intent clear through naming

