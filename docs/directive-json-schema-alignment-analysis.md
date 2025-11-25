# Directive JSON ↔ aifp_core.db Schema Alignment Analysis
**Date**: 2025-11-24
**Purpose**: Ensure directive JSON files perfectly align with database schema before updates

---

## Executive Summary

**Overall Status**: 🟡 **GOOD with minor adjustments needed**

### ✅ What's Working Well
1. Directive structure matches schema (9/11 fields correct)
2. directives-interactions.json perfectly aligned with directives_interactions table
3. directive-helper-interactions.json perfectly aligned with directive_helpers table
4. Separate JSON files for each concern (directives, interactions, helpers)

### 🟡 Issues Found
1. **Category structure mismatch** - embedded object needs extraction
2. **available_helpers orphaned data** - not used, should be removed
3. **Helper file consolidation needed** - multiple overlapping sources

---

## Detailed Schema Alignment

### 1. directives Table

#### Schema Requirements (aifp_core.sql)
```sql
CREATE TABLE IF NOT EXISTS directives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Auto-generated
    name TEXT NOT NULL UNIQUE,                      -- Required
    type TEXT NOT NULL CHECK (type IN (...)),       -- Required with constraints
    level INTEGER DEFAULT NULL,                     -- Optional (project only)
    parent_directive TEXT REFERENCES directives(name), -- Optional
    description TEXT,                               -- Optional
    workflow JSON NOT NULL,                         -- Required
    md_file_path TEXT,                              -- Optional
    roadblocks_json TEXT,                           -- Optional
    intent_keywords_json TEXT,                      -- Optional
    confidence_threshold REAL DEFAULT 0.5           -- Optional with default
);
```

#### Current JSON Structure
```json
{
  "name": "aifp_run",                    // ✓ Matches
  "type": "project",                     // ✓ Matches
  "level": 0,                            // ✓ Matches
  "parent_directive": null,              // ✓ Matches
  "category": {                          // ❌ MISMATCH - see below
    "name": "orchestration",
    "description": "Gateway..."
  },
  "description": "Gateway...",           // ✓ Matches
  "md_file_path": "directives/...",      // ✓ Matches
  "workflow": {...},                     // ✓ Matches
  "roadblocks_json": [...],              // ✓ Matches
  "intent_keywords_json": [...],         // ✓ Matches
  "confidence_threshold": 1.0            // ✓ Matches
}
```

#### Issues

##### Issue 1: Category Embedded as Object
**Current**:
```json
"category": {
  "name": "orchestration",
  "description": "Gateway and reminder..."
}
```

**Problem**:
- Categories belong in separate `categories` table
- Relationship belongs in `directive_categories` junction table
- Can't have nested object in directive JSON if sync-directives.py processes flat structure

**Solution Required**:
```json
// In directive JSON:
"category_name": "orchestration",  // Simple string reference

// In separate categories.json (new file):
[
  {
    "name": "orchestration",
    "description": "Gateway and reminder for AIFP directive application"
  },
  {
    "name": "task_management",
    "description": "Task creation, updates, and lifecycle management"
  }
]

// Junction mapping automatic (directive_name → category_name)
```

##### Issue 2: available_helpers Orphaned Data
**Current**:
```json
"workflow": {
  "branches": [{
    "details": {
      "available_helpers": [
        "get_all_directives",
        "get_directive",
        ...
      ]
    }
  }]
}
```

**Problem**:
- sync-directives.py doesn't read this
- Not in database schema
- Redundant with directive-helper-interactions.json

**Solution**: **REMOVE** all `available_helpers` arrays

---

### 2. directive_categories Junction Table

#### Schema Requirements
```sql
CREATE TABLE IF NOT EXISTS directive_categories (
    directive_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (directive_id, category_id),
    FOREIGN KEY (directive_id) REFERENCES directives(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

#### Current State
**Missing**: No explicit directive-categories.json or mapping file

**Solution Needed**:

**Option A**: Extract during sync (simpler)
```python
# In sync-directives.py
for directive in directives_json:
    category_name = directive.get('category_name')
    # or extract from nested: directive['category']['name']
    # Create/get category, link to directive
```

**Option B**: Separate mapping file (more explicit)
```json
// directive-categories.json
{
  "mappings": [
    {
      "directive_name": "aifp_run",
      "category_name": "orchestration"
    },
    {
      "directive_name": "project_task_create",
      "category_name": "task_management"
    }
  ]
}
```

**Recommendation**: **Option A** - Extract during sync from flat field

---

### 3. directives_interactions Table

#### Schema Requirements
```sql
CREATE TABLE IF NOT EXISTS directives_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_directive_id INTEGER NOT NULL,
    target_directive_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL CHECK (relation_type IN (...)),
    weight INTEGER DEFAULT 1,
    description TEXT,
    active BOOLEAN DEFAULT 1,
    FOREIGN KEY (source_directive_id) REFERENCES directives(id),
    FOREIGN KEY (target_directive_id) REFERENCES directives(id)
);
```

#### Current State: directives-interactions.json
```json
[
  {
    "source": "aifp_run",
    "target": "project_init",
    "relation_type": "triggers",
    "description": "aifp_run triggers project_init...",
    "weight": 1,
    "active": true
  }
]
```

**Status**: ✅ **PERFECT ALIGNMENT**
- All required fields present
- Uses directive names (resolved to IDs during sync)
- Ready for database population

---

### 4. directive_helpers Junction Table

#### Schema Requirements
```sql
CREATE TABLE IF NOT EXISTS directive_helpers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,
    helper_function_id INTEGER NOT NULL,
    execution_context TEXT,
    sequence_order INTEGER DEFAULT 0,
    is_required BOOLEAN DEFAULT 1,
    parameters_mapping JSON,
    description TEXT,
    UNIQUE(directive_id, helper_function_id, execution_context),
    FOREIGN KEY (directive_id) REFERENCES directives(id),
    FOREIGN KEY (helper_function_id) REFERENCES helper_functions(id)
);
```

#### Current State: directive-helper-interactions.json
```json
{
  "mappings": [
    {
      "directive_name": "aifp_run",
      "helper_name": "get_all_directives",
      "execution_context": "`aifp_run`, AI session initialization",
      "sequence_order": 0,
      "is_required": true,
      "description": "aifp_run uses get_all_directives",
      "source": "helper_reference_used_by"
    }
  ]
}
```

**Status**: ✅ **PERFECT ALIGNMENT**
- All required fields present
- Uses string names (resolved during sync)
- Ready for database population

---

### 5. helper_functions Table

#### Schema Requirements
```sql
CREATE TABLE IF NOT EXISTS helper_functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    file_path TEXT,
    parameters JSON,
    purpose TEXT,
    error_handling TEXT,
    is_tool BOOLEAN DEFAULT 0,
    is_sub_helper BOOLEAN DEFAULT 0,
    return_statements JSON,          -- NEW field
    target_database TEXT             -- NEW field
);
```

#### Current State: Multiple Sources (PROBLEM)

**Source 1**: docs/directives-json/helpers_parsed.json
```json
[
  {
    "name": "get_all_directives",
    "file_path": "src/aifp/helpers/mcp.py",
    "purpose": "Retrieve all directives...",
    "parameters": null,
    "error_handling": "Return empty list...",
    "used_by": "`aifp_run`, AI session initialization",
    "is_tool": true,
    "is_sub_helper": false
  }
]
```
**Missing**: `return_statements`, `target_database`

**Source 2-5**: docs/helpers/info-helpers-*.txt (4 files)
- More complete
- Include target_database info
- Have return_statements guidance
- Better organized by database

**Problem**: Multiple sources of truth, inconsistency

---

## Helper File Consolidation Analysis

### Current State (Fragmented)

#### Source of Truth (Correct)
1. ✅ `docs/helpers/info-helpers-core.txt` - MCP/core helpers
2. ✅ `docs/helpers/info-helpers-project.txt` - Project database helpers
3. ✅ `docs/helpers/info-helpers-user-settings.txt` - User preferences helpers
4. ✅ `docs/helpers/info-helpers-user-custom.txt` - User directives helpers

#### To Consolidate/Remove (Confusion)
1. ❌ `docs/helpers/helper-architecture.md` - Architectural docs (move to separate docs folder)
2. ❌ `docs/helpers/helper-tool-classification.md` - Classification docs (move to separate docs folder)
3. ❌ `docs/helpers/generic-tools-mcp.md` - Redundant with info-helpers-core.txt
4. ❌ `docs/helpers/generic-tools-project.md` - Redundant with info-helpers-project.txt
5. ❌ `docs/helpers/helper-functions-reference.md` - Old reference, superseded by info-helpers-*.txt
6. 🟡 `docs/directives-json/directive-helper-interactions.json` - **KEEP** (used by sync-directives.py)
7. 🟡 `docs/directives-json/helpers_parsed.json` - **UPDATE** from info-helpers-*.txt sources

---

## Recommended Changes

### Priority 1: Fix Directive JSON Structure

#### Change 1: Flatten Category
**Before**:
```json
{
  "name": "aifp_run",
  "category": {
    "name": "orchestration",
    "description": "Gateway..."
  }
}
```

**After**:
```json
{
  "name": "aifp_run",
  "category_name": "orchestration"
}
```

**Impact**: All directive JSON files (116+ directives)
**Method**: Can be done programmatically with jq

```bash
jq '.[].category = .[].category.name' directives-project.json
```

#### Change 2: Remove available_helpers
**Before**:
```json
{
  "workflow": {
    "branches": [{
      "details": {
        "available_helpers": ["get_all_directives", ...]
      }
    }]
  }
}
```

**After**:
```json
{
  "workflow": {
    "branches": [{
      "details": {
        // available_helpers removed
      }
    }]
  }
}
```

**Impact**: directives-project.json and others with available_helpers
**Method**: Part of the 5-at-a-time review we're doing

---

### Priority 2: Create categories.json

**New File**: docs/directives-json/categories.json
```json
[
  {
    "name": "orchestration",
    "description": "Gateway and reminder for AIFP directive application"
  },
  {
    "name": "initialization",
    "description": "Project setup and initialization workflows"
  },
  {
    "name": "task_management",
    "description": "Task creation, updates, and lifecycle management"
  }
]
```

**Source**: Extract from existing directive JSON files
**Method**:
```bash
jq -r '.[].category | "\(.name)|\(.description)"' directives-*.json | sort -u
```

---

### Priority 3: Update helpers_parsed.json

**Source Data**: Consolidate from info-helpers-*.txt files
**Add Missing Fields**:
- `return_statements` JSON
- `target_database` TEXT

**Process**:
1. Parse info-helpers-*.txt files
2. Generate complete JSON with all schema fields
3. Replace helpers_parsed.json

---

### Priority 4: Helper File Cleanup

#### Move to docs/architecture/
- helper-architecture.md
- helper-tool-classification.md

#### Remove (Redundant)
- generic-tools-mcp.md → superseded by info-helpers-core.txt
- generic-tools-project.md → superseded by info-helpers-project.txt
- helper-functions-reference.md → superseded by info-helpers-*.txt

#### Keep & Update
- directive-helper-interactions.json (used by sync)
- helpers_parsed.json (regenerate from info-helpers-*.txt)

---

## Updated Workflow for Directive Review

### Before Processing Each Batch
1. **Check category structure**: Ensure category_name is flat string
2. **Remove available_helpers**: Not in schema, not used
3. **Verify all schema fields present**: name, type, level, etc.

### Files to Generate Before Sync
1. **categories.json** - Extract unique categories
2. **helpers_parsed.json** - Regenerate from info-helpers-*.txt
3. **Keep as-is**:
   - directives-*.json (after updates)
   - directives-interactions.json
   - directive-helper-interactions.json

---

## Validation Checklist

Before running sync-directives.py, verify:

### Directive JSON Files
- [ ] All directives have flat `category_name` field
- [ ] No nested `category` objects
- [ ] No `available_helpers` arrays
- [ ] All required fields present (name, type, workflow, etc.)
- [ ] workflow is valid JSON
- [ ] roadblocks_json is array (if present)
- [ ] intent_keywords_json is array (if present)

### Supporting JSON Files
- [ ] categories.json exists with all unique categories
- [ ] directives-interactions.json has all relationships
- [ ] directive-helper-interactions.json has all mappings
- [ ] helpers_parsed.json has complete helper data with new fields

### Helper Source Files
- [ ] info-helpers-*.txt files are source of truth (4 files)
- [ ] Redundant helper docs moved/removed
- [ ] No conflicting helper definitions

---

## sync-directives.py Updates Needed

The sync script should:

1. **Load categories first** (from categories.json)
2. **Resolve category_name** to category_id when inserting directives
3. **Populate directive_categories** junction table
4. **Handle helpers** with new fields (return_statements, target_database)
5. **Validate** all foreign key relationships before commit

---

## Action Items

### Immediate (Before Batch 1)
1. [ ] Create categories.json from existing directives
2. [ ] Update directive JSON structure (flatten category)
3. [ ] Regenerate helpers_parsed.json from info-helpers-*.txt
4. [ ] Move/remove redundant helper docs
5. [ ] Update sync-directives.py to handle categories

### During Batch Review (Each 5 Directives)
1. [ ] Verify category_name is flat string
2. [ ] Remove available_helpers
3. [ ] Check all schema fields present
4. [ ] Validate JSON syntax

### After All Batches Complete
1. [ ] Validate all JSON files before sync
2. [ ] Run sync-directives.py with validation mode
3. [ ] Verify database integrity
4. [ ] Test directive retrieval

---

**Last Updated**: 2025-11-24
**Status**: Analysis Complete - Ready for Action Items
