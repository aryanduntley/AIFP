# fp_guard_clauses

## Purpose

The `fp_guard_clauses` directive rewrites nested conditional branches into early exit guard clauses to improve code clarity, maintainability, and readability. It identifies deeply nested if/else structures and refactors them using early return patterns, reducing cyclomatic complexity and making the "happy path" of code immediately clear. This encourages concise, readable control flow without excessive branching complexity.

**Category**: Control Flow
**Type**: FP Core
**Priority**: Medium
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`analyze_conditionals`**: Scan function bodies for nested conditional statements and validation logic.

### Branches

1. **`nested_if_detected`** → **`convert_to_guard_clause`**
   - **Condition**: Detects nested if/else statements (3+ levels)
   - **Action**: Convert to early return guard clauses
   - **Details**: Extract validation checks to top of function with early returns
   - **Output**: Flattened control flow with guard clauses

2. **`redundant_conditions`** → **`simplify_flow`**
   - **Condition**: Multiple conditions check the same constraint
   - **Action**: Consolidate redundant checks
   - **Details**: Merge duplicate validation logic
   - **Output**: Simplified conditional logic

3. **`validation_pattern`** → **`extract_guards`**
   - **Condition**: Input validation mixed with business logic
   - **Action**: Extract validation to guard clauses at function start
   - **Details**: Separate concerns: validation vs. transformation
   - **Output**: Guards at top, business logic after

4. **`already_guarded`** → **`mark_as_simplified`**
   - **Condition**: Function already uses guard clause pattern
   - **Action**: Mark as compliant
   - **Output**: Compliance confirmation

5. **Fallback** → **`mark_as_simplified`**
   - **Condition**: No nested conditionals requiring refactoring
   - **Action**: Mark as compliant

### Error Handling
- **On failure**: Prompt user with conditional analysis details
- **Low confidence** (< 0.7): Request review before refactoring

---

## Refactoring Strategies

### Strategy 1: Flatten Nested Conditionals
Convert nested if/else to sequential guard clauses.

**Before (Python - Nested)**:
```python
def process_user(user):
    if user is not None:
        if user['active']:
            if user['age'] >= 18:
                if user['verified']:
                    return perform_action(user)
                else:
                    return "User not verified"
            else:
                return "User too young"
        else:
            return "User inactive"
    else:
        return "User not found"
```

**After (Python - Guard Clauses)**:
```python
def process_user(user: dict | None) -> str:
    """Process user with guard clauses for validation."""
    # Guard clauses: early returns for invalid cases
    if user is None:
        return "User not found"

    if not user['active']:
        return "User inactive"

    if user['age'] < 18:
        return "User too young"

    if not user['verified']:
        return "User not verified"

    # Happy path: clear and unindented
    return perform_action(user)
```

### Strategy 2: Input Validation Guards
Extract validation logic to top of function with guard clauses.

**Before (TypeScript - Validation Mixed with Logic)**:
```typescript
function calculateDiscount(price: number, customerType: string): number {
  if (price > 0) {
    if (customerType === 'premium' || customerType === 'regular') {
      if (customerType === 'premium') {
        return price * 0.20;
      } else {
        return price * 0.10;
      }
    } else {
      throw new Error('Invalid customer type');
    }
  } else {
    throw new Error('Price must be positive');
  }
}
```

**After (TypeScript - Guard Clauses)**:
```typescript
function calculateDiscount(price: number, customerType: string): number {
  // Guard clauses: validate inputs first
  if (price <= 0) {
    throw new Error('Price must be positive');
  }

  if (customerType !== 'premium' && customerType !== 'regular') {
    throw new Error('Invalid customer type');
  }

  // Business logic: clear and straightforward
  return customerType === 'premium' ? price * 0.20 : price * 0.10;
}
```

### Strategy 3: Null/Undefined Checks
Use guard clauses for null safety.

**Before (JavaScript - Nested Null Checks)**:
```javascript
function getUserEmail(user) {
  if (user) {
    if (user.profile) {
      if (user.profile.contact) {
        if (user.profile.contact.email) {
          return user.profile.contact.email;
        }
      }
    }
  }
  return null;
}
```

**After (JavaScript - Guard Clauses)**:
```javascript
function getUserEmail(user) {
  // Guard clauses: check each level
  if (!user) return null;
  if (!user.profile) return null;
  if (!user.profile.contact) return null;
  if (!user.profile.contact.email) return null;

  // Happy path
  return user.profile.contact.email;
}

// Or use optional chaining (modern JS)
function getUserEmail(user) {
  return user?.profile?.contact?.email ?? null;
}
```

### Strategy 4: Error Condition Guards
Check error conditions early with guards.

**Before (Rust - Nested Result Handling)**:
```rust
fn process_file(path: &str) -> Result<String, String> {
    let file_result = std::fs::read_to_string(path);
    if file_result.is_ok() {
        let content = file_result.unwrap();
        if !content.is_empty() {
            if content.len() < 10000 {
                Ok(content.to_uppercase())
            } else {
                Err("File too large".to_string())
            }
        } else {
            Err("File is empty".to_string())
        }
    } else {
        Err("Could not read file".to_string())
    }
}
```

**After (Rust - Guard Clauses with ? operator)**:
```rust
fn process_file(path: &str) -> Result<String, String> {
    // Guard: file must be readable
    let content = std::fs::read_to_string(path)
        .map_err(|_| "Could not read file".to_string())?;

    // Guard: file must not be empty
    if content.is_empty() {
        return Err("File is empty".to_string());
    }

    // Guard: file must be reasonable size
    if content.len() >= 10000 {
        return Err("File too large".to_string());
    }

    // Happy path
    Ok(content.to_uppercase())
}
```

### Strategy 5: Combine Multiple Guards
Group related validation checks.

**Before (Python - Scattered Validation)**:
```python
def create_user(name, email, age, country):
    if name:
        if email and '@' in email:
            if age and age >= 13:
                if country and len(country) == 2:
                    return save_user(name, email, age, country)
    raise ValueError("Invalid user data")
```

**After (Python - Grouped Guards)**:
```python
def create_user(name: str, email: str, age: int, country: str) -> dict:
    """Create user with validation guards."""
    # Name validation
    if not name:
        raise ValueError("Name is required")

    # Email validation
    if not email or '@' not in email:
        raise ValueError("Valid email is required")

    # Age validation
    if not age or age < 13:
        raise ValueError("User must be at least 13 years old")

    # Country validation
    if not country or len(country) != 2:
        raise ValueError("Valid country code is required")

    # All validations passed: proceed with creation
    return save_user(name, email, age, country)
```

---

## Examples

### Example 1: Array Processing with Guards

**Before (Nested)**:
```python
def process_items(items):
    if items:
        if len(items) > 0:
            if all(isinstance(item, dict) for item in items):
                return [transform_item(item) for item in items]
            else:
                raise ValueError("All items must be dictionaries")
        else:
            return []
    else:
        raise ValueError("Items cannot be None")
```

**After (Guard Clauses)**:
```python
def process_items(items: list[dict] | None) -> list[dict]:
    """Process items with guard clause validation."""
    # Guard: items must exist
    if items is None:
        raise ValueError("Items cannot be None")

    # Guard: empty list returns empty
    if len(items) == 0:
        return []

    # Guard: all items must be dicts
    if not all(isinstance(item, dict) for item in items):
        raise ValueError("All items must be dictionaries")

    # Happy path: transform items
    return [transform_item(item) for item in items]
```

### Example 2: Authorization Guards

**Before (TypeScript - Nested Authorization)**:
```typescript
function deletePost(postId: number, userId: number): boolean {
  const post = getPost(postId);
  if (post) {
    const user = getUser(userId);
    if (user) {
      if (user.isAdmin || post.authorId === userId) {
        if (post.status !== 'archived') {
          performDelete(postId);
          return true;
        } else {
          throw new Error('Cannot delete archived post');
        }
      } else {
        throw new Error('Unauthorized');
      }
    } else {
      throw new Error('User not found');
    }
  } else {
    throw new Error('Post not found');
  }
}
```

**After (TypeScript - Guard Clauses)**:
```typescript
function deletePost(postId: number, userId: number): boolean {
  // Guard: post must exist
  const post = getPost(postId);
  if (!post) {
    throw new Error('Post not found');
  }

  // Guard: user must exist
  const user = getUser(userId);
  if (!user) {
    throw new Error('User not found');
  }

  // Guard: user must be authorized
  if (!user.isAdmin && post.authorId !== userId) {
    throw new Error('Unauthorized');
  }

  // Guard: post must not be archived
  if (post.status === 'archived') {
    throw new Error('Cannot delete archived post');
  }

  // Happy path: perform deletion
  performDelete(postId);
  return true;
}
```

### Example 3: Configuration Validation

**Before (Python - Nested Config Checks)**:
```python
def initialize_service(config):
    if 'api_key' in config:
        if config['api_key']:
            if 'endpoint' in config:
                if config['endpoint'].startswith('https://'):
                    if 'timeout' in config:
                        if config['timeout'] > 0:
                            return connect_service(config)
    raise ValueError("Invalid configuration")
```

**After (Python - Guard Clauses)**:
```python
def initialize_service(config: dict) -> Service:
    """Initialize service with configuration guards."""
    # Guard: API key required
    if 'api_key' not in config or not config['api_key']:
        raise ValueError("API key is required")

    # Guard: endpoint required and must be HTTPS
    if 'endpoint' not in config:
        raise ValueError("Endpoint is required")

    if not config['endpoint'].startswith('https://'):
        raise ValueError("Endpoint must use HTTPS")

    # Guard: timeout must be positive
    if 'timeout' not in config or config['timeout'] <= 0:
        raise ValueError("Timeout must be positive")

    # Happy path: connect to service
    return connect_service(config)
```

---

## Edge Cases

### Edge Case 1: Guard Clauses with Side Effects
**Scenario**: Early return prevents necessary cleanup
**Issue**: Guard clause returns before cleanup code executes
**Handling**:
- Use context managers or defer patterns
- Ensure cleanup happens before guard checks
- Wrap in try/finally if necessary

**Example**:
```python
# ❌ Bad: cleanup never happens if guard triggers
def process_with_lock(resource):
    lock.acquire()
    if not is_valid(resource):
        return None  # Lock never released!
    result = do_work(resource)
    lock.release()
    return result

# ✅ Good: context manager ensures cleanup
def process_with_lock(resource):
    with lock:
        if not is_valid(resource):
            return None  # Lock automatically released
        return do_work(resource)
```

### Edge Case 2: Order of Guard Clauses
**Scenario**: Guard order affects performance or behavior
**Issue**: Expensive checks performed before cheap ones
**Handling**:
- Order guards by cost (cheap checks first)
- Order guards by likelihood (common failures first)
- Document guard ordering rationale

**Example**:
```python
# ✅ Good: cheap checks first
def process_data(data):
    # Cheap: null check
    if data is None:
        return None

    # Cheap: empty check
    if len(data) == 0:
        return []

    # Expensive: validation
    if not validate_schema(data):
        raise ValueError("Invalid schema")

    # Expensive: remote call
    if not check_permissions_remote(data):
        raise PermissionError("Unauthorized")

    return transform(data)
```

### Edge Case 3: Multiple Return Types
**Scenario**: Guards return different types than happy path
**Issue**: Type safety concerns with mixed return types
**Handling**:
- Use Result/Option types for uniform returns
- Ensure all paths return compatible types
- Use type narrowing for type safety

**Example** (TypeScript):
```typescript
// ✅ Good: consistent return type with Result pattern
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function processUser(user: User | null): Result<string, string> {
  // Guard: uniform error type
  if (!user) {
    return { ok: false, error: 'User not found' };
  }

  if (!user.active) {
    return { ok: false, error: 'User inactive' };
  }

  // Happy path: uniform success type
  return { ok: true, value: performAction(user) };
}
```

### Edge Case 4: Complex Guard Conditions
**Scenario**: Guard condition spans multiple lines
**Issue**: Reduces clarity of guard clause pattern
**Handling**:
- Extract complex condition to named boolean function
- Document intent of complex guard
- Consider breaking into multiple simpler guards

**Example**:
```python
# ❌ Bad: complex inline guard
def process(user):
    if not (user and user.get('active') and user.get('verified') and
            user.get('age', 0) >= 18 and user.get('country') in ALLOWED_COUNTRIES):
        return None

# ✅ Good: named guard function
def is_eligible_user(user):
    """Check if user meets all eligibility requirements."""
    return (
        user is not None and
        user.get('active') and
        user.get('verified') and
        user.get('age', 0) >= 18 and
        user.get('country') in ALLOWED_COUNTRIES
    )

def process(user):
    if not is_eligible_user(user):
        return None
    return perform_action(user)
```

### Edge Case 5: Guard Clauses in Loops
**Scenario**: Guards inside loop iterations
**Issue**: Continue vs. return semantics unclear
**Handling**:
- Use `continue` for skipping iterations
- Use `return` for exiting function
- Document loop guard behavior clearly

**Example**:
```python
def process_batch(items):
    results = []
    for item in items:
        # Guard: skip invalid items (continue)
        if not is_valid(item):
            continue

        # Guard: stop processing on critical error (return)
        if is_critical_error(item):
            return results  # Partial results

        results.append(transform(item))

    return results
```

---

## Database Operations

### Record Guard Clause Refactoring

```sql
-- Update function with guard clause metadata
UPDATE functions
SET
    uses_guard_clauses = 1,
    complexity_score = 2,  -- Reduced from 5
    control_flow_style = 'guard_clauses',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'process_user' AND file_id = ?;

-- Record refactoring
INSERT INTO notes (project_id, content, tags, created_at)
VALUES (
    1,
    'Refactored process_user from nested conditionals to guard clauses, reducing complexity',
    '["fp_guard_clauses", "refactoring", "complexity_reduction"]',
    CURRENT_TIMESTAMP
);
```

### Query Functions Needing Guard Clause Refactoring

```sql
-- Find functions with high nesting depth
SELECT f.id, f.name, f.file_id, f.complexity_score
FROM functions f
WHERE f.control_flow_style = 'nested_conditionals'
  AND f.complexity_score > 4
ORDER BY f.complexity_score DESC;
```

---

## Related Directives

### FP Directives
- **fp_pattern_matching**: Alternative to guard clauses for complex conditions
- **fp_conditional_elimination**: Converts conditionals to expressions
- **fp_purity**: Guard clauses should maintain function purity

### Project Directives
- **project_compliance_check**: Validates guard clause usage
- **project_update_db**: Records control flow refactoring

---

## Helper Functions

### `detect_nested_depth(function_body) -> int`
Measures maximum nesting depth of conditionals.

**Signature**:
```python
def detect_nested_depth(function_body: ASTNode) -> int:
    """
    Analyzes conditional nesting depth.
    Returns maximum depth found (0 = no nesting).
    """
```

### `extract_guard_conditions(function_def) -> list[GuardCondition]`
Identifies conditions suitable for guard clause extraction.

**Signature**:
```python
def extract_guard_conditions(
    function_def: FunctionDefinition
) -> list[GuardCondition]:
    """
    Finds validation checks and error conditions.
    Returns list of conditions that should become guards.
    """
```

### `refactor_to_guards(function_body, guards) -> ASTNode`
Transforms function to use guard clause pattern.

**Signature**:
```python
def refactor_to_guards(
    function_body: ASTNode,
    guards: list[GuardCondition]
) -> ASTNode:
    """
    Rewrites function with guards at top, happy path at bottom.
    Returns transformed AST.
    """
```

---

## Testing

### Test 1: Detect Nesting Depth
```python
def test_detect_nested_depth():
    nested_code = """
def process(x):
    if x:
        if x > 0:
            if x < 100:
                return x * 2
"""

    depth = fp_guard_clauses.analyze_depth(nested_code)
    assert depth == 3  # Three levels of nesting
```

### Test 2: Refactor to Guards
```python
def test_refactor_to_guards():
    nested = """
def validate(user):
    if user:
        if user['active']:
            return True
        else:
            return False
    else:
        return False
"""

    result = fp_guard_clauses.refactor(nested)

    assert "if not user:" in result
    assert "if not user['active']:" in result
    assert result.count("return") <= 2  # Fewer returns
```

### Test 3: Complexity Reduction
```python
def test_complexity_reduction():
    before = """
def process(a, b, c):
    if a:
        if b:
            if c:
                return a + b + c
"""

    after = fp_guard_clauses.refactor(before)

    before_complexity = calculate_complexity(before)
    after_complexity = calculate_complexity(after)

    assert after_complexity < before_complexity
```

---

## Common Mistakes

### Mistake 1: Too Many Guards
**Problem**: Every line becomes a guard clause

**Solution**: Group related validations, use reasonable judgment

```python
# ❌ Bad: excessive guards
def process(x, y, z):
    if x < 0:
        raise ValueError()
    if x > 100:
        raise ValueError()
    if y < 0:
        raise ValueError()
    if y > 100:
        raise ValueError()
    # ... 20 more guards

# ✅ Good: grouped validation
def validate_range(value, name):
    if not 0 <= value <= 100:
        raise ValueError(f"{name} must be 0-100")

def process(x, y, z):
    validate_range(x, "x")
    validate_range(y, "y")
    # Business logic
```

### Mistake 2: Guards with Complex Logic
**Problem**: Guard clause itself is complex

**Solution**: Extract to named function

```python
# ❌ Bad: complex guard
if not (user and user.verified and user.age >= 18 and user.country == 'US'):
    return None

# ✅ Good: named validation
def is_eligible(user):
    return (user and user.verified and user.age >= 18 and user.country == 'US')

if not is_eligible(user):
    return None
```

### Mistake 3: Returning Different Types
**Problem**: Guards return incompatible types

**Solution**: Use consistent return types (Result/Option)

```python
# ❌ Bad: mixed types
def process(x):
    if x is None:
        return None  # None
    if x < 0:
        return False  # bool
    return x * 2  # int

# ✅ Good: consistent Option type
def process(x):
    if x is None or x < 0:
        return None
    return x * 2
```

---

## Roadblocks

### Roadblock 1: Deep Nesting
**Issue**: Nested conditionals 5+ levels deep
**Resolution**: Introduce guard clauses with early returns

### Roadblock 2: Redundant Branch
**Issue**: Multiple branches check same condition
**Resolution**: Simplify flow, consolidate checks

### Roadblock 3: Side Effects Before Guards
**Issue**: Side effects must happen before validation
**Resolution**: Ensure side effects properly handled with guards (use context managers)

---

## Integration Points

### With `fp_pattern_matching`
Guard clauses complement pattern matching for simple validation cases.

### With `fp_conditional_elimination`
Guards are one strategy for eliminating imperative conditionals.

### With `project_compliance_check`
Validates that complex functions use guard clauses.

---

## Intent Keywords

- `guard clause`
- `early return`
- `flatten conditionals`
- `validation`
- `input check`

---

## Confidence Threshold

**0.7** - High confidence for automatic guard clause refactoring.

---

## Notes

- Guard clauses reduce cyclomatic complexity
- Early returns make the "happy path" clear
- Validation logic separated from business logic
- Improves readability by reducing indentation
- Guard clauses are idiomatic in many languages
- Works well with functional programming principles
- Combine with Result types for robust error handling
- Order guards by cost and likelihood for efficiency
- Document guard clause intent when non-obvious
- Guard clauses improve testability by isolating edge cases
