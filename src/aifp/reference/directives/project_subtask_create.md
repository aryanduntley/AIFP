# Directive: project_subtask_create

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: project_task_decomposition
**Priority**: HIGH - Atomic subtask creation with parent task management

---

## Purpose

The `project_subtask_create` directive handles atomic creation of subtasks in `project.db` with automatic parent task management. This directive serves as the **subtask constructor**, providing focused, validated subtask creation that **pauses parent tasks** until completion.

Key responsibilities:
- **Create subtask record** - Insert into `subtasks` table
- **Link to parent task** - Associate with open task
- **Pause parent task** - Set parent status to 'paused'
- **Set high priority** - Subtasks always high priority
- **Initialize status** - Default to 'in_progress' (immediate focus)
- **Validate parent task** - Must be open (not completed/cancelled)
- **Return subtask ID** - Enable immediate tracking

This is the **atomic subtask creator** - called by `project_task_decomposition` when low-level, focused work is needed.

---

## When to Apply

This directive applies when:
- **Refining open task** - Breaking down current work into smaller pieces
- **Low-level work needed** - Single function, single file, specific fix
- **Focused subtask** - Supports parent task, not independent
- **Immediate action** - Work that should be done now before parent continues
- **Called by other directives**:
  - `project_task_decomposition` - Primary caller for subtask creation
  - User directly - Manual subtask creation

**Key Distinction**: Subtasks are NOT independent tasks. They:
- Support a specific open task
- Pause the parent task until complete
- Have high priority (must complete before parent resumes)
- Are low-level (single function, small scope)

---

## Workflow

### Trunk: validate_inputs

Ensures all required fields are present and parent task is valid.

**Steps**:
1. **Validate subtask name** - Non-empty, descriptive
2. **Validate parent task** - Task exists and is open
3. **Check parent status** - Must be 'pending' or 'in_progress'
4. **Verify not duplicate** - Check for similar subtasks

### Branches

**Branch 1: If inputs_valid**
- **Then**: `check_parent_task_exists`
- **Details**: Verify parent task is valid
  - Query `tasks` table for task_id
  - Check task status (must be pending or in_progress)
  - If task completed/cancelled: Cannot create subtask
- **Query**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Parent task validated

**Branch 2: If parent_task_valid**
- **Then**: `check_active_subtasks`
- **Details**: Check if other subtasks already exist
  - Query `subtasks` table for open subtasks
  - Warn if multiple active subtasks (context switching)
  - Prompt: "Another subtask '[name]' is active. Continue?"
- **Query**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: User confirms or handles active subtasks

**Branch 3: If no_blocking_subtasks_or_confirmed**
- **Then**: `create_subtask_record`
- **Details**: Insert new subtask into database
  - Generate subtask record
  - Default status: 'in_progress' (immediate focus)
  - Priority: Always 'high' (subtasks block parent)
  - Set created_at, updated_at timestamps
  - Return generated subtask ID
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Subtask created, ID returned

**Branch 4: If subtask_created**
- **Then**: `pause_parent_task`
- **Details**: Update parent task status
  - Set parent task status to 'paused'
  - Update parent task updated_at timestamp
  - Log pause reason (subtask created)
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Parent task paused

**Branch 5: If parent_paused**
- **Then**: `log_subtask_creation`
- **Details**: Record subtask creation in notes
  - Log subtask name, parent task, reason
  - Source: directive
  - Include both subtask_id and task_id for reference
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Creation logged

**Branch 6: If parent_already_paused**
- **Then**: `add_to_paused_task`
- **Details**: Parent already paused by another subtask
  - Add new subtask to paused task
  - Warn: "Parent task already paused by '[subtask_name]'"
  - New subtask queued or user cancels
- **Result**: Subtask added to already-paused task

**Branch 7: If parent_task_completed**
- **Then**: `reject_creation`
- **Details**: Cannot create subtask for completed task
  - Error: "Parent task '[name]' is completed"
  - Suggestion: "Create new task instead"
  - Abort subtask creation
- **Result**: Creation blocked

**Branch 8: If parent_task_cancelled**
- **Then**: `reject_creation`
- **Details**: Cannot create subtask for cancelled task
  - Error: "Parent task '[name]' is cancelled"
  - Suggestion: "Reopen task or create new task"
  - Abort subtask creation
- **Result**: Creation blocked

**Fallback**: `prompt_user`
- Present issue and ask for clarification
- Common issues: Invalid parent task, missing name

### Error Handling

**on_failure**: `rollback_and_prompt`
- If subtask creation fails: Rollback database transaction
- Parent task status NOT changed
- Prompt user with specific error
- Common issues: Database lock, constraint violation

---

## Examples

### Example 1: Create Subtask for Open Task

**Parameters**:
- `task_id`: 15
- `name`: "Add email verification to auth"
- `description`: "Implement email verification flow with token generation"

**AI Execution**:
1. Validates inputs: ✓ All valid
2. Checks parent task:
   - ID=15, name="Implement authentication", status="in_progress" ✓
3. Checks active subtasks: None found
4. Creates subtask:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Pauses parent task:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
6. Logs creation:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
7. Returns:
   ```json
   {
     "subtask_id": 7,
     "name": "Add email verification to auth",
     "parent_task": "Implement authentication",
     "parent_task_id": 15,
     "parent_status": "paused",
     "priority": "high",
     "status": "in_progress"
   }
   ```

### Example 2: Multiple Active Subtasks Warning

**Parameters**:
- `task_id`: 15
- `name`: "Add password reset"

**Context**: Subtask "Add email verification" already in_progress for this task

**AI Execution**:
1. Validates inputs: ✓ Valid
2. Checks parent task: ✓ Valid (already paused)
3. Checks active subtasks:
   - Found: "Add email verification" (status: in_progress)
4. Prompts:
   ```
   ⚠️  Parent task already has active subtask

   Parent task: Implement authentication (paused)
   Active subtask: Add email verification (in_progress)

   Creating another subtask will:
   - Add to task queue
   - Require completing both before parent resumes
   - May cause context switching

   Options:
   1. Complete current subtask first (recommended)
   2. Create new subtask anyway
   3. Cancel
   ```
5. User chooses: "2" (Create anyway)
6. Creates subtask with status='pending' (not in_progress, since another is active)
7. Logs:
   ```
   Multiple subtasks for task 15: Add email verification (in_progress), Add password reset (pending)
   ```
8. Returns subtask_id

### Example 3: Completed Parent Task Error

**Parameters**:
- `task_id`: 8
- `name`: "Update setup script"

**AI Execution**:
1. Validates inputs: ✓ Valid
2. Checks parent task:
   - ID=8, name="Initial project setup", status="completed" ✗
3. Rejects creation:
   ```
   ❌ Cannot create subtask for completed task

   Parent task: "Initial project setup" (completed)
   Attempted subtask: "Update setup script"

   Completed tasks cannot have new subtasks.

   Suggestion: Create new task instead:
   - Task name: "Update setup script"
   - Milestone: [appropriate milestone]
   ```
4. Prompts: "Create as new task instead?"
5. If yes: Calls `project_task_create`
6. Returns task_id (not subtask_id)

### Example 4: Parent Already Paused

**Parameters**:
- `task_id`: 22
- `name`: "Fix edge case handling"

**Context**: Task 22 already paused by subtask "Refactor validation"

**AI Execution**:
1. Validates inputs: ✓ Valid
2. Checks parent task: ID=22, status="paused" (already paused)
3. Checks active subtasks:
   - Found: "Refactor validation" (status: in_progress)
4. Prompts:
   ```
   ⚠️  Parent task already paused

   Parent task: Process data pipeline (paused)
   Blocking subtask: Refactor validation (in_progress)

   Add new subtask "Fix edge case handling"?
   - Will queue after current subtask
   - Parent remains paused until all subtasks complete
   ```
5. User confirms: "Yes"
6. Creates subtask with status='pending'
7. Parent remains paused
8. Returns subtask_id

### Example 5: Cancelled Parent Task Error

**Parameters**:
- `task_id`: 30
- `name`: "Add feature Y"

**AI Execution**:
1. Validates inputs: ✓ Valid
2. Checks parent task:
   - ID=30, name="Implement feature X", status="cancelled" ✗
3. Rejects creation:
   ```
   ❌ Cannot create subtask for cancelled task

   Parent task: "Implement feature X" (cancelled)
   Attempted subtask: "Add feature Y"

   Cancelled tasks cannot have new subtasks.

   Options:
   1. Reopen parent task (requires confirmation)
   2. Create new independent task
   3. Cancel
   ```
4. User chooses: "2" (New task)
5. Calls `project_task_create`
6. Returns task_id (not subtask_id)

---

## Integration with Other Directives

### Called By:
- `project_task_decomposition` - Primary caller for subtask creation
- User directly - Manual subtask creation

### Calls:
- `project_task_update` - Updates parent task status
- `project_task_create` - Fallback if parent invalid

---

## Database Updates

### Tables Modified:

**project.db**:
**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Roadblocks and Resolutions

### Roadblock 1: parent_task_not_found
**Issue**: Specified parent task doesn't exist
**Resolution**: List available open tasks, prompt user to select

### Roadblock 2: parent_task_completed
**Issue**: Cannot create subtask for completed task
**Resolution**: Offer to create new independent task instead

### Roadblock 3: parent_task_cancelled
**Issue**: Cannot create subtask for cancelled task
**Resolution**: Offer to reopen task or create new task

### Roadblock 4: multiple_active_subtasks
**Issue**: Another subtask already in progress
**Resolution**: Warn about context switching, confirm intent

### Roadblock 5: database_constraint_violation
**Issue**: Subtask creation violates database constraints
**Resolution**: Rollback, report specific constraint, prompt user

---

## Input Parameters

**Required**:
- `task_id` (int) - Parent task ID
- `name` (str) - Subtask name (non-empty, descriptive)

**Optional**:
- `description` (str, default: "") - Detailed subtask description

**Returns**:
```json
{
  "subtask_id": 7,
  "name": "Subtask name",
  "parent_task": "Parent task name",
  "parent_task_id": 15,
  "parent_status": "paused",
  "priority": "high",
  "status": "in_progress"
}
```

---

## Intent Keywords

- "create subtask"
- "add subtask"
- "break down task"
- "refine task"
- "subtask"

**Confidence Threshold**: 0.7

---

## Related Directives

- `project_task_decomposition` - Decides task vs. subtask
- `project_task_create` - Creates independent tasks
- `project_task_update` - Resumes parent when subtask completes
- `project_item_create` - Creates items (smaller than subtasks)

---

## Subtask Rules

**When to Use Subtasks**:
- Low-level, focused work (single function, small scope)
- Supports specific open task
- Should be done NOW before parent continues
- Typically 1-2 hours of work

**When NOT to Use Subtasks**:
- Independent work (use task instead)
- Exploratory work (use sidequest instead)
- Long-term work (use task instead)
- Optional work (use sidequest instead)

**Subtask Lifecycle**:
1. Created → Parent paused
2. In progress → Parent remains paused
3. Completed → Check if all subtasks complete
4. If all complete → Parent resumes (status: in_progress)
5. If subtasks remain → Parent stays paused

---

## Priority and Status

**Priority**:
- Always **high** (subtasks block parent task)
- Cannot be changed to lower priority
- Must complete before parent resumes

**Status**:
- Default: **in_progress** (immediate focus)
- If another subtask active: **pending** (queued)
- Valid transitions:
  - pending → in_progress
  - in_progress → completed
  - in_progress → cancelled

---

## Validation Rules

**Subtask Name**:
- Non-empty
- Max 200 characters
- Descriptive, action-oriented
- Specific (not "Fix bug" or "Update code")

**Parent Task**:
- Must exist in database
- Must be pending or in_progress (or already paused)
- Cannot be completed or cancelled

**Description**:
- Optional but recommended
- Max 2000 characters
- Should explain specific focus area

---

## Notes

- **Always pause parent task** - Subtasks block parent progress
- **High priority only** - Subtasks must complete before parent
- **Default in_progress** - Immediate focus unless another subtask active
- **Return subtask ID** - Enable immediate tracking
- **Log creation** - Audit trail in `notes` table
- **Warn on multiple active** - Prevent context switching
- **Atomic operation** - Single transaction, rollback on failure
- **Check parent status** - Cannot add to completed/cancelled tasks
