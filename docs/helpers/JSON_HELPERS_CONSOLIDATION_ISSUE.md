# Helper JSON Files Consolidation Issue

**Date**: 2025-12-22
**Status**: 🔴 **CRITICAL ISSUE IDENTIFIED**
**Priority**: High - Affects AI's ability to correctly call helper functions

---

## Problem Summary

The helper JSON files in `docs/helpers/json/` were created BEFORE the helper consolidation effort and do NOT match the consolidated design philosophy documented in `REMOVE-helpers-consolidated.md`.

**Result**: Helper JSON files contain:
- ❌ Outdated singular/plural getter patterns (get_note, get_notes)
- ❌ Missing or incomplete parameter definitions
- ❌ Too many specific helpers instead of using generic Tier 2/3/4 functions
- ❌ Inconsistent with the tiered approach

---

## Specific Issues Found

### Issue 1: Notes Helper Parameters Were Incomplete

**File**: `docs/helpers/json/helpers-project-3.json`

**Before Fix** (lines 692-723):
```json
{
  "name": "add_note",
  "parameters": [
    {"name": "content", "type": "string", "required": true},
    {"name": "source", "type": "string", "required": false, "default": "ai"},
    {"name": "severity", "type": "string", "required": false, "default": "info"},
    {"name": "directive_name", "type": "string", "required": false}
  ]
}
```

**MISSING CRITICAL PARAMETERS**:
- ❌ `note_type` (REQUIRED by schema!)
- ❌ `reference_table` (optional)
- ❌ `reference_id` (optional)

**After Fix**:
```json
{
  "name": "add_note",
  "parameters": [
    {"name": "content", "type": "string", "required": true},
    {"name": "note_type", "type": "string", "required": true, "description": "'clarification', 'pivot', 'research', 'entry_deletion', 'warning', 'error', 'info', 'auto_summary'"},
    {"name": "reference_table", "type": "string", "required": false},
    {"name": "reference_id", "type": "integer", "required": false},
    {"name": "source", "type": "string", "required": false, "default": "ai"},
    {"name": "severity", "type": "string", "required": false, "default": "info"},
    {"name": "directive_name", "type": "string", "required": false}
  ]
}
```

**Impact**: AI wouldn't know to pass `note_type`, causing schema constraint violations at runtime.

---

### Issue 2: Singular/Plural Getters Pattern (Outdated)

**According to consolidation philosophy**, we should NOT have:
- ❌ `get_note(note_id)` - singular getter
- ❌ `get_notes([note_ids])` - plural getter

**Instead, use tiered approach**:
- ✅ `get_from_project("notes", [id])` - Tier 3 (ID-based)
- ✅ `get_notes_comprehensive(filters)` - Tier 1 (high-frequency specific)
- ✅ `search_notes(search_string, filters)` - Tier 1 (high-frequency specific)

**Why**: Reduces cognitive load. AI learns:
- Generic pattern for ID retrieval (all tables)
- Specific named helpers only for truly high-frequency operations

---

### Issue 3: Many Helpers Have Blank Parameters

**Example**: From helpers-project-3.json
```json
{
  "name": "get_notes_comprehensive",
  "parameters": [],  // ❌ BLANK - should list all filter parameters
  "purpose": "Advanced note search with filters"
}
```

**Should be**:
```json
{
  "name": "get_notes_comprehensive",
  "parameters": [
    {"name": "note_type", "type": "string", "required": false, "description": "Filter by note_type"},
    {"name": "reference_table", "type": "string", "required": false, "description": "Filter by reference table"},
    {"name": "reference_id", "type": "integer", "required": false, "description": "Filter by reference ID"},
    {"name": "source", "type": "string", "required": false, "description": "Filter by source ('ai', 'user', 'directive')"},
    {"name": "severity", "type": "string", "required": false, "description": "Filter by severity"},
    {"name": "directive_name", "type": "string", "required": false, "description": "Filter by directive name"}
  ],
  "purpose": "Advanced note search with filters"
}
```

**Impact**: AI doesn't know what parameters exist, can't use the helper effectively.

---

## Root Cause

### Timeline of Events

1. **2025-12-11**: Helper consolidation completed
   - Created `REMOVE-helpers-consolidated.md` with tiered design philosophy
   - Documented that singular/plural getters should be replaced with generic Tier 2/3/4 functions
   - Established that only truly high-frequency operations get specific named helpers

2. **Before 2025-12-11**: JSON helper files created
   - Files: `helpers-project-1.json`, `helpers-project-2.json`, `helpers-project-3.json`, etc.
   - Created with old pattern: singular getters, plural getters, incomplete parameters
   - Created BEFORE consolidation philosophy was established

3. **2025-12-22**: Issue discovered during note_type parameter fix
   - Noticed `add_note` missing critical parameters
   - Investigated and found systemic issue across all JSON files

---

## The Consolidation Philosophy (Reference)

From `REMOVE-helpers-consolidated.md`:

### Tiered Approach

**Tier 1: High-Frequency Specific Helpers** (~25 functions)
- Zero cognitive load
- Used dozens of times per session
- Examples: `get_directive_by_name()`, `get_file_by_path()`, `get_function_by_name()`
- **For notes**: `get_notes_comprehensive()`, `search_notes()`, `add_note()`, `update_note()`, `delete_note()`

**Tier 2: JSON-Based Filtering** (4 functions - one per database)
- Replaces 50+ granular getters
- `get_from_X_where(table, conditions, limit, orderby)`
- Examples: `get_from_project_where("notes", {"note_type": "auto_summary"}, 10)`

**Tier 3: ID-Based Retrieval** (4 functions - one per database)
- `get_from_X(table, id_array)`
- Core DB: Empty array allowed (returns all)
- Project/Settings/User Custom: Empty array NOT allowed
- Examples: `get_from_project("notes", [1, 5, 12])`

**Tier 4: Raw SQL Queries** (4 functions - one per database)
- `query_X(table, query)`
- Advanced, rare use only

### Key Principle: Reduce Function Count

**Old approach** (pre-consolidation):
- `get_note(id)` - singular
- `get_notes([ids])` - plural
- `get_note_by_type(type)` - specific getter
- `get_note_by_severity(severity)` - specific getter
- `get_note_by_source(source)` - specific getter
- ... and so on (could be 20+ functions per table!)

**New approach** (consolidated):
- `get_from_project("notes", [id])` - Tier 3 for ID lookup
- `get_from_project_where("notes", {"note_type": "auto_summary"})` - Tier 2 for filtering
- `get_notes_comprehensive(filters)` - Tier 1 ONLY if truly high-frequency
- `search_notes(search_string, filters)` - Tier 1 ONLY for content search

**Result**: 5 functions instead of 20+, less cognitive load, more flexible

---

## Scope of the Problem

### Files Affected

All JSON helper files in `docs/helpers/json/`:
- ❌ `helpers-project-1.json`
- ❌ `helpers-project-2.json`
- ❌ `helpers-project-3.json`
- ❌ `helpers-fp-1.json` (if exists)
- ❌ `helpers-user-preferences.json` (if exists)
- ❌ `helpers-user-directives.json` (if exists)
- ❌ Any other JSON helper files

### Estimated Issue Count

Based on notes table example:
- **~335 total helpers in registry** (from CONSOLIDATION_COMPLETE.md)
- **~130 helpers in consolidated design** (from REMOVE-helpers-consolidated.md)
- **~205 helpers should be removed** (replaced by Tier 2/3/4 generic functions)
- **~130 helpers need parameter audits** (fill in blank parameter fields)

---

## Solution Path

### Phase 1: Documentation Review ✅ COMPLETE

**Status**: Done (this document)

**Tasks**:
- ✅ Identify the issue
- ✅ Document root cause
- ✅ Explain consolidation philosophy
- ✅ Define scope

---

### Phase 2: Schema-to-Helper Parameter Audit

**Status**: Not Started

**Goal**: Ensure every helper's parameters match the corresponding database schema

**Process**:
1. For each database table, read the schema
2. For each helper that operates on that table, verify parameters
3. Fill in missing parameters
4. Add parameter descriptions with valid values
5. Ensure parameter types match schema field types

**Example Audit**:
```
Table: notes (project.sql)
Schema fields:
  - content TEXT NOT NULL
  - note_type TEXT NOT NULL CHECK (note_type IN ('clarification', 'pivot', ...))
  - reference_table TEXT
  - reference_id INTEGER
  - source TEXT DEFAULT 'ai' CHECK (source IN ('ai', 'user', 'directive'))
  - severity TEXT DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'error'))
  - directive_name TEXT

Helper: add_note
Parameters must include all above fields with:
  - Correct types (string, integer)
  - Correct required status
  - Valid value descriptions for CHECK constraints
  - Defaults where applicable
```

**Output**: Updated JSON files with complete parameter definitions

---

### Phase 3: Remove Outdated Singular/Plural Getters

**Status**: Not Started

**Goal**: Remove helpers that are replaced by generic Tier 2/3/4 functions

**Process**:
1. Identify all singular getters (get_X) and plural getters (get_Xs)
2. Check if they should be replaced by:
   - `get_from_project(table, [ids])` (Tier 3)
   - `get_from_project_where(table, conditions)` (Tier 2)
3. Remove from JSON files if redundant
4. Update directive mappings if directives reference removed helpers

**Examples to Remove**:
- ❌ `get_note(id)` → Use `get_from_project("notes", [id])`
- ❌ `get_notes([ids])` → Use `get_from_project("notes", ids)`
- ❌ `get_file(id)` → Use `get_from_project("files", [id])`
- ❌ `get_files([ids])` → Use `get_from_project("files", ids)`

**Examples to Keep** (Tier 1 - truly high-frequency):
- ✅ `get_file_by_path(path)` - Used constantly
- ✅ `get_function_by_name(name)` - Used constantly
- ✅ `get_directive_by_name(name)` - Used constantly
- ✅ `get_notes_comprehensive(filters)` - High-frequency with complex filtering

---

### Phase 4: Verify Against Consolidated Spec

**Status**: Not Started

**Goal**: Ensure JSON files match `REMOVE-helpers-consolidated.md` exactly

**Process**:
1. Read consolidated spec for each database
2. For each helper in spec:
   - Verify it exists in JSON files
   - Verify parameters match
   - Verify classification (is_tool, is_sub_helper) matches
   - Verify "used_by_directives" is populated
3. For each helper in JSON files:
   - Verify it's in consolidated spec OR has justification
   - Remove if not in spec and not Tier 1 high-frequency

**Output**: JSON files that perfectly match consolidated design

---

### Phase 5: Update Implementation Code

**Status**: Not Started (FUTURE)

**Goal**: Update actual Python helper implementations to match JSON definitions

**Note**: This is a separate effort. JSON files document the design; Python code implements it.

**Process**:
1. For each JSON helper, check if implementation exists
2. Update implementation signatures to match JSON parameters
3. Add missing helpers
4. Remove outdated helper implementations

**Output**: Python helper implementations that match JSON design

---

## Immediate Action Taken (2025-12-22)

### Fixed: Notes Table Helpers

**File**: `docs/helpers/json/helpers-project-3.json`

**Changes**:
1. ✅ `add_note`: Added missing `note_type`, `reference_table`, `reference_id` parameters
2. ✅ `get_notes_comprehensive`: Added all filter parameters (note_type, reference_table, reference_id, source, severity, directive_name)
3. ✅ `search_notes`: Added `note_type` parameter to filter list
4. ✅ `update_note`: Added all update parameters (content, note_type, reference_table, reference_id, source, severity, directive_name)
5. ✅ `delete_note`: Added `id` parameter (was blank)

**Result**: Notes helpers now have complete, accurate parameter definitions.

---

## Recommended Next Steps

### Step 1: Create Audit Script (Optional)

**Purpose**: Automate comparison between schema and JSON parameters

**Script**: `docs/helpers/audit_helper_parameters.py`

**Features**:
- Read all schema files (aifp_core.sql, project.sql, user_preferences.sql, user_directives.sql)
- Parse table definitions and field types
- Read all JSON helper files
- Compare helper parameters to table schemas
- Report missing parameters, type mismatches, extra parameters

**Output**: Audit report with issues found

---

### Step 2: Manual Audit (Systematic)

**Process**:
1. Create checklist of all tables across all databases
2. For each table:
   - List all helpers that operate on it
   - Verify parameters match schema
   - Fill in missing parameters
   - Add descriptions with valid values
3. Document changes in audit log

**Time Estimate**: Significant effort - 335 helpers in registry, ~130 in consolidated design

---

### Step 3: Update Directives That Reference Outdated Helpers

**Process**:
1. Search all directive MD files for helper references
2. If directive references removed helper (e.g., `get_note(id)`):
   - Update to use generic pattern (e.g., `get_from_project("notes", [id])`)
   - Update directive documentation
   - Update JSON directive helper mappings

**Example**:
```markdown
# Before
Call `get_note(note_id)` to retrieve the note.

# After
Call `get_from_project("notes", [note_id])` to retrieve the note.
```

---

## Priority Assessment

### Critical (Do First)

1. **Complete notes helper parameters** ✅ DONE (2025-12-22)
2. **Audit project.db table helpers** (files, functions, types, tasks, etc.)
   - These are used most frequently
   - Missing parameters will cause runtime failures
3. **Document which singular/plural getters should be removed**
   - Create removal list
   - Don't actually remove yet (breaking change)

### High Priority (Do Soon)

4. **Audit aifp_core.db table helpers** (directives, helpers, categories)
   - Less critical (read-only database)
   - But still used frequently
5. **Update directive documentation** for removed helpers
   - Prevent confusion
   - Show correct generic patterns

### Medium Priority (Do Later)

6. **Audit user_preferences.db helpers**
   - Used less frequently
7. **Audit user_directives.db helpers**
   - Only used in Use Case 2 (automation projects)
8. **Create removal plan for outdated helpers**
   - Document breaking changes
   - Plan migration path

### Low Priority (Future)

9. **Implement missing helpers in Python code**
10. **Remove outdated helper implementations**
11. **Create automated tests for helper parameter validation**

---

## Success Criteria

✅ **Phase 1 Complete** when:
- All helpers have complete parameter definitions
- No blank parameter fields
- All parameters match schema field types
- All CHECK constraint values documented

✅ **Phase 2 Complete** when:
- All singular/plural getters identified for removal
- Removal list documented
- Directive impacts assessed

✅ **Phase 3 Complete** when:
- JSON files match `REMOVE-helpers-consolidated.md` exactly
- All outdated helpers removed
- All directives updated to use new patterns

✅ **Phase 4 Complete** when:
- Python implementations match JSON definitions
- All helpers tested
- Documentation updated

---

## Notes for Future Sessions

### When Adding New Helpers

**Always follow this checklist**:

1. ✅ Is this operation truly high-frequency? (Tier 1)
   - If NO: Use Tier 2/3/4 generic functions instead
   - If YES: Proceed with specific named helper

2. ✅ Does this table operation need a specific helper?
   - If table is simple: Use `get_from_X_where()` (Tier 2)
   - If operation is complex: Create specific helper (Tier 1)

3. ✅ Are ALL parameters from schema included?
   - Read the schema table definition
   - Include every field that might be queried or set
   - Mark required vs optional correctly
   - Add descriptions with valid values for CHECK constraints

4. ✅ Is the helper classification correct?
   - `is_tool=true`: AI can call directly via MCP
   - `is_tool=false, is_sub_helper=false`: Called via directives
   - `is_sub_helper=true`: Internal, called by other helpers

5. ✅ Is "used_by_directives" populated?
   - List all directives that use this helper
   - Include execution_context and description

### When Updating Schemas

If you add/modify a database table:

1. ✅ Update schema file (e.g., `project.sql`)
2. ✅ Find all helpers that operate on that table
3. ✅ Update helper parameters in JSON files
4. ✅ Update helper implementations in Python code
5. ✅ Update directive documentation if needed

---

**Document Status**: Ready for review and action planning
**Next Action**: Decide whether to proceed with Phase 2 (Schema-to-Helper Parameter Audit)
