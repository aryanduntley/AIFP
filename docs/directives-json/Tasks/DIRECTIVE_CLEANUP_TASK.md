# Task: Directive Review & Cleanup for Helper Function Consistency

**Date Created**: 2025-12-06
**Date Updated**: 2025-12-14
**Status**: 🔄 In Progress (Phases 1 & 3 Complete)
**Priority**: High
**Blocking**: Database import, directive implementation

---

## Overview

Helper function consolidation is now complete. All directives must be reviewed and updated for consistency with the new helper function system.

**Key Decision**: Helper-directive relationships are stored in the **database** (`directive_helpers` table). Development documentation in `docs/helpers/` is for database import preparation only. AI queries the database at runtime, not documentation files.

---

## Helper Function Completion Summary

**Status**: ✅ **COMPLETE** (2025-12-14 - Consolidated)
- **Consolidated Docs**: 7 markdown files organized by function category
- **Databases Covered**: 4 (aifp_core.db, user_preferences.db, user_directives.db, project.db)
- **Source of Truth**: `docs/helpers/helpers-consolidated-*.md`
- **Total Helpers**: 337 helper functions documented in consolidated format

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
   - See `docs/helpers/registry/helper-registry-guide.md` (legacy documentation) for full framework

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

**Location**: `docs/helpers/helpers-consolidated-*.md`
**Database Table**: `directive_helpers` (junction table in aifp_core.db)

### How Relationships Are Maintained

**Production Source of Truth**: Database (`directive_helpers` table in aifp_core.db)

**Development Preparation**: Consolidated helper documentation in `docs/helpers/` (for database import preparation only)

**Database Import Script** reads development helper documentation and populates `directive_helpers` table for production use.

### Benefits of This Approach

- ✅ Database is the single source of truth for production
- ✅ No duplicate helper lists in directive files
- ✅ Easier to maintain (update database, not scattered documentation)
- ✅ AI queries database dynamically at runtime
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

## Progress Summary

### Phase 1: Directive JSON Cleanup ✅ COMPLETE (2025-12-07)

**Completed Actions:**
- ✅ Created scan script (`scan_helper_refs.py`) to identify all helper references
- ✅ Identified 13 helper references across 3 directive files
- ✅ Created removal script (`remove_helper_refs.py`) with backup/restore functionality
- ✅ Moved `directive-helper-interactions.json` to backups (temporary reference)
- ✅ Removed all 13 helper references from directive JSON files
- ✅ Created timestamped backups of all directive files
- ✅ Verified cleanup with re-scan (0 helper references remaining)

**Results:**
- `directives-project.json`: 11 helper refs removed
- `directives-user-system.json`: 1 helper ref removed (entire `helper_functions` section)
- `directives-user-pref.json`: 1 helper ref removed
- `directives-fp-core.json`, `directives-fp-aux.json`, `directives-git.json`: Already clean

**Backups Location:** `docs/directives-json/backups/` (timestamp: 20251207_164554)

---

## Required Actions

### 1. ✅ Remove ALL Helper References from Directive JSON Files (COMPLETE)

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

**Method**: Python script (`remove_helper_refs.py`) ✅ **COMPLETE**

**Rationale**: Helper-directive relationships are stored in the database (`directive_helpers` table), not directive files.

**Completion Date**: 2025-12-07

### 2. ⏳ Update Consolidated Helper Documentation with Directive References (FOR DATABASE IMPORT PREP ONLY)

**Status**: Pending review (consolidated helper docs in `docs/helpers/` are for database import preparation)

**Important**: These files are development/preparation materials only. Production references the database, not documentation.

**For each helper** in the 7 consolidated helper markdown files in `docs/helpers/`, ensure:
- Directive relationships are documented for database import script to read
- Documentation includes directive names (not IDs, since directives aren't imported yet)
- Update any helpers with incomplete or missing directive relationship data

**Example** (from consolidated helper docs - development preparation):
```markdown
### initialize_aifp_project()
**Used by directives**: project_init
**Purpose**: Initialize project structure and databases
```

**Note**: The database import script will read these dev docs, resolve directive names to IDs, and populate the `directive_helpers` table in production database.

### 3. 🔄 Update aifp_system_prompt.txt (NEXT)

**Add guidance** about database-driven helper-directive relationships:

```
When executing a directive, use get_helpers_for_directive(directive_id, include_helpers_data=true)
to retrieve all associated helper functions from the database. Do not rely on hardcoded helper
references in directive files.
```

### 4. ⏳ Remove Hardcoded Helper Lists from Directive Markdown Files (NEXT)

**Location**: `src/aifp/reference/directives/*.md`
**Method**: Python/console script to scan ~125 MD files

**Action**: Remove sections like:
```markdown
**Referenced Helper Functions:**
- `scan_existing_files(project_root)` - Returns structure map
- `infer_architecture(project_root)` - Detects architectural style
```

**Replace with**:
```markdown
## Helper Functions

This directive's helper functions are stored in the database.
At runtime, query the database using:
```python
get_helpers_for_directive(directive_id, include_helpers_data=true)
```
to retrieve all associated helpers.
```

### 5. ⏳ Create Database Import Script

**Script**: Reads consolidated helper documentation and populates `directive_helpers` table.

**Logic**:
1. Import all directives to `directives` table (get directive IDs)
2. Import all helpers to `helper_functions` table (get helper function IDs)
3. For each helper, read directive relationship metadata from consolidated docs
4. For each directive name in the relationships:
   - Look up directive_id from directives table
   - Insert into `directive_helpers` (directive_id, helper_function_id, execution_context, sequence_order, is_required)

**Note**: This approach means consolidated helper documentation is the single source of truth for relationships.

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

### Helper Function System ✅ COMPLETE
- [x] Helper functions documented in JSON registries
- [x] All registries validated (JSON syntax)
- [x] Consolidations documented
- [x] Removed helpers documented
- [x] OOP policy documented
- [x] AI vs Code framework documented

### Directive JSON Cleanup ✅ COMPLETE (2025-12-07)
- [x] Python scan script created (`scan_helper_refs.py`)
- [x] Python removal script created (`remove_helper_refs.py`)
- [x] All directive JSON files cleaned (13 helper refs removed, 0 remaining)
- [x] Backups created with timestamps in `backups/` folder
- [x] `directive-helper-interactions.json` moved to backups
- [x] Cleanup verified with re-scan

### Documentation Cleanup 🔄 IN PROGRESS
- [ ] Consolidated helper docs reviewed for directive relationship completeness
- [x] Directive markdown files scanned for hardcoded helper lists (~125 files) - MD_CLEANUP_CHECKLIST.md shows 100%
- [x] Directive markdown files cleaned (remove hardcoded helper lists) - COMPLETE 2025-12-14
- [ ] aifp_system_prompt.txt updated with database query guidance
- [ ] README.md reviewed and cleaned if needed

### Database Import ⏳ PENDING
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

### Consolidated Helper Documentation (7 files) - Update directive relationships
1. `docs/helpers/helpers-consolidated-core.md`
2. `docs/helpers/helpers-consolidated-git.md`
3. `docs/helpers/helpers-consolidated-index.md`
4. `docs/helpers/helpers-consolidated-orchestrators.md`
5. `docs/helpers/helpers-consolidated-project.md`
6. `docs/helpers/helpers-consolidated-settings.md`
7. `docs/helpers/helpers-consolidated-user-custom.md`

### Directive Markdown Files (~125 files) - Remove Helper Lists
- `src/aifp/reference/directives/*.md`
- Focus on: `project_init.md`, `project_compliance_check.md`, `user_directive_*.md`

### System Prompt
- `sys-prompt/aifp_system_prompt.txt` - Add database query guidance

---

## Related Documentation

**Development Preparation Files** (for database import only):
- `docs/helpers/helpers-consolidated-index.md` - Index of helper functions for import prep
- `docs/helpers/helpers-consolidated-*.md` (7 files) - Helper documentation for import prep
- Categories: core, git, orchestrators, project, settings, user-custom

**Production Source**: Database queries using `get_helpers_for_directive()` and related functions

**Policies & Decisions**:
- `docs/aifp-oop-policy.md` - FP-only policy, OOP rejection workflow
- `docs/helpers/registry/helper-registry-guide.md` (legacy documentation, Section 0) - AI vs Code decision framework

**Database Schema**:
- `src/aifp/database/schemas/aifp_core.sql` - Line 113: directive_helpers table

**Archive**:
- `docs/COMPLETE/ARCHIVE_MANIFEST.md` - List of archived planning docs

---

## Timeline Estimate

**Phase 1: Cleanup Script** ✅ COMPLETE (1 session)
- Create Python script to remove helper refs from directive JSON files
- Test on one file, then run on all 6 files

**Phase 2: Consolidated Helper Updates** (1-2 sessions)
- Review all 337 helpers for directive relationship completeness
- Update missing or incomplete directive references in consolidated docs

**Phase 3: Markdown & System Prompt** ✅ COMPLETE (1 session)
- Update directive markdown files (remove hardcoded helper lists) - DONE 2025-12-14
- Update aifp_system_prompt.txt with database query guidance - PENDING

**Phase 4: Database Import Script** (1-2 sessions)
- Create script to import directives, helpers, and build directive_helpers table
- Test and verify relationships

**Total**: 4-6 sessions (Phase 1 & 3 complete)

---

## Key Decisions

1. **Database is the production source of truth** for directive-helper relationships
   - Rationale: Single source of truth for all production queries
   - Implementation: `directive_helpers` table in aifp_core.db
   - Development docs in `docs/helpers/` are for database import preparation only

2. **Remove ALL helper references from directive files** ✅ COMPLETE
   - Directive JSON files: Remove `helper` and `helper_*` fields - DONE 2025-12-07
   - Directive markdown files: Remove hardcoded helper lists - DONE 2025-12-14
   - AI queries database at runtime, not documentation

3. **Database import script builds production relationships**
   - Reads development documentation in `docs/helpers/` as preparation data
   - Populates `directive_helpers` table in production database
   - Production source of truth = database, not documentation

4. **Update system prompt** ⏳ PENDING
   - AI must query database using `get_helpers_for_directive()` when executing directives
   - No reliance on hardcoded references or documentation files

---

## Scripts Created

1. **`scan_helper_refs.py`** ✅
   - Recursively scans directive JSON files for helper references
   - Outputs detailed report with paths and context
   - Generates JSON report for archival

2. **`remove_helper_refs.py`** ✅
   - Removes all helper references from directive JSON files
   - Supports `--dry-run`, `--execute`, `--restore` modes
   - Creates timestamped backups before modification
   - Preserves all other fields and formatting

---

**Status**: 🔄 Phases 1 & 3 Complete (Directive JSON & MD cleanup done), Phase 2 In Progress (Consolidated helper updates)
**Blocker**: Must complete consolidated helper review before database import
**Owner**: TBD
**Last Updated**: 2025-12-14
