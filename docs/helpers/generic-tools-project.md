# Generic Tools: Project Database

**Database**: project.db
**Purpose**: High-level orchestrator functions for project state management
**Layer**: Layer 2 (MCP-Exposed Generic Tools)
**Total Tools**: 5 generic orchestrators

---

## Overview

These generic tools provide **single-call interfaces** for common project operations. They orchestrate multiple specific helpers (Layer 3) to reduce API round trips and provide intuitive high-level operations for AI and directives.

**All functions in this file have `is_tool: true`** (MCP-exposed)

---

## 1. get_current_progress()

**Purpose**: Single entry point for all project status queries. Replaces 5-10 separate helper calls with one flexible query.

**Signature**:
```python
def get_current_progress(
    scope: str = "full",           # What to query
    detail_level: str = "summary", # How much detail
    filters: dict = {}             # Optional refinement
) -> dict
```

**Parameters**:

### scope (str)
Determines what information to retrieve:
- `"full"` - Everything (completion path + milestones + tasks + files + functions + flows)
- `"task"` - Current task context (delegates to `get_work_context()`)
- `"milestone"` - Current milestone progress only
- `"completion_path"` - Completion path stages and progress
- `"files"` - Recent file changes only
- `"functions"` - Function inventory and recent additions
- `"flows"` - Flow/theme organization
- `"tasks"` - Task list with filtering

### detail_level (str)
Controls verbosity:
- `"minimal"` - Counts and current status only (fast, small response)
- `"summary"` - Counts + current work + next action (default)
- `"detailed"` - Full context with files, functions, flows, history (comprehensive)

### filters (dict)
Optional WHERE-like conditions:
```python
filters = {
    "status": "in_progress",           # Filter by status
    "priority": "high",                 # Filter by priority
    "flow_id": 3,                       # Filter by flow
    "milestone_id": 2,                  # Specific milestone
    "updated_since": "2025-11-02",     # Only recent changes
    "file_language": "Python"           # Files by language
}
```

**Returns**:

### Full Scope, Summary Detail (Default)
```json
{
  "scope": "full",
  "detail_level": "summary",
  "project": {
    "name": "MatrixCalculator",
    "purpose": "Pure functional matrix math library",
    "status": "active",
    "version": 3,
    "blueprint_in_sync": true
  },
  "completion_path": {
    "current_stage": "Development",
    "current_stage_order": 2,
    "total_stages": 4,
    "stage_progress": 0.65,
    "overall_progress": 0.35
  },
  "current_work": {
    "type": "task",
    "id": 5,
    "name": "Implement matrix operations",
    "status": "in_progress",
    "priority": "high",
    "milestone": "Core Development",
    "progress": "3/8 items complete",
    "flows": [
      {"id": 1, "name": "Matrix Computation"},
      {"id": 3, "name": "Core Math Operations"}
    ],
    "started_at": "2025-11-02T10:00:00",
    "last_updated": "2025-11-05T14:30:00"
  },
  "milestones": {
    "total": 5,
    "completed": 1,
    "in_progress": 2,
    "pending": 2,
    "current": {
      "id": 2,
      "name": "Core Development",
      "tasks_completed": 3,
      "tasks_total": 8,
      "progress": 0.375
    }
  },
  "tasks": {
    "total": 24,
    "completed": 8,
    "in_progress": 1,
    "pending": 15,
    "cancelled": 0
  },
  "recent_activity": {
    "files_modified_today": 2,
    "functions_added_today": 3,
    "last_commit": "2025-11-05T14:00:00"
  },
  "next_action": "Complete current task item: 'Add matrix transpose function'"
}
```

### Task Scope, Detailed Level
```json
{
  "scope": "task",
  "detail_level": "detailed",
  "work_item": {
    "type": "task",
    "id": 5,
    "name": "Implement matrix operations",
    "description": "Create core matrix math functions with validation",
    "status": "in_progress",
    "priority": "high",
    "milestone": {
      "id": 2,
      "name": "Core Development",
      "completion_path_stage": "Development"
    },
    "created_at": "2025-11-02T10:00:00",
    "started_at": "2025-11-02T10:15:00",
    "updated_at": "2025-11-05T14:30:00"
  },
  "flows": [
    {
      "id": 1,
      "name": "Matrix Computation",
      "description": "Core matrix math operations",
      "themes": ["Core Math Operations"]
    },
    {
      "id": 3,
      "name": "Validation Flow",
      "description": "Input validation and error handling",
      "themes": ["Code Quality"]
    }
  ],
  "items": {
    "total": 8,
    "completed": 3,
    "pending": 5,
    "list": [
      {"id": 1, "name": "Create matrix structure", "status": "completed"},
      {"id": 2, "name": "Implement matrix_add", "status": "completed"},
      {"id": 3, "name": "Implement matrix_multiply", "status": "completed"},
      {"id": 4, "name": "Add matrix transpose", "status": "pending"},
      {"id": 5, "name": "Add dimension validation", "status": "pending"}
    ]
  },
  "files": [
    {
      "id": 1,
      "path": "src/matrix.py",
      "language": "Python",
      "created_at": "2025-11-02T10:20:00",
      "updated_at": "2025-11-05T14:30:00",
      "action": "modified",
      "checksum": "abc123..."
    },
    {
      "id": 2,
      "path": "tests/test_matrix.py",
      "language": "Python",
      "created_at": "2025-11-05T11:00:00",
      "updated_at": "2025-11-05T11:00:00",
      "action": "created"
    }
  ],
  "functions": [
    {
      "id": 1,
      "name": "matrix_multiply",
      "file_path": "src/matrix.py",
      "signature": "matrix_multiply(a: Matrix, b: Matrix) -> Matrix",
      "is_pure": true,
      "created_at": "2025-11-05T14:15:00",
      "updated_at": "2025-11-05T14:15:00",
      "action": "created"
    },
    {
      "id": 2,
      "name": "validate_dimensions",
      "file_path": "src/matrix.py",
      "signature": "validate_dimensions(a: Matrix, b: Matrix) -> bool",
      "is_pure": true,
      "created_at": "2025-11-02T10:30:00",
      "updated_at": "2025-11-05T14:20:00",
      "action": "modified"
    }
  ],
  "recent_interactions": [
    {
      "source": "matrix_multiply",
      "target": "validate_dimensions",
      "type": "call",
      "description": "Validates dimensions before multiplication"
    }
  ],
  "next_action": "Complete item: 'Add matrix transpose'"
}
```

### Minimal Detail Level
```json
{
  "scope": "full",
  "detail_level": "minimal",
  "project_status": "active",
  "overall_progress": 0.35,
  "current_work": "Task: Implement matrix operations (in_progress)",
  "milestones": {"completed": 1, "total": 5},
  "tasks": {"completed": 8, "total": 24},
  "next_action": "Complete current task item"
}
```

**Internally Calls**:

Based on scope and detail_level:
- `get_project_metadata()` - Always
- `get_completion_path()` - If scope includes completion_path
- `get_current_stage()` - If scope includes milestones/completion_path
- `get_work_context(work_item_type, work_item_id)` - If scope="task" or detail_level="detailed"
- `get_tasks_by_status(status)` - If scope includes tasks
- `get_milestone_progress(milestone_id)` - If scope includes milestones
- `get_recent_files_for_task(task_id, limit)` - If detail_level="detailed"
- `get_recent_functions_for_task(task_id, limit)` - If detail_level="detailed"
- `get_all_flows()` - If scope="flows"
- `get_all_themes()` - If scope="flows" and detail_level="detailed"

**Used By**:
- `aifp_status` directive (PRIMARY)
- AI direct queries ("what's the status?", "where am I?")
- Session initialization
- Project dashboards/reporting

**Error Handling**:
- Returns partial data if some queries fail
- Never fails completely (graceful degradation)
- Logs warnings for failed sub-queries

**is_tool**: `true`

---

## 2. update_project_state()

**Purpose**: Single entry point for common project state updates. Simplifies task lifecycle management and progress tracking.

**Signature**:
```python
def update_project_state(
    action: str,              # What to do
    target_type: str,         # What entity
    target_id: int,           # Which one
    data: dict = {},          # Action-specific data
    create_note: bool = True  # Auto-log action
) -> dict
```

**Parameters**:

### action (str)
The operation to perform:

**Task Actions**:
- `"start_task"` - Mark task as in_progress
- `"complete_task"` - Mark complete, check milestone
- `"cancel_task"` - Mark cancelled
- `"pause_task"` - Mark paused (for subtasks)
- `"resume_task"` - Resume paused task
- `"update_priority"` - Change task priority

**Flow Actions**:
- `"link_flows"` - Associate task with flows
- `"add_flow"` - Add single flow to task
- `"remove_flow"` - Remove flow from task

**File Actions**:
- `"add_file"` - Register new file
- `"update_file"` - Update file checksum
- `"delete_file"` - Mark file as deleted

**Function Actions**:
- `"register_function"` - Add function to database
- `"update_function"` - Update function metadata
- `"add_interaction"` - Record function dependency

**Note Actions**:
- `"add_note"` - Create standalone note

### target_type (str)
Entity type: `"task"`, `"subtask"`, `"sidequest"`, `"file"`, `"function"`, `"milestone"`

### target_id (int)
ID of the target entity

### data (dict)
Action-specific data:

```python
# For "start_task"
data = {}  # No additional data needed

# For "complete_task"
data = {}  # No additional data needed

# For "link_flows"
data = {"flow_ids": [1, 3, 5]}

# For "update_priority"
data = {"priority": "high"}

# For "add_file"
data = {
    "path": "src/matrix.py",
    "language": "Python",
    "checksum": "abc123..."
}

# For "register_function"
data = {
    "name": "matrix_multiply",
    "file_id": 1,
    "signature": "matrix_multiply(a, b) -> Matrix",
    "is_pure": True,
    "parameters": ["a: Matrix", "b: Matrix"]
}
```

### create_note (bool)
If true, automatically creates a note logging the action

**Returns**:

### Success Response
```json
{
  "success": true,
  "action": "complete_task",
  "target": {
    "type": "task",
    "id": 5,
    "name": "Implement matrix operations"
  },
  "changes": {
    "status": {
      "old": "in_progress",
      "new": "completed"
    },
    "completed_at": "2025-11-05T15:00:00",
    "milestone_progress": {
      "completed": 4,
      "total": 8,
      "progress": 0.5
    }
  },
  "side_effects": {
    "milestone_completed": false,
    "tasks_unblocked": [],
    "parent_task_resumed": null
  },
  "note_created": true,
  "note_id": 42
}
```

### Link Flows Response
```json
{
  "success": true,
  "action": "link_flows",
  "target": {"type": "task", "id": 5},
  "changes": {
    "flow_ids": {
      "old": [1],
      "new": [1, 3, 5]
    },
    "flows_added": [
      {"id": 3, "name": "Validation Flow"},
      {"id": 5, "name": "Performance"}
    ]
  },
  "note_created": false
}
```

### Error Response
```json
{
  "success": false,
  "action": "complete_task",
  "target": {"type": "task", "id": 5},
  "error": "Cannot complete task with pending subtasks",
  "error_code": "SUBTASKS_PENDING",
  "details": {
    "pending_subtasks": [
      {"id": 1, "name": "Fix validation bug"}
    ]
  }
}
```

**Internally Calls**:

Based on action:
- `"start_task"` → `update_task_status(id, "in_progress")`
- `"complete_task"` → `update_task_status(id, "completed")` + `get_milestone_progress()` + check completion
- `"link_flows"` → `link_task_to_flows(id, flow_ids)` + `validate_flow_ids()`
- `"add_file"` → `add_file(data)` + optionally link to current task
- `"register_function"` → `register_function(data)` + `add_interaction()` if dependencies
- Always: `create_note()` if create_note=true

**Used By**:
- `project_task_update` directive
- `project_task_complete` directive
- `project_subtask_complete` directive
- `project_file_write` directive
- Any directive that modifies project state

**Error Handling**:
- Validates state transitions (e.g., can't complete task with pending subtasks)
- Returns descriptive error codes
- Provides actionable error details
- Logs all errors

**is_tool**: `true`

---

## 3. batch_update_progress()

**Purpose**: Update multiple project items atomically. Used after code generation or bulk operations to ensure consistency.

**Signature**:
```python
def batch_update_progress(
    updates: list[dict],      # List of update operations
    transaction: bool = True, # All-or-nothing commit
    continue_on_error: bool = False,  # Stop on first error or continue
    rollback_on_partial_failure: bool = True  # Rollback if any fail
) -> dict
```

**Parameters**:

### updates (list[dict])
List of update operations. Each dict contains:
- `action` (str): Operation to perform
- `target_type` (str): Optional entity type
- `target_id` (int): Optional entity ID
- `data` (dict): Operation-specific data

**Example**:
```python
updates = [
    # 1. Add file
    {
        "action": "add_file",
        "data": {
            "path": "src/matrix.py",
            "language": "Python",
            "checksum": "abc123...",
            "project_id": 1
        }
    },
    # 2. Register functions in that file
    {
        "action": "register_function",
        "data": {
            "name": "matrix_multiply",
            "file_id": 1,
            "is_pure": True,
            "signature": "matrix_multiply(a: Matrix, b: Matrix) -> Matrix"
        }
    },
    {
        "action": "register_function",
        "data": {
            "name": "validate_dimensions",
            "file_id": 1,
            "is_pure": True,
            "signature": "validate_dimensions(a: Matrix, b: Matrix) -> bool"
        }
    },
    # 3. Add interaction
    {
        "action": "add_interaction",
        "data": {
            "source_function_id": 1,
            "target_function_id": 2,
            "interaction_type": "call"
        }
    },
    # 4. Link task to flows
    {
        "action": "link_flows",
        "target_type": "task",
        "target_id": 5,
        "data": {"flow_ids": [1, 3]}
    },
    # 5. Update task status
    {
        "action": "update_task_status",
        "target_type": "task",
        "target_id": 5,
        "data": {"status": "in_progress"}
    },
    # 6. Add note
    {
        "action": "add_note",
        "data": {
            "content": "Implemented matrix operations with validation",
            "note_type": "completion",
            "reference_table": "tasks",
            "reference_id": 5
        }
    }
]

result = batch_update_progress(updates, transaction=True)
```

### transaction (bool)
- `true` (default): All updates in single DB transaction (all succeed or all rollback)
- `false`: Updates applied independently (some can fail, others succeed)

### continue_on_error (bool)
- `false` (default): Stop on first error
- `true`: Continue processing remaining updates, collect all errors

### rollback_on_partial_failure (bool)
- `true` (default): If any update fails and transaction=true, rollback all
- `false`: Keep successful updates even if some fail (requires transaction=false)

**Returns**:

### Success Response
```json
{
  "success": true,
  "updates_requested": 7,
  "updates_applied": 7,
  "updates_failed": 0,
  "transaction_committed": true,
  "execution_time_ms": 45,
  "summary": {
    "files_added": 1,
    "functions_registered": 2,
    "interactions_added": 1,
    "flows_linked": 1,
    "task_status_updated": 1,
    "notes_created": 1
  },
  "changes": [
    {"action": "add_file", "success": true, "file_id": 1},
    {"action": "register_function", "success": true, "function_id": 1},
    {"action": "register_function", "success": true, "function_id": 2},
    {"action": "add_interaction", "success": true, "interaction_id": 1},
    {"action": "link_flows", "success": true, "task_id": 5},
    {"action": "update_task_status", "success": true, "task_id": 5},
    {"action": "add_note", "success": true, "note_id": 42}
  ],
  "errors": []
}
```

### Partial Failure Response (continue_on_error=true)
```json
{
  "success": false,
  "updates_requested": 7,
  "updates_applied": 5,
  "updates_failed": 2,
  "transaction_committed": false,
  "transaction_rolled_back": true,
  "summary": {
    "files_added": 1,
    "functions_registered": 1,
    "interactions_added": 0,
    "flows_linked": 1,
    "task_status_updated": 1,
    "notes_created": 1
  },
  "changes": [
    {"action": "add_file", "success": true, "file_id": 1},
    {"action": "register_function", "success": true, "function_id": 1},
    {"action": "register_function", "success": false, "error": "Duplicate function name"},
    {"action": "add_interaction", "success": false, "error": "Function ID 2 not found"},
    {"action": "link_flows", "success": true, "task_id": 5},
    {"action": "update_task_status", "success": true, "task_id": 5},
    {"action": "add_note", "success": true, "note_id": 42}
  ],
  "errors": [
    {
      "update_index": 2,
      "action": "register_function",
      "error": "Duplicate function name 'matrix_multiply' in file",
      "error_code": "DUPLICATE_FUNCTION"
    },
    {
      "update_index": 3,
      "action": "add_interaction",
      "error": "Target function ID 2 does not exist",
      "error_code": "FOREIGN_KEY_VIOLATION"
    }
  ]
}
```

**Internally Calls**:
- Starts database transaction (if transaction=true)
- For each update:
  - Validates update format
  - Calls appropriate helper based on action
  - Collects results
- Commits or rolls back transaction based on results
- Generates summary statistics

**Used By**:
- `project_update_db` directive (PRIMARY - after code generation)
- `project_file_write` directive (file + function registration)
- Any directive doing multiple related updates
- Bulk import/migration operations

**Error Handling**:
- Validates all updates before starting transaction
- Stops on first error (unless continue_on_error=true)
- Provides detailed error information per update
- Atomic rollback if transaction=true

**Performance**:
- Single database connection for all updates
- Transaction overhead minimal
- Typical execution: 20-100ms for 5-10 updates

**is_tool**: `true`

---

## 4. query_project_state()

**Purpose**: Flexible SQL-like query interface for complex project queries. Provides powerful filtering and joining capabilities without writing SQL.

**Signature**:
```python
def query_project_state(
    entity: str,              # What table to query
    filters: dict = {},       # WHERE conditions
    joins: list[str] = [],    # Relations to include
    sort: str = None,         # ORDER BY
    limit: int = None,        # LIMIT
    offset: int = 0           # OFFSET (pagination)
) -> list[dict]
```

**Parameters**:

### entity (str)
Primary table to query:
- `"tasks"` - Tasks table
- `"subtasks"` - Subtasks table
- `"sidequests"` - Sidequests table
- `"files"` - Files table
- `"functions"` - Functions table
- `"flows"` - Flows table
- `"themes"` - Themes table
- `"milestones"` - Milestones table
- `"notes"` - Notes table

### filters (dict)
WHERE-like conditions with operators:

**Simple Equality**:
```python
filters = {
    "status": "in_progress",
    "priority": "high",
    "milestone_id": 2
}
```

**Comparison Operators**:
```python
filters = {
    "priority": {"gte": 3},              # >=
    "created_at": {"gt": "2025-11-01"},  # >
    "task_count": {"lte": 5},            # <=
    "version": {"lt": 3}                 # <
}
```

**List/Pattern Operators**:
```python
filters = {
    "status": {"in": ["pending", "in_progress"]},  # IN
    "name": {"like": "%matrix%"},                   # LIKE
    "path": {"not_like": "%test%"},                 # NOT LIKE
    "flow_id": {"not_in": [1, 5]}                   # NOT IN
}
```

**Date/Time Filters**:
```python
filters = {
    "updated_since": "2025-11-01",      # Shorthand for updated_at > date
    "created_before": "2025-11-05",     # Shorthand for created_at < date
    "updated_in_last": {"days": 7}      # Last N days
}
```

**JSON Array Filters** (for flow_ids):
```python
filters = {
    "has_flow": 3,                      # JSON array contains flow_id 3
    "has_any_flow": [1, 3, 5],         # Contains any of these flows
    "has_all_flows": [1, 3]            # Contains all of these flows
}
```

### joins (list[str])
Relations to include (LEFT JOIN):
- `"milestone"` - Join milestone for tasks
- `"flows"` - Join flows (via flow_ids or file_flows)
- `"themes"` - Join themes (via flows)
- `"files"` - Join files for functions
- `"functions"` - Join functions for files
- `"items"` - Join items for tasks/subtasks/sidequests
- `"notes"` - Join notes for any entity
- `"interactions"` - Join function dependencies

### sort (str)
ORDER BY clause:
- `"created_at DESC"` - Newest first
- `"priority DESC, created_at ASC"` - Multiple fields
- `"name ASC"` - Alphabetical

### limit (int)
Maximum results to return (pagination)

### offset (int)
Skip first N results (pagination)

**Returns**:

### Example 1: High-Priority Tasks in Milestone
```python
tasks = query_project_state(
    entity="tasks",
    filters={
        "priority": "high",
        "milestone_id": 2,
        "status": {"in": ["pending", "in_progress"]}
    },
    joins=["flows", "items"],
    sort="priority DESC, created_at ASC",
    limit=10
)
```

**Result**:
```json
[
  {
    "id": 7,
    "name": "Optimize matrix multiplication",
    "description": "Improve performance of matrix ops",
    "status": "pending",
    "priority": "high",
    "milestone_id": 2,
    "milestone": {
      "id": 2,
      "name": "Core Development",
      "status": "in_progress"
    },
    "flow_ids": "[1, 5]",
    "flows": [
      {"id": 1, "name": "Matrix Computation"},
      {"id": 5, "name": "Performance Optimization"}
    ],
    "items": [
      {"id": 1, "name": "Profile current implementation", "status": "pending"},
      {"id": 2, "name": "Implement Strassen algorithm", "status": "pending"}
    ],
    "created_at": "2025-11-03T10:00:00",
    "updated_at": "2025-11-03T10:00:00"
  }
]
```

### Example 2: Recently Modified Files in Flow
```python
files = query_project_state(
    entity="files",
    filters={
        "has_flow": 3,
        "updated_since": "2025-11-01",
        "language": "Python"
    },
    joins=["functions"],
    sort="updated_at DESC",
    limit=20
)
```

**Result**:
```json
[
  {
    "id": 1,
    "path": "src/matrix.py",
    "language": "Python",
    "checksum": "abc123...",
    "created_at": "2025-11-02T10:20:00",
    "updated_at": "2025-11-05T14:30:00",
    "functions": [
      {
        "id": 1,
        "name": "matrix_multiply",
        "signature": "matrix_multiply(a: Matrix, b: Matrix) -> Matrix",
        "is_pure": true
      },
      {
        "id": 2,
        "name": "validate_dimensions",
        "signature": "validate_dimensions(a: Matrix, b: Matrix) -> bool",
        "is_pure": true
      }
    ]
  }
]
```

### Example 3: Functions with Dependencies
```python
functions = query_project_state(
    entity="functions",
    filters={
        "is_pure": true,
        "file_id": 1
    },
    joins=["files", "interactions"],
    sort="name ASC"
)
```

**Result**:
```json
[
  {
    "id": 1,
    "name": "matrix_multiply",
    "file_id": 1,
    "signature": "matrix_multiply(a: Matrix, b: Matrix) -> Matrix",
    "is_pure": true,
    "files": {
      "id": 1,
      "path": "src/matrix.py",
      "language": "Python"
    },
    "interactions": [
      {
        "id": 1,
        "source_function_id": 1,
        "target_function_id": 2,
        "interaction_type": "call",
        "target_function_name": "validate_dimensions"
      }
    ],
    "created_at": "2025-11-05T14:15:00"
  }
]
```

**Internally Calls**:
- Builds SQL query dynamically based on parameters
- Validates entity and filter parameters
- Performs JOINs for requested relations
- Sanitizes all inputs (SQL injection prevention)
- Returns formatted results

**Used By**:
- Directives needing complex filtering
- AI advanced queries
- Reporting and analytics
- Custom views and dashboards

**Error Handling**:
- Returns empty list if no matches
- Validates entity name (must be valid table)
- Validates filter operators
- Logs invalid queries

**Security**:
- All inputs sanitized
- Parameterized queries only
- No raw SQL execution
- Read-only (no UPDATE/DELETE)

**Performance**:
- Uses indexes where available
- LIMIT prevents large result sets
- JOIN optimization for common patterns

**is_tool**: `true`

---

## 5. get_work_context()

**Purpose**: Get complete context for resuming work. Single call retrieves task/sidequest + flows + files + functions + interactions. Optimized for session resumption.

**Signature**:
```python
def get_work_context(
    work_item_type: str,  # "task", "subtask", "sidequest"
    work_item_id: int,
    include_interactions: bool = True,
    include_history: bool = False  # Include note history
) -> dict
```

**This function is fully specified in `additional-helpers-project.md` (Flow-Based Work Context section) but elevated to Layer 2 as a primary generic tool.**

**Summary**:
- Returns: work_item + milestone + flows + themes + files (sorted) + functions + interactions
- Replaces: 6-8 separate helper calls
- Primary use: `project_auto_resume` directive

**is_tool**: `true`

---

## Generic Tools Summary

| Tool | Lines of Code (Est.) | Helpers Called | Primary Directive |
|------|----------------------|----------------|-------------------|
| `get_current_progress()` | ~200 | 5-15 (dynamic) | `aifp_status` |
| `update_project_state()` | ~150 | 2-5 per action | `project_task_update` |
| `batch_update_progress()` | ~100 | N (one per update) | `project_update_db` |
| `query_project_state()` | ~250 | Dynamic SQL builder | Advanced queries |
| `get_work_context()` | ~150 | 6-8 | `project_auto_resume` |

**Total Generic Tools**: 5
**Total Estimated LOC**: ~850 lines
**Total Specific Helpers Available**: 79 project helpers

---

## Implementation Notes

### Dependencies
All generic tools depend on Layer 3 specific helpers. No circular dependencies.

### Testing Strategy
- Unit tests for each generic tool
- Integration tests for directive workflows
- Performance tests for batch operations
- Edge case tests for error handling

### Versioning
Generic tools maintain backward compatibility. Breaking changes require new function names or version parameters.

---

**End of Project Generic Tools Specification**
