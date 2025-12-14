# Directive: project_compliance_check

**Type**: Project
**Level**: 4
**Parent Directive**: project_update_db
**Priority**: CRITICAL - Required for FP enforcement

---

## Purpose

The `project_compliance_check` directive is the **validation gatekeeper** that ensures all code in an AIFP project adheres to strict functional programming principles before database updates or completion marking. This directive runs a comprehensive suite of FP compliance directives to verify code purity, immutability, OOP elimination, and structural correctness.

This directive is **critical for AIFP integrity** - it prevents non-compliant code from entering the project and ensures that:
- **All functions are pure** (deterministic, no side effects)
- **All data is immutable** (no mutations)
- **No OOP constructs** (no classes, inheritance, or stateful methods)
- **Type safety** (explicit types, no `any`)
- **Proper error handling** (Result types, no exceptions)
- **Project alignment** (code matches completion path goals)

The compliance check is **customizable per user** through user preferences:
- **fp_strictness_level**: Controls how strict checks are (strict, moderate, relaxed)
- **auto_fix_violations**: Whether to automatically refactor violations
- **skip_warnings**: Skip non-critical warnings
- **user_exceptions**: Approved violations for specific use cases

When violations are detected, this directive either:
1. **Auto-fixes** if user preferences allow and confidence is high
2. **Escalates** to specific FP directives for refactoring
3. **Prompts user** for manual resolution

---

## When to Apply

This directive applies when:
- **Called by `project_file_write`** - Before finalizing file writes
- **Called by `project_update_db`** - Before database synchronization
- **User requests validation** - Manual compliance check
- **Pre-merge validation** - Git integration validates before branch merge
- **Completion path milestone** - Validates before marking milestone complete
- **Project audit** - Comprehensive project-wide compliance scan

---

## Workflow

### Trunk: check_user_preferences

Loads user preferences for compliance checking behavior.

**Steps**:
1. **Query user_preferences.db** - Load directive-specific preferences
2. **Load fp_strictness_level** - Get global FP strictness setting
3. **Load user exceptions** - Get approved violations (if any)
4. **Configure compliance context** - Apply preferences to compliance checks
5. **Route to checking** - Proceed with configured compliance check

### Branches

**Branch 1: If directive_preferences_exist**
- **Then**: `load_compliance_preferences`
- **Details**: Load user preferences for compliance checking
  - Query: `SELECT preference_key, preference_value FROM directive_preferences
           WHERE directive_name='project_compliance_check' AND active=1`
  - Also check `user_settings.fp_strictness_level`
  - Common preferences:
    - `auto_fix_violations` (bool) - Auto-refactor violations
    - `skip_warnings` (bool) - Ignore non-critical issues
    - `strict_mode` (bool) - Extra strict checking
  - Apply to compliance context
- **Result**: Preferences loaded and applied

**Branch 2: If preferences_loaded**
- **Then**: `run_checks_with_preferences`
- **Details**: Execute FP compliance checks with user preferences
  - Apply strictness level to checks
  - Respect user exceptions for specific violations
  - Use appropriate thresholds based on strictness
  - Prioritize critical violations over warnings
- **Result**: Compliance results with user context

**Branch 3: If compliance_passed**
- **Then**: `proceed`
- **Details**: All checks passed
  - Update database with compliant code
  - Mark functions as FP-compliant in functions table
  - Log success to notes (if tracking enabled)
  - Return success result
- **Result**: Code validated and approved

**Branch 4: If compliance_failed**
- **Then**: `alert_user` and escalate
- **Details**: Violations detected, escalate for fixing
  - Categorize violations by severity (critical, warning, info)
  - Escalate to specific FP directives:
    - **fp_purity** - For impure functions
    - **fp_no_oop** - For OOP constructs
    - **fp_immutability** - For mutations
    - **fp_type_safety** - For type issues
  - If `auto_fix_violations=true` and confidence high:
    - Attempt automatic refactoring
    - Re-run compliance check
  - If auto-fix fails or disabled:
    - Present violations to user
    - Suggest manual fixes
    - Block database update until resolved
- **Result**: Violations reported and escalated

**Fallback**: `prompt_user`
- **Details**: Unable to determine compliance status
  - Ask: "Resolve compliance issue manually?"
  - Present violation details
  - Offer options: auto-fix, manual fix, skip (with justification)
  - Log decision to notes
- **Result**: User guidance requested

---

## Examples

### ✅ Compliant Code (Passes Check)

**Pure, Immutable, No OOP:**
```python
from dataclasses import dataclass
from returns.result import Result, Success, Failure

@dataclass(frozen=True)
class Order:
    """Immutable order data (no methods)."""
    id: int
    total: float
    items: tuple[str, ...]

def calculate_order_total(items: tuple[float, ...], tax_rate: float) -> float:
    """Pure function - calculates order total."""
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)

def validate_order(order: Order) -> Result[Order, str]:
    """Pure validation using Result type."""
    if order.total < 0:
        return Failure("Total cannot be negative")
    if not order.items:
        return Failure("Order must have items")
    return Success(order)

# Compliance check:
# ✅ fp_purity: All functions pure
# ✅ fp_immutability: frozen dataclass, no mutations
# ✅ fp_no_oop: dataclass has no methods
# ✅ fp_type_safety: All parameters typed
# ✅ fp_result_types: Uses Result for error handling
# RESULT: PASSED
```

---

### ❌ Non-Compliant Code (Fails Check)

**Impure, Mutable, OOP:**
```python
# ❌ MULTIPLE VIOLATIONS

class Order:  # ← VIOLATION: OOP class with methods
    def __init__(self, id, total):  # ← VIOLATION: No type hints
        self.id = id  # ← VIOLATION: Mutable state
        self.total = total
        self.items = []  # ← VIOLATION: Mutable default

    def add_item(self, item):  # ← VIOLATION: Impure method (mutates self)
        self.items.append(item)  # ← VIOLATION: Mutation
        self.total += item['price']  # ← VIOLATION: Reassignment

    def calculate_tax(self):  # ← VIOLATION: Impure (reads mutable state)
        return self.total * 0.1  # ← VIOLATION: Magic number

# Compliance check:
# ❌ fp_purity: Methods are impure (mutate state)
# ❌ fp_immutability: Mutable attributes, list.append()
# ❌ fp_no_oop: Class with methods
# ❌ fp_type_safety: No type annotations
# ❌ fp_no_reassignment: Variable reassignment (self.total +=)
# RESULT: FAILED (5 critical violations)

# Auto-fix attempt (if enabled):
# → Escalate to fp_no_oop: Convert class to frozen dataclass + functions
# → Escalate to fp_purity: Convert methods to pure functions
# → Escalate to fp_immutability: Replace mutations with immutable updates
# → Add type annotations
# → Extract magic number to constant
```

**Refactored (Compliant):**
```python
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class Order:
    """Immutable order data."""
    id: int
    total: float
    items: tuple[Dict[str, float], ...]

TAX_RATE = 0.1  # Extracted constant

def add_item(order: Order, item: Dict[str, float]) -> Order:
    """Add item immutably. Returns new order."""
    new_items = order.items + (item,)
    new_total = order.total + item['price']
    return Order(id=order.id, total=new_total, items=new_items)

def calculate_tax(order: Order) -> float:
    """Pure tax calculation."""
    return order.total * TAX_RATE

# ✅ ALL VIOLATIONS RESOLVED
```

---

## Edge Cases

### Edge Case 1: Strictness Level Variations

**Issue**: Different strictness levels allow different violations

**Handling**:
```python
# Strictness levels (from user_settings)
strictness = user_preferences.fp_strictness_level

match strictness:
    case "strict":
        # Zero tolerance - all FP rules enforced
        run_all_fp_directives()
        fail_on_any_violation()

    case "moderate":
        # Allow minor violations with warnings
        run_core_fp_directives()  # purity, immutability, no_oop
        warn_on_minor_violations()  # type hints optional

    case "relaxed":
        # Allow some non-FP patterns
        run_critical_fp_directives()  # no_oop only
        skip_auxiliary_checks()  # allow mutations in effect functions
```

---

### Edge Case 2: User-Approved Exceptions

**Issue**: User has legitimate reason for FP violation

**Handling**:
```python
# Check user exceptions
exceptions = query_user_preferences_db(
    "SELECT violation_type, justification FROM approved_exceptions"
)

# Example: User approved OOP for external library wrapper
if violation.type == "oop" and violation.in_file("lib/external_wrapper.py"):
    if "external_wrapper" in approved_exceptions:
        # Skip this violation
        log_note("Violation approved by user: OOP in external wrapper")
        continue

# Still flag if not in approved list
```

---

### Edge Case 3: Partially Compliant File

**Issue**: Some functions compliant, others not

**Handling**:
```python
# Check each function individually
compliance_results = []
for function in file.functions:
    result = check_function_compliance(function)
    compliance_results.append(result)

# Separate compliant from non-compliant
compliant_funcs = [r for r in compliance_results if r.passed]
violations = [r for r in compliance_results if not r.passed]

if violations:
    # Report per-function violations
    return {
        "file_compliant": False,
        "compliant_count": len(compliant_funcs),
        "violation_count": len(violations),
        "violations": violations,
        "action": "Fix violations then re-check"
    }
```

---

### Edge Case 4: Performance vs Purity Trade-off

**Issue**: Pure function is performance bottleneck

**Handling**:
```python
# User requests performance exception
if user_approved_performance_exception(function_name):
    # Allow controlled impurity
    log_note(f"Performance exception: {function_name} allowed memoization cache")
    # Still require:
    # - Explicit documentation of impurity
    # - Isolation to effect module
    # - Tests verifying behavior
    return {
        "compliant": True,
        "exception": "performance",
        "requires": ["documentation", "isolation", "tests"]
    }
```

---

## Related Directives

- **Called By**:
  - `project_file_write` - Validates before file write
  - `project_update_db` - Validates before DB update
  - `git_merge_branch` - Validates before merge
- **Escalates To**:
  - `fp_purity` - For purity violations
  - `fp_immutability` - For mutation violations
  - `fp_no_oop` - For OOP violations
  - `fp_type_safety` - For type violations
  - `fp_result_types` - For exception usage
- **Works With**:
  - `user_preferences_sync` - Loads user preferences
  - `project_completion_check` - Verifies roadmap alignment

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: Sets FP compliance flags (`purity_level`, `side_effects_json`, `oop_compliant`)
- **`notes`**: Logs compliance violations with `note_type = 'compliance'` and `severity` levels
- **`directive_preferences`** (user_preferences.db): Reads user compliance preferences

---

## Testing

How to verify this directive is working:

1. **Check compliant code** → Passes all checks
   ```python
   result = project_compliance_check("src/pure_calc.py")
   assert result["compliant"] == True
   assert len(result["violations"]) == 0
   ```

2. **Check non-compliant code** → Detects violations
   ```python
   result = project_compliance_check("src/oop_calc.py")
   assert result["compliant"] == False
   assert "oop" in result["violation_types"]
   ```

3. **Test strictness levels** → Respects user preferences
   ```python
   set_preference("fp_strictness_level", "relaxed")
   result = project_compliance_check("src/partial.py")
   # Minor violations allowed in relaxed mode
   ```

4. **Test auto-fix** → Refactors when enabled
   ```python
   set_preference("auto_fix_violations", True)
   result = project_compliance_check("src/fixable.py")
   assert result["auto_fixed"] == True
   assert result["compliant"] == True
   ```

---

## Common Mistakes

- ❌ **Not loading user preferences** - Always check preferences first
- ❌ **Failing on warnings** - Distinguish critical violations from warnings
- ❌ **Blocking on approved exceptions** - Check user exceptions table
- ❌ **Not escalating to FP directives** - Use specialized directives for fixes
- ❌ **Inconsistent strictness** - Apply strictness level consistently

---

## Roadblocks and Resolutions

### Roadblock 1: compliance_failure
**Issue**: Code fails compliance checks
**Resolution**: Refer to specific FP directives (fp_purity, fp_no_oop) and retry after fixes

### Roadblock 2: fp_violation
**Issue**: Specific FP rule violated
**Resolution**: Run linked fp_* directives automatically to resolve (or prompt user if auto-fix disabled)

---

## References

None
---

*Part of AIFP v1.0 - Critical Project directive for FP compliance enforcement*
