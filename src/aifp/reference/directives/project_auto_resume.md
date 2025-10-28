# Directive: project_auto_resume

**Type**: Project
**Level**: 3 (Operational Execution)
**Parent Directive**: aifp_run
**Priority**: HIGH - Session continuity and workflow restoration

---

## Purpose

The `project_auto_resume` directive detects unfinished tasks or subtasks from `project.db` and resumes execution at the appropriate directive entry point. This directive serves as the **workflow continuity manager**, restoring work context between user sessions or after interruptions, ensuring seamless continuation of project work.

Key responsibilities:
- **Detect incomplete work** - Identify paused or in-progress tasks
- **Restore context** - Load task/subtask details and history
- **Resume execution** - Continue from last checkpoint
- **Handle interruptions** - Gracefully recover from session breaks
- **Prioritize resumption** - Follow priority order (sidequests → subtasks → tasks)
- **Prompt for confirmation** - User verifies resumption before proceeding

This is the **session continuity handler** - ensures work never gets lost or forgotten.

---

## When to Apply

This directive applies when:
- **Session start** - User returns after break ("continue", "resume work")
- **After interruption** - System crash, user logged out, session ended
- **Explicit resumption** - User says "resume" or "continue where we left off"
- **Task paused** - Work interrupted by subtask, now subtask complete
- **Called by other directives**:
  - `aifp_run` - May auto-trigger on session start
  - `aifp_status` - Identifies work to resume, may call auto_resume
  - `project_task_update` - After subtask completion, may resume parent
  - User directly - Manual resumption request

---

## Workflow

### Trunk: detect_incomplete_tasks

Identifies work that should be resumed based on status and priority.

**Steps**:
1. **Query incomplete work** - Find tasks/subtasks with status 'in_progress' or 'paused'
2. **Prioritize by hierarchy** - Sidequests > subtasks > tasks
3. **Load context** - Get task details, items, history
4. **Check resumability** - Verify task can continue (no blockers)
5. **Prompt user** - Confirm resumption or choose different work
6. **Resume execution** - Call appropriate directive to continue work

### Branches

**Branch 1: If task_paused**
- **Then**: `resume_from_checkpoint`
- **Details**: Task is paused, likely waiting for subtask completion
  - Check if blocking subtasks are complete
  - If all subtasks complete: Resume parent task
  - If subtasks remain: Continue with next subtask
  - Update task status from 'paused' to 'in_progress'
  - Load task context (items, completed work)
- **SQL**:
  ```sql
  -- Find paused tasks
  SELECT id, name, milestone_id, description, updated_at
  FROM tasks
  WHERE status = 'paused'
  ORDER BY updated_at DESC;

  -- Check blocking subtasks
  SELECT id, name, status, priority
  FROM subtasks
  WHERE task_id = ? AND status != 'completed'
  ORDER BY priority DESC;

  -- If no blocking subtasks, resume task
  UPDATE tasks
  SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP
  WHERE id = ?;
  ```
- **Result**: Paused task resumed, user notified of context

**Branch 2: If sidequest_paused**
- **Then**: `prompt_resume`
- **Details**: Sidequest is paused or in-progress
  - Sidequests are exploratory, may be abandoned
  - Prompt user: "Resume sidequest or mark complete/cancelled?"
  - If resume: Load sidequest context
  - If complete: Mark complete, return to main work
  - If cancel: Mark cancelled, return to main work
- **SQL**:
  ```sql
  -- Find paused/in-progress sidequests
  SELECT id, name, task_id, status, description, updated_at
  FROM sidequests
  WHERE status IN ('paused', 'in_progress')
  ORDER BY updated_at DESC;
  ```
- **Prompt**:
  ```
  Sidequest in progress: "{sidequest_name}"
  Started: {created_at}
  Last updated: {updated_at}

  This sidequest is exploratory work related to task "{parent_task_name}".

  Options:
  1. Resume sidequest
  2. Mark complete (findings added to notes)
  3. Cancel (abandon exploration)

  Choose action:
  ```
- **Result**: User decides sidequest fate, work continues

**Branch 3: If subtask_incomplete**
- **Then**: `resume_subtask_work`
- **Details**: Subtask is in-progress, blocking parent task
  - Subtasks are high-priority, must complete before parent
  - Load subtask context (description, items, parent task)
  - Resume work on subtask
  - Parent task remains paused until subtask complete
- **SQL**:
  ```sql
  -- Find in-progress subtasks
  SELECT st.id, st.name, st.task_id, st.description, st.updated_at, t.name as parent_task
  FROM subtasks st
  JOIN tasks t ON st.task_id = t.id
  WHERE st.status = 'in_progress'
  ORDER BY st.priority DESC, st.updated_at DESC;
  ```
- **Context Loading**:
  ```sql
  -- Get subtask items
  SELECT id, name, status, created_at
  FROM items
  WHERE subtask_id = ?
  ORDER BY status ASC, created_at ASC;
  ```
- **Result**: Subtask work resumed, parent remains paused

**Branch 4: If task_in_progress**
- **Then**: `resume_task_work`
- **Details**: Task is in-progress, no blocking subtasks
  - Load task context (items, completed work, milestone)
  - Show progress: X/Y items complete
  - Continue with next incomplete item
  - Update task as in-progress
- **SQL**:
  ```sql
  -- Find in-progress tasks
  SELECT t.id, t.name, t.milestone_id, t.description, m.name as milestone
  FROM tasks t
  JOIN milestones m ON t.milestone_id = m.id
  WHERE t.status = 'in_progress'
  ORDER BY t.priority DESC, t.updated_at DESC;

  -- Get task items
  SELECT id, name, status
  FROM items
  WHERE task_id = ?
  ORDER BY status ASC, created_at ASC;
  ```
- **Context Report**:
  ```
  Resuming task: "{task_name}"
  Milestone: {milestone_name}
  Progress: {completed_items}/{total_items} items complete

  Completed:
  - {item_1_name} ✓
  - {item_2_name} ✓

  Remaining:
  - {item_3_name}
  - {item_4_name}

  Next: {item_3_name}
  ```
- **Result**: Task work resumed with clear next action

**Branch 5: If no_incomplete_work**
- **Then**: `mark_as_resolved`
- **Details**: No paused or in-progress work found
  - All tasks either pending or completed
  - Report: "No work to resume"
  - Suggest: Check status or start new task
- **Result**: User informed no resumption needed

**Branch 6: If resume_conflict**
- **Then**: `prompt_user_choice`
- **Details**: Multiple incomplete tasks, ambiguous which to resume
  - List all in-progress/paused work
  - Show priority and last updated
  - Prompt user to choose
  - Resume selected work
- **Prompt**:
  ```
  Multiple incomplete work items found:

  1. Subtask: "Fix memory leak" (priority: high, updated 2 days ago)
     Parent: Task "Optimize database"

  2. Task: "Implement caching" (in_progress, updated 5 days ago)
     Milestone: Performance

  3. Sidequest: "Research Redis" (in_progress, updated 1 week ago)
     Parent: Task "Implement caching"

  Which should I resume? (1-3, or 'none' to start fresh)
  ```
- **Result**: User selects work to resume

**Branch 7: If checkpoint_invalid**
- **Then**: `discard_and_start_fresh`
- **Details**: Resume state is corrupted or outdated
  - Task/subtask exists but context missing
  - Items deleted or task structure changed
  - Prompt: "Cannot resume, state changed. Start fresh?"
  - Options: Mark current as cancelled, start new task
- **Result**: Corrupt state handled gracefully

**Branch 8: If auto_resume_enabled**
- **Then**: `auto_resume_highest_priority`
- **Details**: User preferences set to auto-resume without prompt
  - Select highest priority incomplete work
  - Load context automatically
  - Begin execution without user confirmation
  - Log auto-resume action
- **User Preference Check**:
  ```sql
  SELECT preference_value FROM directive_preferences
  WHERE directive_name = 'project_auto_resume' AND preference_key = 'auto_resume_enabled' AND active = 1;
  -- If preference_value = 'true', auto-resume
  ```
- **Result**: Work resumed automatically

**Fallback**: `mark_as_resolved`
- No work to resume or cannot determine correct action
- Report "No resumable work" and suggest next steps

### Error Handling

**on_failure**: `prompt_user`
- If resumption fails: Log error, prompt user for manual action
- Common issues: Context missing, state corrupted, database inconsistency

---

## Examples

### Example 1: Resume Paused Task After Subtask Completion

**Context**: User completed subtask, parent task auto-resumes

**AI Execution**:
1. Subtask "Fix memory leak" marked complete (via `project_task_update`)
2. `project_task_update` checks parent task:
   ```sql
   SELECT id, status FROM tasks WHERE id = (SELECT task_id FROM subtasks WHERE id = 8);
   -- Result: Task #15 "Optimize database" (status: paused)
   ```
3. Checks for remaining subtasks:
   ```sql
   SELECT COUNT(*) FROM subtasks WHERE task_id = 15 AND status != 'completed';
   -- Result: 0 (no more blocking subtasks)
   ```
4. Triggers `project_auto_resume` for task #15
5. Updates task status:
   ```sql
   UPDATE tasks SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP WHERE id = 15;
   ```
6. Loads task context:
   ```sql
   SELECT id, name, status FROM items WHERE task_id = 15 ORDER BY status ASC;
   -- Results: 3/5 items complete
   ```
7. Reports to user:
   ```
   ✓ Subtask "Fix memory leak" complete!

   Resuming parent task: "Optimize database"
   Progress: 3/5 items complete

   Completed:
   - Profile slow queries ✓
   - Add indexes ✓
   - Fix memory leak ✓ (just completed)

   Remaining:
   - Optimize connection pooling
   - Load test improvements

   Next: Optimize connection pooling
   ```
8. User continues work on next item

### Example 2: User Returns After Break

**Context**: User says "continue" after logging back in

**AI Execution**:
1. Triggered by `aifp_run` detecting "continue" keyword
2. Queries for incomplete work:
   ```sql
   -- Check sidequests
   SELECT id, name FROM sidequests WHERE status IN ('paused', 'in_progress');
   -- Result: None

   -- Check subtasks
   SELECT id, name, task_id FROM subtasks WHERE status = 'in_progress';
   -- Result: None

   -- Check tasks
   SELECT id, name, milestone_id FROM tasks WHERE status = 'in_progress' ORDER BY priority DESC, updated_at DESC;
   -- Result: Task #20 "Implement authentication" (updated 2 hours ago)
   ```
3. Loads task context:
   ```sql
   SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
   FROM items WHERE task_id = 20;
   -- Result: 2/6 items complete
   ```
4. Prompts user:
   ```
   Welcome back!

   You were working on: "Implement authentication"
   Milestone: Core Features
   Progress: 2/6 items (33%)
   Last updated: 2 hours ago

   Resume this task? (y/n)
   ```
5. User: "y"
6. Loads full context:
   ```sql
   SELECT id, name, status FROM items WHERE task_id = 20 ORDER BY status ASC, created_at ASC;
   ```
7. Reports:
   ```
   Resuming: "Implement authentication"

   Completed:
   - Set up auth schema ✓
   - Create user model ✓

   Next:
   - Implement password hashing
   - Create login endpoint
   - Add JWT tokens
   - Write auth tests

   Starting with: Implement password hashing
   ```
8. Work continues

### Example 3: Multiple Incomplete Work Items

**Context**: User has paused sidequest, in-progress task, and paused task

**AI Execution**:
1. Queries all incomplete work:
   ```sql
   SELECT 'sidequest' as type, id, name, status, updated_at FROM sidequests WHERE status IN ('paused', 'in_progress')
   UNION ALL
   SELECT 'subtask' as type, id, name, status, updated_at FROM subtasks WHERE status = 'in_progress'
   UNION ALL
   SELECT 'task' as type, id, name, status, updated_at FROM tasks WHERE status IN ('paused', 'in_progress')
   ORDER BY CASE type WHEN 'sidequest' THEN 1 WHEN 'subtask' THEN 2 ELSE 3 END, updated_at DESC;
   ```
2. Results:
   - Sidequest #5: "Research Redis alternatives" (in_progress, 1 week ago)
   - Task #18: "Implement caching" (in_progress, 3 days ago)
   - Task #12: "Refactor database" (paused, 5 days ago)
3. Prompts user with priority order:
   ```
   Multiple incomplete work items:

   1. [SIDEQUEST] "Research Redis alternatives" (highest priority)
      Status: in_progress
      Last updated: 1 week ago
      Note: Exploratory work, may be abandoned

   2. [TASK] "Implement caching"
      Status: in_progress
      Progress: 2/8 items (25%)
      Last updated: 3 days ago

   3. [TASK] "Refactor database"
      Status: paused (blocked by subtask previously)
      Last updated: 5 days ago

   Which should I resume? (1-3, 'status' for more info, 'none' to start fresh)
   ```
4. User: "2" (Choose task #18)
5. Loads context for task #18 and resumes

### Example 4: Sidequest Resumption or Abandonment

**Context**: User has paused sidequest, needs to decide fate

**AI Execution**:
1. Detects sidequest #7: "Explore graph databases" (paused, 2 weeks ago)
2. Loads sidequest context:
   ```sql
   SELECT sq.id, sq.name, sq.description, sq.task_id, t.name as parent_task
   FROM sidequests sq
   JOIN tasks t ON sq.task_id = t.id
   WHERE sq.id = 7;
   -- Result: Related to task "Choose database solution"
   ```
3. Prompts user:
   ```
   Sidequest found: "Explore graph databases"
   Related to: Task "Choose database solution"
   Started: 2 weeks ago
   Status: Paused

   This sidequest has been inactive for 2 weeks.

   Options:
   1. Resume exploration
   2. Mark complete (add findings to notes)
   3. Cancel (abandon, no longer relevant)

   Choose action:
   ```
4. User: "2" (Mark complete)
5. Prompts for findings:
   ```
   Sidequest complete! Any findings to note?
   (Optional, press Enter to skip)
   ```
6. User: "Neo4j looks promising but too complex for our use case"
7. Marks complete and logs:
   ```sql
   UPDATE sidequests SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = 7;

   INSERT INTO notes (content, note_type, reference_table, reference_id, source)
   VALUES ('Sidequest "Explore graph databases" complete. Findings: Neo4j looks promising but too complex for our use case', 'sidequest_completion', 'sidequests', 7, 'user');
   ```
8. Returns to main work

### Example 5: Auto-Resume Enabled

**Context**: User has preference set to auto-resume highest priority

**AI Execution**:
1. User says "continue" or starts session
2. Checks user preference:
   ```sql
   SELECT preference_value FROM directive_preferences
   WHERE directive_name = 'project_auto_resume' AND preference_key = 'auto_resume_enabled' AND active = 1;
   -- Result: 'true'
   ```
3. Queries incomplete work (same as Example 3)
4. Selects highest priority automatically:
   - Sidequest #5 (highest priority by hierarchy)
5. Loads context and begins without prompt:
   ```
   Auto-resuming: Sidequest "Research Redis alternatives"
   (User preference: auto-resume enabled)

   Context: Exploring cache solutions for Task "Implement caching"
   Started: 1 week ago

   Continuing exploration...
   ```
6. Work resumes automatically

### Example 6: No Work to Resume

**Context**: All tasks either pending or completed

**AI Execution**:
1. Queries incomplete work:
   ```sql
   SELECT COUNT(*) FROM tasks WHERE status IN ('paused', 'in_progress');
   -- Result: 0
   ```
2. Reports:
   ```
   No work to resume.

   All tasks are either:
   - Pending (not started)
   - Completed

   Suggested next steps:
   1. Check status: 'aifp_status'
   2. Start new task from current milestone
   3. Review completed work

   What would you like to do?
   ```
3. User decides next action

---

## Integration with Other Directives

### Called By:
- `aifp_run` - May auto-trigger on session start
- `aifp_status` - Identifies work to resume
- `project_task_update` - After subtask completion
- User directly - Manual "resume" or "continue"

### Calls:
- Task execution directives - Resumes appropriate work
- `aifp_status` - Provides context for resumption

---

## Database Updates

### Tables Modified:

**project.db**:
```sql
-- Resume paused task
UPDATE tasks SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Complete sidequest
UPDATE sidequests SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Cancel sidequest
UPDATE sidequests SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Log resumption
INSERT INTO notes (content, note_type, source, directive_name)
VALUES (?, 'resumption', 'directive', 'project_auto_resume');
```

---

## Roadblocks and Resolutions

### Roadblock 1: resume_conflict
**Issue**: Multiple incomplete tasks, unclear which to resume
**Resolution**: Prompt user to choose branch or discard task, list all incomplete work with priority

### Roadblock 2: context_corrupted
**Issue**: Task exists but items/context missing
**Resolution**: Mark task as corrupted, suggest starting fresh or investigating

### Roadblock 3: ambiguous_priority
**Issue**: Cannot determine highest priority work
**Resolution**: Prompt user with all options, let user decide

### Roadblock 4: auto_resume_failure
**Issue**: Auto-resume enabled but cannot determine work to resume
**Resolution**: Fall back to manual prompt, log failure

---

## Intent Keywords

- "resume"
- "continue"
- "checkpoint"
- "where was I"
- "continue work"
- "pick up where I left off"

**Confidence Threshold**: 0.7

---

## Related Directives

- `aifp_run` - Gateway directive, may trigger auto-resume
- `aifp_status` - Provides context for resumption decisions
- `project_task_update` - May trigger resume after subtask completion
- `project_task_decomposition` - Creates tasks that may need resumption

---

## Resumption Priority Order

**Hierarchy**:
1. **Sidequests** (highest priority)
   - Exploratory work, often forgotten
   - Prompt for completion/cancellation if old

2. **Subtasks** (high priority)
   - Block parent tasks
   - Must complete before parent continues

3. **Tasks** (standard priority)
   - Main work items
   - Resume in order of priority and recency

**Selection Logic**:
```
if sidequests.in_progress:
    prompt_sidequest_action()
elif subtasks.in_progress:
    resume_subtask()
elif tasks.paused:
    check_subtasks_complete()
    if all_subtasks_complete:
        resume_task()
elif tasks.in_progress:
    resume_task()
else:
    no_work_to_resume()
```

---

## User Preferences

### auto_resume_enabled
- **Type**: Boolean
- **Default**: false
- **Effect**: Auto-resume highest priority work without prompt
- **Use Case**: Power users who want seamless continuation

### resume_confirmation_required
- **Type**: Boolean
- **Default**: true
- **Effect**: Always prompt before resuming, even with single item
- **Use Case**: Users who want explicit control

### auto_abandon_stale_sidequests
- **Type**: Boolean + duration
- **Default**: false
- **Effect**: Auto-cancel sidequests older than N days
- **Use Case**: Clean up forgotten exploratory work

---

## Notes

- **Priority order** - Sidequests → subtasks → tasks
- **Context restoration** - Load full task/item context before resuming
- **Prompt for confirmation** - User verifies resumption (unless auto-resume enabled)
- **Handle abandonment** - Gracefully handle stale sidequests
- **Auto-resume parent** - When subtask completes, resume parent task
- **Detect conflicts** - Multiple incomplete items, prompt user to choose
- **Preserve state** - Never lose work progress
- **Log resumptions** - Audit trail in notes table
- **Support preferences** - Respect user settings for auto-resume
- **Graceful degradation** - Handle corrupted state by starting fresh
