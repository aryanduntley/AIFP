# fp_generic_constraints

## Purpose

The `fp_generic_constraints` directive adds compile-time-like constraints for generic parameters (type variables, templates) to ensure type safety and prevent misuse of polymorphic functions. It validates that generics or templates adhere to specified type constraints, using bounds, protocols, traits, or interfaces to restrict what types can be used with generic functions. This ensures correctness when using generics or polymorphic function templates, catching type errors early and providing better developer experience.

**Category**: Type System
**Type**: FP Core
**Priority**: Medium
**Confidence Threshold**: 0.6

---

## Workflow

### Trunk
**`check_generic_bounds`**: Analyze generic type parameters for constraints and validate usage.

### Branches

1. **`unbounded_generic`** → **`infer_constraints`**
   - **Condition**: Generic parameter has no constraints
   - **Action**: Infer constraints from how parameter is used
   - **Details**: Analyze operations to determine required capabilities
   - **Output**: Inferred type constraints

2. **`conflicting_bounds`** → **`prompt_user`**
   - **Condition**: Multiple incompatible constraints on same parameter
   - **Action**: Request user clarification on correct constraints
   - **Details**: Present conflict for resolution

3. **`under_constrained`** → **`suggest_bounds`**
   - **Condition**: Generic too permissive for its usage
   - **Action**: Suggest tighter constraints based on usage
   - **Details**: Recommend Protocol, bound, or trait constraints
   - **Output**: Constraint suggestions

4. **`properly_bounded`** → **`mark_as_safe`**
   - **Condition**: Generic has appropriate constraints
   - **Action**: Mark as type-safe
   - **Output**: Compliance confirmation

5. **Fallback** → **`mark_as_safe`**
   - **Condition**: No generic parameters or constraints verified
   - **Action**: Mark as compliant

### Error Handling
- **On failure**: Prompt user with constraint analysis
- **Low confidence** (< 0.6): Request review before applying constraints

---

## Refactoring Strategies

### Strategy 1: Add Bounds to TypeVar (Python)
Constrain generic type variable to specific types.

**Before (Python - Unbounded)**:
```python
from typing import TypeVar

T = TypeVar('T')  # Unconstrained: accepts ANY type

def find_max(items: list[T]) -> T:
    """Find maximum element."""
    return max(items)  # ERROR: T might not be comparable!
```

**After (Python - Bounded)**:
```python
from typing import TypeVar, Protocol

class Comparable(Protocol):
    """Protocol defining comparable types."""
    def __lt__(self, other: Comparable) -> bool: ...

T = TypeVar('T', bound=Comparable)  # Constrained to comparable types

def find_max(items: list[T]) -> T:
    """Find maximum element (T must be comparable)."""
    return max(items)  # Type-safe: T guaranteed comparable
```

### Strategy 2: Protocol Constraints (Python)
Use protocols to define structural requirements.

**Before (Python - No Constraints)**:
```python
from typing import TypeVar

T = TypeVar('T')

def serialize(obj: T) -> str:
    """Serialize object to string."""
    return obj.to_json()  # ERROR: T might not have to_json!
```

**After (Python - Protocol Constraint)**:
```python
from typing import TypeVar, Protocol

class Serializable(Protocol):
    """Protocol for serializable objects."""
    def to_json(self) -> str: ...

T = TypeVar('T', bound=Serializable)

def serialize(obj: T) -> str:
    """Serialize object to string (T must be Serializable)."""
    return obj.to_json()  # Type-safe: T guaranteed to have to_json
```

### Strategy 3: TypeScript Generic Constraints
Use extends keyword to constrain generics.

**Before (TypeScript - Unconstrained)**:
```typescript
function getProperty<T>(obj: T, key: string): any {
  return obj[key];  // ERROR: T might not be indexable!
}
```

**After (TypeScript - Constrained)**:
```typescript
function getProperty<T extends Record<string, any>>(
  obj: T,
  key: keyof T
): T[keyof T] {
  return obj[key];  // Type-safe: T is indexable, key is valid
}
```

### Strategy 4: Rust Trait Bounds
Use trait bounds to constrain generic types.

**Before (Rust - Unconstrained)**:
```rust
// Won't compile: T not constrained
fn find_max<T>(items: Vec<T>) -> T {
    items.into_iter().max().unwrap()  // ERROR: T might not be Ord!
}
```

**After (Rust - Trait Bound)**:
```rust
fn find_max<T: Ord>(items: Vec<T>) -> T {
    items.into_iter().max().unwrap()  // Type-safe: T implements Ord
}

// Or with where clause for complex bounds
fn find_max<T>(items: Vec<T>) -> T
where
    T: Ord + Clone,
{
    items.into_iter().max().unwrap()
}
```

### Strategy 5: Multiple Constraint Bounds
Combine multiple constraints for complex requirements.

**Before (Python - Multiple Implied Constraints)**:
```python
from typing import TypeVar

T = TypeVar('T')  # Too permissive

def process_and_log(item: T) -> T:
    """Process item and log result."""
    result = item.process()  # Needs process method
    print(result)  # Needs __str__
    return result  # Returns same type
```

**After (Python - Multiple Constraints)**:
```python
from typing import TypeVar, Protocol

class Processable(Protocol):
    """Item that can be processed."""
    def process(self) -> str: ...

    def __str__(self) -> str: ...

T = TypeVar('T', bound=Processable)

def process_and_log(item: T) -> T:
    """Process item and log result (T must be Processable)."""
    result = item.process()
    print(result)
    return item  # Type-safe
```

---

## Examples

### Example 1: Numeric Operations

**Before (Unconstrained)**:
```python
from typing import TypeVar

T = TypeVar('T')

def average(numbers: list[T]) -> T:
    """Calculate average."""
    return sum(numbers) / len(numbers)  # ERROR: T might not support arithmetic!
```

**After (Constrained)**:
```python
from typing import TypeVar

# Constrain to numeric types
Numeric = TypeVar('Numeric', int, float, complex)

def average(numbers: list[Numeric]) -> float:
    """Calculate average (Numeric constrained to int|float|complex)."""
    return sum(numbers) / len(numbers)  # Type-safe
```

### Example 2: Container Operations

**Before (TypeScript - Weak Constraints)**:
```typescript
function first<T>(container: T): any {
  return container[0];  // ERROR: T might not be indexable!
}
```

**After (TypeScript - Proper Constraints)**:
```typescript
interface Indexable<T> {
  [index: number]: T;
  length: number;
}

function first<T>(container: Indexable<T>): T | undefined {
  return container.length > 0 ? container[0] : undefined;
}

// Or use built-in ArrayLike
function first<T>(container: ArrayLike<T>): T | undefined {
  return container.length > 0 ? container[0] : undefined;
}
```

### Example 3: Comparable Items

**Before (Rust - Won't Compile)**:
```rust
fn sort_items<T>(mut items: Vec<T>) -> Vec<T> {
    items.sort();  // ERROR: T doesn't implement Ord
    items
}
```

**After (Rust - Trait Bound)**:
```rust
fn sort_items<T: Ord>(mut items: Vec<T>) -> Vec<T> {
    items.sort();  // Type-safe: T implements Ord
    items
}
```

### Example 4: JSON Serialization

**Before (Python - Unconstrained)**:
```python
from typing import TypeVar
import json

T = TypeVar('T')

def to_json_string(obj: T) -> str:
    return json.dumps(obj)  # Only works for JSON-serializable types
```

**After (Python - Constrained)**:
```python
from typing import TypeVar, Union, Dict, List

# JSON-serializable types
JsonValue = Union[str, int, float, bool, None, Dict[str, 'JsonValue'], List['JsonValue']]
T = TypeVar('T', bound=JsonValue)

def to_json_string(obj: T) -> str:
    """Serialize JSON-compatible object (T constrained to JsonValue)."""
    return json.dumps(obj)  # Type-safe
```

### Example 5: Builder Pattern with Constraints

**Before (TypeScript - Unconstrained)**:
```typescript
class Builder<T> {
  private data: Partial<T> = {};

  set<K>(key: K, value: any): this {
    this.data[key] = value;  // ERROR: K might not be key of T!
    return this;
  }

  build(): T {
    return this.data as T;
  }
}
```

**After (TypeScript - Constrained)**:
```typescript
class Builder<T extends Record<string, any>> {
  private data: Partial<T> = {};

  set<K extends keyof T>(key: K, value: T[K]): this {
    this.data[key] = value;  // Type-safe: K is valid key, value is correct type
    return this;
  }

  build(): T {
    return this.data as T;
  }
}

// Usage
interface User {
  name: string;
  age: number;
}

const user = new Builder<User>()
  .set('name', 'Alice')  // Type-safe
  .set('age', 30)        // Type-safe
  // .set('invalid', 'x')  // Compile error!
  .build();
```

---

## Edge Cases

### Edge Case 1: Variance Issues
**Scenario**: Generic parameter variance affects constraint applicability
**Issue**: Covariance/contravariance complicates constraints
**Handling**:
- Use invariant type variables where needed
- Document variance requirements
- Test with subtype/supertype relationships

**Example** (Python):
```python
from typing import TypeVar

# Invariant (default)
T = TypeVar('T', bound=Animal)

# Covariant (for return types)
T_co = TypeVar('T_co', bound=Animal, covariant=True)

# Contravariant (for parameter types)
T_contra = TypeVar('T_contra', bound=Animal, contravariant=True)
```

### Edge Case 2: Self-Referential Constraints
**Scenario**: Generic type references itself in constraint
**Issue**: Circular type definition
**Handling**:
- Use forward references (string annotations)
- Define recursive protocols carefully
- Test recursive type resolution

**Example**:
```python
from typing import TypeVar, Protocol

class Comparable(Protocol):
    def __lt__(self: 'Comparable', other: 'Comparable') -> bool: ...

T = TypeVar('T', bound=Comparable)
```

### Edge Case 3: Multiple Type Parameters with Dependencies
**Scenario**: One type parameter depends on another
**Issue**: Complex constraint relationships
**Handling**:
- Use multiple bounds with clear relationships
- Document dependencies
- Consider refactoring to simpler constraints

**Example** (TypeScript):
```typescript
// Key type depends on Obj type
function getProperty<Obj extends object, Key extends keyof Obj>(
  obj: Obj,
  key: Key
): Obj[Key] {
  return obj[key];
}
```

### Edge Case 4: Runtime vs. Compile-Time Constraints
**Scenario**: Constraint enforceable at compile time but not runtime
**Issue**: Type erasure removes runtime constraint information
**Handling**:
- Add runtime validation where necessary
- Document compile-time vs. runtime guarantees
- Use type guards for runtime checks

**Example** (Python):
```python
from typing import TypeVar, Protocol, TYPE_CHECKING

class Serializable(Protocol):
    def serialize(self) -> str: ...

T = TypeVar('T', bound=Serializable)

def save(obj: T) -> None:
    """Save object (compile-time type-safe)."""
    # Runtime check needed: type erasure means T info lost at runtime
    if not hasattr(obj, 'serialize'):
        raise TypeError("Object must be Serializable")
    data = obj.serialize()
    write_to_disk(data)
```

### Edge Case 5: Over-Constrained Generics
**Scenario**: Constraints too restrictive for intended use
**Issue**: Reduces reusability
**Handling**:
- Use minimal necessary constraints
- Consider union types for flexibility
- Document constraint rationale

---

## Database Operations

### Store Generic Constraint Metadata

```sql
-- Update function with generic constraint info
UPDATE functions
SET
    has_generics = 1,
    generic_constraints = '{
        "type_params": [
            {"name": "T", "bound": "Comparable", "variance": "invariant"},
            {"name": "U", "bound": "Serializable", "variance": "covariant"}
        ],
        "constraint_method": "protocol"
    }',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'process_items' AND file_id = ?;

-- Record constraint addition
INSERT INTO notes (project_id, content, tags, created_at)
VALUES (
    1,
    'Added Comparable bound to generic parameter T in process_items',
    '["fp_generic_constraints", "type_safety", "refactoring"]',
    CURRENT_TIMESTAMP
);
```

### Query Functions with Unbounded Generics

```sql
-- Find functions with unconstrained generic parameters
SELECT f.id, f.name, f.file_id, f.generic_constraints
FROM functions f
WHERE f.has_generics = 1
  AND (f.generic_constraints IS NULL OR
       json_extract(f.generic_constraints, '$.type_params[0].bound') IS NULL)
ORDER BY f.call_count DESC;
```

---

## Related Directives

### FP Directives
- **fp_type_safety**: Ensures type annotations present (including constraints)
- **fp_type_inference**: Can infer appropriate generic bounds
- **fp_runtime_type_check**: Adds runtime validation for generic constraints

### Project Directives
- **project_compliance_check**: Validates generic constraint usage
- **project_update_db**: Records constraint metadata

---

## Helper Functions

### `infer_generic_bounds(function_body, type_param) -> Constraint`
Infers constraints from how generic parameter is used.

**Signature**:
```python
def infer_generic_bounds(
    function_body: ASTNode,
    type_param: str
) -> Constraint:
    """
    Analyzes operations on type parameter to infer required capabilities.
    Returns inferred bound/protocol/trait.
    """
```

### `validate_constraint_usage(function_def) -> list[ConstraintViolation]`
Checks that generic parameters are used consistently with constraints.

**Signature**:
```python
def validate_constraint_usage(
    function_def: FunctionDefinition
) -> list[ConstraintViolation]:
    """
    Verifies operations on generic types match declared constraints.
    Returns list of constraint violations.
    """
```

### `suggest_constraint(type_param_usage) -> Constraint`
Recommends appropriate constraint based on usage patterns.

**Signature**:
```python
def suggest_constraint(
    type_param_usage: UsageAnalysis
) -> Constraint:
    """
    Analyzes how type parameter is used.
    Suggests appropriate bound, protocol, or trait.
    """
```

---

## Testing

### Test 1: Detect Unbounded Generic
```python
def test_detect_unbounded():
    source = """
from typing import TypeVar

T = TypeVar('T')

def find_max(items: list[T]) -> T:
    return max(items)
"""

    issues = fp_generic_constraints.analyze(source)

    assert len(issues) > 0
    assert any('unbounded' in issue.lower() or 'constraint' in issue.lower()
               for issue in issues)
```

### Test 2: Infer Constraint from Usage
```python
def test_infer_constraint():
    source = """
from typing import TypeVar

T = TypeVar('T')

def compare(a: T, b: T) -> bool:
    return a < b  # Uses comparison
"""

    result = fp_generic_constraints.infer_bounds(source)

    assert 'Comparable' in str(result) or 'bound' in str(result)
```

### Test 3: Validate Constraint Satisfaction
```python
def test_validate_constraint():
    source = """
from typing import TypeVar, Protocol

class Numeric(Protocol):
    def __add__(self, other): ...

T = TypeVar('T', bound=Numeric)

def add(a: T, b: T) -> T:
    return a < b  # ERROR: < not in Numeric protocol!
"""

    violations = fp_generic_constraints.validate(source)

    assert len(violations) > 0
```

---

## Common Mistakes

### Mistake 1: Forgetting Bounds
**Problem**: Using generic without constraints

**Solution**: Add appropriate bound or protocol

```python
# ❌ Bad: no constraint
T = TypeVar('T')

def sort(items: list[T]) -> list[T]:
    return sorted(items)  # T might not be comparable!

# ✅ Good: constrained
from typing import Protocol

class Comparable(Protocol):
    def __lt__(self, other: Comparable) -> bool: ...

T = TypeVar('T', bound=Comparable)

def sort(items: list[T]) -> list[T]:
    return sorted(items)  # Type-safe
```

### Mistake 2: Over-Constraining
**Problem**: Constraints too restrictive

**Solution**: Use minimal necessary constraints

```python
# ❌ Bad: over-constrained
T = TypeVar('T', int, str)  # Only int or str

def identity(x: T) -> T:
    return x  # Doesn't need any constraints!

# ✅ Good: minimal constraint
T = TypeVar('T')  # Any type works

def identity(x: T) -> T:
    return x
```

### Mistake 3: Conflicting Bounds
**Problem**: Multiple incompatible constraints

**Solution**: Resolve conflict or use union

```python
# ❌ Bad: conflicting bounds (if this were possible)
T = TypeVar('T', bound=Comparable)
T = TypeVar('T', bound=Serializable)  # Conflict!

# ✅ Good: combined protocol
class ComparableAndSerializable(Comparable, Serializable, Protocol):
    pass

T = TypeVar('T', bound=ComparableAndSerializable)
```

---

## Roadblocks

### Roadblock 1: Unbounded Generic
**Issue**: Generic parameter has no constraints but needs them
**Resolution**: Infer constraints from usage or specify bound

### Roadblock 2: Type Conflict
**Issue**: Multiple incompatible bounds on same parameter
**Resolution**: Manually verify and resolve bounds

### Roadblock 3: Complex Constraint
**Issue**: Required constraint too complex to express simply
**Resolution**: Define custom protocol or trait, or simplify usage

### Roadblock 4: Runtime Constraint Validation
**Issue**: Compile-time constraint not enforced at runtime (type erasure)
**Resolution**: Add runtime type checks where necessary

---

## Integration Points

### With `fp_type_safety`
Generic constraints are part of overall type safety enforcement.

### With `fp_type_inference`
Type inference can suggest appropriate generic bounds.

### With `fp_runtime_type_check`
Runtime checks validate generic constraints when type erasure occurs.

---

## Intent Keywords

- `generic`
- `constraint`
- `bounded type`
- `type parameter`
- `protocol`
- `trait`

---

## Confidence Threshold

**0.6** - Moderate confidence as constraint inference is heuristic-based.

---

## Notes

- Generic constraints prevent misuse of polymorphic functions
- Python: Use `bound=` parameter or Protocol for constraints
- TypeScript: Use `extends` keyword for constraints
- Rust: Use trait bounds (`: Trait` syntax or `where` clause)
- Protocols/traits define structural requirements
- Constraints enable better compile-time error checking
- Over-constraining reduces reusability
- Under-constraining allows type errors
- Document constraint rationale for maintainability
- Type erasure means runtime validation may be needed
- Generic constraints improve IDE autocompletion and tooling
