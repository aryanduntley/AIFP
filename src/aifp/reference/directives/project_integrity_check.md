# Directive: project_integrity_check

**Type**: Project
**Level**: 4 (State Management)
**Parent Directive**: project_dependency_sync
**Priority**: LOW - Database consistency validation

---

## Purpose

The `project_integrity_check` directive runs validation queries to detect orphaned records, missing links, and checksum mismatches within `project.db`. This directive serves as the **database integrity guardian**, ensuring internal DB consistency and preventing corruption during iterative project growth.

Key responsibilities:
- **Detect orphaned records** - Find records without valid parents
- **Validate foreign keys** - Ensure all relationships intact
- **Check checksums** - Detect external file modifications
- **Repair links** - Auto-correct fixable integrity issues
- **Report violations** - Alert user to data inconsistencies
- **Prevent corruption** - Maintain database health over time

This is the **database validator** - ensures project.db remains consistent and trustworthy.

---

## When to Apply

This directive applies when:
- **Periodic maintenance** - Scheduled integrity check (weekly, after major operations)
- **After bulk operations** - Git merge, mass file updates, dependency sync
- **Database suspicion** - User suspects data corruption
- **Before archival** - Validate integrity before project archive
- **Called by other directives**:
  - `project_dependency_sync` - Checks integrity after sync operations
  - `project_backup_restore` - Validates before backup or after restore
  - `project_archive` - Ensures clean state before archiving
  - User directly - Manual integrity check

---

## Workflow

### Trunk: run_integrity_queries

Executes a series of validation queries to detect inconsistencies.

**Steps**:
1. **Define check scope** - Full database or specific tables
2. **Run foreign key checks** - Verify all relationships valid
3. **Check for orphans** - Detect records without parents
4. **Validate checksums** - Compare file checksums to database
5. **Check duplicate records** - Detect unintended duplicates
6. **Assess severity** - Critical errors vs warnings
7. **Attempt auto-repair** - Fix safe issues automatically
8. **Report findings** - Summary of issues found and fixed

### Branches

**Branch 1: If missing_foreign_key**
- **Then**: `repair_link`
- **Details**: Foreign key reference points to non-existent record
  - Identify the broken link (parent record missing)
  - Check if parent can be recreated or link should be removed
  - Options: Link to default parent, create parent, remove child
  - Auto-fix if safe (remove orphaned items/subtasks)
  - Prompt user for critical repairs (files, functions)
- **SQL**:
  ```sql
  -- Check items with missing task references
  SELECT i.id, i.name, i.task_id
  FROM items i
  LEFT JOIN tasks t ON i.task_id = t.id
  WHERE t.id IS NULL;

  -- Check subtasks with missing task references
  SELECT st.id, st.name, st.task_id
  FROM subtasks st
  LEFT JOIN tasks t ON st.task_id = t.id
  WHERE t.id IS NULL;

  -- Check tasks with missing milestone references
  SELECT t.id, t.name, t.milestone_id
  FROM tasks t
  LEFT JOIN milestones m ON t.milestone_id = m.id
  WHERE m.id IS NULL;

  -- Check functions with missing file references
  SELECT f.id, f.name, f.file_id
  FROM functions f
  LEFT JOIN files fi ON f.file_id = fi.id
  WHERE fi.id IS NULL;
  ```
- **Auto-Fix**:
  ```sql
  -- Safe: Remove orphaned items (small granularity)
  DELETE FROM items WHERE id IN (
    SELECT i.id FROM items i LEFT JOIN tasks t ON i.task_id = t.id WHERE t.id IS NULL
  );

  -- Prompt: Link orphaned task to default milestone or delete
  -- (User decision required)
  ```
- **Result**: Broken foreign keys repaired or flagged for user action

**Branch 2: If orphaned_records_detected**
- **Then**: `identify_and_prompt`
- **Details**: Records exist without valid parent relationships
  - List all orphaned records with context
  - Categorize by severity (items=low, tasks=medium, files=high)
  - Options: Link to parent, delete, ignore
  - Log orphaned records in notes
- **Example Output**:
  ```
  ⚠️ Orphaned Records Detected

  Items: 3 orphaned
  - Item #42: "Fix bug" (task_id=99, task not found)
  - Item #58: "Write test" (task_id=105, task not found)
  - Item #67: "Deploy" (task_id=112, task not found)

  Tasks: 1 orphaned
  - Task #15: "Implement caching" (milestone_id=8, milestone not found)

  Functions: 2 orphaned
  - Function "calculate" (file_id=22, file not found)
  - Function "process" (file_id=22, file not found)

  Options:
  1. Auto-delete orphaned items (safe, low impact)
  2. Link task #15 to existing milestone (specify milestone)
  3. Recreate missing file #22 (manual intervention)
  4. Ignore (not recommended)
  ```
- **Result**: Orphans identified, user decides action

**Branch 3: If checksum_error**
- **Then**: `recalculate_file_checksum`
- **Details**: File checksum in database doesn't match actual file
  - Recalculate checksum from filesystem
  - Compare with database value
  - If different: File modified externally
  - Trigger `project_dependency_sync` to update metadata
- **SQL**:
  ```sql
  -- Check for checksum mismatches
  SELECT id, path, checksum, updated_at
  FROM files
  WHERE project_id = ?
  ORDER BY path;
  -- (AI calculates actual checksum from filesystem and compares)
  ```
- **Action**:
  ```python
  # Pseudo-code
  for file_record in files:
      actual_checksum = calculate_sha256(file_record.path)
      if actual_checksum != file_record.checksum:
          log_mismatch(file_record.path, actual_checksum, file_record.checksum)
          trigger_dependency_sync(file_record.id)
  ```
- **Result**: Checksums validated, mismatches trigger sync

**Branch 4: If duplicate_records**
- **Then**: `detect_and_merge_duplicates`
- **Details**: Same entity exists multiple times (same name, same parent)
  - Detect duplicate tasks (same name, same milestone)
  - Detect duplicate milestones (same name, same stage)
  - Detect duplicate functions (same name, same file)
  - Merge or prompt user to resolve
- **SQL**:
  ```sql
  -- Duplicate tasks
  SELECT milestone_id, name, COUNT(*) as count
  FROM tasks
  GROUP BY milestone_id, name
  HAVING count > 1;

  -- Duplicate functions
  SELECT file_id, name, COUNT(*) as count
  FROM functions
  GROUP BY file_id, name
  HAVING count > 1;
  ```
- **Result**: Duplicates identified, merge or flag

**Branch 5: If circular_references**
- **Then**: `detect_cycles`
- **Details**: Circular dependencies in relationships
  - Check for circular subtask references
  - Check for circular function dependencies
  - Circular flows are valid, but flag for awareness
- **SQL**:
  ```sql
  -- Circular function dependencies (recursive CTE)
  WITH RECURSIVE dependency_chain(source_id, target_id, depth, path) AS (
    SELECT source_function_id, target_function_id, 1, CAST(source_function_id AS TEXT) || '->' || CAST(target_function_id AS TEXT)
    FROM interactions
    UNION ALL
    SELECT dc.source_id, i.target_function_id, dc.depth + 1, dc.path || '->' || CAST(i.target_function_id AS TEXT)
    FROM dependency_chain dc
    JOIN interactions i ON dc.target_id = i.source_function_id
    WHERE dc.depth < 10 AND dc.path NOT LIKE '%' || CAST(i.target_function_id AS TEXT) || '%'
  )
  SELECT source_id, target_id, path
  FROM dependency_chain
  WHERE source_id = target_id;
  ```
- **Result**: Circular dependencies detected and logged

**Branch 6: If data_type_violations**
- **Then**: `validate_field_types`
- **Details**: Check for invalid data in typed fields
  - Status fields must be valid enum values
  - Priority fields must be 1-5
  - Dates must be valid timestamps
  - JSON fields must be valid JSON
- **SQL**:
  ```sql
  -- Invalid status values
  SELECT id, name, status FROM tasks WHERE status NOT IN ('pending', 'in_progress', 'paused', 'completed', 'cancelled');

  -- Invalid priority values
  SELECT id, name, priority FROM tasks WHERE priority NOT BETWEEN 1 AND 5;

  -- Invalid JSON (requires JSON validation function)
  SELECT id, name FROM functions WHERE side_effects_json IS NOT NULL AND json_valid(side_effects_json) = 0;
  ```
- **Result**: Invalid data flagged for correction

**Branch 7: If referential_integrity_passed**
- **Then**: `log_integrity_status`
- **Details**: All checks passed, database is healthy
  - Log successful integrity check in notes
  - Report "No issues found"
  - Include check timestamp and scope
- **SQL**:
  ```sql
  INSERT INTO notes (content, note_type, source, directive_name, severity)
  VALUES ('Integrity check passed: No issues found. Scope: Full database.', 'integrity_check', 'directive', 'project_integrity_check', 'info');
  ```
- **Result**: Clean bill of health logged

**Branch 8: If issues_found_and_auto_fixed**
- **Then**: `report_fixes`
- **Details**: Issues detected and automatically repaired
  - List fixes applied (orphaned items deleted, checksums updated)
  - Log auto-fixes in notes
  - Report summary to user
- **Result**: Fixes applied, user informed

**Fallback**: `log_integrity_status`
- Log whatever findings exist (even if incomplete)
- Ensure audit trail maintained

### Error Handling

**on_failure**: `prompt_user`
- If integrity check fails: Log error, report issue
- Common issues: Database locked, query syntax errors, permission issues

---

## Examples

### Example 1: Orphaned Items Detected and Auto-Fixed

**Context**: Items reference deleted tasks

**AI Execution**:
1. Runs orphan check:
   ```sql
   SELECT i.id, i.name, i.task_id FROM items i LEFT JOIN tasks t ON i.task_id = t.id WHERE t.id IS NULL;
   -- Results: 3 orphaned items
   ```
2. Identifies orphans:
   - Item #42: "Fix bug" (task_id=99 not found)
   - Item #58: "Write test" (task_id=105 not found)
   - Item #67: "Deploy" (task_id=112 not found)
3. Assesses severity: Low (items are granular, safe to delete)
4. Auto-fixes:
   ```sql
   DELETE FROM items WHERE id IN (42, 58, 67);
   ```
5. Logs:
   ```sql
   INSERT INTO notes (content, note_type, source, directive_name, severity)
   VALUES ('Integrity check: Auto-deleted 3 orphaned items (task references invalid)', 'integrity_fix', 'directive', 'project_integrity_check', 'info');
   ```
6. Reports:
   ```
   ✓ Integrity Check Complete

   Issues Found: 3 orphaned items
   Auto-Fixed: 3 items deleted (safe cleanup)

   Details:
   - Item #42, #58, #67 removed (task parents not found)
   ```

### Example 2: Checksum Mismatch Detected

**Context**: File modified externally, checksum doesn't match

**AI Execution**:
1. Queries all files:
   ```sql
   SELECT id, path, checksum FROM files WHERE project_id = 1;
   ```
2. Calculates actual checksums from filesystem:
   - `src/auth.py`: Database=sha256:abc123, Actual=sha256:xyz789 ✗
3. Detects mismatch for `src/auth.py`
4. Triggers `project_dependency_sync`:
   ```
   File modified externally: src/auth.py
   Triggering dependency sync to update metadata...
   ```
5. Logs:
   ```sql
   INSERT INTO notes (content, note_type, source, directive_name, severity)
   VALUES ('Integrity check: Checksum mismatch for src/auth.py. Triggered dependency sync.', 'integrity_warning', 'directive', 'project_integrity_check', 'warning');
   ```
6. Returns after sync completes

### Example 3: Orphaned Task Requires User Decision

**Context**: Task has no milestone parent

**AI Execution**:
1. Runs orphan check:
   ```sql
   SELECT t.id, t.name, t.milestone_id FROM tasks t LEFT JOIN milestones m ON t.milestone_id = m.id WHERE m.id IS NULL;
   -- Result: Task #15 "Implement caching" (milestone_id=8 not found)
   ```
2. Assesses severity: Medium (tasks are significant, user decision needed)
3. Queries available milestones:
   ```sql
   SELECT id, name FROM milestones WHERE status != 'completed' ORDER BY priority DESC;
   -- Results: Milestone #3 "Core Features", Milestone #5 "Performance"
   ```
4. Prompts user:
   ```
   ⚠️ Orphaned Task Detected

   Task: "Implement caching" (id=15)
   Issue: Milestone #8 not found

   Options:
   1. Link to Milestone #3 "Core Features"
   2. Link to Milestone #5 "Performance"
   3. Create new milestone for this task
   4. Delete task (not recommended)

   Choose action:
   ```
5. User chooses: "2" (Link to Performance)
6. Updates task:
   ```sql
   UPDATE tasks SET milestone_id = 5 WHERE id = 15;
   ```
7. Logs fix:
   ```sql
   INSERT INTO notes (content, note_type, source, directive_name)
   VALUES ('Integrity fix: Linked orphaned task "Implement caching" to milestone "Performance"', 'integrity_fix', 'directive', 'project_integrity_check');
   ```

### Example 4: Duplicate Functions Detected

**Context**: Same function name appears twice in same file

**AI Execution**:
1. Runs duplicate check:
   ```sql
   SELECT file_id, name, COUNT(*) as count FROM functions GROUP BY file_id, name HAVING count > 1;
   -- Result: file_id=10, name="process", count=2
   ```
2. Queries duplicate details:
   ```sql
   SELECT id, name, purity_level, created_at FROM functions WHERE file_id = 10 AND name = 'process';
   -- Results:
   -- id=42, process, pure, 2025-10-20
   -- id=58, process, mostly_pure, 2025-10-25
   ```
3. Detects: Likely the same function parsed twice
4. Prompts user:
   ```
   ⚠️ Duplicate Functions Detected

   File: src/utils.py (file_id=10)
   Function: "process" appears 2 times

   Version 1: id=42, pure, created 2025-10-20
   Version 2: id=58, mostly_pure, created 2025-10-25

   Options:
   1. Keep newer version (id=58), delete old
   2. Keep older version (id=42), delete new
   3. Manually inspect and decide
   4. Keep both (if legitimately different)

   Choose action:
   ```
5. User chooses: "1" (Keep newer)
6. Deletes old:
   ```sql
   DELETE FROM interactions WHERE source_function_id = 42 OR target_function_id = 42;
   DELETE FROM functions WHERE id = 42;
   ```
7. Logs:
   ```
   Duplicate function resolved: Kept newer "process" (id=58), deleted old (id=42)
   ```

### Example 5: Clean Bill of Health

**Context**: No integrity issues found

**AI Execution**:
1. Runs all integrity checks:
   - Foreign keys: ✓ All valid
   - Orphaned records: ✓ None found
   - Checksums: ✓ All match
   - Duplicates: ✓ None found
   - Data types: ✓ All valid
2. Logs success:
   ```sql
   INSERT INTO notes (content, note_type, source, directive_name, severity)
   VALUES ('Integrity check passed: No issues found. Checked 5 tables, 342 records.', 'integrity_check', 'directive', 'project_integrity_check', 'info');
   ```
3. Reports:
   ```
   ✓ Database Integrity: HEALTHY

   All checks passed:
   - Foreign keys: ✓
   - Orphaned records: ✓
   - Checksums: ✓
   - Duplicates: ✓
   - Data types: ✓

   Tables checked: 5
   Records validated: 342

   Database is in good health.
   ```

### Example 6: Critical Error - Orphaned File

**Context**: Function references deleted file

**AI Execution**:
1. Runs orphan check:
   ```sql
   SELECT f.id, f.name, f.file_id FROM functions f LEFT JOIN files fi ON f.file_id = fi.id WHERE fi.id IS NULL;
   -- Result: Functions "calculate", "process" (file_id=22 not found)
   ```
2. Assesses severity: HIGH (functions without files are critical)
3. Checks if file exists on filesystem:
   - File path from database: `src/math/utils.py`
   - Filesystem check: File not found
4. Prompts user:
   ```
   ❌ Critical Integrity Issue

   2 functions reference missing file (file_id=22)
   - Function: "calculate"
   - Function: "process"

   Expected path: src/math/utils.py
   Filesystem: File not found

   This suggests the file was deleted outside AIFP.

   Options:
   1. Recreate file record (if file exists elsewhere)
   2. Delete orphaned functions
   3. Restore from backup

   Choose action:
   ```
5. User chooses: "2" (Delete functions)
6. Executes cleanup:
   ```sql
   DELETE FROM interactions WHERE source_function_id IN (SELECT id FROM functions WHERE file_id = 22);
   DELETE FROM functions WHERE file_id = 22;
   ```
7. Logs:
   ```
   Critical integrity fix: Deleted 2 orphaned functions (file_id=22 not found)
   ```

---

## Integration with Other Directives

### Called By:
- `project_dependency_sync` - Checks integrity after sync
- `project_backup_restore` - Validates before backup/after restore
- `project_archive` - Ensures clean state before archiving
- User directly - Manual integrity check

### Calls:
- `project_dependency_sync` - Triggered on checksum mismatches
- Logging functions - Records integrity check results

---

## Database Updates

### Tables Modified:

**project.db**:
```sql
-- Delete orphaned items (auto-fix)
DELETE FROM items WHERE id IN (...);

-- Delete orphaned subtasks (auto-fix)
DELETE FROM subtasks WHERE id IN (...);

-- Update orphaned task milestone (user-directed)
UPDATE tasks SET milestone_id = ? WHERE id = ?;

-- Delete duplicate functions (user-directed)
DELETE FROM functions WHERE id = ?;

-- Log integrity check results
INSERT INTO notes (content, note_type, source, directive_name, severity)
VALUES (?, 'integrity_check', 'directive', 'project_integrity_check', ?);
```

---

## Roadblocks and Resolutions

### Roadblock 1: data_misalignment
**Issue**: Foreign key references point to missing records
**Resolution**: Auto-correct links where safe (items, subtasks), prompt user for critical records (tasks, files, functions)

### Roadblock 2: checksum_corruption
**Issue**: File checksums don't match, files modified externally
**Resolution**: Trigger `project_dependency_sync` to update metadata and re-parse files

### Roadblock 3: orphaned_functions
**Issue**: Functions exist without parent file records
**Resolution**: Prompt user to delete functions or recreate file record

### Roadblock 4: circular_dependencies
**Issue**: Functions have circular call patterns
**Resolution**: Log warning, allow (circular deps are valid in some cases), track in interactions

---

## Intent Keywords

- "integrity"
- "verify database"
- "consistency"
- "check database"
- "validate"
- "orphaned records"

**Confidence Threshold**: 0.8

---

## Related Directives

- `project_dependency_sync` - Parent directive, syncs code to database
- `project_backup_restore` - Uses integrity check before backup
- `project_archive` - Validates integrity before archiving
- `project_error_handling` - Handles integrity check failures

---

## Integrity Check Categories

### Foreign Key Validation
- **Tables**: items, subtasks, tasks, milestones, functions, interactions, file_flows, flow_themes
- **Action**: Verify all foreign key references point to valid parent records
- **Auto-Fix**: Delete orphaned items/subtasks (low impact)
- **Prompt**: Orphaned tasks, functions, files (high impact)

### Checksum Validation
- **Tables**: files
- **Action**: Recalculate checksums from filesystem, compare to database
- **Auto-Fix**: Trigger `project_dependency_sync` on mismatch
- **Result**: Database metadata synchronized with actual files

### Duplicate Detection
- **Tables**: tasks, milestones, functions
- **Action**: Detect same entity appearing multiple times
- **Prompt**: User decides which to keep, which to delete

### Data Type Validation
- **Tables**: All tables with enum/constrained fields
- **Action**: Validate status, priority, JSON fields
- **Auto-Fix**: Correct invalid enum values if mapping obvious
- **Prompt**: Complex cases requiring user decision

---

## Check Scope Options

### Full Database Check
- **Duration**: ~2-5 seconds for typical project
- **When**: Scheduled maintenance, before archival
- **Thoroughness**: All tables, all validations

### Quick Check
- **Duration**: <1 second
- **When**: After routine operations
- **Thoroughness**: Foreign keys and orphans only

### Targeted Check
- **Duration**: Variable
- **When**: After specific operations (e.g., file sync)
- **Thoroughness**: Specific tables (e.g., files, functions only)

---

## Notes

- **Run periodically** - Weekly or after major operations
- **Auto-fix safe issues** - Items, subtasks can be deleted safely
- **Prompt for critical issues** - Tasks, files, functions require user decision
- **Trigger sync on checksums** - Call `project_dependency_sync` when files modified
- **Detect duplicates** - Same entity appearing multiple times
- **Validate foreign keys** - Ensure all relationships intact
- **Log all findings** - Transparency in notes table
- **Prevent corruption** - Catch integrity issues early
- **Support auto-repair** - Fix simple issues automatically
- **Escalate to user** - Complex issues require human judgment
