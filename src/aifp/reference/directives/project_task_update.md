# Directive: project_task_update

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: project_task_decomposition
**Priority**: HIGH - Essential for task lifecycle management

---

## Purpose

The `project_task_update` directive handles updating task, subtask, and sidequest status, priority, and metadata throughout the project lifecycle. This directive serves as the **task state manager**, ensuring accurate tracking of work progress and completion.

Key responsibilities:
- **Update task status** - pending → in_progress → completed/cancelled
- **Update priority** - Adjust based on changing project needs
- **Handle completion logic** - Mark items complete, trigger follow-up actions
- **Resume paused tasks** - When subtasks complete, resume parent tasks
- **Sync with database** - Ensure `project.db` reflects current state
- **Trigger downstream actions** - Notify `project_completion_check` when milestones complete
- **Maintain roadmap integrity** - Update `completion_path` progress

This is the **central task lifecycle manager** - all task state changes flow through here.

---

## When to Apply

This directive applies when:
- **Task status changes** - Moving through workflow states
- **Work is completed** - Marking tasks/subtasks/items as done
- **Priorities shift** - Adjusting task importance
- **Tasks are cancelled** - Removing obsolete work
- **Subtasks complete** - Resuming paused parent tasks
- **Called by other directives**:
  - `project_file_write` - Marks linked tasks complete after file generation
  - `project_completion_check` - Marks milestones complete
  - `aifp_status` - Updates task states based on current context

---

## Workflow

### Trunk: identify_update_type

Determines what aspect of the task needs updating.

**Steps**:
1. **Parse update request** - Status, priority, description, or metadata
2. **Validate update** - Ensure state transition is valid
3. **Query current state** - Get existing task data from database
4. **Apply update** - Modify task according to request

### Branches

**Branch 1: If status_update_requested**
- **Then**: `update_task_status`
- **Details**: Change task workflow state
  - Valid transitions:
    - `pending` → `in_progress`
    - `in_progress` → `completed`
    - `in_progress` → `cancelled`
    - `paused` → `in_progress` (when subtask completes)
  - Invalid transitions:
    - `completed` → any (completed tasks cannot be reopened)
    - `cancelled` → any (cancelled tasks stay cancelled)
  - Update `updated_at` timestamp
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Task status updated, timestamp recorded

**Branch 2: If task_completed**
- **Then**: `handle_completion`
- **Details**: Process task completion
  - Mark all associated items as complete
  - Check if milestone is complete (all tasks done)
  - Trigger `project_completion_check` for milestone
  - Log completion note with directive context
  - Calculate task duration: `completed_at - created_at`
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Task marked complete, milestone checked

**Branch 3: If subtask_completed_parent_paused**
- **Then**: `resume_parent_task`
- **Details**: Subtask done, resume parent
  - Check all subtasks for this parent
  - If all subtasks complete: Resume parent task (`paused` → `in_progress`)
  - If subtasks remaining: Keep parent paused
  - Log resume action
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Parent task resumed or kept paused

**Branch 4: If priority_update_requested**
- **Then**: `update_priority`
- **Details**: Change task priority (1-5, 1=highest)
  - Validate priority value (must be 1-5)
  - Update task priority
  - Log priority change with reason
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Priority adjusted, change logged

**Branch 5: If description_update_requested**
- **Then**: `update_description`
- **Details**: Modify task description or acceptance criteria
  - Update task description
  - Log change for transparency
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Description updated

**Branch 6: If task_cancelled**
- **Then**: `cancel_task`
- **Details**: Mark task as cancelled
  - Set status to 'cancelled'
  - Mark all items as cancelled
  - Log cancellation reason
  - Do NOT resume parent task (manual action required)
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Task cancelled, reason logged

**Branch 7: If milestone_complete**
- **Then**: `trigger_milestone_completion`
- **Details**: All tasks in milestone done
  - Update milestone status to 'completed'
  - Update `completion_path` progress
  - Trigger `project_completion_check`
  - Log milestone completion
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Milestone marked complete, progress updated

**Branch 8: If item_status_update**
- **Then**: `update_item_status`
- **Details**: Update individual items within task
  - Mark item as complete
  - Check if all items complete → Mark parent task complete
  - Log item completion
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Item updated, task completion checked

**Branch 9: If sidequest_status_update**
- **Then**: `update_sidequest_status`
- **Details**: Update exploratory sidequest
  - Sidequests can be: pending, in_progress, completed, abandoned
  - Log outcome for future reference
- **SQL**:
  **Use helper functions** for database operations. Query available helpers for the appropriate database.
- **Result**: Sidequest status updated

**Branch 10: If validation_required**
- **Then**: `validate_state_transition`
- **Details**: Ensure transition is valid
  - Check current state allows transition
  - Verify no blocking dependencies
  - Confirm no active subtasks (for task completion)
  - Prompt user if validation fails
- **Result**: Transition validated or blocked with explanation

**Fallback**: `prompt_user`
- Present issue and ask for clarification
- Log to `notes` for future reference

### Error Handling

**on_failure**: `prompt_user`
**retry**: max 2 attempts
- If update fails, rollback and prompt user
- Common issues: Invalid state transition, database lock, missing task

---

## Examples

### Example 1: Marking Task Complete

**User**: "Mark task 'Implement authentication' as complete"

**AI Execution**:
1. Queries current state: `status = 'in_progress'`
2. Validates transition: `in_progress` → `completed` ✓ Valid
3. Checks for active subtasks: None found
4. Updates task:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Marks all items as complete
6. Checks milestone progress:
   - Milestone: "Authentication System"
   - Tasks: 3 total, 3 completed
   - Action: Mark milestone complete
7. Triggers `project_completion_check`
8. Logs completion:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Example 2: Resuming Paused Task

**Context**:
- Task "Implement authentication" has 2 subtasks
- Subtask 1 "Add email verification" → completed
- Subtask 2 "Add password reset" → in_progress

**User**: "Mark subtask 'Add password reset' complete"

**AI Execution**:
1. Updates subtask:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
2. Checks all subtasks for parent task:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
3. Resumes parent task:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
4. Logs action:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Example 3: Updating Priority

**User**: "Increase priority of 'Fix security vulnerability' to highest"

**AI Execution**:
1. Queries current priority: `priority = 3`
2. Updates priority:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
3. Logs change:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Example 4: Cancelling Task

**User**: "Cancel task 'Implement dark mode'"

**AI Execution**:
1. Prompts for reason: "Why cancel this task?"
2. User responds: "Not needed for v1.0"
3. Updates task:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
4. Cancels all items:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Logs cancellation:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Example 5: Invalid Transition

**User**: "Reopen completed task 'Setup database'"

**AI Execution**:
1. Queries current state: `status = 'completed'`
2. Validates transition: `completed` → `in_progress` ✗ INVALID
3. Blocks transition:
   - Reason: "Completed tasks cannot be reopened"
   - Suggestion: "Create new task or subtask if additional work needed"
4. Prompts user: "Would you like to create a new task related to database setup instead?"

### Example 6: Milestone Completion Trigger

**Context**: Milestone "Core Operations" has 5 tasks

**User**: "Mark task 'Implement transpose' complete"

**AI Execution**:
1. Marks task complete:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
2. Checks milestone progress:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
3. Marks milestone complete:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
4. Updates completion path:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Triggers `project_completion_check` directive
6. Logs milestone completion:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Integration with Other Directives

### Called By:
- `project_file_write` - Marks tasks complete after file generation
- `project_task_decomposition` - Creates and initializes tasks
- `aifp_status` - Reports current task states

### Calls:
- `project_completion_check` - Validates milestone completion
- `project_update_db` - Syncs task metadata changes
- `project_evolution` - Handles goal changes affecting tasks

---

## Database Updates

### Tables Modified:

**project.db**:
**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Roadblocks and Resolutions

### Roadblock 1: invalid_state_transition
**Issue**: Attempted state change not allowed (e.g., completed → in_progress)
**Resolution**: Block transition, explain why, suggest alternative (create new task)

### Roadblock 2: active_subtasks_blocking
**Issue**: Cannot complete task with active subtasks
**Resolution**: Notify user of blocking subtasks, prompt to complete or cancel them first

### Roadblock 3: database_lock
**Issue**: Task locked by concurrent update
**Resolution**: Retry after brief delay (max 2 attempts), then prompt user

### Roadblock 4: orphaned_items
**Issue**: Items exist for non-existent task
**Resolution**: Link items to correct task or mark as orphaned in notes

---

## State Transition Rules

### Valid Transitions:
```
pending → in_progress → completed
pending → in_progress → cancelled
in_progress → paused (when subtask created)
paused → in_progress (when subtasks complete)
in_progress → cancelled
pending → cancelled
```

### Invalid Transitions:
```
completed → * (any state) ❌
cancelled → * (any state) ❌
paused → completed (must resume first) ❌
```

---

## Intent Keywords

- "mark complete"
- "mark done"
- "finish task"
- "update status"
- "change priority"
- "cancel task"
- "resume task"
- "complete"
- "done"

**Confidence Threshold**: 0.7

---

## Related Directives

- `project_task_decomposition` - Creates tasks
- `project_completion_check` - Validates milestone completion
- `project_file_write` - Triggers task completion
- `project_update_db` - Syncs metadata
- `aifp_status` - Reports task states
- `project_evolution` - Handles goal changes

---

## Notes

- **Completed tasks cannot be reopened** - Create new tasks instead
- **Subtasks block parent task completion** - Must complete or cancel subtasks first
- **Always log state changes** to `notes` table for audit trail
- **Trigger downstream checks** when milestones complete
- **Validate transitions** before applying to prevent invalid states
- **Calculate task duration** on completion for metrics
