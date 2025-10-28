# fp_reflection_limitation

## Purpose

The `fp_reflection_limitation` directive detects and disallows reflection, dynamic eval, or runtime metaprogramming constructs that violate AIFP determinism principles. It prevents runtime code generation, dynamic property access, eval statements, and other forms of runtime introspection that make code behavior unpredictable and difficult to reason about. This ensures all code behavior is statically analyzable and deterministic.

**Category**: Introspection
**Type**: FP Core
**Priority**: High
**Confidence Threshold**: 0.8

---

## Workflow

### Trunk
**`scan_code_for_reflection`**: Analyze code for reflection, eval, dynamic code execution, or runtime metaprogramming.

### Branches

1. **`eval_or_reflect_found`** → **`block_or_warn`**
   - **Condition**: Detects eval(), exec(), getattr(), setattr(), __import__(), etc.
   - **Action**: Block usage or generate warning
   - **Details**: Suggest static alternatives
   - **Output**: Reflection violation report

2. **`dynamic_property_access`** → **`suggest_static_access`**
   - **Condition**: Property accessed via string or computed name
   - **Action**: Suggest explicit static property access
   - **Details**: Refactor to use explicit property references
   - **Output**: Static property access recommendation

3. **`type_introspection`** → **`validate_safe_usage`**
   - **Condition**: Uses type checking (isinstance, type())
   - **Action**: Validate introspection is safe and necessary
   - **Details**: Type checks acceptable, but limit dynamic dispatch
   - **Output**: Safe introspection confirmation

4. **`no_reflection`** → **`mark_as_safe`**
   - **Condition**: No reflection or dynamic code detected
   - **Action**: Mark as compliant
   - **Output**: Compliance confirmation

5. **Fallback** → **`mark_as_safe`**
   - **Condition**: Code is reflection-free
   - **Action**: Mark as compliant

### Error Handling
- **On failure**: Prompt user with reflection detection details
- **Low confidence** (< 0.8): Request review for borderline cases

---

## Refactoring Strategies

### Strategy 1: Eliminate eval() and exec()
Replace dynamic code execution with static alternatives.

**Before (Python - Using eval)**:
```python
# Dangerous: arbitrary code execution
def calculate_expression(expression: str) -> float:
    return eval(expression)  # SECURITY RISK!

result = calculate_expression("2 + 2 * 10")  # What if user passes "__import__('os').system('rm -rf /')"?
```

**After (Python - Static Parser)**:
```python
import operator
from dataclasses import dataclass
from typing import Union

@dataclass
class BinaryOp:
    left: Union[float, 'BinaryOp']
    op: str
    right: Union[float, 'BinaryOp']

OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
}

def parse_expression(expr: str) -> BinaryOp:
    """Parse expression into AST."""
    # Simple parser (production code needs robust parser)
    tokens = expr.replace('(', ' ( ').replace(')', ' ) ').split()
    # ... parsing logic ...
    return BinaryOp(left=2, op='+', right=BinaryOp(left=2, op='*', right=10))

def evaluate_ast(node: Union[float, BinaryOp]) -> float:
    """Evaluate AST safely."""
    if isinstance(node, (int, float)):
        return float(node)

    if isinstance(node, BinaryOp):
        left_val = evaluate_ast(node.left)
        right_val = evaluate_ast(node.right)
        op_func = OPERATORS.get(node.op)

        if op_func:
            return op_func(left_val, right_val)

        raise ValueError(f"Unknown operator: {node.op}")

    raise ValueError(f"Unknown node type: {type(node)}")

def calculate_expression_safe(expression: str) -> float:
    """Safe expression evaluation without eval."""
    ast = parse_expression(expression)
    return evaluate_ast(ast)
```

### Strategy 2: Replace getattr/setattr with Explicit Access
Convert dynamic attribute access to static property access.

**Before (Python - Dynamic Attributes)**:
```python
def get_user_property(user: dict, property_name: str):
    """Dynamic property access (unpredictable)."""
    return getattr(user, property_name)  # What property? Unknown at static analysis!

# Usage
value = get_user_property(user, "email")  # Dynamic!
```

**After (Python - Static Access)**:
```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class User:
    name: str
    email: str
    age: int

PropertyName = Literal["name", "email", "age"]

def get_user_property(user: User, property_name: PropertyName) -> str | int:
    """Static property access with type safety."""
    match property_name:
        case "name":
            return user.name
        case "email":
            return user.email
        case "age":
            return user.age

# Or use explicit access
def get_user_email(user: User) -> str:
    return user.email  # Static, type-safe
```

### Strategy 3: Replace __import__() with Static Imports
Convert dynamic imports to static import statements.

**Before (Python - Dynamic Import)**:
```python
def load_module(module_name: str):
    """Dynamic module loading (unpredictable)."""
    return __import__(module_name)  # Runtime import!

# Usage
math_module = load_module("math")
result = math_module.sqrt(16)
```

**After (Python - Static Import with Dispatch)**:
```python
import math
import json
import os

# Static module registry
MODULES = {
    "math": math,
    "json": json,
    "os": os,
}

def get_module(module_name: str):
    """Static module lookup (predictable)."""
    if module_name not in MODULES:
        raise ValueError(f"Module {module_name} not available")
    return MODULES[module_name]

# Usage
math_module = get_module("math")
result = math_module.sqrt(16)
```

### Strategy 4: Replace Dynamic Dispatch with Static Dispatch Table
Convert dynamic method calls to static dispatch.

**Before (JavaScript - Dynamic Method Call)**:
```javascript
// Dynamic method invocation
function callMethod(obj, methodName, ...args) {
  return obj[methodName](...args);  // Unpredictable!
}

const user = {
  getName: () => "Alice",
  getEmail: () => "alice@example.com"
};

const result = callMethod(user, "getName");  // What method? Unknown statically!
```

**After (JavaScript - Static Dispatch)**:
```javascript
// Static method dispatch table
interface User {
  getName: () => string;
  getEmail: () => string;
}

type UserMethod = 'getName' | 'getEmail';

function callUserMethod(user: User, method: UserMethod): string {
  // Static dispatch with type safety
  switch (method) {
    case 'getName':
      return user.getName();
    case 'getEmail':
      return user.getEmail();
    default:
      const exhaustive: never = method;
      throw new Error(`Unknown method: ${exhaustive}`);
  }
}

// Usage
const result = callUserMethod(user, "getName");  // Type-safe!
```

### Strategy 5: Safe Type Checking (Acceptable Reflection)
Allow safe type introspection for runtime validation.

**Acceptable (Python - Type Checking)**:
```python
from typing import Union

def process_value(value: Union[int, str]) -> str:
    """Type checking for runtime dispatch is acceptable."""
    # Acceptable: isinstance for type discrimination
    if isinstance(value, int):
        return f"Number: {value}"
    elif isinstance(value, str):
        return f"String: {value}"
    else:
        raise TypeError(f"Unsupported type: {type(value)}")

# This is safe and deterministic
result = process_value(42)  # "Number: 42"
```

---

## Examples

### Example 1: Configuration Access

**Before (Dynamic - Non-Compliant)**:
```python
config = {
    "api_key": "secret",
    "endpoint": "https://api.example.com",
    "timeout": 30
}

def get_config_value(key: str):
    """Dynamic config access."""
    return config.get(key)  # What key? Unknown!

# Usage
api_key = get_config_value("api_key")
```

**After (Static - Compliant)**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    api_key: str
    endpoint: str
    timeout: int

config = Config(
    api_key="secret",
    endpoint="https://api.example.com",
    timeout=30
)

def get_api_key(config: Config) -> str:
    """Static config access."""
    return config.api_key  # Explicit, type-safe

# Usage
api_key = get_api_key(config)
```

### Example 2: Function Dispatch

**Before (Dynamic - Non-Compliant)**:
```python
def dispatch_operation(operation: str, a: int, b: int) -> int:
    """Dynamic function dispatch."""
    func = globals()[operation]  # Reflection!
    return func(a, b)

# Usage
result = dispatch_operation("add", 5, 3)  # What function? Unknown!
```

**After (Static - Compliant)**:
```python
from typing import Callable, Literal

Operation = Literal["add", "subtract", "multiply"]

def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b

def multiply(a: int, b: int) -> int:
    return a * b

OPERATIONS: dict[Operation, Callable[[int, int], int]] = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
}

def dispatch_operation(operation: Operation, a: int, b: int) -> int:
    """Static function dispatch."""
    func = OPERATIONS.get(operation)
    if func is None:
        raise ValueError(f"Unknown operation: {operation}")
    return func(a, b)

# Usage
result = dispatch_operation("add", 5, 3)  # Type-safe, predictable
```

---

## Edge Cases

### Edge Case 1: Necessary Type Checking
**Scenario**: Runtime type validation required
**Issue**: isinstance() is technically reflection
**Handling**:
- Allow isinstance() for type discrimination
- Limit to simple type checks
- Prefer static typing where possible

### Edge Case 2: Serialization/Deserialization
**Scenario**: Converting objects to/from JSON
**Issue**: May require introspection
**Handling**:
- Use explicit serialization methods
- Define toJSON/fromJSON functions
- Avoid generic reflection-based serializers

### Edge Case 3: Testing and Mocking
**Scenario**: Tests need to mock or introspect
**Issue**: Test code may require reflection
**Handling**:
- Allow reflection in test code only
- Keep production code reflection-free
- Use dependency injection for testability

### Edge Case 4: Plugin Systems
**Scenario**: Dynamic plugin loading
**Issue**: Plugins loaded at runtime
**Handling**:
- Use static plugin registry
- Pre-declare all plugins
- Avoid runtime discovery

### Edge Case 5: Legacy Code Interop
**Scenario**: Interfacing with reflection-heavy legacy code
**Issue**: Cannot avoid reflection at boundary
**Handling**:
- Isolate reflection to adapter layer
- Keep core logic reflection-free
- Document reflection boundary

---

## Database Operations

### Record Reflection Violations

```sql
-- Flag function with reflection usage
UPDATE functions
SET
    uses_reflection = 1,
    reflection_types = '["eval", "getattr"]',
    compliance_status = 'violation',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'dynamic_function' AND file_id = ?;

-- Record violation
INSERT INTO notes (project_id, content, tags, created_at)
VALUES (
    1,
    'VIOLATION: Function dynamic_function uses eval() and getattr() - refactor to static code',
    '["fp_reflection_limitation", "violation", "security"]',
    CURRENT_TIMESTAMP
);
```

---

## Related Directives

### FP Directives
- **fp_purity**: Reflection breaks determinism (purity requirement)
- **fp_type_safety**: Static types eliminate need for reflection

### Project Directives
- **project_compliance_check**: Validates no reflection usage
- **project_update_db**: Records reflection violations

---

## Helper Functions

### `detect_reflection_usage(function_body) -> list[ReflectionUsage]`
Identifies reflection and dynamic code execution.

**Signature**:
```python
def detect_reflection_usage(
    function_body: ASTNode
) -> list[ReflectionUsage]:
    """
    Detects: eval, exec, getattr, setattr, __import__,
    globals(), locals(), compile(), etc.
    Returns list of reflection usages with locations.
    """
```

### `suggest_static_alternative(reflection_usage) -> str`
Recommends static alternative to reflection.

**Signature**:
```python
def suggest_static_alternative(
    reflection_usage: ReflectionUsage
) -> str:
    """
    Provides refactoring suggestion for each reflection type.
    Returns code example of static alternative.
    """
```

---

## Testing

### Test 1: Detect eval()
```python
def test_detect_eval():
    source = """
def calculate(expr):
    return eval(expr)
"""

    violations = fp_reflection_limitation.detect(source)

    assert len(violations) > 0
    assert any('eval' in v.type for v in violations)
```

### Test 2: Detect Dynamic Attribute Access
```python
def test_detect_getattr():
    source = """
def get_property(obj, name):
    return getattr(obj, name)
"""

    violations = fp_reflection_limitation.detect(source)

    assert any('getattr' in v.type for v in violations)
```

### Test 3: Allow Safe Type Checking
```python
def test_allow_isinstance():
    source = """
def process(value):
    if isinstance(value, int):
        return value * 2
    return 0
"""

    violations = fp_reflection_limitation.detect(source)

    # isinstance should be allowed
    assert len(violations) == 0
```

---

## Common Mistakes

### Mistake 1: Using eval() for Configuration
**Problem**: Using eval() to parse config

**Solution**: Use JSON or explicit parsing

```python
# ❌ Bad: eval for config
config_str = "{'key': 'value'}"
config = eval(config_str)  # Dangerous!

# ✅ Good: JSON parsing
import json
config_str = '{"key": "value"}'
config = json.loads(config_str)
```

### Mistake 2: Dynamic Method Dispatch
**Problem**: Calling methods by string name

**Solution**: Use static dispatch table

```python
# ❌ Bad: dynamic method call
method_name = "process"
result = getattr(obj, method_name)()

# ✅ Good: static dispatch
def call_method(obj, method):
    if method == "process":
        return obj.process()
    raise ValueError(f"Unknown method: {method}")
```

### Mistake 3: Runtime Code Generation
**Problem**: Generating code at runtime

**Solution**: Use static code with configuration

```python
# ❌ Bad: runtime code gen
code = f"def func(): return {value}"
exec(code)

# ✅ Good: static function with parameter
def func(value):
    return value
```

---

## Roadblocks

### Roadblock 1: Reflection Detected
**Issue**: Code uses eval, exec, getattr, etc.
**Resolution**: Refactor to static binding, dispatch tables

### Roadblock 2: Dynamic Plugin Loading
**Issue**: Plugins loaded dynamically at runtime
**Resolution**: Use static plugin registry, pre-declare plugins

### Roadblock 3: Legacy Interop
**Issue**: Must interface with reflection-heavy legacy code
**Resolution**: Isolate to adapter layer, keep core reflection-free

---

## Integration Points

### With `fp_purity`
Reflection breaks determinism, violates purity.

### With `project_compliance_check`
Validates codebase is reflection-free.

---

## Intent Keywords

- `reflection`
- `eval`
- `dynamic code`
- `metaprogramming`
- `runtime code generation`

---

## Confidence Threshold

**0.8** - Very high confidence to avoid false positives.

---

## Notes

- Reflection makes code unpredictable and hard to analyze
- eval/exec are security risks (arbitrary code execution)
- Static alternatives: dispatch tables, pattern matching
- Type checking (isinstance) is acceptable reflection
- Dynamic imports should be static registries
- Serialization should use explicit methods
- Testing may require limited reflection (isolate to tests)
- Plugin systems: static registry, not runtime discovery
- Legacy interop: isolate reflection to boundaries
- AIFP requires statically analyzable, deterministic code
