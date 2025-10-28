# Directive: fp_keyword_alignment

**Type**: FP Auxiliary
**Level**: 2 (High Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Prevents syntax conflicts in multi-language projects

---

## Purpose

The `fp_keyword_alignment` directive detects and resolves naming conflicts between AIFP standard identifiers and language-specific reserved keywords. This directive provides **keyword conflict resolution** that ensures code compiles correctly across all target languages.

Keyword alignment provides **syntax safety**, enabling:
- **Compile-Time Safety**: No syntax errors from keyword conflicts
- **Consistent Alternatives**: Standard fallback names for conflicting identifiers
- **Cross-Language Portability**: Code patterns work across languages
- **Clear Documentation**: Document why non-standard names are used
- **Automated Resolution**: Systematic approach to keyword conflicts

This directive acts as a **syntax guardian** preventing reserved keyword violations in generated code.

---

## When to Apply

This directive applies when:
- **Keyword conflicts detected** - Identifier matches language reserved word
- **Cross-language code generation** - Generating code for multiple languages
- **Language migration** - Converting code between languages
- **Standard name unavailable** - AIFP standard conflicts with keyword
- **Syntax errors from keywords** - Compilation fails due to reserved words
- **Called by project directives**:
  - `project_file_write` - Check for keyword conflicts before writing
  - Works with `fp_language_standardization` - Complement to naming standards
  - Works with `fp_cross_language_wrappers` - Ensure wrapper names are valid

---

## Workflow

### Trunk: detect_keyword_conflicts

Scans identifiers to detect conflicts with language reserved keywords and generates safe alternatives.

**Steps**:
1. **Detect language** - Identify target programming language
2. **Load keyword list** - Get reserved keywords for language
3. **Scan identifiers** - Extract function names, variable names, type names
4. **Check for conflicts** - Compare identifiers against reserved keywords
5. **Generate alternatives** - Create safe replacement names
6. **Validate alternatives** - Ensure replacements don't create new conflicts

### Branches

**Branch 1: If keyword_conflict**
- **Then**: `rename_identifier`
- **Details**: Identifier matches reserved keyword
  - Examples: "type", "class", "interface", "match", "async"
  - Apply AIFP conflict resolution strategy:
    - Option 1: Add `aifp_` prefix → `aifp_type`
    - Option 2: Use descriptive alternative → `get_type`
    - Option 3: Add FP prefix → `fp_type`
  - Update all references consistently
  - Document conflict in comments
- **Result**: Returns renamed code

**Branch 2: If reserved_name**
- **Then**: `apply_safe_prefix`
- **Details**: Name is reserved but not keyword (special names)
  - Examples: Python's `__init__`, JavaScript's `constructor`
  - Apply systematic prefix strategy
  - Maintain naming pattern across codebase
- **Result**: Returns prefixed identifier

**Branch 3: If builtin_name_conflict**
- **Then**: `warn_and_suggest`
- **Details**: Name conflicts with built-in function
  - Examples: "map", "filter", "type", "list", "dict"
  - Usually acceptable (shadowing)
  - Warn user of potential confusion
  - Suggest alternative if in global scope
- **Result**: Returns warning with suggestion

**Branch 4: If no_conflict**
- **Then**: `mark_safe`
- **Details**: No keyword conflicts detected
  - Identifier is valid in target language
  - No reserved word collision
  - Safe to use as-is
- **Result**: Code passes check

**Fallback**: `prompt_user`
- **Details**: Unable to resolve automatically
  - Multiple conflicts
  - Complex naming situation
  - Ask user for preferred resolution
- **Result**: User provides alternative name

---

## Examples

### ✅ Compliant Code

**Safe Keyword Alternatives (Passes):**

```python
# Python - Reserved keyword conflicts resolved
def get_type(value):
    """
    Get type of value.

    AIFP Note: "type" is Python keyword, using "get_type"
    """
    return type(value).__name__

def aifp_match(pattern, value):
    """
    Pattern matching function.

    AIFP Note: "match" is Python 3.10+ keyword, using "aifp_match"
    """
    if pattern == value:
        return True
    return False

def check_value(value, predicate):
    """
    Check if value satisfies predicate.

    AIFP Note: "lambda" is keyword, using "predicate" parameter name
    """
    return predicate(value)
```

**Why Compliant**:
- All keyword conflicts resolved
- Clear documentation of why alternative names used
- Consistent naming strategy (get_*, aifp_*)
- No syntax errors

---

**Cross-Language Safe Naming (Passes):**

```javascript
// JavaScript - Reserved keyword conflicts avoided
function getClass(obj) {
    /**
     * Get class/type of object.
     *
     * AIFP Note: "class" is JS keyword, using "getClass"
     */
    return obj.constructor.name;
}

function fpInterface(methods) {
    /**
     * Define functional interface.
     *
     * AIFP Note: "interface" is reserved (TypeScript), using "fpInterface"
     */
    return methods;
}

function checkAsync(promise) {
    /**
     * Check if function is async.
     *
     * AIFP Note: "async" is keyword, using "checkAsync"
     */
    return promise instanceof Promise;
}
```

**Why Compliant**:
- JavaScript and TypeScript keyword conflicts resolved
- Consistent naming pattern (get*, fp*, check*)
- Forward-compatible with TypeScript
- Documented reasoning

---

### ❌ Non-Compliant Code

**Direct Keyword Usage (Violation):**

```python
# ❌ VIOLATION: Using Python reserved keywords
def type(value):
    """Get type of value."""
    return type(value)  # ← SyntaxError: invalid syntax

def class(name, methods):
    """Define a class."""
    return {"name": name, "methods": methods}  # ← SyntaxError

def lambda(x):
    """Create lambda function."""
    return x  # ← SyntaxError

# Problem:
# - "type", "class", "lambda" are Python keywords
# - Code will not compile
# - Syntax errors prevent execution
```

**Why Non-Compliant**:
- Direct use of reserved keywords as identifiers
- Syntax errors
- Code cannot compile
- Must rename

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Safe alternatives
def get_type(value):
    """
    Get type of value.

    AIFP Note: Renamed from "type" (Python keyword)
    """
    return type(value).__name__

def create_class(name, methods):
    """
    Define a class structure.

    AIFP Note: Renamed from "class" (Python keyword)
    """
    return {"name": name, "methods": methods}

def create_lambda(body):
    """
    Create lambda function.

    AIFP Note: Renamed from "lambda" (Python keyword)
    """
    return body
```

---

**TypeScript Interface Conflict (Violation):**

```typescript
// ❌ VIOLATION: Using TypeScript reserved words
function interface(methods: any): any {  // ← SyntaxError: Unexpected token
    return methods;
}

function implements(spec: any): any {  // ← SyntaxError
    return spec;
}

function type(value: any): string {  // ← Conflicts with "type" keyword
    return typeof value;
}

// Problem:
// - "interface", "implements", "type" are TypeScript keywords
// - Will not compile in TypeScript
// - Even JavaScript may have issues in strict mode
```

**Why Non-Compliant**:
- Reserved keywords used as function names
- TypeScript compilation errors
- Violates language syntax rules

**Refactored (Compliant):**

```typescript
// ✅ REFACTORED: TypeScript-safe naming
function createInterface(methods: any): any {
    /**
     * Create interface specification.
     *
     * AIFP Note: "interface" is TypeScript keyword
     */
    return methods;
}

function implementsSpec(spec: any): any {
    /**
     * Implement specification.
     *
     * AIFP Note: "implements" is TypeScript keyword
     */
    return spec;
}

function getType(value: any): string {
    /**
     * Get runtime type.
     *
     * AIFP Note: "type" is TypeScript keyword
     */
    return typeof value;
}
```

---

**Go Reserved Name Conflict (Violation):**

```go
// ❌ VIOLATION: Using Go reserved words
package main

func type(value interface{}) string {  // ← Syntax error
    return fmt.Sprintf("%T", value)
}

func interface(methods []string) map[string]interface{} {  // ← Syntax error
    return make(map[string]interface{})
}

func func(name string) string {  // ← Syntax error
    return name
}

// Problem:
// - "type", "interface", "func" are Go keywords
// - Code will not compile
// - Invalid Go syntax
```

**Why Non-Compliant**:
- Go keywords used as function names
- Compilation errors
- Invalid syntax

**Refactored (Compliant):**

```go
// ✅ REFACTORED: Go-safe naming
package main

import "fmt"

// GetType returns the type of a value
// AIFP Note: "type" is Go keyword, using "GetType"
func GetType(value interface{}) string {
    return fmt.Sprintf("%T", value)
}

// CreateInterface creates interface specification
// AIFP Note: "interface" is Go keyword, using "CreateInterface"
func CreateInterface(methods []string) map[string]interface{} {
    return make(map[string]interface{})
}

// CreateFunc creates function specification
// AIFP Note: "func" is Go keyword, using "CreateFunc"
func CreateFunc(name string) string {
    return name
}
```

---

## Edge Cases

### Edge Case 1: Context-Dependent Keywords

**Issue**: Some keywords are reserved only in specific contexts

**Handling**:
```python
# Python 3.10+: "match" is keyword only in match statements context

# ✅ Safe: "match" as parameter name in Python < 3.10
def find_match(pattern, text):
    """Find pattern match in text."""
    match = re.search(pattern, text)
    return match

# ❌ Risk: "match" as function name in Python 3.10+
def match(pattern, text):  # Conflicts with match statement
    return re.search(pattern, text)

# ✅ AIFP Solution: Use safe alternative always
def find_pattern(pattern, text):
    """
    Find pattern in text.

    AIFP Note: Avoiding "match" keyword conflict (Python 3.10+)
    """
    result = re.search(pattern, text)
    return result
```

**Directive Action**: Use safe alternatives even for context-dependent keywords.

---

### Edge Case 2: Soft Keywords vs Hard Keywords

**Issue**: Some languages have "soft" keywords that are contextual

**Handling**:
```typescript
// TypeScript: "async" is hard keyword, "await" only inside async

// ✅ Safe: "await" as identifier outside async context
function processAwait(value: any): any {
    return value;  // OK, not inside async function
}

// ❌ Risk: "await" inside async context
async function processValue(value: any): Promise<any> {
    const await = value;  // ← Error: "await" is keyword in async
    return await;
}

// ✅ AIFP Solution: Avoid soft keywords everywhere
async function processValue(value: any): Promise<any> {
    const result = value;  // Safe alternative
    return result;
}
```

**Directive Action**: Avoid soft keywords in all contexts for consistency.

---

### Edge Case 3: Future Reserved Words

**Issue**: Language may reserve words for future use

**Handling**:
```javascript
// JavaScript: Some identifiers reserved for future

// ❌ Future-reserved words (in strict mode)
function implements() {}  // Reserved for future
function interface() {}   // Reserved for future
function package() {}     // Reserved for future

// ✅ AIFP Solution: Avoid all reserved words (current + future)
function implementsSpec() {
    /**
     * AIFP Note: "implements" is future-reserved keyword
     */
}

function createInterface() {
    /**
     * AIFP Note: "interface" is future-reserved keyword
     */
}

function createPackage() {
    /**
     * AIFP Note: "package" is future-reserved keyword
     */
}
```

**Directive Action**: Check both current and future reserved words.

---

## Language Keyword Tables

### Python Reserved Keywords

```
False, None, True, and, as, assert, async, await, break, class,
continue, def, del, elif, else, except, finally, for, from, global,
if, import, in, is, lambda, nonlocal, not, or, pass, raise, return,
try, while, with, yield, match (3.10+), case (3.10+), type (3.12+)
```

### JavaScript/TypeScript Reserved Keywords

```
break, case, catch, class, const, continue, debugger, default, delete,
do, else, enum, export, extends, false, finally, for, function, if,
import, in, instanceof, new, null, return, super, switch, this, throw,
true, try, typeof, var, void, while, with, yield, let, static,
implements, interface, package, private, protected, public, async, await
```

### Rust Reserved Keywords

```
as, break, const, continue, crate, else, enum, extern, false, fn, for,
if, impl, in, let, loop, match, mod, move, mut, pub, ref, return, self,
Self, static, struct, super, trait, true, type, unsafe, use, where, while,
async, await, dyn, abstract, become, box, do, final, macro, override,
priv, typeof, unsized, virtual, yield
```

### Go Reserved Keywords

```
break, case, chan, const, continue, default, defer, else, fallthrough,
for, func, go, goto, if, import, interface, map, package, range, return,
select, struct, switch, type, var
```

---

## AIFP Conflict Resolution Strategies

### Strategy 1: Descriptive Prefix
```
keyword → action_keyword
type → get_type, check_type
class → create_class, define_class
match → find_match, check_match
```

### Strategy 2: AIFP Namespace Prefix
```
keyword → aifp_keyword
type → aifp_type
class → aifp_class
interface → aifp_interface
```

### Strategy 3: FP Domain Prefix
```
keyword → fp_keyword
type → fp_type
match → fp_match
```

### Strategy 4: Underscore Suffix (Last Resort)
```
keyword → keyword_
type → type_
class → class_
```

**Preferred Order**: Descriptive > AIFP namespace > FP domain > Underscore

---

## Related Directives

- **Depends On**:
  - `fp_language_standardization` - Works with naming standards
- **Triggers**:
  - `fp_syntax_normalization` - May need syntax adjustments
- **Called By**:
  - `project_file_write` - Validate no keyword conflicts before writing
- **Escalates To**: None

---

## Helper Functions Used

- `get_language_keywords(language: str) -> set[str]` - Get reserved keywords
- `detect_keyword_conflict(identifier: str, keywords: set[str]) -> bool` - Check conflict
- `generate_safe_alternative(identifier: str, strategy: str) -> str` - Create safe name
- `validate_identifier(identifier: str, language: str) -> bool` - Verify validity
- `update_functions_table(func_id: int, renamed: bool)` - Update database

---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `keyword_safe = 1` for conflict-free functions
- **`notes`**: Logs keyword conflict resolutions with `note_type = 'refactoring'`

---

## Testing

How to verify this directive is working:

1. **Keyword conflict detected** → Directive renames automatically
   ```python
   # Before: def type(value)
   # After: def get_type(value)
   ```

2. **Safe alternative generated** → Follows naming strategy
   ```python
   # Conflict with "class" → "create_class"
   # Conflict with "match" → "aifp_match"
   ```

3. **Check database** → Verify keyword safety marked
   ```sql
   SELECT name, keyword_safe
   FROM functions
   WHERE keyword_safe = 1;
   ```

---

## Common Mistakes

- ❌ **Ignoring future reserved words** - Code breaks in newer language versions
- ❌ **Inconsistent conflict resolution** - Mix of strategies
- ❌ **Using underscore prefix** - Reserved for language internal use
- ❌ **Shadowing built-ins carelessly** - Causes confusion
- ❌ **Not documenting why alternative used** - Unclear to readers

---

## Roadblocks and Resolutions

### Roadblock 1: keyword_conflict
**Issue**: Identifier matches language reserved keyword
**Resolution**: Apply AIFP conflict resolution strategy (descriptive prefix preferred)

### Roadblock 2: multiple_languages_different_conflicts
**Issue**: Name valid in one language but keyword in another
**Resolution**: Use universally safe name across all target languages

### Roadblock 3: preferred_name_unavailable
**Issue**: Desired alternative also conflicts
**Resolution**: Try fallback strategies in order (descriptive → namespace → domain → suffix)

### Roadblock 4: builtin_shadowing
**Issue**: Name shadows built-in function
**Resolution**: Warn user, suggest alternative if in global scope

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-keyword-alignment)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#language-adaptation)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for reserved keyword conflict resolution*
