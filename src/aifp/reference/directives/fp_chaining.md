# Directive: fp_chaining

**Type**: FP
**Level**: 2
**Parent Directive**: None
**Priority**: MEDIUM - Code clarity and composability

---

## Purpose

The `fp_chaining` directive **encourages chaining of small functions using pipeline or composition syntax**, improving clarity and composability in generated functional code. This directive is **important for code quality** because:

- **Readability**: Linear data flow easier to understand than nesting
- **Composability**: Functions naturally compose in pipelines
- **Refactoring**: Easy to add/remove steps in pipeline
- **Debugging**: Can inspect intermediate values in pipeline
- **AI generation**: AI can generate pipelines step-by-step

This directive creates:
- **Function pipelines** - Sequential data transformation
- **Method chains** - Fluent-style function chaining (FP variant)
- **Composition chains** - Right-to-left function composition
- **Monadic chains** - flatMap/bind chains for effects
- **Point-free style** - Functions composed without explicit parameters

**Chaining principle**: Transform nested calls into sequential pipelines.

---

## When to Apply

This directive applies when:
- **Nested function calls detected** - `f(g(h(x)))`
- **Sequential transformations** - Data processed through multiple steps
- **During compliance checks** - `project_compliance_check` suggests chaining
- **User requests pipeline** - "Use pipeline", "Chain functions"
- **Code generation** - AI creates multi-step transformations
- **Refactoring nested code** - Improve readability

---

## Workflow

### Trunk: analyze_function_calls

Analyzes function call patterns for chaining opportunities.

**Steps**:
1. **Parse call expressions** - Extract function call chains
2. **Identify nesting depth** - Count nested function calls
3. **Detect sequential patterns** - Find transformation sequences
4. **Route to chaining** - Convert to pipeline or composition

### Branches

**Branch 1: If independent_calls**
- **Then**: `convert_to_pipeline`
- **Details**: Convert sequential independent calls to pipeline
  - Independent call pattern:
    ```python
    # ❌ Sequential calls (verbose)
    data = load_data(filename)
    cleaned = clean_data(data)
    normalized = normalize_data(cleaned)
    filtered = filter_data(normalized)
    result = aggregate_data(filtered)
    ```
  - Pipeline conversion:
    ```python
    # ✅ Pipeline (clear data flow)
    from functools import reduce

    def pipe(initial, *functions):
        """Left-to-right pipeline"""
        return reduce(lambda acc, f: f(acc), functions, initial)

    result = pipe(
        filename,
        load_data,
        clean_data,
        normalize_data,
        filter_data,
        aggregate_data
    )

    # Or: Using |> operator (if language supports)
    # result = (filename
    #     |> load_data
    #     |> clean_data
    #     |> normalize_data
    #     |> filter_data
    #     |> aggregate_data)
    ```
  - Pipeline variations:
    - **Left-to-right (pipe)**: Read naturally, data flows forward
    - **Right-to-left (compose)**: Math notation, composition order
    - **Method chain**: `data.load().clean().normalize()`
  - Benefits:
    - Linear flow (top to bottom)
    - Easy to add/remove steps
    - Each step testable
    - Intermediate inspection possible
  

---

**Creating Reusable Composition:**
```python
# Initial code (repeated pipeline)
def process_users(data):
    parsed = parse_json(data)
    validated = validate_schema(parsed)
    transformed = transform_data(validated)
    return save_to_db(transformed)

def process_products(data):
    parsed = parse_json(data)
    validated = validate_schema(parsed)
    transformed = transform_data(validated)
    return save_to_db(transformed)

# AI calls: fp_chaining()

# Workflow:
# 1. analyze_function_calls:
#    - Same pipeline in multiple functions
#    - Composition opportunity
#
# 2. composition_pattern: use_compose
#    - Create reusable pipeline
#
# Refactored code (compliant)
def compose(*functions):
    from functools import reduce
    return reduce(
        lambda f, g: lambda x: f(g(x)),
        functions,
        lambda x: x
    )

# Reusable pipeline
standard_etl = compose(
    save_to_db,
    transform_data,
    validate_schema,
    parse_json
)

# Use in multiple places
def process_users(data):
    return standard_etl(data)

def process_products(data):
    return standard_etl(data)

# Or: Direct assignment
process_users = standard_etl
process_products = standard_etl

# Result:
# ✅ DRY (Don't Repeat Yourself)
# ✅ Reusable pipeline
# ✅ Composable and testable
```

---

**Creating Monadic Chain:**
```python
# Initial code (nested error handling)
def process_user_input(input_str):
    result = parse_user_input(input_str)
    if not result.success:
        return result

    validated = validate_user(result.data)
    if not validated.success:
        return validated

    saved = save_user(validated.data)
    return saved

# AI calls: fp_chaining()

# Workflow:
# 1. analyze_function_calls:
#    - Error handling pattern (Result type)
#    - Monadic chain opportunity
#
# 2. monadic_chain: create_flatmap_chain
#    - Use flatmap for elegant chaining
#
# Refactored code (compliant)
from dataclasses import dataclass
from typing import Union, TypeVar, Callable

T = TypeVar('T')

@dataclass(frozen=True)
class Ok:
    value: T

@dataclass(frozen=True)
class Err:
    error: str

Result = Union[Ok, Err]

def bind(result: Result, f: Callable[[any], Result]) -> Result:
    """Monadic bind (flatmap)"""
    return f(result.value) if isinstance(result, Ok) else result

def chain(*operations):
    """Chain monadic operations"""
    def chained(initial):
        result = initial
        for op in operations:
            result = bind(result, op)
        return result
    return chained

# Chained pipeline
process_user_input = chain(
    parse_user_input,
    validate_user,
    save_user
)

# Usage
result = process_user_input(input_str)

# Result:
# ✅ Elegant error propagation
# ✅ Linear flow
# ✅ Monadic composition
```

---

### ❌ Non-Compliant Usage

**Leaving Deeply Nested Calls:**
```python
# ❌ Deep nesting (hard to read)
result = f(g(h(i(j(k(x))))))

# Why Non-Compliant:
# - Hard to read (count parentheses)
# - Difficult to debug
# - Not composable
```

**Corrected:**
```python
# ✅ Pipeline
result = pipe(x, k, j, i, h, g, f)
```

---

## Edge Cases

### Edge Case 1: Functions with Multiple Arguments

**Issue**: Pipeline functions take >1 argument

**Handling**:
```python
# ❌ Multiple arguments break pipeline
def add(x, y):
    return x + y

# Can't pipe: add needs 2 args

# ✅ Solution: Curry or partial application
from functools import partial

add_five = partial(add, 5)

result = pipe(
    10,
    add_five,  # 10 + 5 = 15
    lambda x: x * 2  # 15 * 2 = 30
)
```

**Directive Action**: Use currying or lambdas for multi-arg functions.

---

### Edge Case 2: Conditional Logic in Pipeline

**Issue**: Pipeline needs branching

**Handling**:
```python
# ❌ Can't easily branch in pipeline
result = pipe(
    data,
    parse,
    # if valid then process_a else process_b?
    format
)

# ✅ Solution: Use Maybe/Option monad or conditional function
def conditional_process(data):
    return process_a(data) if is_valid(data) else process_b(data)

result = pipe(
    data,
    parse,
    conditional_process,
    format
)
```

**Directive Action**: Extract conditional logic to separate function.

---

### Edge Case 3: Side Effects in Pipeline

**Issue**: Pipeline step has side effect

**Handling**:
```python
# ❌ Side effect breaks purity
def log_and_process(data):
    print(f"Processing: {data}")  # Side effect
    return process(data)

# ✅ Solution: Use IO monad or separate logging
# Option 1: Separate side effects
def process_with_log(data, log_fn):
    log_fn(f"Processing: {data}")
    return process(data)

# Option 2: Return tuple (value, log messages)
def process_tracked(data):
    return (process(data), [f"Processing: {data}"])
```

**Directive Action**: Isolate side effects or use effect tracking.

---

## Related Directives

- **Called By**:
  - `project_file_write` - Suggests chaining for generated code
  - `project_compliance_check` - Recommends chaining for nested calls
  - User requests - "Create pipeline", "Chain functions"
- **Calls**:
  - Database helpers - Logs chaining transformations
  - `project_notes_log` - Documents pipeline creation
- **Related**:
  - `fp_currying` - Enables partial application in pipelines
  - `fp_monadic_composition` - Advanced chaining with effects
  - `fp_function_composition` - Related composition patterns

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.

---

## Database Operations

This directive updates the following tables:

- **`notes`**: INSERT chaining transformations and pipeline creation logs (only if `fp_flow_tracking` enabled - disabled by default)

---

## Testing

1. **Detect nesting** → Nested calls found
   ```python
   nested = detect_nested_calls("f(g(h(x)))")
   assert len(nested) == 3
   ```

2. **Convert to pipeline** → Pipeline code generated
   ```python
   pipeline = convert_to_pipeline(nested)
   assert "pipe(" in pipeline
   ```

3. **Already chained** → No changes needed
   ```python
   assert is_chained("pipe(x, f, g, h)") == True
   ```

---

## Common Mistakes

- ❌ **Over-chaining** - Too many steps hard to debug
- ❌ **Not handling errors** - Pipeline breaks on error
- ❌ **Complex pipelines** - Should extract to separate functions
- ❌ **Side effects in chain** - Breaks purity

---

## Roadblocks and Resolutions

### Roadblock 1: deep_nesting
**Issue**: Functions nested 5+ levels deep
**Resolution**: Flatten into chained composition

### Roadblock 2: redundant_calls
**Issue**: Same pipeline repeated
**Resolution**: Simplify chain, extract reusable composition

---

## References

None

---

*Part of AIFP v1.0 - FP directive for function chaining and pipeline creation*
