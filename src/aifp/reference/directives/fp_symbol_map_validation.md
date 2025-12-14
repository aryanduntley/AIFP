# Directive: fp_symbol_map_validation

**Type**: FP Auxiliary
**Level**: 3 (Medium Priority)
**Parent Directive**: None
**Priority**: LOW - Validates exported function symbols for completeness

---

## Purpose

The `fp_symbol_map_validation` directive validates that all exported functions are properly tracked in project.db and that the symbol map (exported functions) is complete and accurate. This directive provides **export validation** ensuring no functions are orphaned or missing from the index.

Symbol map validation provides **export integrity**, enabling:
- **Complete Indexing**: All public functions tracked
- **No Orphaned Functions**: Every export has database entry
- **API Surface Validation**: Public API completely documented
- **Import/Export Consistency**: Exports match what's declared
- **Dependency Resolution**: All public symbols resolvable

This directive acts as an **export integrity checker** ensuring complete function tracking.

---

## When to Apply

This directive applies when:
- **Writing new exports** - Validate export completeness
- **Refactoring modules** - Ensure exports still tracked
- **Project compliance check** - Verify all exports indexed
- **API changes** - Validate public surface area
- **Called by project directives**:
  - `project_file_write` - Validate exports before writing
  - `project_compliance_check` - Check symbol map completeness
  - Works with `fp_function_indexing` - Ensures indexed functions match exports

---

## Workflow

### Trunk: validate_symbol_map

Validates that all exported functions have corresponding entries in project.db and vice versa.

**Steps**:
1. **Extract exports** - Parse module to find all exported functions
2. **Query database** - Get all functions for this file from project.db
3. **Compare sets** - Identify missing exports or orphaned entries
4. **Check consistency** - Verify export names match database names
5. **Validate metadata** - Ensure exported functions have complete metadata
6. **Report discrepancies** - Flag any mismatches

### Branches

**Branch 1: If exports_not_indexed**
- **Then**: `index_missing_exports`
- **Details**: Exports found in code but not in database
  - Pattern: Function exported but not in functions table
  - Add missing functions to database
  - Generate metadata if missing
  - Create interactions entries
  - Log addition to notes
- **Result**: Returns indexed exports

**Branch 2: If orphaned_database_entries**
- **Then**: `remove_or_flag_orphans`
- **Details**: Database entries for functions no longer exported
  - Pattern: Functions table has entries not in current exports
  - Check if function was deleted or made private
  - Remove from database if deleted
  - Update visibility if made private
  - Log change to notes
- **Result**: Returns cleaned database

**Branch 3: If export_name_mismatch**
- **Then**: `sync_export_names`
- **Details**: Export name differs from database name
  - Pattern: Function renamed but database not updated
  - Update database with new name
  - Update all references in interactions table
  - Preserve function history
  - Log rename to notes
- **Result**: Returns synchronized names

**Branch 4: If symbol_map_valid**
- **Then**: `mark_compliant`
- **Details**: Symbol map is complete and accurate
  - All exports indexed in database
  - No orphaned database entries
  - Names match between code and database
  - Metadata complete
- **Result**: Passes validation

**Fallback**: `prompt_user`
- **Details**: Ambiguous symbol map issue
  - Multiple functions with same export name
  - Unclear if function should be exported
  - Ask user for clarification
- **Result**: User provides guidance

---

## Examples

### ✅ Compliant Code

**Complete Symbol Map (Passes):**

```python
# File: src/math_operations.py

# AIFP_METADATA
# function_name: add
# purity_level: pure
# ...
def add(x: float, y: float) -> float:
    """Add two numbers."""
    return x + y

# AIFP_METADATA
# function_name: subtract
# purity_level: pure
# ...
def subtract(x: float, y: float) -> float:
    """Subtract two numbers."""
    return x - y

# Private helper (not exported)
def _validate_input(x: float) -> bool:
    return isinstance(x, (int, float))

# Module exports
__all__ = ['add', 'subtract']

# ✅ Symbol map valid:
# - add: exported and indexed in database
# - subtract: exported and indexed in database
# - _validate_input: not exported, not required in database
# - __all__ matches database entries
```

**Why Compliant**:
- All exported functions (`add`, `subtract`) are in database
- Private function (`_validate_input`) correctly not exported
- `__all__` explicitly lists exports
- No orphaned database entries

---

**Explicit Exports with Full Tracking (Passes):**

```javascript
// File: src/utils.js

// AIFP_METADATA
// function_name: formatCurrency
// purity_level: pure
// ...
export function formatCurrency(amount) {
    return `$${amount.toFixed(2)}`;
}

// AIFP_METADATA
// function_name: parseDate
// purity_level: pure
// ...
export function parseDate(dateString) {
    return new Date(dateString);
}

// Private helper (not exported)
function validateFormat(str) {
    return /^\d{4}-\d{2}-\d{2}$/.test(str);
}

// ✅ Symbol map valid:
// - formatCurrency: exported and in database
// - parseDate: exported and in database
// - validateFormat: not exported, not required
// - All exports tracked
```

**Why Compliant**:
- Exported functions have `export` keyword
- All exports in database
- Private helper not exported
- Clear separation between public and private

---

### ❌ Non-Compliant Code

**Export Not Indexed (Violation):**

```python
# ❌ VIOLATION: Exported function not in database

# File: src/calculations.py

def calculate_total(items):  # ← Exported but NO metadata
    """Calculate total price."""
    return sum(item.price for item in items)

def calculate_tax(subtotal, rate):  # ← Exported but not in database
    """Calculate tax amount."""
    return subtotal * rate

# Module exports
__all__ = ['calculate_total', 'calculate_tax']

# Problem:
# - calculate_total exported but no AIFP metadata
# - calculate_tax exported but not indexed in database
# - Symbol map incomplete
# - Cannot track dependencies
# - AI has no context about these functions
```

**Why Non-Compliant**:
- Functions exported but not indexed
- No metadata annotations
- Database missing these functions
- Symbol map incomplete

**Refactored (Compliant):**

```python
# ✅ REFACTORED: All exports indexed

# File: src/calculations.py

# AIFP_METADATA
# function_name: calculate_total
# purity_level: pure
# parameters: items: list[Item]
# return_type: float
# dependencies: []
# side_effects: none
def calculate_total(items):
    """Calculate total price."""
    return sum(item.price for item in items)

# AIFP_METADATA
# function_name: calculate_tax
# purity_level: pure
# parameters: subtotal: float, rate: float
# return_type: float
# dependencies: []
# side_effects: none
def calculate_tax(subtotal, rate):
    """Calculate tax amount."""
    return subtotal * rate

# Module exports
__all__ = ['calculate_total', 'calculate_tax']

# Database entries created for both functions
# Symbol map now complete
```

---

**Orphaned Database Entry (Violation):**

```python
# ❌ VIOLATION: Database has entry for deleted function

# File: src/auth.py

# AIFP_METADATA
# function_name: login_user
# ...
def login_user(username, password):
    """Authenticate user."""
    return authenticate(username, password)

# Module exports
__all__ = ['login_user']

# Database has entries for:
# - login_user (correct)
# - logout_user (orphaned - function was deleted)
# - refresh_token (orphaned - function was removed)

# Problem:
# - Database contains functions that no longer exist
# - Symbol map inconsistent
# - Stale database entries
# - Dependency tracking incorrect
```

**Why Non-Compliant**:
- Database has entries for non-existent functions
- Orphaned database records
- Symbol map out of sync
- Stale function tracking

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Database cleaned

# File: src/auth.py

# AIFP_METADATA
# function_name: login_user
# ...
def login_user(username, password):
    """Authenticate user."""
    return authenticate(username, password)

# Module exports
__all__ = ['login_user']

# After cleanup:
# Database only contains: login_user
# Orphaned entries (logout_user, refresh_token) removed
# Symbol map now consistent
```

---

**Export Name Mismatch (Violation):**

```python
# ❌ VIOLATION: Function renamed but database not updated

# File: src/formatters.py

# AIFP_METADATA
# function_name: formatUserName  # ← Old name in metadata
# ...
def format_user_display_name(user):  # ← New name in code
    """Format user name for display."""
    return f"{user.first_name} {user.last_name}"

__all__ = ['format_user_display_name']

# Database has:
# - formatUserName (old name)
# But code exports:
# - format_user_display_name (new name)

# Problem:
# - Name mismatch between code and database
# - Symbol map incorrect
# - Dependency tracking broken
# - Function appears as two different entities
```

**Why Non-Compliant**:
- Function renamed but database not updated
- Metadata has old name
- Export name doesn't match database
- Inconsistent tracking

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Name synchronized

# File: src/formatters.py

# AIFP_METADATA
# function_name: format_user_display_name  # ← Updated
# ...
def format_user_display_name(user):
    """Format user name for display."""
    return f"{user.first_name} {user.last_name}"

__all__ = ['format_user_display_name']

# Database updated:
# - Old entry (formatUserName) removed or renamed
# - New entry (format_user_display_name) matches code
# - All references in interactions table updated
# - Symbol map now consistent
```

---

## Symbol Map Validation Process

### Step 1: Extract Exports from Code

```python
# Python: Check __all__ or public functions
if '__all__' in module:
    exports = module.__all__
else:
    exports = [name for name in dir(module) if not name.startswith('_')]

# JavaScript: Parse export statements
// export function foo() {}
// export { bar, baz }
// export default qux
```

### Step 2: Query Database

```sql
-- Get all functions for file
SELECT name, visibility
FROM functions
WHERE file_id = (SELECT id FROM files WHERE path = 'src/math_operations.py');
```

### Step 3: Compare Sets

```python
# Code exports
code_exports = {'add', 'subtract', 'multiply'}

# Database functions (public only)
db_exports = {'add', 'subtract'}

# Missing from database
missing = code_exports - db_exports  # {'multiply'}

# Orphaned in database
orphaned = db_exports - code_exports  # {}
```

### Step 4: Resolve Discrepancies

```python
# Add missing exports to database
for func_name in missing:
    add_function_to_database(func_name, file_id)

# Remove orphaned entries
for func_name in orphaned:
    remove_function_from_database(func_name, file_id)
```

---

## Export Patterns

### Python

```python
# Explicit exports with __all__
__all__ = ['public_func1', 'public_func2']

# Everything without underscore is exported
def public_func():
    pass

def _private_func():
    pass
```

### JavaScript/TypeScript

```javascript
// Named exports
export function publicFunc() {}
export const publicConst = 42;

// Default export
export default mainFunc;

// Re-exports
export { func1, func2 } from './other';

// Private (not exported)
function privateFunc() {}
```

### Rust

```rust
// Public functions
pub fn public_func() {}

// Private (module-only)
fn private_func() {}

// Re-exports
pub use other_module::some_func;
```

---

## Edge Cases

### Edge Case 1: Re-exported Functions

**Issue**: Function imported from another module and re-exported

**Handling**:
```python
# File: src/api.py
from .calculations import calculate_total

# Re-export
__all__ = ['calculate_total']

# Symbol map validation:
# - Track that calculate_total is defined in calculations.py
# - api.py re-exports it
# - Database entry references original definition
# - Interactions track re-export relationship
```

**Directive Action**: Track original definition location; mark as re-export in database.

---

### Edge Case 2: Conditional Exports

**Issue**: Exports vary based on runtime conditions

**Handling**:
```python
# Dynamic exports based on platform
if platform.system() == 'Windows':
    __all__ = ['windows_func']
else:
    __all__ = ['unix_func']

# Symbol map validation:
# - Track all possible exports
# - Mark conditional exports in database
# - Validate based on current environment
```

**Directive Action**: Track all conditional branches; validate current environment exports.

---

### Edge Case 3: Wildcard Exports

**Issue**: `from module import *` exports everything

**Handling**:
```python
# File: src/all_functions.py
from .math_ops import *  # Imports all from math_ops

# Symbol map validation:
# - Resolve * to actual function names
# - Track source module for each import
# - Validate all resolved functions indexed
```

**Directive Action**: Resolve wildcard to explicit names before validation.

---

## Related Directives

- **Depends On**:
  - `fp_function_indexing` - Requires functions to be indexed
  - `fp_metadata_annotation` - Needs metadata to validate
- **Triggers**:
  - `project_update_db` - Updates database to fix inconsistencies
- **Called By**:
  - `project_file_write` - Validate exports on file write
  - `project_compliance_check` - Check symbol map completeness
- **Escalates To**: None

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: Adds missing exports, removes orphaned entries, updates names
- **`interactions`**: Updates references when function names change
- **`notes`**: Logs symbol map discrepancies with `note_type = 'validation'`

---

## Testing

How to verify this directive is working:

1. **Export not indexed** → Directive adds to database
   ```python
   # Before: Function exported but not in database
   # After: Database entry created
   ```

2. **Orphaned entry** → Directive removes from database
   ```sql
   -- Before: Database has entry for deleted function
   -- After: Entry removed
   ```

3. **Check symbol map completeness**
   ```sql
   SELECT f.name, fi.path
   FROM functions f
   JOIN files fi ON f.file_id = fi.id
   WHERE f.visibility = 'public';
   ```

---

## Common Mistakes

- ❌ **Exporting without indexing** - Function exported but not in database
- ❌ **Orphaned database entries** - Deleted functions still in database
- ❌ **Name mismatch** - Function renamed but database not updated
- ❌ **Missing __all__** - Unclear what's exported in Python
- ❌ **Incomplete metadata** - Exported functions without metadata

---

## Roadblocks and Resolutions

### Roadblock 1: exports_not_indexed
**Issue**: Functions exported in code but not in database
**Resolution**: Parse exports, generate metadata, add to database with complete indexing

### Roadblock 2: orphaned_database_entries
**Issue**: Database has functions that no longer exist in code
**Resolution**: Compare exports with database, remove or mark deleted entries

### Roadblock 3: export_name_mismatch
**Issue**: Function name in code differs from database
**Resolution**: Synchronize names, update all references in interactions table

### Roadblock 4: re_export_tracking
**Issue**: Function imported from another module and re-exported
**Resolution**: Track original definition, mark as re-export, maintain source reference

---

## References

None
---

*Part of AIFP v1.0 - FP Auxiliary directive for symbol map validation*
