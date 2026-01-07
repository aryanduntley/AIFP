# Directive: project_completion_check

**Type**: Project
**Level**: 4 (State Management)
**Parent Directive**: project_milestone_complete
**Priority**: MEDIUM - Roadmap progress evaluation

---

## Purpose

The `project_completion_check` directive evaluates roadmap progress and completion readiness by checking completion_path, milestones, and tasks for status updates. This directive serves as the **completion monitor**, marking completion milestones when conditions are met and preventing premature completion marking.

Key responsibilities:
- **Monitor roadmap alignment** - Check if work aligns with completion path
- **Mark progress milestones** - Update status when criteria met
- **Detect roadmap drift** - Identify misalignment between plan and execution
- **Prevent premature completion** - Ensure all requirements met before marking complete
- **Auto-complete parent tasks** - Mark tasks complete when all items/subtasks done
- **Log completion events** - Record milestone achievements in notes

This is the **completion guardian** - ensures accurate progress tracking and prevents premature closure.

---

## When to Apply

This directive applies when:
- **Task items all completed** - All items in a task are marked complete
- **Subtasks all completed** - All subtasks of a task are done
- **Milestone evaluation** - Check if milestone should be marked complete
- **Roadmap review** - User requests status or completion check
- **Called by other directives**:
  - `project_task_update` - Checks if task should be marked complete after item/subtask completion
  - `aifp_status` - Includes completion metrics in status report
  - `project_evolution` - Checks completion alignment during pivots
  - User directly - Manual completion verification

---

## Workflow

### Trunk: check_progress

Evaluates completion status at various levels (items → subtasks → tasks → milestones → stages).

**Steps**:
1. **Identify check level** - What entity to evaluate (task, milestone, stage)
2. **Query child entities** - Get all child tasks/items/subtasks
3. **Calculate completion percentage** - Count completed vs total
4. **Check completion criteria** - All children must be complete
5. **Mark complete if criteria met** - Update status and timestamps
6. **Check parent completion** - Cascade check up the hierarchy

### Branches

**Branch 1: If check_task_completion**
- **Then**: `evaluate_task_items_and_subtasks`
- **Details**: Check if all task dependencies are complete
  - Query all items for this task
  - Query all subtasks for this task
  - Check: All items status = 'completed'
  - Check: All subtasks status = 'completed'
  - If all complete: Mark task as 'completed'
  - Trigger milestone completion check
- **SQL**:
  ```sql
  -- Check items
  SELECT COUNT(*) as total,
         SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
  FROM items WHERE task_id = ?;

  -- Check subtasks
  SELECT COUNT(*) as total,
         SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
  FROM subtasks WHERE task_id = ?;

  -- If all complete, mark task done
  UPDATE tasks
  SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
  WHERE id = ? AND status != 'completed';
  ```
- **Result**: Task marked complete, parent milestone checked

**Branch 2: If check_milestone_completion**
- **Then**: `evaluate_milestone_tasks`
- **Details**: Check if all tasks in milestone are complete
  - Query all tasks for this milestone
  - Check: All tasks status = 'completed'
  - If all complete: Mark milestone as 'completed'
  - Trigger completion_path stage check
- **SQL**:
  ```sql
  -- Check all tasks in milestone
  SELECT COUNT(*) as total,
         SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
  FROM tasks WHERE milestone_id = ?;

  -- If all complete, mark milestone done
  UPDATE milestones
  SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
  WHERE id = ? AND status != 'completed';
  ```
- **Result**: Milestone marked complete, stage checked

**Branch 3: If check_stage_completion**
- **Then**: `evaluate_stage_milestones`
- **Details**: Check if all milestones in completion path stage are complete
  - Query all milestones for this stage
  - Check: All milestones status = 'completed'
  - If all complete: Mark stage as 'completed'
  - Check if project completion path is fully complete
- **SQL**:
  ```sql
  -- Check all milestones in stage
  SELECT COUNT(*) as total,
         SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
  FROM milestones WHERE completion_path_id = ?;

  -- If all complete, mark stage done
  UPDATE completion_path
  SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
  WHERE id = ? AND status != 'completed';
  ```
- **Result**: Stage marked complete, project completion evaluated

**Branch 4: If criteria_met**
- **Then**: `mark_done`
- **Details**: Entity meets completion criteria
  - Update status to 'completed'
  - Set completed_at timestamp
  - Update parent entity
  - Log completion in notes
- **SQL**:
  ```sql
  UPDATE {table}
  SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
  WHERE id = ?;

  -- Log completion
  INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
  VALUES (?, 'completion', ?, ?, 'directive', 'project_completion_check');
  ```
- **Result**: Entity marked complete, logged

**Branch 5: If criteria_not_met**
- **Then**: `report_incomplete_dependencies`
- **Details**: Cannot mark complete, show what's missing
  - List incomplete items/subtasks/tasks
  - Show completion percentage
  - Suggest next actions
- **Result**: User informed of remaining work

**Branch 6: If drift_detected**
- **Then**: `alert_user`
- **Details**: Work doesn't align with roadmap
  - Detect: Tasks completed but not in milestone
  - Detect: Work proceeding on wrong milestone
  - Detect: Completion path out of order
  - Prompt user to realign or update roadmap
- **Log**:
  ```sql
  INSERT INTO notes (content, note_type, source, directive_name, severity)
  VALUES ('Roadmap drift detected: [details]', 'drift', 'directive', 'project_completion_check', 'warning');
  ```
- **Result**: User alerted to alignment issue

**Branch 7: If all_stages_complete**
- **Then**: `mark_project_complete`
- **Details**: All completion path stages are done
  - Update project status to 'completed'
  - Set project completed_at timestamp
  - Log project completion
  - Suggest archiving (call project_archive)
- **SQL**:
  ```sql
  -- Check all stages
  SELECT COUNT(*) as total,
         SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
  FROM completion_path WHERE project_id = ?;

  -- If all complete, mark project done
  UPDATE project
  SET status = 'completed', completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
  WHERE id = ? AND status != 'completed';
  ```
- **Result**: Project marked complete, archival suggested

**Branch 8: If incomplete_tasks_found**
- **Then**: `calculate_completion_percentage`
- **Details**: Show progress metrics
  - Calculate: (completed / total) * 100
  - Show by level: items, tasks, milestones, stages
  - Estimate remaining work
- **Result**: Progress metrics reported

**Fallback**: `prompt_user`
- Present completion status and ask for clarification
- Common issues: Ambiguous completion criteria, manual override needed

### Error Handling

**on_failure**: `rollback_and_prompt`
- If completion marking fails: Rollback status change
- Prompt user with specific error
- Common issues: Database constraint violation, orphaned records

---

## Examples

### Example 1: Task Completion - All Items Done

**Context**: Task "Implement authentication" has 5 items, all completed

**AI Execution**:
1. Checks task_id=15 for completion
2. Queries items:
   ```sql
   SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
   FROM items WHERE task_id = 15;
   -- Result: total=5, completed=5
   ```
3. Queries subtasks:
   ```sql
   SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
   FROM subtasks WHERE task_id = 15;
   -- Result: total=0, completed=0 (no subtasks)
   ```
4. All items complete, no subtasks: Mark task complete
   ```sql
   UPDATE tasks
   SET status = 'completed', completed_at = CURRENT_TIMESTAMP
   WHERE id = 15;
   ```
5. Logs completion:
   ```sql
   INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
   VALUES ('Task completed: Implement authentication (5/5 items)', 'completion', 'tasks', 15, 'directive', 'project_completion_check');
   ```
6. Checks parent milestone (milestone_id=3) for completion

### Example 2: Milestone Completion - All Tasks Done

**Context**: Milestone "Core Authentication" has 3 tasks, all completed

**AI Execution**:
1. Triggered by task completion check (from Example 1)
2. Queries all tasks in milestone_id=3:
   ```sql
   SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
   FROM tasks WHERE milestone_id = 3;
   -- Result: total=3, completed=3
   ```
3. All tasks complete: Mark milestone complete
   ```sql
   UPDATE milestones
   SET status = 'completed', completed_at = CURRENT_TIMESTAMP
   WHERE id = 3;
   ```
4. Logs:
   ```
   Milestone completed: Core Authentication (3/3 tasks)
   ```
5. Checks parent completion_path stage for completion

### Example 3: Criteria Not Met - Incomplete Subtasks

**Context**: Task has 4 items completed but 1 subtask still in progress

**AI Execution**:
1. Checks task_id=20
2. Queries items: total=4, completed=4 ✓
3. Queries subtasks: total=1, completed=0 ✗
4. Criteria not met: Cannot mark complete
5. Reports to user:
   ```
   Task "Refactor database layer" cannot be marked complete:
   - Items: 4/4 (100%) ✓
   - Subtasks: 0/1 (0%) ✗
     - Subtask #8: "Fix connection pool bug" (in_progress)

   Complete the subtask before marking task done.
   ```
6. Does not update task status

### Example 4: Roadmap Drift Detection

**Context**: User working on tasks outside current milestone

**AI Execution**:
1. Checks current focus: Milestone "Core Features" (order_index=2)
2. Queries recently completed tasks:
   - Task "Deploy to production" (milestone "Deployment", order_index=5)
3. Detects drift: Working on milestone 5 while milestone 2 not complete
4. Alerts user:
   ```
   ⚠️ Roadmap drift detected

   Current milestone: "Core Features" (Stage 2) - 40% complete
   Recently completed: "Deploy to production" (Stage 5)

   You're working ahead of the roadmap. This may indicate:
   1. Milestone order needs adjustment
   2. Work is proceeding out of sequence
   3. Roadmap needs updating

   Options:
   1. Continue (accept drift)
   2. Realign work to current milestone
   3. Update roadmap structure
   ```
5. Logs drift warning:
   ```sql
   INSERT INTO notes (content, note_type, source, directive_name, severity)
   VALUES ('Roadmap drift: Working on Stage 5 while Stage 2 incomplete', 'drift', 'directive', 'project_completion_check', 'warning');
   ```

### Example 5: Project Completion

**Context**: All completion path stages are complete

**AI Execution**:
1. Final stage "Finalization" marked complete (triggered by milestone completion)
2. Checks all stages:
   ```sql
   SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
   FROM completion_path WHERE project_id = 1;
   -- Result: total=5, completed=5
   ```
3. All stages complete: Mark project complete
   ```sql
   UPDATE project
   SET status = 'completed', completed_at = CURRENT_TIMESTAMP
   WHERE id = 1;
   ```
4. Logs project completion:
   ```sql
   INSERT INTO notes (content, note_type, source, directive_name, severity)
   VALUES ('Project completed: All 5 stages complete', 'completion', 'directive', 'project_completion_check', 'info');
   ```
5. Suggests archiving:
   ```
   ✓ Project Complete!

   All completion path stages finished.

   Suggested next step: Archive project
   Run project_archive to package deliverables.
   ```

### Example 6: Completion Percentage Calculation

**Context**: User requests progress report

**AI Execution**:
1. Queries completion at all levels:
   ```sql
   -- Items
   SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
   FROM items WHERE task_id IN (SELECT id FROM tasks WHERE milestone_id IN (SELECT id FROM milestones WHERE completion_path_id IN (SELECT id FROM completion_path WHERE project_id = 1)));

   -- Tasks
   SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
   FROM tasks WHERE milestone_id IN (SELECT id FROM milestones WHERE completion_path_id IN (SELECT id FROM completion_path WHERE project_id = 1));

   -- Milestones
   SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
   FROM milestones WHERE completion_path_id IN (SELECT id FROM completion_path WHERE project_id = 1);

   -- Stages
   SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
   FROM completion_path WHERE project_id = 1;
   ```
2. Results:
   - Items: 42/65 (65%)
   - Tasks: 8/15 (53%)
   - Milestones: 2/5 (40%)
   - Stages: 1/3 (33%)
3. Reports:
   ```
   Project Completion Status
   ═════════════════════════

   Stages:     1/3  (33%)  [Setup] [Core Development] [Finalization]
   Milestones: 2/5  (40%)
   Tasks:      8/15 (53%)
   Items:      42/65 (65%)

   Overall Progress: 48% (weighted average)

   Current Focus: Stage 2 "Core Development"
   ```

---

## Integration with Other Directives

### Called By:
- `project_task_update` - Checks completion after status changes
- `aifp_status` - Includes completion metrics
- `project_evolution` - Validates completion during pivots
- User directly - Manual completion verification

### Calls:
- `project_archive` - Suggests archiving when project complete
- `project_evolution` - May trigger evolution if completion path changes
- Logging functions - Records completion events

---

## Database Updates

### Tables Modified:

**project.db**:
```sql
-- Mark task complete
UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Mark milestone complete
UPDATE milestones SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Mark stage complete
UPDATE completion_path SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Mark project complete
UPDATE project SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?;

-- Log completion
INSERT INTO notes (content, note_type, reference_table, reference_id, source, directive_name)
VALUES (?, 'completion', ?, ?, 'directive', 'project_completion_check');

-- Log drift warning
INSERT INTO notes (content, note_type, source, directive_name, severity)
VALUES (?, 'drift', 'directive', 'project_completion_check', 'warning');
```

---

## Roadblocks and Resolutions

### Roadblock 1: roadmap_drift
**Issue**: Work proceeding out of sequence with completion path
**Resolution**: Prompt user to realign completion_path or accept drift, log warning

### Roadblock 2: incomplete_tasks
**Issue**: Cannot mark milestone complete due to pending tasks
**Resolution**: Report remaining tasks, suggest completing them or marking as cancelled

### Roadblock 3: orphaned_items
**Issue**: Items exist without parent task
**Resolution**: Link items to correct task or create parent task

### Roadblock 4: premature_completion_attempt
**Issue**: User tries to mark entity complete when dependencies remain
**Resolution**: Block completion, show remaining dependencies clearly

---

## Intent Keywords

- "progress"
- "check completion"
- "roadmap"
- "is task done"
- "mark complete"
- "completion status"

**Confidence Threshold**: 0.6

---

## Related Directives

- `project_milestone_complete` - Parent directive, handles milestone completion workflow
- `project_task_update` - Updates task status, triggers completion check
- `project_metrics` - Calculates completion percentages and progress metrics
- `project_archive` - Archives completed projects
- `project_evolution` - Handles roadmap changes that affect completion path

---

## Completion Hierarchy

```
Project (100% = all stages complete)
  └── Completion Path Stages (100% = all milestones complete)
      └── Milestones (100% = all tasks complete)
          └── Tasks (100% = all items AND subtasks complete)
              ├── Items (atomic work units)
              └── Subtasks (blocking dependencies)
```

**Completion Rules**:
- **Task**: Complete when all items complete AND all subtasks complete
- **Milestone**: Complete when all tasks complete
- **Stage**: Complete when all milestones complete
- **Project**: Complete when all stages complete

---

## Completion Metrics

### Progress Calculation

**Weighted Average**:
```
Progress = (Items% * 0.4) + (Tasks% * 0.3) + (Milestones% * 0.2) + (Stages% * 0.1)
```

**Rationale**: Items are most granular and best represent actual work done.

### Drift Detection

**Drift Indicators**:
- Working on milestone with higher order_index while lower incomplete
- Tasks completed outside any milestone
- Large gap between item completion rate and task completion rate

---

## Notes

- **Cascade checking** - Completion check propagates up the hierarchy
- **Block premature completion** - Ensure all dependencies met
- **Detect drift** - Alert when work doesn't align with roadmap
- **Log all completions** - Audit trail for project progress
- **Calculate metrics** - Provide completion percentages at all levels
- **Auto-complete parent tasks** - Mark tasks done when all children complete
- **Respect completion criteria** - Both items AND subtasks must be complete
- **Support manual override** - Allow user to mark complete with warning
