# Task: Directive Review & Cleanup for Helper Function Consistency

**Date Created**: 2025-12-06
**Status**: ⏳ Pending
**Priority**: High
**Blocking**: Database import, directive implementation

---

## Overview

Helper function registry is now complete (349 helpers across 12 JSON files). All directives must be reviewed and updated for consistency with the new helper function system.

**Key Decision**: Helper-directive relationships are maintained in **helper registry files** (not directive files). The database import script will read `used_by_directives` fields from helper registries to populate the `directive_helpers` table.

---

## Helper Function Completion Summary

**Status**: ✅ **COMPLETE** (2025-12-06)
- **Total Helpers**: 349 documented helpers
- **Registry Files**: 12 JSON files
- **Databases Covered**: 4 (aifp_core.db, user_preferences.db, user_directives.db, project.db)
- **Source of Truth**: `docs/helpers/registry/*.json`

### Key Changes to Helper Functions

1. **Consolidations**:
   - `create_project_directory`, `initialize_project_db`, `initialize_user_preferences_db` → **`initialize_aifp_project()`**

2. **Removed (AI Directive-Driven)**:
   - `create_project_blueprint` - AI creates via directives using Write tool
   - `read_project_blueprint` - AI uses Read tool directly
   - `parse_directive_file` - AI handles via `user_directive_parse` directive (NLP)
   - `validate_user_directive` - AI handles via `user_directive_validate` directive (interactive Q&A)
   - `scan_existing_files` - AI uses Glob/Grep/Read tools (superior pattern recognition)

3. **Added**:
   - `initialize_aifp_project()` - Unified initialization with OOP detection
   - `validate_initialization()` - Post-init validation orchestrator
   - 8 orchestrators for MCP and project operations

4. **OOP Handling Policy**:
   - **AIFP is FP-only** (documented in `docs/aifp-oop-policy.md`)
   - `initialize_aifp_project()` detects OOP and rejects per policy
   - No gradual migration - firm rejection for large OOP projects

5. **AI vs Code Decision Framework**:
   - **AI handles**: NLP, semantic validation, file operations, flexible scanning, interactive workflows
   - **Code handles**: Deterministic operations, structured data CRUD, performance-critical tasks, state management
   - See `docs/helpers/registry/helper-registry-guide.md` for full framework

---

## Database-Driven Helper-Directive Relationships

### ✅ Available Helper Functions

Directives should **NOT** hardcode helper function lists. Instead, AI queries the database at runtime:

```python
# Get helpers for a directive (AI calls this when executing a directive)
get_helpers_for_directive(directive_id, include_helpers_data=true)
# Returns: directive_helpers data + full helper_functions data

# Get directives that use a helper
get_directives_for_helper(helper_function_id, include_directives_data=true)
# Returns: directive_helpers data + full directives data
```

**Location**: `docs/helpers/registry/helpers_registry_core.json`
**Database Table**: `directive_helpers` (junction table in aifp_core.db)

### How Relationships Are Maintained

**Source of Truth**: Helper registry JSON files (`used_by_directives` field)

Each helper in the registry includes:
```json
{
  "name": "initialize_aifp_project",
  "used_by_directives": ["project_init"],
  "execution_context": "Initialize project structure and databases",
  "sequence_order": 1,
  "is_required": true
}
```

**Database Import Script** reads helper registries and populates `directive_helpers` table automatically.

### Benefits of This Approach

- ✅ Helper functions are source of truth (they're more stable than directives)
- ✅ No duplicate helper lists in directive files
- ✅ Easier to maintain (update once in helper registry)
- ✅ AI queries relationships dynamically at runtime
- ✅ Directives remain clean and focused on workflow logic

---

## Issues Found in Directive JSON Files

### Issue 1: Hardcoded Helper References in Workflow Branches

**File**: `docs/directives-json/directives-project.json`

**Problem**: Workflow branches contain `"helper"` and `"helper_*"` fields.

**Example 1**:
```json
{
  "if": "structure_created",
  "then": "generate_project_blueprint",
  "details": {
    "helper": "create_project_blueprint",  // ❌ REMOVE
    "module": "aifp.scripts.init_aifp_project",
    "parameters": {...},
    "template": "ProjectBlueprint_template.md",
    "output": ".aifp-project/ProjectBlueprint.md"
  }
}
```

**Issues**:
- ❌ `create_project_blueprint` does NOT exist (AI directive-driven, not a helper)
- ❌ Hardcoded helper reference must be removed
- ❌ References standalone script that may not exist

**Example 2**:
```json
{
  "if": "blueprint_generated",
  "then": "initialize_databases",
  "details": {
    "helper_project_db": "initialize_project_db",  // ❌ REMOVE
    "helper_prefs_db": "initialize_user_preferences_db",  // ❌ REMOVE
    "module": "aifp.scripts.init_aifp_project",
    "databases": ["project.db", "user_preferences.db"],
    "schemas": ["project_db_schema.sql", "user_preferences_schema.sql"]
  }
}
```

**Issues**:
- ❌ `helper_project_db` and `helper_prefs_db` - non-standard fields, must be removed
- ❌ These helpers were consolidated → `initialize_aifp_project()`
- ❌ All helper references must be removed from directive files

### Issue 2: References to Non-Existent or Consolidated Helpers

Many directives may reference helpers that:
1. Were removed (AI directive-driven)
2. Were consolidated into unified functions
3. Were renamed or restructured

**Action**: Remove ALL helper references from directive JSON files.

### Issue 3: Directive Markdown Files with Hardcoded Helper Lists

**Location**: `src/aifp/reference/directives/*.md`

Some directive markdown files contain hardcoded helper lists that must be removed.

---

## Required Actions

### 1. ✅ Remove ALL Helper References from Directive JSON Files

**Affected Files**:
- `docs/directives-json/directives-project.json`
- `docs/directives-json/directives-fp-core.json`
- `docs/directives-json/directives-fp-aux.json`
- `docs/directives-json/directives-user-system.json`
- `docs/directives-json/directives-user-pref.json`
- `docs/directives-json/directives-git.json`

**Action**:
- Remove ALL `"helper"` fields from workflow branches
- Remove ALL `"helper_*"` variant fields (e.g., `helper_project_db`, `helper_prefs_db`)
- Remove `"module"` references to standalone scripts (if obsolete)
- Clean up `"note"` fields that reference removed helpers

**Method**: Python script (see Script Requirements below)

**Rationale**: Helper-directive relationships are maintained in helper registry files, not directive files.

### 2. ✅ Update Helper Registry JSON Files with Directive References

**For each helper** in the 12 registry JSON files, ensure:
- `used_by_directives` field lists all directives that use this helper
- Field includes directive names (not IDs, since directives aren't imported yet)
- Update any helpers with incomplete or missing `used_by_directives` data

**Example** (from `helpers_registry_project_core.json`):
```json
{
  "name": "initialize_aifp_project",
  "used_by_directives": ["project_init"]
}
```

**Note**: The database import script will resolve directive names to IDs when building the `directive_helpers` table.

### 3. ✅ Update aifp_system_prompt.txt

**Add guidance** about database-driven helper-directive relationships:

```
When executing a directive, use get_helpers_for_directive(directive_id, include_helpers_data=true)
to retrieve all associated helper functions from the database. Do not rely on hardcoded helper
references in directive files.
```

### 4. ✅ Remove Hardcoded Helper Lists from Directive Markdown Files

**Location**: `src/aifp/reference/directives/*.md`

**Action**: Remove sections like:
```markdown
**Referenced Helper Functions:**
- `scan_existing_files(project_root)` - Returns structure map
- `infer_architecture(project_root)` - Detects architectural style
```

**Replace with**:
```markdown
## Helper Functions

This directive's helper functions are maintained in the helper registry.
At runtime, use:
```python
get_helpers_for_directive(directive_id, include_helpers_data=true)
```
to retrieve all associated helpers.
```

### 5. ✅ Create Database Import Script

**Script**: Reads helper registries and populates `directive_helpers` table.

**Logic**:
1. Import all directives to `directives` table (get directive IDs)
2. Import all helpers to `helper_functions` table (get helper function IDs)
3. For each helper, read `used_by_directives` field
4. For each directive name in `used_by_directives`:
   - Look up directive_id from directives table
   - Insert into `directive_helpers` (directive_id, helper_function_id, execution_context, sequence_order, is_required)

**Note**: This approach means helper registries are the single source of truth for relationships.

---

## Script Requirements

### Python Script: `remove_helper_refs_from_directives.py`

**Purpose**: Remove ALL helper references from workflow branches in directive JSON files

**Requirements**:
1. Parse each directive JSON file
2. Navigate to all objects recursively
3. Remove any keys matching:
   - `"helper"` (exact match)
   - `"helper_*"` (any variant: helper_project_db, helper_prefs_db, etc.)
   - Optionally: `"module"` if it references `aifp.scripts.*`
4. Preserve all other fields
5. Write back to JSON with proper formatting (2-space indent)
6. Create backup before modifying (`.backup` extension)
7. Log all changes to console and log file

**Execution**:
```bash
# Dry run (show what would be removed)
python3 docs/directives-json/Tasks/remove_helper_refs_from_directives.py --dry-run

# Execute (create backups and remove helper refs)
python3 docs/directives-json/Tasks/remove_helper_refs_from_directives.py --execute

# Restore from backups if needed
python3 docs/directives-json/Tasks/remove_helper_refs_from_directives.py --restore
```

---

## Verification Checklist

### Helper Function System
- [x] 349 helpers documented in JSON registries
- [x] All registries validated (JSON syntax)
- [x] Consolidations documented
- [x] Removed helpers documented
- [x] OOP policy documented
- [x] AI vs Code framework documented

### Directive Cleanup (Pending)
- [ ] Python script created and tested
- [ ] All directive JSON files cleaned (helper refs removed)
- [ ] Helper registries updated with `used_by_directives` data
- [ ] Directive markdown files updated (remove hardcoded helper lists)
- [ ] aifp_system_prompt.txt updated with database query guidance
- [ ] OOP handling integrated into relevant directives

### Database Import (Pending)
- [ ] directive_helpers table verified in aifp_core.sql
- [ ] Database import script created
- [ ] Import script populates directive_helpers from helper registries
- [ ] Relationships verified in database

---

## Files to Review

### Directive JSON Files (6 files) - Remove Helper Refs
1. `docs/directives-json/directives-project.json` - **HIGH PRIORITY**
2. `docs/directives-json/directives-fp-core.json`
3. `docs/directives-json/directives-fp-aux.json`
4. `docs/directives-json/directives-user-system.json`
5. `docs/directives-json/directives-user-pref.json`
6. `docs/directives-json/directives-git.json`

### Helper Registry Files (12 files) - Update used_by_directives
1. `docs/helpers/registry/helpers_registry_core.json`
2. `docs/helpers/registry/helpers_registry_mcp_orchestrators.json`
3. `docs/helpers/registry/helpers_registry_user_settings.json`
4. `docs/helpers/registry/helpers_registry_user_directives_getters.json`
5. `docs/helpers/registry/helpers_registry_user_directives_setters.json`
6. `docs/helpers/registry/helpers_registry_project_core.json`
7. `docs/helpers/registry/helpers_registry_project_structure_getters.json`
8. `docs/helpers/registry/helpers_registry_project_structure_setters.json`
9. `docs/helpers/registry/helpers_registry_project_workflow_getters.json`
10. `docs/helpers/registry/helpers_registry_project_workflow_setters.json`
11. `docs/helpers/registry/helpers_registry_project_orchestrators.json`
12. `docs/helpers/registry/helpers_registry_git.json`

### Directive Markdown Files (~125 files) - Remove Helper Lists
- `src/aifp/reference/directives/*.md`
- Focus on: `project_init.md`, `project_compliance_check.md`, `user_directive_*.md`

### System Prompt
- `sys-prompt/aifp_system_prompt.txt` - Add database query guidance

---

## Related Documentation

**Helper Function Registry**:
- `docs/helpers/registry/CURRENT_STATUS.md` - Current status overview
- `docs/helpers/registry/HELPER_REGISTRY_STATUS.md` - Detailed breakdown
- `docs/helpers/registry/helper-registry-guide.md` - Design principles & AI vs Code framework
- `docs/helpers/registry/CONSOLIDATION_REPORT.md` - Changes summary

**Policies & Decisions**:
- `docs/aifp-oop-policy.md` - FP-only policy, OOP rejection workflow
- `docs/helpers/registry/helper-registry-guide.md` (Section 0) - AI vs Code decision framework

**Database Schema**:
- `src/aifp/database/schemas/aifp_core.sql` - Line 113: directive_helpers table

**Archive**:
- `docs/COMPLETE/ARCHIVE_MANIFEST.md` - List of archived planning docs

---

## Timeline Estimate

**Phase 1: Cleanup Script** (1 session)
- Create Python script to remove helper refs from directive JSON files
- Test on one file, then run on all 6 files

**Phase 2: Helper Registry Updates** (1-2 sessions)
- Review all 349 helpers for `used_by_directives` completeness
- Update missing or incomplete directive references

**Phase 3: Markdown & System Prompt** (1 session)
- Update directive markdown files (remove hardcoded helper lists)
- Update aifp_system_prompt.txt with database query guidance

**Phase 4: Database Import Script** (1-2 sessions)
- Create script to import directives, helpers, and build directive_helpers table
- Test and verify relationships

**Total**: 4-6 sessions

---

## Key Decisions

1. **Helper registries are source of truth** for directive-helper relationships
   - Rationale: Helpers are more stable than directives
   - Implementation: `used_by_directives` field in each helper entry

2. **Remove ALL helper references from directive files**
   - Directive JSON files: Remove `helper` and `helper_*` fields
   - Directive markdown files: Remove hardcoded helper lists
   - AI queries database at runtime instead

3. **Database import script builds relationships**
   - Reads `used_by_directives` from helper registries
   - Populates `directive_helpers` table automatically
   - Single source of truth = helper registries

4. **Update system prompt**
   - AI must query `get_helpers_for_directive()` when executing directives
   - No reliance on hardcoded references

---

**Status**: ⏳ Awaiting directive cleanup script and helper registry updates
**Blocker**: Must complete before database import
**Owner**: TBD
**Last Updated**: 2025-12-06
