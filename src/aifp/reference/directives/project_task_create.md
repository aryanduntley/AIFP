# Directive: project_task_create

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: project_task_decomposition
**Priority**: HIGH - Atomic task creation

---

## Purpose

The `project_task_create` directive handles atomic creation of new tasks in `project.db`. This directive serves as the **task constructor**, providing a focused, validated interface for inserting new task records.

Key responsibilities:
- **Create task record** - Insert into `tasks` table
- **Link to milestone** - Associate with appropriate milestone in completion_path
- **Set initial status** - Default to 'pending'
- **Assign priority** - Based on milestone or user specification
- **Increment project version** - Mark project evolution
- **Validate inputs** - Ensure required fields present
- **Return task ID** - Enable immediate linking to items and files

This is the **atomic task creator** - called by `project_task_decomposition` when new independent tasks are needed.

---

## When to Apply

This directive applies when:
- **New independent work** - Creating standalone tasks
- **Milestone expansion** - Adding tasks to existing milestones
- **Goal breakdown** - Decomposing high-level goals into tasks
- **Called by other directives**:
  - `project_task_decomposition` - Primary caller for task creation
  - `project_init` - Creates initial tasks during project setup
  - `project_evolution` - Creates tasks when goals change
  - User directly - Manual task creation

---

## Workflow

### Trunk: validate_inputs

Ensures all required fields are present and valid.

**Steps**:
1. **Validate task name** - Non-empty, descriptive
2. **Validate milestone** - Milestone exists and is pending/in_progress
3. **Validate priority** - Value between 1-5
4. **Check duplicates** - Warn if similar task exists

### Branches

**Branch 1: If inputs_valid**
- **Then**: `check_milestone_exists`
- **Details**: Verify milestone is valid
  - Query `milestones` table for milestone_id
  - Check milestone status (must be pending or in_progress)
  - If milestone completed or doesn't exist: Prompt user
- **Query**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Milestone validated

**Branch 2: If milestone_valid**
- **Then**: `check_duplicate_tasks`
- **Details**: Warn if similar task exists
  - Query `tasks` table for similar names
  - Use fuzzy matching (Levenshtein distance < 3)
  - Prompt: "Similar task '[name]' exists. Create anyway?"
- **Query**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: User confirms or cancels

**Branch 3: If no_duplicates_or_confirmed**
- **Then**: `create_task_record`
- **Details**: Insert new task into database
  - Generate task record with all fields
  - Default status: 'pending'
  - Set created_at, updated_at timestamps
  - Return generated task ID
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Task created, ID returned

**Branch 4: If task_created**
- **Then**: `increment_project_version`
- **Details**: Mark project evolution
  - Update `project.version`
  - Indicates project scope changed
- **SQL**:
  **Use helper functions** for database operations. Query available helpers for the appropriate database.
- **Result**: Project version incremented

**Branch 5: If version_incremented**
- **Then**: `log_task_creation`
- **Details**: Record task creation in notes
  - Log task name, milestone, priority
  - Source: directive
  - Include task_id for reference
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Creation logged

**Branch 6: If priority_not_specified**
- **Then**: `infer_priority_from_milestone`
- **Details**: Auto-assign priority based on milestone
  - Early milestones: Higher priority (1-2)
  - Middle milestones: Medium priority (3)
  - Later milestones: Lower priority (4-5)
- **Result**: Priority auto-assigned

**Branch 7: If description_missing**
- **Then**: `prompt_for_description`
- **Details**: Ask user for task description
  - Description helps with clarity
  - Not required but recommended
  - Can be added later via `project_task_update`
- **Result**: Description provided or left empty

**Branch 8: If acceptance_criteria_provided**
- **Then**: `store_acceptance_criteria`
- **Details**: Save acceptance criteria for task completion
  - Store in task description or separate field
  - Used by `project_completion_check` to validate done-ness
- **Result**: Criteria stored

**Fallback**: `prompt_user`
- Present issue and ask for clarification
- Common issues: Missing name, invalid milestone, invalid priority

### Error Handling

**on_failure**: `rollback_and_prompt`
- If task creation fails: Rollback database transaction
- Prompt user with specific error
- Common issues: Database lock, constraint violation

---

## Examples

### Example 1: Create Task with All Fields

**Parameters**:
- `milestone_id`: 3
- `name`: "Implement matrix multiplication"
- `description`: "Create pure functional matrix multiplication with validation"
- `priority`: 2
- `acceptance_criteria`: "Handles all matrix dimensions, validates inputs, pure function"

**AI Execution**:
1. Validates inputs: ✓ All valid
2. Checks milestone: ID=3, name="Core Operations", status="in_progress" ✓
3. Checks duplicates: No similar tasks found
4. Creates task:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Increments project version:
   **Use helper functions** for database operations. Query available helpers for the appropriate database.
6. Logs creation:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
7. Returns:
   ```json
   {
     "task_id": 42,
     "name": "Implement matrix multiplication",
     "milestone": "Core Operations",
     "priority": 2,
     "status": "pending"
   }
   ```

### Example 2: Create Task with Auto-Priority

**Parameters**:
- `milestone_id`: 5
- `name`: "Add performance benchmarks"
- `description`: ""
- `priority`: null (not specified)

**AI Execution**:
1. Validates inputs: Name ✓, Milestone ✓, Priority missing
2. Checks milestone: ID=5, name="Optimization", order_index=4 (later milestone)
3. Infers priority: Later milestone → priority=4 (lower priority)
4. Prompts: "No description provided. Add description? (optional)"
5. User: "Skip"
6. Creates task with priority=4
7. Increments project version
8. Logs creation
9. Returns task_id: 43

### Example 3: Duplicate Task Warning

**Parameters**:
- `milestone_id`: 3
- `name`: "Implement matrix multiplycation" (typo)

**AI Execution**:
1. Validates inputs: ✓ Valid
2. Checks milestone: ✓ Valid
3. Checks duplicates:
   - Found: "Implement matrix multiplication" (Levenshtein distance = 2)
   - Status: pending
4. Prompts:
   ```
   ⚠️  Similar task already exists:
   - "Implement matrix multiplication" (status: pending)

   Your task: "Implement matrix multiplycation"

   This appears to be a typo or duplicate.
   Options:
   1. Cancel (fix typo and retry)
   2. Create anyway
   ```
5. User chooses: "1" (Cancel)
6. Aborts creation
7. Returns: "Task creation cancelled. Please fix typo and retry."

### Example 4: Invalid Milestone

**Parameters**:
- `milestone_id`: 99
- `name`: "Add feature X"

**AI Execution**:
1. Validates inputs: Name ✓, Milestone ?
2. Checks milestone: ✗ ID=99 not found
3. Prompts:
   ```
   ❌ Milestone ID 99 not found

   Available milestones:
   1. Project Setup (completed)
   2. Core Development (in_progress)
   3. Core Operations (in_progress)
   4. Testing (pending)
   5. Optimization (pending)

   Choose milestone for task "Add feature X":
   ```
4. User selects: "3"
5. Creates task with milestone_id=3
6. Returns task_id

### Example 5: Completed Milestone Error

**Parameters**:
- `milestone_id`: 1
- `name`: "Update setup docs"

**AI Execution**:
1. Validates inputs: ✓ Valid
2. Checks milestone: ID=1, name="Project Setup", status="completed" ✗
3. Prompts:
   ```
   ❌ Cannot add task to completed milestone

   Milestone: "Project Setup" (completed)
   Task: "Update setup docs"

   Options:
   1. Choose different milestone
   2. Reopen milestone (requires confirmation)
   3. Cancel
   ```
4. User chooses: "1"
5. Lists available pending/in_progress milestones
6. User selects milestone
7. Creates task
8. Returns task_id

---

## Integration with Other Directives

### Called By:
- `project_task_decomposition` - Primary caller
- `project_init` - Creates initial tasks
- `project_evolution` - Creates tasks when goals change
- User directly - Manual task creation

### Calls:
- `project_update_db` - Syncs metadata (implicitly)
- `project_task_decomposition` - May call back for subtasks

---

## Database Updates

### Tables Modified:

**project.db**:
**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Roadblocks and Resolutions

### Roadblock 1: milestone_not_found
**Issue**: Specified milestone doesn't exist
**Resolution**: List available milestones, prompt user to select

### Roadblock 2: milestone_completed
**Issue**: Cannot add task to completed milestone
**Resolution**: Offer to choose different milestone or reopen milestone

### Roadblock 3: duplicate_task
**Issue**: Similar task already exists (typo or actual duplicate)
**Resolution**: Warn user, show similar task, confirm intent

### Roadblock 4: invalid_priority
**Issue**: Priority not in range 1-5
**Resolution**: Default to 3 (medium) or infer from milestone

### Roadblock 5: database_constraint_violation
**Issue**: Task creation violates database constraints
**Resolution**: Rollback, report specific constraint, prompt user

---

## Input Parameters

**Required**:
- `milestone_id` (int) - Which milestone this task belongs to
- `name` (str) - Task name (non-empty, descriptive)

**Optional**:
- `description` (str, default: "") - Detailed task description
- `priority` (int, 1-5, default: infer from milestone) - Task priority
- `acceptance_criteria` (str, default: "") - How to know when task is done

**Returns**:
```json
{
  "task_id": 42,
  "name": "Task name",
  "milestone": "Milestone name",
  "priority": 2,
  "status": "pending",
  "created_at": "2025-10-27T14:30:00Z"
}
```

---

## Intent Keywords

- "create task"
- "add task"
- "new task"
- "make task"
- "insert task"

**Confidence Threshold**: 0.7

---

## Related Directives

- `project_task_decomposition` - Decomposes user requests into tasks
- `project_task_update` - Updates task status/priority
- `project_subtask_create` - Creates subtasks under tasks
- `project_item_create` - Creates items within tasks
- `project_init` - Uses task creation during setup

---

## Priority Levels

| Priority | Description | Use Case |
|----------|-------------|----------|
| 1 | Critical | Blocking issues, core functionality |
| 2 | High | Important features, key milestones |
| 3 | Medium | Standard tasks, regular features |
| 4 | Low | Nice-to-have, optimizations |
| 5 | Lowest | Future enhancements, stretch goals |

---

## Validation Rules

**Task Name**:
- Non-empty
- Max 200 characters
- Descriptive (not "Fix bug" or "TODO")
- Action-oriented (starts with verb)

**Milestone**:
- Must exist in database
- Must be pending or in_progress
- Cannot be completed

**Priority**:
- Must be 1-5
- If not specified: Inferred from milestone order

**Description**:
- Optional but recommended
- Max 2000 characters
- Should explain "why" not just "what"

---

## Notes

- **Always validate milestone** - Cannot add to completed milestones
- **Check for duplicates** - Prevent typos and accidental duplication
- **Increment project version** - Task creation is project evolution
- **Return task ID immediately** - Enable linking to items and files
- **Log all creations** - Audit trail in `notes` table
- **Auto-infer priority** - Use milestone order if not specified
- **Atomic operation** - Single transaction, rollback on failure
