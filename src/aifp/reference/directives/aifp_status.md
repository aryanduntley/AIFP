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

### Project Not Initialized

If `.aifp-project/` does not exist, `aifp_status` invokes **`detect_and_init_project`** sub-workflow:

**Step 1: Check for `.aifp-project/`**
```bash
if [ ! -d ".aifp-project" ]; then
    # Check for legacy backup in .git/.aifp/
    if [ -d ".git/.aifp" ]; then
        prompt_user: "Found archived project state. Restore or initialize new?"
    else
        prompt_user: "Project not initialized. Initialize now?"
    fi
fi
```

**Step 2: Optional Restore from `.git/.aifp/`**
```bash
if restore_selected:
    cp .git/.aifp/ProjectBlueprint.md .aifp-project/
    cp .git/.aifp/project.db.backup .aifp-project/project.db
    # Verify restoration
    call aifp_status again
```

**Step 3: Route to `project_init`**
```bash
if initialize_new:
    call project_init directive
    # After init completes, call aifp_status again
```

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
-- Get project metadata (including user directive status)
SELECT name, purpose, status, version, goals_json, user_directives_status
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

**Step 3: Check User Directive Status (Use Case 2 Projects)**

```python
# Check if this is a Use Case 2 project (automation-based)
if project.user_directives_status is not None:
    # This is a Use Case 2 project
    # Call user_directive_status for comprehensive directive reporting
    user_directive_report = call_directive("user_directive_status")

    # Determine project phase based on status
    if project.user_directives_status == 'in_progress':
        project_phase = "DEVELOPMENT MODE - Directives being set up"
        focus = "Complete directive setup pipeline (parse → validate → implement → approve → activate)"
    elif project.user_directives_status == 'active':
        project_phase = "RUN MODE - Directives executing"
        focus = "Monitor directive execution, check health, handle errors"
    elif project.user_directives_status == 'disabled':
        project_phase = "PAUSED - Directives deactivated"
        focus = "Resume directives when ready or debug issues"
```

**User Directive Status Values**:
- **NULL** (default): Use Case 1 project (regular software development)
- **'in_progress'**: Use Case 2 project, directives being developed (setup phase)
- **'active'**: Use Case 2 project, directives deployed and running (production phase)
- **'disabled'**: Use Case 2 project, directives temporarily paused

**Step 4: Build Priority-Based Status Tree**

AIFP uses a priority-based system for determining current focus:

**Priority 1: Open Sidequests** (Highest priority)
```sql
-- Find open sidequests
SELECT sq.id, sq.name, sq.status, sq.paused_task_id, sq.paused_subtask_id
FROM sidequests sq
WHERE sq.status IN ('pending', 'in_progress')
ORDER BY sq.created_at ASC;

-- Get parent task context
SELECT t.name, t.status, t.description
FROM tasks t
WHERE t.id = ?;

-- Get all items for parent task
SELECT i.name, i.status, i.description
FROM items i
WHERE i.reference_table = 'tasks' AND i.reference_id = ?;

-- Get all items for sidequest
SELECT i.name, i.status, i.description
FROM items i
WHERE i.reference_table = 'sidequests' AND i.reference_id = ?;

-- If no completed items in task, get historical context
SELECT t.name, t.status, i.name AS item_name, i.status AS item_status
FROM tasks t
LEFT JOIN items i ON i.reference_table = 'tasks' AND i.reference_id = t.id
WHERE t.milestone_id = ? AND t.created_at < ?
ORDER BY t.created_at DESC, i.created_at DESC
LIMIT 10;
```

**Priority 2: Current Subtask** (If no sidequests)
```sql
-- Find open subtask
SELECT st.id, st.name, st.status, st.parent_task_id
FROM subtasks st
WHERE st.status IN ('pending', 'in_progress')
ORDER BY st.priority DESC, st.created_at ASC
LIMIT 1;

-- Get all items for subtask
SELECT i.name, i.status, i.description
FROM items i
WHERE i.reference_table = 'subtasks' AND i.reference_id = ?;

-- If no completed items, get historical context from parent task
```

**Priority 3: Current Task** (If no subtasks)
```sql
-- Find open task
SELECT t.id, t.name, t.status, t.milestone_id
FROM tasks t
WHERE t.status IN ('pending', 'in_progress')
ORDER BY t.priority DESC, t.created_at ASC
LIMIT 1;

-- Get all items for task
SELECT i.name, i.status, i.description
FROM items i
WHERE i.reference_table = 'tasks' AND i.reference_id = ?;

-- Evaluate completed vs incomplete items
```

**Step 4: Check for Ambiguities and Recent Context**

```sql
-- Query notes for recent clarifications or warnings
SELECT content, note_type, directive_name, severity
FROM notes
WHERE source IN ('directive', 'ai')
  AND severity IN ('warning', 'error')
ORDER BY created_at DESC
LIMIT 5;
```

**Step 5: Build Status Report**

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
        "type": "sidequest|subtask|task",  # Priority type
        "item": current_item,
        "parent": parent_context if applicable,
        "progress": f"{completed_items}/{total_items} items"
    },
    "historical_context": [
        {"task": "Previous task", "last_items": [...], "completed": True}
    ],
    "ambiguities": [
        {"note": "Type error in function", "severity": "warning"}
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

**Step 6: Return Status Report**

Returns structured JSON with full context, prioritized focus, and historical awareness.

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

### Example 4: Use Case 2 Status (Automation Project)

**User**: "Show status"

**Project Context**: Home automation project with user directives active

**Returns**:
```json
{
  "success": true,
  "project": {
    "name": "Home Automation",
    "purpose": "Automated home controls via user directives",
    "status": "active",
    "user_directives_status": "active"
  },
  "project_type": "Use Case 2 - Automation Project",
  "project_phase": "RUN MODE - Directives executing",
  "user_directives": {
    "total": 3,
    "active": 3,
    "inactive": 0,
    "directives": [
      {
        "name": "lights_off_5pm",
        "status": "active",
        "executions_today": 1,
        "last_execution": "2025-10-30 17:00:00",
        "success_rate": "100%"
      },
      {
        "name": "stove_alert",
        "status": "active",
        "executions_today": 0,
        "last_check": "2025-10-30 18:45:00",
        "success_rate": "100%"
      },
      {
        "name": "door_lock_check",
        "status": "active",
        "executions_today": 2,
        "last_execution": "2025-10-30 18:30:00",
        "success_rate": "100%"
      }
    ],
    "errors_last_24h": 0
  },
  "focus": "Monitor directive execution, check health, handle errors",
  "recommendations": [
    "All directives running healthy",
    "Check logs if any execution failures occur"
  ]
}
```

**AI presents**:
```
🏠 Home Automation Status
Project Type: Use Case 2 (Automation)
Phase: RUN MODE - Directives Executing

Active Directives: 3/3
  ✓ lights_off_5pm - Executed 1x today (last: 5:00 PM)
  ✓ stove_alert - Monitoring (last check: 6:45 PM)
  ✓ door_lock_check - Executed 2x today (last: 6:30 PM)

Health: All directives running normally
Errors (24h): 0

→ Directives are executing as expected. Use "show directive logs" for details.
```

**Use Case 2 vs Use Case 1**:
- **Use Case 1** (regular dev): Status shows code files, functions, tasks, completion paths
- **Use Case 2** (automation): Status shows directive execution health, runs, errors, monitoring

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

### Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
### Helper Functions Defined by Project Structure

**`get_status_tree(project_id, context_limit=10)`**
- Builds hierarchical status tree with historical context
- Returns priority-based current focus (sidequest → subtask → task)
- Includes parent context and previous task items
- Returns: `{"priority": "type", "current": {...}, "parent": {...}, "historical_context": [...]}`

**`detect_and_init_project()`**
- Checks for `.aifp-project/` existence
- Checks for `.git/.aifp/` backup if not found
- Prompts user for restoration or new initialization
- Routes to `project_init` if needed
- Returns status after initialization

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
