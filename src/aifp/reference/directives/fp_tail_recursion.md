# fp_tail_recursion

## Purpose

The `fp_tail_recursion` directive refactors recursive calls to use tail recursion for stack safety and performance optimization. It analyzes recursive functions and transforms non-tail-recursive calls into tail-call-optimized forms or iterative equivalents, ensuring AI-generated code doesn't cause stack overflows and maintains functional purity while enabling compiler/interpreter optimizations.

**Category**: Control Flow
**Type**: FP Core
**Priority**: High
**Confidence Threshold**: 0.6

---

## Workflow

### Trunk
**`analyze_recursion`**: Scan function bodies for recursive calls and determine if they are in tail position (last operation before return).

### Branches

1. **`non_tail_recursion`** → **`refactor_to_tail_call`**
   - **Condition**: Detects recursive calls not in tail position (e.g., followed by operations)
   - **Action**: Transform to tail-recursive form using accumulator parameters
   - **Details**: Add accumulator parameters, move operations before recursive call
   - **Output**: Tail-recursive function with accumulator

2. **`deep_recursion_risk`** → **`convert_to_iteration`**
   - **Condition**: Recursion depth analysis indicates potential stack overflow risk
   - **Action**: Convert to iterative loop with explicit stack/queue if needed
   - **Details**: Transform recursion to while/for loop maintaining functional style
   - **Output**: Iterative equivalent or trampolined version

3. **`already_tail_recursive`** → **`mark_as_optimized`**
   - **Condition**: Function already uses tail recursion
   - **Action**: Mark as optimized and record in database
   - **Output**: Compliance confirmation

4. **`mutual_recursion`** → **`apply_trampoline`**
   - **Condition**: Detects mutually recursive functions (A calls B, B calls A)
   - **Action**: Apply trampoline pattern to prevent stack growth
   - **Details**: Wrap recursive calls in thunks, evaluate with trampoline runner
   - **Output**: Trampolined mutual recursion

5. **Fallback** → **`mark_as_optimized`**
   - **Condition**: No recursion detected or already optimal
   - **Action**: Mark as compliant

### Error Handling
- **On failure**: Prompt user with recursion analysis details
- **Low confidence** (< 0.6): Request user review before transformation

---

## Refactoring Strategies

### Strategy 1: Accumulator Pattern for Tail Recursion
Convert non-tail recursion to tail recursion using accumulator parameters.

**Before (Python - Non-Compliant)**:
```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)  # Not tail recursive (multiplication after call)
```

**After (Python - Compliant)**:
```python
def factorial(n: int, acc: int = 1) -> int:
    """Tail-recursive factorial with accumulator."""
    if n <= 1:
        return acc
    return factorial(n - 1, n * acc)  # Tail recursive (no operation after call)
```

### Strategy 2: List Processing with Tail Recursion
Convert head-recursive list operations to tail-recursive with accumulator.

**Before (Python - Non-Compliant)**:
```python
def sum_list(items):
    if not items:
        return 0
    return items[0] + sum_list(items[1:])  # Not tail recursive (addition after call)
```

**After (Python - Compliant)**:
```python
def sum_list(items: list[int], acc: int = 0) -> int:
    """Tail-recursive list sum with accumulator."""
    if not items:
        return acc
    return sum_list(items[1:], acc + items[0])  # Tail recursive
```

**Alternative (Using reduce for better performance)**:
```python
from functools import reduce

def sum_list(items: list[int]) -> int:
    """Functional reduce alternative to recursion."""
    return reduce(lambda acc, x: acc + x, items, 0)
```

### Strategy 3: Tree Traversal with Continuation Passing Style
For complex recursion, use continuation-passing style (CPS) to achieve tail calls.

**Before (Python - Non-Compliant)**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TreeNode:
    value: int
    left: Optional['TreeNode'] = None
    right: Optional['TreeNode'] = None

def tree_sum(node: Optional[TreeNode]) -> int:
    if node is None:
        return 0
    return node.value + tree_sum(node.left) + tree_sum(node.right)  # Not tail recursive
```

**After (Python - Compliant with explicit stack)**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TreeNode:
    value: int
    left: Optional['TreeNode'] = None
    right: Optional['TreeNode'] = None

def tree_sum(node: Optional[TreeNode]) -> int:
    """Iterative tree sum with explicit stack (tail-call equivalent)."""
    if node is None:
        return 0

    stack = [node]
    total = 0

    while stack:
        current = stack.pop()
        total += current.value
        if current.right:
            stack.append(current.right)
        if current.left:
            stack.append(current.left)

    return total
```

### Strategy 4: Trampoline Pattern for Mutual Recursion
Handle mutually recursive functions with trampoline pattern.

**Before (JavaScript - Non-Compliant)**:
```javascript
function isEven(n) {
  if (n === 0) return true;
  return isOdd(n - 1);
}

function isOdd(n) {
  if (n === 0) return false;
  return isEven(n - 1);  // Mutual recursion causes stack growth
}

// isEven(10000) -> Stack overflow!
```

**After (JavaScript - Compliant with Trampoline)**:
```javascript
// Trampoline runner
function trampoline(fn) {
  let result = fn();
  while (typeof result === 'function') {
    result = result();
  }
  return result;
}

// Return thunks instead of direct recursive calls
function isEven(n) {
  if (n === 0) return true;
  return () => isOdd(n - 1);  // Return thunk
}

function isOdd(n) {
  if (n === 0) return false;
  return () => isEven(n - 1);  // Return thunk
}

// Usage: trampoline(() => isEven(10000)) -> No stack overflow!
const result = trampoline(() => isEven(10000));
```

### Strategy 5: Rust Tail Call Optimization
Leverage Rust's tail-call optimization capabilities.

**Before (Rust - Non-Optimal)**:
```rust
fn fibonacci(n: u64) -> u64 {
    if n <= 1 {
        return n;
    }
    fibonacci(n - 1) + fibonacci(n - 2)  // Exponential time, not tail recursive
}
```

**After (Rust - Tail-Recursive with Accumulator)**:
```rust
fn fibonacci(n: u64) -> u64 {
    fn fib_tail(n: u64, a: u64, b: u64) -> u64 {
        if n == 0 {
            return a;
        }
        fib_tail(n - 1, b, a + b)  // Tail recursive
    }
    fib_tail(n, 0, 1)
}
```

---

## Examples

### Example 1: List Reversal

**Non-Compliant** (Non-tail recursive):
```python
def reverse_list(items):
    if not items:
        return []
    return reverse_list(items[1:]) + [items[0]]  # Not tail recursive
```

**Compliant** (Tail recursive with accumulator):
```python
def reverse_list(items: list, acc: list = None) -> list:
    """Tail-recursive list reversal."""
    if acc is None:
        acc = []
    if not items:
        return acc
    return reverse_list(items[1:], [items[0]] + acc)  # Tail recursive
```

### Example 2: String Processing

**Non-Compliant** (TypeScript):
```typescript
function countVowels(str: string): number {
  if (str.length === 0) return 0;
  const first = str[0].toLowerCase();
  const isVowel = ['a', 'e', 'i', 'o', 'u'].includes(first) ? 1 : 0;
  return isVowel + countVowels(str.slice(1));  // Not tail recursive
}
```

**Compliant** (TypeScript with accumulator):
```typescript
function countVowels(str: string, acc: number = 0): number {
  if (str.length === 0) return acc;
  const first = str[0].toLowerCase();
  const isVowel = ['a', 'e', 'i', 'o', 'u'].includes(first) ? 1 : 0;
  return countVowels(str.slice(1), acc + isVowel);  // Tail recursive
}
```

### Example 3: Deep Tree Search

**Compliant** (Rust with explicit stack - iterative equivalent):
```rust
#[derive(Debug)]
struct TreeNode {
    value: i32,
    left: Option<Box<TreeNode>>,
    right: Option<Box<TreeNode>>,
}

fn find_value(root: Option<Box<TreeNode>>, target: i32) -> bool {
    let mut stack = Vec::new();
    if let Some(node) = root {
        stack.push(node);
    }

    while let Some(node) = stack.pop() {
        if node.value == target {
            return true;
        }
        if let Some(right) = node.right {
            stack.push(right);
        }
        if let Some(left) = node.left {
            stack.push(left);
        }
    }

    false
}
```

---

## Edge Cases

### Edge Case 1: Multiple Recursive Calls (Binary Recursion)
**Scenario**: Function makes multiple recursive calls (e.g., tree traversal, Fibonacci)
**Issue**: Cannot directly convert to tail recursion with simple accumulator
**Handling**:
- Convert to iterative with explicit stack/queue
- Use continuation-passing style (CPS)
- Apply memoization for repeated computations

**Example**:
```python
# Binary recursion - use iteration instead
def fibonacci_iterative(n: int) -> int:
    """Iterative Fibonacci - avoids recursion entirely."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
```

### Edge Case 2: Recursion with Side Effects
**Scenario**: Recursive function performs I/O or mutation
**Issue**: Side effects make tail-call optimization unsafe or ineffective
**Handling**:
- Separate pure recursive logic from side effects
- Isolate effects to function boundaries
- Use effect handlers for I/O operations

**Example**:
```python
# ❌ Bad: Recursion with side effects
def print_countdown(n):
    if n <= 0:
        return
    print(n)  # Side effect!
    print_countdown(n - 1)

# ✅ Good: Separate pure logic from effects
def generate_countdown(n: int) -> list[int]:
    """Pure tail-recursive countdown generator."""
    if n <= 0:
        return []
    return generate_countdown(n - 1, [n] + acc) if acc else generate_countdown(n - 1, [n])

# Effect at boundary
def print_countdown_pure(n: int):
    countdown = generate_countdown(n)
    for num in countdown:
        print(num)
```

### Edge Case 3: Language Without TCO
**Scenario**: Target language doesn't support tail-call optimization (Python, JavaScript without strict mode)
**Issue**: Tail-recursive code still causes stack overflow
**Handling**:
- Convert to explicit iteration instead
- Use trampoline pattern for JavaScript
- Document recursion limits in Python

**Example** (Python with iteration):
```python
# Python doesn't optimize tail calls - use iteration
def factorial_iterative(n: int) -> int:
    """Iterative factorial - no stack growth."""
    result = 1
    while n > 1:
        result *= n
        n -= 1
    return result
```

### Edge Case 4: Indirect/Mutual Recursion
**Scenario**: Functions call each other recursively (A → B → A)
**Issue**: Traditional tail-call optimization doesn't handle mutual recursion
**Handling**:
- Apply trampoline pattern
- Combine into single function with state parameter
- Use continuation-passing style

**Example** (already shown in Strategy 4)

### Edge Case 5: Accumulator Type Complexity
**Scenario**: Accumulator requires complex data structure (tuple, dict, custom class)
**Issue**: Accumulator becomes hard to manage and reason about
**Handling**:
- Use immutable data structures (frozen dataclasses)
- Document accumulator semantics clearly
- Consider iterative approach if accumulator too complex

**Example**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class TraversalState:
    visited: frozenset
    path: tuple
    distance: int

def find_path_tail(
    graph: dict,
    current: str,
    target: str,
    state: TraversalState = None
) -> tuple | None:
    """Tail-recursive path finding with complex accumulator."""
    if state is None:
        state = TraversalState(frozenset(), tuple(), 0)

    if current == target:
        return state.path + (current,)

    if current in state.visited:
        return None

    new_state = TraversalState(
        visited=state.visited | {current},
        path=state.path + (current,),
        distance=state.distance + 1
    )

    for neighbor in graph.get(current, []):
        result = find_path_tail(graph, neighbor, target, new_state)
        if result:
            return result

    return None
```

---

## Database Operations

### Update Function with Tail Recursion Flag

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Query Functions Needing Tail Call Optimization

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Related Directives

### FP Directives
- **fp_recursion_enforcement**: Enforces recursion over iteration for FP style
- **fp_memoization**: Optimizes recursive functions with caching
- **fp_pattern_matching**: Used for base cases in recursive functions
- **fp_purity**: Ensures recursive functions remain pure

### Project Directives
- **project_compliance_check**: Validates tail recursion usage
- **project_update_db**: Records tail recursion transformations

---

## Helper Functions

### `is_tail_recursive(ast_node) -> bool`
Determines if a recursive call is in tail position.

**Signature**:
```python
def is_tail_recursive(ast_node: ASTNode) -> bool:
    """
    Checks if recursive call is in tail position (last operation before return).
    Returns True if tail-recursive, False otherwise.
    """
```

### `transform_to_tail_recursive(function_ast) -> ASTNode`
Transforms non-tail recursive function to tail-recursive with accumulator.

**Signature**:
```python
def transform_to_tail_recursive(function_ast: ASTNode) -> ASTNode:
    """
    Adds accumulator parameter and moves operations before recursive call.
    Returns transformed AST with tail-recursive function.
    """
```

### `estimate_recursion_depth(function_def, typical_input) -> int`
Estimates maximum recursion depth for typical inputs.

**Signature**:
```python
def estimate_recursion_depth(
    function_def: FunctionDefinition,
    typical_input: dict
) -> int:
    """
    Analyzes function logic to estimate recursion depth.
    Used to determine if conversion to iteration needed.
    """
```

---

## Testing

### Test 1: Tail Recursion Validation
```python
def test_is_tail_recursive():
    # Tail-recursive example
    tail_recursive_code = """
def factorial(n, acc=1):
    if n <= 1:
        return acc
    return factorial(n - 1, n * acc)
"""

    ast = parse_code(tail_recursive_code)
    assert is_tail_recursive(ast.body[0]) is True

    # Non-tail-recursive example
    non_tail_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

    ast = parse_code(non_tail_code)
    assert is_tail_recursive(ast.body[0]) is False
```

### Test 2: Accumulator Transformation
```python
def test_transform_to_accumulator():
    source = """
def sum_list(items):
    if not items:
        return 0
    return items[0] + sum_list(items[1:])
"""

    result = fp_tail_recursion.refactor(source, language="python")

    # Should add accumulator parameter
    assert "acc" in result
    assert "return sum_list(items[1:], acc + items[0])" in result
```

### Test 3: Stack Safety Verification
```python
def test_stack_safety():
    # Tail-recursive version should handle large inputs
    def factorial_tail(n, acc=1):
        if n <= 1:
            return acc
        return factorial_tail(n - 1, n * acc)

    # Should not raise RecursionError (up to Python's limit)
    # Note: Python doesn't optimize tail calls, but structure is correct
    try:
        result = factorial_tail(100)
        assert result > 0
    except RecursionError:
        pytest.fail("Tail-recursive function should handle moderate recursion")
```

---

## Common Mistakes

### Mistake 1: Forgetting to Update Accumulator
**Problem**: Accumulator not updated correctly in recursive call

**Solution**: Ensure accumulator captures all intermediate computations

```python
# ❌ Bad: Accumulator not updated
def factorial(n, acc=1):
    if n <= 1:
        return acc
    return factorial(n - 1, acc)  # BUG: Should be n * acc

# ✅ Good: Accumulator properly updated
def factorial(n, acc=1):
    if n <= 1:
        return acc
    return factorial(n - 1, n * acc)  # Correct
```

### Mistake 2: Operation After Recursive Call
**Problem**: Performing operation after recursive call defeats tail position

**Solution**: Move all operations before the recursive call

```python
# ❌ Bad: Operation after recursive call
def sum_list(items, acc=0):
    if not items:
        return acc
    return 1 + sum_list(items[1:], acc + items[0])  # +1 defeats tail position

# ✅ Good: All operations before recursive call
def sum_list(items, acc=0):
    if not items:
        return acc
    return sum_list(items[1:], acc + items[0] + 1)  # Correct
```

### Mistake 3: Mutable Accumulator
**Problem**: Using mutable accumulator breaks functional purity

**Solution**: Use immutable data structures for accumulator

```python
# ❌ Bad: Mutable accumulator
def collect_items(items, acc=[]):  # Mutable default!
    if not items:
        return acc
    acc.append(items[0])  # Mutation!
    return collect_items(items[1:], acc)

# ✅ Good: Immutable accumulator
def collect_items(items, acc=None):
    if acc is None:
        acc = ()  # Immutable tuple
    if not items:
        return acc
    return collect_items(items[1:], acc + (items[0],))  # New tuple
```

---

## Roadblocks

### Roadblock 1: Deep Recursion
**Issue**: Recursion depth analysis indicates potential stack overflow risk
**Resolution**: Convert to iteration or apply trampoline pattern

### Roadblock 2: Multiple Recursive Calls
**Issue**: Function makes multiple recursive calls (binary recursion)
**Resolution**: Use explicit stack/queue or continuation-passing style

### Roadblock 3: Side Effects in Recursion
**Issue**: Recursive function performs I/O or mutations
**Resolution**: Separate pure logic from effects, isolate to boundaries

### Roadblock 4: Language Without TCO
**Issue**: Target language doesn't optimize tail calls
**Resolution**: Convert to explicit iteration or document recursion limits

---

## Integration Points

### With `fp_purity`
Tail-recursive functions must remain pure (no side effects, deterministic).

### With `fp_memoization`
Tail-recursive functions can be memoized to avoid redundant computation.

### With `fp_recursion_enforcement`
Ensures recursion is used over loops, but in tail-recursive form for safety.

### With `project_compliance_check`
Validates that recursive functions are tail-call optimized where possible.

---

## Intent Keywords

- `tail recursion`
- `optimize recursion`
- `tail call`
- `accumulator`
- `stack safety`
- `trampoline`

---

## Confidence Threshold

**0.6** - Moderate confidence sufficient as tail recursion patterns are well-defined.

---

## Notes

- Python doesn't optimize tail calls - prefer iteration for deep recursion
- JavaScript in strict mode may optimize tail calls (ES6+)
- Rust and functional languages (Haskell, OCaml) optimize tail calls natively
- Always measure stack depth for critical recursive functions
- Tail recursion improves performance by enabling compiler optimizations
- Use trampoline pattern for mutual recursion to avoid stack growth
- Document maximum expected recursion depth in function metadata
