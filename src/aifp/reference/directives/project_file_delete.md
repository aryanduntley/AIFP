# Directive: project_file_delete

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: project_file_write
**Priority**: HIGH - File removal with database cleanup

---

## Purpose

The `project_file_delete` directive handles safe deletion of files from the project, ensuring both filesystem and database consistency. This directive serves as the **file removal manager**, coordinating deletion across filesystem and `project.db` while preserving referential integrity.

Key responsibilities:
- **Delete file from filesystem** - Remove physical file
- **Update database** - Remove or mark deleted in `project.db`
- **Handle dependencies** - Check and clean up dependent functions and interactions
- **Preserve history** - Option to soft-delete (mark as deleted) vs. hard-delete (remove entirely)
- **Update tasks** - Adjust items/tasks that reference the deleted file
- **Create backup** - Optional backup before deletion
- **Cascade cleanup** - Remove orphaned functions, interactions, flow associations

This is the **safe file remover** - ensures clean deletion with no orphaned database records.

---

## When to Apply

This directive applies when:
- **Removing obsolete code** - Deleting files no longer needed
- **Refactoring** - Consolidating files, removing duplicates
- **Cleanup** - Removing test files, prototypes, or experiments
- **Project evolution** - Removing deprecated implementations
- **Called by other directives**:
  - `project_refactor_path` - Removes old files during refactoring
  - `project_evolution` - Deletes files during architectural changes
  - User directly - Manual file deletion

---

## Workflow

### Trunk: validate_delete_request

Ensures file can be safely deleted and confirms user intent.

**Steps**:
1. **Validate file path** - Check file exists and is within project
2. **Check database** - Verify file is tracked in `project.db`
3. **Analyze dependencies** - Find functions and interactions that depend on this file
4. **Confirm with user** - Verify intent, especially if dependencies exist
5. **Choose delete mode** - Soft delete (mark as deleted) or hard delete (remove entirely)

### Branches

**Branch 1: If file_tracked_in_db**
- **Then**: `check_dependencies`
- **Details**: File is tracked, check for dependencies
  - Query `functions` table for functions defined in file
  - Query `interactions` table for dependencies
  - Check if other files call functions from this file
  - Identify orphaned records if deleted
- **Query**:
  ```sql
  -- Get functions in file
  SELECT id, name FROM functions WHERE file_id = ?;

  -- Get incoming dependencies (other files calling this file's functions)
  SELECT DISTINCT sf.name as source_function, sfi.path as source_file
  FROM interactions i
  JOIN functions tf ON i.target_function_id = tf.id
  JOIN functions sf ON i.source_function_id = sf.id
  JOIN files sfi ON sf.file_id = sfi.id
  WHERE tf.file_id = ? AND sf.file_id != ?;

  -- Get task/item references
  SELECT t.name, i.name
  FROM items i
  JOIN tasks t ON i.task_id = t.id
  WHERE i.reference_table = 'files' AND i.reference_id = ?;
  ```
- **Result**: Dependency analysis complete

**Branch 2: If dependencies_exist**
- **Then**: `warn_and_confirm`
- **Details**: Other files depend on this file
  - List dependent files and functions
  - Warn about potential breakage
  - Prompt: "Delete anyway? This will break dependencies."
  - Offer alternatives:
    - Soft delete (mark deleted but keep in DB for reference)
    - Cancel deletion
    - Continue with hard delete
- **Result**: User confirms or cancels

**Branch 3: If user_confirms_delete**
- **Then**: `create_backup_option`
- **Details**: Offer to backup before deletion
  - Prompt: "Create backup before deleting?"
  - If yes: Copy to `.aifp-project/backups/deleted/[filename]_[timestamp]`
  - If no: Proceed directly to deletion
- **Result**: Backup created or skipped

**Branch 4: If soft_delete_chosen**
- **Then**: `mark_as_deleted`
- **Details**: Mark file as deleted in database, don't remove
  - Update `files` table: Add `deleted_at` timestamp
  - Keep functions and interactions for reference
  - Add note to `notes` table about deletion
  - File remains in database for historical reference
- **SQL**:
  ```sql
  UPDATE files
  SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
  WHERE id = ?;

  INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
  VALUES ('File soft-deleted: [path]. Dependencies preserved for reference.', 'deletion', 'files', ?, 'directive', 'project_file_delete');
  ```
- **Result**: File marked deleted, database intact

**Branch 5: If hard_delete_chosen**
- **Then**: `cascade_delete_database`
- **Details**: Remove file and all related records
  - Delete file from filesystem
  - Delete from `files` table
  - Delete all functions from `functions` table (CASCADE)
  - Delete all interactions from `interactions` table (CASCADE)
  - Delete flow associations from `file_flows` table (CASCADE)
  - Update tasks/items that reference file (mark as orphaned or remove)
  - Log deletion to `notes` table
- **SQL**:
  ```sql
  -- Delete interactions (must be first due to foreign keys)
  DELETE FROM interactions
  WHERE source_function_id IN (SELECT id FROM functions WHERE file_id = ?)
     OR target_function_id IN (SELECT id FROM functions WHERE file_id = ?);

  -- Delete functions
  DELETE FROM functions WHERE file_id = ?;

  -- Delete file-flow associations
  DELETE FROM file_flows WHERE file_id = ?;

  -- Update items referencing this file
  UPDATE items
  SET status = 'orphaned', description = description || ' (File deleted)'
  WHERE reference_table = 'files' AND reference_id = ?;

  -- Delete file record
  DELETE FROM files WHERE id = ?;

  -- Log deletion
  INSERT INTO notes (content, note_type, source, directive_name)
  VALUES ('File hard-deleted: [path]. Removed [N] functions, [M] interactions.', 'deletion', 'directive', 'project_file_delete');
  ```
- **Result**: File and all related records removed

**Branch 6: If file_not_in_db**
- **Then**: `delete_filesystem_only`
- **Details**: File exists but not tracked in database
  - Delete file from filesystem
  - Warn: "File not tracked in database"
  - Log to `notes` as untracked file deletion
- **Result**: File deleted, database unaffected

**Branch 7: If file_not_exists**
- **Then**: `clean_database_only`
- **Details**: File missing from filesystem but in database
  - Prompt: "File already deleted from filesystem. Clean database?"
  - If yes: Perform database cleanup (same as hard delete)
  - Log as orphaned entry cleanup
- **Result**: Database cleaned of stale entry

**Branch 8: If backup_created**
- **Then**: `proceed_with_deletion`
- **Details**: Backup successful, safe to delete
  - Backup path logged
  - Continue with chosen delete mode
- **Result**: Ready for deletion

**Fallback**: `prompt_user`
- Present issue and ask for clarification
- Log to `notes` for future reference

### Error Handling

**on_failure**: `rollback_and_prompt`
- If filesystem deletion fails: Rollback database changes
- If database deletion fails: Keep file on filesystem, prompt user
- Transactional: All-or-nothing for database operations

---

## Examples

### Example 1: Safe Hard Delete (No Dependencies)

**User**: "Delete src/old_helper.py"

**AI Execution**:
1. Validates path: `src/old_helper.py` ✓ Valid
2. Checks file exists: ✓ Present
3. Queries database: Found (ID: 42)
4. Checks dependencies:
   - Functions: 1 (`format_output`)
   - Incoming calls: None
   - Task references: None
5. No dependencies found → Safe to delete
6. Prompts: "Delete src/old_helper.py? (No dependencies found)"
7. User confirms: "Yes"
8. Prompts: "Create backup before deleting?"
9. User confirms: "Yes"
10. Creates backup: `.aifp-project/backups/deleted/old_helper.py_20251027_143000`
11. Prompts: "Hard delete (remove from database) or soft delete (mark as deleted)?"
12. User chooses: "Hard delete"
13. Deletes file from filesystem
14. Removes from database:
    ```sql
    DELETE FROM functions WHERE file_id = 42;
    DELETE FROM files WHERE id = 42;
    ```
15. Logs deletion:
    ```sql
    INSERT INTO notes (content, note_type, source, directive_name)
    VALUES ('File hard-deleted: src/old_helper.py. Removed 1 function. Backup: backups/deleted/old_helper.py_20251027_143000', 'deletion', 'directive', 'project_file_delete');
    ```
16. Reports: "✓ File deleted. Backup: .aifp-project/backups/deleted/old_helper.py_20251027_143000"

### Example 2: Delete with Dependencies (Warning)

**User**: "Delete src/core.py"

**AI Execution**:
1. Validates path: `src/core.py` ✓ Valid
2. Checks file exists: ✓ Present
3. Queries database: Found (ID: 5)
4. Checks dependencies:
   - Functions: 5 (`init_system`, `process_data`, `validate`, `transform`, `output`)
   - Incoming calls: 12 calls from 4 different files
   - Dependent files:
     - `src/main.py` calls `init_system`, `process_data`
     - `src/batch.py` calls `process_data`, `transform`
     - `src/utils.py` calls `validate`
     - `src/export.py` calls `output`
5. Dependencies found → Warn user
6. Prompts:
   ```
   ⚠️  Warning: src/core.py has dependencies

   Functions (5): init_system, process_data, validate, transform, output

   Dependent files (4):
   - src/main.py → calls init_system, process_data
   - src/batch.py → calls process_data, transform
   - src/utils.py → calls validate
   - src/export.py → calls output

   Deleting this file will break 12 function calls in 4 files.

   Options:
   1. Cancel deletion (recommended)
   2. Soft delete (mark deleted, preserve DB records)
   3. Hard delete (remove file and break dependencies)

   Choose option:
   ```
7. User chooses: "2" (Soft delete)
8. Marks as deleted:
   ```sql
   UPDATE files SET deleted_at = CURRENT_TIMESTAMP WHERE id = 5;
   ```
9. Logs:
   ```sql
   INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name, severity)
   VALUES ('File soft-deleted: src/core.py. Functions preserved in DB for reference. 12 dependent calls from 4 files.', 'deletion', 'files', 5, 'directive', 'project_file_delete', 'warning');
   ```
10. Reports: "✓ File marked as deleted. Functions preserved in database for reference."

### Example 3: Delete File Not in Database

**User**: "Delete temp_test.py"

**AI Execution**:
1. Validates path: `temp_test.py` ✓ Valid
2. Checks file exists: ✓ Present
3. Queries database: ✗ Not found
4. Prompts: "File not tracked in database. Delete from filesystem?"
5. User confirms: "Yes"
6. Deletes file from filesystem
7. Logs:
   ```sql
   INSERT INTO notes (content, note_type, source, directive_name)
   VALUES ('Untracked file deleted: temp_test.py', 'deletion', 'directive', 'project_file_delete');
   ```
8. Reports: "✓ File deleted (was not tracked in database)"

### Example 4: Clean Orphaned Database Entry

**User**: "Delete src/removed.py"

**AI Execution**:
1. Validates path: `src/removed.py` ✓ Valid
2. Checks file exists: ✗ Not found
3. Queries database: Found (ID: 18)
4. Prompts:
   ```
   File src/removed.py not found on filesystem but exists in database.

   Database entry:
   - Functions: 2 (helper, validator)
   - Created: 2025-10-20
   - Last updated: 2025-10-22

   Clean up database entry?
   ```
5. User confirms: "Yes"
6. Removes from database:
   ```sql
   DELETE FROM functions WHERE file_id = 18;
   DELETE FROM files WHERE id = 18;
   ```
7. Logs:
   ```sql
   INSERT INTO notes (content, note_type, source, directive_name)
   VALUES ('Orphaned database entry cleaned: src/removed.py (file already deleted from filesystem). Removed 2 functions.', 'cleanup', 'directive', 'project_file_delete');
   ```
8. Reports: "✓ Database cleaned. File was already deleted from filesystem."

### Example 5: Cancelled Deletion

**User**: "Delete src/critical.py"

**AI Execution**:
1. Validates path: `src/critical.py` ✓ Valid
2. Checks file exists: ✓ Present
3. Queries database: Found (ID: 2)
4. Checks dependencies:
   - Functions: 8
   - Incoming calls: 45 calls from 15 files
   - Critical: Part of core system
5. Warns user about extensive dependencies
6. Prompts deletion confirmation
7. User responds: "Cancel"
8. Aborts deletion
9. Reports: "Deletion cancelled. File preserved."

---

## Integration with Other Directives

### Called By:
- `project_refactor_path` - Removes files during refactoring
- `project_evolution` - Deletes files during architectural changes
- User directly - Manual file deletion

### Calls:
- `project_file_read` - Reads file before deletion (for backup)
- `project_update_db` - Syncs database after deletion
- `project_dependency_sync` - Cleans up orphaned records

---

## Database Updates

### Tables Modified:

**Hard Delete**:
```sql
-- Delete interactions first (foreign keys)
DELETE FROM interactions
WHERE source_function_id IN (SELECT id FROM functions WHERE file_id = ?)
   OR target_function_id IN (SELECT id FROM functions WHERE file_id = ?);

-- Delete functions
DELETE FROM functions WHERE file_id = ?;

-- Delete flow associations
DELETE FROM file_flows WHERE file_id = ?;

-- Update items (mark orphaned)
UPDATE items SET status = 'orphaned', description = description || ' (File deleted)'
WHERE reference_table = 'files' AND reference_id = ?;

-- Delete file
DELETE FROM files WHERE id = ?;

-- Log deletion
INSERT INTO notes (content, note_type, source, directive_name)
VALUES (?, 'deletion', 'directive', 'project_file_delete');
```

**Soft Delete**:
```sql
-- Mark file as deleted
UPDATE files SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Log soft deletion
INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
VALUES (?, 'deletion', 'files', ?, 'directive', 'project_file_delete');
```

**Filesystem**:
```bash
# Create backup
cp [file_path] .aifp-project/backups/deleted/[filename]_[timestamp]

# Delete file
rm [file_path]
```

---

## Roadblocks and Resolutions

### Roadblock 1: dependencies_exist
**Issue**: Other files depend on this file's functions
**Resolution**: Warn user, offer soft delete, list all dependencies

### Roadblock 2: file_not_found
**Issue**: File doesn't exist on filesystem
**Resolution**: Offer to clean up database entry only

### Roadblock 3: delete_failed
**Issue**: Filesystem deletion fails (permissions, file locked)
**Resolution**: Rollback database changes, report error, suggest fixing permissions

### Roadblock 4: backup_failed
**Issue**: Cannot create backup before deletion
**Resolution**: Offer to proceed without backup or cancel deletion

### Roadblock 5: critical_file
**Issue**: File has extensive dependencies (> 10 files)
**Resolution**: Strong warning, recommend cancellation, require explicit confirmation

---

## Intent Keywords

- "delete file"
- "remove file"
- "rm"
- "delete"
- "remove"
- "clean up"

**Confidence Threshold**: 0.8 (high threshold for safety)

---

## Related Directives

- `project_file_write` - Creates files
- `project_file_read` - Reads files
- `project_update_db` - Syncs database
- `project_dependency_sync` - Cleans orphaned records
- `project_refactor_path` - Uses deletion during refactoring

---

## Delete Modes

### Soft Delete
- **Filesystem**: File deleted
- **Database**: Marked as deleted (`deleted_at` timestamp)
- **Functions**: Preserved in database
- **Interactions**: Preserved in database
- **Use case**: File removed but may need to reference functions/dependencies

### Hard Delete
- **Filesystem**: File deleted
- **Database**: All records removed
- **Functions**: Deleted (CASCADE)
- **Interactions**: Deleted (CASCADE)
- **Use case**: Complete removal, file and history not needed

---

## Safety Checklist

Before deletion, verify:
- [ ] File exists and path is valid
- [ ] Database entry checked for dependencies
- [ ] User confirmed deletion intent
- [ ] Backup created (if requested)
- [ ] Delete mode chosen (soft vs. hard)
- [ ] Dependencies analyzed and user warned
- [ ] Cascade deletion plan clear
- [ ] Rollback possible if failure occurs

---

## Notes

- **Always check dependencies** - Prevent breaking other files
- **Offer backups** - Protect against accidental deletion
- **Transactional deletes** - All-or-nothing for database
- **Soft delete preferred** - Preserve history when uncertain
- **Log all deletions** - Audit trail in `notes` table
- **High confirmation threshold** - Multiple prompts for safety
- **Rollback on failure** - Never leave inconsistent state
