# Directive: fp_pattern_unpacking

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Improves code clarity and reduces indexing errors

---

## Purpose

The `fp_pattern_unpacking` directive encourages declarative unpacking of tuples, lists, and objects through destructuring instead of index-based access. This directive provides **declarative data extraction** that makes code more readable and eliminates indexing errors.

Pattern unpacking provides **clear data access**, enabling:
- **No Magic Indices**: Named bindings instead of `[0]`, `[1]`, `[2]`
- **Self-Documenting Code**: Variable names reveal structure
- **Fewer Errors**: Compiler catches arity mismatches
- **FP Idiom**: Destructuring is standard in functional languages
- **Nested Unpacking**: Extract deeply nested values declaratively

This directive acts as a **clarity enhancer** transforming opaque index access into clear named bindings.

**Important**: This directive is reference documentation for pattern unpacking patterns.
AI consults this when uncertain about destructuring complex data structures or advanced unpacking scenarios.

**FP pattern unpacking is baseline behavior**:
- AI writes pattern unpacking naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about destructuring complex nested data structures
- Complex unpacking scenarios (deep nesting, partial matches, wildcards)
- Edge cases with optional fields or variable-length unpacking
- Need for detailed guidance on pattern unpacking syntax

**Context**:
- AI writes pattern unpacking as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_pattern_matching`, `fp_immutability`) may reference this for guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: analyze_data_access

Scans code for index-based access patterns that can be replaced with declarative destructuring.

**Steps**:
1. **Detect index access** - Find `tuple[0]`, `list[1]`, etc.
2. **Analyze access patterns** - Determine if indices are fixed
3. **Check structure** - Verify data structure has known shape
4. **Identify unpacking opportunity** - Multiple indices accessed
5. **Generate destructuring** - Create unpacking statement
6. **Replace index access** - Use unpacked variable names

### Branches

**Branch 1: If index_access**
- **Then**: `convert_to_destructuring`
- **Details**: Code uses index-based access for fixed positions
  - Pattern: `x = tuple[0]; y = tuple[1]`
  - Convert to: `x, y = tuple`
  - Declarative and clear
  - Compiler checks arity
- **Result**: Returns destructured code

**Branch 2: If nested_index_access**
- **Then**: `convert_to_nested_destructuring`
- **Details**: Nested structures accessed with multiple indices
  - Pattern: `a = nested[0][1]`
  - Convert to: `(x, (a, b)) = nested` or similar
  - Extract deeply nested values
  - Maintain clarity
- **Result**: Returns nested destructuring

**Branch 3: If dict_key_access**
- **Then**: `convert_to_dict_destructuring`
- **Details**: Dictionary with repeated key access
  - Pattern: `name = user['name']; age = user['age']`
  - Convert to: `{name, age} = user` (JS) or similar
  - Python: Use unpacking where supported
- **Result**: Returns dict destructuring

**Branch 4: If pattern_compatible**
- **Then**: `mark_as_compliant`
- **Details**: Already using destructuring
  - Code uses tuple unpacking
  - Named variables instead of indices
  - Clear and declarative
- **Result**: Code passes check

**Fallback**: `prompt_user`
- **Details**: Complex access pattern
  - Dynamic indices
  - Unclear structure
  - Ask user for guidance
- **Result**: User decides approach

---

## Examples

### ✅ Compliant Code

**Tuple Unpacking (Passes):**

```python
def get_user_info():
    """Return user name and age."""
    return ("Alice", 30)

# ✅ Good: Destructuring
name, age = get_user_info()
print(f"{name} is {age} years old")

# Clear what each value represents
# No magic indices
# Self-documenting
```

**Why Compliant**:
- Uses tuple unpacking
- Named variables (name, age)
- Clear and readable
- No index access

---

**Nested Unpacking (Passes):**

```python
def get_coordinates():
    """Return 3D point with metadata."""
    return (10, (20, 30), "origin")

# ✅ Good: Nested destructuring
x, (y, z), label = get_coordinates()
print(f"Point {label}: ({x}, {y}, {z})")

# Nested tuple unpacked declaratively
# All values have meaningful names
# Structure is clear
```

**Why Compliant**:
- Nested destructuring
- All values named
- Clear structure
- No nested index access

---

**Multiple Return Values (Passes):**

```python
def divide_with_remainder(a: int, b: int) -> tuple[int, int]:
    """Return quotient and remainder."""
    return (a // b, a % b)

# ✅ Good: Unpack both values
quotient, remainder = divide_with_remainder(17, 5)
print(f"{quotient} remainder {remainder}")

# Both values extracted with descriptive names
# No need for [0] and [1]
```

**Why Compliant**:
- Both return values unpacked
- Descriptive variable names
- Clear intent
- No index access

---

**List Destructuring (Passes):**

```python
# ✅ Good: Destructure list with known structure
def get_rgb_color():
    """Return RGB color as list."""
    return [255, 128, 0]  # Orange

# Unpack list values
red, green, blue = get_rgb_color()
print(f"RGB: ({red}, {green}, {blue})")

# Fixed-size list unpacked
# Color components have names
# Clear and readable
```

**Why Compliant**:
- Fixed-size list unpacked
- Named components
- Self-documenting
- No magic indices

---

### ❌ Non-Compliant Code

**Index-Based Tuple Access (Violation):**

```python
# ❌ VIOLATION: Index-based tuple access
def get_user_info():
    """Return user name and age."""
    return ("Alice", 30)

user_info = get_user_info()
name = user_info[0]  # ← Magic index [0]
age = user_info[1]   # ← Magic index [1]
print(f"{name} is {age} years old")

# Problem:
# - Magic indices [0], [1]
# - Not self-documenting
# - Easy to swap accidentally
# - Not using tuple unpacking
```

**Why Non-Compliant**:
- Uses index access [0], [1]
- Magic numbers
- Not declarative
- Should use unpacking

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Tuple unpacking
def get_user_info():
    """Return user name and age."""
    return ("Alice", 30)

name, age = get_user_info()
print(f"{name} is {age} years old")

# Clear, declarative, self-documenting
```

---

**Nested Index Access (Violation):**

```python
# ❌ VIOLATION: Nested index access
def get_point_3d():
    """Return 3D point with metadata."""
    return (10, (20, 30), "origin")

point = get_point_3d()
x = point[0]        # ← Index access
y = point[1][0]     # ← Nested index access
z = point[1][1]     # ← Nested index access
label = point[2]    # ← Index access

print(f"Point {label}: ({x}, {y}, {z})")

# Problem:
# - Multiple nested index accesses
# - Hard to understand structure
# - Error-prone (easy to get indices wrong)
# - Not using destructuring
```

**Why Non-Compliant**:
- Nested index access
- Opaque structure
- Error-prone
- Should use nested unpacking

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Nested destructuring
def get_point_3d():
    """Return 3D point with metadata."""
    return (10, (20, 30), "origin")

x, (y, z), label = get_point_3d()
print(f"Point {label}: ({x}, {y}, {z})")

# Structure is clear from unpacking
# All values have meaningful names
# Declarative and readable
```

---

**List Index Access (Violation):**

```python
# ❌ VIOLATION: List index access for fixed structure
def get_rgb_color():
    """Return RGB color as list."""
    return [255, 128, 0]

color = get_rgb_color()
red = color[0]    # ← Magic index
green = color[1]  # ← Magic index
blue = color[2]   # ← Magic index

print(f"RGB: ({red}, {green}, {blue})")

# Problem:
# - Index-based access for fixed structure
# - Magic indices 0, 1, 2
# - Not self-documenting
# - Should use unpacking
```

**Why Non-Compliant**:
- Index access for fixed list
- Magic numbers
- Not declarative
- Should unpack

**Refactored (Compliant):**

```python
# ✅ REFACTORED: List unpacking
def get_rgb_color():
    """Return RGB color as list."""
    return [255, 128, 0]

red, green, blue = get_rgb_color()
print(f"RGB: ({red}, {green}, {blue})")

# Clear, named components
# Self-documenting
```

---

**Dictionary Repeated Access (Violation):**

```python
# ❌ VIOLATION: Repeated dictionary key access
user = {
    'name': 'Alice',
    'age': 30,
    'email': 'alice@example.com'
}

name = user['name']    # ← Repeated key access
age = user['age']      # ← Repeated key access
email = user['email']  # ← Repeated key access

print(f"{name} ({age}): {email}")

# Problem:
# - Repeated dictionary access
# - Could use destructuring
# - Not as clear as it could be
```

**Why Non-Compliant**:
- Repeated dict access
- Could be more declarative
- Python 3.5+ supports unpacking

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Dictionary unpacking (Python 3.5+)
user = {
    'name': 'Alice',
    'age': 30,
    'email': 'alice@example.com'
}

# Unpack into function call
def format_user(name, age, email):
    """Format user info."""
    return f"{name} ({age}): {email}"

print(format_user(**user))

# Or with explicit unpacking in Python 3.10+:
# name, age, email = user['name'], user['age'], user['email']
# Better yet, use dataclasses or named tuples for structured data
```

---

## Edge Cases

### Edge Case 1: Partial Unpacking with Rest

**Issue**: Need some values but want to ignore rest

**Handling**:
```python
# Use underscore for ignored values

def get_user_data():
    """Return name, age, email, phone."""
    return ("Alice", 30, "alice@example.com", "555-1234")

# ✅ Only need name and age, ignore rest
name, age, *_ = get_user_data()
print(f"{name} is {age}")

# Or with specific ignores:
name, age, _, _ = get_user_data()

# Clear which values are used vs ignored
```

**Directive Action**: Use `*_` or `_` for ignored values in unpacking.

---

### Edge Case 2: Variable-Length Unpacking

**Issue**: Structure has variable number of elements

**Handling**:
```python
# Use starred expression for variable-length part

def get_scores():
    """Return first, last, and middle scores."""
    return [95, 87, 90, 88, 92]

# ✅ Unpack first, last, and collect middle
first, *middle, last = get_scores()
print(f"First: {first}, Last: {last}, Middle: {middle}")
# First: 95, Last: 92, Middle: [87, 90, 88]

# Works with any number of middle elements
```

**Directive Action**: Use starred expressions (`*name`) for variable-length parts.

---

### Edge Case 3: Deeply Nested Structures

**Issue**: Very deep nesting makes unpacking hard to read

**Handling**:
```python
# Balance between unpacking depth and readability

def get_complex_data():
    """Return deeply nested structure."""
    return (1, (2, (3, (4, 5))))

# ❌ Too complex: Overly nested unpacking
a, (b, (c, (d, e))) = get_complex_data()

# ✅ Better: Partial unpacking
a, nested = get_complex_data()
b, more_nested = nested
c, innermost = more_nested
d, e = innermost

# Or: Flatten structure if possible
def get_flat_data():
    """Return flat structure."""
    return (1, 2, 3, 4, 5)

a, b, c, d, e = get_flat_data()
```

**Directive Action**: Limit unpacking depth to 2-3 levels for readability.

---

### Edge Case 4: Dictionary Unpacking for Function Args

**Issue**: Function takes many keyword arguments

**Handling**:
```python
# Use dictionary unpacking for keyword arguments

config = {
    'host': 'localhost',
    'port': 8080,
    'debug': True,
    'timeout': 30
}

# ✅ Unpack dictionary as keyword arguments
def connect(host, port, debug, timeout):
    """Connect to server."""
    return f"Connecting to {host}:{port} (debug={debug}, timeout={timeout})"

result = connect(**config)

# Clear and declarative
# All parameters named
# Easy to add/remove parameters
```

**Directive Action**: Use `**kwargs` unpacking for dictionaries as function arguments.

---

## Language-Specific Patterns

### Python

```python
# Tuple unpacking
x, y = (1, 2)

# List unpacking
a, b, c = [1, 2, 3]

# Extended unpacking (starred)
first, *middle, last = [1, 2, 3, 4, 5]

# Dictionary unpacking for function args
def foo(a, b, c):
    return a + b + c

kwargs = {'a': 1, 'b': 2, 'c': 3}
result = foo(**kwargs)

# Nested unpacking
(x, y), z = ((1, 2), 3)
```

### JavaScript/TypeScript

```javascript
// Array destructuring
const [x, y] = [1, 2];

// Object destructuring
const {name, age} = {name: "Alice", age: 30};

// Nested destructuring
const {user: {name, email}} = data;

// Rest parameters
const [first, ...rest] = [1, 2, 3, 4, 5];

// Default values
const {name = "Unknown", age = 0} = user;

// Renaming
const {name: userName, age: userAge} = user;
```

### Rust

```rust
// Tuple destructuring
let (x, y) = (1, 2);

// Struct destructuring
struct Point { x: i32, y: i32 }
let Point { x, y } = point;

// Match destructuring
match value {
    (x, y) => println!("x: {}, y: {}", x, y),
}

// Slice patterns
let [first, second, rest @ ..] = array;
```

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Unpacking doesn't change purity
- **Triggers**:
  - `fp_pattern_matching` - Unpacking often used with match
- **Called By**:
  - `project_file_write` - Apply unpacking before writing
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `uses_pattern_unpacking = 1` for functions using destructuring

**Tracking** (Optional - Disabled by Default):

If tracking is enabled:
- **`tracking_notes`** (user_preferences.db): Logs FP analysis with `note_type='fp_analysis'`

Only occurs when `fp_flow_tracking` is enabled via `tracking_toggle`.
Token overhead: ~5% per file write.
Most users will never enable this. It's for AIFP development and debugging only.

**Note**: When tracking is enabled, use helper functions from user_preferences helpers (e.g., `add_tracking_note`, `get_tracking_notes`, `search_tracking_notes`) to log FP analysis data. Never write SQL directly.
---
---

## Testing

How to verify this directive is working:

1. **Index access detected** → Directive converts to unpacking
   ```python
   # Before: x = tuple[0]; y = tuple[1]
   # After: x, y = tuple
   ```

2. **Nested access** → Directive uses nested unpacking
   ```python
   # Before: a = nested[0][1]
   # After: (x, (a, b)) = nested
   ```

3. **Check database** → Verify unpacking usage marked
   ```sql
   SELECT name, uses_pattern_unpacking
   FROM functions
   WHERE uses_pattern_unpacking = 1;
   ```

---

## Common Mistakes

- ❌ **Using index access for fixed structures** - Not declarative
- ❌ **Not using unpacking for multiple return values** - Less clear
- ❌ **Over-nesting destructuring** - Hard to read
- ❌ **Forgetting starred expressions** - Can't handle variable length
- ❌ **Not using meaningful names** - Defeats purpose of unpacking

---

## Roadblocks and Resolutions

### Roadblock 1: index_access_detected
**Issue**: Code uses [0], [1], etc. for fixed-position access
**Resolution**: Convert to tuple/list unpacking with named variables

### Roadblock 2: nested_structure
**Issue**: Multiple levels of indexing for nested data
**Resolution**: Use nested destructuring to extract all values declaratively

### Roadblock 3: variable_length_structure
**Issue**: Structure has variable number of elements
**Resolution**: Use starred expressions (*rest) for variable parts

### Roadblock 4: complex_dict_access
**Issue**: Repeated dictionary key access
**Resolution**: Use dictionary unpacking or convert to named tuple/dataclass

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for declarative pattern unpacking*
