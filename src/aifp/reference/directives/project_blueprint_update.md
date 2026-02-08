# Directive: project_blueprint_update

**Type**: Project
**Level**: 2 (High-Level Coordination)
**Parent Directive**: project_evolution
**Priority**: HIGH - Standard helper for ProjectBlueprint.md modifications

---

## Purpose

The `project_blueprint_update` directive provides the **standard interface** for updating specific sections of `ProjectBlueprint.md` with new content. This directive serves as the **atomic blueprint modifier**, ensuring that all blueprint updates follow a consistent, safe pattern with backups and validation.

Key responsibilities:
- **Update specific sections** - Modify Section 1-7 content with surgical precision
- **Backup before modification** - Preserve previous state in `.aifp-project/backups/`
- **Replace section content** - Update section while preserving structure
- **Increment version** (optional) - Update `project.version` in database
- **Add evolution history** (optional) - Log change in Section 5
- **Update checksum** - Sync `project.blueprint_checksum` in database
- **Atomic updates** - All-or-nothing with rollback on failure

This is the **atomic blueprint updater** - called by `project_evolution` and other directives when blueprint changes are needed.

---

## When to Apply

This directive applies when:
- **Section-specific updates** - Modifying a single blueprint section
- **Evolution changes** - Called by `project_evolution` to update blueprint
- **Metadata sync** - Ensuring blueprint reflects database state
- **Manual corrections** - User requests specific blueprint edits
- **Called by other directives**:
  - `project_evolution` - Updates sections for architecture, goals, themes, flows, completion path changes
  - `project_theme_flow_mapping` - Updates Section 3 when themes/flows change
  - `project_init` - Creates initial blueprint
  - `project_add_path` - Updates Section 4 when completion path changes

---

## Workflow

### Trunk: validate_parameters

Ensures required parameters are present before proceeding.

**Steps**:
1. **Validate section_number** - Must be 1-7
2. **Validate new_content** - Must be non-empty string
3. **Validate file exists** - `ProjectBlueprint.md` must exist
4. **Read current blueprint** - Load existing content

### Branches

**Branch 1: If parameters_valid**
- **Then**: `read_current_blueprint`
- **Details**: Load existing blueprint content
  - Call `project_blueprint_read` helper
  - Parse all sections
  - Validate structure
- **Result**: Current blueprint loaded and parsed

**Branch 2: If blueprint_read**
- **Then**: `backup_current_blueprint`
- **Details**: Create backup before modification
  - Backup path: `.aifp-project/backups/ProjectBlueprint.md.v{version}`
  - Include timestamp: `ProjectBlueprint.md.v{version}_{YYYYMMDD_HHMMSS}`
  - Verify backup created successfully
- **Result**: Backup created, safe to proceed

**Branch 3: If backup_complete**
- **Then**: `replace_section_content`
- **Details**: Update specified section
  - Locate section by number (## 1., ## 2., etc.)
  - Replace content between section header and next section
  - Preserve markdown structure
  - Maintain heading levels
- **Example**:
  ```markdown
  ## 2. Technical Blueprint
  [OLD CONTENT]
  ---
  ## 3. Project Themes & Flows
  ```
  Becomes:
  ```markdown
  ## 2. Technical Blueprint
  [NEW CONTENT]
  ---
  ## 3. Project Themes & Flows
  ```
- **Result**: Section content replaced

**Branch 4: If increment_version_requested**
- **Then**: `update_version_and_date`
- **Details**: Increment version in database and blueprint
  - Increment `project.version` in database:
    **Use helper functions** for database operations. Query available helpers for the appropriate database.
  - Update **Version** field in Section 1:
    ```markdown
    **Version**: 1.1
    ```
  - Update **Last Updated** field:
    ```markdown
    **Last Updated**: 2025-10-27
    ```
- **Result**: Version incremented, dates updated

**Branch 5: If version_incremented**
- **Then**: `add_evolution_history_entry`
- **Details**: Log change in Section 5
  - Append to Section 5: Evolution History
  - Format:
    ```markdown
    ### Version X - YYYY-MM-DD
    - **Change**: [description of what changed]
    - **Rationale**: [why this change was made]
    ```
  - Show new version number
  - Show change date
- **Result**: Evolution history updated with audit trail

**Branch 6: If section_replaced**
- **Then**: `write_updated_blueprint`
- **Details**: Write modified content back to file
  - Path: `.aifp-project/ProjectBlueprint.md`
  - Atomic write (write to temp, then rename)
  - Verify write succeeded
- **Result**: Blueprint file updated on disk

**Branch 7: If write_complete**
- **Then**: `update_blueprint_checksum`
- **Details**: Sync checksum in database
  - Calculate SHA-256 checksum of updated file
  - Update database:
    **Use helper functions** for database operations. Query available helpers for the appropriate database.
  - Checksum enables blueprint/DB sync detection
- **Result**: Database checksum matches file

**Branch 8: If update_complete**
- **Then**: `return_success`
- **Details**: Report success to caller
  - Show new version number (if incremented)
  - Show updated section number
  - Confirm backup created
- **Result**: Caller notified of successful update

**Fallback**: `prompt_user`
- Present issue and ask for clarification
- Common issues: Section not found, backup failed, write failed

### Error Handling

**on_failure**: `restore_from_backup`
**prompt_user**: true
- If any step fails, restore from backup
- Rollback database changes (version, checksum)
- Prompt user to resolve issue manually

---

## Examples

### Example 1: Update Section 2 (Architecture Change)

**Called By**: `project_evolution` directive

**Parameters**:
- `section_number`: 2
- `new_content`:
  ```markdown
  ### Language & Runtime
  - **Primary Language**: Rust 1.75+
  - **Runtime/Framework**: Tokio async runtime
  - **Build Tool**: Cargo
  ```
- `increment_version`: true
- `change_description`: "Migrated from Python to Rust"
- `rationale`: "Performance improvements for matrix operations"

**AI Execution**:
1. Validates parameters: ✓ Valid
2. Reads current blueprint via `project_blueprint_read`
3. Creates backup:
   - Path: `.aifp-project/backups/ProjectBlueprint.md.v1_20251027_143022`
4. Replaces Section 2 content
5. Increments version:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
6. Updates Section 1 metadata:
   ```markdown
   **Version**: 2
   **Last Updated**: 2025-10-27
   ```
7. Adds evolution history to Section 5:
   ```markdown
   ### Version 2 - 2025-10-27
   - **Change**: Migrated from Python to Rust
   - **Rationale**: Performance improvements for matrix operations
   ```
8. Writes updated blueprint to disk
9. Updates checksum:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
10. Returns success: "Blueprint updated: Section 2. Version: 1 → 2."

### Example 2: Update Section 3 (Themes/Flows)

**Called By**: `project_theme_flow_mapping` directive

**Parameters**:
- `section_number`: 3
- `new_content`:
  ```markdown
  ### Themes

  1. **Authentication**
     - Purpose: User identity verification
     - Files: src/aifp/auth/

  2. **Authorization**
     - Purpose: Role-based access control
     - Files: src/aifp/permissions/
  ```
- `increment_version`: true
- `change_description`: "Split Authentication into Auth and Authorization themes"
- `rationale`: "Separation of concerns for modularity"

**AI Execution**:
1. Validates parameters: ✓ Valid
2. Reads current blueprint
3. Creates backup
4. Replaces Section 3 content
5. Increments version to 4
6. Updates Section 1 metadata
7. Adds evolution history
8. Writes updated blueprint
9. Updates checksum
10. Returns success

### Example 3: Update Section 4 (Completion Path)

**Called By**: `project_evolution` directive

**Parameters**:
- `section_number`: 4
- `new_content`:
  ```markdown
  ### Stage 3: Performance Optimization (Weeks 5-6)

  **Status**: pending

  **Key Milestones**:
  - Profile CPU and memory usage
  - Optimize hot paths identified in profiling
  - Benchmark improvements (target: 2x speedup)
  ```
- `increment_version`: true
- `change_description`: "Added Performance Optimization stage"
- `rationale`: "Profiling revealed bottlenecks requiring dedicated optimization stage"

**AI Execution**:
1. Validates parameters: ✓ Valid
2. Reads current blueprint
3. Creates backup
4. Replaces Section 4 content (adds new stage)
5. Increments version to 5
6. Updates Section 1 metadata
7. Adds evolution history
8. Writes updated blueprint
9. Updates checksum
10. Returns success

### Example 4: Update Section 5 (Evolution History Only)

**Called By**: Manual logging (no version increment)

**Parameters**:
- `section_number`: 5
- `new_content`:
  ```markdown
  ### Version 6 - 2025-10-27
  - **Change**: Fixed typo in project description
  - **Rationale**: Documentation accuracy
  ```
- `increment_version`: false (already incremented by another operation)

**AI Execution**:
1. Validates parameters: ✓ Valid
2. Reads current blueprint
3. Creates backup
4. Appends to Section 5 (Evolution History)
5. NO version increment (already done)
6. Writes updated blueprint
7. Updates checksum
8. Returns success

### Example 5: Section Not Found Error

**Parameters**:
- `section_number`: 8 (invalid)

**AI Execution**:
1. Validates parameters: ✗ Invalid (section 8 doesn't exist)
2. Prompts user: "Section 8 not found. Valid sections: 1-7. Please specify valid section number."
3. User corrects: "Section 2"
4. Retries with corrected parameter

### Example 6: Backup Failed Error

**Parameters**:
- `section_number`: 2
- `new_content`: [valid content]

**AI Execution**:
1. Validates parameters: ✓ Valid
2. Reads current blueprint
3. Attempts backup: ✗ Failed (permission error)
4. **Aborts update** (on_failure: restore_from_backup)
5. Prompts user: "Backup failed: Permission denied. Please check file permissions for .aifp-project/backups/ directory."
6. User resolves permissions
7. Retries operation

### Example 7: Write Failed Error with Rollback

**Parameters**:
- `section_number`: 2
- `new_content`: [valid content]
- `increment_version`: true

**AI Execution**:
1. Validates parameters: ✓ Valid
2. Reads current blueprint
3. Creates backup successfully
4. Replaces section content
5. Increments version in DB: ✓ Success
6. Attempts to write file: ✗ Failed (disk full)
7. **Triggers rollback**:
   - Restore blueprint from backup
   - Rollback version increment:
     **Use helper functions** for database operations. Query available helpers for the appropriate database.
8. Prompts user: "Blueprint update failed: Disk full. Changes rolled back. Please free disk space and retry."

---

## Integration with Other Directives

### Called By:
- `project_evolution` - Primary caller for all blueprint updates
- `project_theme_flow_mapping` - Updates Section 3
- `project_add_path` - Updates Section 4
- `project_init` - Creates initial blueprint

### Calls:
- `project_blueprint_read` - Reads current blueprint
- `project_backup_restore` - Creates backups (implicitly)

---

## Database Updates

### Tables Modified:

**project.db**:
**Use helper functions** for database operations. Query available helpers for the appropriate database.

**Filesystem**:
```bash
# Create backup
cp .aifp-project/ProjectBlueprint.md \
   .aifp-project/backups/ProjectBlueprint.md.v{version}_{timestamp}

# Write updated blueprint (atomic)
mv .aifp-project/ProjectBlueprint.md.tmp \
   .aifp-project/ProjectBlueprint.md
```

---

## Roadblocks and Resolutions

### Roadblock 1: section_not_found
**Issue**: Specified section number doesn't exist (not 1-7)
**Resolution**: Warn user, suggest valid sections (1-7), or append new section if appropriate

### Roadblock 2: backup_failed
**Issue**: Cannot create backup (permissions, disk full, etc.)
**Resolution**: **Abort update**, prompt user to resolve issue, do NOT proceed without backup

### Roadblock 3: write_failed
**Issue**: Cannot write updated blueprint to disk
**Resolution**: Restore from backup, rollback database changes, prompt user

### Roadblock 4: version_conflict
**Issue**: Version in blueprint doesn't match database version
**Resolution**: Prompt user to resolve manually, use database version as source of truth

### Roadblock 5: blueprint_corrupted
**Issue**: Blueprint file is malformed or missing sections
**Resolution**: Attempt to parse sections individually, use database fallback for missing sections

### Roadblock 6: checksum_mismatch
**Issue**: Calculated checksum doesn't match expected value
**Resolution**: Update checksum in database, warn user about potential desync

---

## Blueprint Section Numbers

| Section | Title | Typical Content |
|---------|-------|-----------------|
| 1 | Project Overview | Idea, goals, success criteria |
| 2 | Technical Blueprint | Language, runtime, architecture, infrastructure |
| 3 | Project Themes & Flows | Organizational structure, themes, flows |
| 4 | Completion Path | Stages, milestones, roadmap |
| 5 | Evolution History | Version history, changes, rationale |
| 6 | User Settings System | User preferences, tracking settings (optional) |
| 7 | User Custom Directives | User-defined automation (optional) |

---

## Update Pattern

```
1. Validate parameters
   ↓
2. Read current blueprint (project_blueprint_read)
   ↓
3. Create backup (.aifp-project/backups/)
   ↓
4. Replace section content
   ↓
5. [Optional] Increment version in DB
   ↓
6. [Optional] Update Section 1 metadata (Version, Last Updated)
   ↓
7. [Optional] Add evolution history to Section 5
   ↓
8. Write updated blueprint (atomic)
   ↓
9. Update checksum in DB
   ↓
10. Add 'evolution' note via add_note (note_type='evolution', directive_name='project_blueprint_update')
    describing what was changed and why. Do NOT set reference_table — ProjectBlueprint.md is a file, not a DB table.
   ↓
11. Return success
```

---

## Intent Keywords

- "update blueprint"
- "modify blueprint"
- "change blueprint section"
- "edit blueprint"
- "sync blueprint"

**Confidence Threshold**: 0.7

---

## Related Directives

- `project_evolution` - Primary caller for blueprint updates
- `project_blueprint_read` - Reads current blueprint
- `project_backup_restore` - Creates backups
- `project_theme_flow_mapping` - Updates Section 3
- `project_add_path` - Updates Section 4
- `project_init` - Creates initial blueprint

---

## Parameters

**Required**:
- `section_number` (int, 1-7) - Which section to update
- `new_content` (str) - New content for the section

**Optional**:
- `increment_version` (bool, default: false) - Whether to increment project.version
- `change_description` (str) - Description of change for evolution history
- `rationale` (str) - Rationale for change (evolution history)

**Example Call** (from `project_evolution`):
```python
project_blueprint_update(
    section_number=2,
    new_content="### Language & Runtime\n- **Primary Language**: Rust 1.75+\n...",
    increment_version=True,
    change_description="Migrated from Python to Rust",
    rationale="Performance improvements for matrix operations"
)
```

---

## Atomic Update Guarantee

This directive guarantees **atomicity** through:

1. **Backup before modification** - Original state preserved
2. **Database transaction** - Version and checksum updated together
3. **Atomic file write** - Write to temp file, then rename
4. **Rollback on failure** - Restore backup and rollback DB on any error
5. **Validation gates** - Multiple validation steps prevent partial updates

If ANY step fails:
- Blueprint restored from backup
- Database changes rolled back
- User notified of exact failure point

---

## Notes

- **Always backup before modification** - Non-negotiable safety requirement
- **Atomic writes** - Use temp file + rename for filesystem atomicity
- **Checksum tracking** - Enables blueprint/DB sync detection
- **Version increments optional** - Caller decides if version should increment
- **Evolution history append-only** - Never delete history entries
- **Rollback on any failure** - All-or-nothing updates
- **Section numbers fixed** - Valid range: 1-7
- **Evolution note mandatory** - After updating any blueprint section, add an 'evolution' note via add_note (note_type='evolution', directive_name='project_blueprint_update') describing what was changed and why. Do NOT set reference_table — ProjectBlueprint.md is a file, not a database table.
