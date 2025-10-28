# Directive: fp_data_filtering

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: HIGH - Core data selection pattern

---

## Purpose

The `fp_data_filtering` directive replaces imperative data filtering with declarative filter expressions using pure predicates. This directive ensures all filtering logic is expressed as **composable pure functions** that clearly document selection criteria and can be combined, reused, and tested independently.

Data filtering provides **declarative selection**, enabling:
- **Clear Intent**: Predicate functions document what to select
- **Composability**: Predicates combine with and/or logic
- **Reusability**: Named predicates reused across codebase
- **Testability**: Predicates are pure functions (easy to test)
- **No Side Effects**: Filtering doesn't modify original data

This directive is fundamental to functional data processing and appears in virtually all data manipulation code.

---

## When to Apply

This directive applies when:
- **Selecting elements from collections** - Filter based on criteria
- **Conditional data processing** - Process only elements matching predicate
- **Data validation** - Filter out invalid elements
- **Search operations** - Find elements matching criteria
- **Imperative filtering detected** - if statements inside loops
- **Called by project directives**:
  - `project_file_write` - Validate filtering patterns
  - Works with `fp_list_operations` - Filter is core list operation
  - Works with `fp_lazy_evaluation` - Lazy filtering for large datasets

---

## Workflow

### Trunk: scan_filter_logic

Scans code to detect filtering patterns that should use declarative predicates.

**Steps**:
1. **Parse loops and conditionals** - Identify filtering logic
2. **Detect selection patterns** - if statements that select elements
3. **Extract predicate logic** - Conditions used for selection
4. **Verify predicate purity** - Ensure predicate functions are pure
5. **Check for built-in predicates** - all(), any(), etc.
6. **Generate filter equivalent** - Convert to filter() or comprehension

### Branches

**Branch 1: If simple_predicate_filter**
- **Then**: `convert_to_filter_comprehension`
- **Details**: Simple filtering with single predicate
  - Pattern: `for x in items: if pred(x): result.append(x)`
  - Convert to: `result = [x for x in items if pred(x)]`
  - Or: `result = list(filter(pred, items))`
- **Result**: Returns filter-based code

**Branch 2: If complex_predicate**
- **Then**: `extract_named_predicate`
- **Details**: Complex predicate logic
  - Extract to named function
  - Document predicate purpose
  - Reusable across codebase
- **Result**: Returns named predicate + filter

**Branch 3: If combined_predicates**
- **Then**: `compose_predicates`
- **Details**: Multiple predicates combined
  - AND logic: `all_of(pred1, pred2, pred3)`
  - OR logic: `any_of(pred1, pred2, pred3)`
  - NOT logic: `negate(pred)`
  - Compose predicates functionally
- **Result**: Returns composed predicate filter

**Branch 4: If builtin_any_all**
- **Then**: `use_builtin_predicate`
- **Details**: Use built-in any/all
  - `any(pred(x) for x in items)`
  - `all(pred(x) for x in items)`
  - More readable than manual loops
- **Result**: Returns built-in any/all

**Branch 5: If already_declarative**
- **Then**: `mark_compliant`
- **Details**: Already using filter/comprehension
  - Declarative filtering
  - Pure predicates
  - Mark as compliant
- **Result**: Code passes check

**Fallback**: `prompt_user`
- **Details**: Complex filtering pattern
  - Stateful filtering
  - Side effects in predicate
  - Ask user for filtering strategy
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Simple Filter (Passes):**
```python
def get_positive_numbers(numbers: list[int]) -> list[int]:
    """
    Get positive numbers using filter.

    Declarative filtering with pure predicate.
    """
    return [x for x in numbers if x > 0]

# Or with filter function
def get_positive_numbers_v2(numbers: list[int]) -> list[int]:
    """Get positive numbers using filter."""
    return list(filter(lambda x: x > 0, numbers))

# Usage
result = get_positive_numbers([-2, -1, 0, 1, 2, 3])
# Returns: [1, 2, 3]
```

**Why Compliant**:
- Declarative filtering
- Pure predicate (x > 0)
- Clear intent
- Functional style

---

**Named Predicate (Passes):**
```python
def is_adult(person: dict) -> bool:
    """
    Check if person is adult (pure predicate).

    Age >= 18.
    """
    return person['age'] >= 18

def get_adults(people: list[dict]) -> list[dict]:
    """
    Get adult people using named predicate.

    Declarative filtering with reusable predicate.
    """
    return [p for p in people if is_adult(p)]

# Or with filter
def get_adults_v2(people: list[dict]) -> list[dict]:
    """Get adults using filter."""
    return list(filter(is_adult, people))

# Predicate is reusable, testable, clear
# Usage
adults = get_adults([
    {'name': 'Alice', 'age': 25},
    {'name': 'Bob', 'age': 17},
    {'name': 'Charlie', 'age': 30}
])
# Returns: [{'name': 'Alice', 'age': 25}, {'name': 'Charlie', 'age': 30}]
```

**Why Compliant**:
- Named predicate (clear purpose)
- Pure function
- Reusable across codebase
- Testable independently

---

**Composed Predicates (Passes):**
```python
# Predicate composition utilities
def and_predicate(*predicates):
    """Combine predicates with AND logic."""
    def combined(x):
        return all(pred(x) for pred in predicates)
    return combined

def or_predicate(*predicates):
    """Combine predicates with OR logic."""
    def combined(x):
        return any(pred(x) for pred in predicates)
    return combined

def not_predicate(predicate):
    """Negate predicate."""
    def negated(x):
        return not predicate(x)
    return negated

# Individual predicates
def is_adult(person: dict) -> bool:
    """Age >= 18."""
    return person['age'] >= 18

def has_email(person: dict) -> bool:
    """Has email address."""
    return bool(person.get('email'))

def is_verified(person: dict) -> bool:
    """Account is verified."""
    return person.get('verified', False)

# Composed predicate
eligible_for_newsletter = and_predicate(
    is_adult,
    has_email,
    is_verified
)

def get_newsletter_recipients(people: list[dict]) -> list[dict]:
    """
    Get people eligible for newsletter.

    Uses composed predicate: adult AND has_email AND verified.
    """
    return list(filter(eligible_for_newsletter, people))

# Composable, reusable, clear
```

**Why Compliant**:
- Predicate composition
- Pure predicates
- Clear logic (AND/OR/NOT)
- Highly reusable

---

**Built-in any/all (Passes):**
```python
def has_positive_number(numbers: list[int]) -> bool:
    """
    Check if list contains any positive number.

    Uses built-in any with generator expression.
    """
    return any(x > 0 for x in numbers)

def all_positive_numbers(numbers: list[int]) -> bool:
    """
    Check if all numbers are positive.

    Uses built-in all with generator expression.
    """
    return all(x > 0 for x in numbers)

# Usage
has_pos = has_positive_number([-1, -2, 3, -4])
# Returns: True

all_pos = all_positive_numbers([1, 2, 3, 4])
# Returns: True
```

**Why Compliant**:
- Uses built-in any/all
- Generator expression (lazy)
- Clear and concise
- Functional style

---

### ❌ Non-Compliant Code

**Imperative Filter Loop (Violation):**
```python
# ❌ VIOLATION: Imperative filtering
def get_positive_numbers(numbers: list[int]) -> list[int]:
    """Get positive numbers using imperative loop."""
    result = []  # ← Mutable accumulator
    for num in numbers:  # ← Imperative loop
        if num > 0:  # ← Predicate logic embedded
            result.append(num)  # ← Mutation
    return result

# Problem:
# - Imperative loop structure
# - Mutable accumulator
# - Predicate logic not extracted
# - Not composable
# - Not reusable
```

**Why Non-Compliant**:
- Imperative filtering
- Mutable accumulator
- Should use filter/comprehension

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Declarative filter
def get_positive_numbers(numbers: list[int]) -> list[int]:
    """Get positive numbers using filter."""
    return [x for x in numbers if x > 0]

# Clear, functional, composable
```

---

**Complex Inline Predicate (Violation):**
```python
# ❌ VIOLATION: Complex predicate inline (unclear, not reusable)
def get_eligible_users(users: list[dict]) -> list[dict]:
    """Get eligible users using inline complex predicate."""
    return [
        u for u in users
        if u.get('age', 0) >= 18 and  # ← Complex logic inline
           u.get('email') and
           '@' in u['email'] and
           u.get('verified', False) and
           u.get('country') == 'US' and
           u.get('active', True)
    ]

# Problem:
# - Complex predicate logic inline
# - Hard to read
# - Not reusable
# - Not testable independently
# - Unclear intent
```

**Why Non-Compliant**:
- Complex predicate not extracted
- Unclear intent
- Not reusable or testable

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Named predicate
def is_eligible_user(user: dict) -> bool:
    """
    Check if user is eligible.

    Criteria:
    - Age >= 18
    - Has valid email
    - Account verified
    - US-based
    - Active account
    """
    return (
        user.get('age', 0) >= 18 and
        user.get('email') and
        '@' in user['email'] and
        user.get('verified', False) and
        user.get('country') == 'US' and
        user.get('active', True)
    )

def get_eligible_users(users: list[dict]) -> list[dict]:
    """Get eligible users using named predicate."""
    return list(filter(is_eligible_user, users))

# Clear, reusable, testable
```

---

**Stateful Filter (Violation):**
```python
# ❌ VIOLATION: Stateful filtering (impure predicate)
seen_ids = set()  # ← Global state

def get_unique_users(users: list[dict]) -> list[dict]:
    """Get unique users (IMPURE - uses global state)."""
    result = []
    for user in users:
        if user['id'] not in seen_ids:  # ← Reads global state
            seen_ids.add(user['id'])  # ← Modifies global state
            result.append(user)
    return result

# Problem:
# - Impure predicate (side effects)
# - Global state dependency
# - Not thread-safe
# - Breaks on repeated calls
```

**Why Non-Compliant**:
- Impure predicate (side effects)
- Global state mutation
- Not functional

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Pure filtering
def get_unique_users(users: list[dict]) -> list[dict]:
    """
    Get unique users by ID using pure filtering.

    Returns first occurrence of each user ID.
    """
    seen_ids = set()
    result = []

    for user in users:
        if user['id'] not in seen_ids:
            seen_ids.add(user['id'])  # Local state (OK within function)
            result.append(user)

    return result

# Or fully functional with dict
def get_unique_users_v2(users: list[dict]) -> list[dict]:
    """Get unique users using dict (preserves first occurrence)."""
    unique_dict = {user['id']: user for user in users}
    return list(unique_dict.values())

# Pure, no global state
```

---

**Manual any/all Loop (Violation):**
```python
# ❌ VIOLATION: Manual loop for any/all logic
def has_adult(people: list[dict]) -> bool:
    """Check if any person is adult using manual loop."""
    for person in people:  # ← Manual loop
        if person['age'] >= 18:  # ← Predicate logic
            return True  # ← Early return
    return False

# Problem:
# - Manual loop for any logic
# - Should use built-in any()
# - Less clear than declarative
```

**Why Non-Compliant**:
- Manual loop for any logic
- Should use built-in

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Built-in any
def has_adult(people: list[dict]) -> bool:
    """Check if any person is adult."""
    return any(person['age'] >= 18 for person in people)

# Or with named predicate
def is_adult(person: dict) -> bool:
    """Check if person is adult."""
    return person['age'] >= 18

def has_adult_v2(people: list[dict]) -> bool:
    """Check if any person is adult."""
    return any(map(is_adult, people))

# Clear, declarative, functional
```

---

## Edge Cases

### Edge Case 1: Filtering with Index

**Issue**: Need both element and index for filtering

**Handling**:
```python
# Filter with index using enumerate
def get_elements_at_even_indices(items: list) -> list:
    """
    Get elements at even indices.

    Uses enumerate to access both index and value.
    """
    return [value for i, value in enumerate(items) if i % 2 == 0]

# Or with filter
def get_elements_at_even_indices_v2(items: list) -> list:
    """Get elements at even indices using filter."""
    return [value for i, value in filter(
        lambda pair: pair[0] % 2 == 0,
        enumerate(items)
    )]

# Usage
result = get_elements_at_even_indices(['a', 'b', 'c', 'd', 'e'])
# Returns: ['a', 'c', 'e']
```

**Directive Action**: Use enumerate() with filter for index-based filtering.

---

### Edge Case 2: Filtering with Limit

**Issue**: Need to stop after N matches

**Handling**:
```python
from itertools import islice

def get_first_n_matches(items: list, predicate, n: int) -> list:
    """
    Get first N items matching predicate.

    Uses filter + islice for early termination.
    """
    return list(islice(filter(predicate, items), n))

# Usage
def is_even(x):
    return x % 2 == 0

first_three_evens = get_first_n_matches(range(100), is_even, 3)
# Returns: [0, 2, 4]
```

**Directive Action**: Use islice() with filter for limited results.

---

### Edge Case 3: Filtering with Context

**Issue**: Predicate needs context from outside

**Handling**:
```python
# Pass context as parameter or use closure
def create_age_filter(min_age: int):
    """
    Create age filter with min_age context.

    Returns predicate function with min_age captured.
    """
    def is_old_enough(person: dict) -> bool:
        return person['age'] >= min_age
    return is_old_enough

# Usage
is_adult = create_age_filter(18)
is_senior = create_age_filter(65)

adults = list(filter(is_adult, people))
seniors = list(filter(is_senior, people))

# Predicates carry context via closure
```

**Directive Action**: Use closures or partial application for contextual predicates.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Predicate functions must be pure
- **Triggers**:
  - `fp_list_operations` - Filter is core list operation
  - `fp_lazy_evaluation` - Lazy filtering for large datasets
- **Called By**:
  - `project_file_write` - Validate filtering patterns
  - Works with `fp_pattern_matching` - Match-based filtering
- **Escalates To**: None

---

## Helper Functions Used

- `detect_filter_loops(ast: AST) -> list[Loop]` - Find filtering patterns
- `extract_predicate_logic(loop: Loop) -> Predicate` - Extract predicate from if statement
- `verify_predicate_purity(predicate: Predicate) -> bool` - Check predicate is pure
- `convert_to_filter(loop: Loop, predicate: Predicate) -> str` - Convert to filter
- `update_functions_table(func_id: int, uses_declarative_filter: bool)` - Update project.db

---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `filtering_style = 'declarative'` for functions using filter
- **`functions`**: Tracks predicate purity in metadata
- **`notes`**: Logs filter conversions with `note_type = 'refactoring'`

---

## Testing

How to verify this directive is working:

1. **Imperative filter loop** → Directive converts to filter
   ```python
   # Input
   result = []
   for x in items:
       if x > 0:
           result.append(x)

   # Output
   result = [x for x in items if x > 0]
   ```

2. **Declarative filter** → Directive marks compliant
   ```python
   result = list(filter(lambda x: x > 0, items))
   # ✅ Already declarative
   ```

3. **Check database** → Verify filtering style marked
   ```sql
   SELECT name, filtering_style
   FROM functions
   WHERE filtering_style = 'declarative';
   ```

---

## Common Mistakes

- ❌ **Imperative loops for filtering** - Use filter/comprehension
- ❌ **Complex inline predicates** - Extract to named functions
- ❌ **Impure predicates** - No side effects in filter predicates
- ❌ **Not composing predicates** - Combine with AND/OR/NOT
- ❌ **Manual any/all loops** - Use built-in any/all

---

## Roadblocks and Resolutions

### Roadblock 1: imperative_filter_loop
**Issue**: Loop with if statement selecting elements
**Resolution**: Convert to filter() or list comprehension

### Roadblock 2: complex_inline_predicate
**Issue**: Complex filtering logic inline
**Resolution**: Extract to named predicate function

### Roadblock 3: stateful_predicate
**Issue**: Predicate depends on or modifies external state
**Resolution**: Make predicate pure, pass state as parameter

### Roadblock 4: manual_any_all
**Issue**: Manual loop for any/all logic
**Resolution**: Use built-in any() or all()

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-data-filtering)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#data-structures)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for declarative data filtering*
