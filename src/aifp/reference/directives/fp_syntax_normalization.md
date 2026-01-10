# Directive: fp_syntax_normalization

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: MEDIUM - AST-level cross-language consistency

---

## Purpose

The `fp_syntax_normalization` directive abstracts language-specific syntax differences into a uniform AIFP-friendly Abstract Syntax Tree (AST) representation, enabling directives to operate uniformly across multiple programming languages. This directive provides **syntax-level abstraction** that makes AIFP language-agnostic.

Syntax normalization provides **universal code representation**, enabling:
- **Language-Agnostic Directives**: Same FP directives work across languages
- **Consistent AST**: Uniform tree structure regardless of source language
- **Cross-Language Analysis**: Analyze patterns across language boundaries
- **Simplified Directive Logic**: Directives don't handle per-language syntax
- **Code Translation**: Easier migration between languages

This directive acts as a **universal translator** converting language-specific syntax to AIFP canonical form.

---

## When to Apply

This directive applies when:
- **Multi-language analysis** - Directives need to analyze multiple languages
- **Cross-language patterns** - Detect same pattern in different syntaxes
- **Code generation** - Generate code for multiple target languages
- **Language migration** - Convert code from one language to another
- **Directive execution** - Before FP directives analyze code
- **Called by project directives**:
  - All FP directives - Normalize syntax before analysis
  - `project_compliance_check` - Normalize before checking compliance
  - Works with `fp_language_standardization` - Complement to naming

---

## Workflow

### Trunk: analyze_syntax_tree

Parses source code into AST and normalizes language-specific constructs to AIFP canonical form.

**Steps**:
1. **Detect language** - Identify source language from file extension/syntax
2. **Parse to AST** - Generate language-specific AST
3. **Normalize constructs** - Convert to AIFP canonical AST
4. **Validate structure** - Ensure normalized AST is valid
5. **Map back to source** - Maintain source location mappings
6. **Cache normalized AST** - Store for other directives

### Branches

**Branch 1: If language_variant_detected**
- **Then**: `apply_normalization`
- **Details**: Language uses different syntax for same concept
  - Examples: Python `lambda` vs JS arrow `=>`, Ruby blocks vs Python comprehensions
  - Map to AIFP canonical AST node type
  - Preserve semantic meaning
  - Maintain source location for error messages
- **Result**: Returns normalized AST

**Branch 2: If syntax_sugar**
- **Then**: `desugar_to_canonical`
- **Details**: Language has syntax sugar for FP patterns
  - Examples: List comprehensions, pattern matching shortcuts
  - Convert to explicit canonical form
  - Make implicit operations explicit
  - Preserve readability in normalized form
- **Result**: Returns desugared AST

**Branch 3: If already_normalized**
- **Then**: `mark_canonical`
- **Details**: Syntax already in canonical form
  - No language-specific constructs
  - AST is AIFP-standard
  - Ready for directive analysis
- **Result**: Returns AST as-is

**Fallback**: `use_language_specific_handler`
- **Details**: Complex language-specific construct
  - Cannot automatically normalize
  - Use language-specific directive extension
  - Preserve original AST with metadata
- **Result**: Returns AST with language marker

---

## Examples

### ✅ Compliant Code

**Normalized Lambda/Arrow Functions (Passes):**

```python
# Python source
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
```

```javascript
// JavaScript source
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(x => x * 2);
```

**AIFP Canonical AST (normalized to same structure):**
```json
{
  "type": "MapExpression",
  "collection": {"type": "Variable", "name": "numbers"},
  "function": {
    "type": "Lambda",
    "parameter": {"type": "Parameter", "name": "x"},
    "body": {
      "type": "BinaryOp",
      "operator": "*",
      "left": {"type": "Variable", "name": "x"},
      "right": {"type": "Literal", "value": 2}
    }
  }
}
```

**Why Compliant**:
- Different syntaxes normalized to same AST
- Directives can analyze both uniformly
- Semantic equivalence preserved
- Source language abstracted away

---

**Normalized List Comprehensions (Passes):**

```python
# Python comprehension
evens = [x for x in numbers if x % 2 == 0]
```

```javascript
// JavaScript equivalent
const evens = numbers.filter(x => x % 2 === 0);
```

**AIFP Canonical AST:**
```json
{
  "type": "FilterExpression",
  "collection": {"type": "Variable", "name": "numbers"},
  "predicate": {
    "type": "Lambda",
    "parameter": {"type": "Parameter", "name": "x"},
    "body": {
      "type": "BinaryOp",
      "operator": "==",
      "left": {
        "type": "BinaryOp",
        "operator": "%",
        "left": {"type": "Variable", "name": "x"},
        "right": {"type": "Literal", "value": 2}
      },
      "right": {"type": "Literal", "value": 0}
    }
  }
}
```

**Why Compliant**:
- Comprehension and filter() normalized to same AST
- Universal "FilterExpression" node type
- FP directives can analyze both uniformly

---

**Normalized Pattern Matching (Passes):**

```python
# Python 3.10+ match statement
match value:
    case 0:
        return "zero"
    case 1:
        return "one"
    case _:
        return "other"
```

```rust
// Rust match expression
match value {
    0 => "zero",
    1 => "one",
    _ => "other",
}
```

**AIFP Canonical AST:**
```json
{
  "type": "MatchExpression",
  "value": {"type": "Variable", "name": "value"},
  "cases": [
    {
      "pattern": {"type": "LiteralPattern", "value": 0},
      "body": {"type": "Literal", "value": "zero"}
    },
    {
      "pattern": {"type": "LiteralPattern", "value": 1},
      "body": {"type": "Literal", "value": "one"}
    },
    {
      "pattern": {"type": "WildcardPattern"},
      "body": {"type": "Literal", "value": "other"}
    }
  ]
}
```

**Why Compliant**:
- Different match syntaxes normalized
- Universal pattern matching AST
- Cross-language pattern analysis possible

---

### ❌ Non-Compliant Code

**Language-Specific AST Without Normalization (Violation):**

```python
# Python-specific AST (not normalized)
{
  "type": "ListComp",  # ← Python-specific node type
  "generators": [{
    "target": {"type": "Name", "id": "x"},
    "iter": {"type": "Name", "id": "numbers"},
    "ifs": [{
      "type": "Compare",
      "ops": ["Mod"],
      # ... Python-specific structure
    }]
  }]
}

# Problem:
# - Python-specific AST structure
# - Other languages have different AST types
# - Directives must handle each language separately
# - Not cross-language compatible
```

**Why Non-Compliant**:
- Language-specific AST nodes
- Not normalized to AIFP canonical form
- FP directives cannot analyze uniformly
- Each language needs separate directive logic

**Refactored (Compliant):**

```python
# AIFP Canonical AST (normalized)
{
  "type": "FilterExpression",  # ← Universal AIFP node type
  "source_language": "python",
  "source_construct": "list_comprehension",
  "collection": {"type": "Variable", "name": "numbers"},
  "predicate": {
    "type": "Lambda",
    "parameter": {"type": "Parameter", "name": "x"},
    "body": {
      "type": "BinaryOp",
      "operator": "==",
      "left": {
        "type": "BinaryOp",
        "operator": "%",
        "left": {"type": "Variable", "name": "x"},
        "right": {"type": "Literal", "value": 2}
      },
      "right": {"type": "Literal", "value": 0}
    }
  },
  "source_location": {"line": 5, "column": 10}
}

# Now directives can analyze uniformly across languages
```

---

**Implicit vs Explicit (Violation):**

```javascript
// JavaScript - implicit return in arrow function
const double = x => x * 2;  // ← Implicit return

// Problem: Some languages require explicit return
// Normalized AST should make it explicit
```

**Why Non-Compliant**:
- Implicit behavior not explicit in AST
- Cross-language analysis harder
- Should desugar to explicit form

**Refactored (Compliant):**

```javascript
// AIFP Canonical AST (explicit return)
{
  "type": "FunctionExpression",
  "name": "double",
  "parameters": [{"type": "Parameter", "name": "x"}],
  "body": {
    "type": "Block",
    "statements": [{
      "type": "Return",  # ← Explicit return in AST
      "value": {
        "type": "BinaryOp",
        "operator": "*",
        "left": {"type": "Variable", "name": "x"},
        "right": {"type": "Literal", "value": 2}
      }
    }]
  },
  "implicit_return": true  # ← Metadata preserves source info
}
```

---

## AIFP Canonical AST Node Types

### Expression Nodes

| AIFP Type | Description | Language Examples |
|-----------|-------------|-------------------|
| **Variable** | Variable reference | `x`, `foo`, `my_var` |
| **Literal** | Constant value | `42`, `"hello"`, `true` |
| **Lambda** | Anonymous function | Python `lambda x: x*2`, JS `x => x*2` |
| **BinaryOp** | Binary operation | `a + b`, `x * 2` |
| **UnaryOp** | Unary operation | `not x`, `!flag`, `-n` |
| **MapExpression** | Map transformation | Python `map()`, JS `.map()` |
| **FilterExpression** | Filter selection | Python `filter()`, JS `.filter()` |
| **ReduceExpression** | Reduce aggregation | Python `reduce()`, JS `.reduce()` |
| **MatchExpression** | Pattern matching | Python `match`, Rust `match`, Scala `match` |

### Statement Nodes

| AIFP Type | Description | Language Examples |
|-----------|-------------|-------------------|
| **FunctionDef** | Function definition | `def`, `function`, `fn` |
| **Assignment** | Variable binding | `x = 5`, `let x = 5`, `const x = 5` |
| **Return** | Return statement | `return x` |
| **Block** | Statement block | `{ ... }`, indented block |
| **IfExpression** | Conditional | `if/else`, ternary `? :` |

### Type Nodes

| AIFP Type | Description | Language Examples |
|-----------|-------------|-------------------|
| **TypeAnnotation** | Type hint | Python `: int`, TS `: number`, Rust `: i32` |
| **FunctionType** | Function type | `(int) -> int`, `(x: number) => number` |
| **UnionType** | Union type | Python `Union[A, B]`, TS `A | B` |
| **GenericType** | Parameterized type | Python `List[T]`, Rust `Vec<T>` |

---

## Normalization Rules

### Rule 1: Lambda Expressions

```
Python:  lambda x: x * 2
JS:      x => x * 2
Rust:    |x| x * 2

AIFP:    Lambda(Parameter("x"), BinaryOp("*", Variable("x"), Literal(2)))
```

### Rule 2: List Operations

```
Python:  [x * 2 for x in items]
JS:      items.map(x => x * 2)
Rust:    items.iter().map(|x| x * 2).collect()

AIFP:    MapExpression(Variable("items"), Lambda(Parameter("x"), BinaryOp("*", Variable("x"), Literal(2))))
```

### Rule 3: Conditionals

```
Python:  x if condition else y
JS:      condition ? x : y
Rust:    if condition { x } else { y }

AIFP:    IfExpression(Variable("condition"), Variable("x"), Variable("y"))
```

### Rule 4: Type Annotations

```
Python:  def foo(x: int) -> str
JS/TS:   function foo(x: number): string
Rust:    fn foo(x: i32) -> String

AIFP:    FunctionDef("foo", [Parameter("x", TypeAnnotation("int"))], TypeAnnotation("str"), ...)
```

---

## Edge Cases

### Edge Case 1: Language-Specific Operators

**Issue**: Different languages have different operators for same operation

**Handling**:
```python
# Normalize operators to canonical form

Python: and, or, not
JS:     &&, ||, !
Rust:   &&, ||, !

AIFP Canonical:
- Logical AND → "and"
- Logical OR → "or"
- Logical NOT → "not"

# AST preserves original for code generation
{
  "type": "BinaryOp",
  "operator": "and",  # Canonical
  "source_operator": "&&",  # Original for code gen
  "left": ...,
  "right": ...
}
```

**Directive Action**: Normalize operators to canonical form, preserve original in metadata.

---

### Edge Case 2: Indentation vs Braces

**Issue**: Python uses indentation, most languages use braces

**Handling**:
```python
# Both normalize to Block with statements

Python:
def foo():
    stmt1
    stmt2

JS:
function foo() {
    stmt1;
    stmt2;
}

AIFP Canonical:
FunctionDef("foo", [], Block([
    Statement("stmt1"),
    Statement("stmt2")
]))

# Indentation/braces are rendering details, not semantic
```

**Directive Action**: Abstract block structure from syntax formatting.

---

### Edge Case 3: Multiple Ways to Express Same Pattern

**Issue**: Language has multiple syntaxes for same operation

**Handling**:
```python
# Normalize to single canonical form

Python list creation (4 ways):
1. [x * 2 for x in items]  # List comprehension
2. list(map(lambda x: x*2, items))  # map + list
3. list(map(lambda x: x*2, iter(items)))  # explicit iter
4. [items[i] * 2 for i in range(len(items))]  # index-based

AIFP Canonical (single form):
MapExpression(Variable("items"), Lambda(Parameter("x"), BinaryOp("*", Variable("x"), Literal(2))))

# All four normalize to same AST
```

**Directive Action**: Normalize all variants to single canonical form.

---

## Related Directives

- **Depends On**: None (foundational directive)
- **Triggers**:
  - All FP directives - Use normalized AST for analysis
- **Called By**:
  - All FP directives - Call before analyzing code
  - `project_compliance_check` - Normalize before checking
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `ast_normalized = 1` for normalized function ASTs
- **`notes`**: Logs normalization issues with `note_type = 'normalization'`

---

## Testing

How to verify this directive is working:

1. **Same pattern, different syntax** → Normalizes to same AST
   ```python
   # Python: [x*2 for x in items]
   # JS: items.map(x => x*2)
   # Both → MapExpression AST
   ```

2. **Directives work across languages** → No per-language code
   ```python
   fp_purity directive works on normalized AST
   → Doesn't need Python-specific or JS-specific logic
   ```

3. **Check database** → Verify ASTs normalized
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Common Mistakes

- ❌ **Preserving language-specific AST types** - Not normalizing
- ❌ **Losing semantic information** - Over-normalization
- ❌ **Not preserving source locations** - Error messages unclear
- ❌ **Incomplete operator normalization** - Inconsistent comparisons
- ❌ **Forgetting to desugar** - Leaving implicit behavior

---

## Roadblocks and Resolutions

### Roadblock 1: language_variant_detected
**Issue**: Different syntax for same FP pattern
**Resolution**: Map to AIFP canonical AST node type, preserve source metadata

### Roadblock 2: syntax_sugar
**Issue**: Language has convenient syntax sugar
**Resolution**: Desugar to explicit canonical form while preserving readability

### Roadblock 3: complex_language_construct
**Issue**: Language-specific construct without cross-language equivalent
**Resolution**: Preserve original AST with language marker, handle specially

### Roadblock 4: ambiguous_normalization
**Issue**: Multiple possible canonical forms for construct
**Resolution**: Choose most explicit form, document choice in AST metadata

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for AST-level syntax normalization*
