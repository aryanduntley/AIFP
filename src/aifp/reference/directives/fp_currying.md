# Directive: fp_currying

**Type**: FP
**Level**: 2
**Parent Directive**: None
**Priority**: MEDIUM - Advanced functional pattern

---

## Purpose

The `fp_currying` directive **refactors functions with multiple parameters into curried, single-argument forms** for partial application and higher-order reuse of generated functions. This directive is **powerful for composability** because:

- **Partial application**: Create specialized functions by fixing some arguments
- **Function composition**: Curried functions compose naturally
- **Flexibility**: Build complex functions from simple building blocks
- **Point-free style**: Enable function composition without explicit parameters
- **Reusability**: One function generates many specialized variants

This directive creates:
- **Curried functions** - `f(x)(y)(z)` instead of `f(x, y, z)`
- **Partially applied functions** - Fix some arguments, return function awaiting rest
- **Function factories** - Create specialized functions from general ones
- **Composable pipelines** - Curried functions fit into pipelines naturally

**Currying principle**: Transform `f(a, b, c)` into `f(a)(b)(c)` for maximum flexibility.

---

## When to Apply

This directive applies when:
- **Multi-argument function detected** - Function takes 2+ parameters
- **Partial application needed** - Want to fix some arguments
- **Function composition desired** - Need unary functions for composition
- **User requests currying** - "Curry function", "Enable partial application"
- **During code generation** - AI creates reusable function variants
- **Higher-order functions** - Building function factories

---

## Workflow

### Trunk: inspect_function_signature

Inspects function signatures for currying opportunities.

**Steps**:
1. **Parse function parameters** - Extract parameter list
2. **Analyze parameter dependencies** - Check if currying makes sense
3. **Determine curry strategy** - Auto-curry or manual curry
4. **Route to transformation** - Generate curried version

### Branches

**Branch 1: If multi_argument_function**
- **Then**: `transform_to_curried`
- **Details**: Convert multi-parameter function to curried form
  - Multi-argument pattern:
    ```python
    # ❌ Standard function (not curried)
    def add(x, y):
        return x + y

    result = add(5, 3)  # Must provide all arguments
    ```
  - Curried form:
    ```python
    # ✅ Curried function
    def add(x):
        def inner(y):
            return x + y
        return inner

    # Usage
    result = add(5)(3)  # 8

    # Or: Partial application
    add_five = add(5)  # Specialized function
    result1 = add_five(3)  # 8
    result2 = add_five(10)  # 15
    ```
  - Automatic currying decorator:
    ```python
    # ✅ Auto-curry with decorator
    def curry(f):
        """Automatically curry a function"""
        from functools import wraps
        import inspect

        @wraps(f)
        def curried(*args):
            sig = inspect.signature(f)
            params = list(sig.parameters.values())

            if len(args) >= len(params):
                # All arguments provided
                return f(*args)
            else:
                # Partial application
                def partial(*more_args):
                    return curried(*(args + more_args))
                return partial

        return curried

    @curry
    def add(x, y):
        return x + y

    # Usage
    result = add(5)(3)  # Curried: 8
    result = add(5, 3)  # Direct: 8
    add_five = add(5)  # Partial: function
    ```
  - Currying strategies:
    - **Manual curry**: Explicit nested functions
    - **Auto-curry**: Decorator handles currying automatically
    - **Partial application**: Use `functools.partial` (Python)
  - Benefits:
    - Flexible function usage
    - Create specialized variants
    - Pipeline-friendly
- **Result**: Function curried

**Branch 2: If partial_application_opportunity**
- **Then**: `create_partial_variants`
- **Details**: Generate commonly used partial applications
  - Common partial application pattern:
    ```python
    # ❌ Repeated arguments
    def multiply(x, y):
        return x * y

    double1 = multiply(2, 5)  # 10
    double2 = multiply(2, 10)  # 20
    double3 = multiply(2, 15)  # 30
    # First argument always 2!
    ```
  - Partial application:
    ```python
    # ✅ Partial application
    from functools import partial

    def multiply(x, y):
        return x * y

    # Create specialized function
    double = partial(multiply, 2)

    # Usage
    result1 = double(5)  # 10
    result2 = double(10)  # 20
    result3 = double(15)  # 30

    # Or: Curried version
    def multiply(x):
        return lambda y: x * y

    double = multiply(2)
    triple = multiply(3)
    ```
  - Common partial applications:
    - `map(f, xs)` → `map_with_f = partial(map, f)`
    - `filter(pred, xs)` → `filter_with_pred = partial(filter, pred)`
    - `reduce(op, xs, init)` → `reduce_with_op = partial(reduce, op)`
  - Benefits:
    - Reduce repetition
    - Create domain-specific functions
    - Self-documenting code
- **Result**: Partial variants created

**Branch 3: If parameter_reordering_needed**
- **Then**: `reorder_for_currying`
- **Details**: Reorder parameters to enable useful partial application
  - Parameter order matters for currying:
    ```python
    # ❌ Bad parameter order (variable comes first)
    def divide(numerator, denominator):
        return numerator / denominator

    # Partial application not useful
    divide_by_x = partial(divide, ???)  # Numerator varies!

    # ✅ Good parameter order (constant comes first)
    def divide(denominator, numerator):
        return numerator / denominator

    # Useful partial application
    halve = partial(divide, 2)  # Divide by 2
    result = halve(10)  # 5
    ```
  - Parameter ordering principle:
    - **Most general first**: Parameters that vary least
    - **Most specific last**: Parameters that vary most
    - **Configuration first**: Setup/config parameters
    - **Data last**: Actual data to process
  - Examples:
    - `map(function, iterable)` - function first (more general)
    - `filter(predicate, iterable)` - predicate first
    - `reduce(function, iterable, initial)` - function first
  - Refactoring:
    ```python
    # Before: Data first
    def process(data, config, formatter):
        validated = validate(data, config)
        return formatter(validated)

    # After: Config first, data last
    def process(config, formatter, data):
        validated = validate(data, config)
        return formatter(validated)

    # Now useful partial application
    process_with_config = partial(process, my_config, my_formatter)
    result = process_with_config(data)
    ```
- **Result**: Parameters reordered for useful currying

**Branch 4: If already_curried**
- **Then**: `mark_as_compliant`
- **Details**: Function already in curried form
  - Curried patterns:
    - Nested single-parameter functions
    - Using curry decorator
    - Manually curried
  - No refactoring needed
- **Result**: Function validated as curried

**Fallback**: `prompt_user`
- **Details**: Unclear if currying makes sense
  - When to prompt:
    - Function has complex parameter dependencies
    - Parameters can't be meaningfully separated
    - Currying would reduce readability
  - Prompt example:
    ```
    Currying opportunity detected

    Function: calculate(x, y, z)
    Parameters: x (number), y (number), z (config)

    Suggested curried form:
    calculate(z)(x)(y)  # Config first, data last

    Apply currying? (y/n):
    Alternative: Use partial() instead? (y/n):
    ```
- **Result**: User decides currying approach

---

## Examples

### ✅ Compliant Usage

**Currying Multi-Argument Function:**
```python
# Initial code (not curried)
def add(x, y):
    return x + y

result = add(5, 3)  # Must provide both arguments

# AI calls: fp_currying()

# Workflow:
# 1. inspect_function_signature:
#    - Function has 2 parameters
#    - Simple parameter dependencies
#
# 2. multi_argument_function: transform_to_curried
#    - Convert to curried form
#
# Refactored code (compliant)
# Manual curry
def add(x):
    return lambda y: x + y

# Usage
result = add(5)(3)  # 8

# Partial application
add_five = add(5)
result1 = add_five(3)  # 8
result2 = add_five(10)  # 15

# Or: Auto-curry with decorator
def curry(f):
    from functools import wraps
    import inspect

    @wraps(f)
    def curried(*args):
        sig = inspect.signature(f)
        n_params = len(sig.parameters)

        if len(args) >= n_params:
            return f(*args)
        else:
            return lambda *more: curried(*(args + more))

    return curried

@curry
def add(x, y):
    return x + y

# Both work
result = add(5)(3)  # Curried: 8
result = add(5, 3)  # Direct: 8

# Result:
# ✅ Function curried
# ✅ Partial application enabled
# ✅ Flexible usage
```

---

**Creating Useful Partial Applications:**
```python
# Initial code (repeated arguments)
def format_price(price, currency, decimal_places):
    return f"{currency}{price:.{decimal_places}f}"

# Usage with repeated arguments
usd_price1 = format_price(19.99, "$", 2)
usd_price2 = format_price(29.99, "$", 2)
usd_price3 = format_price(39.99, "$", 2)
# Currency and decimals always "$" and 2!

# AI calls: fp_currying()

# Workflow:
# 1. inspect_function_signature:
#    - Repeated arguments detected: currency="$", decimal_places=2
#
# 2. partial_application_opportunity: create_partial_variants
#    - Create USD formatter
#
# Refactored code (compliant)
from functools import partial

def format_price(currency, decimal_places, price):
    # Reordered: config first, data last
    return f"{currency}{price:.{decimal_places}f}"

# Create specialized formatters
format_usd = partial(format_price, "$", 2)
format_eur = partial(format_price, "€", 2)
format_jpy = partial(format_price, "¥", 0)  # No decimal for JPY

# Usage (cleaner)
usd_price1 = format_usd(19.99)  # "$19.99"
usd_price2 = format_usd(29.99)  # "$29.99"
eur_price = format_eur(49.99)  # "€49.99"
jpy_price = format_jpy(1500)  # "¥1500"

# Result:
# ✅ Partial application useful
# ✅ Domain-specific formatters created
# ✅ Reduced repetition
```

---

**Reordering Parameters for Currying:**
```python
# Initial code (bad parameter order)
def map_and_filter(data, mapper, predicate):
    mapped = [mapper(x) for x in data]
    filtered = [x for x in mapped if predicate(x)]
    return filtered

# Data comes first - not ideal for partial application

# AI calls: fp_currying()

# Workflow:
# 1. inspect_function_signature:
#    - Parameter order: data, mapper, predicate
#    - Data varies most (should be last)
#
# 2. parameter_reordering_needed: reorder_for_currying
#    - Reorder: mapper, predicate, data
#
# Refactored code (compliant)
def map_and_filter(mapper, predicate, data):
    # Reordered: config first, data last
    mapped = [mapper(x) for x in data]
    filtered = [x for x in mapped if predicate(x)]
    return filtered

# Now useful partial application
from functools import partial

# Create specialized pipeline
process_numbers = partial(
    map_and_filter,
    lambda x: x * 2,  # Mapper: double
    lambda x: x > 10  # Predicate: > 10
)

# Use with different data
result1 = process_numbers([1, 5, 10, 15])  # [20, 30]
result2 = process_numbers([3, 6, 9, 12])  # [12, 18, 24]

# Or: Curried version
def map_and_filter(mapper):
    return lambda predicate: lambda data: [
        x for x in map(mapper, data) if predicate(x)
    ]

# Build pipeline step by step
double = map_and_filter(lambda x: x * 2)
double_and_filter = double(lambda x: x > 10)
result = double_and_filter([1, 5, 10, 15])  # [20, 30]

# Result:
# ✅ Parameters in optimal order
# ✅ Partial application useful
# ✅ Reusable pipelines
```

---

### ❌ Non-Compliant Usage

**Not Currying When Beneficial:**
```python
# ❌ Not curried (missed opportunity)
def multiply(x, y):
    return x * y

# Repeated first argument
double1 = multiply(2, 5)
double2 = multiply(2, 10)
double3 = multiply(2, 15)

# Why Non-Compliant:
# - Should curry or use partial
# - Repetition not eliminated
```

**Corrected:**
```python
# ✅ Curried or partial
from functools import partial

def multiply(x, y):
    return x * y

double = partial(multiply, 2)
result1 = double(5)
result2 = double(10)
result3 = double(15)
```

---

## Edge Cases

### Edge Case 1: Functions with Default Arguments

**Issue**: Default arguments complicate currying

**Handling**:
```python
# Default arguments
def format_text(text, prefix="", suffix=""):
    return f"{prefix}{text}{suffix}"

# Curry with defaults
def format_text(prefix=""):
    return lambda suffix="": lambda text: f"{prefix}{text}{suffix}"

# Usage
add_brackets = format_text("[")("]")
result = add_brackets("hello")  # "[hello]"
```

**Directive Action**: Handle defaults in curried form carefully.

---

### Edge Case 2: Variable-Length Arguments (*args)

**Issue**: *args don't curry well

**Handling**:
```python
# ❌ Varargs don't curry cleanly
def sum_all(*numbers):
    return sum(numbers)

# ✅ Solution: Don't curry varargs functions
# Or: Convert to explicit list parameter
def sum_all(numbers):
    return sum(numbers)

# Now can curry if needed
def sum_with_initial(initial):
    return lambda numbers: initial + sum(numbers)
```

**Directive Action**: Avoid currying varargs functions.

---

### Edge Case 3: Method Currying

**Issue**: Methods have implicit self parameter

**Handling**:
```python
# ❌ Method (has self)
class Calculator:
    def add(self, x, y):
        return x + y

# ✅ Curry as standalone function
def add(x):
    return lambda y: x + y

# Or: Use functools.partial with bound method
from functools import partial
calc = Calculator()
add_five = partial(calc.add, 5)
```

**Directive Action**: Extract methods to standalone functions for currying.

---

## Related Directives

- **Called By**:
  - `fp_chaining` - Curried functions fit in pipelines
  - `project_file_write` - Generate curried functions
  - User requests - "Curry function", "Enable partial application"
- **Calls**:
  - Database helpers - Logs currying transformations
  - `project_notes_log` - Documents currying decisions
- **Related**:
  - `fp_function_composition` - Curried functions compose naturally
  - `fp_chaining` - Currying enables pipeline building
  - `fp_higher_order_functions` - Currying creates HOFs

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`notes`**: INSERT currying transformations and partial application creation logs

---

## Testing

1. **Detect multi-param function** → Function has 2+ parameters
   ```python
   assert get_param_count(add) == 2
   ```

2. **Generate curried version** → Curried code created
   ```python
   curried = generate_curried_version(add)
   assert "lambda" in curried or "def inner" in curried
   ```

3. **Already curried** → No changes needed
   ```python
   def curried_add(x):
       return lambda y: x + y
   assert is_curried(curried_add) == True
   ```

---

## Common Mistakes

- ❌ **Currying everything** - Not all functions benefit from currying
- ❌ **Wrong parameter order** - Data should come last
- ❌ **Currying varargs** - *args don't curry well
- ❌ **Over-complicating simple functions** - Sometimes direct call is clearer

---

## Roadblocks and Resolutions

### Roadblock 1: parameter_dependency
**Issue**: Parameters depend on each other in complex ways
**Resolution**: Reorder for partial application or use partial() instead of full curry

---

## References

None
---

*Part of AIFP v1.0 - FP directive for currying and partial application*
