# Directive: project_backup_restore

**Type**: Project
**Level**: 4 (Compliance & Recovery)
**Parent Directive**: project_integrity_check
**Priority**: MEDIUM - Project state protection

---

## Purpose

The `project_backup_restore` directive manages periodic backups of `project.db` and associated files, and restores them on demand or after failure detection. This directive provides **project state protection**, ensuring you can recover from corruption, user error, or system failure.

Backup and restore provides **state recovery**, enabling:
- **Automatic Backups**: Periodic snapshots of project state
- **On-Demand Backups**: Manual backup before risky operations
- **Corruption Recovery**: Restore from backup when integrity check fails
- **Version History**: Track project evolution through backups
- **Safety Net**: Protection against destructive changes

This directive acts as a **safety guardian** for your project data.

---

## When to Apply

This directive applies when:
- **Scheduled backup time** - Periodic automatic backups
- **Before risky operations** - Manual backup before major changes
- **Integrity check failure** - Restore from backup when corruption detected
- **User request** - Manual restore to previous state
- **Called by other directives**:
  - `project_integrity_check` - Triggers restore when corruption found
  - `project_init` - Creates initial backup
  - `project_evolution` - Backup before major project changes
  - Works with `git_sync_state` - Coordinate with Git backups

---

## Workflow

### Trunk: determine_operation

Determines whether to perform backup or restore operation.

**Steps**:
1. **Check operation type** - Backup or restore?
2. **Validate parameters** - Paths and permissions correct?
3. **Route to appropriate branch** - Backup or restore workflow

### Branches

**Branch 1: If scheduled_backup_time**
- **Then**: `execute_backup`
- **Details**: Periodic automatic backup
  - Check time since last backup
  - Backup frequency from preferences
  - Copy project.db to backups folder
  - Name: ProjectDB_YYYY-MM-DD_HH-MM.db
  - Copy ProjectBlueprint.md
  - Record backup in notes
  - Clean up old backups (keep last N)
- **Result**: Backup created successfully

**Branch 2: If manual_backup_requested**
- **Then**: `execute_backup`
- **Details**: User-requested backup
  - Same as scheduled backup
  - Optional custom backup name
  - Mark as manual in notes
  - Immediate execution
- **Result**: Manual backup created

**Branch 3: If restore_requested**
- **Then**: `load_backup`
- **Details**: Restore from backup
  - List available backups
  - User selects backup to restore
  - Backup current state first
  - Copy selected backup to project.db
  - Restore ProjectBlueprint.md
  - Verify integrity after restore
  - Record restoration in notes
- **Result**: Project restored to backup state

**Branch 4: If integrity_check_failed**
- **Then**: `auto_restore_latest`
- **Details**: Automatic restore on corruption
  - Triggered by project_integrity_check
  - Find most recent valid backup
  - Backup corrupted state for analysis
  - Restore from latest backup
  - Run integrity check on restored state
  - Alert user to data loss (if any)
- **Result**: Project restored from corruption

**Fallback**: `log_backup_status`
- **Details**: No operation needed
  - Log current backup status
  - Show backup history
  - Show next scheduled backup time
- **Result**: Status logged

---

## Examples

### ✅ Compliant Usage

**Scheduled Backup (Compliant):**

```python
# Automatic backup every 24 hours
def scheduled_backup():
    """Perform scheduled project backup.

    Returns:
        Result indicating backup success or failure
    """
    backup_path = f".aifp-project/backups/ProjectDB_{timestamp()}.db"

    # Copy database
    copy_result = copy_file(
        src="project.db",
        dest=backup_path
    )

    if copy_result.is_ok():
        # Also backup blueprint
        copy_blueprint(backup_path)
        log_backup(backup_path, "scheduled")
        return Ok(f"Backup created: {backup_path}")
    else:
        return Err("Backup failed")

# ✅ Pure backup operation
# ✅ Side effects isolated to file system
# ✅ Error handling via Result type
```

**Why Compliant**:
- Pure function with clear purpose
- Side effects isolated to file operations
- Result type for error handling
- Logged for audit trail

---

**Manual Backup Before Risky Operation (Compliant):**

```python
# Backup before major project evolution
def backup_before_evolution():
    """Create backup before project pivot.

    Returns:
        Result with backup path or error
    """
    backup_name = f"ProjectDB_pre_pivot_{timestamp()}.db"
    backup_path = f".aifp-project/backups/{backup_name}"

    return pipe(
        validate_source("project.db"),
        lambda _: copy_database(backup_path),
        lambda _: copy_blueprint(backup_path),
        lambda _: log_backup(backup_path, "manual"),
        lambda _: Ok(backup_path)
    ).or_else(lambda err: Err(f"Backup failed: {err}"))

# ✅ Chained operations
# ✅ Error handling throughout
# ✅ Clear audit trail
```

**Why Compliant**:
- Functional pipeline
- Each step validated
- Full error handling
- Audit logging

---

**Restore from Backup (Compliant):**

```python
# Restore project from backup
def restore_from_backup(backup_path: str) -> Result[str, str]:
    """Restore project from specified backup.

    Args:
        backup_path: Path to backup file to restore

    Returns:
        Ok with success message or Err with failure reason
    """
    # Backup current state first
    emergency_backup = backup_current_state()

    if emergency_backup.is_err():
        return Err("Cannot backup current state before restore")

    # Restore from backup
    restore_result = pipe(
        validate_backup(backup_path),
        lambda _: copy_file(backup_path, "project.db"),
        lambda _: restore_blueprint(backup_path),
        lambda _: verify_integrity(),
        lambda _: log_restoration(backup_path)
    )

    return restore_result.or_else(
        lambda err: rollback_to_emergency_backup(emergency_backup)
    )

# ✅ Safety-first approach
# ✅ Backup before restore
# ✅ Integrity verification
# ✅ Rollback on failure
```

**Why Compliant**:
- Safety backup before restore
- Validation at each step
- Integrity check after restore
- Rollback capability

---

### ❌ Non-Compliant Code

**No Backup Before Risky Operation (Violation):**

```python
# ❌ VIOLATION: No backup before destructive operation
def refactor_database():
    # Directly modifying database without backup
    execute_sql("ALTER TABLE tasks DROP COLUMN old_field")
    execute_sql("UPDATE tasks SET status = 'new_status'")

# Problem:
# - No backup before destructive changes
# - Cannot recover if operation fails
# - Data loss risk
# - No safety net
```

**Why Non-Compliant**:
- No backup created
- Destructive operation unprotected
- Cannot rollback
- Violates safety principle

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Backup before destructive operation
def refactor_database_safe() -> Result[None, str]:
    """Safely refactor database with backup.

    Returns:
        Ok if refactor successful, Err if failed
    """
    # Create backup first
    backup_result = create_backup("pre_refactor")

    if backup_result.is_err():
        return Err("Cannot create backup, aborting refactor")

    # Now safe to refactor
    refactor_result = pipe(
        lambda: execute_sql("ALTER TABLE tasks DROP COLUMN old_field"),
        lambda _: execute_sql("UPDATE tasks SET status = 'new_status'"),
        lambda _: verify_integrity()
    )

    # Restore if refactor failed
    if refactor_result.is_err():
        restore_from_backup(backup_result.unwrap())
        return Err("Refactor failed, restored from backup")

    return Ok(None)

# Safety backup created
# Rollback on failure
```

---

**Corrupted Restore Without Verification (Violation):**

```python
# ❌ VIOLATION: Restore without integrity check
def restore_backup(backup_path: str):
    shutil.copy(backup_path, "project.db")
    print("Restored!")

# Problem:
# - No integrity check after restore
# - Backup might be corrupted
# - No verification of success
# - Could restore bad data
```

**Why Non-Compliant**:
- No integrity verification
- No validation of backup
- Blind restore
- Could propagate corruption

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Verified restore
def restore_backup_safe(backup_path: str) -> Result[None, str]:
    """Safely restore from backup with verification.

    Args:
        backup_path: Path to backup file

    Returns:
        Ok if restore successful and verified, Err otherwise
    """
    return pipe(
        validate_backup(backup_path),
        lambda _: backup_current_state(),
        lambda emergency: copy_file(backup_path, "project.db"),
        lambda _: verify_database_integrity(),
        lambda _: log_restoration(backup_path),
        lambda _: Ok(None)
    ).or_else(lambda err: Err(f"Restore failed: {err}"))

# Backup validation
# Emergency backup
# Integrity check
# Error handling
```

---

## Edge Cases

### Edge Case 1: Backup During Active Write

**Issue**: Database being modified during backup

**Handling**:
```python
def safe_backup() -> Result[str, str]:
    """Create backup with database lock.

    Returns:
        Ok with backup path or Err if failed
    """
    with database_lock():
        backup_path = create_timestamped_path()
        return copy_database(backup_path)

# Use database lock to ensure consistency
```

**Directive Action**: Acquire lock before backup to ensure consistent state.

---

### Edge Case 2: Backup Storage Full

**Issue**: Not enough space for backup

**Handling**:
```python
def backup_with_space_check() -> Result[str, str]:
    """Create backup after checking available space.

    Returns:
        Ok with backup path or Err if insufficient space
    """
    required_space = get_db_size() * 1.1  # 10% buffer
    available_space = get_free_space(".aifp-project/backups/")

    if available_space < required_space:
        # Clean old backups
        cleanup_result = remove_old_backups()
        if cleanup_result.is_err():
            return Err("Insufficient space for backup")

    return create_backup()

# Check space before backup
# Clean old backups if needed
```

**Directive Action**: Check available space and clean old backups if necessary.

---

### Edge Case 3: Multiple Restore Requests

**Issue**: User requests restore while another is in progress

**Handling**:
```python
restore_in_progress = False

def restore_with_lock(backup_path: str) -> Result[None, str]:
    """Restore from backup with operation lock.

    Args:
        backup_path: Path to backup file

    Returns:
        Ok if restore successful, Err if failed or locked
    """
    global restore_in_progress

    if restore_in_progress:
        return Err("Restore already in progress")

    restore_in_progress = True
    try:
        result = perform_restore(backup_path)
        return result
    finally:
        restore_in_progress = False

# Lock to prevent concurrent restores
```

**Directive Action**: Use operation lock to prevent concurrent restore operations.

---

## Related Directives

- **Depends On**:
  - `project_integrity_check` - Triggers restore when corruption detected
- **Triggers**:
  - `project_integrity_check` - After restore, verify integrity
- **Called By**:
  - `project_init` - Creates initial backup
  - `project_evolution` - Backup before major changes
  - `project_integrity_check` - Restore on corruption
- **Escalates To**:
  - `project_user_referral` - If restore fails

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`notes`**: Logs backup and restore operations with `note_type = 'backup'` or `'restore'`
- **`project`**: Updates `last_backup_date` field

---

## Testing

How to verify this directive is working:

1. **Create manual backup**
   ```bash
   # Verify backup created in .aifp-project/backups/
   ls -la .aifp-project/backups/
   ```

2. **Check backup integrity**
   ```bash
   sqlite3 .aifp-project/backups/ProjectDB_*.db "PRAGMA integrity_check;"
   ```

3. **Verify scheduled backups**
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

4. **Test restore**
   ```bash
   # Restore from backup and verify integrity
   # Check that project.db is restored correctly
   ```

---

## Common Mistakes

- ❌ **No backup before risky operations** - Always backup first
- ❌ **No integrity check after restore** - Verify restored data
- ❌ **Keeping too many backups** - Clean old backups to save space
- ❌ **No backup verification** - Check backup is valid before relying on it
- ❌ **Concurrent backup/restore** - Use locks to prevent conflicts

---

## Roadblocks and Resolutions

### Roadblock 1: backup_failure
**Issue**: Cannot create backup due to file system error
**Resolution**: Prompt user to retry or check file permissions, try alternative backup location

### Roadblock 2: insufficient_space
**Issue**: Not enough disk space for backup
**Resolution**: Clean old backups automatically, prompt user if still insufficient space

### Roadblock 3: restore_corruption
**Issue**: Restored backup is corrupted
**Resolution**: Rollback to emergency backup, try alternative backup, prompt user

### Roadblock 4: backup_during_write
**Issue**: Database being modified during backup
**Resolution**: Acquire database lock before backup to ensure consistency

---

## References

None
---

*Part of AIFP v1.0 - Project directive for backup and restore operations*
