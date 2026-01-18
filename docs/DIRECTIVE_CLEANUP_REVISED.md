# Directive Cleanup - Revised Requirements

**Date**: 2026-01-18
**Status**: Ready for Implementation
**Purpose**: Clear documentation of what exists, what's needed, and cleanup approach

---

## Summary

**Total SQL Queries to Remove**: 24 across 4 JSON directive files
**Total aifp.scripts References to Remove**: 4 in project_init directive
**New Helpers Actually Needed**: 2 (not 14!)
**Cleanup Approach**: Replace hardcoded SQL/helpers with general guidance

---

## Part 1: What We Already Have ✅

### Orchestrators (helpers-orchestrators.json)
- `aifp_run` - Main entry point, bundles session data
- `aifp_status` - Comprehensive status with infrastructure_status
- `get_current_progress` - Current work state
- `get_work_context` - Work context for active items
- `validate_initialization` - Validates project setup ✅ ALREADY EXISTS

### Task Management (helpers-project-6.json, helpers-project-7.json)
- `get_incomplete_completion_paths` - All non-completed paths ✅
- `get_next_completion_path` - Next incomplete path ✅
- `get_incomplete_milestones` - All non-completed milestones ✅
- `get_milestones_by_status` - Filtered by status ✅
- `get_incomplete_tasks_by_milestone` - Open tasks with subtasks ✅
- `get_incomplete_tasks` - All incomplete tasks ✅
- `get_tasks_by_milestone` - All tasks for milestone ✅

### User Preferences (helpers-settings.json)
- `load_directive_preferences` - Loads preferences for a directive ✅
- `add_directive_preference` - Add/update preferences ✅

### Git Collaboration (helpers-git.json)
- `get_current_commit_hash` - Current commit ✅
- `get_current_branch` - Current branch ✅
- `create_user_branch` - Creates work branch ✅
- `list_active_branches` - List active branches ✅
- Full merge and conflict resolution helpers ✅

### Generic CRUD (helpers-project-1.json)
- `get_from_project` - Get by ID(s) ✅
- `get_from_project_where` - Flexible filtering ✅
- `update_project_entry` - Update any table ✅
- `query_project` - Custom SQL queries ✅

### Infrastructure (helpers-project-1.json)
- `get_infrastructure_by_type` - Get infrastructure by type ✅

---

## Part 2: What We Actually Need ❌

### Critical - Must Create

**1. project_init (Orchestrator)**
- **File**: `docs/helpers/json/helpers-orchestrators.json`
- **Purpose**: Main initialization orchestrator
- **Why**: Coordinates all initialization steps (databases, directories, blueprint, state DB)
- **Referenced by**: project_init directive
- **Status**: ✅ Documented in INFRASTRUCTURE_GOALS.md and NEW_HELPERS_SPECIFICATIONS.md
- **Implementation**: One-time operations (mkdir, DB creation) happen directly in orchestrator code
- **Sub-operations**:
  - Create `.aifp-project/` directories (direct os.makedirs)
  - Initialize `project.db` with schema + standard_infrastructure.sql
  - Initialize `user_preferences.db` with schema
  - Generate blueprint (if template exists)
  - Initialize state database (calls `initialize_state_database`)
  - Validate setup (calls `validate_initialization`)

**2. get_all_infrastructure**
- **File**: `docs/helpers/json/helpers-project-1.json`
- **Purpose**: Get all infrastructure entries (including empty standard entries)
- **Why**: Used by `aifp_run(is_new_session=true)` to bundle infrastructure in session context
- **Used by**: aifp_run, aifp_status
- **Status**: ✅ Documented in INFRASTRUCTURE_GOALS.md
- **Note**: Could use `get_from_project_where("infrastructure", {})` but dedicated helper is clearer

---

## Part 3: What We DON'T Need ✅ (AI Natural Behavior)

These are NOT helpers - they are AI natural capabilities:

**1. ❌ detect_primary_language**
- **Why not**: AI scans file extensions and analyzes code naturally
- **Where it happens**: During/after project_init, AI detects language and updates infrastructure
- **Approach**: Directive instructs AI to detect language, not coded logic

**2. ❌ detect_build_tool**
- **Why not**: AI checks for Cargo.toml, package.json, Makefile naturally
- **Where it happens**: During/after project_init, AI detects build tool
- **Approach**: Directive instructs AI to detect build tool, not coded logic

**3. ❌ scan_for_oop_patterns**
- **Why not**: AI does this as part of FP coding principles
- **Where it happens**: During project_init, AI scans codebase naturally
- **Approach**: If OOP detected, AI notifies user that AIFP is not for OOP projects

**4. ❌ generate_blueprint_from_template**
- **Why not**: Only happens once during init
- **Where it happens**: Directly in `project_init` orchestrator code
- **Approach**: Load template, replace placeholders, write file (simple operation)

**5. ❌ Count Helpers**
- `count_incomplete_tasks`
- `count_incomplete_subtasks`
- `count_incomplete_completion_paths`

**Why not**: We already have getters that return full data
- Use `get_incomplete_tasks()` and count results
- Use `get_incomplete_milestones()` and count results
- Counting alone is not useful - need context of what's incomplete

**6. ❌ get_next_milestone**
**Why not**: We already have `get_incomplete_milestones()` which returns all incomplete milestones ordered properly

**7. ❌ get_completion_path_for_milestone**
**Why not**: Use `get_from_project_where("milestones", {"id": milestone_id})` to get milestone with completion_path_id, then get the path

**8. ❌ get_max_branch_number**
**Why not**: Use `get_from_project_where("work_branches", {"user_name": "..."})` and find max in results

**9. ❌ get_user_directives_by_status**
**Why not**: Use `get_from_project_where("user_directives", {"status": "active"})` for each status

**10. ❌ get_directive_execution_stats**
**Why not**: Use `get_from_project_where("directive_executions", {})` and aggregate in AI logic

---

## Part 4: Files to Create

### 1. standard_infrastructure.sql ✅ REQUIRED
**Path**: `src/aifp/database/initialization/standard_infrastructure.sql`
**Purpose**: Pre-populate standard infrastructure entries with empty values
**Content**:
```sql
-- Standard Infrastructure Entries
-- Populated during project initialization with empty values
-- AI detects and populates values after initialization

INSERT INTO infrastructure (type, value, description) VALUES
  ('source_directory', '', 'Primary source code directory (e.g., src, lib, app)'),
  ('primary_language', '', 'Main programming language (e.g., Python 3.11, Rust 1.75, Node 18)'),
  ('build_tool', '', 'Primary build tool (e.g., cargo, npm, make, maven, gradle)'),
  ('package_manager', '', 'Package/dependency manager (e.g., pip, npm, cargo, maven)'),
  ('test_framework', '', 'Testing framework (e.g., pytest, jest, cargo test, junit)'),
  ('runtime_version', '', 'Language runtime or compiler version (e.g., Python 3.11.2, rustc 1.75.0)');
```

### 2. Add to helpers-orchestrators.json
- Add `project_init` orchestrator definition
- Update `aifp_run` to include infrastructure_data in session bundle

### 3. Add to helpers-project-1.json
- Add `get_all_infrastructure` helper definition

---

## Part 5: SQL Cleanup Approach

**CRITICAL**: Do NOT hardcode helper names in directives. Helper names change frequently.

### OLD Approach (Wrong ❌)
```json
{
  "if": "need_tasks",
  "then": "load_tasks",
  "details": {
    "helper": "get_incomplete_tasks_by_milestone",
    "parameters": {"milestone_id": "from_context"}
  }
}
```

### NEW Approach (Correct ✅)
```json
{
  "if": "need_tasks",
  "then": "load_tasks",
  "details": {
    "action": "query_helpers_database",
    "guidance": "Query aifp_core.db helper_functions table for project database helpers. Search by target_database='project' and purpose keywords: 'task', 'incomplete', 'milestone'. Use the most specific helper available.",
    "note": "Helper names are subject to change. Always query the helper_functions table to find current helpers rather than hardcoding helper names."
  }
}
```

### General Guidance Template
```json
{
  "action": "query_helpers_database",
  "guidance": "Search helper_functions table by target_database='[database]' and purpose keywords: '[keyword1]', '[keyword2]', '[keyword3]'. Filter by is_tool=true for directly callable helpers.",
  "note": "Do not hardcode helper names. Query database for current helpers."
}
```

---

## Part 6: Directive Cleanup Order

### Phase 1: Infrastructure Foundation (CRITICAL)
1. ✅ Create `standard_infrastructure.sql`
2. ✅ Add `get_all_infrastructure` to helpers-project-1.json
3. ✅ Add `project_init` orchestrator to helpers-orchestrators.json
4. ✅ Update `aifp_run` in helpers-orchestrators.json (add infrastructure_data)

### Phase 2: directives-project.json SQL Cleanup (17 queries)
Replace SQL queries with general guidance:

**Lines to Update**:
- Line 464, 663: Directive preferences → general guidance to search for preference helpers
- Line 939: Tracking settings → general guidance to search for settings helpers
- Line 949: All functions → general guidance to use project CRUD helpers
- Line 1911: Infrastructure query ⚠️ CRITICAL → general guidance to use infrastructure helpers
- Line 1918: User directives status → general guidance to use project metadata helpers
- Line 2707, 2813: Task/subtask counts → use incomplete getters, count results
- Line 2727, 2832: Pending tasks/subtasks → general guidance to search task helpers
- Line 2906: Sidequest parent → general guidance to use project CRUD helpers
- Line 2981, 2997: Completion path queries → general guidance to search completion path helpers
- Line 3016: Next milestone → general guidance to search milestone helpers

### Phase 3: Other JSON Files (7 queries)
- directives-git.json (2 queries) → general guidance to search git helpers
- directives-user-system.json (3 queries) → general guidance to search user directive helpers
- directives-user-pref.json (2 queries) → general guidance to search preference helpers

### Phase 4: aifp.scripts Cleanup (4 references)
Replace in directives-project.json:
- Line 137: Description text → remove aifp.scripts mention
- Line 246: create_project_structure → "orchestrator handles directly"
- Line 261: generate_project_blueprint → "orchestrator handles directly"
- Line 275: initialize_databases → "orchestrator handles directly"
- Line 295: validate_initialization → general guidance to search validation helpers

### Phase 5: MD Files
Update corresponding MD files to match JSON changes

---

## Part 7: Example Replacements

### Example 1: Infrastructure Query (Line 1911)
**Before**:
```json
{
  "if": "load_infrastructure_data",
  "then": "query_infrastructure",
  "details": {
    "query": "SELECT type, value, description FROM infrastructure WHERE project_id = ?"
  }
}
```

**After**:
```json
{
  "if": "load_infrastructure_data",
  "then": "query_infrastructure",
  "details": {
    "action": "query_helpers_database",
    "guidance": "Search helper_functions table for infrastructure helpers. Query by target_database='project' and purpose keywords: 'infrastructure', 'all'. Should return helper that gets all infrastructure entries.",
    "note": "Infrastructure table has no project_id (one project per database). Helper names change - query database for current helpers."
  }
}
```

### Example 2: Directive Preferences (Line 464)
**Before**:
```json
{
  "query": "SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='project_task_decomposition' AND active=1"
}
```

**After**:
```json
{
  "action": "query_helpers_database",
  "guidance": "Search helper_functions table for preference helpers. Query by target_database='user_preferences' and purpose keywords: 'directive', 'preference', 'load'. Pass directive_name as parameter.",
  "note": "Helper names change - query database for current helpers."
}
```

### Example 3: Incomplete Tasks (Line 2707)
**Before**:
```json
{
  "query": "SELECT COUNT(*) FROM tasks WHERE milestone_id = ? AND status NOT IN ('completed', 'cancelled')"
}
```

**After**:
```json
{
  "action": "query_helpers_database",
  "guidance": "Search helper_functions table for task helpers. Query by target_database='project' and purpose keywords: 'task', 'incomplete', 'milestone'. Use helper that returns incomplete tasks, then count results in AI logic.",
  "note": "No need for dedicated count helper - get incomplete tasks and count them. Helper names change - query database."
}
```

---

## Part 8: Success Criteria

### For Infrastructure
- ✅ `standard_infrastructure.sql` exists and contains 6 INSERT statements
- ✅ `project_init` orchestrator defined in helpers-orchestrators.json
- ✅ `get_all_infrastructure` defined in helpers-project-1.json
- ✅ `aifp_run` updated to include infrastructure_data in bundle
- ✅ After init, `SELECT * FROM infrastructure` returns 6 rows with empty values

### For SQL Cleanup
- ✅ All 24 SQL queries replaced with general guidance
- ✅ No hardcoded helper names in directive JSON files
- ✅ Each replacement includes guidance to query helper_functions table
- ✅ Each replacement includes note about helper names changing

### For aifp.scripts Cleanup
- ✅ All 4 references to aifp.scripts removed
- ✅ Replaced with "orchestrator handles directly" or general guidance
- ✅ project_init directive references project_init orchestrator

---

## Part 9: Key Principles

1. **AI Natural Behavior**: Don't code what AI does naturally (language detection, OOP scanning)
2. **Helper Flexibility**: Never hardcode helper names - they change
3. **Query Database**: Always instruct to query helper_functions table
4. **Orchestrator Simplicity**: One-time operations happen directly in orchestrator code
5. **Existing Helpers First**: Use `get_from_project_where` and other generic CRUD before creating new helpers
6. **Context Over Counts**: Get full data, not just counts - context is valuable

---

## Next Steps

1. Create `standard_infrastructure.sql` file
2. Add helper definitions to JSON files (project_init, get_all_infrastructure)
3. Begin SQL cleanup in directives-project.json (17 queries)
4. Continue with other JSON files (7 queries)
5. Complete aifp.scripts cleanup (4 references)
6. Update MD files to match JSON changes

**Ready to begin implementation.**
