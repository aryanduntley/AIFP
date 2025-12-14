# Directive: fp_reflection_block

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: LOW - Prevents dynamic introspection for safety

---

## Purpose

The `fp_reflection_block` directive prevents runtime reflection, dynamic type inspection, and `eval`-like constructs that compromise code predictability and safety. This directive provides **reflection prevention** ensuring code behavior is statically analyzable.

Reflection blocking provides **static predictability**, enabling:
- **No Runtime Surprises**: All code paths known at compile time
- **Security**: No eval() or exec() exploitation
- **Performance**: No reflection overhead
- **AI Reasoning**: Code behavior is statically determinable
- **Type Safety**: No dynamic type manipulation

This directive acts as a **reflection guardian** preventing dynamic code execution.

---

## When to Apply

This directive applies when:
- **Writing new code** - Prevent reflection patterns
- **Refactoring legacy code** - Remove reflection usage
- **Security audit** - Block eval/exec for safety
- **Performance optimization** - Eliminate reflection overhead
- **Called by project directives**:
  - `project_file_write` - Check for reflection before writing
  - `project_compliance_check` - Flag reflection violations
  - Works with `fp_purity` - Reflection breaks purity

---

## Workflow

### Trunk: detect_reflection_usage

Scans code for reflection, eval, dynamic execution patterns and blocks or refactors them.

**Steps**:
1. **Parse code** - Build AST
2. **Detect reflection** - Find eval, exec, getattr, setattr, etc.
3. **Classify usage** - Determine if reflection is necessary
4. **Check alternatives** - Can it be done statically?
5. **Block or refactor** - Remove reflection or find alternative
6. **Validate safety** - Ensure no dynamic execution remains

### Branches

**Branch 1: If eval_or_exec_detected**
- **Then**: `block_dynamic_execution`
- **Details**: Code uses eval() or exec()
  - Pattern: `eval(user_input)`, `exec(code_string)`
  - **ALWAYS BLOCK** - Major security risk
  - Refactor to static alternative
  - Use explicit control flow
  - Never allow dynamic code execution
- **Result**: Returns code without eval/exec

**Branch 2: If reflection_for_serialization**
- **Then**: `use_explicit_serialization`
- **Details**: Reflection used for JSON/dict conversion
  - Pattern: `vars(obj)`, `obj.__dict__`
  - Replace with explicit serialization
  - Use dataclass asdict() or explicit dict
  - Make structure explicit
- **Result**: Returns explicit serialization

**Branch 3: If dynamic_attribute_access**
- **Then**: `refactor_to_static_access`
- **Details**: Uses getattr/setattr dynamically
  - Pattern: `getattr(obj, attr_name)` where attr_name is variable
  - Replace with match/case or if/elif
  - Make attribute access explicit
  - Use pattern matching
- **Result**: Returns static attribute access

**Branch 4: If type_introspection**
- **Then**: `use_static_typing`
- **Details**: Uses isinstance, type() dynamically
  - Pattern: Dynamic type checking
  - Replace with static type annotations
  - Use Union types or pattern matching
  - Make types explicit
- **Result**: Returns static types

**Branch 5: If no_reflection**
- **Then**: `mark_compliant`
- **Details**: No reflection usage found
  - Code is statically analyzable
  - No eval, exec, getattr, setattr
  - Type safety preserved
  - Compliant
- **Result**: Code passes check

**Fallback**: `prompt_user`
- **Details**: Complex reflection pattern
  - Unclear if reflection necessary
  - Possible legitimate use case
  - Ask user for guidance
- **Result**: User decides approach

---

## Examples

### ✅ Compliant Code

**Static Attribute Access (Passes):**

```python
# ✅ Good: Explicit attribute access
def get_user_name(user: User) -> str:
    """Get user full name."""
    return f"{user.first_name} {user.last_name}"

# No reflection
# Attributes accessed explicitly
# Type-safe
# AI can reason about code
```

**Why Compliant**:
- No dynamic attribute access
- Explicit attribute names
- Type-safe
- Statically analyzable

---

**Explicit Serialization (Passes):**

```python
from dataclasses import dataclass, asdict

@dataclass
class User:
    name: str
    age: int
    email: str

# ✅ Good: Explicit serialization
def serialize_user(user: User) -> dict:
    """Convert user to dictionary."""
    return asdict(user)

# Or manual explicit serialization
def serialize_user_manual(user: User) -> dict:
    """Convert user to dictionary explicitly."""
    return {
        'name': user.name,
        'age': user.age,
        'email': user.email
    }

# No vars() or __dict__
# Explicit fields
# Type-safe
```

**Why Compliant**:
- Uses explicit serialization (asdict)
- No __dict__ access
- All fields explicitly listed
- Type-safe and clear

---

**Pattern Matching Instead of getattr (Passes):**

```python
# ✅ Good: Pattern matching for attribute access
def get_attribute(obj: Config, attribute: str) -> str:
    """Get configuration attribute."""
    match attribute:
        case 'host':
            return obj.host
        case 'port':
            return str(obj.port)
        case 'debug':
            return str(obj.debug)
        case _:
            raise ValueError(f"Unknown attribute: {attribute}")

# Explicit attribute names
# No getattr() with variable name
# Type-safe
# All cases handled
```

**Why Compliant**:
- Uses pattern matching instead of getattr
- All attributes explicitly named
- Type-safe
- Statically analyzable

---

### ❌ Non-Compliant Code

**eval() Usage (CRITICAL VIOLATION):**

```python
# ❌ CRITICAL VIOLATION: eval() is NEVER allowed
def calculate_expression(expression: str) -> float:
    """Calculate mathematical expression."""
    return eval(expression)  # ← MAJOR SECURITY RISK!

# User input: calculate_expression("__import__('os').system('rm -rf /')")
# ← ARBITRARY CODE EXECUTION!

# Problem:
# - Arbitrary code execution
# - CRITICAL security vulnerability
# - No static analysis possible
# - ALWAYS blocked by AIFP
```

**Why Non-Compliant**:
- Uses eval() with untrusted input
- Critical security vulnerability
- Can execute arbitrary code
- ALWAYS blocked

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Explicit parser
import ast
import operator

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def calculate_expression_safe(expression: str) -> float:
    """Calculate mathematical expression safely."""
    try:
        tree = ast.parse(expression, mode='eval')
        return eval_node(tree.body)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

def eval_node(node):
    """Evaluate AST node safely."""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = eval_node(node.left)
        right = eval_node(node.right)
        op = ALLOWED_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Operator not allowed: {type(node.op)}")
        return op(left, right)
    else:
        raise ValueError(f"Node type not allowed: {type(node)}")

# Safe parsing
# Only allowed operations
# No arbitrary code execution
```

---

**Dynamic Attribute Access (Violation):**

```python
# ❌ VIOLATION: Dynamic attribute access with getattr
def get_config_value(config: Config, key: str):
    """Get configuration value dynamically."""
    return getattr(config, key)  # ← Dynamic reflection

# Problem:
# - Attribute name determined at runtime
# - No type safety
# - Cannot statically analyze
# - Any attribute can be accessed
# - Typos not caught at compile time
```

**Why Non-Compliant**:
- Uses getattr with variable attribute name
- Not statically analyzable
- No type safety
- Runtime errors possible

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Explicit pattern matching
def get_config_value(config: Config, key: str) -> str | int | bool:
    """Get configuration value explicitly."""
    match key:
        case 'host':
            return config.host
        case 'port':
            return config.port
        case 'debug':
            return config.debug
        case 'timeout':
            return config.timeout
        case _:
            raise ValueError(f"Unknown config key: {key}")

# All attributes explicitly named
# Type-safe
# Statically analyzable
# Typos caught at compile time
```

---

**vars() / __dict__ Access (Violation):**

```python
# ❌ VIOLATION: Using __dict__ for serialization
def serialize_object(obj) -> dict:
    """Serialize object to dictionary."""
    return obj.__dict__  # ← Reflection

# Or using vars()
def serialize_with_vars(obj) -> dict:
    """Serialize using vars()."""
    return vars(obj)  # ← Reflection

# Problem:
# - Accesses internal __dict__
# - Not explicit about structure
# - Includes private attributes
# - No type safety
# - Cannot validate structure
```

**Why Non-Compliant**:
- Uses __dict__ or vars()
- Not explicit about fields
- Includes private attributes
- No validation

**Refactored (Compliant):**

```python
from dataclasses import dataclass, asdict

# ✅ REFACTORED: Explicit serialization
@dataclass
class User:
    name: str
    age: int
    email: str

def serialize_user(user: User) -> dict:
    """Serialize user explicitly."""
    return asdict(user)

# Or manual explicit serialization
def serialize_user_manual(user: User) -> dict:
    """Serialize user with explicit fields."""
    return {
        'name': user.name,
        'age': user.age,
        'email': user.email
    }

# Explicit fields
# Type-safe
# Validated structure
```

---

**Dynamic Type Checking (Violation):**

```python
# ❌ VIOLATION: Dynamic type introspection
def process_value(value):
    """Process value based on runtime type."""
    if type(value) == int:  # ← Runtime type check
        return value * 2
    elif type(value) == str:
        return value.upper()
    elif type(value) == list:
        return len(value)
    else:
        raise ValueError("Unsupported type")

# Problem:
# - Runtime type checking
# - No static type information
# - Cannot validate at compile time
# - Not using Union types
```

**Why Non-Compliant**:
- Uses runtime type() checking
- No static types
- Not statically analyzable
- Should use Union types

**Refactored (Compliant):**

```python
from typing import Union

# ✅ REFACTORED: Static types with overloading or Union
def process_value(value: int) -> int:
    """Process integer value."""
    return value * 2

def process_string(value: str) -> str:
    """Process string value."""
    return value.upper()

def process_list(value: list) -> int:
    """Process list value."""
    return len(value)

# Or with Union type and pattern matching
def process_value_union(value: Union[int, str, list]) -> Union[int, str]:
    """Process value with static types."""
    match value:
        case int():
            return value * 2
        case str():
            return value.upper()
        case list():
            return len(value)
        case _:
            raise ValueError("Unsupported type")

# Static types
# Type checking at compile time
# Pattern matching explicit
```

---

## Blocked Reflection Patterns

### Python

| Pattern | Violation | Alternative |
|---------|-----------|-------------|
| `eval(code)` | ❌ CRITICAL | Parse and validate explicitly |
| `exec(code)` | ❌ CRITICAL | Use explicit control flow |
| `getattr(obj, var)` | ❌ Medium | Use pattern matching |
| `setattr(obj, var, val)` | ❌ Medium | Explicit attribute assignment |
| `obj.__dict__` | ❌ Low | Use asdict() or explicit dict |
| `vars(obj)` | ❌ Low | Explicit serialization |
| `type(obj)` | ❌ Low | Static type annotations |
| `isinstance(obj, str)` | ⚠️ Sometimes OK | Prefer Union types + match |

### JavaScript

| Pattern | Violation | Alternative |
|---------|-----------|-------------|
| `eval(code)` | ❌ CRITICAL | JSON.parse() for data only |
| `new Function(code)` | ❌ CRITICAL | Explicit functions |
| `obj[dynamicKey]` | ❌ Medium | Pattern matching |
| `typeof x === 'string'` | ❌ Low | TypeScript static types |

### Reflection Severity Levels

- **CRITICAL**: eval, exec, new Function - ALWAYS block
- **MEDIUM**: getattr, setattr, dynamic access - Refactor to static
- **LOW**: __dict__, vars(), type() - Use explicit alternatives

---

## Edge Cases

### Edge Case 1: Legitimate Dynamic Access

**Issue**: Need to access attributes based on configuration

**Handling**:
```python
# Instead of dynamic getattr:
# ❌ value = getattr(config, user_setting)

# ✅ Use explicit mapping
SETTING_GETTERS = {
    'host': lambda c: c.host,
    'port': lambda c: c.port,
    'debug': lambda c: c.debug,
}

def get_setting(config: Config, setting: str):
    """Get setting value explicitly."""
    getter = SETTING_GETTERS.get(setting)
    if getter is None:
        raise ValueError(f"Unknown setting: {setting}")
    return getter(config)

# Explicit mapping
# All attributes listed
# Type-safe
```

**Directive Action**: Use explicit mapping dictionaries instead of getattr.

---

### Edge Case 2: Plugin Systems

**Issue**: Plugins need to be loaded dynamically

**Handling**:
```python
# ❌ Bad: Dynamic import
# plugin = __import__(plugin_name)

# ✅ Good: Explicit plugin registry
PLUGINS = {
    'auth': auth_plugin,
    'logging': logging_plugin,
    'cache': cache_plugin,
}

def load_plugin(name: str):
    """Load plugin from registry."""
    plugin = PLUGINS.get(name)
    if plugin is None:
        raise ValueError(f"Unknown plugin: {name}")
    return plugin

# All plugins explicitly registered
# No dynamic imports
# Statically analyzable
```

**Directive Action**: Use explicit plugin registries instead of dynamic imports.

---

### Edge Case 3: Testing and Mocking

**Issue**: Tests may need to mock attributes

**Handling**:
```python
# ✅ Use explicit mock objects instead of setattr
class MockDatabase:
    """Explicit mock for database."""
    def __init__(self):
        self.queries = []

    def query(self, sql):
        self.queries.append(sql)
        return []

# Use dependency injection
def test_user_service():
    mock_db = MockDatabase()
    service = UserService(db=mock_db)  # Inject mock
    service.get_users()
    assert len(mock_db.queries) == 1

# No setattr
# Explicit mock
# Type-safe
```

**Directive Action**: Use explicit mock objects and dependency injection for tests.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Reflection breaks purity
  - `fp_type_safety` - Reflection bypasses type safety
- **Triggers**:
  - `project_compliance_check` - Flag reflection violations
- **Called By**:
  - `project_file_write` - Check for reflection before writing
  - Works with `fp_metadata_annotation` - Reflection prevents metadata
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `has_reflection = 1` for functions using reflection (violation)
- **`notes`**: Logs reflection violations with `note_type = 'security'`

---

## Testing

How to verify this directive is working:

1. **eval() detected** → Directive blocks and suggests alternative
   ```python
   # Before: eval(expression)
   # After: Blocked with safe parser suggestion
   ```

2. **getattr() detected** → Directive suggests pattern matching
   ```python
   # Before: getattr(obj, attr)
   # After: match statement with explicit attributes
   ```

3. **Check database** → Verify no reflection usage
   ```sql
   SELECT name, has_reflection
   FROM functions
   WHERE has_reflection = 1;
   -- Should return no results
   ```

---

## Common Mistakes

- ❌ **Using eval() for calculations** - Major security risk
- ❌ **Dynamic attribute access** - Breaks type safety
- ❌ **__dict__ for serialization** - Not explicit
- ❌ **Runtime type checking** - Should use static types
- ❌ **Dynamic imports** - Not statically analyzable

---

## Roadblocks and Resolutions

### Roadblock 1: eval_or_exec_detected
**Issue**: Code uses eval() or exec() for dynamic execution
**Resolution**: ALWAYS block; refactor to explicit parsing with whitelist of allowed operations

### Roadblock 2: dynamic_attribute_access
**Issue**: Uses getattr/setattr with variable attribute names
**Resolution**: Replace with pattern matching and explicit attribute names

### Roadblock 3: reflection_for_serialization
**Issue**: Uses __dict__ or vars() for object serialization
**Resolution**: Use dataclass asdict() or explicit dictionary construction

### Roadblock 4: plugin_system
**Issue**: Plugin system requires dynamic loading
**Resolution**: Use explicit plugin registry with all plugins pre-registered

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for reflection prevention*
