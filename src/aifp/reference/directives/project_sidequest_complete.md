# Directive: project_sidequest_complete

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: project_task_update
**Priority**: MEDIUM - Captures exploratory work outcomes

---

## Purpose

The `project_sidequest_complete` directive handles the complete post-sidequest completion workflow, capturing lessons learned and managing work resumption.

Key responsibilities:
- Marks sidequest as complete
- **Captures lessons learned** from exploratory work
- Optionally resumes paused task
- Offers to create new task if sidequest revealed new work
- Logs outcomes for future reference

Sidequests are **low-priority exploratory work** that pause tasks for bug fixes, pivots, or unrelated investigations. This directive ensures knowledge is captured and work resumes appropriately.

---

## When to Apply

This directive is automatically triggered when:
- `project_task_update` changes a sidequest status to `completed`
- User explicitly says "complete sidequest [name]"
- Exploratory work is finished

**Delegation Chain**:
```
User marks sidequest complete
  → project_task_update (validates and updates status)
  → project_sidequest_complete (handles outcome capture and resumption)
  → Optionally resume paused task or create new task
```

---

## Workflow

### Trunk: mark_sidequest_complete

Primary execution path for sidequest completion and outcome capture.

### Branches

**Branch 1: If sidequest_valid_for_completion**
- **Then**: `mark_complete_and_log`
- **Details**:
  - Updates sidequest status to `completed`
  - Sets `completed_at` timestamp
  - Prompts for outcome description
- **SQL**:
  ```sql
  UPDATE sidequests
  SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
  WHERE id = ?;
  ```

**Branch 2: If sidequest_completed** ⭐ **CAPTURE LESSONS**
- **Then**: `capture_lessons_learned`
- **Details**:
  - Prompts user: "What did you learn from this sidequest?"
  - Logs outcome to notes table
  - Captures context for future reference
- **SQL**:
  ```sql
  INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name, severity)
  VALUES ('[user_response]', 'sidequest_outcome', 'sidequests', ?, 'user', 'project_sidequest_complete', 'info');
  ```
- **Prompt**: "What did you learn from this sidequest? (e.g., bug fix, architectural insight, new requirement)"

**Branch 3: If linked_to_paused_task**
- **Then**: `prompt_resume_work`
- **Details**:
  - Queries linked task from sidequests table
  - Presents options to user:
    1. Resume paused task
    2. Continue with different work
    3. Create new task based on sidequest findings
- **SQL**:
  ```sql
  SELECT paused_task_id, t.name
  FROM sidequests sq
  JOIN tasks t ON sq.paused_task_id = t.id
  WHERE sq.id = ?;
  ```
- **Notification**: "Sidequest '[sidequest_name]' complete. Resume paused task '[task_name]'?"

**Branch 4: If user_chooses_resume**
- **Then**: `resume_paused_task`
- **Details**:
  - Updates task status to `in_progress`
  - Logs resume action
  - Returns user to original work
- **SQL**:
  ```sql
  UPDATE tasks
  SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP
  WHERE id = ?;

  INSERT INTO notes (content, note_type, source, directive_name)
  VALUES ('Task resumed after sidequest completion: [task_name]', 'resume', 'directive', 'project_sidequest_complete');
  ```

**Branch 5: If sidequest_revealed_new_work**
- **Then**: `offer_task_creation`
- **Details**:
  - Sidequest findings suggest new task needed
  - Prompt user to create task
  - Delegates to `project_task_create`
- **Prompt**: "Should we create a new task based on sidequest findings?"

**Fallback**: `prompt_user`
- User clarification needed
- Log outcome and defer decisions

### Error Handling

**on_failure**: `prompt_user`
**retry**: max 1 attempt

- If outcome capture fails: Complete sidequest anyway, log warning
- If resume fails: Prompt user for manual action

---

## Examples

### Example 1: Sidequest Complete, Resume Paused Task

**Context**:
- Paused Task: "Implement user registration"
- Sidequest: "Fix email validation bug in dependency"

**User**: "Complete sidequest 'Fix email validation bug in dependency'"

**AI Execution**:
1. Marks sidequest complete:
   ```sql
   UPDATE sidequests SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = 12;
   ```
2. Captures lessons learned:
   - Prompts: "What did you learn from this sidequest?"
   - User responds: "Email regex was too strict, updated to RFC 5322 standard"
   - Logs:
     ```sql
     INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
     VALUES ('Email regex was too strict, updated to RFC 5322 standard', 'sidequest_outcome', 'sidequests', 12, 'user', 'project_sidequest_complete');
     ```
3. Checks linked task:
   ```sql
   SELECT paused_task_id, t.name FROM sidequests sq JOIN tasks t ON sq.paused_task_id = t.id WHERE sq.id = 12;
   -- Result: Task 8 - "Implement user registration"
   ```
4. Prompts user:
   ```
   Sidequest 'Fix email validation bug in dependency' complete!

   Resume paused task 'Implement user registration'?
   1. Resume paused task
   2. Continue with different work
   3. Create new task based on findings
   ```
5. User chooses: "Resume paused task"
6. Resumes task:
   ```sql
   UPDATE tasks SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP WHERE id = 8;
   ```
7. Notifies user:
   ```
   Task 'Implement user registration' resumed.
   You can now continue where you left off.
   ```

**Result**: Work resumes seamlessly, lessons captured

### Example 2: Sidequest Reveals New Task

**Context**:
- Sidequest: "Investigate performance bottleneck"

**User**: "Complete sidequest 'Investigate performance bottleneck'"

**AI Execution**:
1. Marks sidequest complete
2. Captures lessons:
   - Prompts: "What did you learn?"
   - User responds: "Database queries are N+1 problem, need to refactor with joins"
   - Logs outcome
3. Not linked to paused task (exploratory)
4. **Sidequest revealed new work**:
   - Prompts: "Should we create a new task based on sidequest findings?"
   - User responds: "Yes, create task to refactor database queries"
5. Delegates to `project_task_create`:
   - Task name: "Refactor database queries to eliminate N+1"
   - Task items:
     - Identify all N+1 queries
     - Add database joins
     - Add query performance tests
     - Update documentation
6. New task created and set to `in_progress`

**Result**: Exploratory work leads to new actionable task

### Example 3: Sidequest Reveals Pivot

**Context**:
- Sidequest: "Research alternative authentication libraries"

**User**: "Complete sidequest 'Research alternative authentication libraries'"

**AI Execution**:
1. Marks sidequest complete
2. Captures lessons:
   - Prompts: "What did you learn?"
   - User responds: "Current approach won't scale, need to pivot to OAuth 2.0"
3. **Sidequest reveals pivot**:
   - Logs to notes with severity `warning`:
     ```sql
     INSERT INTO notes (content, note_type, severity, source, directive_name)
     VALUES ('Research suggests pivot: Current approach won''t scale, need OAuth 2.0', 'sidequest_outcome', 'warning', 'user', 'project_sidequest_complete');
     ```
4. Prompts user:
   ```
   ⚠️ Sidequest findings suggest a project pivot:
   "Current approach won't scale, need to pivot to OAuth 2.0"

   This may affect the completion path and milestones.
   Would you like to:
   1. Call project_evolution to handle roadmap change
   2. Create tasks for migration
   3. Discuss strategy before proceeding
   ```
5. User chooses: "Call project_evolution"
6. Delegates to `project_evolution` to handle pivot

**Result**: Major findings escalated appropriately

### Example 4: Standalone Sidequest, No Paused Task

**Context**:
- Sidequest: "Experiment with new CSS framework" (not linked to any task)

**User**: "Complete sidequest 'Experiment with new CSS framework'"

**AI Execution**:
1. Marks sidequest complete
2. Captures lessons:
   - Prompts: "What did you learn?"
   - User responds: "Framework is good but too heavy for our use case"
   - Logs outcome
3. No paused task linked:
   - Prompts: "Sidequest complete. What's next?"
   - Options:
     1. Continue with existing task
     2. Create new task
     3. Start different work
4. User chooses: "Continue with existing task"
5. Returns to work

**Result**: Exploratory work documented, user continues

---

## Integration with Other Directives

### Called By:
- `project_task_update` - Delegates when sidequest status changes to completed

### Calls:
- `project_task_create` - If user wants to create task from findings
- `project_evolution` - If sidequest reveals pivot

### Triggers:
- Task resumption if linked
- New task creation if findings warrant it
- Project evolution if pivot detected

---

## Database Updates

### Tables Modified:

**project.db**:
```sql
-- Mark sidequest complete
UPDATE sidequests SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Resume paused task (if user chooses)
UPDATE tasks SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Log outcome
INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name, severity)
VALUES ('[user_response]', 'sidequest_outcome', 'sidequests', ?, 'user', 'project_sidequest_complete', 'info');

-- Log resume (if applicable)
INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
VALUES ('Task resumed after sidequest completion', 'resume', 'tasks', ?, 'directive', 'project_sidequest_complete');
```

### Tables Queried:
```sql
-- Check linked task
SELECT paused_task_id, paused_subtask_id, t.name as task_name
FROM sidequests sq
LEFT JOIN tasks t ON sq.paused_task_id = t.id
WHERE sq.id = ?;

-- Get sidequest details
SELECT name, description, status FROM sidequests WHERE id = ?;
```

---

## Roadblocks and Resolutions

### Roadblock 1: sidequest_reveals_pivot
**Issue**: Sidequest findings suggest project direction change
**Resolution**: Capture findings in notes (severity: warning), discuss with user if `project_evolution` should be triggered

### Roadblock 2: paused_task_no_longer_relevant
**Issue**: After sidequest, paused task is obsolete
**Resolution**: Offer to cancel paused task instead of resuming

### Roadblock 3: user_forgets_context
**Issue**: User completed sidequest but forgot original context
**Resolution**: Show paused task details, offer to review before resuming

---

## Intent Keywords

- "complete sidequest"
- "finish sidequest"
- "sidequest done"
- "exploratory work done"
- "sidequest finished"

**Confidence Threshold**: 0.8

---

## Related Directives

- `project_task_update` - Parent directive that delegates here
- `project_sidequest_create` - Creates sidequests and links to paused work
- `project_task_complete` - Sibling directive for task completion
- `project_subtask_complete` - Sibling directive for subtask completion
- `project_task_create` - Called when creating task from findings
- `project_evolution` - Called when pivot detected

---

## Notes

- **Lessons learned** capture is the key feature - preserves exploratory knowledge
- Sidequests are low-priority by default (defined in `project_sidequest_create`)
- Not all sidequests link to paused tasks (standalone exploration is valid)
- Always prompt user for outcome description
- Major findings (pivots) should escalate to `project_evolution`
- Flexible resumption - user chooses what's next
- Logs all outcomes for future reference and pattern detection
