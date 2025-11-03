# Additional Project Database Helpers (project.db)

**Purpose**: Comprehensive getters and setters for all project state, code tracking, task management, and organizational structures.

**Philosophy**: Enable AI to efficiently query and update project state without SQL construction. Provide complete CRUD operations for all project.db tables.

**Database**: `project.db` (per-project, mutable, located in `.aifp-project/`)

**Status**: 🔵 Proposed (Not Yet Implemented)

---

## Table of Contents

1. [Project Metadata Tools](#project-metadata-tools)
2. [Code Structure Tools](#code-structure-tools)
3. [Organization Tools](#organization-tools)
4. [Task Management Tools](#task-management-tools)
5. [Completion Tracking Tools](#completion-tracking-tools)
6. [Notes & Context Tools](#notes--context-tools)
7. [Git Integration Tools](#git-integration-tools)
8. [Batch & Analytics Tools](#batch--analytics-tools)

---

## Project Metadata Tools

**Table**: `project` - High-level project metadata (ONE row per database)

**Note**: 4 existing project helpers already exist (get_project_status, get_project_context, get_status_tree, query_project_db) - marked as MCP tools

### Getters

#### `get_project_metadata()`
**Purpose**: Get complete project metadata (the single project row).

**Returns**:
```json
{
  "id": 1,
  "name": "MatrixCalculator",
  "purpose": "Fast matrix operations library",
  "goals": ["Fast computation", "No OOP", "Pure FP"],
  "status": "active",
  "version": 1,
  "blueprint_checksum": "abc123...",
  "user_directives_status": null,
  "last_known_git_hash": "def456...",
  "last_git_sync": "2025-11-02T10:00:00",
  "created_at": "2025-10-15T08:00:00"
}
```

**Use Case**: Session initialization, status reporting

**Note**: Similar to existing `get_project_context()` but focused on project table only

---

#### `get_project_name()`
**Purpose**: Quick access to project name only.

**Returns**: String project name

**Use Case**: Display, logging, quick checks

---

#### `get_project_status()`
**Purpose**: Check project status.

**Returns**: "active", "paused", "completed", "abandoned"

**Note**: Already exists as MCP tool (project.py)

---

#### `get_project_version()`
**Purpose**: Get current project version (pivot tracking).

**Returns**: Integer version number

**Use Case**: Evolution tracking, version comparison

---

#### `get_user_directives_status()`
**Purpose**: Check if user directives are initialized/active.

**Returns**: null, "in_progress", "active", "disabled"

**Use Case**: `aifp_run` checks whether to load user directives context

---

### Setters

#### `update_project_metadata(field: str, value: any)`
**Purpose**: Update specific project metadata field.

**Parameters**:
- `field` (str): Field name (purpose, goals_json, status, etc.)
- `value` (any): New value

**Returns**: `{"success": true, "updated_field": "purpose", "new_value": "..."}`

**Use Case**: `project_evolution`, `project_blueprint_update`

---

#### `update_blueprint_checksum(checksum: str)`
**Purpose**: Update blueprint checksum after ProjectBlueprint.md changes.

**Returns**: `{"success": true, "previous_checksum": "...", "new_checksum": "..."}`

**Use Case**: `project_blueprint_update` maintains sync validation

---

#### `set_user_directives_status(status: str)`
**Purpose**: Update user directives system status.

**Parameters**:
- `status` (str): null, "in_progress", "active", "disabled"

**Returns**: `{"success": true, "previous_status": "...", "new_status": "active"}`

**Use Case**: `user_directive_parse/activate/deactivate` directives

---

#### `increment_project_version()`
**Purpose**: Increment version on major pivot.

**Returns**: `{"success": true, "previous_version": 1, "new_version": 2}`

**Use Case**: `project_evolution` directive

---

## Code Structure Tools

**Tables**: `files`, `functions`, `types`, `interactions`

### File Management

#### `get_file_by_path(path: str)`
**Purpose**: Get file metadata by path.

**Returns**:
```json
{
  "id": 1,
  "path": "src/matrix.py",
  "language": "Python",
  "checksum": "abc123...",
  "project_id": 1,
  "created_at": "2025-10-15T08:00:00"
}
```

---

#### `get_all_files(language: str = None)`
**Purpose**: List all files, optionally filtered by language.

**Parameters**:
- `language` (str, optional): Filter by language

**Returns**: List of file objects

**Note**: Similar to existing `get_project_files()` but with full metadata

---

#### `get_files_by_theme(theme_id: int)`
**Purpose**: Get all files associated with theme.

**Returns**: List of file objects (via file_flows junction)

---

#### `add_file(path: str, language: str = None, checksum: str = None)`
**Purpose**: Register new file in project.

**Returns**: `{"success": true, "file_id": 1, "path": "..."}`

**Use Case**: `project_file_write` directive

---

#### `update_file_checksum(path: str, checksum: str)`
**Purpose**: Update file checksum for change detection.

**Returns**: `{"success": true, "previous_checksum": "...", "new_checksum": "..."}`

**Use Case**: After file modifications

---

#### `delete_file(path: str)`
**Purpose**: Remove file from tracking.

**Returns**: `{"success": true, "deleted_path": "..."}`

**Use Case**: `project_file_delete` directive

---

### Function Management

#### `get_function_by_name(name: str, file_path: str = None)`
**Purpose**: Get function metadata by name.

**Parameters**:
- `name` (str): Function name
- `file_path` (str, optional): Filter by file if multiple functions with same name

**Returns**:
```json
{
  "id": 1,
  "name": "matrix_multiply",
  "signature": "matrix_multiply(a: Matrix, b: Matrix) -> Matrix",
  "file_id": 1,
  "file_path": "src/matrix.py",
  "is_pure": true,
  "dependencies": ["matrix_add", "validate_dimensions"],
  "created_at": "2025-10-15T08:00:00"
}
```

---

#### `get_functions_by_file(file_path: str)`
**Purpose**: List all functions in specific file.

**Returns**: List of function objects

**Note**: Similar to existing `get_project_functions()` but filtered by file

---

#### `get_pure_functions()`
**Purpose**: Get all pure functions (is_pure = true).

**Returns**: List of function objects

**Use Case**: FP compliance analysis

---

#### `add_function(name: str, signature: str, file_id: int, is_pure: bool = false, dependencies: list = None)`
**Purpose**: Register new function.

**Returns**: `{"success": true, "function_id": 1}`

**Use Case**: `project_file_write`, `project_update_db`

---

#### `update_function_purity(function_name: str, is_pure: bool)`
**Purpose**: Mark function as pure/impure after FP compliance check.

**Returns**: `{"success": true, "function": "...", "is_pure": true}`

**Use Case**: FP directives update purity status

---

### Interaction Management

#### `get_function_interactions(function_name: str)`
**Purpose**: Get all functions that this function calls or is called by.

**Returns**:
```json
{
  "function": "matrix_multiply",
  "calls": ["matrix_add", "validate_dimensions"],
  "called_by": ["main", "process_matrices"]
}
```

**Use Case**: Dependency analysis, impact assessment

---

#### `add_interaction(source_function: str, target_function: str, interaction_type: str = "calls")`
**Purpose**: Record function interaction.

**Parameters**:
- `interaction_type` (str): "calls", "implements", "tests", etc.

**Returns**: `{"success": true, "interaction_id": 1}`

---

## Organization Tools

**Tables**: `themes`, `flows`, `flow_themes`, `file_flows`, `infrastructure`

### Theme Management

#### `get_all_themes()`
**Purpose**: List all project themes.

**Returns**:
```json
{
  "themes": [
    {
      "id": 1,
      "name": "Matrix Operations",
      "description": "Core matrix manipulation functions",
      "color": "#4CAF50"
    }
  ],
  "count": 5
}
```

---

#### `get_theme_by_name(name: str)`
**Purpose**: Get specific theme details.

**Returns**: Theme object or `{"found": false}`

---

#### `get_files_in_theme(theme_id: int)`
**Purpose**: Get all files tagged with theme.

**Returns**: List of file objects (via file_flows)

---

#### `create_theme(name: str, description: str = None, color: str = None)`
**Purpose**: Create new organizational theme.

**Returns**: `{"success": true, "theme_id": 1}`

**Use Case**: `project_theme_flow_mapping` directive

---

### Flow Management

#### `get_all_flows()`
**Purpose**: List all project flows.

**Returns**:
```json
{
  "flows": [
    {
      "id": 1,
      "name": "Matrix Computation",
      "description": "Input -> Validate -> Compute -> Output",
      "stage": "development"
    }
  ],
  "count": 3
}
```

---

#### `get_flow_by_name(name: str)`
**Purpose**: Get specific flow details.

**Returns**: Flow object with associated themes

---

#### `get_files_in_flow(flow_id: int)`
**Purpose**: Get all files in flow execution path.

**Returns**: List of file objects (via file_flows)

---

#### `create_flow(name: str, description: str = None, stage: str = "planning")`
**Purpose**: Create new execution flow.

**Returns**: `{"success": true, "flow_id": 1}`

---

#### `link_theme_to_flow(theme_id: int, flow_id: int)`
**Purpose**: Associate theme with flow.

**Returns**: `{"success": true}`

**Use Case**: `project_theme_flow_mapping`

---

### Infrastructure Management

#### `get_infrastructure_items()`
**Purpose**: List all infrastructure components.

**Returns**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "PostgreSQL Database",
      "type": "database",
      "status": "active",
      "connection_string": "..."
    }
  ]
}
```

---

#### `add_infrastructure_item(name: str, type: str, status: str = "planned", connection_string: str = None)`
**Purpose**: Register infrastructure component.

**Returns**: `{"success": true, "infrastructure_id": 1}`

---

## Task Management Tools

**Tables**: `tasks`, `subtasks`, `items`, `sidequests`

**Note**: Existing helper `get_project_tasks()` provides basic task listing

### Task Management

#### `get_task_by_id(task_id: int)`
**Purpose**: Get complete task details.

**Returns**:
```json
{
  "id": 1,
  "name": "Implement matrix multiplication",
  "description": "...",
  "status": "in_progress",
  "priority": "high",
  "completion_path_id": 1,
  "parent_task_id": null,
  "created_at": "2025-10-15T08:00:00"
}
```

---

#### `get_tasks_by_status(status: str)`
**Purpose**: Filter tasks by status.

**Parameters**:
- `status` (str): "pending", "in_progress", "completed", "blocked"

**Returns**: List of task objects

**Note**: Extends existing `get_project_tasks(status)` with full metadata

---

#### `get_tasks_by_priority(priority: str)`
**Purpose**: Filter tasks by priority.

**Parameters**:
- `priority` (str): "critical", "high", "medium", "low"

**Returns**: List of task objects

---

#### `get_subtasks(task_id: int)`
**Purpose**: Get all subtasks for task.

**Returns**: List of subtask objects

---

#### `get_task_hierarchy(task_id: int)`
**Purpose**: Get complete task hierarchy (task -> subtasks -> items).

**Returns**:
```json
{
  "task": {...},
  "subtasks": [
    {
      "subtask": {...},
      "items": [...]
    }
  ],
  "total_subtasks": 3,
  "total_items": 12
}
```

---

#### `create_task(name: str, description: str, priority: str = "medium", completion_path_id: int = None)`
**Purpose**: Create new task.

**Returns**: `{"success": true, "task_id": 1}`

**Use Case**: `project_task_create` directive

---

#### `update_task_status(task_id: int, status: str)`
**Purpose**: Update task status.

**Parameters**:
- `status` (str): "pending", "in_progress", "completed", "blocked"

**Returns**: `{"success": true, "previous_status": "...", "new_status": "..."}`

**Use Case**: `project_task_update`, `project_task_complete`

---

#### `create_subtask(task_id: int, name: str, description: str, status: str = "pending")`
**Purpose**: Create subtask under task.

**Returns**: `{"success": true, "subtask_id": 1}`

**Use Case**: `project_subtask_create` directive

---

#### `update_subtask_status(subtask_id: int, status: str)`
**Purpose**: Update subtask status.

**Returns**: `{"success": true}`

**Use Case**: `project_subtask_complete`, `project_subtask_update`

---

### Item Management

#### `get_items(subtask_id: int = None, status: str = None)`
**Purpose**: Get checklist items, optionally filtered.

**Returns**: List of item objects

---

#### `create_item(subtask_id: int, description: str, status: str = "pending")`
**Purpose**: Create checklist item under subtask.

**Returns**: `{"success": true, "item_id": 1}`

**Use Case**: `project_item_create` directive

---

#### `update_item_status(item_id: int, status: str)`
**Purpose**: Mark item as done/pending.

**Returns**: `{"success": true}`

---

### Sidequest Management

#### `get_all_sidequests(status: str = None)`
**Purpose**: List sidequests (high-priority interrupts).

**Returns**: List of sidequest objects

---

#### `get_active_sidequests()`
**Purpose**: Get in_progress sidequests only.

**Returns**: List of sidequest objects

**Use Case**: `get_status_tree()` prioritizes sidequests first

---

#### `create_sidequest(name: str, description: str, priority: str = "critical", blocks_task_id: int = None)`
**Purpose**: Create urgent sidequest.

**Parameters**:
- `blocks_task_id` (int, optional): Task this sidequest blocks

**Returns**: `{"success": true, "sidequest_id": 1}`

**Use Case**: `project_sidequest_create` directive

---

#### `complete_sidequest(sidequest_id: int)`
**Purpose**: Mark sidequest as completed.

**Returns**: `{"success": true, "unblocked_tasks": [...]}`

**Use Case**: `project_sidequest_complete` directive

---

## Completion Tracking Tools

**Tables**: `completion_path`, `milestones`

### Completion Path Management

#### `get_completion_path()`
**Purpose**: Get project completion roadmap.

**Returns**:
```json
{
  "path": [
    {
      "id": 1,
      "stage": "Development",
      "description": "Core implementation phase",
      "order": 1,
      "status": "in_progress",
      "tasks_in_stage": 5,
      "completed_tasks": 2
    }
  ],
  "current_stage": "Development",
  "total_stages": 4,
  "overall_progress": 0.35
}
```

**Use Case**: Status reporting, roadmap visualization

---

#### `get_current_stage()`
**Purpose**: Get current completion path stage.

**Returns**: Completion path stage object

---

#### `add_completion_stage(stage: str, description: str, order: int)`
**Purpose**: Add new stage to completion path.

**Returns**: `{"success": true, "stage_id": 1}`

---

#### `update_stage_status(stage_id: int, status: str)`
**Purpose**: Update completion path stage status.

**Parameters**:
- `status` (str): "pending", "in_progress", "completed"

**Returns**: `{"success": true}`

---

### Milestone Management

#### `get_all_milestones()`
**Purpose**: List all project milestones.

**Returns**:
```json
{
  "milestones": [
    {
      "id": 1,
      "name": "MVP Release",
      "description": "Minimum viable product",
      "target_date": "2025-12-01",
      "status": "in_progress",
      "completion_path_id": 2
    }
  ],
  "count": 3
}
```

---

#### `get_milestones_by_status(status: str)`
**Purpose**: Filter milestones by status.

**Returns**: List of milestone objects

---

#### `create_milestone(name: str, description: str, target_date: str = None, completion_path_id: int = None)`
**Purpose**: Create project milestone.

**Returns**: `{"success": true, "milestone_id": 1}`

**Use Case**: `project_milestone_complete` directive

---

#### `complete_milestone(milestone_id: int)`
**Purpose**: Mark milestone as completed.

**Returns**: `{"success": true, "completed_date": "2025-11-02"}`

---

## Notes & Context Tools

**Table**: `notes` - AI-written clarifications, decisions, context

### Note Management

#### `get_notes(source: str = None, directive_name: str = None, severity: str = None)`
**Purpose**: Get notes, optionally filtered.

**Parameters**:
- `source` (str, optional): "ai", "user", "system"
- `directive_name` (str, optional): Related directive
- `severity` (str, optional): "info", "warning", "error"

**Returns**: List of note objects

---

#### `get_note_by_id(note_id: int)`
**Purpose**: Get specific note details.

**Returns**: Note object

---

#### `create_note(content: str, source: str = "ai", directive_name: str = None, severity: str = "info", reference_table: str = None, reference_id: int = None)`
**Purpose**: Add note to project.

**Returns**: `{"success": true, "note_id": 1}`

**Use Case**: AI logs decisions, warnings, context

---

#### `update_note(note_id: int, content: str)`
**Purpose**: Update existing note content.

**Returns**: `{"success": true}`

---

#### `delete_note(note_id: int)`
**Purpose**: Remove note.

**Returns**: `{"success": true}`

---

## Git Integration Tools

**Tables**: `work_branches`, `merge_history`

**Note**: 10 existing Git helpers in git.py (all internal, not tools)

### Work Branches

#### `get_active_branches()`
**Purpose**: List all active AIFP work branches.

**Returns**:
```json
{
  "branches": [
    {
      "id": 1,
      "branch_name": "aifp-john-001",
      "created_by": "john",
      "purpose": "Implement matrix operations",
      "status": "active",
      "created_at": "2025-10-15T08:00:00"
    }
  ],
  "count": 2
}
```

**Note**: Similar to existing `list_active_branches()` but with full metadata

---

#### `get_branch_by_name(branch_name: str)`
**Purpose**: Get work branch details.

**Returns**: Branch object or `{"found": false}`

---

#### `create_work_branch(branch_name: str, created_by: str, purpose: str)`
**Purpose**: Register new AIFP work branch.

**Returns**: `{"success": true, "branch_id": 1}`

**Use Case**: `git_create_branch` directive

---

#### `update_branch_status(branch_name: str, status: str)`
**Purpose**: Update branch status.

**Parameters**:
- `status` (str): "active", "merged", "abandoned"

**Returns**: `{"success": true}`

---

### Merge History

#### `get_merge_history(limit: int = 50)`
**Purpose**: Get recent merge operations.

**Returns**:
```json
{
  "merges": [
    {
      "id": 1,
      "source_branch": "aifp-john-001",
      "target_branch": "main",
      "merge_type": "fast-forward",
      "conflicts_detected": false,
      "merged_at": "2025-11-01T15:00:00"
    }
  ],
  "count": 50
}
```

---

#### `record_merge(source_branch: str, target_branch: str, merge_type: str, conflicts_detected: bool = false, resolution_notes: str = None)`
**Purpose**: Log merge operation.

**Returns**: `{"success": true, "merge_id": 1}`

**Use Case**: `git_merge_branch` directive

---

## Batch & Analytics Tools

**Purpose**: Efficient bulk operations and project analytics

### Batch Operations

#### `get_project_summary()`
**Purpose**: Get comprehensive project overview in single call.

**Returns**:
```json
{
  "project": {...},
  "stats": {
    "files": 25,
    "functions": 87,
    "pure_functions": 72,
    "tasks": 15,
    "completed_tasks": 8,
    "themes": 5,
    "flows": 3
  },
  "current_stage": "Development",
  "active_branches": 2,
  "recent_notes": [...]
}
```

**Use Case**: Session initialization, status reporting

**Note**: More comprehensive than existing `get_project_context()`

---

#### `export_project_data()`
**Purpose**: Export complete project data for backup.

**Returns**: JSON with all tables (excluding sensitive data)

**Use Case**: Backup, migration, analysis

---

### Analytics

#### `get_project_metrics()`
**Purpose**: Calculate project health metrics.

**Returns**:
```json
{
  "code_metrics": {
    "total_functions": 87,
    "fp_compliance_rate": 0.83,
    "average_function_dependencies": 2.3
  },
  "task_metrics": {
    "completion_rate": 0.53,
    "average_task_duration_days": 3.2,
    "blocked_tasks_count": 2
  },
  "velocity": {
    "tasks_per_week": 4.2,
    "functions_per_week": 12.5
  }
}
```

**Use Case**: `project_metrics` directive, progress reporting

---

#### `get_bottlenecks()`
**Purpose**: Identify project bottlenecks.

**Returns**:
```json
{
  "blocked_tasks": [...],
  "high_dependency_functions": [...],
  "stale_branches": [...],
  "incomplete_stages": [...]
}
```

**Use Case**: Project health checks, optimization

---

## Implementation Notes

### Module Organization

**Directory Structure**:
```
src/aifp/helpers/project/
├── tools/                          # is_tool=true (MCP-exposed)
│   ├── project_meta_tools.py       # ~8 functions
│   ├── file_tools.py               # ~6 functions
│   ├── function_tools.py           # ~5 functions
│   ├── theme_flow_tools.py         # ~9 functions
│   ├── task_tools.py               # ~14 functions
│   ├── completion_tools.py         # ~7 functions
│   ├── note_tools.py               # ~5 functions
│   ├── git_tools.py                # ~7 functions
│   └── analytics_tools.py          # ~5 functions
└── internal/                       # is_tool=false (used by directives)
    ├── initialization.py           # Project init helpers
    ├── blueprint.py                # Blueprint management
    ├── validation.py               # Data validation
    └── (other internal helpers)
```

**Current Project Helpers**: 18 functions (4 tools, 14 internal)
**Proposed Project Tools**: ~66 functions (from this document)
**Total Project Tools After Additions**: ~70 tools

**Breakdown**:
- Project Metadata: 8 functions (4 getters + 4 setters)
- Code Structure: 16 functions (11 getters + 5 setters)
- Organization: 11 functions (7 getters + 4 setters)
- Task Management: 14 functions (10 getters + 4 setters)
- Completion Tracking: 7 functions (5 getters + 2 setters)
- Notes & Context: 5 functions (2 getters + 3 setters)
- Git Integration: 7 functions (4 getters + 3 setters)
- Batch & Analytics: 3 functions (batch/analytics)

### Naming Conventions

- **Single entity**: `get_task_by_id()`, `get_file_by_path()`
- **Multiple entities**: `get_all_tasks()`, `get_tasks_by_status()`
- **Creation**: `create_task()`, `add_file()`, `register_function()`
- **Updates**: `update_task_status()`, `update_file_checksum()`
- **Completion**: `complete_task()`, `complete_milestone()`
- **Deletion**: `delete_file()`, `remove_task()`
- **Analytics**: `get_project_metrics()`, `get_bottlenecks()`

### Return Types

All functions return:
- **Single entity**: Object dict or `{"found": false}`
- **Multiple entities**: List of dicts (empty list if none)
- **Setters**: `{"success": true/false, ...details}`
- **Analytics**: Dict with metrics and insights

### Error Handling

- Never raise exceptions
- Return empty structures or `{"found": false}`
- Log warnings for invalid parameters
- Validate foreign keys (task_id, file_id, etc.)

---

## Priority Implementation Order

### Phase 1: Critical (Core Workflow Support)
**Essential for Directive Execution**
1. `get_project_metadata()` - Session context
2. `get_task_by_id()` - Task operations
3. `get_tasks_by_status()` - Task filtering
4. `update_task_status()` - Task updates
5. `create_task()` - Task creation
6. `get_file_by_path()` - File operations
7. `add_file()` - File registration
8. `create_note()` - Context logging

### Phase 2: Important (Organization & Tracking)
**Task Hierarchy & Organization**
9. `get_subtasks()` - Task decomposition
10. `get_task_hierarchy()` - Complete view
11. `create_subtask()` - Subtask creation
12. `get_all_themes()` - Organization
13. `get_all_flows()` - Flow management
14. `get_completion_path()` - Roadmap tracking
15. `get_project_summary()` - Batch efficiency

### Phase 3: Advanced (Analytics & Optimization)
**Metrics & Git Integration**
16. `get_project_metrics()` - Health metrics
17. `get_bottlenecks()` - Optimization
18. `get_active_branches()` - Git coordination
19. `get_merge_history()` - Git tracking
20. All remaining helpers

---

## Existing Helpers (Already in helpers_parsed.json)

**Current Project Helpers** (18 functions):

**MCP Tools** (4 functions - already is_tool=true):
1. ✅ `get_project_status()` - Check if initialized
2. ✅ `get_project_context()` - Structured overview
3. ✅ `get_status_tree()` - Hierarchical status
4. ✅ `query_project_db()` - Advanced SQL queries

**Internal Helpers** (14 functions - is_tool=false):
5. `create_project_directory()`
6. `initialize_project_db()`
7. `initialize_user_preferences_db()`
8. `validate_initialization()`
9. `init_project_db()`
10. `get_project_files()`
11. `get_project_functions()`
12. `get_project_tasks()`
13. `create_project_blueprint()`
14. `read_project_blueprint()`
15. `update_project_blueprint_section()`
16. `scan_existing_files()`
17. `infer_architecture()`
18. `detect_and_init_project()`

**Note**: Internal helpers should remain internal (used by directives, not called directly by AI)

---

## Integration with Other Databases

### With aifp_core.db (MCP Helpers)
- Directives query project.db for context
- Helper execution details reference project tasks

### With user_preferences.db (Preferences Helpers)
- Preferences loaded before directive execution
- User customizations applied to project operations

### With user_directives.db (User Directive Helpers)
- User directives may query project state
- Project status includes user_directives_status field

---

## Discussion Questions

1. **Batch vs Single**: Should `get_project_summary()` be Phase 1 for efficiency?
2. **Caching**: Should AI cache project metadata at session start?
3. **Soft deletes**: Should deletions be soft (archived) or hard (permanent)?
4. **Validation**: Should setters validate foreign keys automatically?
5. **Transactions**: Should batch operations support transactions?
6. **Checksums**: Should file updates automatically recalculate checksums?

---

**Next Steps**:
1. Create `additional-helpers-user-directives.md`
2. Review all four helper documents
3. Update project database with preparation notes
4. Add approved helpers to `helpers_parsed.json` with new folder structure
5. Re-run `sync-directives.py`

---

**Status**: 🔵 Proposed - Awaiting Review
**Created**: 2025-11-02
**Author**: AIFP Development Team
