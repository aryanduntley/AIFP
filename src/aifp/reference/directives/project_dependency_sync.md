# Directive: project_dependency_sync

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: project_update_db
**Priority**: MEDIUM - Database-codebase consistency maintenance

---

## Purpose

The `project_dependency_sync` directive compares functions and flows in physical files against database records, resolving discrepancies to maintain consistency. This directive serves as the **consistency enforcer**, ensuring `project.db` accurately reflects the codebase state.

Key responsibilities:
- **Compare files to database** - Detect missing, stale, or orphaned records
- **Sync function definitions** - Update functions table with current code
- **Update dependencies** - Sync interactions table with actual function calls
- **Reconcile checksums** - Detect external file modifications
- **Clean orphaned records** - Remove database entries for deleted files
- **Preserve intentional state** - Don't overwrite user-defined metadata

This is the **database-codebase synchronizer** - fixes drift between code and metadata.

---

## When to Apply

This directive applies when:
- **External file modifications** - Files changed outside AIFP sessions
- **Database desync suspected** - Checksums mismatch or metadata stale
- **After bulk changes** - Git merge, external edits, refactoring
- **Periodic maintenance** - Regular sync to catch drift
- **Called by other directives**:
  - `project_file_read` - Suggests sync on checksum mismatch
  - `git_detect_external_changes` - Syncs after detecting git changes
  - User directly - Manual sync trigger

---

## Workflow

### Trunk: compare_db_and_files

Compares physical files with database records to identify discrepancies.

**Steps**:
1. **List all files in DB** - Query files table
2. **List all files on disk** - Scan project directory
3. **Compare lists** - Identify missing/extra files
4. **Check checksums** - Detect modified files
5. **Parse modified files** - Extract functions and dependencies
6. **Reconcile differences** - Update, insert, or delete records

### Branches

**Branch 1: If missing_function_in_db**
- **Then**: `insert_function_entry`
- **Details**: Function exists in file but not in database
  - Parse function from file (name, parameters, return type)
  - Extract metadata (purity level, side effects)
  - Insert into functions table
  - Log addition
- **SQL**:
  ```sql
  INSERT INTO functions (
    file_id,
    name,
    purpose,
    purity_level,
    side_effects_json,
    parameters_json,
    return_type,
    created_at,
    updated_at
  ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
  ```
- **Result**: Missing function added to database

**Branch 2: If db_function_stale**
- **Then**: `update_dependency_entry`
- **Details**: Function exists but metadata is outdated
  - Re-parse function from file
  - Compare with database record
  - Update changed fields (parameters, return type, purity)
  - Preserve user-defined fields (purpose, notes)
- **SQL**:
  ```sql
  UPDATE functions
  SET parameters_json = ?,
      return_type = ?,
      purity_level = ?,
      updated_at = CURRENT_TIMESTAMP
  WHERE id = ?;
  ```
- **Result**: Function metadata updated

**Branch 3: If function_in_db_not_in_file**
- **Then**: `mark_function_deleted_or_remove`
- **Details**: Database has function that doesn't exist in file
  - Check if file still exists
  - If file deleted: Mark function as deleted or remove
  - If file exists: Function was removed from file, delete from DB
- **SQL**:
  ```sql
  -- Option 1: Soft delete (mark deleted_at)
  UPDATE functions SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?;

  -- Option 2: Hard delete (remove)
  DELETE FROM functions WHERE id = ?;
  ```
- **Result**: Orphaned function removed or marked deleted

**Branch 4: If unlinked_file**
- **Then**: `link_to_flow`
- **Details**: File exists but not linked to any flow
  - Call `project_theme_flow_mapping` to assign theme/flow
  - Link file to appropriate flow
- **Result**: File properly categorized

**Branch 5: If file_on_disk_not_in_db**
- **Then**: `add_file_to_database`
- **Details**: Physical file exists but not tracked
  - Check if file should be tracked (not .gitignore, not binary)
  - Parse file for functions
  - Insert into files table
  - Insert functions
  - Assign theme/flow
  - Log addition
- **SQL**:
  ```sql
  INSERT INTO files (project_id, path, language, checksum, created_at, updated_at)
  VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

  -- Get file_id
  SELECT last_insert_rowid() as file_id;
  ```
- **Result**: New file tracked in database

**Branch 6: If file_in_db_not_on_disk**
- **Then**: `mark_file_deleted_or_remove`
- **Details**: Database has file that doesn't exist on filesystem
  - Soft delete: Update files.deleted_at
  - Hard delete: Remove file and cascade delete functions
  - Prompt user to choose
- **SQL**:
  ```sql
  -- Soft delete
  UPDATE files SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?;

  -- Hard delete (cascade)
  DELETE FROM interactions WHERE source_function_id IN (SELECT id FROM functions WHERE file_id = ?);
  DELETE FROM functions WHERE file_id = ?;
  DELETE FROM file_flows WHERE file_id = ?;
  DELETE FROM files WHERE id = ?;
  ```
- **Result**: Orphaned file cleaned from database

**Branch 7: If checksum_mismatch**
- **Then**: `re_parse_file_and_update`
- **Details**: File modified externally
  - Re-parse entire file
  - Update checksum
  - Update all functions
  - Update interactions
  - Log sync
- **SQL**:
  ```sql
  UPDATE files SET checksum = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;

  -- Update all functions from this file
  -- (individual UPDATE statements per function)
  ```
- **Result**: File metadata synchronized

**Branch 8: If dependency_missing**
- **Then**: `add_interaction_record**
- **Details**: Function calls another but interaction not in DB
  - Parse function code for calls
  - Identify called functions
  - Insert into interactions table
- **SQL**:
  ```sql
  INSERT INTO interactions (source_function_id, target_function_id, interaction_type)
  VALUES (?, ?, 'call');
  ```
- **Result**: Missing dependency tracked

**Branch 9: If dependency_stale**
- **Then**: `remove_interaction_record`
- **Details**: Interaction in DB but not in current code
  - Function no longer calls another
  - Delete interaction record
- **SQL**:
  ```sql
  DELETE FROM interactions
  WHERE source_function_id = ? AND target_function_id = ?;
  ```
- **Result**: Stale dependency removed

**Branch 10: If sync_complete**
- **Then**: `log_sync_status`
- **Details**: Record sync results
  - Count files synced
  - Count functions added/updated/deleted
  - Count interactions synced
  - Log to notes table
- **SQL**:
  ```sql
  INSERT INTO notes (content, note_type, source, directive_name)
  VALUES ('Dependency sync complete: [N] files, [M] functions, [K] interactions updated', 'sync', 'directive', 'project_dependency_sync');
  ```
- **Result**: Sync logged for audit

**Fallback**: `prompt_user`
- Present discrepancy and ask how to resolve
- Log decision for future reference

### Error Handling

**on_failure**: `rollback_and_prompt`
- If sync fails: Rollback partial changes
- Prompt user with specific error
- Common issues: Parse error, database lock, invalid file

---

## Examples

### Example 1: Function Added to File Externally

**Context**: User edited `src/matrix.py` outside AIFP and added `transpose` function

**AI Execution**:
1. Reads `src/matrix.py` from disk
2. Calculates checksum: `sha256:new123...`
3. Compares with DB: `sha256:old789...` ✗ Mismatch
4. Re-parses file:
   - Existing functions: `multiply_matrices`, `validate_dimensions`
   - New function found: `transpose`
5. Checks DB for `transpose`: Not found
6. Inserts new function:
   ```sql
   INSERT INTO functions (file_id, name, purpose, purity_level, parameters_json, return_type, created_at, updated_at)
   VALUES (15, 'transpose', 'Transpose matrix', 'pure', '[{"name": "matrix", "type": "List[List[float]]"}]', 'List[List[float]]', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
   ```
7. Updates file checksum:
   ```sql
   UPDATE files SET checksum = 'sha256:new123...', updated_at = CURRENT_TIMESTAMP WHERE id = 15;
   ```
8. Logs sync:
   ```
   File synced: src/matrix.py. Added function: transpose
   ```

### Example 2: File Deleted Externally

**Context**: User deleted `src/old_utils.py` outside AIFP

**AI Execution**:
1. Queries all files from database:
   - Found: `src/old_utils.py` (file_id=23)
2. Checks filesystem: File not found
3. Prompts user:
   ```
   File in database but not on filesystem: src/old_utils.py

   Options:
   1. Soft delete (mark deleted, keep metadata)
   2. Hard delete (remove from database)
   3. Skip (file may return later)
   ```
4. User chooses: "2" (Hard delete)
5. Cascades delete:
   ```sql
   DELETE FROM interactions WHERE source_function_id IN (SELECT id FROM functions WHERE file_id = 23);
   DELETE FROM functions WHERE file_id = 23;
   DELETE FROM file_flows WHERE file_id = 23;
   DELETE FROM files WHERE id = 23;
   ```
6. Logs cleanup:
   ```
   File deleted: src/old_utils.py (removed from database)
   ```

### Example 3: Function Modified Externally

**Context**: User changed `multiply_matrices` signature from `(a, b)` to `(a, b, validate=True)`

**AI Execution**:
1. Detects checksum mismatch for `src/matrix.py`
2. Re-parses `multiply_matrices`:
   - Old parameters: `[{"name": "a"}, {"name": "b"}]`
   - New parameters: `[{"name": "a"}, {"name": "b"}, {"name": "validate", "default": "True"}]`
3. Updates function metadata:
   ```sql
   UPDATE functions
   SET parameters_json = '[{"name": "a", "type": "List[List[float]]"}, {"name": "b", "type": "List[List[float]]"}, {"name": "validate", "type": "bool", "default": true}]',
       updated_at = CURRENT_TIMESTAMP
   WHERE file_id = 15 AND name = 'multiply_matrices';
   ```
4. Logs update:
   ```
   Function updated: multiply_matrices (parameters changed)
   ```

### Example 4: New File Created Externally

**Context**: User created `src/vector.py` with Git and didn't use AIFP

**AI Execution**:
1. Scans project directory for all `.py` files
2. Finds `src/vector.py` not in database
3. Prompts:
   ```
   File found but not tracked: src/vector.py

   Track this file in project database?
   ```
4. User confirms: "Yes"
5. Parses file:
   - Functions: `dot_product`, `cross_product`, `magnitude`
6. Inserts file record:
   ```sql
   INSERT INTO files (project_id, path, language, checksum, created_at, updated_at)
   VALUES (1, 'src/vector.py', 'python', 'sha256:abc...', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
   -- Returns file_id: 48
   ```
7. Inserts functions:
   ```sql
   INSERT INTO functions (file_id, name, purity_level, ...) VALUES (48, 'dot_product', 'pure', ...);
   INSERT INTO functions (file_id, name, purity_level, ...) VALUES (48, 'cross_product', 'pure', ...);
   INSERT INTO functions (file_id, name, purity_level, ...) VALUES (48, 'magnitude', 'pure', ...);
   ```
8. Calls `project_theme_flow_mapping` to assign theme/flow
9. Logs addition:
   ```
   File tracked: src/vector.py (3 functions added)
   ```

### Example 5: Orphaned Interactions

**Context**: Function `helper_a` was deleted but interactions still reference it

**AI Execution**:
1. Queries interactions table:
   ```sql
   SELECT i.id, sf.name as source, tf.name as target
   FROM interactions i
   LEFT JOIN functions sf ON i.source_function_id = sf.id
   LEFT JOIN functions tf ON i.target_function_id = tf.id
   WHERE sf.id IS NULL OR tf.id IS NULL;
   -- Found: interaction referencing deleted function_id=99
   ```
2. Identifies orphaned interactions
3. Deletes orphaned records:
   ```sql
   DELETE FROM interactions WHERE source_function_id = 99 OR target_function_id = 99;
   ```
4. Logs cleanup:
   ```
   Cleaned 3 orphaned interaction records
   ```

### Example 6: Bulk Sync After Git Merge

**Context**: Git merge brought in 15 new files and modified 8 existing files

**AI Execution**:
1. Triggered by `git_detect_external_changes`
2. Scans all files for checksum mismatches: Found 8 changed, 15 new
3. For each changed file:
   - Re-parse functions
   - Update metadata
   - Update interactions
4. For each new file:
   - Parse and insert file record
   - Parse and insert functions
   - Assign theme/flow
5. Logs bulk sync:
   ```
   Bulk sync complete:
   - 8 files updated
   - 15 files added
   - 42 functions synced
   - 18 new interactions tracked
   ```

---

## Integration with Other Directives

### Called By:
- `project_file_read` - Suggests sync on checksum mismatch
- `git_detect_external_changes` - Syncs after git changes
- `aifp_status` - Periodic sync check
- User directly - Manual sync

### Calls:
- `project_theme_flow_mapping` - Assigns themes/flows to new files
- `project_file_read` - Parses files for sync
- `project_update_db` - Updates metadata

---

## Database Updates

### Tables Modified:

**project.db**:
```sql
-- Update file checksum
UPDATE files SET checksum = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Insert missing function
INSERT INTO functions (file_id, name, purpose, purity_level, ...) VALUES (...);

-- Update stale function
UPDATE functions SET parameters_json = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Delete orphaned function
DELETE FROM functions WHERE id = ?;

-- Insert missing file
INSERT INTO files (project_id, path, language, checksum, ...) VALUES (...);

-- Soft delete file
UPDATE files SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Hard delete file (cascade)
DELETE FROM files WHERE id = ?;

-- Insert missing interaction
INSERT INTO interactions (source_function_id, target_function_id, interaction_type) VALUES (?, ?, 'call');

-- Delete stale interaction
DELETE FROM interactions WHERE source_function_id = ? AND target_function_id = ?;

-- Log sync
INSERT INTO notes (content, note_type, source, directive_name)
VALUES (?, 'sync', 'directive', 'project_dependency_sync');
```

---

## Roadblocks and Resolutions

### Roadblock 1: unresolved_dependency
**Issue**: Function calls another but target doesn't exist
**Resolution**: Warn user, flag as missing dependency, suggest creating target

### Roadblock 2: parse_error
**Issue**: Cannot parse file due to syntax error
**Resolution**: Skip file, log error, prompt user to fix syntax

### Roadblock 3: ambiguous_function_match
**Issue**: Function name changed, unclear if new or renamed
**Resolution**: Prompt user: "Is function_new a renamed function_old?"

### Roadblock 4: circular_dependency
**Issue**: Functions have circular call patterns
**Resolution**: Log warning, allow (circular deps are valid), track in interactions

---

## Intent Keywords

- "sync database"
- "reconcile files"
- "update metadata"
- "sync dependencies"
- "clean database"
- "fix drift"

**Confidence Threshold**: 0.7

---

## Related Directives

- `project_update_db` - Updates database after file writes
- `project_file_read` - Reads files for parsing
- `project_theme_flow_mapping` - Assigns themes/flows
- `git_detect_external_changes` - Detects external modifications
- `project_integrity_check` - Validates database consistency

---

## Sync Modes

### Full Sync
- Scans all files and database records
- Reconciles all discrepancies
- Time-intensive but thorough
- Use after major changes (git merge, bulk refactor)

### Incremental Sync
- Only checks files with checksum mismatches
- Faster, targets known changes
- Use for periodic maintenance

### File-Specific Sync
- Syncs single file on demand
- Quick, targeted fix
- Use when checksum mismatch detected

---

## Sync Report Format

After sync completes, generate report:

```
Dependency Sync Report
═══════════════════════

Files Scanned: 42
Files Modified: 8
Files Added: 3
Files Deleted: 1

Functions Updated: 15
Functions Added: 7
Functions Deleted: 2

Interactions Added: 12
Interactions Deleted: 5

Orphaned Records Cleaned: 3

Warnings: 2
- src/utils/helper.py: Parse error (syntax)
- src/api/routes.py: Unresolved dependency (missing_func)

Status: ✓ Sync Complete
```

---

## Notes

- **Preserve user metadata** - Don't overwrite purpose, notes fields
- **Detect external changes** - Checksums catch modifications
- **Support soft delete** - Preserve history when uncertain
- **Parse carefully** - Handle syntax errors gracefully
- **Log all changes** - Audit trail for sync actions
- **Transactional sync** - Rollback on failure
- **Prompt on ambiguity** - Don't guess, ask user
- **Enable bulk operations** - Efficient sync after major changes
