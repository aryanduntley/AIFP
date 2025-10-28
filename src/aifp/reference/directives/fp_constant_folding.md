# Directive: fp_constant_folding

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: LOW - Compile-time optimization

---

## Purpose

The `fp_constant_folding` directive simplifies constant expressions and evaluates literals during code generation to reduce runtime overhead. This directive performs **compile-time evaluation** of constant expressions, transforming computations from runtime to generation-time.

Constant folding provides **zero-cost abstractions**, enabling:
- **Compile-Time Evaluation**: Calculate constant expressions during code generation
- **Runtime Performance**: Eliminate redundant calculations at runtime
- **Zero Overhead**: Constants cost nothing at runtime
- **Maintained Readability**: Symbolic constants for clarity, literal values for performance
- **Safe Optimization**: Pure functions enable safe compile-time evaluation

This directive leverages FP purity to enable aggressive compile-time optimizations that would be unsafe in imperative code.

---

## When to Apply

This directive applies when:
- **Constant arithmetic expressions** - `3 * 7 + 2` → `23`
- **Constant string concatenation** - `"Hello, " + "World"` → `"Hello, World"`
- **Constant boolean expressions** - `True and False` → `False`
- **Pure function calls on constants** - `len("hello")` → `5`
- **Configuration constants** - Combine config values at compile time
- **Called by project directives**:
  - `project_file_write` - Fold constants before writing code
  - Works with `fp_function_inlining` - Inline then fold constants
  - Works with `fp_purity` - Only fold pure expressions

---

## Workflow

### Trunk: detect_constant_expressions

Scans code to identify expressions that can be evaluated at compile time.

**Steps**:
1. **Parse expressions** - Build AST for all expressions
2. **Identify constant literals** - Find numeric, string, boolean literals
3. **Detect constant operations** - Find operations on constants
4. **Verify purity** - Ensure expressions are pure (deterministic, no side effects)
5. **Evaluate at compile time** - Compute constant results
6. **Replace with literals** - Substitute expressions with evaluated values

### Branches

**Branch 1: If constant_arithmetic**
- **Then**: `evaluate_and_replace`
- **Details**: Evaluate arithmetic on constants
  - `2 + 3 * 4` → `14`
  - `10 / 2 - 1` → `4`
  - `2 ** 10` → `1024`
  - Replace expression with computed literal
- **Result**: Returns literal value

**Branch 2: If constant_string_operations**
- **Then**: `fold_string_constants`
- **Details**: Evaluate string operations at compile time
  - `"Hello, " + "World"` → `"Hello, World"`
  - `"test" * 3` → `"testtesttest"`
  - `len("hello")` → `5`
  - Replace with literal result
- **Result**: Returns string literal

**Branch 3: If constant_boolean_logic**
- **Then**: `simplify_boolean_expression`
- **Details**: Simplify boolean logic at compile time
  - `True and False` → `False`
  - `True or anything` → `True`
  - `not False` → `True`
  - Replace with boolean literal
- **Result**: Returns boolean literal

**Branch 4: If pure_function_on_constants**
- **Then**: `evaluate_pure_function`
- **Details**: Call pure function at compile time
  - `len([1, 2, 3])` → `3`
  - `max(5, 10, 3)` → `10`
  - `abs(-42)` → `42`
  - Verify function is pure, evaluate, replace with result
- **Result**: Returns computed literal

**Branch 5: If symbolic_constant_preferred**
- **Then**: `keep_symbolic`
- **Details**: Keep symbolic constant for readability
  - `PI * 2` kept as expression (PI is meaningful)
  - Named constants provide documentation
  - Don't fold if readability harmed
- **Result**: Expression kept symbolic

**Fallback**: `prompt_user`
- **Details**: Uncertain about folding
  - Present expression and potential folding
  - Ask: "Fold this constant expression?"
  - Consider readability tradeoff
- **Result**: User decides

---

## Examples

### ✅ Compliant Code

**Folded Arithmetic (Passes):**
```python
# BEFORE: Constant arithmetic at runtime
BUFFER_SIZE = 1024 * 1024 * 10  # 10 MB

# AFTER: Folded at compile time
BUFFER_SIZE = 10485760  # 10 MB (pre-computed)

# Why folded:
# - Pure arithmetic on constants
# - No runtime overhead
# - Same meaning, faster execution
```

**Why Compliant**:
- Constant expression evaluated at compile time
- Zero runtime cost
- Maintains meaning

---

**Folded String Concatenation (Passes):**
```python
# BEFORE: String concatenation at runtime
ERROR_PREFIX = "ERROR: " + "[" + get_timestamp() + "] "  # Partially constant

# AFTER: Folded constant parts
ERROR_PREFIX_CONST = "ERROR: ["  # Folded
ERROR_PREFIX = ERROR_PREFIX_CONST + get_timestamp() + "] "  # Variable part remains

# Why folded:
# - "ERROR: " + "[" is constant (folded to "ERROR: [")
# - get_timestamp() is non-constant (kept as call)
# - Partial folding reduces runtime concatenation
```

**Why Compliant**:
- Constant portions folded
- Non-constant portions kept
- Optimal performance

---

**Symbolic Constants Kept (Passes):**
```python
# KEPT SYMBOLIC: Mathematical constants for readability
import math

CIRCLE_AREA = math.PI * RADIUS ** 2  # Kept symbolic

# Why NOT folded:
# - PI is symbolic constant (meaningful)
# - Expression documents intent ("pi times radius squared")
# - Readability more important than micro-optimization
# - Compiler/runtime can optimize anyway

# VERDICT: Keep symbolic for clarity
```

**Why Compliant**:
- Readability prioritized
- Symbolic constants provide meaning
- Optimization deferred to compiler

---

**Partial Folding (Passes):**
```python
# BEFORE: Mixed constant and variable
MAX_RETRIES = 3
RETRY_DELAY_MS = 1000 * MAX_RETRIES  # Constant

def retry_operation(operation):
    for attempt in range(MAX_RETRIES):  # Variable
        try:
            return operation()
        except:
            time.sleep(RETRY_DELAY_MS / 1000)  # Partially constant

# AFTER: Constants folded
MAX_RETRIES = 3
RETRY_DELAY_MS = 3000  # Folded: 1000 * 3

def retry_operation(operation):
    for attempt in range(3):  # Folded: MAX_RETRIES
        try:
            return operation()
        except:
            time.sleep(3.0)  # Folded: 3000 / 1000

# Why folded:
# - MAX_RETRIES is constant (3)
# - RETRY_DELAY_MS is constant expression (folded to 3000)
# - Division by 1000 is constant (folded to 3.0)
```

**Why Compliant**:
- All constant expressions folded
- Variable parts kept
- Optimal performance

---

### ❌ Non-Compliant Code

**Missed Constant Folding (Suboptimal):**
```python
# ❌ SUBOPTIMAL: Constants not folded
# Current code
def allocate_buffer():
    # Computed at EVERY call (wasteful)
    size = 1024 * 1024 * 10  # ← Runtime calculation
    return bytearray(size)

# Called frequently
for i in range(1000):
    buffer = allocate_buffer()  # Calculates 1024*1024*10 1000 times!

# Problem:
# - Constant expression evaluated at runtime
# - 1000 redundant multiplications
# - Wasted CPU cycles
```

**Why Non-Compliant**:
- Constant not folded (evaluated at runtime)
- Redundant computation
- Performance waste

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Constant folded
BUFFER_SIZE = 10485760  # Folded: 1024 * 1024 * 10

def allocate_buffer():
    return bytearray(BUFFER_SIZE)  # Literal lookup (instant)

# Called frequently
for i in range(1000):
    buffer = allocate_buffer()  # No multiplication (just loads constant)
```

---

**Folding Non-Pure Expression (Violation):**
```python
# ❌ VIOLATION: Attempting to fold non-pure expression
# BEFORE:
def get_config_value():
    # Folded incorrectly (value can change!)
    return "database_" + get_environment()  # ← Non-deterministic

# ❌ AFTER: Incorrectly folded
def get_config_value():
    return "database_production"  # ← WRONG if environment changes!

# Problem:
# - get_environment() is non-pure (can return different values)
# - Folding freezes value to "production"
# - Breaks in dev/staging environments
# - Violates correctness
```

**Why Non-Compliant**:
- Non-pure expression folded
- Loss of dynamic behavior
- Breaks correctness
- Only fold pure expressions!

**Resolution**: Don't fold non-pure expressions:
```python
# ✅ FIXED: Keep non-pure expression
def get_config_value():
    # NOT folded (get_environment() is non-pure)
    return "database_" + get_environment()  # Evaluated at runtime
```

---

**Over-Folding Harms Readability (Violation):**
```python
# ❌ VIOLATION: Over-aggressive folding loses meaning
# BEFORE: Clear symbolic constants
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
SECONDS_PER_DAY = SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY

# ❌ AFTER: Folded to magic number
SECONDS_PER_DAY = 86400  # What does 86400 mean? Lost clarity!

# Problem:
# - Symbolic constants provide meaning
# - 86400 is "magic number" (unclear)
# - Original expression documents calculation
# - Readability lost for micro-optimization
```

**Why Non-Compliant**:
- Over-folding loses readability
- Magic numbers harder to understand
- Symbolic constants are self-documenting
- Micro-optimization not worth clarity loss

**Resolution**: Keep symbolic for clarity:
```python
# ✅ FIXED: Keep symbolic constants
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
SECONDS_PER_DAY = SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY

# Self-documenting (clear what 86400 represents)
# Compiler can optimize anyway
```

---

## Edge Cases

### Edge Case 1: Floating Point Precision

**Issue**: Folding floating point may change precision

**Handling**:
```python
# Be careful with floating point folding
# BEFORE:
result = 0.1 + 0.2  # Floating point arithmetic

# AFTER: Folded
result = 0.30000000000000004  # Exact folded value (precision exposed)

# Issue: Folding may expose floating point precision quirks
# Resolution: Fold carefully, test numerical stability
```

**Directive Action**: Fold floating point constants but verify precision preservation.

---

### Edge Case 2: Large Constant Arrays

**Issue**: Folding large arrays increases code size

**Handling**:
```python
# Don't fold large constant collections
# BEFORE:
PRIMES = [p for p in range(2, 10000) if is_prime(p)]  # Generate at runtime

# DON'T fold to:
# PRIMES = [2, 3, 5, 7, 11, 13, ...] # 1000+ element literal (huge code size)

# KEEP AS: Runtime generation or external data file
# Code size vs runtime tradeoff
```

**Directive Action**: Don't fold large constants (use runtime generation or external data).

---

### Edge Case 3: Platform-Dependent Constants

**Issue**: Constant value may differ by platform

**Handling**:
```python
# Don't fold platform-dependent constants
# BEFORE:
import sys
PTR_SIZE = 8 if sys.maxsize > 2**32 else 4  # Platform-dependent

# DON'T fold (value depends on platform at runtime)
# KEEP AS: Runtime evaluation

# Fold only truly constant expressions
```

**Directive Action**: Don't fold platform-dependent or runtime-determined values.

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Only fold pure expressions
  - `fp_immutability` - Folded values must be immutable
- **Triggers**:
  - May follow `fp_function_inlining` - Inline then fold resulting constants
- **Called By**:
  - `project_file_write` - Fold constants before writing code
- **Conflicts With**:
  - Readability - Don't over-fold symbolic constants
- **Escalates To**: None

---

## Helper Functions Used

- `detect_constant_expressions(ast: AST) -> list[ConstExpr]` - Finds constant expressions
- `verify_expression_purity(expr: Expression) -> bool` - Checks if expression is pure
- `evaluate_constant_expression(expr: Expression) -> Literal` - Evaluates at compile time
- `replace_with_literal(code: str, expr: Expression, value: Literal) -> str` - Replaces expression
- `update_functions_table(func_id: int, has_folded_constants: bool)` - Updates project.db

---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `optimization_level = 'constant_folded'` for optimized code
- **`notes`**: Logs constant folding with `note_type = 'optimization'`

---

## Testing

How to verify this directive is working:

1. **Write constant expression** → Directive folds
   ```python
   # Input
   SIZE = 1024 * 1024

   # Output: Folded
   SIZE = 1048576
   ```

2. **Write symbolic constant** → Directive keeps symbolic
   ```python
   # Input
   AREA = PI * radius ** 2

   # Output: Kept symbolic (PI is meaningful)
   AREA = PI * radius ** 2
   ```

3. **Write non-pure expression** → Directive doesn't fold
   ```python
   # Input
   value = get_config() + "suffix"

   # Output: Not folded (get_config() is non-pure)
   value = get_config() + "suffix"
   ```

---

## Common Mistakes

- ❌ **Folding non-pure expressions** - Changes program behavior
- ❌ **Over-folding symbolic constants** - Loses readability
- ❌ **Folding platform-dependent values** - Breaks cross-platform compatibility
- ❌ **Folding large arrays** - Bloats code size
- ❌ **Folding before verifying purity** - Unsafe optimization

---

## Roadblocks and Resolutions

### Roadblock 1: non_pure_expression
**Issue**: Expression contains non-pure function calls
**Resolution**: Don't fold, keep as runtime evaluation

### Roadblock 2: symbolic_constant_clarity
**Issue**: Folding loses self-documenting symbolic constant
**Resolution**: Keep symbolic for readability

### Roadblock 3: platform_dependent_value
**Issue**: Constant value depends on platform
**Resolution**: Don't fold, evaluate at runtime

### Roadblock 4: code_size_bloat
**Issue**: Folding large constant increases code size
**Resolution**: Don't fold, use runtime generation or external data

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-constant-folding)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#optimization)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for compile-time constant evaluation*
