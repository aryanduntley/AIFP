# Directive: fp_dead_code_elimination

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: MEDIUM - Code cleanup and maintenance

---

## Purpose

The `fp_dead_code_elimination` directive scans the dependency graph and eliminates dead or unreachable code paths safely. Dead code elimination keeps the codebase **lean, clean, and maintainable** by removing unused functions, unreachable branches, and obsolete code while maintaining referential integrity.

Dead code elimination provides **maintenance and performance benefits**, enabling:
- **Reduced Codebase Size**: Remove unused code accumulation
- **Improved Readability**: Eliminate clutter and confusion
- **Faster Compilation**: Less code to compile/analyze
- **Easier Maintenance**: No maintaining dead code
- **Safe Cleanup**: Referential transparency enables confident removal

This directive leverages FP's referential transparency to safely identify and remove dead code without fear of breaking hidden dependencies.

---

## When to Apply

This directive applies when:
- **Refactoring legacy code** - Remove obsolete functions after changes
- **After feature removal** - Clean up unused code from removed features
- **Dead branches detected** - Unreachable if/else branches
- **Unused imports/exports** - Remove unused dependencies
- **Project cleanup** - Periodic maintenance to remove accumulation
- **Called by project directives**:
  - `project_compliance_check` - Detect dead code during audits
  - `project_file_write` - Warn if writing functions that are never called
  - Works with `project_dependency_tracking` - Use dependency graph

---

## Workflow

### Trunk: analyze_dependencies

Scans entire codebase to build dependency graph and identify dead code.

**Steps**:
1. **Build call graph** - Map all function calls in codebase
2. **Identify entry points** - Find exported functions, main functions, tests
3. **Traverse from entry points** - Mark all reachable functions
4. **Identify unreachable code** - Functions never called from entry points
5. **Detect dead branches** - Unreachable if/else, match cases
6. **Verify safety** - Ensure removal doesn't break anything
7. **Generate removal plan** - List code safe to remove

### Branches

**Branch 1: If unused_function**
- **Then**: `mark_for_removal`
- **Details**: Function defined but never called
  - Check function not exported (public API)
  - Verify no dynamic calls (reflection, getattr)
  - Ensure not test fixture or utility
  - Mark as safe to remove
- **Result**: Returns removal recommendation

**Branch 2: If unreachable_branch**
- **Then**: `eliminate_dead_branch`
- **Details**: Code path that can never execute
  - `if False:` blocks
  - Branches after return/raise
  - Impossible match cases
  - Remove unreachable code
- **Result**: Returns cleaned code

**Branch 3: If unused_import**
- **Then**: `remove_import`
- **Details**: Imported module never used
  - Check import not used anywhere
  - Verify no side effects on import
  - Remove import statement
- **Result**: Returns cleaned imports

**Branch 4: If code_in_use**
- **Then**: `mark_as_live`
- **Details**: Code is reachable and used
  - Function called from entry points
  - Exported as public API
  - Keep code
- **Result**: Code preserved

**Branch 5: If uncertain**
- **Then**: `prompt_user`
- **Details**: Unsure if code is dead
  - Dynamic calls possible
  - Reflection/metaprogramming
  - Ask user for confirmation
- **Result**: User decides

**Fallback**: `conservative_keep`
- **Details**: When uncertain, keep code
  - Better to keep unused code than break functionality
  - Conservative approach
  - Log as potential dead code
- **Result**: Code preserved with warning

---

## Examples

### ✅ Compliant Code

**No Dead Code (Passes):**
```python
def calculate_total(items: list[float]) -> float:
    """Calculate total of items (USED)."""
    return sum(items)

def apply_discount(total: float, rate: float) -> float:
    """Apply discount to total (USED)."""
    return total * (1 - rate)

def process_order(items: list[float], discount: float) -> float:
    """
    Process order with discount.

    All functions are used in call chain.
    """
    total = calculate_total(items)  # ← calculate_total is USED
    final = apply_discount(total, discount)  # ← apply_discount is USED
    return final

# Entry point
result = process_order([10, 20, 30], 0.1)

# Analysis:
# - process_order: USED (entry point)
# - calculate_total: USED (called from process_order)
# - apply_discount: USED (called from process_order)
# VERDICT: No dead code
```

**Why Compliant**:
- All functions reachable from entry point
- No unused code
- Clean codebase

---

**Dead Code Removed (Passes):**
```python
# BEFORE: Contains dead code
def calculate_total(items: list[float]) -> float:
    """Calculate total (USED)."""
    return sum(items)

def apply_tax(total: float, rate: float) -> float:
    """Apply tax (UNUSED - dead code!)."""
    return total * (1 + rate)

def process_order(items: list[float]) -> float:
    """Process order."""
    return calculate_total(items)  # No tax applied!

# AFTER: Dead code eliminated
def calculate_total(items: list[float]) -> float:
    """Calculate total (USED)."""
    return sum(items)

# apply_tax removed (never called)

def process_order(items: list[float]) -> float:
    """Process order."""
    return calculate_total(items)

# Analysis:
# - apply_tax was never called
# - Safe to remove
# VERDICT: Dead code eliminated
```

**Why Compliant**:
- Unused function identified and removed
- No functionality lost
- Cleaner codebase

---

### ❌ Non-Compliant Code

**Unreachable Branch (Violation):**
```python
# ❌ VIOLATION: Unreachable code after return
def process_value(x: int) -> int:
    """Process value with dead code."""
    if x > 0:
        return x * 2
    else:
        return 0

    # Dead code - unreachable!
    print("This never executes")  # ← DEAD CODE
    return x * 3  # ← DEAD CODE

# Problem:
# - Code after return in all branches
# - Never executes
# - Clutters codebase
```

**Why Non-Compliant**:
- Code after return (unreachable)
- Wastes space and confuses readers
- Should be removed

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Dead code removed
def process_value(x: int) -> int:
    """Process value (cleaned)."""
    if x > 0:
        return x * 2
    else:
        return 0

# Dead code removed
# Clean, clear function
```

---

**Constant Condition Dead Branch (Violation):**
```python
# ❌ VIOLATION: Constant False condition (dead branch)
DEBUG = False

def process_data(data: list[int]) -> list[int]:
    """Process data with dead debug code."""
    result = [x * 2 for x in data]

    if DEBUG:  # ← Always False (dead branch)
        print(f"Debug: {result}")  # ← DEAD CODE
        validate_result(result)  # ← DEAD CODE

    return result

# Problem:
# - DEBUG is constant False
# - if block never executes
# - Debug code is dead
```

**Why Non-Compliant**:
- Constant condition (always False)
- Dead branch never executes
- Bloats codebase

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Dead branch removed
DEBUG = False

def process_data(data: list[int]) -> list[int]:
    """Process data (debug code removed)."""
    result = [x * 2 for x in data]

    # Debug code removed (was never used)

    return result

# If debugging needed, add it back or use proper logging
```

---

**Unused Helper Function (Violation):**
```python
# ❌ VIOLATION: Helper function never called
def format_currency(amount: float) -> str:
    """Format amount as currency (UNUSED)."""
    return f"${amount:.2f}"

def format_percentage(rate: float) -> str:
    """Format rate as percentage (UNUSED)."""
    return f"{rate * 100:.1f}%"

def calculate_discount(price: float, rate: float) -> float:
    """Calculate discount (USED)."""
    return price * rate

# Entry point
discount = calculate_discount(100, 0.1)
print(discount)  # Just prints number (no formatting)

# Problem:
# - format_currency never called
# - format_percentage never called
# - Dead code accumulation
```

**Why Non-Compliant**:
- Helper functions defined but unused
- Code bloat
- Maintenance burden

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Unused helpers removed
def calculate_discount(price: float, rate: float) -> float:
    """Calculate discount."""
    return price * rate

# Formatting functions removed (never used)

# Entry point
discount = calculate_discount(100, 0.1)
print(discount)

# Clean, minimal codebase
```

---

**Unused Imports (Violation):**
```python
# ❌ VIOLATION: Many unused imports
import json  # ← UNUSED
import re  # ← UNUSED
import datetime  # ← UNUSED
from typing import Dict, List, Optional  # ← Dict and Optional UNUSED
from collections import defaultdict  # ← UNUSED

def process_items(items: List[int]) -> int:
    """Process items (only uses List from typing)."""
    return sum(items)

# Problem:
# - 4 unused imports (json, re, datetime, defaultdict)
# - 2 unused type imports (Dict, Optional)
# - Clutters imports section
```

**Why Non-Compliant**:
- Multiple unused imports
- Confusing to readers (what's actually used?)
- Import overhead

**Refactored (Compliant):**
```python
# ✅ REFACTORED: Only needed imports
from typing import List

def process_items(items: List[int]) -> int:
    """Process items."""
    return sum(items)

# Clean imports - only what's needed
```

---

## Edge Cases

### Edge Case 1: Exported Public API

**Issue**: Function unused internally but exported for external use

**Handling**:
```python
# Don't remove exported functions (public API)
def internal_helper(x: int) -> int:
    """Internal helper (not exported) - safe to remove if unused."""
    return x * 2

def public_api_function(x: int) -> int:
    """
    Public API function (exported).

    KEEP even if not called internally - external users may depend on it.
    """
    return x * 3

# Exports
__all__ = ['public_api_function']  # Exported

# Analysis:
# - internal_helper: Not in __all__, not called → Can remove if unused
# - public_api_function: In __all__ → KEEP (public API)
```

**Directive Action**: Never remove exported public API functions (even if unused internally).

---

### Edge Case 2: Dynamic/Reflection Calls

**Issue**: Function called dynamically (getattr, eval, etc.)

**Handling**:
```python
# Be careful with dynamic calls
def handler_create(data):
    """Create handler (may be called dynamically)."""
    pass

def handler_update(data):
    """Update handler (may be called dynamically)."""
    pass

def handler_delete(data):
    """Delete handler (may be called dynamically)."""
    pass

def dispatch(action: str, data):
    """Dynamic dispatch to handlers."""
    handler = globals()[f'handler_{action}']  # Dynamic lookup!
    return handler(data)

# Analysis:
# - handler_* functions not called directly
# - BUT called dynamically via globals()
# VERDICT: KEEP (dynamic calls)
```

**Directive Action**: Conservative - keep functions that may be called dynamically.

---

### Edge Case 3: Test Fixtures and Utilities

**Issue**: Utility function only used in tests

**Handling**:
```python
# Production code
def calculate_total(items: list[float]) -> float:
    """Calculate total (USED in production and tests)."""
    return sum(items)

# Test utilities
def create_test_items() -> list[float]:
    """Create test items (USED in tests only)."""
    return [1.0, 2.0, 3.0]

# Tests
def test_calculate_total():
    items = create_test_items()  # Uses test utility
    assert calculate_total(items) == 6.0

# Analysis:
# - calculate_total: Used in production and tests → KEEP
# - create_test_items: Used in tests → KEEP (test utility)
# VERDICT: Both are live code
```

**Directive Action**: Consider test files as entry points - test utilities are live code.

---

### Edge Case 4: Gradual Feature Rollout

**Issue**: Feature code exists but not yet enabled

**Handling**:
```python
# Feature flag
FEATURE_NEW_ALGORITHM = False  # Not yet enabled

def new_algorithm(data):
    """
    New algorithm (not yet enabled).

    Looks like dead code, but will be enabled in future.
    """
    # ... implementation

def process(data):
    if FEATURE_NEW_ALGORITHM:
        return new_algorithm(data)  # Will be used when flag enabled
    else:
        return old_algorithm(data)

# Analysis:
# - new_algorithm looks unused (flag is False)
# - BUT will be enabled in future
# VERDICT: KEEP (feature flag controlled)
```

**Directive Action**: Keep code behind feature flags (mark with comment or metadata).

---

## Related Directives

- **Depends On**:
  - `project_dependency_tracking` - Uses dependency graph to identify dead code
- **Triggers**:
  - May trigger `project_update_db` - Update metadata after removal
- **Called By**:
  - `project_compliance_check` - Detect dead code during audits
  - `project_file_write` - Warn about unused functions
- **Escalates To**: None

---

## Helper Functions Used

- `build_dependency_graph(project_id: int) -> DependencyGraph` - Maps all dependencies
- `identify_entry_points(project_id: int) -> list[Function]` - Finds entry points
- `traverse_reachable_code(graph: DependencyGraph, entry: Function) -> set[Function]` - Mark reachable
- `detect_unreachable_branches(ast: AST) -> list[Branch]` - Find dead branches
- `safe_to_remove(func: Function) -> bool` - Verify removal safety
- `update_functions_table(func_id: int, is_dead: bool)` - Update project.db

---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets `is_dead_code = true` for unused functions
- **`functions`**: Removes entries for deleted functions
- **`notes`**: Logs dead code findings with `note_type = 'cleanup'`
- **`interactions`**: Updates after function removal

---

## Testing

How to verify this directive is working:

1. **Define unused function** → Directive detects and suggests removal
   ```python
   # Input
   def unused_func(): pass
   def main(): print("hello")

   # Output: unused_func marked as dead code
   ```

2. **All functions used** → Directive marks all as live
   ```python
   def helper(): pass
   def main(): helper()

   # Output: No dead code detected
   ```

3. **Check database** → Verify dead code marked
   ```sql
   SELECT name, is_dead_code, call_count
   FROM functions
   WHERE is_dead_code = true;
   -- Lists all dead code
   ```

---

## Common Mistakes

- ❌ **Removing exported API functions** - Break external users
- ❌ **Removing dynamically called functions** - Break runtime dispatch
- ❌ **Not checking test usage** - Remove test utilities
- ❌ **Removing feature-flagged code** - Break future features
- ❌ **Over-aggressive cleanup** - When in doubt, keep it

---

## Roadblocks and Resolutions

### Roadblock 1: unused_function
**Issue**: Function defined but never called
**Resolution**: Verify not exported, not dynamically called, then remove

### Roadblock 2: dynamic_calls_possible
**Issue**: Function may be called dynamically (reflection, getattr)
**Resolution**: Conservative - keep function, mark as "possibly dead"

### Roadblock 3: exported_public_api
**Issue**: Function unused internally but part of public API
**Resolution**: Keep (external users may depend on it)

### Roadblock 4: feature_flag_controlled
**Issue**: Code unused now but will be enabled later
**Resolution**: Keep, document as feature flag controlled

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-dead-code-elimination)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#optimization)
- [JSON Definition](../../../docs/directives-json/directives-fp-aux.json)

---

*Part of AIFP v1.0 - FP Auxiliary directive for safe dead code elimination*
