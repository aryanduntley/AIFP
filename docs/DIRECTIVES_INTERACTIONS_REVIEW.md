# directives_interactions Table Removal - Review

**Status**: Schema updated, helpers updated, documentation updated
**Last Updated**: 2025-01-15

---

## Summary

The `directives_interactions` table has been removed from the core database schema (v1.8) and replaced with `directive_flow`. This document tracks all remaining references that need to be updated or verified.

### Current Status

✅ **Completed**:
- Core schema (v1.8)
- Helper functions (core & orchestrators)
- Production directive MD files (aifp_help.md)
- Task documentation notes added

⚠️ **Pending** (for future directive flow implementation):
- sync-directives.py updates (awaiting directive-flow.json creation)
- directive-flow.json creation (planned for later)

---

## ✅ Already Completed

### 1. Core Schema (src/aifp/database/schemas/aifp_core.sql)
- ✅ Removed `directives_interactions` table
- ✅ Added `directive_flow` table
- ✅ Updated version to 1.8

### 2. Core Helpers (docs/helpers/helpers-consolidated-core.md)
- ✅ Removed `get_directive_interactions()`
- ✅ Removed `get_interactions_for_directive()`
- ✅ Removed `get_interactions_for_directive_as_target()`
- ✅ Added new directive navigation helpers

### 3. Orchestrators (docs/helpers/helpers-consolidated-orchestrators.md)
- ✅ Added `aifp_status()` orchestrator

---

## 📋 Files Requiring Updates

### Category 1: Orchestrator References (SAFE - Not directives_interactions)

**File**: `docs/helpers/helpers-consolidated-orchestrators.md:368`
```
**Helpers Called**: get_incomplete_tasks, get_task_flows, get_files_by_flow,
get_incomplete_sidequests, get_functions_by_file, get_interactions_by_function
```

**Status**: ✅ NO ACTION NEEDED
- `get_interactions_by_function` refers to **project database** `interactions` table (function dependencies)
- NOT related to `directives_interactions` table
- This is correct

---

### Category 2: Directive JSON Files (ACTION REQUIRED)

#### 2.1 sync-directives.py

**File**: `docs/directives-json/sync-directives.py`

**Lines that need updating:**

**Line 10** - Comment:
```python
- Directive Interactions (from directives-interactions.json)
```
**Action**: Update comment to reference directive_flow

**Line 19** - Comment:
```python
- Updated to use directives-interactions.json (replaces project_directive_graph.json)
```
**Action**: Update to mention directive_flow

**Line 67** - Variable:
```python
DIRECTIVE_INTERACTIONS_FILE = "directives-interactions.json"
```
**Action**: Change to `DIRECTIVE_FLOW_FILE = "directive-flow.json"`

**Line 306** - SQL Insert:
```python
INSERT OR IGNORE INTO directives_interactions
```
**Action**: Change to `INSERT OR IGNORE INTO directive_flow` with updated fields

**Lines 602-605** - Loading interactions:
```python
# Directive relationships from directives-interactions.json
if os.path.exists(DIRECTIVE_INTERACTIONS_FILE):
    print(f"📊 Linking interactions from {DIRECTIVE_INTERACTIONS_FILE}")
    interactions_data = load_json_file(DIRECTIVE_INTERACTIONS_FILE)
```
**Action**: Update to load directive-flow.json with new schema

**Line 717** - Query:
```python
FROM directives_interactions i
```
**Action**: Change to `FROM directive_flow`

**Line 784** - Guide generation:
```python
os.path.join(guides_dir, "directive-interactions.md")
```
**Action**: Update to "directive-flow.md"

**Status**: ⚠️ NEEDS UPDATE - This is the main sync script

---

#### 2.2 directives-interactions.json

**File**: Should exist as `docs/directives-json/directives-interactions.json`

**Action**:
1. Check if file exists
2. If exists, create new `directive-flow.json` with new schema
3. Convert data from old format to new format (see Format Conversion Reference below)
4. Archive old file to backups

**New Schema Format**:
```json
{
  "flows": [
    {
      "from_directive": "aifp_run",
      "to_directive": "aifp_status",
      "flow_type": "status_branch",
      "condition_key": null,
      "condition_value": null,
      "condition_description": "Always start with status",
      "priority": 100,
      "description": "Entry point always checks status"
    }
  ]
}
```

**Status**: ⚠️ NEEDS CREATION

---

#### 2.3 Task Documentation Files ✅ COMPLETED

**Files**:
- `docs/directives-json/Tasks/HELPER_FUNCTIONS_QUICK_REF.md` (lines 203-209)
- `docs/directives-json/Tasks/INTERACTIONS_TABLE_COVERAGE.md` (multiple references) ✅
- `docs/directives-json/Tasks/SQL_CLEANUP_CHECKLIST.md:211`
- `docs/directives-json/Tasks/DIRECTIVE_CLEANUP_TASK.md` (lines 166, 322) ✅

**Action Taken**:
- ✅ Added historical note to `DIRECTIVE_CLEANUP_TASK.md` with links to new docs
- ✅ Added clarifying note to `INTERACTIONS_TABLE_COVERAGE.md` (distinguishes project.interactions from directives_interactions)

**Status**: ✅ KEY DOCS UPDATED (others are reference docs, safe to leave as-is)

---

#### 2.5 Backup Files

**File**: `docs/directives-json/backups/directive-helper-interactions.json`
- Lines 2, 57, 61

**Status**: ✅ NO ACTION - Already in backups folder, keep for historical reference

---

### Category 3: Production Directive MD Files ✅ COMPLETED

#### 3.1 aifp_help.md ✅

**File**: `src/aifp/reference/directives/aifp_help.md`

**Lines 131, 141**:
```markdown
3. Queries `directive_flow` table for related directives (conditional flows, error paths)

> **Related directives** (from directive_flow table):
```

**Status**: ✅ UPDATED

---

#### 3.2 aifp_run.md

**File**: `src/aifp/reference/directives/aifp_run.md:12`

**Content**:
```markdown
`aifp_run` is the **gateway directive** and primary entry point for all AIFP
operations. It acts as a router and reminder system, ensuring AI applies AIFP
directives appropriately based on user intent. Every AIFP interaction begins
with this directive.
```

**Status**: ✅ NO ACTION - Generic description, not specific to interactions table

---

#### 3.3 user_preferences_learn.md

**File**: `src/aifp/reference/directives/user_preferences_learn.md:12`

**Content**: References `ai_interaction_log` (different table)

**Status**: ✅ NO ACTION - Not related to directives_interactions

---

### Category 4: Deprecated Registry Files

**Files**:
- `docs/helpers/registry-depricated/helpers_registry_project_orchestrators.json:173`
- `docs/helpers/registry-depricated/helpers_registry_mcp_orchestrators.json` (lines 57, 118, 139)

**Status**: ✅ NO ACTION - Files are already in "registry-depricated" folder

---

## 🎯 Action Plan

### Priority 1: Critical Updates (Blocks Production)

1. **Create directive-flow.json**
   - [ ] Design new format
   - [ ] Map project management directives to flows
   - [ ] Add initial flow entries (aifp_run → aifp_status, etc.)

2. **Update sync-directives.py**
   - [ ] Update constants (DIRECTIVE_FLOW_FILE)
   - [ ] Update SQL inserts for directive_flow table
   - [ ] Update queries from old table to new
   - [ ] Update comments and print statements

### Completed Items ✅

3. **Update aifp_help.md** ✅
   - [x] Change directives_interactions references to directive_flow
   - [x] Update query examples

4. **Update task documentation** ✅
   - [x] Add "Historical" notes to task docs
   - [x] Link to DIRECTIVE_NAVIGATION_SYSTEM.md

### Not Needed (Initial Development)

- ~~Create migration file~~ - Not needed, no released version to migrate from
- ~~Archive old files~~ - Will handle during directive-flow.json creation

---

## ✅ Verification Checklist

Current status:

- [x] Core schema has directive_flow table ✅
- [ ] sync-directives.py loads directive-flow.json (pending)
- [x] aifp_help.md references directive_flow ✅
- [ ] New directive-flow.json file exists with initial flows (pending)
- [x] All helper functions reference directive_flow ✅
- [ ] Test sync process with new schema (pending - blocked on directive-flow.json)

---

## 📝 Notes

### Safe References (No Action Needed)

These are NOT related to directives_interactions:

1. **Project database `interactions` table** (function dependencies)
   - `get_interactions_by_function` in orchestrators
   - This is separate from directives_interactions

2. **User interaction logs**
   - `ai_interaction_log` in user_preferences_learn.md
   - Completely different feature

3. **Deprecated registry files**
   - Already in "registry-depricated" folder
   - No action needed

### Format Conversion Reference

When creating directive-flow.json from directives-interactions.json:

**Old format**:
```json
{
  "source_directive": "aifp_run",
  "target_directive": "aifp_status",
  "relation_type": "triggers",
  "weight": 1,
  "description": "Always check status first"
}
```

**New format**:
```json
{
  "from_directive": "aifp_run",
  "to_directive": "aifp_status",
  "flow_type": "status_branch",
  "condition_key": null,
  "condition_value": null,
  "condition_description": "Always start with status",
  "priority": 100,
  "description": "Entry point always checks status"
}
```

**Mapping**:
- `source_directive` → `from_directive`
- `target_directive` → `to_directive`
- `relation_type: "triggers"` → `flow_type: "status_branch"` or `"completion_loop"` (depends on context)
- `weight` → `priority` (higher = preferred)
- `description` → `description`

---

**Last Updated**: 2025-01-15
**Schema Version**: 1.8
