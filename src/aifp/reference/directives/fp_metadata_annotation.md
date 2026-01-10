# Directive: fp_metadata_annotation

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Enables AI introspection and function tracking

---

## Purpose

The `fp_metadata_annotation` directive adds structured metadata annotations to functions, enabling AI introspection, automatic indexing, and enhanced reasoning about code behavior. This directive provides **machine-readable function documentation** that makes code AI-friendly.

Metadata annotations provide **AI introspection**, enabling:
- **Automatic Indexing**: Functions automatically tracked in project.db
- **Dependency Analysis**: Call graphs generated from metadata
- **Purity Tracking**: Explicit purity level declarations
- **Theme/Flow Mapping**: Functions linked to project organization
- **AI Reasoning**: Context for AI decision-making

This directive acts as a **function metadata layer** bridging code and database tracking.

---

## When to Apply

This directive applies when:
- **Writing new functions** - Add metadata on creation
- **Refactoring existing code** - Update or add missing metadata
- **Project indexing** - Bulk metadata generation for existing codebase
- **FP compliance checking** - Metadata enables automated checks
- **Called by project directives**:
  - `project_file_write` - Add metadata before writing
  - `project_update_db` - Extract metadata for database
  - `fp_function_indexing` - Use metadata for indexing
  - Works with `fp_docstring_enforcement` - Complements docstrings

---

## Workflow

### Trunk: analyze_function_for_metadata

Analyzes function structure and generates appropriate AIFP metadata annotations.

**Steps**:
1. **Parse function signature** - Extract name, parameters, return type
2. **Analyze function body** - Detect purity, side effects, dependencies
3. **Determine metadata fields** - What information to annotate
4. **Generate metadata block** - Format as structured comment
5. **Insert metadata** - Place above function definition
6. **Validate metadata** - Ensure all required fields present

### Branches

**Branch 1: If function_missing_metadata**
- **Then**: `generate_and_insert_metadata`
- **Details**: Function has no AIFP metadata
  - Extract function information from AST
  - Analyze purity level (pure, IO, impure)
  - Identify dependencies (calls to other functions)
  - Determine theme/flow if applicable
  - Generate metadata comment block
  - Insert above function
- **Result**: Returns function with metadata

**Branch 2: If metadata_incomplete**
- **Then**: `update_existing_metadata`
- **Details**: Metadata present but missing fields
  - Parse existing metadata
  - Identify missing required fields
  - Analyze code to fill gaps
  - Update metadata in place
  - Preserve existing correct fields
- **Result**: Returns complete metadata

**Branch 3: If metadata_outdated**
- **Then**: `refresh_metadata`
- **Details**: Function changed, metadata stale
  - Compare metadata with current code
  - Detect discrepancies (purity changed, new dependencies)
  - Update metadata to match current state
  - Increment version if present
- **Result**: Returns refreshed metadata

**Branch 4: If metadata_compliant**
- **Then**: `mark_compliant`
- **Details**: Metadata is complete and accurate
  - All required fields present
  - Metadata matches code behavior
  - Format is correct
  - No action needed
- **Result**: Function passes check

**Fallback**: `prompt_user`
- **Details**: Unclear metadata requirements
  - Complex function with ambiguous classification
  - User-defined metadata fields requested
  - Ask user for clarification
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Complete Metadata (Passes):**

```python
# AIFP_METADATA
# function_name: calculate_total
# purity_level: pure
# parameters: items: list[float]
# return_type: float
# dependencies: []
# side_effects: none
# complexity: O(n)
# theme: calculations
# flow: invoice-processing
# version: 1.0
def calculate_total(items: list[float]) -> float:
    """Calculate total price of items."""
    return sum(items)

# ✅ Complete metadata
# ✅ All required fields present
# ✅ Accurate purity level
# ✅ AI can reason about this function
```

**Why Compliant**:
- All required metadata fields present
- Accurate purity classification (pure)
- Dependencies correctly listed (none)
- Theme and flow mapped
- Enables automatic indexing

---

**Metadata with Dependencies (Passes):**

```python
# AIFP_METADATA
# function_name: process_order
# purity_level: pure
# parameters: order: Order, tax_rate: float
# return_type: ProcessedOrder
# dependencies: [calculate_subtotal, calculate_tax, apply_discount]
# side_effects: none
# complexity: O(n)
# theme: order-processing
# flow: checkout
# version: 1.0
def process_order(order: Order, tax_rate: float) -> ProcessedOrder:
    """Process order with tax and discounts."""
    subtotal = calculate_subtotal(order.items)
    tax = calculate_tax(subtotal, tax_rate)
    discount = apply_discount(order.coupon, subtotal)
    total = subtotal + tax - discount

    return ProcessedOrder(
        order_id=order.id,
        subtotal=subtotal,
        tax=tax,
        discount=discount,
        total=total
    )

# ✅ Dependencies explicitly listed
# ✅ Enables call graph generation
# ✅ AI knows function composition
```

**Why Compliant**:
- Dependencies explicitly declared
- Enables automatic call graph generation
- Purity level accurately reflects behavior
- Theme and flow enable project organization

---

**IO Function Metadata (Passes):**

```python
# AIFP_METADATA
# function_name: read_config_file
# purity_level: IO
# parameters: file_path: str
# return_type: Result[Config, str]
# dependencies: [parse_config]
# side_effects: file_read
# complexity: O(n)
# theme: configuration
# flow: initialization
# version: 1.0
def read_config_file(file_path: str) -> Result[Config, str]:
    """Read and parse configuration file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return Ok(parse_config(content))
    except IOError as e:
        return Err(f"Failed to read config: {e}")

# ✅ Purity level correctly marked as IO
# ✅ Side effects explicitly documented
# ✅ Result type for error handling
```

**Why Compliant**:
- Correct purity level (IO, not pure)
- Side effects documented (file_read)
- Result type shows error handling
- Dependencies listed

---

### ❌ Non-Compliant Code

**Missing Metadata (Violation):**

```python
# ❌ VIOLATION: No metadata
def calculate_total(items: list[float]) -> float:
    """Calculate total price of items."""
    return sum(items)

# Problem:
# - No AIFP metadata present
# - Cannot be automatically indexed
# - AI has no context about purity
# - Dependencies not tracked
# - Not linked to theme/flow
```

**Why Non-Compliant**:
- No metadata annotation
- Cannot be indexed in project.db
- AI cannot reason about function properties
- No dependency tracking
- Missing theme/flow mapping

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Complete metadata added
# AIFP_METADATA
# function_name: calculate_total
# purity_level: pure
# parameters: items: list[float]
# return_type: float
# dependencies: []
# side_effects: none
# complexity: O(n)
# theme: calculations
# flow: invoice-processing
# version: 1.0
def calculate_total(items: list[float]) -> float:
    """Calculate total price of items."""
    return sum(items)

# Now AI can index and reason about function
```

---

**Incomplete Metadata (Violation):**

```python
# ❌ VIOLATION: Incomplete metadata
# AIFP_METADATA
# function_name: process_payment
# purity_level: IO
def process_payment(amount: float, card: str) -> bool:
    """Process payment transaction."""
    response = payment_gateway.charge(amount, card)
    return response.success

# Problem:
# - Missing parameters field
# - Missing return_type
# - Missing dependencies
# - Missing side_effects
# - Missing theme/flow
# - Incomplete metadata
```

**Why Non-Compliant**:
- Many required fields missing
- Cannot generate complete index
- Dependency tracking incomplete
- No theme/flow mapping

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Complete metadata
# AIFP_METADATA
# function_name: process_payment
# purity_level: IO
# parameters: amount: float, card: str
# return_type: Result[bool, str]
# dependencies: [payment_gateway.charge]
# side_effects: external_api_call
# complexity: O(1)
# theme: payments
# flow: checkout
# version: 1.0
def process_payment(amount: float, card: str) -> Result[bool, str]:
    """Process payment transaction."""
    try:
        response = payment_gateway.charge(amount, card)
        return Ok(response.success)
    except Exception as e:
        return Err(f"Payment failed: {e}")

# Complete metadata enables full tracking
```

---

**Incorrect Purity Level (Violation):**

```python
# ❌ VIOLATION: Incorrect purity level
# AIFP_METADATA
# function_name: save_user
# purity_level: pure  # ← WRONG! This has I/O
# parameters: user: User
# return_type: bool
# dependencies: []
# side_effects: none  # ← WRONG!
def save_user(user: User) -> bool:
    """Save user to database."""
    db.insert('users', user.to_dict())  # ← I/O operation
    return True

# Problem:
# - Marked as pure but performs I/O
# - Side effects not documented
# - Misleading metadata
# - AI will incorrectly classify function
```

**Why Non-Compliant**:
- Purity level incorrect (should be IO)
- Side effects not documented (should be database_write)
- Misleading information
- Breaks AI reasoning

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Correct metadata
# AIFP_METADATA
# function_name: save_user
# purity_level: IO
# parameters: user: User
# return_type: Result[bool, str]
# dependencies: []
# side_effects: database_write
# complexity: O(1)
# theme: users
# flow: registration
# version: 1.0
def save_user(user: User) -> Result[bool, str]:
    """Save user to database."""
    try:
        db.insert('users', user.to_dict())
        return Ok(True)
    except Exception as e:
        return Err(f"Failed to save user: {e}")

# Accurate metadata reflects true behavior
```

---

## Metadata Fields Reference

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| **function_name** | Exact function name | `calculate_total` |
| **purity_level** | Purity classification | `pure`, `IO`, `impure` |
| **parameters** | Function parameters with types | `items: list[float], tax: float` |
| **return_type** | Return type annotation | `float`, `Result[int, str]` |
| **dependencies** | Functions called by this function | `[calculate_tax, format_result]` |
| **side_effects** | Side effects present | `none`, `file_read`, `database_write` |

### Optional Fields

| Field | Description | Example |
|-------|-------------|---------|
| **complexity** | Big-O complexity | `O(n)`, `O(n log n)`, `O(1)` |
| **theme** | Project theme | `authentication`, `payments` |
| **flow** | Project flow | `checkout`, `registration` |
| **version** | Function version | `1.0`, `2.1` |
| **tags** | Custom tags | `critical`, `tested`, `deprecated` |
| **author** | Original author | `alice`, `ai-claude` |

---

## Purity Level Classification

### pure
- No side effects
- Deterministic (same inputs → same outputs)
- No I/O operations
- No external state access
- Can be memoized

**Example**: `add(x, y) -> x + y`

### IO
- Performs I/O operations
- May fail (file not found, network error)
- Should return Result type
- Isolated from pure logic
- Side effects documented

**Example**: `read_file(path) -> Result[str, str]`

### impure
- Has side effects beyond I/O
- Accesses or modifies external state
- Non-deterministic behavior
- Should be refactored to pure + IO boundaries

**Example**: `increment_global_counter() -> int` (should be refactored)

---

## Edge Cases

### Edge Case 1: Lambda Functions

**Issue**: Lambdas are anonymous, how to annotate?

**Handling**:
```python
# For inline lambdas, no metadata needed (covered by parent function)
numbers = [1, 2, 3, 4, 5]
evens = list(filter(lambda x: x % 2 == 0, numbers))

# For assigned lambdas, use metadata
# AIFP_METADATA
# function_name: is_even
# purity_level: pure
# parameters: x: int
# return_type: bool
# dependencies: []
# side_effects: none
is_even = lambda x: x % 2 == 0

# Or better: convert to named function
def is_even(x: int) -> bool:
    """Check if number is even."""
    return x % 2 == 0
```

**Directive Action**: Encourage converting lambdas to named functions for metadata.

---

### Edge Case 2: Higher-Order Functions

**Issue**: Function takes or returns functions

**Handling**:
```python
# AIFP_METADATA
# function_name: compose
# purity_level: pure
# parameters: f: Callable[[B], C], g: Callable[[A], B]
# return_type: Callable[[A], C]
# dependencies: []
# side_effects: none
# complexity: O(1)
# note: Returns composed function, purity depends on f and g
def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Compose two functions: compose(f, g)(x) == f(g(x))."""
    def composed(x: A) -> C:
        return f(g(x))
    return composed

# Metadata documents that purity is context-dependent
```

**Directive Action**: Document that returned function purity depends on inputs.

---

### Edge Case 3: Recursive Functions

**Issue**: Function calls itself

**Handling**:
```python
# AIFP_METADATA
# function_name: factorial
# purity_level: pure
# parameters: n: int
# return_type: int
# dependencies: [factorial]  # ← Self-reference
# side_effects: none
# complexity: O(n)
# recursion: tail_recursive
def factorial(n: int, acc: int = 1) -> int:
    """Calculate factorial using tail recursion."""
    if n <= 1:
        return acc
    return factorial(n - 1, acc * n)

# List function itself in dependencies
# Add recursion field for tail-recursion optimization
```

**Directive Action**: List self in dependencies; add recursion field if applicable.

---

## Language-Specific Metadata Formats

### Python

```python
# AIFP_METADATA
# field: value
# field: value
def function_name():
    pass
```

### JavaScript/TypeScript

```javascript
// AIFP_METADATA
// field: value
// field: value
function functionName() {}
```

### Rust

```rust
// AIFP_METADATA
// field: value
// field: value
fn function_name() {}
```

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Determines purity_level field
  - `fp_side_effect_detection` - Identifies side_effects
- **Triggers**:
  - `fp_function_indexing` - Uses metadata for indexing
  - `project_update_db` - Extracts metadata to database
- **Called By**:
  - `project_file_write` - Add metadata before writing
  - Works with `fp_docstring_enforcement` - Complements docstrings
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: Populates fields from metadata (purity_level, parameters, return_type, dependencies_json, side_effects_json)
- **`interactions`**: Creates entries from dependencies list
- **`notes`**: Logs metadata generation with `note_type = 'metadata'`

---

## Testing

How to verify this directive is working:

1. **Function without metadata** → Directive generates and inserts metadata
   ```python
   # Before: def add(x, y): return x + y
   # After: Has AIFP_METADATA block with all fields
   ```

2. **Metadata extraction** → Check database populated
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

3. **Dependency tracking** → Verify interactions table
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Common Mistakes

- ❌ **Incorrect purity classification** - Marking IO functions as pure
- ❌ **Missing dependencies** - Not listing all function calls
- ❌ **Incomplete metadata** - Missing required fields
- ❌ **Stale metadata** - Function changed but metadata not updated
- ❌ **Wrong side effects** - Not documenting I/O operations

---

## Roadblocks and Resolutions

### Roadblock 1: function_missing_metadata
**Issue**: Function has no AIFP metadata annotation
**Resolution**: Generate complete metadata block from function analysis and insert above definition

### Roadblock 2: metadata_incomplete
**Issue**: Metadata present but missing required fields
**Resolution**: Analyze code to fill missing fields while preserving existing correct data

### Roadblock 3: metadata_outdated
**Issue**: Function changed, metadata no longer accurate
**Resolution**: Re-analyze function and update metadata to reflect current state

### Roadblock 4: complex_dependencies
**Issue**: Complex dependency graph difficult to represent
**Resolution**: List direct dependencies only; transitive dependencies computed by call graph analysis

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for function metadata annotation*
