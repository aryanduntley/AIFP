# FP Directives Blueprint

## Overview

FP (Functional-Procedural) directives enforce **pure functional programming standards** across all AIFP projects, regardless of programming language. They eliminate OOP constructs, ensure referential transparency, and create AI-friendly, deterministic code that is easy to reason about.

### Core Philosophy

- **Language-Agnostic**: Work across Python, JavaScript, TypeScript, Rust, Go, etc.
- **Purity First**: All functions must be pure, deterministic, and side-effect-free
- **No OOP**: Zero classes, objects, inheritance, or mutable state
- **Composability**: Functions compose via pipelines, monads, and pure transformations
- **AI-Optimized**: Predictable code behavior for AI reasoning and generation

---

## FP Directive Categories

### 1. Purity (Core Foundation)
**Directives**: `fp_purity`, `fp_state_elimination`, `fp_side_effect_detection`, `fp_immutability`

**Purpose**: Enforce referential transparency and eliminate hidden state.

**Rules**:
- Functions must return same output for same inputs (deterministic)
- No external state access (global variables, singletons)
- No mutations (arrays, objects, primitives passed by reference)
- No I/O operations within pure functions (isolate via wrappers)

**Example Violations**:
```python
# ❌ BAD: Accesses global state
counter = 0
def increment():
    global counter
    counter += 1
    return counter

# ✅ GOOD: Pure function with explicit state
def increment(counter):
    return counter + 1
```

### 2. Control Flow
**Directives**: `fp_recursion_enforcement`, `fp_branching_elimination`, `fp_pattern_matching`

**Purpose**: Replace imperative loops and conditionals with functional constructs.

**Rules**:
- Use tail recursion instead of loops
- Use pattern matching instead of if/else chains
- Use guard clauses for validation
- No early returns (use Result types)

**Example**:
```python
# ❌ BAD: Imperative loop
def sum_list(items):
    total = 0
    for item in items:
        total += item
    return total

# ✅ GOOD: Tail recursion
def sum_list(items, acc=0):
    if not items:
        return acc
    return sum_list(items[1:], acc + items[0])

# ✅ BETTER: Functional reduce
from functools import reduce
def sum_list(items):
    return reduce(lambda acc, x: acc + x, items, 0)
```

### 3. Error Handling
**Directives**: `fp_optionals`, `fp_result_types`, `fp_try_monad`, `fp_error_pipeline`, `fp_null_elimination`

**Purpose**: Replace exceptions with declarative error handling.

**Rules**:
- Use Option/Maybe for nullable values
- Use Result/Either for operations that can fail
- Use Try monad for error-prone operations
- Chain error handling with flatMap/bind
- Never use null/undefined literals

**Example**:
```python
# ❌ BAD: Exception-based error handling
def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

# ✅ GOOD: Result type
from typing import Union

class Ok:
    def __init__(self, value):
        self.value = value

class Err:
    def __init__(self, error):
        self.error = error

def divide(a, b) -> Union[Ok, Err]:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)
```

### 4. Composition
**Directives**: `fp_monadic_composition`, `fp_function_composition`, `fp_chaining`, `fp_pipelines`

**Purpose**: Enable function composition and data transformation pipelines.

**Rules**:
- Compose functions using pipe operators or composition functions
- Chain monadic operations with bind/flatMap
- Build data transformation pipelines
- Avoid nested function calls (use composition)

**Example**:
```python
# ❌ BAD: Nested function calls
result = str(int(float(user_input)))

# ✅ GOOD: Composition pipeline
from functools import reduce

def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

pipeline = compose(str, int, float)
result = pipeline(user_input)
```

### 5. Data Structures
**Directives**: `fp_list_operations`, `fp_map_reduce`, `fp_lazy_evaluation`, `fp_data_filtering`, `fp_pattern_unpacking`, `fp_adt`

**Purpose**: Use immutable, functional data structures and operations.

**Rules**:
- Use map/filter/reduce instead of loops
- Use immutable lists, tuples, records
- Use lazy evaluation for large datasets
- Define Algebraic Data Types (ADTs) for domain modeling
- Use destructuring/pattern unpacking for data access

**Example ADT**:
```python
# ✅ GOOD: ADT for Result type
from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

Result = Union[Ok[T], Err[E]]
```

### 6. OOP Elimination
**Directives**: `fp_class_elimination`, `fp_inheritance_block`, `fp_static_methods_only`, `fp_object_state_block`, `fp_wrapper_generation`

**Purpose**: Eliminate all OOP constructs and convert to FP patterns.

**Rules**:
- No classes with instance methods
- No inheritance or polymorphism
- Convert objects to pure data structures (records, tuples)
- Extract methods into standalone pure functions
- Generate wrappers for OOP libraries

**Example**:
```python
# ❌ BAD: OOP class with state
class Calculator:
    def __init__(self):
        self.memory = 0

    def add(self, x, y):
        result = x + y
        self.memory = result
        return result

# ✅ GOOD: Pure functions + data structure
from typing import NamedTuple

class CalculatorState(NamedTuple):
    memory: float

def add(x: float, y: float) -> float:
    return x + y

def add_with_memory(state: CalculatorState, x: float, y: float) -> tuple[float, CalculatorState]:
    result = add(x, y)
    new_state = CalculatorState(memory=result)
    return result, new_state
```

### 7. I/O Isolation
**Directives**: `fp_io_isolation`, `fp_effect_boundaries`, `fp_dependency_injection`

**Purpose**: Isolate side effects and I/O operations from pure logic.

**Rules**:
- Separate pure logic from I/O effects
- Use dependency injection for I/O operations
- Create effect boundaries at program edges
- Pass I/O dependencies as parameters

**Example**:
```python
# ❌ BAD: I/O mixed with logic
def process_user():
    name = input("Enter name: ")
    age = int(input("Enter age: "))
    if age >= 18:
        print(f"{name} is an adult")
    else:
        print(f"{name} is a minor")

# ✅ GOOD: Separated I/O and logic
def classify_age(age: int) -> str:
    return "adult" if age >= 18 else "minor"

def format_message(name: str, classification: str) -> str:
    return f"{name} is a {classification}"

# I/O boundary (not pure, but isolated)
def main():
    name = input("Enter name: ")
    age = int(input("Enter age: "))
    classification = classify_age(age)
    message = format_message(name, classification)
    print(message)
```

### 8. Optimization
**Directives**: `fp_memoization`, `fp_lazy_computation`, `fp_parallel_evaluation`, `fp_function_inlining`, `fp_dead_code_elimination`, `fp_constant_folding`, `fp_purity_caching_analysis`, `fp_cost_analysis`, `fp_evaluation_order_control`

**Purpose**: Optimize functional code without breaking purity guarantees.

**Rules**:
- Apply memoization only to pure functions
- Use lazy evaluation for expensive computations
- Parallelize independent pure expressions
- Inline small pure functions
- Eliminate unreachable code
- Precompute constant expressions

### 9. Meta/Reflection
**Directives**: `fp_metadata_annotation`, `fp_symbol_map_validation`, `fp_reflection_block`, `fp_docstring_enforcement`, `fp_function_indexing`, `fp_ai_reasoning_trace`

**Purpose**: Enable AI introspection and prevent runtime reflection.

**Rules**:
- Annotate functions with AIFP metadata
- Maintain symbol map for exported functions
- Block runtime reflection and eval
- Enforce docstrings for all functions
- Index functions in project.db
- Add reasoning traces for AI explainability

### 10. Language Adaptation
**Directives**: `fp_language_standardization`, `fp_keyword_alignment`, `fp_cross_language_wrappers`, `fp_syntax_normalization`, `fp_encoding_consistency`

**Purpose**: Enable cross-language AIFP compliance.

**Rules**:
- Normalize function names across languages (map → collect → map)
- Handle reserved keyword conflicts
- Generate wrappers for language-specific libraries
- Normalize syntax differences (AST-level)
- Enforce UTF-8 encoding everywhere

---

## Directive Structure

### Standard Format

```json
{
  "name": "fp_purity",
  "type": "fp",
  "category": {
    "name": "purity",
    "description": "Eliminates hidden state and ensures referential transparency"
  },
  "description": "Enforces pure functions: deterministic output for given inputs, no external state or side effects",
  "workflow": {
    "trunk": "analyze_function",
    "branches": [
      {"if": "mutation_detected", "then": "refactor_to_pure", "details": {"explicit_params": true}},
      {"if": "external_state_access", "then": "isolate_side_effects"},
      {"if": "pure", "then": "mark_compliant"},
      {"if": "refactored", "then": "update_functions_table", "details": {"side_effects_json": "none", "purity_level": "pure"}},
      {"if": "low_confidence", "then": "prompt_user", "details": {"clarify": "Function purity uncertain"}},
      {"fallback": "prompt_user", "details": {"log_note": true}}
    ],
    "error_handling": {"on_failure": "prompt_user"}
  },
  "roadblocks_json": [
    {"issue": "stateful_function", "resolution": "Isolate state outside of function scope"},
    {"issue": "hidden_mutation", "resolution": "Refactor to pure function"},
    {"issue": "language_mismatch", "resolution": "Escalate to fp_language_standardization"},
    {"issue": "external_dependency", "resolution": "Pass as explicit parameter or isolate with fp_wrapper_generation"}
  ],
  "intent_keywords_json": ["pure", "no side effects", "deterministic"],
  "confidence_threshold": 0.7,
  "notes": "Central FP rule; applies to all code generation and compliance checks. Links to project_compliance_check.",
  "related_directives": {
    "fp": ["fp_immutability", "fp_side_effect_detection", "fp_state_elimination"],
    "project": ["project_compliance_check", "project_file_write"]
  }
}
```

### Workflow Branches

**Common Patterns**:
- **Detect violation** → Refactor to compliant code
- **Compliance achieved** → Update database (`update_functions_table`)
- **Low confidence** → Prompt user for clarification
- **Fallback** → Log note and prompt user

### Roadblocks

FP directives include language-specific and common roadblocks:

- **language_mismatch**: Escalate to `fp_language_standardization`
- **external_dependency**: Use `fp_wrapper_generation` for OOP library isolation
- **performance_concern**: Escalate to optimization directives
- **unclear_pattern**: Prompt user or escalate to markdown

---

## Database Integration

### Functions Table Updates

When FP directives refactor code, they update the `functions` table:

```sql
UPDATE functions
SET
    purpose = 'Pure calculation function',
    parameters = '["x: float", "y: float"]',
    return_type = 'float',
    purity_level = 'pure',
    side_effects_json = 'null',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 42;
```

### Interactions Table

FP directives track function composition and dependencies:

```sql
INSERT INTO interactions (source_function_id, target_function_id, interaction_type, description)
VALUES
    (42, 15, 'call', 'add calls multiply for intermediate calculation'),
    (42, 23, 'compose', 'add composes with format_result in pipeline');
```

### Types Table

ADT definitions are stored in the `types` table:

```sql
INSERT INTO types (name, definition_json, description, linked_function_id, project_id)
VALUES
    ('Result', '{"type": "union", "variants": ["Ok", "Err"]}', 'Result type for error handling', NULL, 1);
```

---

## Compliance Checking

### project_compliance_check Workflow

When `project_compliance_check` runs, it:

1. Queries all functions from `functions` table
2. Runs relevant FP directives on each function
3. Collects violations
4. Generates compliance report
5. Updates `notes` table with issues

**Output**:
```json
{
  "compliant": false,
  "violations": [
    {
      "file": "src/auth/login.py",
      "function": "authenticate_user",
      "directive": "fp_purity",
      "issue": "Accesses global database connection",
      "resolution": "Pass database connection as parameter"
    }
  ]
}
```

---

## Cross-Directive Interactions

### FP → Project Links

- `fp_purity` → called by `project_file_write` before writing code
- `fp_adt` → updates `types` table via `project_update_db`
- All FP directives → referenced by `project_compliance_check`

### FP → FP Links

- `fp_purity` → may call `fp_wrapper_generation` for OOP isolation
- `fp_recursion_enforcement` → may call `fp_list_operations` for transformation
- `fp_error_pipeline` → requires `fp_result_types` and `fp_monadic_composition`

---

## Language-Specific Adaptations

### Python
- Use `functools.reduce` for aggregations
- Use `dataclasses(frozen=True)` for immutable records
- Use `typing` module for ADTs (Union, TypeVar, Generic)

### JavaScript/TypeScript
- Use `const` everywhere (no `let` or `var`)
- Use `Object.freeze()` for immutability
- Use `Array.map/filter/reduce` for list operations
- TypeScript: Use discriminated unions for ADTs

### Rust
- Use `fn` for all functions (no `impl` blocks with `&self`)
- Use `match` for pattern matching
- Use `Result<T, E>` and `Option<T>` natively
- Use `iter()` for lazy evaluation

### Go
- Use standalone functions only (no methods with receivers)
- Pass state explicitly as parameters
- Use interfaces for ADTs (limited support)
- Generate wrappers for error-prone operations

---

## Metadata Annotations

### AIFP_METADATA Format

FP directives insert metadata comments:

```python
# AIFP_METADATA
# function_name: calculate_total
# purity_level: pure
# dependencies: [multiply, add]
# theme: calculations
# flow: invoice-processing
# complexity: O(n)
def calculate_total(items):
    return reduce(lambda acc, item: add(acc, multiply(item.price, item.quantity)), items, 0)
```

This enables:
- AI reasoning and explanation
- Quick function lookup in project.db
- Dependency graph construction
- Complexity analysis

---

## Escalation to Markdown

When JSON workflows are insufficient (complex refactoring, ambiguous patterns), FP directives escalate to `.md` files:

**Triggers**:
- User confidence < 0.5
- Multiple roadblocks encountered
- Language-specific edge case
- AI requests detailed explanation

**Example**: `fp_purity.md` contains step-by-step refactoring guides for common impure patterns.

---

## Optimization Directives

### Memoization (fp_memoization)

Only applies to **pure, deterministic functions**:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

### Lazy Evaluation (fp_lazy_evaluation)

For large datasets:

```python
# ❌ BAD: Eager evaluation
results = [expensive_computation(x) for x in large_list]
final_result = process(results[:10])  # Only need first 10!

# ✅ GOOD: Lazy evaluation
results = (expensive_computation(x) for x in large_list)
final_result = process(list(itertools.islice(results, 10)))
```

### Parallel Evaluation (fp_parallel_evaluation)

For independent pure expressions:

```python
from multiprocessing import Pool

def parallel_map(func, items):
    with Pool() as pool:
        return pool.map(func, items)

results = parallel_map(expensive_pure_function, large_dataset)
```

---

## Common Violations and Fixes

### 1. Mutable Default Arguments

```python
# ❌ BAD
def append_item(item, list=[]):
    list.append(item)
    return list

# ✅ GOOD
def append_item(item, list=None):
    if list is None:
        list = []
    return list + [item]  # Returns new list
```

### 2. Hidden I/O

```python
# ❌ BAD
def process_data(filename):
    with open(filename) as f:
        data = f.read()
    return transform(data)

# ✅ GOOD
def transform_data(data: str) -> str:
    return transform(data)

# I/O boundary (separate)
def main():
    with open(filename) as f:
        data = f.read()
    result = transform_data(data)
    print(result)
```

### 3. Global State Access

```python
# ❌ BAD
config = {"threshold": 100}

def check_value(value):
    return value > config["threshold"]

# ✅ GOOD
def check_value(value: int, threshold: int) -> bool:
    return value > threshold

# Pass config explicitly
result = check_value(150, config["threshold"])
```

---

## Testing FP Compliance

### Property-Based Testing

FP functions enable property-based testing:

```python
from hypothesis import given, strategies as st

# Pure function
def add(x: int, y: int) -> int:
    return x + y

# Property: Addition is commutative
@given(st.integers(), st.integers())
def test_add_commutative(a, b):
    assert add(a, b) == add(b, a)

# Property: Addition is associative
@given(st.integers(), st.integers(), st.integers())
def test_add_associative(a, b, c):
    assert add(add(a, b), c) == add(a, add(b, c))
```

---

## Summary

FP directives enforce a **strict functional programming paradigm** across AIFP projects:

- **60+ directives** covering purity, composition, error handling, optimization
- **Language-agnostic** enforcement via standardization directives
- **Database-driven** tracking of functions, interactions, types
- **AI-friendly** code that is deterministic, composable, and easy to reason about
- **Zero OOP** constructs (classes, inheritance, mutable state)
- **Cross-directive integration** with project directives for compliance checking

They transform traditional imperative/OOP code into pure functional code that AI can confidently generate, modify, and reason about.
