# fp_pattern_matching

## Purpose

The `fp_pattern_matching` directive promotes declarative pattern matching constructs for control flow instead of nested if/else chains. It analyzes conditional logic and converts imperative branching into pattern matching structures (match/case statements), ensuring cleaner, more maintainable, and AI-friendly decision logic across all supported languages.

**Category**: Control Flow
**Type**: FP Core
**Priority**: High
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`analyze_conditionals`**: Scan function bodies for conditional statements (if/else, switch, nested conditionals) to identify opportunities for pattern matching conversion.

### Branches

1. **`nested_conditionals`** → **`convert_to_match`**
   - **Condition**: Detects deeply nested if/else chains (3+ levels) or type-checking conditionals
   - **Action**: Convert to pattern matching construct (match/case)
   - **Details**: Extract patterns, create match expression with exhaustive cases
   - **Output**: Pattern matching code structure

2. **`static_patterns`** → **`create_case_structures`**
   - **Condition**: Detects static value comparisons or discriminated unions
   - **Action**: Create case-based structures with explicit patterns
   - **Details**: Map each condition to a pattern case
   - **Output**: Match/case structure with all patterns

3. **`already_using_match`** → **`mark_compliant`**
   - **Condition**: Function already uses pattern matching constructs
   - **Action**: Mark as FP-compliant and record in database
   - **Output**: Compliance confirmation

4. **`ambiguous_pattern`** → **`prompt_user`**
   - **Condition**: Pattern structure unclear or requires domain knowledge
   - **Action**: Request user clarification on pattern mapping
   - **Details**: Present options for pattern structure

5. **Fallback** → **`mark_compliant`**
   - **Condition**: No nested conditionals or already optimal
   - **Action**: Mark as compliant, no changes needed

### Error Handling
- **On failure**: Prompt user with context about conditional structure
- **Low confidence** (< 0.7): Request user review before refactoring

---

## Refactoring Strategies

### Strategy 1: Type-Based Pattern Matching
Convert type-checking conditionals to discriminated union matching.

**Before (Python - Non-Compliant)**:
```python
def process_response(response):
    if isinstance(response, SuccessResponse):
        return format_success(response.data)
    elif isinstance(response, ErrorResponse):
        return format_error(response.error)
    elif isinstance(response, PendingResponse):
        return format_pending(response.status)
    else:
        return "Unknown response"
```

**After (Python - Compliant)**:
```python
from dataclasses import dataclass
from typing import Union, Literal

@dataclass(frozen=True)
class SuccessResponse:
    kind: Literal["success"] = "success"
    data: dict

@dataclass(frozen=True)
class ErrorResponse:
    kind: Literal["error"] = "error"
    error: str

@dataclass(frozen=True)
class PendingResponse:
    kind: Literal["pending"] = "pending"
    status: str

Response = Union[SuccessResponse, ErrorResponse, PendingResponse]

def process_response(response: Response) -> str:
    match response:
        case SuccessResponse(data=data):
            return format_success(data)
        case ErrorResponse(error=error):
            return format_error(error)
        case PendingResponse(status=status):
            return format_pending(status)
        case _:
            return "Unknown response"
```

### Strategy 2: Value-Based Pattern Matching
Convert nested value comparisons to match expressions.

**Before (Python - Non-Compliant)**:
```python
def calculate_discount(customer_type, order_total):
    if customer_type == "premium":
        if order_total >= 1000:
            return order_total * 0.20
        elif order_total >= 500:
            return order_total * 0.15
        else:
            return order_total * 0.10
    elif customer_type == "regular":
        if order_total >= 500:
            return order_total * 0.10
        else:
            return order_total * 0.05
    else:
        return 0
```

**After (Python - Compliant)**:
```python
def calculate_discount(customer_type: str, order_total: float) -> float:
    match (customer_type, order_total):
        case ("premium", total) if total >= 1000:
            return total * 0.20
        case ("premium", total) if total >= 500:
            return total * 0.15
        case ("premium", total):
            return total * 0.10
        case ("regular", total) if total >= 500:
            return total * 0.10
        case ("regular", total):
            return total * 0.05
        case _:
            return 0.0
```

### Strategy 3: JavaScript/TypeScript Discriminated Unions
Convert type guards to discriminated union matching.

**Before (TypeScript - Non-Compliant)**:
```typescript
type Success = { status: 'success'; data: string };
type Error = { status: 'error'; message: string };
type Loading = { status: 'loading' };
type State = Success | Error | Loading;

function renderState(state: State): string {
  if (state.status === 'success') {
    return `Success: ${state.data}`;
  } else if (state.status === 'error') {
    return `Error: ${state.message}`;
  } else if (state.status === 'loading') {
    return 'Loading...';
  } else {
    return 'Unknown';
  }
}
```

**After (TypeScript - Compliant)**:
```typescript
type Success = { status: 'success'; data: string };
type Error = { status: 'error'; message: string };
type Loading = { status: 'loading' };
type State = Success | Error | Loading;

function renderState(state: State): string {
  switch (state.status) {
    case 'success':
      return `Success: ${state.data}`;
    case 'error':
      return `Error: ${state.message}`;
    case 'loading':
      return 'Loading...';
    default:
      const exhaustive: never = state;
      return exhaustive;
  }
}
```

### Strategy 4: Rust Native Pattern Matching
Leverage Rust's native match expressions for enum handling.

**Before (Rust - Non-Compliant)**:
```rust
enum PaymentMethod {
    CreditCard(String),
    PayPal(String),
    Bitcoin(String),
}

fn process_payment(method: PaymentMethod) -> String {
    if let PaymentMethod::CreditCard(card_number) = method {
        format!("Processing credit card: {}", card_number)
    } else if let PaymentMethod::PayPal(email) = method {
        format!("Processing PayPal: {}", email)
    } else if let PaymentMethod::Bitcoin(address) = method {
        format!("Processing Bitcoin: {}", address)
    } else {
        String::from("Unknown payment method")
    }
}
```

**After (Rust - Compliant)**:
```rust
enum PaymentMethod {
    CreditCard(String),
    PayPal(String),
    Bitcoin(String),
}

fn process_payment(method: PaymentMethod) -> String {
    match method {
        PaymentMethod::CreditCard(card_number) => {
            format!("Processing credit card: {}", card_number)
        }
        PaymentMethod::PayPal(email) => {
            format!("Processing PayPal: {}", email)
        }
        PaymentMethod::Bitcoin(address) => {
            format!("Processing Bitcoin: {}", address)
        }
    }
}
```

---

## Examples

### Example 1: HTTP Status Code Handling

**Non-Compliant** (Nested if/else):
```python
def handle_http_response(status_code, body):
    if status_code >= 200 and status_code < 300:
        return {"success": True, "data": body}
    elif status_code >= 400 and status_code < 500:
        return {"success": False, "error": "Client error", "data": body}
    elif status_code >= 500:
        return {"success": False, "error": "Server error", "data": body}
    else:
        return {"success": False, "error": "Unknown status"}
```

**Compliant** (Pattern matching with guards):
```python
from typing import Literal, Union
from dataclasses import dataclass

@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    body: str

def handle_http_response(response: HttpResponse) -> dict:
    match response.status_code:
        case code if 200 <= code < 300:
            return {"success": True, "data": response.body}
        case code if 400 <= code < 500:
            return {"success": False, "error": "Client error", "data": response.body}
        case code if 500 <= code:
            return {"success": False, "error": "Server error", "data": response.body}
        case _:
            return {"success": False, "error": "Unknown status"}
```

### Example 2: Command Parser

**Non-Compliant** (JavaScript):
```javascript
function parseCommand(input) {
  if (input.startsWith('add ')) {
    const value = input.substring(4);
    return { type: 'add', value: value };
  } else if (input.startsWith('remove ')) {
    const value = input.substring(7);
    return { type: 'remove', value: value };
  } else if (input === 'clear') {
    return { type: 'clear' };
  } else if (input === 'help') {
    return { type: 'help' };
  } else {
    return { type: 'unknown' };
  }
}
```

**Compliant** (JavaScript with pattern-like dispatch):
```javascript
const commandPatterns = [
  { pattern: /^add (.+)$/, handler: (match) => ({ type: 'add', value: match[1] }) },
  { pattern: /^remove (.+)$/, handler: (match) => ({ type: 'remove', value: match[1] }) },
  { pattern: /^clear$/, handler: () => ({ type: 'clear' }) },
  { pattern: /^help$/, handler: () => ({ type: 'help' }) },
];

function parseCommand(input) {
  for (const { pattern, handler } of commandPatterns) {
    const match = input.match(pattern);
    if (match) {
      return handler(match);
    }
  }
  return { type: 'unknown' };
}
```

### Example 3: AST Node Processing

**Compliant** (Rust with comprehensive pattern matching):
```rust
enum ASTNode {
    Number(i32),
    BinaryOp { left: Box<ASTNode>, op: String, right: Box<ASTNode> },
    Variable(String),
    FunctionCall { name: String, args: Vec<ASTNode> },
}

fn evaluate_ast(node: ASTNode) -> i32 {
    match node {
        ASTNode::Number(n) => n,
        ASTNode::BinaryOp { left, op, right } => {
            let l = evaluate_ast(*left);
            let r = evaluate_ast(*right);
            match op.as_str() {
                "+" => l + r,
                "-" => l - r,
                "*" => l * r,
                "/" => l / r,
                _ => 0,
            }
        }
        ASTNode::Variable(name) => {
            // Look up variable (simplified)
            0
        }
        ASTNode::FunctionCall { name, args } => {
            // Call function (simplified)
            0
        }
    }
}
```

---

## Edge Cases

### Edge Case 1: Dynamic Pattern Matching
**Scenario**: Pattern depends on runtime configuration or external data
**Issue**: Cannot statically determine all patterns at compile time
**Handling**:
- Use dispatch table mapping for runtime patterns
- Maintain static type safety with discriminated unions
- Document dynamic behavior in function metadata

**Example**:
```python
# Dynamic pattern dispatch table
def create_handler_map(config):
    return {
        "mode_a": lambda x: process_mode_a(x, config),
        "mode_b": lambda x: process_mode_b(x, config),
        "mode_c": lambda x: process_mode_c(x, config),
    }

def process_with_mode(mode: str, data: dict, config: dict) -> dict:
    handlers = create_handler_map(config)
    handler = handlers.get(mode, lambda x: {"error": "Unknown mode"})
    return handler(data)
```

### Edge Case 2: Incomplete Pattern Coverage
**Scenario**: Not all possible values are covered in pattern match
**Issue**: Runtime errors or undefined behavior for unhandled cases
**Handling**:
- Add exhaustive default case (`_` wildcard)
- Use type system to enforce exhaustiveness (TypeScript `never`, Rust compiler checks)
- Log warnings for unhandled patterns

**Example** (TypeScript):
```typescript
function exhaustiveCheck(value: never): never {
  throw new Error(`Unhandled case: ${value}`);
}

function handleState(state: State): string {
  switch (state.status) {
    case 'success':
      return state.data;
    case 'error':
      return state.message;
    case 'loading':
      return 'Loading...';
    default:
      return exhaustiveCheck(state); // Compile error if new state added
  }
}
```

### Edge Case 3: Pattern Matching on Complex Objects
**Scenario**: Matching on deeply nested object structures
**Issue**: Pattern matching syntax becomes verbose and hard to read
**Handling**:
- Extract nested patterns into separate functions
- Use helper functions for complex condition checking
- Consider flattening data structures

**Example**:
```python
# Complex nested pattern - extract to helper
def is_premium_large_order(order):
    return (
        order.customer.type == "premium" and
        order.total >= 1000 and
        order.items_count > 10
    )

def calculate_shipping(order: Order) -> float:
    match order:
        case order if is_premium_large_order(order):
            return 0.0  # Free shipping
        case Order(customer=Customer(type="premium")):
            return 5.0
        case Order(total=total) if total >= 500:
            return 10.0
        case _:
            return 15.0
```

### Edge Case 4: Language Without Native Pattern Matching
**Scenario**: Target language (e.g., older JavaScript, Go) lacks native pattern matching
**Issue**: Cannot directly translate match expressions
**Handling**:
- Use dispatch tables with type tags
- Implement if/else chains but structure them declaratively
- Document pattern intent in comments

**Example** (Go):
```go
type ResponseType int

const (
    SuccessType ResponseType = iota
    ErrorType
    PendingType
)

type Response struct {
    Type    ResponseType
    Data    string
    Error   string
    Status  string
}

// Pattern-like dispatch using type switch alternative
func ProcessResponse(r Response) string {
    handlers := map[ResponseType]func(Response) string{
        SuccessType: func(r Response) string {
            return "Success: " + r.Data
        },
        ErrorType: func(r Response) string {
            return "Error: " + r.Error
        },
        PendingType: func(r Response) string {
            return "Pending: " + r.Status
        },
    }

    if handler, ok := handlers[r.Type]; ok {
        return handler(r)
    }
    return "Unknown response type"
}
```

### Edge Case 5: Performance-Critical Pattern Matching
**Scenario**: Pattern matching in hot path with performance requirements
**Issue**: Complex pattern matching can introduce overhead
**Handling**:
- Profile and benchmark critical sections
- Consider switch statements over complex match for simple cases
- Cache pattern results if patterns are expensive to evaluate
- Use early returns for most common patterns

---

## Database Operations

### Insert Pattern Matching Metadata

When converting to pattern matching, record the transformation:

```sql
-- Update function record
UPDATE functions
SET
    control_flow_style = 'pattern_matching',
    complexity_score = 2,  -- Reduced from 5 (nested if/else)
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'process_response' AND file_id = ?;
```

### Query Functions Needing Pattern Matching

```sql
-- Find functions with high conditional complexity
SELECT f.id, f.name, f.file_id, f.complexity_score
FROM functions f
WHERE f.control_flow_style IN ('if_else', 'nested_conditionals')
  AND f.complexity_score > 3
ORDER BY f.complexity_score DESC;
```

---

## Related Directives

### FP Directives
- **fp_guard_clauses**: Complementary for early returns and validation
- **fp_conditional_elimination**: Converts imperative conditionals to expressions
- **fp_adt**: Defines discriminated unions for pattern matching
- **fp_type_safety**: Ensures exhaustive pattern matching via type system

### Project Directives
- **project_compliance_check**: Validates pattern matching usage
- **project_update_db**: Records pattern matching transformations

---

## Helper Functions

### `detect_nested_conditionals(ast) -> list[ConditionalNode]`
Analyzes AST to find nested conditional structures.

**Signature**:
```python
def detect_nested_conditionals(ast: ASTNode) -> list[ConditionalNode]:
    """
    Scans AST for nested if/else chains (3+ levels).
    Returns list of conditional nodes with nesting depth.
    """
```

### `generate_match_structure(conditionals, language) -> str`
Generates pattern matching code from conditional analysis.

**Signature**:
```python
def generate_match_structure(
    conditionals: list[ConditionalNode],
    language: str
) -> str:
    """
    Creates pattern matching code structure for target language.
    Supports: Python (match/case), TypeScript (switch), Rust (match).
    """
```

### `extract_discriminator(type_union) -> str`
Identifies discriminator field in discriminated union.

**Signature**:
```python
def extract_discriminator(type_union: TypeDefinition) -> str:
    """
    Extracts discriminator field name from union type definition.
    Example: For Union[Ok, Err], returns "kind" or "status".
    """
```

---

## Testing

### Test 1: Nested Conditional Conversion
```python
def test_convert_nested_to_match():
    # Non-compliant nested conditionals
    source = """
def classify(x):
    if x < 0:
        if x < -10:
            return "very negative"
        else:
            return "negative"
    elif x > 0:
        if x > 10:
            return "very positive"
        else:
            return "positive"
    else:
        return "zero"
"""

    result = fp_pattern_matching.refactor(source, language="python")

    # Should convert to pattern matching with guards
    assert "match" in result
    assert "case x if x < -10:" in result
    assert "case x if x > 10:" in result
```

### Test 2: Discriminated Union Pattern
```python
def test_discriminated_union_pattern():
    source = """
@dataclass
class Ok:
    kind: Literal["ok"] = "ok"
    value: int

@dataclass
class Err:
    kind: Literal["err"] = "err"
    error: str

def unwrap(result):
    if isinstance(result, Ok):
        return result.value
    else:
        raise Exception(result.error)
"""

    result = fp_pattern_matching.refactor(source, language="python")

    assert "match result:" in result
    assert "case Ok(value=v):" in result
    assert "case Err(error=e):" in result
```

### Test 3: Exhaustiveness Check
```typescript
// Should fail TypeScript compilation if pattern incomplete
type Status = 'pending' | 'approved' | 'rejected';

function handleStatus(status: Status): string {
  switch (status) {
    case 'pending':
      return 'Waiting';
    case 'approved':
      return 'Approved';
    // Missing 'rejected' case - should trigger exhaustiveCheck error
    default:
      const _exhaustive: never = status;
      return _exhaustive;
  }
}
```

---

## Common Mistakes

### Mistake 1: Forgetting Exhaustive Default Case
**Problem**: Missing `_` or `default` case leads to runtime errors

**Solution**: Always include exhaustive default case, even if it's unreachable

```python
# ❌ Bad: Missing default
match response:
    case SuccessResponse():
        return "OK"
    case ErrorResponse():
        return "Error"
    # Missing default - what if new type added?

# ✅ Good: Exhaustive default
match response:
    case SuccessResponse():
        return "OK"
    case ErrorResponse():
        return "Error"
    case _:
        raise ValueError(f"Unknown response type: {type(response)}")
```

### Mistake 2: Over-Nesting Pattern Matches
**Problem**: Nesting multiple match expressions reduces readability

**Solution**: Extract nested patterns into separate functions

```python
# ❌ Bad: Nested match
match outer:
    case TypeA(inner):
        match inner:
            case SubType1():
                return "A1"
            case SubType2():
                return "A2"
    case TypeB():
        return "B"

# ✅ Good: Extract to helper
def handle_inner(inner):
    match inner:
        case SubType1():
            return "A1"
        case SubType2():
            return "A2"

match outer:
    case TypeA(inner):
        return handle_inner(inner)
    case TypeB():
        return "B"
```

### Mistake 3: Complex Guard Conditions
**Problem**: Guard conditions become too complex and hard to understand

**Solution**: Extract guards into named boolean functions

```python
# ❌ Bad: Complex inline guard
match order:
    case order if order.total > 1000 and order.customer.type == "premium" and len(order.items) > 5:
        return calculate_premium_discount(order)

# ✅ Good: Named guard function
def is_premium_bulk_order(order):
    return (
        order.total > 1000 and
        order.customer.type == "premium" and
        len(order.items) > 5
    )

match order:
    case order if is_premium_bulk_order(order):
        return calculate_premium_discount(order)
```

---

## Roadblocks

### Roadblock 1: Deep If/Else Chains
**Issue**: Nested if/else chains 5+ levels deep
**Resolution**: Convert to pattern matching with discriminated unions or dispatch tables

### Roadblock 2: Ambiguous Patterns
**Issue**: Pattern structure unclear or requires domain knowledge
**Resolution**: Prompt user for clarification on pattern mapping and expected cases

### Roadblock 3: Language Lacks Pattern Matching
**Issue**: Target language doesn't support native pattern matching (older JS, Go)
**Resolution**: Use dispatch tables with type tags or structured if/else chains

### Roadblock 4: Runtime Pattern Determination
**Issue**: Patterns depend on runtime configuration
**Resolution**: Use dispatch table mapping with static type safety via discriminated unions

---

## Integration Points

### With `fp_guard_clauses`
Pattern matching works well with guard clauses for input validation before pattern matching logic.

### With `fp_conditional_elimination`
Pattern matching is the preferred method for eliminating imperative conditionals.

### With `fp_adt`
Algebraic Data Types (discriminated unions) enable type-safe exhaustive pattern matching.

### With `project_compliance_check`
Validates that complex conditionals have been converted to pattern matching.

---

## Intent Keywords

- `pattern match`
- `case`
- `control flow`
- `match expression`
- `discriminated union`
- `exhaustive matching`

---

## Confidence Threshold

**0.7** - High confidence required for automatic pattern matching conversion due to potential logic changes.

---

## Notes

- Python 3.10+ required for native `match`/`case` syntax
- TypeScript uses `switch` with discriminated unions and exhaustiveness checking
- Rust has first-class pattern matching support with compile-time exhaustiveness
- For languages without native support, use dispatch tables or structured conditionals
- Pattern matching reduces cyclomatic complexity and improves code readability
- Always ensure exhaustive pattern coverage to prevent runtime errors
