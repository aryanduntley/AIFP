# aifp_status - Project Status Reporting Directive

**Type**: Project Management
**Level**: 1
**Parent**: `aifp_run`
**Category**: Status & Context

---

## Purpose

`aifp_status` provides comprehensive project context for continuation and status checking. It reads ProjectBlueprint.md, queries project.db, and returns a structured status report with historical context, open items, and recommended actions.

**Use this directive when**:
- User requests continuation ("continue", "resume", "what's next")
- User asks for status ("status", "where are we", "show progress")
- Starting task decomposition (context-aware planning)
- AI needs project context after context loss

---

## When to Use

### Automatic Triggers

Keywords that trigger `aifp_status`:
- "continue", "resume", "keep going"
- "status", "progress", "where are we"
- "what's next", "what should I do"
- "show me", "summarize", "update"

### Proactive Calls

Called by other directives:
- `project_task_decomposition` → Calls `aifp_status` first for context
- `aifp_run` → Routes continuation requests to `aifp_status`
- `project_evolution` → Checks status before architectural changes

---

## Workflow

### Trunk: `generate_status_report`

**Step 1: Read ProjectBlueprint.md**

```python
# Load blueprint for high-level context
blueprint_path = f"{project_root}/.aifp-project/ProjectBlueprint.md"
blueprint_content = read_file(blueprint_path)

# Parse sections
project_overview = parse_section(blueprint_content, "1. Project Overview")
technical_blueprint = parse_section(blueprint_content, "2. Technical Blueprint")
themes_flows = parse_section(blueprint_content, "3. Project Themes & Flows")
completion_path = parse_section(blueprint_content, "4. Completion Path")
```

**Step 2: Query project.db for Current State**

```sql
-- Get project metadata
SELECT name, purpose, status, version, goals_json
FROM project
WHERE id = 1;

-- Get completion path with progress
SELECT cp.name, cp.status, cp.description,
       COUNT(m.id) as total_milestones,
       SUM(CASE WHEN m.status = 'completed' THEN 1 ELSE 0 END) as completed_milestones
FROM completion_path cp
LEFT JOIN milestones m ON m.completion_path_id = cp.id
GROUP BY cp.id
ORDER BY cp.order_index;

-- Get active milestones
SELECT m.name, m.status, m.description,
       COUNT(t.id) as total_tasks,
       SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
FROM milestones m
LEFT JOIN tasks t ON t.milestone_id = m.id
WHERE m.status IN ('in_progress', 'pending')
GROUP BY m.id;

-- Get open tasks (pending or in_progress)
SELECT t.id, t.name, t.status, t.priority, t.description,
       m.name as milestone_name
FROM tasks t
JOIN milestones m ON t.milestone_id = m.id
WHERE t.status IN ('pending', 'in_progress')
ORDER BY t.priority DESC, t.created_at ASC;

-- Get active sidequests
SELECT name, reason, status, priority
FROM sidequests
WHERE status IN ('pending', 'in_progress')
ORDER BY priority DESC;

-- Get recent notes (last 10)
SELECT content, note_type, source, created_at
FROM notes
ORDER BY created_at DESC
LIMIT 10;
```

**Step 3: Build Status Tree**

```python
status_report = {
    "project": {
        "name": project_name,
        "purpose": project_purpose,
        "version": project_version,
        "status": project_status
    },
    "completion_path": [
        {
            "stage": stage_name,
            "status": stage_status,
            "progress": f"{completed_milestones}/{total_milestones} milestones"
        }
    ],
    "current_focus": {
        "milestone": active_milestone_name,
        "progress": f"{completed_tasks}/{total_tasks} tasks",
        "open_tasks": [
            {"id": 1, "name": "Implement multiply", "priority": 1}
        ]
    },
    "sidequests": [
        {"name": "Fix type hint", "reason": "Test failure", "priority": 1}
    ],
    "recent_activity": [
        {"note": "Added matrix operations", "source": "ai", "when": "2 hours ago"}
    ],
    "recommendations": [
        "Continue with task #5: Implement multiply_matrices",
        "Address sidequest: Fix type hint in add_matrices"
    ]
}
```

**Step 4: Return Status Report**

Returns structured JSON with full context.

---

## Interactions with Other Directives

### Called By

- **`aifp_run`** - Routes continuation/status requests
- **`project_task_decomposition`** - Gets context before creating tasks
- **`project_evolution`** - Checks state before architectural changes

### Calls

- **`get_project_context()`** - Helper function for structured data
- **`get_status_tree()`** - Helper function for hierarchical status
- **`parse_blueprint_section()`** - Parses ProjectBlueprint.md

### Data Flow

```
User: "Continue"
  ↓
aifp_run → aifp_status
  ├─ Reads .aifp-project/ProjectBlueprint.md
  ├─ Queries project.db (completion_path, milestones, tasks, notes)
  ├─ Builds structured status report
  └─ Returns to AI with recommendations
  ↓
AI uses context to continue work
```

---

## Examples

### Example 1: Basic Status Check

**User**: "Show me the status"

**AI calls**: `aifp_status()`

**Returns**:
```json
{
  "success": true,
  "project": {
    "name": "Matrix Calculator",
    "purpose": "Pure FP matrix operations library",
    "version": 1,
    "status": "active"
  },
  "completion_path": [
    {
      "stage": "Foundation",
      "status": "completed",
      "progress": "5/5 milestones"
    },
    {
      "stage": "Core Development",
      "status": "in_progress",
      "progress": "2/4 milestones"
    }
  ],
  "current_focus": {
    "milestone": "Matrix Operations",
    "progress": "3/6 tasks",
    "open_tasks": [
      {"id": 5, "name": "Implement multiply_matrices", "priority": 1},
      {"id": 6, "name": "Add validation for dimensions", "priority": 2}
    ]
  },
  "recommendations": [
    "Continue with task #5: Implement multiply_matrices function",
    "Review completed tasks for patterns before starting task #6"
  ]
}
```

**AI presents**:
```
📊 Matrix Calculator Status

Current Stage: Core Development (2/4 milestones)
Current Milestone: Matrix Operations (3/6 tasks)

Open Tasks:
  1. [Priority 1] Implement multiply_matrices
  2. [Priority 2] Add validation for dimensions

Recommendations:
  • Continue with multiply_matrices function
  • Review completed patterns before validation
```

---

### Example 2: Continuation After Break

**User**: "Where were we?"

**AI calls**: `aifp_status()`

**Returns**:
```json
{
  "success": true,
  "current_focus": {
    "milestone": "Testing Infrastructure",
    "progress": "1/3 tasks",
    "last_completed": {
      "task": "Set up pytest configuration",
      "when": "3 hours ago"
    },
    "in_progress": {
      "task": "Write property-based tests for add_matrices",
      "status": "in_progress"
    }
  },
  "recent_activity": [
    {"note": "Added hypothesis for property-based testing", "when": "3 hours ago"},
    {"note": "Created test_matrix.py with basic structure", "when": "3 hours ago"}
  ],
  "recommendations": [
    "Resume property-based tests for add_matrices",
    "Use hypothesis strategies for matrix generation"
  ]
}
```

**AI presents**:
```
Last work: Set up pytest configuration (3 hours ago)
In progress: Write property-based tests for add_matrices

Recent activity:
  • Added hypothesis library
  • Created test_matrix.py structure

Let's continue with the property-based tests using hypothesis strategies.
```

---

### Example 3: Status with Sidequests

**User**: "What's the current status?"

**Returns**:
```json
{
  "success": true,
  "current_focus": {
    "milestone": "Matrix Operations",
    "progress": "4/6 tasks"
  },
  "sidequests": [
    {
      "name": "Fix type hint in add_matrices",
      "reason": "mypy reported error",
      "priority": 2,
      "status": "pending"
    }
  ],
  "recommendations": [
    "Address sidequest: Fix type hint before continuing",
    "Type error blocks next task implementation"
  ]
}
```

**AI presents**:
```
⚠️ Sidequest Detected: Fix type hint in add_matrices
Reason: mypy error blocking progress

Should we fix this first? (Recommended: Yes)
```

---

## Edge Cases

### Case 1: Project Not Initialized

**Trigger**: `.aifp-project/` doesn't exist

**Response**:
```json
{
  "success": false,
  "error": "Project not initialized",
  "recommendation": "Run `aifp init` to initialize project"
}
```

---

### Case 2: No Open Tasks

**Trigger**: All tasks completed for current milestone

**Response**:
```json
{
  "success": true,
  "current_focus": {
    "milestone": "Matrix Operations",
    "progress": "6/6 tasks",
    "status": "All tasks completed!"
  },
  "recommendations": [
    "Mark milestone as completed",
    "Move to next milestone: Vector Operations",
    "Or run project_completion_check to verify stage completion"
  ]
}
```

---

### Case 3: Blueprint Out of Sync

**Trigger**: Blueprint checksum doesn't match database

**Response**:
```json
{
  "success": true,
  "warning": "ProjectBlueprint.md may be out of sync",
  "recommendation": "Run project_blueprint_update to sync",
  "current_focus": { ... }  // Still returns status
}
```

---

## Related Directives

### Primary Relationships

- **`aifp_run`** - Routes to this directive
- **`project_blueprint_read`** - Parses blueprint file
- **`project_task_decomposition`** - Uses status for context
- **`project_completion_check`** - Validates completion progress

### Helper Functions Used

- `get_project_context(type)` - Structured project overview
- `get_status_tree()` - Hierarchical status with history
- `parse_blueprint_section(file, section)` - Parse blueprint sections

---

## Database Operations

**Read Operations**:
- Reads `.aifp-project/ProjectBlueprint.md` (file system)
- Queries `project.db`:
  - `project` table - metadata
  - `completion_path` table - stage progress
  - `milestones` table - milestone status
  - `tasks` table - open tasks
  - `sidequests` table - active sidequests
  - `notes` table - recent activity

**Write Operations**:
- None (read-only directive)

---

## FP Compliance

**Purity**: ✅ Pure function
- No side effects (read-only)
- Deterministic given same database state
- Returns structured data

**Immutability**: ✅ Immutable
- No state mutations
- Database reads only
- Report structure frozen

**Side Effects**: ✅ Isolated
- File reads (effect isolated in helper)
- Database queries (effect isolated in helper)

---

## Error Handling

### File Not Found

**Trigger**: ProjectBlueprint.md missing

**Response**:
```json
{
  "success": true,
  "warning": "ProjectBlueprint.md not found",
  "fallback": "Using database only for status",
  "current_focus": { ... }  // Returns database-only status
}
```

### Database Query Failure

**Trigger**: Corrupt project.db or missing tables

**Response**:
```json
{
  "success": false,
  "error": "Database query failed: table 'tasks' does not exist",
  "recommendation": "Re-initialize project database"
}
```

---

## Best Practices

1. **Call for every continuation** - Provides essential context
2. **Use before task decomposition** - Prevents duplicate tasks
3. **Present recommendations** - AI should follow suggested actions
4. **Show hierarchical progress** - Completion path → Milestones → Tasks
5. **Highlight sidequests** - Address blockers before continuing
6. **Include recent activity** - Helps AI remember context
7. **Be concise to user** - Format status clearly, not verbose

---

## Version History

- **v1.0** (2025-10-23): Initial status directive
- **v1.1** (2025-10-24): Added ProjectBlueprint.md integration
- **v1.2** (2025-10-25): Added sidequest support and recommendations

---

## Notes

- This directive is essential for **stateful continuation**
- Combines file-based (blueprint) and database context
- Enables AI to pick up where it left off
- Reports should be **actionable** with clear next steps
