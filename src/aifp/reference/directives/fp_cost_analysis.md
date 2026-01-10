# Directive: fp_cost_analysis

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: LOW - Internal optimization heuristics

---

## Purpose

The `fp_cost_analysis` directive analyzes functions to estimate time and space complexity, feeding cost metadata into AIFP's internal reasoning for smarter optimization decisions. This directive provides **complexity analysis** that informs other directives about performance characteristics.

Cost analysis provides **optimization intelligence**, enabling:
- **Informed Optimization Decisions**: Know which functions are expensive
- **Smart Memoization**: Prioritize caching expensive functions
- **Hot Path Identification**: Focus optimization on costly operations
- **Complexity Awareness**: Understand algorithmic efficiency
- **Resource Planning**: Estimate memory and time requirements

This directive acts as a **performance profiler at the code level**, providing metadata that other directives use for optimization decisions.

---

## When to Apply

This directive applies when:
- **Analyzing new functions** - Estimate complexity for metadata
- **Before memoization** - Identify expensive functions worth caching
- **Optimization planning** - Prioritize high-cost functions
- **Performance audits** - Understand complexity distribution
- **Resource estimation** - Plan memory/CPU requirements
- **Called by project directives**:
  - `fp_memoization` - Consult cost analysis before caching
  - `project_task_decomposition` - Use cost for task sizing
  - Works with `project_performance_summary` - Report complexity metrics

---

## Workflow

### Trunk: analyze_function_complexity

Analyzes function code to estimate time and space complexity.

**Steps**:
1. **Parse function body** - Build AST for analysis
2. **Identify loops** - Count nested loops (indicate O(n²), O(n³), etc.)
3. **Identify recursion** - Detect recursive calls, estimate depth
4. **Analyze data structures** - Estimate memory allocation
5. **Count operations** - Estimate instruction count
6. **Classify complexity** - Assign Big-O notation
7. **Store metadata** - Update project.db with cost estimates

### Branches

**Branch 1: If nested_loops**
- **Then**: `estimate_polynomial_complexity`
- **Details**: Nested loops indicate polynomial time
  - Single loop: O(n)
  - Double nested: O(n²)
  - Triple nested: O(n³)
  - Estimate based on nesting depth
- **Result**: Returns complexity estimate

**Branch 2: If recursive_function**
- **Then**: `analyze_recursion_complexity`
- **Details**: Analyze recursive call patterns
  - Tail recursion: O(n) time, O(1) space
  - Binary recursion: O(2ⁿ) time (Fibonacci-like)
  - Divide-and-conquer: O(n log n) (merge sort-like)
  - Estimate based on pattern
- **Result**: Returns complexity estimate

**Branch 3: If constant_operations**
- **Then**: `mark_as_constant`
- **Details**: Function has constant complexity
  - No loops or recursion
  - Fixed number of operations
  - O(1) time and space
- **Result**: Returns O(1) estimate

**Branch 4: If complex_algorithm**
- **Then**: `detailed_analysis`
- **Details**: Complex algorithm requires deeper analysis
  - Multiple phases with different complexities
  - Amortized complexity analysis
  - Best/average/worst case scenarios
  - Detailed profiling recommended
- **Result**: Returns complexity range

**Branch 5: If uncertain**
- **Then**: `conservative_estimate`
- **Details**: Cannot determine complexity statically
  - Dynamic behavior
  - Complex control flow
  - Mark as "unknown" or worst-case estimate
- **Result**: Returns conservative estimate

**Fallback**: `prompt_user`
- **Details**: Ask user for complexity info
  - Present analysis findings
  - Request manual complexity annotation
  - User provides Big-O notation
- **Result**: User-provided complexity

---

## Examples

### ✅ Compliant Code

**Constant Complexity (Annotated):**
```python
def add(a: int, b: int) -> int:
    """
    Add two numbers.

    Time Complexity: O(1)
    Space Complexity: O(1)
    Cost: CHEAP
    """
    return a + b

# Analysis:
# - No loops or recursion
# - Single arithmetic operation
# - Constant time and space
# VERDICT: O(1) - Very cheap
```

**Why Compliant**:
- Clear complexity: O(1)
- Very cheap operation
- Good candidate for inlining
- No memoization needed

---

**Linear Complexity (Annotated):**
```python
def sum_list(items: list[int]) -> int:
    """
    Sum all items in list.

    Time Complexity: O(n) where n = len(items)
    Space Complexity: O(1)
    Cost: MODERATE
    """
    total = 0
    for item in items:  # Single loop: O(n)
        total += item
    return total

# Analysis:
# - Single loop over n items
# - Constant space (accumulator)
# - Linear time complexity
# VERDICT: O(n) - Moderate cost
```

**Why Compliant**:
- Clear complexity: O(n)
- Moderate cost
- Good candidate for optimization if called frequently
- Possible memoization candidate

---

**Quadratic Complexity (Annotated):**
```python
def bubble_sort(items: list[int]) -> list[int]:
    """
    Sort items using bubble sort.

    Time Complexity: O(n²) where n = len(items)
    Space Complexity: O(n) for new list
    Cost: EXPENSIVE

    WARNING: Quadratic algorithm - use only for small lists.
    """
    result = items[:]  # Copy: O(n) space
    n = len(result)

    for i in range(n):  # Outer loop: O(n)
        for j in range(n - 1):  # Inner loop: O(n)
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]

    return result

# Analysis:
# - Nested loops: O(n) * O(n) = O(n²)
# - Memory for copy: O(n)
# - Very expensive for large n
# VERDICT: O(n²) - Expensive, avoid for large inputs
```

**Why Compliant**:
- Clear complexity: O(n²)
- Expensive operation
- Documented warning
- Consider alternative algorithm (merge sort O(n log n))

---

**Recursive Exponential (Annotated):**
```python
def fibonacci_naive(n: int) -> int:
    """
    Calculate Fibonacci number (naive recursive).

    Time Complexity: O(2ⁿ) - EXPONENTIAL!
    Space Complexity: O(n) stack depth
    Cost: EXTREMELY EXPENSIVE

    WARNING: Exponential time - only use for n < 30.
    RECOMMENDATION: Use memoization or iterative version.
    """
    if n <= 1:
        return n
    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)  # Binary recursion

# Analysis:
# - Binary recursion: 2 recursive calls per invocation
# - Exponential time: O(2ⁿ)
# - Recomputes same values many times
# VERDICT: O(2ⁿ) - EXTREMELY expensive, needs memoization
```

**Why Compliant**:
- Clear complexity: O(2ⁿ)
- Warning documented
- Recommendation provided (memoization)
- **High priority for memoization**

---

### ❌ Non-Compliant Code

**Missing Complexity Analysis (Violation):**
```python
# ❌ VIOLATION: No complexity analysis
def process_matrix(matrix: list[list[int]]) -> list[list[int]]:
    """Process matrix."""
    result = []
    for row in matrix:
        new_row = []
        for col in row:
            for i in range(100):  # Hidden O(100) factor
                col = col * 2
            new_row.append(col)
        result.append(new_row)
    return result

# Problem:
# - Triple nested loops: O(n * m * 100) = O(n * m)
# - No complexity annotation
# - Users don't know this is expensive
# - May use on large matrices (slow!)
```

**Why Non-Compliant**:
- No complexity analysis
- Hidden expensive operation
- Users unaware of cost
- Should be annotated

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Complexity documented
def process_matrix(matrix: list[list[int]]) -> list[list[int]]:
    """
    Process matrix with 100 iterations per element.

    Time Complexity: O(n * m * 100) = O(n * m) where n=rows, m=cols
    Space Complexity: O(n * m) for result matrix
    Cost: EXPENSIVE for large matrices

    WARNING: 100 iterations per element - expensive operation.
    """
    result = []
    for row in matrix:  # O(n)
        new_row = []
        for col in row:  # O(m)
            for i in range(100):  # O(100) = constant
                col = col * 2
            new_row.append(col)
        result.append(new_row)
    return result

# Now users know this is expensive!
```

---

**Incorrect Complexity Estimate (Violation):**
```python
# ❌ VIOLATION: Wrong complexity annotation
def find_duplicates(items: list[int]) -> set[int]:
    """
    Find duplicate values in list.

    Time Complexity: O(n)  # ← WRONG! Actually O(n²)
    Space Complexity: O(n)
    """
    duplicates = set()
    for i, item in enumerate(items):  # O(n)
        if item in items[i+1:]:  # ← O(n) search INSIDE loop = O(n²)!
            duplicates.add(item)
    return duplicates

# Problem:
# - Annotated as O(n) but actually O(n²)
# - Nested search not accounted for
# - Misleading users about performance
```

**Why Non-Compliant**:
- Incorrect complexity annotation
- Hidden nested operation
- Misleading documentation

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Correct complexity
def find_duplicates(items: list[int]) -> set[int]:
    """
    Find duplicate values in list.

    Time Complexity: O(n) with dict/set
    Space Complexity: O(n)
    Cost: MODERATE
    """
    seen = set()
    duplicates = set()

    for item in items:  # O(n)
        if item in seen:  # O(1) set lookup
            duplicates.add(item)
        seen.add(item)

    return duplicates

# Correct O(n) algorithm and annotation!
```

---

## Edge Cases

### Edge Case 1: Amortized Complexity

**Issue**: Some operations have amortized complexity

**Handling**:
```python
def dynamic_array_append(array: list, item):
    """
    Append to dynamic array.

    Time Complexity:
    - Amortized: O(1) - average case
    - Worst case: O(n) - when resize needed
    Space Complexity: O(n)

    Note: Python list.append() is amortized O(1).
    """
    array.append(item)  # Amortized O(1)
    return array

# Document both amortized and worst-case complexity
```

**Directive Action**: Document both amortized and worst-case complexity.

---

### Edge Case 2: Best/Average/Worst Cases

**Issue**: Algorithm complexity varies by input

**Handling**:
```python
def quicksort(items: list[int]) -> list[int]:
    """
    Sort using quicksort.

    Time Complexity:
    - Best case: O(n log n) - balanced partitions
    - Average case: O(n log n)
    - Worst case: O(n²) - already sorted or reverse sorted
    Space Complexity: O(log n) recursion depth

    Note: Use random pivot to avoid worst case.
    """
    # ... implementation
    pass
```

**Directive Action**: Document best/average/worst case complexities.

---

### Edge Case 3: Input-Dependent Complexity

**Issue**: Complexity depends on input characteristics

**Handling**:
```python
def search_sorted(items: list[int], target: int) -> int:
    """
    Binary search in sorted array.

    Time Complexity: O(log n) for sorted input
    Space Complexity: O(1)

    REQUIREMENT: Input must be sorted (not verified).
    If unsorted: behavior undefined, may return wrong answer.
    """
    # Binary search assumes sorted input
    pass
```

**Directive Action**: Document input requirements and complexity conditions.

---

## Related Directives

- **Depends On**: None
- **Triggers**:
  - `fp_memoization` - High-cost functions are memoization candidates
  - `fp_function_inlining` - Low-cost functions are inlining candidates
- **Called By**:
  - `project_task_decomposition` - Use cost for task sizing
  - `project_performance_summary` - Report complexity distribution
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `time_complexity` field (e.g., "O(n)")
- **`functions`**: Sets `space_complexity` field (e.g., "O(1)")
- **`functions`**: Sets `cost_category` (cheap/moderate/expensive)
- **`notes`**: Logs complexity analysis with `note_type = 'performance'`

---

## Testing

How to verify this directive is working:

1. **Analyze constant function** → Directive estimates O(1)
   ```python
   def add(a, b): return a + b
   # Expected: O(1) time, O(1) space
   ```

2. **Analyze nested loops** → Directive estimates O(n²)
   ```python
   def bubble_sort(items):
       for i in items:
           for j in items: ...
   # Expected: O(n²) time
   ```

3. **Check database** → Verify complexity stored
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Common Mistakes

- ❌ **Forgetting hidden loops** - List comprehensions, map/filter count as loops
- ❌ **Ignoring recursion depth** - Recursive calls use stack space
- ❌ **Wrong Big-O notation** - O(2n) should be simplified to O(n)
- ❌ **Missing worst-case analysis** - Only documenting average case
- ❌ **No complexity documentation** - Users unaware of performance characteristics

---

## Roadblocks and Resolutions

### Roadblock 1: complex_control_flow
**Issue**: Cannot statically determine complexity (dynamic behavior)
**Resolution**: Use conservative estimate, mark as "unknown", recommend profiling

### Roadblock 2: library_function_cost
**Issue**: Complexity depends on external library function
**Resolution**: Document dependency, look up library function complexity

### Roadblock 3: data_structure_complexity
**Issue**: Operations on custom data structures
**Resolution**: Analyze data structure implementation or document assumed complexity

### Roadblock 4: multiple_phases
**Issue**: Function has multiple phases with different complexities
**Resolution**: Document dominant term (highest complexity phase)

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for function complexity analysis*
