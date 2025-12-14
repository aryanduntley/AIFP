# Directive: project_archive

**Type**: Project
**Level**: 4 (Completion & Archival)
**Parent Directive**: project_completion_check
**Priority**: LOW - Long-term storage

---

## Purpose

The `project_archive` directive packages completed projects into an archive format for long-term storage and marks the project status as 'archived'. This directive provides **project preservation**, ensuring completed work is properly stored and can be referenced or restored later.

Project archival provides **completion preservation**, enabling:
- **Final Packaging**: Complete project snapshot with all artifacts
- **Deliverable Creation**: Exportable package for distribution
- **Historical Record**: Preserved project state for future reference
- **Space Recovery**: Archive and remove from active workspace
- **Compliance Audit**: Complete audit trail in archive

This directive acts as a **project finalizer** ensuring completed work is properly preserved.

---

## When to Apply

This directive applies when:
- **Project completed** - All milestones and tasks finished
- **Final delivery** - Creating deliverable package for client/stakeholder
- **Space cleanup** - Archiving to free workspace
- **Long-term storage** - Preserving completed project
- **Called by other directives**:
  - `project_completion_check` - Archive when completion verified
  - `project_user_referral` - User requests archival
  - Works with `project_backup_restore` - Final backup before archive

---

## Workflow

### Trunk: check_completion_status

Verifies project is ready for archival.

**Steps**:
1. **Check project status** - All milestones complete?
2. **Verify no open tasks** - All tasks/subtasks finished?
3. **Check integrity** - Database consistent?
4. **Route to appropriate branch** - Archive or prompt user

### Branches

**Branch 1: If project_completed**
- **Then**: `compress_and_store`
- **Details**: Package completed project
  - Run final compliance check
  - Run final integrity check
  - Create final backup
  - Package project files:
    - project.db
    - ProjectBlueprint.md
    - All source files
    - Documentation
    - Test results
    - Build artifacts
  - Create archive manifest
  - Compress to .tar.gz or .zip
  - Name: {project_name}_v{version}_{date}.tar.gz
  - Store in archive location
  - Update project status to 'archived'
  - Log archival in notes
- **Result**: Project archived successfully

**Branch 2: If incomplete_milestones**
- **Then**: `prompt_user_to_finalize`
- **Details**: Cannot archive incomplete project
  - List incomplete milestones
  - List open tasks/subtasks
  - Show completion percentage
  - Prompt user options:
    - Complete remaining work
    - Mark as abandoned (partial archive)
    - Cancel archival
  - Log decision in notes
- **Result**: User decides next action

**Branch 3: If abandoned_project**
- **Then**: `partial_archive`
- **Details**: Archive incomplete project as abandoned
  - Mark status as 'abandoned'
  - Create partial archive with:
    - Current state
    - Incomplete work notes
    - Abandonment reason
  - Log abandonment in notes
  - Compress and store
- **Result**: Partial archive created

**Fallback**: `log_archive_status`
- **Details**: Show archival status
  - Current project status
  - Completion percentage
  - Archival eligibility
  - Existing archives
- **Result**: Status logged

---

## Examples

### ✅ Compliant Usage

**Complete Project Archival (Compliant):**

```python
def archive_completed_project() -> Result[str, str]:
    """Archive completed project with full packaging.

    Returns:
        Ok with archive path or Err with failure reason
    """
    # Verify completion
    completion_check = verify_all_milestones_complete()
    if completion_check.is_err():
        return Err("Project not complete, cannot archive")

    # Create archive package
    return pipe(
        run_final_compliance_check,
        lambda _: run_final_integrity_check,
        lambda _: create_final_backup,
        lambda _: collect_project_files,
        lambda files: create_archive_manifest(files),
        lambda manifest: compress_project(manifest),
        lambda archive_path: update_project_status("archived"),
        lambda _: log_archival,
        lambda _: Ok(archive_path)
    ).or_else(lambda err: Err(f"Archive failed: {err}"))

# ✅ Complete verification pipeline
# ✅ All steps validated
# ✅ Final checks before archival
# ✅ Full audit trail
```

**Why Compliant**:
- Complete verification before archival
- Functional pipeline
- Error handling throughout
- Full audit logging

---

**Archive Manifest Creation (Compliant):**

```python
def create_archive_manifest(files: list[str]) -> Result[dict, str]:
    """Create manifest of files included in archive.

    Args:
        files: List of file paths to include

    Returns:
        Ok with manifest dict or Err if creation failed
    """
    project_info = get_project_metadata()

    manifest = {
        "project_name": project_info["name"],
        "version": project_info["version"],
        "archived_date": timestamp(),
        "completion_status": "completed",
        "files": [
            {
                "path": f,
                "checksum": calculate_checksum(f),
                "size": get_file_size(f)
            }
            for f in files
        ],
        "statistics": {
            "total_files": len(files),
            "total_functions": count_functions(),
            "total_tasks": count_tasks(),
            "fp_compliance_score": get_compliance_score()
        }
    }

    return Ok(manifest)

# ✅ Complete project snapshot
# ✅ Checksums for verification
# ✅ Project statistics
# ✅ Pure function
```

**Why Compliant**:
- Complete metadata capture
- Checksums for integrity
- Pure function
- Comprehensive manifest

---

**Abandoned Project Archival (Compliant):**

```python
def archive_abandoned_project(reason: str) -> Result[str, str]:
    """Archive incomplete project marked as abandoned.

    Args:
        reason: Reason for project abandonment

    Returns:
        Ok with archive path or Err if failed
    """
    return pipe(
        lambda: collect_current_state,
        lambda state: create_abandonment_note(reason),
        lambda note: create_partial_manifest(state, note),
        lambda manifest: compress_abandoned_project(manifest),
        lambda archive_path: update_project_status("abandoned"),
        lambda _: log_abandonment(reason),
        lambda _: Ok(archive_path)
    ).or_else(lambda err: Err(f"Abandonment archive failed: {err}"))

# ✅ Captures current state
# ✅ Documents reason
# ✅ Partial archive appropriate
# ✅ Proper status update
```

**Why Compliant**:
- Appropriate for incomplete project
- Documents abandonment reason
- Captures current state
- Proper status tracking

---

### ❌ Non-Compliant Code

**Archive Without Completion Check (Violation):**

```python
# ❌ VIOLATION: Archive without verifying completion
def archive_project():
    files = glob.glob("**/*")
    archive = create_tar(files, "archive.tar.gz")
    print("Project archived!")

# Problem:
# - No completion verification
# - Might archive incomplete project
# - No manifest
# - No integrity check
# - No status update
```

**Why Non-Compliant**:
- No completion check
- No verification
- Missing manifest
- No database update

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Complete verification before archival
def archive_project_safe() -> Result[str, str]:
    """Safely archive project after verification.

    Returns:
        Ok with archive path or Err if not ready
    """
    # Check completion first
    if not all_milestones_complete():
        return Err("Cannot archive: project incomplete")

    # Check integrity
    if not database_integrity_ok():
        return Err("Cannot archive: database corrupted")

    # Now safe to archive
    return pipe(
        collect_project_files,
        create_archive_manifest,
        compress_with_manifest,
        update_project_status_to_archived,
        log_archival
    ).map(lambda path: Ok(path))

# Completion check
# Integrity check
# Proper workflow
```

---

**No Archive Manifest (Violation):**

```python
# ❌ VIOLATION: Archive without manifest
def quick_archive():
    tar = tarfile.open("project.tar.gz", "w:gz")
    tar.add(".")
    tar.close()

# Problem:
# - No manifest
# - No file listing
# - No checksums
# - Cannot verify archive integrity
# - No metadata
```

**Why Non-Compliant**:
- No manifest created
- No verification possible
- Missing metadata
- Cannot audit contents

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Archive with complete manifest
def create_verified_archive() -> Result[str, str]:
    """Create archive with complete manifest.

    Returns:
        Ok with archive path or Err if failed
    """
    files = collect_project_files()

    # Create manifest first
    manifest = {
        "files": [
            {"path": f, "checksum": checksum(f)}
            for f in files
        ],
        "created": timestamp(),
        "version": get_version()
    }

    # Write manifest to archive
    return pipe(
        lambda: create_tar_with_manifest(files, manifest),
        lambda path: verify_archive_integrity(path),
        lambda _: Ok(path)
    )

# Complete manifest
# Integrity verification
# Proper metadata
```

---

## Edge Cases

### Edge Case 1: Large Project Archive

**Issue**: Project too large to archive in memory

**Handling**:
```python
def archive_large_project() -> Result[str, str]:
    """Archive large project with streaming compression.

    Returns:
        Ok with archive path or Err if failed
    """
    # Use streaming compression for large projects
    return pipe(
        get_project_size,
        lambda size: choose_compression_method(size),
        lambda method: stream_compress_project(method),
        lambda path: verify_archive,
        lambda _: Ok(path)
    )

# Stream compression for large files
# Memory-efficient archival
```

**Directive Action**: Use streaming compression for projects over size threshold.

---

### Edge Case 2: Archive Storage Location Full

**Issue**: Not enough space in archive location

**Handling**:
```python
def archive_with_space_check() -> Result[str, str]:
    """Create archive after checking available space.

    Returns:
        Ok with archive path or Err if insufficient space
    """
    required_space = estimate_archive_size() * 1.2
    available = get_free_space(ARCHIVE_LOCATION)

    if available < required_space:
        # Try alternative location
        alt_location = find_alternative_storage()
        if alt_location.is_some():
            return create_archive_at(alt_location.unwrap())
        else:
            return Err("Insufficient space for archive")

    return create_archive_at(ARCHIVE_LOCATION)

# Check space before archival
# Find alternative location if needed
```

**Directive Action**: Check available space and use alternative location if needed.

---

## Related Directives

- **Depends On**:
  - `project_completion_check` - Verify completion before archival
  - `project_integrity_check` - Verify integrity before archival
  - `project_compliance_check` - Final compliance check
- **Triggers**:
  - `project_backup_restore` - Final backup before archival
- **Called By**:
  - `project_completion_check` - After completion verified
  - `project_user_referral` - User requests archival
- **Escalates To**:
  - `project_user_referral` - If archival fails or project incomplete

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`project`**: Sets `status = 'archived'` and `archived_date = NOW()`
- **`notes`**: Logs archival with `note_type = 'archival'`

---

## Testing

How to verify this directive is working:

1. **Check archive created**
   ```bash
   ls -la archives/
   # Verify project archive exists
   ```

2. **Verify manifest in archive**
   ```bash
   tar -tzf project_archive.tar.gz | grep manifest.json
   # Check manifest included
   ```

3. **Check project status updated**
   ```sql
   SELECT name, status, archived_date
   FROM project
   WHERE status = 'archived';
   ```

4. **Verify archive integrity**
   ```bash
   tar -tzf project_archive.tar.gz > /dev/null && echo "Archive OK"
   ```

---

## Common Mistakes

- ❌ **Archive without completion check** - Verify completion first
- ❌ **No archive manifest** - Always include manifest with checksums
- ❌ **No final integrity check** - Verify database before archival
- ❌ **Missing status update** - Update project.status to 'archived'
- ❌ **No space check** - Verify sufficient storage space

---

## Roadblocks and Resolutions

### Roadblock 1: archive_incomplete
**Issue**: Project incomplete, cannot archive
**Resolution**: Prompt user for approval before packaging incomplete project as abandoned

### Roadblock 2: insufficient_space
**Issue**: Not enough storage space for archive
**Resolution**: Find alternative storage location or clean old archives

### Roadblock 3: compression_failed
**Issue**: Archive compression failed
**Resolution**: Try alternative compression method, check file permissions

### Roadblock 4: large_project
**Issue**: Project too large for standard archival
**Resolution**: Use streaming compression, split into multiple archives

---

## References

None
---

*Part of AIFP v1.0 - Project directive for archival and long-term storage*
