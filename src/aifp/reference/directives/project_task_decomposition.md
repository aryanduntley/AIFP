# Directive: project_task_decomposition

**Type**: Project
**Level**: 2 (High-Level Coordination)
**Parent Directive**: aifp_run
**Priority**: HIGH - Central decomposition for all user requests

---

## Purpose

The `project_task_decomposition` directive decomposes high-level user requests into structured, AIFP-aligned work items: `completion_path`, `milestones`, `tasks`, `subtasks`, and `items`. This directive serves as the **central intelligence** for translating user intent into actionable roadmap structures.

Key responsibilities:
- **Apply user preferences** for task granularity, naming conventions, and decomposition style
- **Understand context** by calling `aifp_status` before decomposition
- **Distinguish work item types**:
  - **Tasks** - Independent units aligned with milestones
  - **Subtasks** - High-priority, pause parent task, support open task
  - **Sidequests** - Low-priority, exploratory, optional
- **Handle interruptions** - Manage active subtasks, prompt for completion/discard/resume
- **Parallel execution** - Coordinate code generation and DB updates simultaneously
- **Maintain roadmap alignment** - Link to `completion_path` and milestones

This is the **central decomposition directive** - all user goals flow through here to create structured work.

---

## When to Apply

This directive applies when:
- **User provides new goals** - Breaking down high-level requests
- **Project needs tasks** - Converting milestones into actionable items
- **Exploring new ideas** - Creating sidequests for experimentation
- **Refining existing work** - Creating subtasks for current tasks
- **Called by other directives**:
  - `aifp_run` - Routes decomposition requests here
  - `project_evolution` - Updates tasks when goals change
  - `user_directive_validate` - Creates tasks for directive implementation

**User Preferences Integration**:
- Before decomposing, loads preferences like `naming_convention`, `auto_create_items`, `default_priority`
- Respects user's preferred task naming convention and default priority level

---

## Workflow

### Trunk: check_user_preferences

Loads user-defined preferences for task decomposition.

**Steps**:
1. **Query directive_preferences** - Load settings for `project_task_decomposition`
2. **Apply preferences** - Configure decomposition engine
3. **Call aifp_status** - Understand current project context

### Branches

**Branch 1: If directive_preferences_exist**
- **Then**: `load_task_preferences`
- **Details**: Query and apply user preferences
  - `naming_convention` - "descriptive", "short", "numbered" (default: descriptive)
  - `auto_create_items` - true/false (default: true)
  - `default_priority` - "low", "medium", "high", "critical" (default: medium)
- **Query**: `SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='project_task_decomposition' AND active=1`
- **Result**: Preferences loaded and ready to apply

**Branch 2: If preferences_loaded**
- **Then**: `decompose_with_preferences`
- **Details**: Apply user customization to decomposition
  - Use specified granularity level
  - Follow naming convention
  - Auto-create items if enabled
- **Result**: Decomposition respects user preferences

**Branch 3: If task_decomposition_requested**
- **Then**: `call_aifp_status`
- **Details**: Get current project context before creating tasks
  - Brief status: Current focus, open items, completion path
  - Purpose: Understand where new tasks fit
- **Result**: Context-aware decomposition

**Branch 4: If status_obtained**
- **Then**: `review_open_tasks`
- **Details**: Check for related existing work
  - Query open sidequests (priority: highest)
  - Query open subtasks (priority: high)
  - Query open tasks (priority: normal)
  - Determine if request aligns with existing work
- **Result**: Understanding of current work landscape

**Branch 5: If related_to_open_task**
- **Then**: `update_if_needed`
- **Details**: Request aligns with existing task
  - Option 1: Add items to existing task
  - Option 2: Create subtask under existing task
  - Check alignment and suggest appropriate action
- **Result**: Existing task enhanced or subtask created

**Branch 6: If new_task_needed**
- **Then**: `create_new_task`
- **Details**: Request is independent or pivots from current work
  - Link to appropriate milestone in `completion_path`
  - Increment `project.version`
  - Create task with description, acceptance criteria
  - Set priority based on milestone
- **SQL**:
  ```sql
  INSERT INTO tasks (milestone_id, name, description, priority, status, created_at)
  VALUES (?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP);

  UPDATE project SET version = version + 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?;
  ```
- **Result**: New independent task created and tracked

**Branch 7: If subtask_needed**
- **Then**: `create_subtask`
- **Details**: Request supports open task at low level
  - Create in `subtasks` table
  - Set `priority = 'high'`
  - Link to `parent_task_id`
  - Pause parent task (`status = 'paused'`)
  - Subtasks must complete before parent resumes
- **SQL**:
  ```sql
  INSERT INTO subtasks (task_id, name, description, priority, status, created_at)
  VALUES (?, ?, ?, 'high', 'in_progress', CURRENT_TIMESTAMP);

  UPDATE tasks SET status = 'paused' WHERE id = ?;
  ```
- **Result**: Subtask created, parent task paused

**Branch 8: If sidequest_needed**
- **Then**: `create_sidequest`
- **Details**: Request is exploratory or optional
  - Create in `sidequests` table
  - Set `priority = 'low'`
  - Link to `project_id` (not task-specific)
  - Does not block other work
- **SQL**:
  ```sql
  INSERT INTO sidequests (project_id, name, description, priority, status, created_at)
  VALUES (?, ?, ?, 'low', 'pending', CURRENT_TIMESTAMP);
  ```
- **Result**: Sidequest created for exploration

**Branch 9: If interruption_detected**
- **Then**: `handle_subtask_priority`
- **Details**: Active subtask exists, new request comes in
  - Notify user: "Subtask [name] in progress—complete, discard, or resume?"
  - Options:
    - **Complete** - Finish subtask, then handle new request
    - **Discard** - Mark subtask as cancelled, resume parent task
    - **Resume** - Keep subtask active, queue new request
  - Update `subtasks.status` based on choice
- **Result**: User chooses how to handle interruption

**Branch 10: If confidence < 0.5 (low_confidence)**
- **Then**: `prompt_user`
- **Details**: Uncertain about decomposition
  - Present analysis: "Is this a new task, subtask, or sidequest?"
  - Ask for clarification
  - Log to `notes` table for future learning
- **Result**: User clarifies work item type

**Branch 11: If code_and_db_needed**
- **Then**: `parallel_execution`
- **Details**: Execute code generation and DB update simultaneously
  - Parallel 1: Call `project_file_write` for code generation
  - Parallel 2: Call `project_update_db` for metadata sync
  - Wait for both to complete
- **Result**: Efficient parallel execution

**Fallback**: `prompt_user`
- Present issue and ask for clarification
- Log to `notes` for future reference

### Error Handling

**on_failure**: `prompt_user`
**retry**: max 2 attempts
- If decomposition fails, prompt user for clarification
- Common issues: Ambiguous request, no matching milestone, missing context

---

## Examples

### Example 1: New Task with User Preferences

**User Preference**:
```sql
INSERT INTO directive_preferences (directive_name, preference_key, preference_value)
VALUES ('project_task_decomposition', 'default_priority', 'high');
VALUES ('project_task_decomposition', 'auto_create_items', 'true');
```

**User Request**: "Implement matrix multiplication"

**AI Execution**:
1. Loads preferences: `default_priority = high`, `auto_create_items = true`
2. Calls `aifp_status`: Current milestone = "Core Operations"
3. Reviews open tasks: None related to matrix multiplication
4. Creates new task with high priority:
   - Task: "Implement matrix multiplication"
   - Priority: "high" (from preference)
   - Auto-creates items:
     - Item 1: "Write multiply_matrices function"
     - Item 2: "Write validate_dimensions helper"
     - Item 3: "Add error handling for dimension mismatch"
     - Item 4: "Write unit tests"
5. Links to milestone: "Core Operations"
6. Updates `project.version`

### Example 2: Subtask for Refinement

**Context**: Task "Implement authentication" is open, status = 'in_progress'

**User Request**: "Add email verification to auth"

**AI Execution**:
1. Calls `aifp_status`: Open task found - "Implement authentication"
2. Request aligns with open task → Create subtask
3. Creates subtask:
   - Name: "Add email verification"
   - Parent task: "Implement authentication"
   - Priority: high
4. Pauses parent task: `tasks.status = 'paused'`
5. Sets subtask: `subtasks.status = 'in_progress'`
6. Notifies user: "Created subtask under 'Implement authentication'. Parent task paused."

### Example 3: Sidequest for Exploration

**User Request**: "Research alternative hashing algorithms"

**AI Execution**:
1. Calls `aifp_status`: Current milestone = "Authentication", no open tasks
2. Evaluates: Exploratory, not critical, optional
3. Creates sidequest:
   - Name: "Research alternative hashing algorithms"
   - Description: "Explore bcrypt, argon2, scrypt alternatives to SHA-256"
   - Priority: low
   - Status: pending
4. Links to project (not task-specific)
5. Notifies user: "Created sidequest for exploration. Doesn't block main roadmap."

### Example 4: Interruption Handling

**Context**: Subtask "Add email verification" is active (status = 'in_progress')

**User Request**: "Implement password reset"

**AI Execution**:
1. Detects active subtask: "Add email verification"
2. Prompts user: "Subtask 'Add email verification' in progress. Complete, discard, or resume?"
3. User chooses: "Complete"
4. AI completes email verification subtask
5. Resumes parent task: "Implement authentication"
6. Creates new subtask: "Implement password reset"

### Example 5: Low Confidence

**User Request**: "Do the thing with the database"

**AI Execution**:
1. Analyzes request: Ambiguous, unclear intent
2. Confidence < 0.5 → Prompt user
3. AI asks: "Could you clarify? Is this:
   - A new task (independent database operation)?
   - A subtask (supporting current work)?
   - A sidequest (exploring database alternatives)?"
4. User clarifies: "Create backup functionality"
5. AI creates new task: "Implement database backup"

---

## Integration with Other Directives

### Called By:
- `aifp_run` - Routes decomposition requests
- `project_evolution` - Updates tasks when goals change
- `user_directive_validate` - Creates implementation tasks

### Calls:
- `aifp_status` - Gets current project context
- `user_preferences_sync` - Loads user customizations
- `project_file_write` - Generates code for tasks (parallel)
- `project_update_db` - Updates metadata (parallel)
- `project_add_path` - Creates new milestones/paths if needed

---

## Database Updates

### Tables Modified:

**project.db**:
```sql
-- Create new task
INSERT INTO tasks (milestone_id, name, description, priority, status, created_at)
VALUES (1, 'Implement matrix multiplication', 'Core matrix operation', 3, 'pending', CURRENT_TIMESTAMP);

-- Create subtask
INSERT INTO subtasks (task_id, name, description, priority, status, created_at)
VALUES (1, 'Add email verification', 'Verification flow for auth', 'high', 'in_progress', CURRENT_TIMESTAMP);

-- Pause parent task
UPDATE tasks SET status = 'paused', updated_at = CURRENT_TIMESTAMP WHERE id = 1;

-- Create sidequest
INSERT INTO sidequests (project_id, name, description, priority, status, created_at)
VALUES (1, 'Research hashing algorithms', 'Explore alternatives', 'low', 'pending', CURRENT_TIMESTAMP);

-- Increment project version
UPDATE project SET version = version + 1, updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

---

## Roadblocks and Resolutions

### Roadblock 1: task vs subtask vs sidequest ambiguity
**Issue**: Unclear which type of work item to create
**Resolution**: Prompt user for clarification, log in notes for future learning

### Roadblock 2: no matching open task
**Issue**: Request doesn't align with any open tasks
**Resolution**: Create new task or sidequest, align to completion_path

### Roadblock 3: status_unavailable
**Issue**: Cannot call `aifp_status` (project not initialized)
**Resolution**: Continue with decomposition but warn user about potential context issues

### Roadblock 4: interruption_conflict
**Issue**: Active subtask blocks new request
**Resolution**: Prompt user to choose: complete, discard, or queue new request

---

## Intent Keywords

- "decompose task"
- "break down"
- "plan steps"
- "create task"
- "explore"
- "implement"
- "add feature"

**Confidence Threshold**: 0.5 (low threshold to catch broad requests)

---

## Related Directives

- `aifp_status` - Provides project context
- `project_add_path` - Creates milestones and paths
- `project_reserve_finalize` - Reserve names before generating code for tasks
- `project_file_write` - Generates code for tasks with embedded IDs
- `project_update_db` - Syncs task metadata
- `project_task_update` - Updates task status
- `user_preferences_sync` - Loads user customizations
- `project_evolution` - Handles goal changes

---

## Decision Tree: Task vs Subtask vs Sidequest

```
User Request
    │
    ├─ Aligns with open task?
    │   ├─ Yes → Is it low-level, single function?
    │   │   ├─ Yes → Create SUBTASK (high priority, pause parent)
    │   │   └─ No → Add items to existing task
    │   └─ No → Continue
    │
    ├─ Independent or pivots goals?
    │   └─ Yes → Create NEW TASK (link to milestone)
    │
    ├─ Exploratory or optional?
    │   └─ Yes → Create SIDEQUEST (low priority)
    │
    └─ Uncertain?
        └─ Prompt user: "New task, subtask, or sidequest?"
```

---

## Notes

- **Always call aifp_status first** to understand context
- **Apply user preferences** for granularity and naming
- **Subtasks pause parent tasks** - must complete before parent resumes
- **Sidequests don't block** - exploratory and optional
- **Parallel execution** when code and DB updates needed
- **Log ambiguities** in `notes` for AI learning
- **Increment project.version** when creating new tasks
