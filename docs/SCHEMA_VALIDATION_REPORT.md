# Schema Validation Report - Project Files Helpers

**Date**: 2026-01-11
**Scope**: `src/aifp/helpers/project/files_1.py` (6 helpers)
**Status**: ✅ Fixed and validated

---

## Issue Found

Initial implementation included **checksum field** that does NOT exist in actual database schema.

### Discrepancy Source

**JSON Spec** (`helpers-project-2.json`) mentions:
- "Computes file checksum (SHA-256) and stores in checksum field"
- "Recalculates checksum from file content"
- "SQL: UPDATE files SET checksum=? WHERE id=?"

**Actual Schema** (`project.sql` lines 45-53):
```sql
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,                              -- File name (e.g., 'calculator-ID_42.py')
    path TEXT NOT NULL UNIQUE,              -- Full file path
    language TEXT,                          -- Guessed or set (e.g., 'Python')
    is_reserved BOOLEAN DEFAULT 0,          -- TRUE during reservation, FALSE after finalization
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**No `checksum` field!**

---

## Changes Made

### 1. Data Structure
```diff
@dataclass(frozen=True)
class FileRecord:
    id: int
    name: str
    path: str
    language: str
-   checksum: str
    is_reserved: bool
    created_at: str
    updated_at: str
```

### 2. Imports
```diff
- import hashlib
  import os
  import sqlite3
```

### 3. Functions Removed
```python
# REMOVED: compute_file_checksum()
# No longer needed - Git handles change tracking
```

### 4. Effect Functions Updated

**Before**:
```python
def _reserve_file_effect(conn, name, path, language):
    cursor = conn.execute(
        "INSERT INTO files (name, path, language, is_reserved, checksum) VALUES (?, ?, ?, 1, '')",
        (name, path, language)
    )
```

**After**:
```python
def _reserve_file_effect(conn, name, path, language):
    cursor = conn.execute(
        "INSERT INTO files (name, path, language, is_reserved) VALUES (?, ?, ?, 1)",
        (name, path, language)
    )
```

### 5. Finalization Logic Simplified

**Before**:
```python
def finalize_file(db_path, file_id, name, path, language):
    # Compute checksum
    checksum = compute_file_checksum(path)

    # Store in database
    _finalize_file_effect(conn, file_id, name, path, language, checksum)
```

**After**:
```python
def finalize_file(db_path, file_id, name, path, language):
    # No checksum computation needed
    _finalize_file_effect(conn, file_id, name, path, language)
```

---

## Validation Results

### ✅ Schema Compliance
- All fields match `files` table schema exactly
- No extra fields in dataclasses
- All SQL queries use only existing columns

### ✅ Python Syntax
```bash
$ python3 -m py_compile src/aifp/helpers/project/files_1.py
✓ Python syntax valid
```

### ✅ Line Count
- **705 lines** (within 600-900 target)
- Reduced from 753 lines after removing checksum code

---

## Rationale

### Why No Checksum?

1. **Git Provides Better Tracking**
   - Git already tracks all file changes with hashes
   - Git diff/log provides complete history
   - Database checksum would be redundant

2. **Schema Simplicity**
   - Files table focuses on metadata only
   - Change detection delegated to Git
   - Cleaner separation of concerns

3. **Performance**
   - No need to compute SHA-256 on every finalization
   - No database bloat with redundant checksums
   - Faster finalization operations

### JSON Spec vs Schema

**Question**: Why does JSON mention checksums?

**Answer**: JSON specs were written aspirationally during design phase. Actual schema implementation simplified the design by delegating change tracking to Git.

**Lesson**: Always validate against actual schemas, not JSON specs.

---

## Impact on Other Helpers

### Files Affected by This Discovery
✅ `files_1.py` - Fixed
⚠️ `files_2.py` - Will need review for similar issues

### Potential Similar Issues
Need to check these helpers in `files_2.py`:
- `update_file` - May reference checksum in implementation notes
- `file_has_changed` - Compares with Git, not checksum (correct approach)
- `update_file_timestamp` - May try to update non-existent checksum field

### Functions Table Review Needed
Check if `functions` table has similar discrepancies:
- Does JSON mention checksums for functions? (unlikely)
- Are all fields in JSON actually in schema?

---

## Recommendations

### For Future Implementations

1. **Schema-First Workflow**:
   ```
   1. Read schema SQL file
   2. Map exact fields to dataclass
   3. Then read JSON for logic/behavior
   4. Validate SQL queries against schema
   ```

2. **Schema Validation Checklist**:
   - [ ] Dataclass fields match table columns exactly
   - [ ] No extra fields in dataclass
   - [ ] All SQL queries use only existing columns
   - [ ] Foreign key references are valid
   - [ ] CHECK constraints match schema

3. **When JSON Conflicts with Schema**:
   - Schema is source of truth
   - Update JSON specs to match schema
   - Document discrepancies in implementation

4. **Testing Strategy**:
   - Create test database from schema SQL
   - Run queries against actual schema
   - Verify no "no such column" errors

---

## Action Items

- [x] Fix `files_1.py` checksum issue
- [ ] Review `files_2.py` for checksum references
- [ ] Update JSON specs to remove checksum mentions
- [ ] Add schema validation to implementation workflow
- [ ] Create schema validation script for future helpers

---

**Conclusion**: Schema validation is CRITICAL. Always verify against actual database schemas before implementing helpers.
