# Orchestrator Helper Functions

**Purpose**: Complex multi-step operations that coordinate multiple database helpers
**Classification**: All functions are is_tool=true, is_sub_helper=false

For the master index and design philosophy, see [helpers-consolidated-index.md](helpers-consolidated-index.md)

---

## What Are Orchestrators?

Orchestrators are complex helper functions that:
1. Call 3+ different database helpers
2. Construct complex data structures from multiple sources
3. Implement business logic beyond simple queries
4. Coordinate workflows across multiple tables/databases

**Two Types of Orchestrators**:
- **Layer 2 Generic Orchestrators**: Flexible, parameter-driven tools for common patterns (progress queries, state updates, batch operations)
- **Layer 3 Specific Orchestrators**: Complex, specialized multi-step workflows (project analysis, user directive handling)

**When to Use**: AI should call orchestrators for comprehensive analysis, status reports, and multi-step workflows.

---

## Layer 2: Generic Project Orchestrators

These orchestrators provide flexible, parameter-driven interfaces for common patterns.

### `get_current_progress(scope, detail_level, filters)`

**Purpose**: Single entry point for all project status queries. Replaces 5-10 separate helper calls with one flexible query.

**Parameters**:
- `scope` (String, optional, default="full") - What information to retrieve
  - Values: "full", "task", "milestone", "completion_path", "files", "functions", "flows", "tasks"
- `detail_level` (String, optional, default="summary") - How much detail to return
  - Values: "minimal", "summary", "detailed"
- `filters` (Object, optional) - WHERE-like conditions
  - Fields: status, priority, flow_id, milestone_id, updated_since, file_language

**Returns**:
```json
{
  "project_metadata": {...},
  "completion_path": {
    "current_stage": "Development",
    "progress": 0.45
  },
  "current_work": {
    "task": {...},
    "subtask": {...},
    "sidequest": {...},
    "flows": [...],
    "progress": "3 of 8 items completed"
  },
  "milestones": {
    "total": 5,
    "completed": 2,
    "current": "Core Features"
  },
  "tasks": {
    "completed": 12,
    "in_progress": 3,
    "pending": 8
  },
  "recent_activity": [...],
  "next_action": "Complete authentication implementation"
}
```

**Detail Levels**:
- **minimal**: Just counts and current status (<50ms)
- **summary**: Context and next action (<200ms) - DEFAULT
- **detailed**: Full file/function lists with interactions

**Notes**:
- scope='full' + detail_level='summary' is default
- scope='task' + detail_level='detailed' delegates to `get_work_context()`
- Returns partial data with warnings if some queries fail (graceful degradation)
- Primary entry point for `aifp_status` directive

**Helpers Called**: get_project_metadata, get_completion_path, get_current_stage, get_work_context, get_tasks_by_status, get_milestone_progress, get_recent_files_for_task, get_recent_functions_for_task, get_all_flows, get_all_themes

**Classification**: is_tool=true, is_sub_helper=false

---

### `update_project_state(action, target_type, target_id, data, create_note)`

**Purpose**: Single entry point for common project state updates. Simplifies task lifecycle management and progress tracking.

**Parameters**:
- `action` (String, required) - Operation to perform
  - Values: "start_task", "complete_task", "cancel_task", "pause_task", "resume_task", "update_priority", "link_flows", "add_flow", "remove_flow", "add_file", "update_file", "delete_file", "register_function", "update_function", "add_interaction", "add_note"
- `target_type` (String, required) - Entity type
  - Values: "task", "subtask", "sidequest", "file", "function", "milestone"
- `target_id` (Integer, required) - ID of target entity
- `data` (Object, optional) - Action-specific data
  - Examples: flow_ids for link_flows, priority for update_priority, file details for add_file
- `create_note` (Boolean, optional, default=true) - Auto-log action as note

**Returns**:
```json
{
  "success": true,
  "action": "complete_task",
  "target": {
    "type": "task",
    "id": 15,
    "name": "Implement authentication"
  },
  "changes": {
    "old_status": "in_progress",
    "new_status": "completed",
    "completed_at": "2025-12-11T20:30:00Z"
  },
  "side_effects": [
    "milestone_completed: Core Features",
    "tasks_unblocked: 2 tasks now available"
  ],
  "note_created": true,
  "note_id": 42
}
```

**Validation**:
- Complete_task checks for pending subtasks before allowing completion
- Link_flows validates flow_ids exist before linking
- Returns descriptive error codes: SUBTASKS_PENDING, INVALID_TRANSITION, etc.

**Notes**:
- Note automatically created if create_note=true
- Changes include status transitions, completion timestamps, milestone progress updates
- Side effects tracked: milestone_completed, tasks_unblocked, parent_task_resumed
- Use for task lifecycle directives, file/function registration

**Helpers Called**: update_task_status, link_task_to_flows, validate_flow_ids, add_file, register_function, add_interaction, create_note, get_milestone_progress

**Used By**: project_task_update, project_task_complete, project_subtask_complete, project_file_write

**Classification**: is_tool=true, is_sub_helper=false

---

### `batch_update_progress(updates, transaction, continue_on_error, rollback_on_partial_failure)`

**Purpose**: Update multiple project items atomically. Used after code generation or bulk operations to ensure consistency.

**Parameters**:
- `updates` (Array, required) - List of update operation objects
  - Each object: {action, target_type (optional), target_id (optional), data}
- `transaction` (Boolean, optional, default=true) - All-or-nothing commit vs independent updates
- `continue_on_error` (Boolean, optional, default=false) - Stop on first error or continue processing
- `rollback_on_partial_failure` (Boolean, optional, default=true) - If transaction=true and any update fails, rollback all

**Returns**:
```json
{
  "success": true,
  "updates_requested": 10,
  "updates_applied": 10,
  "updates_failed": 0,
  "transaction_committed": true,
  "execution_time_ms": 85,
  "summary": {
    "files_added": 3,
    "functions_registered": 7,
    "interactions_added": 5,
    "flows_linked": 2,
    "task_status_updated": 1,
    "notes_created": 10
  },
  "changes": [
    {
      "action": "add_file",
      "success": true,
      "file_id": 23,
      "file_name": "auth-ID_23.py"
    }
  ],
  "errors": []
}
```

**Transaction Modes**:
- **transaction=true**: Atomicity - all succeed or all rollback
- **continue_on_error=true**: Collects all errors instead of stopping on first
- **rollback_on_partial_failure=true**: Ensures consistency if any update fails

**Notes**:
- Validates all updates before starting transaction
- Each change includes action, success status, generated IDs (file_id, function_id, etc.)
- Errors include update_index, action, error message, error_code
- Typical execution: 20-100ms for 5-10 updates in transaction
- Primary use: `project_update_db` directive after code generation

**Used By**: project_update_db, project_file_write

**Classification**: is_tool=true, is_sub_helper=false

---

### `query_project_state(entity, filters, joins, sort, limit, offset)`

**Purpose**: Flexible SQL-like query interface for complex project queries. Provides powerful filtering and joining capabilities without writing SQL.

**Parameters**:
- `entity` (String, required) - Primary table to query
  - Values: "tasks", "subtasks", "sidequests", "files", "functions", "flows", "themes", "milestones", "notes"
- `filters` (Object, optional) - WHERE-like conditions with operators
  - Simple equality: {"status": "active"}
  - Comparison: {"priority_gte": 5, "updated_at_lt": "2025-12-01"}
  - List: {"status_in": ["active", "in_progress"], "language_not_in": ["javascript"]}
  - Pattern: {"name_like": "%auth%", "path_not_like": "%test%"}
  - Date: {"updated_since": "2025-12-01", "created_before": "2025-11-01"}
  - JSON array: {"has_flow": 5, "has_any_flow": [5, 7], "has_all_flows": [5, 7]}
- `joins` (Array, optional) - Relations to include (LEFT JOIN)
  - Values: "milestone", "flows", "themes", "files", "functions", "items", "notes", "interactions"
- `sort` (String, optional) - ORDER BY clause
  - Example: "created_at DESC", "priority DESC, created_at ASC"
- `limit` (Integer, optional) - Maximum results (pagination)
- `offset` (Integer, optional, default=0) - Skip first N results (pagination)

**Returns**: Array of entity objects with requested joins included

**Filter Operators**:
- Comparison: gte, gt, lte, lt
- List: in, not_in, like, not_like
- Date: updated_since, created_before, updated_in_last (days)
- JSON array: has_flow, has_any_flow, has_all_flows

**Notes**:
- Returns empty array if no matches
- All inputs sanitized - parameterized queries only (SQL injection prevention)
- Read-only - no UPDATE/DELETE operations allowed
- Use for complex filtering, reporting, analytics, custom views
- Joins populate related data: milestone (for tasks), flows (via flow_ids), files (for functions), functions (for files), items (for work items), notes, interactions (for functions)

**Classification**: is_tool=true, is_sub_helper=false

---

### `validate_initialization(aifp_dir)`

**Purpose**: Validate that project initialization is complete and correct. Performs comprehensive structural validation.

**Parameters**:
- `aifp_dir` (String, required) - Path to .aifp-project/ directory

**Returns**:
```json
{
  "success": true,
  "validation_checks": [
    {"check": ".aifp-project directory exists", "passed": true},
    {"check": "project.db exists with valid schema", "passed": true},
    {"check": "project table has metadata populated", "passed": true},
    {"check": "user_preferences.db exists with valid schema", "passed": true},
    {"check": "ProjectBlueprint.md exists and not empty", "passed": true},
    {"check": "all required tables created", "passed": true}
  ]
}
```

**Error Example**:
```json
{
  "success": false,
  "error": "project table empty - metadata not populated",
  "failed_check": "project table has metadata populated"
}
```

**Validation Checks Performed**:
1. .aifp-project/ directory exists
2. project.db exists and has valid schema
3. project table has metadata populated
4. user_preferences.db exists and has valid schema
5. ProjectBlueprint.md exists and is not empty
6. All required tables created in both databases

**Notes**:
- This is deterministic validation - checking file existence, database schema, table population
- NOT pattern recognition - just structural checks
- Use after `project_init` to confirm initialization succeeded
- Can be called standalone for troubleshooting initialization issues
- Fast execution (<50ms) - just file/database structure checks
- Never raises exceptions - always returns result object

**Used By**: project_init

**Classification**: is_tool=true, is_sub_helper=false

---

### `get_work_context(work_item_type, work_item_id, include_interactions, include_history)`

**Purpose**: Get complete context for resuming work. Single call retrieves task/subtask/sidequest + flows + files + functions + interactions. Optimized for session resumption.

**Parameters**:
- `work_item_type` (String, required) - Type of work item
  - Values: "task", "subtask", "sidequest"
- `work_item_id` (Integer, required) - ID of work item
- `include_interactions` (Boolean, optional, default=true) - Include function dependency interactions
- `include_history` (Boolean, optional, default=false) - Include note history for work item

**Returns**:
```json
{
  "work_item": {
    "id": 15,
    "name": "Implement authentication",
    "status": "in_progress",
    "description": "...",
    "type": "task"
  },
  "milestone": {
    "id": 3,
    "name": "Core Features"
  },
  "flows": [
    {
      "id": 5,
      "name": "Authentication Flow",
      "themes": ["Security", "User Management"]
    }
  ],
  "files": [
    {
      "id": 23,
      "name": "auth-ID_23.py",
      "path": "src/auth-ID_23.py",
      "updated_at": "2025-12-11T19:30:00Z",
      "functions": [
        {
          "id": 42,
          "name": "validate_token_id_42",
          "signature": "validate_token(token: str) -> bool",
          "is_pure": true,
          "has_tests": true
        }
      ]
    }
  ],
  "interactions": [
    {
      "source_function_id": 42,
      "target_function_id": 43,
      "interaction_type": "calls"
    }
  ],
  "notes": []
}
```

**Notes**:
- Replaces 6-8 separate helper calls with single comprehensive query
- Files sorted by most recently updated first for immediate context
- Functions include purity analysis and test status
- Interactions show function dependency graph
- Primary use case: `project_auto_resume` directive for session resumption
- Also used by `aifp_status` when detailed work context needed
- Graceful degradation if some related data missing
- Returns partial context if some queries fail
- Empty structure returned if work_item_id not found

**Helpers Called**: get_incomplete_tasks, get_task_flows, get_files_by_flow, get_incomplete_sidequests, get_functions_by_file, get_interactions_by_function

**Used By**: project_auto_resume, aifp_status

**Classification**: is_tool=true, is_sub_helper=false

---

## Layer 3: Specific Project Analysis Orchestrators

### `get_project_status()`

**Purpose**: Analyze entire work hierarchy and return comprehensive project status

**Returns**:
```json
{
  "project": {
    "name": "Project Name",
    "status": "active",
    "version": "0.1.0"
  },
  "completion_paths": {
    "total": 5,
    "completed": 2,
    "in_progress": 1,
    "pending": 2,
    "completion_percentage": 40
  },
  "milestones": {
    "total": 12,
    "completed": 5,
    "in_progress": 3,
    "pending": 4
  },
  "tasks": {
    "total": 45,
    "completed": 20,
    "in_progress": 8,
    "pending": 17,
    "completion_percentage": 44
  },
  "subtasks": {
    "total": 78,
    "completed": 35,
    "in_progress": 15,
    "pending": 28
  },
  "sidequests": {
    "total": 5,
    "completed": 2,
    "in_progress": 1,
    "pending": 2
  },
  "blocking_issues": [
    {
      "type": "task",
      "id": 15,
      "name": "Fix authentication bug",
      "status": "in_progress",
      "days_active": 3,
      "items": {
        "completed": 2,
        "in_progress": 1,
        "pending": 0
      }
    }
  ],
  "next_priorities": [
    {
      "type": "milestone",
      "id": 3,
      "name": "Core Features Complete",
      "path": "Development",
      "pending_tasks": 5
    }
  ]
}
```

**Helpers Called**:
- `get_project()`
- `get_all_completion_paths()`
- `get_incomplete_tasks()`
- `get_incomplete_subtasks()`
- `get_incomplete_sidequests()`
- `get_items_for_task()` (for multiple tasks)

**Note**: This is NOT a simple field getter - it analyzes the entire work hierarchy and provides detailed status analysis for AI to understand project progress.

**Classification**: is_tool=true, is_sub_helper=false

---

### `get_project_context(type)`

**Purpose**: Get structured project overview for different contexts

**Parameters**:
- `type` (String) - Context type: "blueprint", "metadata", "status", "infrastructure"

**Returns** (varies by type):

**Type: "blueprint"**
```json
{
  "project": {project object},
  "blueprint": {
    "exists": true,
    "changed": false,
    "path": ".aifp/ProjectBlueprint.md"
  },
  "themes": [{theme objects}],
  "flows": [{flow objects}]
}
```

**Type: "metadata"**
```json
{
  "project": {project object},
  "infrastructure": [{infrastructure objects}],
  "git": {
    "branch": "main",
    "hash": "abc123",
    "uncommitted_changes": false
  }
}
```

**Type: "status"**
- Returns same as `get_project_status()`

**Helpers Called** (varies by type):
- `get_project()`
- `blueprint_has_changed()`
- `get_all_themes()`
- `get_all_flows()`
- `get_infrastructure_by_type()`
- `get_git_status()`
- Plus all helpers from `get_project_status()` for type="status"

**Classification**: is_tool=true, is_sub_helper=false

---

### `get_status_tree()`

**Purpose**: Get hierarchical view of all work items with nested structure

**Returns**:
```json
{
  "completion_paths": [
    {
      "id": 1,
      "name": "Setup",
      "status": "completed",
      "order_index": 1,
      "milestones": [
        {
          "id": 1,
          "name": "Initialize Project",
          "status": "completed",
          "tasks": [
            {
              "id": 1,
              "name": "Setup database",
              "status": "completed",
              "priority": "high",
              "subtasks": [],
              "sidequests": []
            }
          ]
        }
      ]
    },
    {
      "id": 2,
      "name": "Development",
      "status": "in_progress",
      "order_index": 2,
      "milestones": [
        {
          "id": 3,
          "name": "Core Features",
          "status": "in_progress",
          "tasks": [
            {
              "id": 15,
              "name": "Implement auth",
              "status": "in_progress",
              "priority": "high",
              "subtasks": [
                {
                  "id": 42,
                  "name": "JWT validation",
                  "status": "in_progress",
                  "priority": "high"
                }
              ],
              "sidequests": [
                {
                  "id": 5,
                  "name": "Fix security issue",
                  "status": "in_progress",
                  "priority": "urgent",
                  "paused_task_id": 15,
                  "paused_subtask_id": 42
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "orphaned_sidequests": []
}
```

**Helpers Called**:
- `get_all_completion_paths()`
- `get_milestones_by_path()` (for each path)
- `get_tasks_by_milestone()` (for each milestone)
- `get_subtasks_by_task()` (for each task)
- `get_sidequests_comprehensive()` (all sidequests, then nested appropriately)

**Note**: Provides complete hierarchical view for visualization and progress tracking

**Classification**: is_tool=true, is_sub_helper=false

---

### `get_files_by_flow_context(flow_id)`

**Purpose**: Get all files for a flow with functions embedded

**Parameters**:
- `flow_id` (Integer) - Flow ID

**Returns**:
```json
[
  {
    "id": 23,
    "name": "auth-ID_23.py",
    "path": "src/auth-ID_23.py",
    "language": "python",
    "flow_id": 5,
    "functions": [
      {
        "id": 42,
        "name": "validate_token_id_42",
        "file_id": 23,
        "purpose": "Validate JWT tokens",
        "parameters": "token: str",
        "returns": "bool"
      },
      {
        "id": 43,
        "name": "generate_token_id_43",
        "file_id": 23,
        "purpose": "Generate new JWT tokens",
        "parameters": "user_id: int, expiry: int",
        "returns": "str"
      }
    ]
  }
]
```

**Helpers Called**:
- `get_files_by_flow(flow_id)`
- `get_functions_by_file(file_id)` (for each file)

**Note**: Useful for understanding complete flow implementation with all associated functions

**Classification**: is_tool=false, is_sub_helper=false (directive-callable but not MCP tool)

---

## Git Orchestrators

See [helpers-consolidated-git.md](helpers-consolidated-git.md) for Git orchestrator functions:
- `get_git_status()` - Comprehensive Git state snapshot
- `detect_external_changes()` - Compare Git hashes, find changed files
- `detect_conflicts_before_merge()` - FP-powered conflict analysis
- `merge_with_fp_intelligence()` - Auto-resolve conflicts using purity rules
- `sync_git_state()` - Update project.last_known_git_hash

---

## Design Principles for Orchestrators

1. **Complex Coordination**: Must call 3+ helpers or perform complex analysis
2. **Single Entry Point**: Provide comprehensive data in one call
3. **Business Logic**: Implement logic beyond simple queries
4. **Return Rich Data**: Nested structures with all relevant information
5. **Clear Purpose**: Descriptive names indicating what they orchestrate
6. **Documented Helpers**: Always list which helpers are called

**When NOT to Use**: Simple queries, single-table operations, straightforward lookups → Use Tier 1-4 helpers instead

---

**End of Orchestrator Helper Functions**
