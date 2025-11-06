# AIFP Helper Function Architecture

**Version**: 1.0
**Last Updated**: 2025-11-05
**Status**: Design Phase - Specification Complete, Implementation Pending

---

## Overview

This document describes the **three-tier helper function architecture** for the AIFP (AI Functional Programming) system. The architecture separates concerns into directives (high-level orchestration), generic tools (MCP-exposed interfaces), specific helpers (database operations), and internal sub-helpers (utility functions).

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: DIRECTIVES                                            │
│  - High-level workflow orchestration                            │
│  - Defined in src/aifp/reference/directives/*.md               │
│  - Registered in docs/directives-json/directives-*.json        │
├─────────────────────────────────────────────────────────────────┤
│  Examples: aifp_status, project_auto_resume,                    │
│           project_task_create, fp_purity_check                  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Uses
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: GENERIC TOOLS (MCP-Exposed)                          │
│  - High-level orchestrator functions                            │
│  - is_tool=true (exposed via MCP server)                       │
│  - Called directly by AI and directives                         │
│  - Single entry points for common operations                    │
├─────────────────────────────────────────────────────────────────┤
│  Examples: get_current_progress(), update_project_state(),      │
│           get_work_context(), batch_update_progress()           │
│                                                                  │
│  Location: src/aifp/helpers/{database}/tools/*.py              │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Orchestrates
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: SPECIFIC HELPERS (Available to AI)                   │
│  - Granular CRUD operations                                     │
│  - is_tool=false, is_sub_helper=false                          │
│  - Available to AI via MCP but not primary interface            │
│  - Called by generic tools and directives                       │
├─────────────────────────────────────────────────────────────────┤
│  Examples: get_task_by_id(), update_task_status(),              │
│           link_task_to_flows(), get_flows_for_task()            │
│                                                                  │
│  Location: src/aifp/helpers/{database}/tools/*.py              │
│  Total Count: ~195 helpers across 4 databases                   │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Uses
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: INTERNAL SUB-HELPERS (Not exposed to AI)             │
│  - Pure utility functions                                       │
│  - is_tool=false, is_sub_helper=true                           │
│  - Used only by helpers in Layer 3                              │
│  - Not called directly by AI or directives                      │
├─────────────────────────────────────────────────────────────────┤
│  Examples: validate_flow_ids(), infer_action(),                 │
│           compute_checksum(), parse_function_signature()        │
│                                                                  │
│  Location: src/aifp/helpers/{database}/internal/*.py           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. **Separation of Concerns**
- **Directives**: Define workflows and business logic
- **Generic Tools**: Provide intuitive, high-level interfaces
- **Specific Helpers**: Perform atomic database operations
- **Sub-Helpers**: Handle low-level utilities

### 2. **Functional Programming**
- All helpers are pure functions where possible
- Database operations return Results (Ok/Err) for error handling
- No side effects beyond database updates and logging
- Immutable data structures preferred

### 3. **Composability**
- Generic tools compose specific helpers
- Specific helpers compose sub-helpers
- Each layer can be tested independently
- Clear dependency flow (no circular dependencies)

### 4. **MCP Exposure Strategy**
- **Layer 2 (Generic Tools)**: Primary MCP interface (is_tool=true)
- **Layer 3 (Specific Helpers)**: Available via MCP but not primary (is_tool=false by default)
- **Layer 4 (Sub-Helpers)**: NOT exposed via MCP (is_tool=false, is_sub_helper=true)

### 5. **Efficiency**
- Generic tools batch multiple operations to reduce round trips
- Context helpers (like `get_work_context()`) replace 6+ separate queries with single call
- Database transactions used for multi-step operations

---

## Current State: Specific Helpers (Layer 3)

We have designed **~195 specific helper functions** across 4 databases:

| Database | Helper Count | Status | Document |
|----------|--------------|--------|----------|
| **project.db** | ~79 functions | ✅ Complete | `docs/helpers/additional-helpers-project.md` |
| **user_preferences.db** | ~39 functions | ✅ Complete | `docs/helpers/additional-helpers-preferences.md` |
| **user_directives.db** | ~32 functions | ✅ Complete | `docs/helpers/additional-helpers-user-directives.md` |
| **aifp_core.db (MCP)** | ~55 functions | ✅ Complete | `docs/helpers/additional-helpers-mcp.md` |

### Helper Categories (Project DB Example)

**Project Metadata** (11 functions):
- Getters: `get_project_metadata()`, `get_project_summary()`
- Setters: `update_project_metadata()`, `update_blueprint_checksum()`
- Blueprint Sync: `blueprint_has_changed()`, `check_blueprint_sync()`, `sync_blueprint_checksum()`

**Code Structure** (16 functions):
- Files: `add_file()`, `get_file_by_path()`, `update_file_checksum()`
- Functions: `register_function()`, `get_function_by_name()`, `get_functions_by_file()`
- Interactions: `add_interaction()`, `get_function_dependencies()`

**Flow-Based Work Context** (10 functions) - **NEW**:
- Flow Linking: `link_task_to_flows()`, `add_flow_to_task()`, `remove_flow_from_task()`
- Context Retrieval: `get_work_context()`, `get_recent_files_for_task()`, `get_recent_functions_for_task()`
- Queries: `get_flows_for_task()`, `get_tasks_by_flow()`
- Utilities: `validate_flow_ids()`, `infer_action()`

**Task Management** (14 functions):
- Getters: `get_task_by_id()`, `get_tasks_by_status()`, `get_task_hierarchy()`
- Setters: `create_task()`, `update_task_status()`, `create_subtask()`

**Organization** (11 functions):
- Themes: `get_all_themes()`, `create_theme()`, `link_theme_to_flow()`
- Flows: `get_all_flows()`, `create_flow()`, `get_files_in_flow()`

**Completion Tracking** (7 functions):
- Completion Path: `get_completion_path()`, `get_current_stage()`
- Milestones: `get_milestone_progress()`, `complete_milestone()`

**Notes & Context** (5 functions):
- `create_note()`, `get_notes_for_task()`, `search_notes()`

**Git Integration** (7 functions):
- `get_active_branches()`, `record_merge()`, `get_merge_history()`

**Analytics** (3 functions):
- `get_project_metrics()`, `get_bottlenecks()`

---

## Proposed: Generic Tools (Layer 2)

These are **high-level orchestrator functions** that AI and directives call directly. They compose multiple specific helpers into single-call operations.

### 1. `get_current_progress()`

**Purpose**: Single entry point for all status queries

**Signature**:
```python
def get_current_progress(
    scope: str = "full",           # "full", "task", "milestone", "files", "functions", "flows"
    detail_level: str = "summary", # "summary", "detailed", "minimal"
    filters: dict = {}             # Optional WHERE-like filters
) -> dict
```

**Scope Options**:
- `"full"` - Everything (completion path + milestones + tasks + files + functions)
- `"task"` - Current task context (delegates to `get_work_context()`)
- `"milestone"` - Current milestone progress
- `"files"` - Recent file changes
- `"functions"` - Function inventory
- `"flows"` - Flow/theme organization

**Detail Levels**:
- `"minimal"` - Counts and current status only
- `"summary"` - Counts + current work + next action
- `"detailed"` - Full context with files, functions, flows, history

**Example Usage**:
```python
# Called by aifp_status directive
status = get_current_progress(scope="full", detail_level="summary")

# AI asks "what am I working on?"
context = get_current_progress(scope="task", detail_level="detailed")

# AI asks "how many tasks are left?"
counts = get_current_progress(scope="milestone", detail_level="minimal")
```

**Returns**:
```json
{
  "project": {
    "name": "MatrixCalculator",
    "status": "active",
    "version": 3
  },
  "completion_path": {
    "current_stage": "Development",
    "stage_progress": 0.65,
    "overall_progress": 0.35
  },
  "current_work": {
    "type": "task",
    "id": 5,
    "name": "Implement matrix operations",
    "status": "in_progress",
    "progress": "3/8 items",
    "flows": ["Matrix Computation", "Core Math"],
    "recent_files": ["src/matrix.py"],
    "recent_functions": ["matrix_multiply", "validate_dimensions"]
  },
  "next_action": "Complete current item: 'Add matrix transpose'"
}
```

**Internally Calls**:
- `get_project_metadata()`
- `get_completion_path()`
- `get_current_stage()`
- `get_work_context()` (if scope="task")
- `get_tasks_by_status()` (if scope includes tasks)
- `get_recent_files_for_task()` (if detail_level="detailed")

**Used By**:
- `aifp_status` directive (primary)
- AI direct queries ("what's the status?")
- Session initialization

---

### 2. `update_project_state()`

**Purpose**: Single entry point for common update operations

**Signature**:
```python
def update_project_state(
    action: str,              # "start_task", "complete_task", "link_flows", etc.
    target_type: str,         # "task", "subtask", "sidequest", "file", "function"
    target_id: int,           # ID of target entity
    data: dict = {},          # Action-specific data
    create_note: bool = True  # Auto-log action
) -> dict
```

**Actions**:
- `"start_task"` → `update_task_status(id, "in_progress")`
- `"complete_task"` → `update_task_status(id, "completed")` + check milestone
- `"cancel_task"` → `update_task_status(id, "cancelled")`
- `"link_flows"` → `link_task_to_flows(id, data["flow_ids"])`
- `"add_file"` → `add_file(data)` + optionally link to task
- `"register_function"` → `register_function(data)` + update interactions
- `"update_priority"` → `update_task_priority(id, data["priority"])`

**Example Usage**:
```python
# Start working on task
update_project_state(
    action="start_task",
    target_type="task",
    target_id=5,
    create_note=True
)

# Complete task and check milestone
update_project_state(
    action="complete_task",
    target_type="task",
    target_id=5,
    create_note=True
)

# Link task to flows
update_project_state(
    action="link_flows",
    target_type="task",
    target_id=5,
    data={"flow_ids": [1, 3]},
    create_note=False
)
```

**Returns**:
```json
{
  "success": true,
  "action": "complete_task",
  "target": {"type": "task", "id": 5, "name": "Implement matrix ops"},
  "changes": {
    "status": {"old": "in_progress", "new": "completed"},
    "milestone_progress": {"completed": 3, "total": 8}
  },
  "note_created": true,
  "note_id": 42
}
```

**Internally Calls**:
- Various setters based on action type
- `create_note()` if create_note=true
- Validation helpers

**Used By**:
- `project_task_update` directive
- `project_task_complete` directive
- `project_file_write` directive (when marking tasks complete)

---

### 3. `batch_update_progress()`

**Purpose**: Update multiple items in single atomic transaction

**Signature**:
```python
def batch_update_progress(
    updates: list[dict],      # List of update operations
    transaction: bool = True, # All-or-nothing commit
    continue_on_error: bool = False  # Stop on first error or continue
) -> dict
```

**Update Format**:
```python
updates = [
    {
        "action": "add_file",
        "data": {"path": "src/matrix.py", "language": "Python"}
    },
    {
        "action": "register_function",
        "data": {"name": "matrix_multiply", "file_id": 1, "is_pure": True}
    },
    {
        "action": "register_function",
        "data": {"name": "validate_dimensions", "file_id": 1, "is_pure": True}
    },
    {
        "action": "add_interaction",
        "data": {"source_fn_id": 1, "target_fn_id": 2, "type": "call"}
    },
    {
        "action": "link_flows",
        "target_id": 5,
        "data": {"flow_ids": [1, 3]}
    },
    {
        "action": "create_note",
        "data": {"content": "Implemented matrix operations", "type": "completion"}
    }
]

result = batch_update_progress(updates, transaction=True)
```

**Returns**:
```json
{
  "success": true,
  "updates_applied": 6,
  "updates_failed": 0,
  "transaction_committed": true,
  "summary": {
    "files_added": 1,
    "functions_registered": 2,
    "interactions_added": 1,
    "flows_linked": 1,
    "notes_created": 1
  },
  "errors": []
}
```

**Transaction Behavior**:
- If `transaction=true`: All updates succeed or all rollback
- If `transaction=false`: Updates applied independently
- If `continue_on_error=true`: Continue despite failures (collect errors)

**Internally Calls**:
- Starts DB transaction
- Calls appropriate helpers for each update
- Commits or rolls back based on results

**Used By**:
- `project_update_db` directive (after code generation)
- `project_file_write` directive
- Any directive that needs multiple atomic updates

---

### 4. `query_project_state()`

**Purpose**: Flexible SQL-like query interface for complex queries

**Signature**:
```python
def query_project_state(
    entity: str,              # "tasks", "files", "functions", "flows", "notes"
    filters: dict = {},       # WHERE-like conditions
    joins: list[str] = [],    # Relations to include
    sort: str = None,         # Sort field and direction
    limit: int = None,        # Limit results
    offset: int = 0           # Pagination offset
) -> list[dict]
```

**Example Usage**:
```python
# Get high-priority pending tasks in current milestone with flows
tasks = query_project_state(
    entity="tasks",
    filters={
        "priority": "high",
        "milestone_id": 2,
        "status": "pending"
    },
    joins=["flows", "items"],
    sort="priority DESC",
    limit=10
)

# Get recently modified files in specific flow
files = query_project_state(
    entity="files",
    filters={
        "flow_id": 3,
        "updated_since": "2025-11-01"
    },
    joins=["functions"],
    sort="updated_at DESC",
    limit=20
)
```

**Returns**:
```json
[
  {
    "id": 7,
    "name": "Optimize matrix multiplication",
    "priority": "high",
    "status": "pending",
    "milestone": {"id": 2, "name": "Core Development"},
    "flows": [
      {"id": 1, "name": "Matrix Computation"},
      {"id": 5, "name": "Performance Optimization"}
    ],
    "items": [
      {"id": 1, "name": "Profile implementation", "status": "pending"}
    ]
  }
]
```

**Filter Operators**:
```python
filters = {
    "status": "in_progress",              # Equals
    "priority": {"gte": 3},               # Greater than or equal
    "created_at": {"gt": "2025-11-01"},  # Greater than
    "name": {"like": "%matrix%"},         # LIKE pattern
    "flow_id": {"in": [1, 3, 5]}         # IN list
}
```

**Internally Calls**:
- Builds SQL query dynamically
- Validates entity and filter parameters
- Performs JOINs based on joins parameter
- Returns sanitized results

**Used By**:
- Directives that need complex filtering
- AI advanced queries
- Reporting and analytics

---

### 5. `get_work_context()` (Already Designed)

**Purpose**: Get complete context for resuming work

This was already designed in the flow-based helpers section. It's elevated to Layer 2 as a primary generic tool.

**Signature**:
```python
def get_work_context(
    work_item_type: str,  # "task", "subtask", "sidequest"
    work_item_id: int,
    include_interactions: bool = True
) -> dict
```

**Returns**: Complete context with task + flows + files + functions + interactions

**Used By**:
- `project_auto_resume` directive (PRIMARY)
- `aifp_status` directive
- `get_current_progress()` (when scope="task")

---

## Generic Tools Summary

| Tool | Purpose | Primary Use | Helpers Called |
|------|---------|-------------|----------------|
| `get_current_progress()` | Status queries with flexible scope | `aifp_status` | 5-10 helpers based on scope |
| `update_project_state()` | Single-call common updates | Task lifecycle directives | 2-5 helpers per action |
| `batch_update_progress()` | Atomic multi-item updates | `project_update_db` | N helpers (one per update) |
| `query_project_state()` | Complex filtered queries | Advanced queries | Dynamic based on query |
| `get_work_context()` | Session resumption context | `project_auto_resume` | 6-8 helpers for complete context |

---

## Schema Changes Supporting This Architecture

### Recent Addition: Flow-Based Work Context

**Schema Change (v1.2)**:
- Added `flow_ids TEXT` (JSON array) to `tasks` table
- Added `flow_ids TEXT` to `sidequests` table

**Purpose**: Link tasks/sidequests to flows without junction tables

**Benefits**:
- Tasks can now reference multiple flows: `[1, 3, 5]`
- Enables `get_work_context()` to chain: Task → Flows → Files → Functions
- Supports efficient session resumption with complete context

**Example**:
```sql
-- Task with flows
INSERT INTO tasks (name, milestone_id, flow_ids)
VALUES ('Implement auth', 2, '[1, 3]');

-- Query tasks by flow using json_each
SELECT t.* FROM tasks t
WHERE EXISTS (
    SELECT 1 FROM json_each(t.flow_ids)
    WHERE value = 1  -- flow_id = 1
);
```

---

## Directory Structure

```
src/aifp/
├── reference/
│   └── directives/                    # Layer 1: Directives (MD files)
│       ├── aifp_status.md
│       ├── project_auto_resume.md
│       ├── project_task_create.md
│       └── ...
│
├── helpers/
│   ├── mcp/                           # MCP (aifp_core.db)
│   │   ├── tools/                     # Layer 2 & 3
│   │   │   ├── directive_tools.py     # Generic + Specific
│   │   │   └── helper_tools.py
│   │   └── internal/                  # Layer 4: Sub-helpers
│   │       └── validation.py
│   │
│   ├── project/                       # Project (project.db)
│   │   ├── tools/                     # Layer 2 & 3
│   │   │   ├── progress_tools.py      # Generic: get_current_progress()
│   │   │   ├── project_meta_tools.py  # Specific: get_project_metadata()
│   │   │   ├── file_tools.py
│   │   │   ├── function_tools.py
│   │   │   ├── task_tools.py
│   │   │   ├── flow_context_tools.py  # get_work_context()
│   │   │   └── ...
│   │   └── internal/                  # Layer 4: Sub-helpers
│   │       ├── validation.py          # validate_flow_ids()
│   │       ├── checksums.py
│   │       └── blueprint.py
│   │
│   ├── user_preferences/              # User preferences
│   │   ├── tools/
│   │   └── internal/
│   │
│   └── user_directives/               # User directives/automation
│       ├── tools/
│       └── internal/
│
docs/
├── helpers/
│   ├── helper-architecture.md         # THIS FILE
│   ├── additional-helpers-project.md  # Spec: 79 project helpers
│   ├── additional-helpers-mcp.md      # Spec: 55 MCP helpers
│   ├── additional-helpers-preferences.md  # Spec: 39 pref helpers
│   └── additional-helpers-user-directives.md  # Spec: 32 user helpers
│
└── directives-json/
    ├── directives-project.json        # Directive definitions
    ├── directives-fp-core.json
    ├── directives-user-system.json
    └── helpers_parsed.json            # Helper registry (to be updated)
```

---

## Implementation Status

### ✅ Completed (Design Phase)

**Layer 3: Specific Helpers** - All ~195 helpers fully specified:
- ✅ Project helpers (79) - `docs/helpers/additional-helpers-project.md`
- ✅ MCP helpers (55) - `docs/helpers/additional-helpers-mcp.md`
- ✅ Preferences helpers (39) - `docs/helpers/additional-helpers-preferences.md`
- ✅ User directives helpers (32) - `docs/helpers/additional-helpers-user-directives.md`

**Schema Updates**:
- ✅ `project.db` schema v1.2 - Added flow_ids to tasks/sidequests

### 🔄 In Progress

**Layer 2: Generic Tools** - Proposed but not yet specified in detail:
- 🔄 `get_current_progress()` - Architecture defined, needs full spec
- 🔄 `update_project_state()` - Architecture defined, needs full spec
- 🔄 `batch_update_progress()` - Architecture defined, needs full spec
- 🔄 `query_project_state()` - Architecture defined, needs full spec
- ✅ `get_work_context()` - Fully specified in project helpers

**Documentation**:
- 🔄 Directive MD files need updates for flow_ids schema changes
- 🔄 Directive JSON files need helper references

### ⏳ Pending (Implementation Phase)

**Code Implementation**:
- ⏳ Layer 4: Internal sub-helpers
- ⏳ Layer 3: Specific helpers (~195 functions)
- ⏳ Layer 2: Generic tools (~4-5 functions)
- ⏳ MCP server integration
- ⏳ Testing framework

**Documentation Updates**:
- ⏳ Update `helpers_parsed.json` with all new helpers
- ⏳ Update directive MD files (3 critical: task_create, auto_resume, sidequest_create)
- ⏳ Update directive JSON files with helper references

---

## Next Steps

### Phase 1: Complete Generic Tools Specification
1. Flesh out remaining generic tools (get_current_progress, update_project_state, etc.)
2. Design similar generic tools for other databases (preferences, user_directives, MCP)
3. Document all generic tools in detail with examples

### Phase 2: Update JSON Registries
1. Add all ~195 specific helpers to `helpers_parsed.json`
2. Add generic tools to `helpers_parsed.json`
3. Update directive JSON files with helper references

### Phase 3: Update Directive Documentation
1. Update 3 critical directive MD files (task_create, auto_resume, sidequest_create)
2. Update all directive JSON entries with flow_ids support
3. Ensure consistency across MD and JSON

### Phase 4: Implementation
1. Implement Layer 4 (internal sub-helpers)
2. Implement Layer 3 (specific helpers)
3. Implement Layer 2 (generic tools)
4. MCP server integration
5. Testing and validation

---

## Design Patterns & Conventions

### Naming Conventions

**Generic Tools** (Layer 2):
- Action-oriented, broad scope
- Pattern: `{verb}_{domain}_{object}()`
- Examples: `get_current_progress()`, `update_project_state()`, `batch_update_progress()`

**Specific Helpers** (Layer 3):
- Entity-specific, CRUD operations
- Getters: `get_{entity}_by_{field}()`, `get_all_{entities}()`
- Setters: `update_{entity}_{field}()`, `create_{entity}()`
- Linkers: `link_{entity}_to_{related}()`, `add_{related}_to_{entity}()`
- Examples: `get_task_by_id()`, `update_task_status()`, `link_task_to_flows()`

**Sub-Helpers** (Layer 4):
- Descriptive, utility-focused
- Pattern: `{verb}_{noun}()`
- Examples: `validate_flow_ids()`, `infer_action()`, `compute_checksum()`

### Return Value Patterns

**Success/Failure**:
```python
# Success
{"success": true, "data": {...}, "message": "Operation completed"}

# Failure
{"success": false, "error": "Error message", "code": "ERROR_CODE"}
```

**Lists**:
```python
# Found
[{...}, {...}]

# Not found
[]
```

**Single Entity**:
```python
# Found
{"id": 1, "name": "...", ...}

# Not found
{"found": false}
```

### Error Handling

**Principle**: Never raise exceptions from helpers

**Patterns**:
- Return empty structures (`[]`, `{}`, `{"found": false}`)
- Log warnings for invalid parameters
- Validate foreign keys before operations
- Return descriptive error dicts for failures

---

## References

### Documentation

**Helper Specifications (Layer 3 - Specific Helpers)**:
- [Project Helpers Spec](./additional-helpers-project.md) - 79 project.db helpers
- [MCP Helpers Spec](./additional-helpers-mcp.md) - 55 aifp_core.db helpers
- [Preferences Helpers Spec](./additional-helpers-preferences.md) - 39 user_preferences.db helpers
- [User Directives Helpers Spec](./additional-helpers-user-directives.md) - 32 user_directives.db helpers

**Generic Tools (Layer 2 - Orchestrators)**:
- [Project Generic Tools](./generic-tools-project.md) - 5 orchestrator tools
- [MCP Generic Tools](./generic-tools-mcp.md) - 4 orchestrator tools

**Tool Classification**:
- [Helper Tool Classification](./helper-tool-classification.md) - Which helpers are MCP tools vs internal

### Schemas
- [Project DB Schema](../../src/aifp/database/schemas/project.sql) - v1.2 (with flow_ids)
- [User Preferences Schema](../../src/aifp/database/schemas/user_preferences.sql)
- [User Directives Schema](../../src/aifp/database/schemas/user_directives.sql)
- [MCP Core Schema](../../src/aifp/database/schemas/aifp_core.sql)

### Implementation Plans
- [Phase 1: MCP Server Bootstrap](../implementation-plans/phase-1-mcp-server-bootstrap.md)
- [Overview: All Phases](../implementation-plans/overview-all-phases.md)

---

**End of Architecture Document**

*This document will be updated as the design evolves and implementation progresses.*
