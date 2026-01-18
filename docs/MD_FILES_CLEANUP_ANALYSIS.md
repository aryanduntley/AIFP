# Directive MD Files - SQL & Scripts Cleanup Analysis

**Date**: 2026-01-17
**Status**: Analysis Complete
**Purpose**: Cross-reference JSON issues with corresponding MD files

---

## Executive Summary

**Finding**: YES, MD files have parallel issues with SQL queries and implementation details.

**Types of SQL in MD files**:
1. **Workflow specifications** - Direct SQL queries that should reference helpers (⚠️ CRITICAL)
2. **Implementation examples** - Python code showing how operations work (⚠️ NEEDS UPDATE)
3. **Documentation comments** - SQL in workflow explanations (ℹ️ ADD CLARIFICATION)

**aifp.scripts**: ✅ NO references found in MD files (only in JSON)

---

## Category 1: Workflow Specifications (CRITICAL - Must Match JSON)

These are directive workflow specifications that should match their JSON counterparts.

### project_file_write.md - Line 65

**MD File**:
```markdown
- **Query**: `SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='project_file_write' AND active=1`
```

**JSON File** (directives-project.json:663):
```json
"query": "SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='project_file_write' AND active=1"
```

**Issue**: ✅ EXACT MATCH - Both have same SQL query
**Fix Required**: Update BOTH files to use helper reference
**Replace with** (both files):
```markdown
- **Helper**: `get_directive_preferences`
- **Parameters**: `directive_name='project_file_write'`
- **Returns**: Dictionary of active preferences {preference_key: preference_value}
```

---

### project_task_decomposition.md - Line 66

**MD File**:
```markdown
- **Query**: `SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='project_task_decomposition' AND active=1`
```

**JSON File** (directives-project.json:464):
```json
"query": "SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='project_task_decomposition' AND active=1"
```

**Issue**: ✅ EXACT MATCH - Both have same SQL query
**Fix Required**: Update BOTH files to use helper reference
**Replace with** (both files):
```markdown
- **Helper**: `get_directive_preferences`
- **Parameters**: `directive_name='project_task_decomposition'`
- **Returns**: Dictionary of active preferences {preference_key: preference_value}
```

---

## Category 2: Implementation Examples (NEEDS UPDATE)

These are Python code examples showing how operations work. Should be updated to show orchestrator pattern.

### project_init.md - Lines 245-290

**Found**: Multiple Python code blocks with direct database operations:
- Line 247: `conn = sqlite3.connect(...)`
- Line 248: `conn.executescript(schema_sql)`
- Line 251-254: `conn.execute("""INSERT INTO project...""")`
- Line 259-266: `conn.execute("""INSERT INTO completion_path...""")`
- Line 277-278: User preferences database creation
- Line 281-287: `conn.execute("""INSERT INTO tracking_settings...""")`

**Issue**: Shows implementation details (direct SQL execution) rather than orchestrator pattern

**Context**: This is "Step 5: Initialize project.db" and "Step 6: Initialize user_preferences.db"

**Fix Required**: Update to show orchestrator pattern

**Replace with**:
```markdown
**Step 5: Initialize Project Databases**

System calls `project_init` orchestrator which handles database initialization internally:

**project.db initialization** (executed directly in orchestrator):
1. Load schema from `schemas/project.sql`
2. Create database and execute schema
3. Insert project metadata (name, purpose, goals)
4. Execute `initialization/standard_infrastructure.sql` (6 standard entries with empty values)
5. Insert default completion_path

**user_preferences.db initialization** (executed directly in orchestrator):
1. Load schema from `schemas/user_preferences.sql`
2. Create database and execute schema
3. Insert default tracking_settings (all disabled)

**Standard infrastructure entries created**:
- source_directory (empty)
- primary_language (empty)
- build_tool (empty)
- package_manager (empty)
- test_framework (empty)
- runtime_version (empty)

**AI's role post-init**: Populate empty infrastructure values using:
- `detect_primary_language()` - detect from codebase
- `detect_build_tool()` - detect from config files
- User confirmation prompts
- `update_project_entry('infrastructure', id, {'value': '...'})`
```

**Note**: Remove all Python `conn.execute()` examples - these are implementation details hidden in orchestrator

---

### project_update_db.md - Lines 283, 311, 429

**Found**:
- Line 283: `existing = conn.execute("SELECT id FROM files WHERE path=?", (path,)).fetchone()`
- Line 311: `target_func = conn.execute("SELECT id FROM functions WHERE name=?", (dep_name,)).fetchone()`
- Line 429: `SELECT COUNT(*) FROM files WHERE path='src/calc.py';`

**Issue**: Shows direct database operations instead of helpers

**Fix Required**: Update to reference helpers

**Replace line 283**:
```markdown
existing = get_from_project_where('files', {'path': path})
```

**Replace line 311**:
```markdown
target_func = get_from_project_where('functions', {'name': dep_name})
```

**Replace line 429** (in example):
```markdown
# Check if file exists
files = get_from_project_where('files', {'path': 'src/calc.py'})
file_exists = len(files) > 0
```

---

### project_notes_log.md - Lines 471, 494, 520, 608, 622, 634, 649

**Found**: Multiple `query_db()` examples showing SQL queries

Examples:
- Line 471: `function_id = query_db("SELECT id FROM functions WHERE name='calculate_total'")[0]`
- Line 494: `function_id = query_db("SELECT id FROM functions WHERE name=?", (function_name,))`
- Line 608: `result = query_db("SELECT * FROM notes WHERE note_type='clarification'")`
- Line 622: `result = query_db("SELECT * FROM notes WHERE directive_name='project_file_write'")`

**Issue**: Shows generic `query_db()` instead of specific helpers

**Fix Required**: Update examples to use specific helpers

**Replace examples**:
```markdown
# Get function ID by name
functions = get_from_project_where('functions', {'name': 'calculate_total'})
function_id = functions[0]['id'] if functions else None

# Get notes by type
notes = get_from_project_where('notes', {'note_type': 'clarification'})

# Get notes by directive
notes = get_from_project_where('notes', {'directive_name': 'project_file_write'})

# Get notes by severity
notes = get_from_project_where('notes', {'severity': 'error'})
```

**Add note**:
```markdown
**Note**: Examples show helper functions for clarity. Direct SQL queries should not be used in directives.
```

---

## Category 3: Documentation Comments (ADD CLARIFICATION)

These are SQL queries in workflow explanations or comments - for documentation purposes.

### git_detect_external_changes.md - Lines 55, 159, 164, 166, 202

**Found**: SQL in workflow steps and comments showing what happens

Examples:
- Line 55: `1. **Query database** - SELECT last_known_git_hash FROM project WHERE id=1`
- Line 159: `# 1. Query: SELECT last_known_git_hash FROM project → "abc123"`
- Line 164: `# 5. Query: SELECT themes FROM ... WHERE file='src/calc.py'`

**Issue**: Documentation shows SQL for clarity but doesn't clarify these are conceptual

**Fix Required**: Add clarification that helpers are used

**Update examples**:
```markdown
1. **Query database using helper** - `get_project()` returns project metadata including `last_known_git_hash`

# 1. Call helper: get_project() → {last_known_git_hash: "abc123", ...}
# 5. Get file themes: get_from_project_where('files', {'path': 'src/calc.py'}) → includes themes
```

**Add note at top of workflow**:
```markdown
**Note**: Workflow examples show conceptual SQL for clarity. Actual implementation uses helper functions.
```

---

### git_sync_state.md - Lines 165, 185, 219, 240, 444, 450, 469

**Found**: Similar documentation SQL in workflow examples

**Fix Required**: Same as git_detect_external_changes.md - add clarification and update to helper references

---

### git_create_branch.md - Lines 185, 416

**Found**:
- Line 185: `#    - Query: SELECT MAX(...) FROM work_branches WHERE user_name='alice-smith'`
- Line 416: `result = query_db("SELECT branch_name FROM work_branches WHERE user_name='alice'")`

**Fix Required**:
```markdown
# Line 185: Call helper: get_max_branch_number('alice-smith')
# Line 416:
branches = get_from_project_where('work_branches', {'user_name': 'alice'})
branch_names = [b['branch_name'] for b in branches]
```

---

### project_sidequest_create.md - Line 428

**Found**:
```
        SELECT * FROM sidequests
```

**Context**: In example output showing database state

**Fix Required**: Add note that examples show data conceptually
```markdown
**Note**: Examples show database state for clarity. Access via `get_from_project_where('sidequests', {})` helper.
```

---

## Summary by File

### Files Needing Updates

| File | Lines | Issue Type | Priority |
|------|-------|------------|----------|
| **project_file_write.md** | 65 | Workflow SQL query | ⚠️ CRITICAL |
| **project_task_decomposition.md** | 66 | Workflow SQL query | ⚠️ CRITICAL |
| **project_init.md** | 245-290 | Implementation examples | HIGH |
| **project_update_db.md** | 283, 311, 429 | Implementation examples | HIGH |
| **project_notes_log.md** | 471, 494, 520, 608, 622, 634, 649 | Example code | MEDIUM |
| **git_detect_external_changes.md** | 55, 159, 164, 166, 202 | Documentation SQL | MEDIUM |
| **git_sync_state.md** | 165, 185, 219, 240, 444, 450, 469 | Documentation SQL | MEDIUM |
| **git_create_branch.md** | 185, 416 | Documentation/examples | MEDIUM |
| **git_detect_conflicts.md** | 475 | Example code | LOW |
| **git_merge_branch.md** | 529, 530, 555 | Example code | LOW |
| **project_sidequest_create.md** | 428 | Example output | LOW |

---

## aifp.scripts References in MD Files

**Search Results**: ✅ **NONE FOUND**

The `aifp.scripts.init_aifp_project` references only exist in JSON files, not in MD files.

**Conclusion**: MD files don't need cleanup for aifp.scripts - only JSON files do.

---

## Consistency Check: JSON ↔ MD Mapping

### Verified Matches

| JSON Line | MD File | MD Line | Status |
|-----------|---------|---------|--------|
| directives-project.json:464 | project_task_decomposition.md | 66 | ✅ MATCH |
| directives-project.json:663 | project_file_write.md | 65 | ✅ MATCH |
| directives-project.json:1911 | - | - | ❌ NO MD EQUIVALENT |
| directives-project.json:2707 | - | - | ❌ NO MD EQUIVALENT |

### JSON Queries Without MD Equivalents

Many JSON queries are internal workflow logic that don't appear in MD files:
- Infrastructure query (line 1911)
- Task count queries (lines 2707, 2813)
- Milestone queries (lines 2997, 3016)

**These are OK** - MD files are high-level guidance, JSON has implementation details.

---

## Action Items

### Phase 1: Critical Workflow Updates (Must Match JSON)
- [ ] **project_file_write.md** line 65 - Replace SQL query with helper reference
- [ ] **project_task_decomposition.md** line 66 - Replace SQL query with helper reference
- [ ] Verify updates match corresponding JSON changes

### Phase 2: Implementation Examples (Remove Direct SQL)
- [ ] **project_init.md** lines 245-290 - Update to orchestrator pattern, remove conn.execute examples
- [ ] **project_update_db.md** lines 283, 311, 429 - Replace with helper calls
- [ ] **project_notes_log.md** lines 471, 494, 520, 608, 622, 634, 649 - Update to helper examples

### Phase 3: Documentation Clarifications
- [ ] **git_detect_external_changes.md** - Add note about helpers, update SQL comments
- [ ] **git_sync_state.md** - Add note about helpers, update SQL comments
- [ ] **git_create_branch.md** - Update examples to use helpers
- [ ] **project_sidequest_create.md** - Add clarification note

### Phase 4: Verification
- [ ] Cross-check every JSON query change has corresponding MD update (if applicable)
- [ ] Ensure MD examples don't contradict JSON specifications
- [ ] Verify no direct SQL remains in workflow specifications

---

## Update Pattern for MD Files

### Pattern 1: Workflow SQL → Helper Reference

**Before**:
```markdown
- **Query**: `SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='X' AND active=1`
```

**After**:
```markdown
- **Helper**: `get_directive_preferences`
- **Parameters**: `directive_name='X'`
- **Returns**: Dictionary of active preferences {preference_key: preference_value}
- **Note**: See helpers-user-preferences.json for complete specification
```

### Pattern 2: Implementation Example → Orchestrator/Helper

**Before**:
```python
conn = sqlite3.connect("project.db")
conn.execute("SELECT * FROM table WHERE condition=?", (value,))
```

**After**:
```markdown
**System calls orchestrator**: `project_init` handles database operations internally

**What happens** (internal to orchestrator):
1. Load schema and create database
2. Execute initialization SQL
3. Populate standard data

**AI's role**: Use helpers to interact with data after initialization
```

### Pattern 3: Documentation SQL → Helper + Clarification

**Before**:
```markdown
# 1. Query: SELECT last_known_git_hash FROM project
```

**After**:
```markdown
# 1. Get project data: get_project() → includes last_known_git_hash

**Note**: Conceptual SQL shown for clarity - actual implementation uses helpers.
```

---

## Priority Summary

**CRITICAL** (Must be consistent with JSON):
- project_file_write.md line 65
- project_task_decomposition.md line 66

**HIGH** (Implementation examples need updates):
- project_init.md (major orchestrator pattern update)
- project_update_db.md

**MEDIUM** (Documentation clarity):
- project_notes_log.md
- git_detect_external_changes.md
- git_sync_state.md
- git_create_branch.md

**LOW** (Minor clarifications):
- git_detect_conflicts.md
- git_merge_branch.md
- project_sidequest_create.md

---

## Next Steps

1. ✅ Complete SQL and aifp.scripts cleanup in JSON files
2. ✅ Update corresponding MD files in parallel
3. ✅ Verify JSON ↔ MD consistency for all changes
4. Run consistency check script (if available)
5. Test directives with updated documentation
