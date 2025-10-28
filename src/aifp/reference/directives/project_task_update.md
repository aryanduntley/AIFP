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
  - `project_compliance_check` - Updates tasks based on validation results
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
  ```sql
  UPDATE tasks
  SET status = ?, updated_at = CURRENT_TIMESTAMP
  WHERE id = ? AND status NOT IN ('completed', 'cancelled');
  ```
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
  ```sql
  UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?;

  UPDATE items SET status = 'completed' WHERE task_id = ? AND status != 'completed';

  INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
  VALUES ('Task completed: [name]', 'completion', 'tasks', ?, 'directive', 'project_task_update');
  ```
- **Result**: Task marked complete, milestone checked

**Branch 3: If subtask_completed_parent_paused**
- **Then**: `resume_parent_task`
- **Details**: Subtask done, resume parent
  - Check all subtasks for this parent
  - If all subtasks complete: Resume parent task (`paused` → `in_progress`)
  - If subtasks remaining: Keep parent paused
  - Log resume action
- **SQL**:
  ```sql
  -- Check if all subtasks complete
  SELECT COUNT(*) FROM subtasks
  WHERE task_id = ? AND status NOT IN ('completed', 'cancelled');

  -- If count = 0, resume parent
  UPDATE tasks SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP
  WHERE id = ? AND status = 'paused';
  ```
- **Result**: Parent task resumed or kept paused

**Branch 4: If priority_update_requested**
- **Then**: `update_priority`
- **Details**: Change task priority (1-5, 1=highest)
  - Validate priority value (must be 1-5)
  - Update task priority
  - Log priority change with reason
- **SQL**:
  ```sql
  UPDATE tasks SET priority = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;

  INSERT INTO notes (content, source, directive_name)
  VALUES ('Task priority updated: [old] → [new]. Reason: [reason]', 'directive', 'project_task_update');
  ```
- **Result**: Priority adjusted, change logged

**Branch 5: If description_update_requested**
- **Then**: `update_description`
- **Details**: Modify task description or acceptance criteria
  - Update task description
  - Log change for transparency
- **SQL**:
  ```sql
  UPDATE tasks SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;
  ```
- **Result**: Description updated

**Branch 6: If task_cancelled**
- **Then**: `cancel_task`
- **Details**: Mark task as cancelled
  - Set status to 'cancelled'
  - Mark all items as cancelled
  - Log cancellation reason
  - Do NOT resume parent task (manual action required)
- **SQL**:
  ```sql
  UPDATE tasks SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP WHERE id = ?;

  UPDATE items SET status = 'cancelled' WHERE task_id = ?;

  INSERT INTO notes (content, note_type, source, directive_name)
  VALUES ('Task cancelled: [name]. Reason: [reason]', 'cancellation', 'directive', 'project_task_update');
  ```
- **Result**: Task cancelled, reason logged

**Branch 7: If milestone_complete**
- **Then**: `trigger_milestone_completion`
- **Details**: All tasks in milestone done
  - Update milestone status to 'completed'
  - Update `completion_path` progress
  - Trigger `project_completion_check`
  - Log milestone completion
- **SQL**:
  ```sql
  UPDATE milestones SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?;

  UPDATE completion_path SET status = 'completed' WHERE id = ?;
  ```
- **Result**: Milestone marked complete, progress updated

**Branch 8: If item_status_update**
- **Then**: `update_item_status`
- **Details**: Update individual items within task
  - Mark item as complete
  - Check if all items complete → Mark parent task complete
  - Log item completion
- **SQL**:
  ```sql
  UPDATE items SET status = 'completed', updated_at = CURRENT_TIMESTAMP WHERE id = ?;

  -- Check if all items for task are complete
  SELECT COUNT(*) FROM items WHERE task_id = ? AND status != 'completed';

  -- If count = 0, mark task complete
  UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?;
  ```
- **Result**: Item updated, task completion checked

**Branch 9: If sidequest_status_update**
- **Then**: `update_sidequest_status`
- **Details**: Update exploratory sidequest
  - Sidequests can be: pending, in_progress, completed, abandoned
  - Log outcome for future reference
- **SQL**:
  ```sql
  UPDATE sidequests SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;
  ```
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
   ```sql
   UPDATE tasks
   SET status = 'completed', completed_at = CURRENT_TIMESTAMP
   WHERE id = 15;
   ```
5. Marks all items as complete
6. Checks milestone progress:
   - Milestone: "Authentication System"
   - Tasks: 3 total, 3 completed
   - Action: Mark milestone complete
7. Triggers `project_completion_check`
8. Logs completion:
   ```sql
   INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
   VALUES ('Task completed: Implement authentication. Duration: 5 days.',
           'completion', 'tasks', 15, 'directive', 'project_task_update');
   ```

### Example 2: Resuming Paused Task

**Context**:
- Task "Implement authentication" has 2 subtasks
- Subtask 1 "Add email verification" → completed
- Subtask 2 "Add password reset" → in_progress

**User**: "Mark subtask 'Add password reset' complete"

**AI Execution**:
1. Updates subtask:
   ```sql
   UPDATE subtasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = 7;
   ```
2. Checks all subtasks for parent task:
   ```sql
   SELECT COUNT(*) FROM subtasks
   WHERE task_id = 15 AND status NOT IN ('completed', 'cancelled');
   -- Result: 0 (all subtasks complete)
   ```
3. Resumes parent task:
   ```sql
   UPDATE tasks SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP
   WHERE id = 15 AND status = 'paused';
   ```
4. Logs action:
   ```sql
   INSERT INTO notes (content, source, directive_name)
   VALUES ('All subtasks complete for task 15. Parent task resumed.',
           'directive', 'project_task_update');
   ```

### Example 3: Updating Priority

**User**: "Increase priority of 'Fix security vulnerability' to highest"

**AI Execution**:
1. Queries current priority: `priority = 3`
2. Updates priority:
   ```sql
   UPDATE tasks SET priority = 1, updated_at = CURRENT_TIMESTAMP WHERE id = 42;
   ```
3. Logs change:
   ```sql
   INSERT INTO notes (content, source, directive_name)
   VALUES ('Task priority updated: 42 - Fix security vulnerability. Priority: 3 → 1 (highest). Reason: Security critical.',
           'directive', 'project_task_update');
   ```

### Example 4: Cancelling Task

**User**: "Cancel task 'Implement dark mode'"

**AI Execution**:
1. Prompts for reason: "Why cancel this task?"
2. User responds: "Not needed for v1.0"
3. Updates task:
   ```sql
   UPDATE tasks SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP WHERE id = 28;
   ```
4. Cancels all items:
   ```sql
   UPDATE items SET status = 'cancelled' WHERE task_id = 28;
   ```
5. Logs cancellation:
   ```sql
   INSERT INTO notes (content, note_type, source, directive_name)
   VALUES ('Task cancelled: 28 - Implement dark mode. Reason: Not needed for v1.0.',
           'cancellation', 'directive', 'project_task_update');
   ```

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
   ```sql
   UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = 18;
   ```
2. Checks milestone progress:
   ```sql
   SELECT COUNT(*) FROM tasks WHERE milestone_id = 3 AND status != 'completed';
   -- Result: 0 (all tasks complete)
   ```
3. Marks milestone complete:
   ```sql
   UPDATE milestones SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = 3;
   ```
4. Updates completion path:
   ```sql
   UPDATE completion_path SET status = 'completed' WHERE id = 2;
   ```
5. Triggers `project_completion_check` directive
6. Logs milestone completion:
   ```sql
   INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
   VALUES ('Milestone completed: Core Operations. All 5 tasks finished.',
           'milestone_completion', 'milestones', 3, 'directive', 'project_task_update');
   ```

---

## Integration with Other Directives

### Called By:
- `project_file_write` - Marks tasks complete after file generation
- `project_compliance_check` - Updates based on validation
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
```sql
-- Update task status
UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Update subtask and resume parent
UPDATE subtasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?;
UPDATE tasks SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'paused';

-- Update priority
UPDATE tasks SET priority = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Update items
UPDATE items SET status = 'completed', updated_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Cancel task
UPDATE tasks SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP WHERE id = ?;
UPDATE items SET status = 'cancelled' WHERE task_id = ?;

-- Milestone completion
UPDATE milestones SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?;
UPDATE completion_path SET status = 'completed' WHERE id = ?;

-- Log to notes
INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name, severity)
VALUES (?, ?, ?, ?, 'directive', 'project_task_update', 'info');
```

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
