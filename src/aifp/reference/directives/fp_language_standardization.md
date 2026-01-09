# Directive: fp_language_standardization

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Cross-language consistency enabler

---

## Purpose

The `fp_language_standardization` directive normalizes functional programming terminology, naming conventions, and idioms across different programming languages to maintain consistency in multi-language AIFP projects. This directive provides **cross-language FP consistency** that enables uniform functional patterns regardless of implementation language.

Language standardization provides **multi-language coherence**, enabling:
- **Consistent Terminology**: Same FP concepts use same names across languages
- **Unified Idioms**: map/filter/reduce patterns standardized everywhere
- **Cross-Language Refactoring**: Easier migration between languages
- **Clear Documentation**: Universal FP vocabulary across codebase
- **Team Alignment**: Developers understand patterns across language boundaries

This directive acts as a **translation layer** ensuring FP principles remain consistent across Python, JavaScript, TypeScript, Rust, Go, and other languages.

**Important**: This directive is reference documentation for language standardization patterns.
AI consults this when uncertain about language-specific FP idioms or cross-language compatibility concerns.

**FP language standardization is baseline behavior**:
- AI writes cross-language compatible code naturally (enforced by system prompt during code writing)
- This directive provides detailed guidance for complex scenarios
- NO post-write validation occurs
- NO automatic checking after file writes

---

## When to Apply

**When AI Consults This Directive**:
- Uncertainty about language-specific FP idiom translation
- Complex cross-language standardization scenarios
- Edge cases with language-specific features or naming conventions
- Need for detailed guidance on AIFP standardization patterns

**Context**:
- AI writes standardized code as baseline behavior (system prompt enforcement)
- This directive is consulted DURING code writing when uncertainty arises
- Related directives (`fp_keyword_alignment`, other FP directives) may reference this for guidance

**NOT Applied**:
- ❌ NOT called automatically after every file write
- ❌ NOT used for post-write validation
- ❌ NO validation loop

---

## Workflow

### Trunk: normalize_identifiers

Analyzes code to detect language-specific FP terminology and normalizes to AIFP standard names.

**Steps**:
1. **Detect language** - Identify programming language from file extension/syntax
2. **Scan identifiers** - Find function names, variable names, type names
3. **Compare to standards** - Check against AIFP naming standards table
4. **Detect variants** - Identify language-specific aliases (e.g., "collect" vs "map")
5. **Check consistency** - Verify names match AIFP standards
6. **Generate replacements** - Create rename mappings for non-standard names

### Branches

**Branch 1: If alias_detected**
- **Then**: `replace_with_standard_name`
- **Details**: Language uses non-standard name for FP concept
  - Examples: Ruby's `collect` → `map`, Scala's `foldLeft` → `reduce`
  - Replace with AIFP standard: map, filter, reduce, flatMap
  - Update all call sites consistently
  - Document original name in comments if needed
- **Result**: Returns code with standardized names

**Branch 2: If syntax_variant**
- **Then**: `apply_language_adapter`
- **Details**: Language has different syntax for same concept
  - Example: Python `lambda x: x*2` vs JS `x => x*2`
  - Normalize to AIFP standard form
  - Preserve language-specific syntax requirements
  - Maintain semantic equivalence
- **Result**: Returns adapted code

**Branch 3: If naming_conflict**
- **Then**: `resolve_with_prefix`
- **Details**: Standard name conflicts with language keyword
  - Example: "type" is keyword in some languages
  - Apply AIFP prefix: `aifp_type`, `fp_type`
  - Document conflict resolution strategy
  - Maintain consistency across files
- **Result**: Returns renamed identifiers

**Branch 4: If already_standardized**
- **Then**: `mark_compliant`
- **Details**: Code uses AIFP standard naming
  - Consistent with naming conventions
  - No language-specific aliases
  - Clear and universal terminology
- **Result**: Code passes check

**Fallback**: `prompt_user`
- **Details**: Unclear how to standardize
  - Ambiguous identifier meaning
  - Multiple possible standards
  - Ask user for preferred naming
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Standardized Naming Across Languages (Passes):**

```python
# Python - AIFP Standard
def process_numbers(numbers: list[int]) -> list[int]:
    """
    Process numbers: filter evens, map to doubles.

    AIFP Standard: map, filter, reduce
    """
    evens = filter(lambda x: x % 2 == 0, numbers)
    doubled = map(lambda x: x * 2, evens)
    return list(doubled)
```

```javascript
// JavaScript - AIFP Standard (same names)
function processNumbers(numbers) {
    /**
     * Process numbers: filter evens, map to doubles.
     *
     * AIFP Standard: map, filter, reduce
     */
    const evens = numbers.filter(x => x % 2 === 0);
    const doubled = evens.map(x => x * 2);
    return doubled;
}
```

```rust
// Rust - AIFP Standard (same names)
fn process_numbers(numbers: Vec<i32>) -> Vec<i32> {
    /// Process numbers: filter evens, map to doubles.
    ///
    /// AIFP Standard: map, filter, reduce
    numbers
        .into_iter()
        .filter(|x| x % 2 == 0)
        .map(|x| x * 2)
        .collect()
}
```

**Why Compliant**:
- Same operation names across all three languages
- Consistent terminology (filter, map)
- Universal FP vocabulary
- Easy to understand cross-language

---

**Standardized Error Handling (Passes):**

```python
# Python - AIFP Standard: Result type
from typing import Union

class Ok:
    def __init__(self, value):
        self.value = value

class Err:
    def __init__(self, error):
        self.error = error

Result = Union[Ok, Err]

def divide(a: float, b: float) -> Result:
    """AIFP Standard: Result type for error handling"""
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)
```

```typescript
// TypeScript - AIFP Standard: Result type (same name)
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function divide(a: number, b: number): Result<number, string> {
    /** AIFP Standard: Result type for error handling */
    if (b === 0) {
        return { ok: false, error: "Division by zero" };
    }
    return { ok: true, value: a / b };
}
```

```rust
// Rust - AIFP Standard: Result type (native)
fn divide(a: f64, b: f64) -> Result<f64, String> {
    /// AIFP Standard: Result type for error handling
    if b == 0.0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}
```

**Why Compliant**:
- Universal "Result" type name
- Consistent Ok/Err terminology
- Same pattern across languages
- FP standard error handling

---

### ❌ Non-Compliant Code

**Language-Specific Aliases (Violation):**

```ruby
# ❌ VIOLATION: Ruby-specific naming
def process_numbers(numbers)
  evens = numbers.select { |x| x.even? }  # ← "select" instead of "filter"
  doubled = evens.collect { |x| x * 2 }   # ← "collect" instead of "map"
  doubled
end

# Problem:
# - "select" is Ruby-specific (should be "filter")
# - "collect" is Ruby-specific (should be "map")
# - Inconsistent with AIFP standards
# - Hard to understand for non-Ruby developers
```

**Why Non-Compliant**:
- Uses language-specific aliases
- Not consistent with AIFP standard
- Reduces cross-language comprehension
- Should use universal FP terms

**Refactored (Compliant):**

```ruby
# ✅ REFACTORED: AIFP standard naming
def process_numbers(numbers)
  # AIFP Standard: filter and map (universal terms)
  evens = numbers.filter { |x| x.even? }   # Ruby also supports "filter"
  doubled = evens.map { |x| x * 2 }        # Use "map" instead of "collect"
  doubled
end

# Or with explicit AIFP comment:
def process_numbers_v2(numbers)
  # AIFP Note: Using select→filter, collect→map for consistency
  evens = numbers.filter { |x| x.even? }
  doubled = evens.map { |x| x * 2 }
  doubled
end
```

---

**Inconsistent Reduce Naming (Violation):**

```scala
// ❌ VIOLATION: Scala-specific naming
def sum_numbers(numbers: List[Int]): Int = {
  numbers.foldLeft(0)(_ + _)  // ← "foldLeft" instead of "reduce"
}

def sum_numbers_v2(numbers: List[Int]): Int = {
  numbers.reduceLeft(_ + _)  // ← "reduceLeft" instead of "reduce"
}

// Problem:
// - "foldLeft" is Scala-specific (should be "reduce")
// - "reduceLeft" is also Scala-specific
// - AIFP standard is "reduce"
// - Inconsistent with other languages
```

**Why Non-Compliant**:
- Scala-specific terminology
- Multiple names for same concept
- Not standardized across languages
- Should use universal "reduce"

**Refactored (Compliant):**

```scala
// ✅ REFACTORED: AIFP standard with wrapper
def reduce[A](init: A, combine: (A, A) => A)(items: List[A]): A = {
  // AIFP Standard: "reduce" wrapper over Scala's foldLeft
  items.foldLeft(init)(combine)
}

def sum_numbers(numbers: List[Int]): Int = {
  // Uses AIFP standard "reduce" function
  reduce(0, (a: Int, b: Int) => a + b)(numbers)
}

// Or with type alias:
type Reducer[A] = (A, A) => A

def sum_numbers_v2(numbers: List[Int]): Int = {
  // AIFP Standard: reduce terminology maintained
  reduce(0, (a, b) => a + b)(numbers)
}
```

---

**Mixed Terminology (Violation):**

```go
// ❌ VIOLATION: Inconsistent naming across functions
package main

func FilterEven(numbers []int) []int {
    var result []int
    for _, num := range numbers {
        if num%2 == 0 {
            result = append(result, num)
        }
    }
    return result
}

func Transform(numbers []int, fn func(int) int) []int {  // ← "Transform" not standard
    var result []int
    for _, num := range numbers {
        result = append(result, fn(num))
    }
    return result
}

func Fold(init int, numbers []int, fn func(int, int) int) int {  // ← "Fold" not standard
    acc := init
    for _, num := range numbers {
        acc = fn(acc, num)
    }
    return acc
}

// Problem:
// - "Transform" should be "Map"
// - "Fold" should be "Reduce"
// - Inconsistent naming scheme
// - Not aligned with AIFP standards
```

**Why Non-Compliant**:
- Inconsistent naming across functions
- Non-standard terminology
- Harder to understand pattern
- Should use universal FP names

**Refactored (Compliant):**

```go
// ✅ REFACTORED: AIFP standard naming
package main

// AIFP Standard: Filter
func Filter(numbers []int, predicate func(int) bool) []int {
    var result []int
    for _, num := range numbers {
        if predicate(num) {
            result = append(result, num)
        }
    }
    return result
}

// AIFP Standard: Map
func Map(numbers []int, transform func(int) int) []int {
    var result []int
    for _, num := range numbers {
        result = append(result, transform(num))
    }
    return result
}

// AIFP Standard: Reduce
func Reduce(init int, numbers []int, combine func(int, int) int) int {
    acc := init
    for _, num := range numbers {
        acc = combine(acc, num)
    }
    return acc
}

// Usage example
func ProcessNumbers(numbers []int) int {
    // AIFP Standard: Filter → Map → Reduce pipeline
    evens := Filter(numbers, func(x int) bool { return x%2 == 0 })
    doubled := Map(evens, func(x int) int { return x * 2 })
    total := Reduce(0, doubled, func(a, b int) int { return a + b })
    return total
}
```

---

## Edge Cases

### Edge Case 1: Language Lacks Standard Operator

**Issue**: Language doesn't have built-in map/filter/reduce

**Handling**:
```go
// Go doesn't have generic map/filter/reduce built-ins
// AIFP Standard: Provide standard implementations

// AIFP Standard: Map implementation
func Map[T any, R any](items []T, transform func(T) R) []R {
    result := make([]R, len(items))
    for i, item := range items {
        result[i] = transform(item)
    }
    return result
}

// AIFP Standard: Filter implementation
func Filter[T any](items []T, predicate func(T) bool) []T {
    result := make([]T, 0)
    for _, item := range items {
        if predicate(item) {
            result = append(result, item)
        }
    }
    return result
}

// AIFP Standard: Reduce implementation
func Reduce[T any, R any](items []T, initial R, combine func(R, T) R) R {
    acc := initial
    for _, item := range items {
        acc = combine(acc, item)
    }
    return acc
}

// Usage
numbers := []int{1, 2, 3, 4, 5}
doubled := Map(numbers, func(x int) int { return x * 2 })
evens := Filter(doubled, func(x int) bool { return x%2 == 0 })
total := Reduce(evens, 0, func(acc, x int) int { return acc + x })
```

**Directive Action**: Generate standard implementations for languages lacking built-ins.

---

### Edge Case 2: Reserved Keyword Conflict

**Issue**: AIFP standard name is reserved keyword in target language

**Handling**:
```python
# "type" is common in FP but conflicts in many languages

# ❌ Problem: "type" is keyword in Python for type hints
def type(value):  # SyntaxError: invalid syntax
    return type(value)

# ✅ Solution: AIFP prefix convention
def aifp_type(value):
    """
    AIFP Standard: type introspection
    Note: Prefixed due to Python keyword conflict
    """
    return type(value).__name__

# Alternative: Use "get_type" for clarity
def get_type(value):
    """AIFP Standard: type introspection (keyword-safe)"""
    return type(value).__name__
```

**Directive Action**: Use `aifp_` prefix or descriptive alternative for keyword conflicts.

---

### Edge Case 3: Multiple Valid Aliases

**Issue**: Language has multiple equally valid names for same concept

**Handling**:
```javascript
// JavaScript has multiple ways to express same pattern

// AIFP Decision: Choose most universal form

// ✅ AIFP Standard: Use "map" (universal)
const doubled = numbers.map(x => x * 2);

// ❌ Avoid: Array.from with mapping
const doubled_alt = Array.from(numbers, x => x * 2);

// Reasoning: "map" is universal FP term, recognized across languages
// Array.from is JavaScript-specific utility

// AIFP Standard: Document when using non-standard but necessary
function mapWithIndex(items, fn) {
    // AIFP Note: Using Array.from for index access
    // Standard "map" doesn't provide index in pure form
    return Array.from(items, (item, idx) => fn(item, idx));
}
```

**Directive Action**: Prefer universal FP term over language-specific utility.

---

## AIFP Standard Naming Table

### Core FP Operations

| Concept | AIFP Standard | Language Variants |
|---------|---------------|-------------------|
| **Transform each** | `map` | Ruby: collect, Scala: map |
| **Select matching** | `filter` | Ruby: select, Python: filter, JS: filter |
| **Aggregate/Combine** | `reduce` | Scala: foldLeft, JS: reduce, Python: reduce |
| **Flatten nested** | `flatMap` | Scala: flatMap, JS: flatMap, Haskell: bind |
| **Chain operations** | `compose` | Math: ∘, Haskell: ., Ramda: compose |
| **Maybe/Nullable** | `Option` | Haskell: Maybe, Rust: Option, Scala: Option |
| **Success/Failure** | `Result` | Rust: Result, Haskell: Either, Scala: Either |

### Collection Operations

| Concept | AIFP Standard | Language Variants |
|---------|---------------|-------------------|
| **Get first** | `head` | Python: [0], JS: [0], Rust: first() |
| **Get rest** | `tail` | Python: [1:], Lisp: cdr |
| **Get length** | `length` | Python: len(), JS: length, Ruby: size |
| **Check empty** | `is_empty` | Python: not list, Ruby: empty? |
| **Combine lists** | `concat` | Python: +, JS: concat, Rust: extend |

### Type Operations

| Concept | AIFP Standard | Language Variants |
|---------|---------------|-------------------|
| **ADT variant** | `variant` | Rust: enum, Haskell: data |
| **Pattern match** | `match` | Rust: match, Haskell: case, Python: match |
| **Type constructor** | `constructor` | Haskell: data, Rust: enum |

---

## Related Directives

- **Depends On**:
  - `fp_purity` - Ensure standardized functions remain pure
- **Triggers**:
  - `fp_cross_language_wrappers` - Generate wrappers with standard names
  - `fp_syntax_normalization` - Normalize syntax after naming
- **Called By**:
  - `project_file_write` - Apply standardization when writing files
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

**Project Database** (project.db):
- **`functions`**: Sets `naming_standard = 'aifp'` for standardized functions

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

1. **Multi-language project** → Directive ensures consistent naming
   ```python
   # Python: uses "map"
   result = list(map(lambda x: x*2, items))
   ```
   ```javascript
   // JavaScript: also uses "map"
   result = items.map(x => x * 2);
   ```

2. **Language alias detected** → Directive replaces with standard
   ```ruby
   # Before: numbers.collect { |x| x * 2 }
   # After: numbers.map { |x| x * 2 }
   ```

3. **Check database** → Verify standardization marked
   ```sql
   SELECT name, naming_standard
   FROM functions
   WHERE naming_standard = 'aifp';
   ```

---

## Common Mistakes

- ❌ **Using language-specific aliases** - Reduces cross-language clarity
- ❌ **Inconsistent naming within project** - Mix of standards
- ❌ **Ignoring keyword conflicts** - Causes syntax errors
- ❌ **Over-standardizing** - Forcing standards where language idioms are clearer
- ❌ **Not documenting variations** - When language-specific form is necessary

---

## Roadblocks and Resolutions

### Roadblock 1: alias_detected
**Issue**: Code uses language-specific alias for FP operation
**Resolution**: Replace with AIFP standard name (map, filter, reduce)

### Roadblock 2: keyword_conflict
**Issue**: AIFP standard name conflicts with language keyword
**Resolution**: Use `aifp_` prefix or descriptive alternative

### Roadblock 3: no_builtin_equivalent
**Issue**: Language lacks built-in for standard FP operation
**Resolution**: Generate standard implementation with AIFP naming

### Roadblock 4: multiple_standards_conflict
**Issue**: Different parts of codebase use different conventions
**Resolution**: Audit codebase, choose one standard, apply consistently

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for cross-language naming consistency*
