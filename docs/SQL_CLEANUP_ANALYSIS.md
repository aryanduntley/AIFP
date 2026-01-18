# SQL Query Cleanup Analysis

**Date**: 2026-01-17
**Status**: Analysis Complete - Ready for Cleanup
**Total SQL Queries Found**: 24 in JSON files

---

## Summary

Found **24 direct SQL queries** across 4 directive JSON files:
- `directives-project.json`: 17 queries ⚠️ (most problematic)
- `directives-user-pref.json`: 2 queries
- `directives-git.json`: 2 queries
- `directives-user-system.json`: 3 queries

**MD files**: SQL found in code examples (documentation/illustration purposes) - less critical

---

## directives-project.json (17 queries - PRIORITY 1)

### Query 1: Line 464 - Directive Preferences
```json
"query": "SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='project_task_decomposition' AND active=1"
```
**Context**: Loading preferences for task decomposition
**Replace with**: `"helper": "get_directive_preferences", "directive_name": "project_task_decomposition"`
**Helper exists**: ✅ Likely exists in user preferences helpers

---

### Query 2: Line 663 - Directive Preferences
```json
"query": "SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='project_file_write' AND active=1"
```
**Context**: Loading preferences for file write directive
**Replace with**: `"helper": "get_directive_preferences", "directive_name": "project_file_write"`
**Helper exists**: ✅ Same as Query 1

---

### Query 3: Line 939 - Tracking Settings
```json
"query": "SELECT enabled FROM tracking_settings WHERE feature_name='compliance_checking'"
```
**Context**: Check if compliance checking is enabled
**Replace with**: `"helper": "get_tracking_setting", "feature_name": "compliance_checking"`
**Helper exists**: ✅ Check user preferences helpers

---

### Query 4: Line 949 - Functions Query
```json
"query_project_db": "SELECT * FROM functions"
```
**Context**: Get all functions from project database
**Replace with**: `"helper": "get_all_functions"`
**Helper exists**: ❌ **NEEDS CREATION** (or use existing CRUD: `get_from_project_where('functions', {})`)

---

### Query 5: Line 1911 - Infrastructure ⚠️ (CRITICAL)
```json
"query": "SELECT type, value, description FROM infrastructure WHERE project_id = ?"
```
**Context**: Load infrastructure data
**Issues**:
- Direct SQL in directive
- References `project_id` (removed from schema - one project per DB)

**Replace with**: `"helper": "get_all_infrastructure"`
**Helper exists**: ❌ **NEEDS CREATION** (documented in INFRASTRUCTURE_GOALS.md)

---

### Query 6: Line 1918 - User Directives Status
```json
"query": "SELECT user_directives_status FROM project WHERE id = ?"
```
**Context**: Check if user directives are active
**Replace with**: `"helper": "get_project"` (returns full project metadata)
**Helper exists**: ✅ Already in helpers-project-1.json

---

### Query 7: Line 2707 - Task Count
```json
"query": "SELECT COUNT(*) FROM tasks WHERE milestone_id = ? AND status NOT IN ('completed', 'cancelled')"
```
**Context**: Count incomplete tasks for a milestone
**Replace with**: `"helper": "count_incomplete_tasks", "milestone_id": "milestone_id_from_context"`
**Helper exists**: ❌ **NEEDS CREATION** (or use query_project with count)

---

### Query 8: Line 2727 - Pending Tasks
```json
"query_pending_tasks": "SELECT id, name, description FROM tasks WHERE milestone_id = ? AND status = 'pending' ORDER BY priority DESC LIMIT 5"
```
**Context**: Get top 5 pending tasks for milestone
**Replace with**: `"helper": "get_from_project_where", "table": "tasks", "conditions": {"milestone_id": "...", "status": "pending"}, "orderby": "priority DESC", "limit": 5`
**Helper exists**: ✅ Already in helpers-project-1.json

---

### Query 9: Line 2813 - Subtask Count
```json
"query": "SELECT COUNT(*) FROM subtasks WHERE parent_task_id = ? AND status NOT IN ('completed', 'cancelled')"
```
**Context**: Count incomplete subtasks
**Replace with**: `"helper": "count_incomplete_subtasks", "parent_task_id": "..."`
**Helper exists**: ❌ **NEEDS CREATION** (or use query_project)

---

### Query 10: Line 2832 - Pending Subtasks
```json
"query": "SELECT id, name FROM subtasks WHERE parent_task_id = ? AND status = 'pending' ORDER BY priority DESC"
```
**Context**: Get pending subtasks
**Replace with**: `"helper": "get_from_project_where", "table": "subtasks", "conditions": {"parent_task_id": "...", "status": "pending"}, "orderby": "priority DESC"`
**Helper exists**: ✅ Already in helpers-project-1.json

---

### Query 11: Line 2906 - Sidequest Parent Task
```json
"query": "SELECT task_id FROM sidequests WHERE id = ?"
```
**Context**: Get parent task for sidequest
**Replace with**: `"helper": "get_from_project", "table": "sidequests", "id_array": [sidequest_id]`
**Helper exists**: ✅ Already in helpers-project-1.json

---

### Query 12: Line 2981 - Completion Path
```json
"query_completion_path": "SELECT id, status FROM completion_path WHERE id = (SELECT completion_path_id FROM milestones WHERE id = ?)"
```
**Context**: Get completion path for milestone (nested query)
**Replace with**: `"helper": "get_completion_path_for_milestone", "milestone_id": "..."`
**Helper exists**: ❌ **NEEDS CREATION** (nested query needs dedicated helper)

---

### Query 13: Line 2997 - Incomplete Completion Paths
```json
"query": "SELECT COUNT(*) FROM completion_path WHERE project_id = ? AND status NOT IN ('completed')"
```
**Context**: Count incomplete completion paths
**Issues**: References `project_id` (removed)
**Replace with**: `"helper": "count_incomplete_completion_paths"`
**Helper exists**: ❌ **NEEDS CREATION**

---

### Query 14: Line 3016 - Next Milestone
```json
"query_next_milestone": "SELECT m.id, m.name, m.description FROM milestones m JOIN completion_path cp ON m.completion_path_id = cp.id WHERE cp.project_id = ? AND m.status = 'pending' ORDER BY cp.order_index, m.id LIMIT 1"
```
**Context**: Get next pending milestone (complex JOIN)
**Issues**: References `project_id` (removed), complex JOIN query
**Replace with**: `"helper": "get_next_milestone"`
**Helper exists**: ❌ **NEEDS CREATION** (complex query needs dedicated helper)

---

## directives-git.json (2 queries)

### Query 15: Line 239 - Max Branch Number
```json
"query": "MAX(branch_number) FROM work_branches WHERE user_name = ?"
```
**Context**: Get highest branch number for user
**Replace with**: `"helper": "get_max_branch_number", "user_name": "..."`
**Helper exists**: ❌ **NEEDS CREATION** (git helpers)

---

### Query 16: Line 648 - Last Git Hash
```json
"query": "SELECT last_known_git_hash FROM project"
```
**Context**: Get last known git hash
**Replace with**: `"helper": "get_project"` (returns full project metadata including git hash)
**Helper exists**: ✅ Already in helpers-project-1.json

---

## directives-user-system.json (3 queries)

### Query 17: Line 917 - Active User Directives
```json
"query": "user_directives table for any remaining directives with status='active'"
```
**Context**: Check for active user directives (informal query description)
**Replace with**: `"helper": "get_from_project_where", "table": "user_directives", "conditions": {"status": "active"}`
**Helper exists**: ✅ Already in helpers-project-1.json (generic CRUD)

---

### Query 18: Line 977 - User Directives Grouped
```json
"query": "user_directives table for all directives grouped by status"
```
**Context**: Get directives grouped by status (informal)
**Replace with**: `"helper": "get_user_directives_by_status"` (aggregation query)
**Helper exists**: ❌ **NEEDS CREATION** (grouping operation)

---

### Query 19: Line 980 - Execution Statistics
```json
"query": "directive_executions table for execution statistics"
```
**Context**: Get execution stats (informal)
**Replace with**: `"helper": "get_directive_execution_stats"`
**Helper exists**: ❌ **NEEDS CREATION** (statistics aggregation)

---

## directives-user-pref.json (2 queries)

### Query 20: Line 35 - Directive Preferences
```json
"query": "SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name=? AND active=1"
```
**Context**: Get active preferences for directive
**Replace with**: `"helper": "get_directive_preferences", "directive_name": "..."`
**Helper exists**: ✅ Likely in user preferences helpers

---

### Query 21: Line 517 - Tracking Setting
```json
"query": "SELECT enabled FROM tracking_settings WHERE feature_name=?"
```
**Context**: Check if tracking feature enabled
**Replace with**: `"helper": "get_tracking_setting", "feature_name": "..."`
**Helper exists**: ✅ Likely in user preferences helpers

---

## MD Files - SQL in Examples (Lower Priority)

MD files contain SQL in:
1. **Code examples** (showing what operations occur)
2. **Documentation** (explaining database operations)
3. **Workflow illustrations** (conceptual queries)

**Examples found**:
- `fp_lazy_computation.md`: SQL in code examples (lines 253, 483, 540)
- `fp_state_elimination.md`: SQL in refactoring examples
- `git_detect_external_changes.md`: SQL in workflow explanation
- `user_preferences_import.md`: SQL showing import operations

**Action**: These are **documentation/examples**, not directive specifications. They should:
- Reference that helpers would be used in actual implementation
- Add note: "Example shows SQL for clarity - actual implementation uses helpers"
- Keep examples for educational value but clarify they're illustrative

---

## Helpers Needed (New Creations)

Based on SQL query analysis, these helpers need to be created:

### 1. Infrastructure Helpers
- ✅ **`get_all_infrastructure()`** - Already documented in INFRASTRUCTURE_GOALS.md
  - Returns all infrastructure rows
  - Used by: aifp_run, aifp_status

### 2. Task/Work Management Helpers
- ❌ **`count_incomplete_tasks(milestone_id)`**
  - Count tasks not completed/cancelled for milestone
  - Alternative: Use `query_project` with COUNT

- ❌ **`count_incomplete_subtasks(parent_task_id)`**
  - Count subtasks not completed/cancelled
  - Alternative: Use `query_project` with COUNT

- ❌ **`count_incomplete_completion_paths()`**
  - Count completion paths not completed
  - No project_id parameter (one project per DB)

- ❌ **`get_next_milestone()`**
  - Complex JOIN to find next pending milestone by order
  - Returns: {id, name, description, completion_path_id}

- ❌ **`get_completion_path_for_milestone(milestone_id)`**
  - Get completion path data for a milestone
  - Nested query: milestone → completion_path

### 3. Git Helpers
- ❌ **`get_max_branch_number(user_name)`**
  - Get highest branch number for user
  - Returns: integer

### 4. User Directive Helpers
- ❌ **`get_user_directives_by_status()`**
  - Get directives grouped by status
  - Returns: {active: [...], disabled: [...], in_progress: [...]}

- ❌ **`get_directive_execution_stats()`**
  - Get execution statistics
  - Returns: {total_executions, success_count, error_count, avg_duration, ...}

### 5. Function Helpers
- ❌ **`get_all_functions()`**
  - Get all functions from project DB
  - Alternative: `get_from_project_where('functions', {})`
  - Decision: Use existing generic CRUD instead

---

## Replacement Strategy

### Pattern to Use

**Before** (Direct SQL):
```json
{
  "if": "need_data",
  "then": "load_data",
  "details": {
    "query": "SELECT * FROM table WHERE condition = ?"
  }
}
```

**After** (Helper Reference):
```json
{
  "if": "need_data",
  "then": "load_data",
  "details": {
    "helper": "get_data_helper",
    "parameters": {
      "condition_value": "from_context"
    },
    "note": "Helper abstracts database query - see helpers JSON for details"
  }
}
```

### For Complex Queries

If helper doesn't exist:
1. Document needed helper in section above
2. Use generic CRUD if possible: `get_from_project_where()`
3. Create new helper if query is complex (JOINs, aggregations, nested)

---

## Action Items

### Phase 1: Create Missing Helpers (Documentation)
- [ ] Define `get_all_infrastructure()` helper (already in INFRASTRUCTURE_GOALS.md)
- [ ] Define `count_incomplete_tasks()` helper
- [ ] Define `count_incomplete_subtasks()` helper
- [ ] Define `count_incomplete_completion_paths()` helper
- [ ] Define `get_next_milestone()` helper (complex JOIN)
- [ ] Define `get_completion_path_for_milestone()` helper
- [ ] Define `get_max_branch_number()` helper
- [ ] Define `get_user_directives_by_status()` helper
- [ ] Define `get_directive_execution_stats()` helper

### Phase 2: Update directives-project.json
- [ ] Replace Query 1 (line 464) - directive preferences
- [ ] Replace Query 2 (line 663) - directive preferences
- [ ] Replace Query 3 (line 939) - tracking settings
- [ ] Replace Query 4 (line 949) - all functions
- [ ] Replace Query 5 (line 1911) - infrastructure ⚠️ CRITICAL
- [ ] Replace Query 6 (line 1918) - user directives status
- [ ] Replace Query 7 (line 2707) - task count
- [ ] Replace Query 8 (line 2727) - pending tasks
- [ ] Replace Query 9 (line 2813) - subtask count
- [ ] Replace Query 10 (line 2832) - pending subtasks
- [ ] Replace Query 11 (line 2906) - sidequest parent
- [ ] Replace Query 12 (line 2981) - completion path
- [ ] Replace Query 13 (line 2997) - incomplete completion paths
- [ ] Replace Query 14 (line 3016) - next milestone

### Phase 3: Update directives-git.json
- [ ] Replace Query 15 (line 239) - max branch number
- [ ] Replace Query 16 (line 648) - last git hash

### Phase 4: Update directives-user-system.json
- [ ] Replace Query 17 (line 917) - active user directives
- [ ] Replace Query 18 (line 977) - directives grouped by status
- [ ] Replace Query 19 (line 980) - execution statistics

### Phase 5: Update directives-user-pref.json
- [ ] Replace Query 20 (line 35) - directive preferences
- [ ] Replace Query 21 (line 517) - tracking setting

### Phase 6: Verify MD Files
- [ ] Check project_init.md for SQL references
- [ ] Add notes to example SQL in MD files clarifying they're illustrative
- [ ] Verify consistency between JSON and MD for each directive

---

## Priority Order

### Immediate (Blocks infrastructure work)
1. Query 5 (line 1911) - Infrastructure query ⚠️ CRITICAL
2. Query 6 (line 1918) - User directives status (wrong approach, use get_project)
3. Query 13 (line 2997) - References removed project_id

### High Priority (Complex queries need helpers)
4. Query 14 (line 3016) - Next milestone (complex JOIN)
5. Query 12 (line 2981) - Completion path (nested query)

### Medium Priority (Can use existing generic CRUD)
6-11. Task/subtask queries (use get_from_project_where)

### Low Priority (Simple replacements)
12-21. Remaining queries (straightforward helper mappings)

---

## Next Steps

1. ✅ Review this analysis document
2. Create helper specification document for new helpers
3. Update JSON files with helper references
4. Verify MD files match JSON changes
5. Test that helpers exist or document needed helpers
