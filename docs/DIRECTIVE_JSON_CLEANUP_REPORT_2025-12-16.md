# Directive JSON Files Cleanup Report

**Date**: 2025-12-16
**Scope**: Schema reference cleanup in directive JSON files
**Status**: ✅ COMPLETE

---

## Executive Summary

Successfully cleaned all directive JSON files to align with recent schema changes:
- ✅ Removed references to removed `project.blueprint_checksum` field
- ✅ Clarified ambiguous "interactions table" references
- ✅ Verified all other schema references are correct
- ✅ Confirmed `intent_keywords_json` field remains (handled by sync-directives.py later)

**Files Modified**: 2
**Changes Made**: 4
**Backups Created**: 2

---

## Changes Made

### 1. directives-fp-aux.json (2 changes)

**Backup**: `backups/directives-fp-aux_schema_cleanup_[timestamp].json`

#### Change 1: fp_recursion_enforcement (line 1281)
**Before**:
```json
"description": "...Links to project_update_db to track recursion depth in interactions table."
```

**After**:
```json
"description": "...Links to project_update_db to track recursion depth in function interactions table (project.interactions)."
```

**Reason**: Clarified that this refers to `project.interactions` (function dependencies), not the removed `directives_interactions` table.

#### Change 2: fp_monadic_composition (line 1346)
**Before**:
```json
"description": "...Links to project_update_db to store monadic dependencies in interactions table."
```

**After**:
```json
"description": "...Links to project_update_db to store monadic dependencies in function interactions table (project.interactions)."
```

**Reason**: Clarified that this refers to `project.interactions` (function dependencies), not the removed `directives_interactions` table.

---

### 2. directives-project.json (2 changes)

**Backup**: `backups/directives-project_schema_cleanup_[timestamp].json`

#### Change 1: project_blueprint_read (lines 1982-1990)
**Before**:
```json
{
  "if": "parse_complete",
  "then": "return_structured_data",
  "details": {
    "include_checksum": true,
    "compare_with_db": true,
    "db_checksum_field": "project.blueprint_checksum"
  }
}
```

**After**:
```json
{
  "if": "parse_complete",
  "then": "return_structured_data",
  "details": {
    "return_structured_data": true
  }
}
```

**Reason**: Removed reference to `project.blueprint_checksum` field (removed from project database schema). Git handles version tracking via `last_known_git_hash` field.

#### Change 2: project_blueprint_update (lines 2083-2091)
**Before**:
```json
{
  "if": "write_complete",
  "then": "update_blueprint_checksum",
  "details": {
    "update_checksum": true,
    "table": "project",
    "field": "blueprint_checksum"
  }
},
{
  "if": "update_complete",
  "then": "return_success",
  ...
}
```

**After**:
```json
{
  "if": "write_complete",
  "then": "return_success",
  ...
}
```

**Reason**: Removed entire workflow step that updated non-existent `project.blueprint_checksum` field. Git handles this functionality now.

---

## Verification Results

### ✅ No Old Schema References Found

**Checked**:
- ❌ `directives_interactions` table → **0 references** (removed table, should have 0)
- ❌ `blueprint_checksum` field → **0 references** (removed field, should have 0)
- ✅ "interactions table" → **2 references, both clarified** (now say "function interactions table (project.interactions)")

### ✅ Valid References Preserved

**File Checksums** (for change detection):
- directives-project.json: 6 valid references (file tracking)
- directives-user-system.json: 6 valid references (user directive source file tracking)
- **All preserved** - these are correct and necessary

**Database Tables** (current schema):
- `project.interactions` → Function dependencies ✅
- `project.files` → File tracking ✅
- `project.functions` → Function registry ✅
- `directive_flow` → Directive navigation ✅
- `intent_keywords` → Keyword normalization ✅

---

## Files Reviewed (No Changes Needed)

### directives-fp-core.json
**Status**: ✅ Clean
**Checked**: No old schema references found

### directives-git.json
**Status**: ✅ Clean
**Checked**: No old schema references found

### directives-user-pref.json
**Status**: ✅ Clean
**Checked**: No old schema references found

### directives-user-system.json
**Status**: ✅ Clean (file checksums are valid)
**Checked**: 6 checksum references - all for user directive source file change detection (valid)

---

## What Was NOT Changed (Intentional)

### 1. intent_keywords_json Field (Kept)

**Occurrences**: 117 directives across 5 files
- directives-fp-aux.json (36)
- directives-fp-core.json (29)
- directives-git.json (6)
- directives-project.json (38)
- directives-user-pref.json (8)

**Status**: ✅ **Keeping for now**

**Reason**:
- Field will be removed when sync-directives.py is updated (future task)
- Sync script will normalize these into `intent_keywords` + `directives_intent_keywords` tables
- For now, field provides dev convenience for editing keywords in JSON

**Example** (staying as-is):
```json
{
  "name": "aifp_run",
  "intent_keywords_json": [
    "run",
    "execute",
    "aifp",
    "start"
  ]
}
```

---

## Alignment with Previous Cleanup Work

### ✅ Builds on Completed Cleanups

**1. MD Files Cleanup** (Complete per MD_CLEANUP_CHECKLIST.md)
- 125 directive MD files cleaned (100%)
- Removed all hardcoded helper references
- Replaced with database query guidance

**2. Helper Function Cleanup** (Complete per DIRECTIVE_CLEANUP_TASK.md)
- Removed all `helper` fields from directive JSON workflows
- Directive-helper relationships now in database (`directive_helpers` table)

**3. SQL Cleanup** (Complete per SQL_CLEANUP_CHECKLIST.md)
- Removed all `INSERT INTO notes` from FP directives (27 files)
- Logging is opt-in via `fp_flow_tracking` (disabled by default)

**4. Schema Updates** (This report)
- ✅ Removed `blueprint_checksum` references
- ✅ Clarified `interactions table` references
- ✅ Verified all other schema references

---

## Schema Version Compliance

### ✅ Core Database (aifp_core.sql v1.9)
- `intent_keywords` table → Used ✅
- `directives_intent_keywords` table → Used ✅
- `directive_flow` table → Used ✅
- `directives_interactions` table → **Removed** ✅
- `directives.intent_keywords_json` field → **Removed from schema** (JSON files will be handled by sync script)

### ✅ Project Database (project.sql v1.3)
- `project.interactions` table → Function dependencies ✅
- `project.blueprint_checksum` field → **Removed** ✅
- `project.last_known_git_hash` field → Git tracking ✅
- File checksums → Valid for change detection ✅

---

## Success Criteria Met

- [x] No references to `directives_interactions` table
- [x] All "interactions table" references clarified with "(project.interactions)"
- [x] No references to `project.blueprint_checksum` field
- [x] All directive JSON files verified clean
- [x] Backups created for modified files
- [x] Valid checksum references preserved (file tracking)
- [x] intent_keywords_json field kept for now (sync script will handle)

---

## Next Steps

### Immediate (Ready Now)
1. ✅ **Directive JSON cleanup** - COMPLETE (this report)
2. ✅ **Directive MD cleanup** - COMPLETE (MD_CLEANUP_CHECKLIST.md)
3. ✅ **Helper function cleanup** - COMPLETE (DIRECTIVE_CLEANUP_TASK.md)

### Future (When Ready)
4. **directive_flow mapping** - Map directive flows for navigation system
5. **directive_helpers mapping** - Populate `used_by_directive` field in helpers
6. **sync-directives.py update** - Handle `intent_keywords_json` normalization
7. **Database population** - Import cleaned directives into production database

---

## Files Modified Summary

| File | Changes | Backup Location |
|------|---------|----------------|
| directives-fp-aux.json | 2 clarifications | backups/directives-fp-aux_schema_cleanup_*.json |
| directives-project.json | 2 removals | backups/directives-project_schema_cleanup_*.json |

---

## Statistics

**Total Files Reviewed**: 6
- directives-fp-aux.json ✓
- directives-fp-core.json ✓
- directives-git.json ✓
- directives-project.json ✓
- directives-user-pref.json ✓
- directives-user-system.json ✓

**Total Changes**: 4
- Clarifications: 2
- Removals: 2

**Lines Modified**: 12 total
- directives-fp-aux.json: 2 lines
- directives-project.json: 10 lines (removed workflow step)

---

## Conclusion

All directive JSON files are now aligned with the current schema (core v1.9, project v1.3). Old table and field references have been removed or clarified. Files are ready for directive_flow and directive_helpers mapping tasks.

**Status**: ✅ **READY FOR NEXT PHASE**

---

**Report Created**: 2025-12-16
**Reviewed By**: Claude (AIFP Schema Cleanup Assistant)
**Next Task**: directive_flow mapping and directive_helpers mapping
