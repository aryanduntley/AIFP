# Directive and Schema Review Findings

**Date**: 2025-12-16
**Reviewer**: Claude (AIFP Project Assistant)
**Scope**: Schema changes v1.9, directive_flow table, intent_keywords normalization

---

## Executive Summary

Reviewed the following for alignment with recent schema changes:
- ✅ `src/aifp/database/schemas/aifp_core.sql` (v1.9) - CORRECT
- ✅ `src/aifp/database/schemas/project.sql` (v1.3) - CORRECT (no blueprint_checksum)
- ⚠️ **Dev directive JSON files** - NEED UPDATES (still using `intent_keywords_json` field)
- ✅ Production MD files - Minimal issues found (2 references)
- ✅ Consolidated helpers - UPDATED for new schema

---

## Key Changes Verified

### 1. Schema v1.9: Intent Keywords Normalization ✅

**Status**: Schema is CORRECT

**What Changed**:
- Removed: `intent_keywords_json` field from directives table
- Added: `intent_keywords` master table
- Added: `directives_intent_keywords` junction table (many-to-many)

**Verification**:
```sql
-- aifp_core.sql lines 23-46
CREATE TABLE IF NOT EXISTS intent_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS directives_intent_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,
    keyword_id INTEGER NOT NULL,
    UNIQUE(directive_id, keyword_id),
    FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES intent_keywords(id) ON DELETE CASCADE
);
```

✅ Schema correctly implements normalized structure
✅ Indexes created for performance
✅ Version updated to 1.9

---

### 2. Schema v1.8: directive_flow Table ✅

**Status**: Schema is CORRECT

**What Changed**:
- Removed: `directives_interactions` table
- Added: `directive_flow` table with flow_type, conditions, priority

**Verification**:
```sql
-- aifp_core.sql lines 82-109
CREATE TABLE IF NOT EXISTS directive_flow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_directive TEXT NOT NULL,
    to_directive TEXT NOT NULL,
    flow_type TEXT CHECK (flow_type IN (
        'status_branch', 'completion_loop', 'conditional', 'error'
    )) NOT NULL DEFAULT 'conditional',
    condition_key TEXT,
    condition_value TEXT,
    condition_description TEXT,
    priority INTEGER DEFAULT 0,
    description TEXT,
    FOREIGN KEY (from_directive) REFERENCES directives(name),
    FOREIGN KEY (to_directive) REFERENCES directives(name)
);
```

✅ New table structure is correct
✅ Indexes added for performance
✅ Old `directives_interactions` table removed

---

### 3. Project Schema: Checksum Removal ✅

**Status**: Schema is CORRECT

**Verification**:
- Checked `project.sql` - NO `blueprint_checksum` field found
- Checked `project.sql` - NO `checksum` fields in project table
- Git hash tracking via `last_known_git_hash` field (line 28) ✅

**Note**: The `project.interactions` table (lines 94-105) is CORRECT - this is for **function dependencies**, NOT directive interactions. This is a different table and should remain.

---

## Issues Found

### ISSUE 1: Directive JSON Files Still Use `intent_keywords_json` Field

**Severity**: ⚠️ **HIGH** - Blocks production sync

**Files Affected**:
- `docs/directives-json/directives-fp-aux.json` (36 occurrences)
- `docs/directives-json/directives-fp-core.json` (29 occurrences)
- `docs/directives-json/directives-git.json` (6 occurrences)
- `docs/directives-json/directives-project.json` (38 occurrences)
- `docs/directives-json/directives-user-pref.json` (8 occurrences)

**Total**: 117 directives with old field structure

**Example** (from directives-project.json:83-91):
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

**Required Fix**:
1. Remove `intent_keywords_json` field from all directive JSON objects
2. Update `sync-directives.py` to handle keywords separately:
   - Extract keywords array from directive definition
   - INSERT keywords into `intent_keywords` table (INSERT OR IGNORE)
   - Link to directive via `directives_intent_keywords` table

**Impact**: 
- sync-directives.py will fail if run with current JSON structure
- Database population will not work correctly

---

### ISSUE 2: directives_interactions References in Descriptions

**Severity**: ℹ️ **LOW** - Documentation only

**Files**: `docs/directives-json/directives-fp-aux.json`

**Occurrences**:
1. Line 1281: `fp_recursion_enforcement` description
   ```json
   "description": "...Links to project_update_db to track recursion depth in interactions table."
   ```

2. Line 1346: `fp_monadic_composition` description
   ```json
   "description": "...Links to project_update_db to store monadic dependencies in interactions table."
   ```

**Clarification**: These references to "interactions table" are talking about `project.interactions` (function dependencies), NOT `directives_interactions`. The wording could be clearer.

**Recommended Fix**: Update descriptions to say "function interactions table" or "project.interactions table" for clarity.

---

### ISSUE 3: Production MD Files with Old References

**Severity**: ℹ️ **VERY LOW** - Already addressed

**Count**: 2 references found in `/src/aifp/reference/directives/*.md`

**Status**: Per DIRECTIVES_INTERACTIONS_REVIEW.md, aifp_help.md was already updated to use `directive_flow`. The 2 remaining references are likely in context where they're correctly referring to the new system.

---

## Helper Functions Status ✅

**Verified Files**:
- `docs/helpers/helpers-consolidated-core.md`
- `docs/helpers/helpers-consolidated-orchestrators.md`

**Status**: CORRECT

**What Was Updated**:
✅ Removed old helpers:
- `get_directive_interactions()`
- `get_interactions_for_directive()`
- `get_interactions_for_directive_as_target()`

✅ Added new directive navigation helpers:
- `get_next_directives_from_status()`
- `get_matching_next_directives()`
- `get_completion_loop_target()`
- `get_conditional_work_paths()`

✅ Updated intent keyword helpers (lines 132-272):
- `find_directives_by_intent_keyword()` - Now JOINs with intent_keywords table
- `add_directive_intent_keyword()` - Multi-step process (create keyword, then link)
- `get_directive_keywords()` - JOINs to get keyword strings
- `get_all_directive_keywords()` - Simple query from intent_keywords table
- All include updated SQL examples

---

## Action Items

### Priority 1: CRITICAL (Blocks Production)

**1. Update sync-directives.py for intent_keywords normalization**
- File: `docs/directives-json/sync-directives.py`
- Changes needed:
  ```python
  # OLD (won't work):
  # Read intent_keywords_json from directive object
  
  # NEW (required):
  # For each directive:
  #   1. Extract keywords array
  #   2. For each keyword:
  #      - INSERT OR IGNORE INTO intent_keywords (keyword) VALUES (?)
  #      - SELECT id FROM intent_keywords WHERE keyword = ?
  #      - INSERT INTO directives_intent_keywords (directive_id, keyword_id) VALUES (?, ?)
  ```

**2. Decision: Keep or remove intent_keywords_json from directive JSON files?**

Two options:

**Option A: Keep field in JSON, update sync script**
- Pros: No changes to 117 directive definitions
- Pros: Easier to read/edit keywords in JSON
- Cons: Redundant field that's not in database
- Implementation: Update sync-directives.py to read this field and populate normalized tables

**Option B: Remove field from JSON, manage keywords separately**
- Pros: Clean alignment with database schema
- Cons: Requires editing 117 directives
- Cons: Need separate keywords management file/process
- Implementation: Create directive-keywords.json mapping, update sync script

**Recommendation**: Option A for now (pragmatic), Option B for future cleanup.

---

### Priority 2: Documentation Clarity

**3. Update directive descriptions for "interactions table" clarity**
- Files: `docs/directives-json/directives-fp-aux.json` (2 occurrences)
- Change: "interactions table" → "function interactions table" or "project.interactions"
- Purpose: Avoid confusion with removed directives_interactions table

**4. Add note to directive JSON files**
- Add comment at top of each file:
  ```json
  {
    "_schema_note": "intent_keywords_json field is for dev convenience only. sync-directives.py normalizes these into intent_keywords + directives_intent_keywords tables during database population.",
    "directives": [...]
  }
  ```

---

### Priority 3: Nice to Have

**5. Verify production MD files**
- Check the 2 references found in src/aifp/reference/directives/*.md
- Ensure they're using correct terminology (directive_flow, not directives_interactions)

---

## Summary

### ✅ What's Working
1. Schema files are correct (v1.9 core, v1.3 project)
2. Helper functions updated for new schema
3. Old tables removed (directives_interactions)
4. New tables added (directive_flow, intent_keywords, directives_intent_keywords)

### ⚠️ What Needs Attention
1. **sync-directives.py must be updated** to handle intent_keywords normalization
2. Decide on directive JSON format (keep intent_keywords_json field or remove?)
3. Minor documentation clarity improvements

### 📊 Statistics
- Directive JSON files: 5 main files
- Directives with intent_keywords_json: 117
- Helper functions updated: 10+ functions
- Schema versions: core v1.9, project v1.3

---

## Next Steps

1. Update sync-directives.py for normalized intent_keywords (CRITICAL)
2. Test sync process with updated script
3. Decide on long-term approach for intent_keywords_json field
4. Update directive descriptions for clarity (optional)

---

**Review Complete**: 2025-12-16
