# SQL Analysis Report - FP Directive Files

**Date**: 2025-12-14
**Files Analyzed**: 66 FP directive files
**Purpose**: Identify which SQL statements need removal vs. which are legitimate

---

## Summary

**SQL to REMOVE** (disabled by default, opt-in debugging):
- `INSERT INTO notes` - 27 files, 31 total occurrences

**SQL to KEEP** (standard behavior):
- `UPDATE functions` - 47 occurrences - tracks function metadata (purity, patterns, etc.)
- `INSERT INTO functions` - registers new functions
- `INSERT INTO call_graph` - tracks function calls
- `INSERT INTO interactions` - tracks function dependencies
- `INSERT INTO files` - registers files

---

## Detailed Breakdown

### 1. INSERT INTO notes (REMOVE)

**Count**: 31 occurrences across 27 files

**Files with 2 occurrences:**
- fp_wrapper_generation.md
- fp_currying.md
- fp_const_refactoring.md
- fp_chaining.md

**Files with 1 occurrence:** (23 files)
- All other FP files listed in SQL_CLEANUP_NEEDED.md

**Why Remove:**
- `fp_flow_tracking` is DISABLED by default (costs ~5% more tokens)
- Should only be enabled temporarily for debugging
- Directives document it as standard behavior (incorrect)
- Creates false expectations for users

**Action**: Remove all `INSERT INTO notes` from FP directive files

---

### 2. UPDATE functions (KEEP)

**Count**: 47 occurrences

**Examples:**
```sql
UPDATE functions
SET
    purity_level = 'pure',
    side_effects_json = '[]',
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?;
```

```sql
UPDATE functions SET error_handling_pattern = 'option'
```

```sql
UPDATE functions SET null_safety = 'null_free'
```

**Why Keep:**
- This IS standard behavior for FP directives
- Tracks function-level metadata (purity, patterns, safety)
- Core to AIFP's FP compliance tracking
- NOT opt-in debugging, but actual data model

**Files using UPDATE functions:**
- fp_borrow_check.md
- fp_concurrency_safety.md
- fp_conditional_elimination.md
- fp_documentation.md
- fp_error_pipeline.md
- fp_function_indexing.md
- fp_generic_constraints.md
- fp_guard_clauses.md
- fp_io_isolation.md
- fp_logging_safety.md
- fp_memoization.md
- fp_naming_conventions.md
- fp_no_reassignment.md
- fp_null_elimination.md
- fp_optionals.md
- (and more)

**Action**: Keep all `UPDATE functions` statements

---

### 3. INSERT INTO call_graph (KEEP)

**File**: fp_call_graph_generation.md

```sql
INSERT INTO call_graph (caller_function_id, callee_function_id, file_id, line_number)
VALUES (
    (SELECT id FROM functions WHERE name = 'main'),
    (SELECT id FROM functions WHERE name = 'calculate'),
    1,
    5
);
```

**Why Keep:**
- Standard behavior for call graph directive
- Tracks which functions call which other functions
- Core feature, not debugging

**Action**: Keep

---

### 4. INSERT INTO interactions (KEEP)

**File**: fp_dependency_tracking.md (2 occurrences)

```sql
INSERT INTO interactions (source_function_id, target_function_id, interaction_type, description)
VALUES (
    (SELECT id FROM functions WHERE name = 'calculate_total'),
    (SELECT id FROM functions WHERE name = 'calculate_tax'),
    'calls',
    'function_a calls function_b with tax rate parameter'
);
```

**Why Keep:**
- Standard behavior for dependency tracking
- Different from `notes` - this is structured relationship data
- Core feature

**Action**: Keep

---

### 5. INSERT INTO module_dependencies (KEEP)

**File**: fp_dependency_tracking.md

```sql
INSERT INTO module_dependencies (source_module, target_module, dependency_type, symbols_used)
VALUES ('a', 'b', 'import', '["helper_b"]');
```

**Why Keep:**
- Tracks module-level dependencies
- Standard behavior
- Different from notes logging

**Action**: Keep

---

### 6. INSERT INTO functions (KEEP)

**File**: fp_function_indexing.md

```sql
INSERT INTO functions (
    name,
    file_id,
    purpose,
    purity_level,
    ...
)
```

**Why Keep:**
- Registers new functions in the system
- Absolutely standard behavior
- Core data model operation

**Action**: Keep

---

### 7. INSERT INTO files (KEEP)

**File**: fp_test_purity.md

```sql
INSERT INTO files (path, language, file_type, metadata, project_id)
VALUES (?, ?, 'test', ?, ?);
```

**Why Keep:**
- Registers test files
- Standard behavior

**Action**: Keep

---

### 8. Code Examples (KEEP)

**Files**: Various

Many FP directives have SQL in code examples showing:
- SQL injection vulnerabilities
- String formatting issues
- Database query patterns

**Examples:**
```python
# Bad example showing SQL injection
cursor.execute(f"SELECT * FROM users WHERE id={user_id}")

# Good example showing parameterization
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**Why Keep:**
- These are teaching examples
- Not actual SQL to execute
- Part of directive education content

**Action**: Keep all code example SQL

---

## Cleanup Strategy

### Only Remove: INSERT INTO notes

**Pattern 1**: Workflow steps with SQL blocks
```markdown
- Update database:
  ```sql
  INSERT INTO notes ...
  ```
```

**Pattern 2**: SQL in code comments
```python
# Database log
INSERT INTO notes ...
```

**Pattern 3**: Standalone SQL blocks
```sql
INSERT INTO notes ...
```

### Keep Everything Else

All other SQL is legitimate:
- Function metadata updates
- Relationship tracking
- Data model operations
- Code examples

---

## Files Requiring Cleanup

All 27 files listed in SQL_CLEANUP_NEEDED.md - but ONLY remove INSERT INTO notes, nothing else.

---

## Recommended Script Behavior

The cleanup script should:
1. ✅ Remove ONLY `INSERT INTO notes` statements
2. ✅ Remove "Update database:" lines that precede notes inserts
3. ✅ Add conditional note about fp_flow_tracking
4. ❌ NOT touch UPDATE functions
5. ❌ NOT touch INSERT INTO call_graph/interactions/functions/files
6. ❌ NOT touch SQL in code examples

---

## Key Insight

**FP directives DO update the database as standard behavior** - specifically the `functions` table to track metadata like purity levels, error handling patterns, etc. This is core functionality.

**What they should NOT do by default:** Log to `notes` table (opt-in debugging only).

---

**Status**: Analysis complete, ready for targeted cleanup script
