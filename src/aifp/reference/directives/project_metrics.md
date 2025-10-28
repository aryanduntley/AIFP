# Directive: project_metrics

**Type**: Project
**Level**: 4 (State Management)
**Parent Directive**: project_completion_check
**Priority**: LOW - Quantitative progress tracking

---

## Purpose

The `project_metrics` directive calculates project completion percentage, directive success rates, and task distribution to inform AI reasoning and user summaries. This directive serves as the **metrics calculator**, providing periodic project health reports for both AI and user reference.

Key responsibilities:
- **Calculate completion percentages** - Track progress at all levels
- **Track directive success rates** - Monitor directive reliability
- **Measure task distribution** - Analyze work allocation across milestones
- **Generate health reports** - Periodic project status summaries
- **Identify bottlenecks** - Detect stuck tasks or overloaded milestones
- **Log metrics transparently** - Record in notes for audit trail

This is the **project analyst** - quantifies project health and progress trends.

---

## When to Apply

This directive applies when:
- **Status request** - User asks for progress or metrics
- **Periodic reporting** - Scheduled health check intervals
- **Completion evaluation** - After major milestone completions
- **Performance review** - Analyzing directive effectiveness
- **Called by other directives**:
  - `aifp_status` - Includes metrics in status report
  - `project_completion_check` - Uses metrics for completion evaluation
  - `project_auto_summary` - Incorporates metrics in summaries
  - User directly - Manual metrics request

---

## Workflow

### Trunk: gather_metrics

Collects quantitative data across project dimensions.

**Steps**:
1. **Identify metrics scope** - What metrics to calculate (completion, success rates, distribution)
2. **Query project database** - Gather raw data from tables
3. **Calculate metrics** - Compute percentages, averages, trends
4. **Analyze patterns** - Identify bottlenecks, success trends
5. **Format report** - Structure metrics for readability
6. **Log to notes** - Record metrics for historical tracking

### Branches

**Branch 1: If completion_path_available**
- **Then**: `compute_progress`
- **Details**: Calculate completion percentages at all levels
  - Query completion_path stages with completion counts
  - Query milestones with task counts
  - Query tasks with item/subtask counts
  - Calculate weighted progress score
  - Identify current focus (highest priority incomplete)
- **SQL**:
  ```sql
  -- Stage completion
  SELECT
    cp.name,
    cp.order_index,
    COUNT(m.id) as total_milestones,
    SUM(CASE WHEN m.status = 'completed' THEN 1 ELSE 0 END) as completed_milestones,
    ROUND(100.0 * SUM(CASE WHEN m.status = 'completed' THEN 1 ELSE 0 END) / COUNT(m.id), 2) as completion_pct
  FROM completion_path cp
  LEFT JOIN milestones m ON cp.id = m.completion_path_id
  WHERE cp.project_id = ?
  GROUP BY cp.id
  ORDER BY cp.order_index;

  -- Task completion
  SELECT
    m.name as milestone,
    COUNT(t.id) as total_tasks,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
    ROUND(100.0 * SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) / COUNT(t.id), 2) as completion_pct
  FROM milestones m
  LEFT JOIN tasks t ON m.id = t.milestone_id
  WHERE m.completion_path_id IN (SELECT id FROM completion_path WHERE project_id = ?)
  GROUP BY m.id;

  -- Item completion
  SELECT
    COUNT(*) as total_items,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_items,
    ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as completion_pct
  FROM items
  WHERE task_id IN (
    SELECT t.id FROM tasks t
    JOIN milestones m ON t.milestone_id = m.id
    WHERE m.completion_path_id IN (SELECT id FROM completion_path WHERE project_id = ?)
  );
  ```
- **Result**: Completion metrics calculated, current focus identified

**Branch 2: If function_table_updated**
- **Then**: `calculate_compliance_score`
- **Details**: Track FP compliance across functions
  - Count functions by purity level
  - Calculate average purity score
  - Identify non-compliant functions
  - Track improvement trends
- **SQL**:
  ```sql
  -- Purity distribution
  SELECT
    purity_level,
    COUNT(*) as function_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM functions WHERE project_id = ?), 2) as percentage
  FROM functions
  WHERE project_id = ?
  GROUP BY purity_level;

  -- Compliance score (pure functions / total functions)
  SELECT
    ROUND(100.0 * SUM(CASE WHEN purity_level = 'pure' THEN 1 ELSE 0 END) / COUNT(*), 2) as compliance_score
  FROM functions
  WHERE project_id = ?;

  -- Non-compliant functions needing refactoring
  SELECT name, file_id, purity_level, side_effects_json
  FROM functions
  WHERE project_id = ? AND purity_level != 'pure'
  ORDER BY purity_level DESC;
  ```
- **Result**: FP compliance metrics calculated

**Branch 3: If task_distribution_requested**
- **Then**: `analyze_task_distribution`
- **Details**: Examine work allocation across milestones
  - Count tasks per milestone
  - Identify overloaded milestones (>10 tasks)
  - Detect empty milestones (0 tasks)
  - Calculate average tasks per milestone
- **SQL**:
  ```sql
  SELECT
    m.name as milestone,
    cp.name as stage,
    COUNT(t.id) as task_count,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN t.status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
    SUM(CASE WHEN t.status = 'pending' THEN 1 ELSE 0 END) as pending,
    CASE
      WHEN COUNT(t.id) = 0 THEN 'Empty'
      WHEN COUNT(t.id) > 10 THEN 'Overloaded'
      ELSE 'Balanced'
    END as load_status
  FROM milestones m
  JOIN completion_path cp ON m.completion_path_id = cp.id
  LEFT JOIN tasks t ON m.id = t.milestone_id
  WHERE cp.project_id = ?
  GROUP BY m.id
  ORDER BY cp.order_index, m.priority;
  ```
- **Result**: Task distribution analyzed, imbalances flagged

**Branch 4: If directive_success_tracking**
- **Then**: `calculate_directive_success_rates`
- **Details**: Track directive execution reliability
  - Query notes table for directive executions
  - Count successes vs failures
  - Calculate success rate per directive
  - Identify problematic directives (< 80% success)
- **SQL**:
  ```sql
  -- Directive success rates
  SELECT
    directive_name,
    COUNT(*) as total_executions,
    SUM(CASE WHEN note_type IN ('error', 'failure') THEN 1 ELSE 0 END) as failures,
    SUM(CASE WHEN note_type IN ('success', 'completion', 'info') THEN 1 ELSE 0 END) as successes,
    ROUND(100.0 * SUM(CASE WHEN note_type IN ('success', 'completion', 'info') THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
  FROM notes
  WHERE source = 'directive' AND created_at > datetime('now', '-7 days')
  GROUP BY directive_name
  ORDER BY success_rate ASC;
  ```
- **Result**: Directive reliability metrics calculated

**Branch 5: If velocity_tracking**
- **Then**: `calculate_completion_velocity`
- **Details**: Track work completion rate over time
  - Calculate items completed per day/week
  - Estimate remaining time to milestone completion
  - Identify acceleration or deceleration trends
- **SQL**:
  ```sql
  -- Completions per day (last 7 days)
  SELECT
    DATE(completed_at) as date,
    COUNT(*) as items_completed
  FROM items
  WHERE completed_at > datetime('now', '-7 days') AND status = 'completed'
  GROUP BY DATE(completed_at)
  ORDER BY date;

  -- Average velocity
  SELECT
    ROUND(COUNT(*) / 7.0, 2) as avg_items_per_day
  FROM items
  WHERE completed_at > datetime('now', '-7 days') AND status = 'completed';

  -- Estimated days to milestone completion
  SELECT
    m.name,
    COUNT(i.id) as remaining_items,
    ROUND(COUNT(i.id) / (
      SELECT COUNT(*) / 7.0
      FROM items
      WHERE completed_at > datetime('now', '-7 days') AND status = 'completed'
    ), 1) as estimated_days
  FROM milestones m
  JOIN tasks t ON m.id = t.milestone_id
  JOIN items i ON t.id = i.task_id
  WHERE i.status != 'completed' AND m.status != 'completed'
  GROUP BY m.id;
  ```
- **Result**: Velocity metrics calculated, estimates provided

**Branch 6: If bottleneck_detection**
- **Then**: `identify_stuck_tasks`
- **Details**: Find tasks with no recent progress
  - Query tasks updated > 7 days ago with status in_progress
  - Identify subtasks blocking parent tasks
  - Flag sidequests that may be abandoned
- **SQL**:
  ```sql
  -- Stale in-progress tasks
  SELECT
    t.name,
    t.status,
    m.name as milestone,
    t.updated_at,
    ROUND(julianday('now') - julianday(t.updated_at), 1) as days_stale,
    COUNT(i.id) as total_items,
    SUM(CASE WHEN i.status = 'completed' THEN 1 ELSE 0 END) as completed_items
  FROM tasks t
  JOIN milestones m ON t.milestone_id = m.id
  LEFT JOIN items i ON t.id = i.task_id
  WHERE t.status = 'in_progress' AND t.updated_at < datetime('now', '-7 days')
  GROUP BY t.id
  ORDER BY days_stale DESC;

  -- Blocking subtasks
  SELECT
    st.name as subtask,
    t.name as parent_task,
    st.status,
    st.priority,
    st.updated_at
  FROM subtasks st
  JOIN tasks t ON st.task_id = t.id
  WHERE st.status != 'completed' AND t.status = 'paused'
  ORDER BY st.priority DESC, st.created_at ASC;
  ```
- **Result**: Bottlenecks identified with recommendations

**Branch 7: If generate_health_report**
- **Then**: `format_metrics_report`
- **Details**: Create human-readable summary
  - Include all calculated metrics
  - Add visual indicators (progress bars, warnings)
  - Highlight key insights
  - Provide recommendations
- **Report Format**:
  ```
  Project Health Report
  ═══════════════════════

  ## Overall Progress: 62% ▓▓▓▓▓▓▒▒▒▒

  Stages:     2/4  (50%)  [✓][✓][ ][ ]
  Milestones: 5/12 (42%)
  Tasks:      15/35 (43%)
  Items:      89/120 (74%)

  ## Compliance Score: 85%

  Pure Functions: 42/50 (84%)
  Mostly Pure:    6/50 (12%)
  Impure:         2/50 (4%)

  ⚠️ 2 functions need refactoring

  ## Velocity: 8.5 items/day

  Last 7 days:  60 items completed
  Trend:        ↗ Accelerating

  Estimated milestone completion: 4.2 days

  ## Bottlenecks Detected: 2

  1. Task "Refactor database layer" (stale 12 days)
     - 3/8 items complete
     - Recommendation: Break into subtasks

  2. Subtask "Fix memory leak" (blocking parent)
     - In progress 5 days
     - Recommendation: User review needed

  ## Directive Performance: Healthy

  Average success rate: 94%
  Most reliable: project_file_write (100%)
  Needs attention: fp_compliance_check (78%)

  ## Recommendations:

  1. Address 2 stale tasks to improve flow
  2. Refactor 2 impure functions for compliance
  3. Consider breaking Milestone "Core Features" (12 tasks) into sub-milestones
  ```
- **Result**: Comprehensive health report generated

**Branch 8: If log_metrics_to_notes**
- **Then**: `record_metrics_snapshot`
- **Details**: Log current metrics for historical tracking
  - Store key metrics in notes table
  - Enable trend analysis over time
  - Support retrospectives
- **SQL**:
  ```sql
  INSERT INTO notes (content, note_type, source, directive_name, severity)
  VALUES (
    'Metrics snapshot: Overall 62%, Compliance 85%, Velocity 8.5 items/day, Bottlenecks: 2',
    'metrics',
    'directive',
    'project_metrics',
    'info'
  );
  ```
- **Result**: Metrics logged for historical analysis

**Fallback**: `log_metrics_to_notes`
- Record basic metrics even if advanced calculations fail
- Ensure some visibility into project state

### Error Handling

**on_failure**: `prompt_user`
- If metrics calculation fails: Log error, report available metrics
- Common issues: Empty database, missing tables, calculation errors

---

## Examples

### Example 1: Basic Progress Report

**Context**: User requests project progress

**AI Execution**:
1. Calculates completion at all levels
2. Queries:
   - Stages: 2/4 complete (50%)
   - Milestones: 5/12 complete (42%)
   - Tasks: 15/35 complete (43%)
   - Items: 89/120 complete (74%)
3. Calculates weighted score:
   ```
   Progress = (74% * 0.4) + (43% * 0.3) + (42% * 0.2) + (50% * 0.1)
            = 29.6 + 12.9 + 8.4 + 5.0
            = 55.9% ≈ 56%
   ```
4. Reports:
   ```
   Project Progress: 56%

   Stages:     2/4  (50%)
   Milestones: 5/12 (42%)
   Tasks:      15/35 (43%)
   Items:      89/120 (74%)

   Current Focus: Stage 3 "Feature Development"
   ```

### Example 2: FP Compliance Tracking

**Context**: After file writes, check compliance trends

**AI Execution**:
1. Queries function purity distribution:
   ```sql
   SELECT purity_level, COUNT(*) FROM functions WHERE project_id = 1 GROUP BY purity_level;
   -- Results:
   -- pure: 42
   -- mostly_pure: 6
   -- impure: 2
   ```
2. Calculates compliance score:
   ```
   Compliance = (42 / 50) * 100 = 84%
   ```
3. Identifies non-compliant:
   ```sql
   SELECT name, purity_level FROM functions WHERE purity_level != 'pure';
   -- Results:
   -- process_user_input (mostly_pure)
   -- global_config_loader (impure)
   -- legacy_auth_handler (impure)
   ```
4. Reports:
   ```
   FP Compliance: 84%

   Pure Functions: 42/50 (84%)
   ⚠️ 8 functions need attention:
     - 6 mostly_pure (minor refactoring)
     - 2 impure (requires isolation)

   Priority refactoring:
   1. global_config_loader (impure) - Isolate I/O
   2. legacy_auth_handler (impure) - Deprecated, replace
   ```

### Example 3: Velocity Calculation

**Context**: Estimate when milestone will complete

**AI Execution**:
1. Queries completions last 7 days:
   ```sql
   SELECT DATE(completed_at), COUNT(*) FROM items
   WHERE completed_at > datetime('now', '-7 days') AND status = 'completed'
   GROUP BY DATE(completed_at);
   -- Results:
   -- 2025-10-20: 12 items
   -- 2025-10-21: 8 items
   -- 2025-10-22: 10 items
   -- 2025-10-23: 9 items
   -- 2025-10-24: 7 items
   -- 2025-10-25: 8 items
   -- 2025-10-26: 6 items
   -- Total: 60 items
   ```
2. Calculates average velocity:
   ```
   Velocity = 60 items / 7 days = 8.57 items/day
   ```
3. Queries remaining items in milestone:
   ```sql
   SELECT COUNT(*) FROM items i
   JOIN tasks t ON i.task_id = t.id
   WHERE t.milestone_id = 3 AND i.status != 'completed';
   -- Result: 36 items
   ```
4. Estimates completion:
   ```
   Days to completion = 36 / 8.57 = 4.2 days
   Estimated completion: 2025-10-30
   ```
5. Reports:
   ```
   Milestone "Core Authentication" Progress

   Velocity: 8.6 items/day (last 7 days)
   Remaining: 36 items
   Estimated completion: 4.2 days (Oct 30)

   Trend: ↗ Accelerating (was 7.2 items/day last week)
   ```

### Example 4: Bottleneck Detection

**Context**: Identify stuck tasks

**AI Execution**:
1. Queries stale tasks:
   ```sql
   SELECT name, updated_at,
     ROUND(julianday('now') - julianday(updated_at), 1) as days_stale
   FROM tasks
   WHERE status = 'in_progress' AND updated_at < datetime('now', '-7 days');
   -- Results:
   -- "Refactor database layer" - 12.3 days stale
   -- "Implement caching" - 8.1 days stale
   ```
2. Analyzes task details:
   ```sql
   SELECT COUNT(*), SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
   FROM items WHERE task_id = 15;
   -- Task "Refactor database layer": 3/8 items complete (38%)
   ```
3. Identifies causes:
   - Large task (8 items) with slow progress
   - No subtasks created (should decompose)
   - Last update 12 days ago
4. Reports:
   ```
   ⚠️ 2 Bottlenecks Detected

   1. Task: "Refactor database layer" (stale 12 days)
      Progress: 3/8 items (38%)
      Issue: Large task with slow progress
      Recommendation: Break into 2-3 subtasks

   2. Task: "Implement caching" (stale 8 days)
      Progress: 0/5 items (0%)
      Issue: No progress since creation
      Recommendation: Review priority or cancel
   ```

### Example 5: Directive Success Rates

**Context**: Evaluate directive reliability

**AI Execution**:
1. Queries directive execution logs:
   ```sql
   SELECT directive_name, note_type, COUNT(*)
   FROM notes
   WHERE source = 'directive' AND created_at > datetime('now', '-7 days')
   GROUP BY directive_name, note_type;
   -- Results analyzed...
   ```
2. Calculates success rates:
   - project_file_write: 25 successes, 0 failures = 100%
   - project_task_create: 18 successes, 1 failure = 95%
   - fp_compliance_check: 14 successes, 4 failures = 78%
3. Identifies issues:
   - fp_compliance_check failing 22% of the time
   - Common error: "Cannot parse function signature"
4. Reports:
   ```
   Directive Performance (Last 7 Days)

   Most Reliable:
   - project_file_write: 100% (25/25)
   - project_task_update: 98% (42/43)
   - project_task_create: 95% (18/19)

   Needs Attention:
   - fp_compliance_check: 78% (14/18) ⚠️
     Common error: Cannot parse function signature
     Recommendation: Review parsing logic

   Average Success Rate: 94%
   ```

---

## Integration with Other Directives

### Called By:
- `aifp_status` - Includes metrics in status reports
- `project_completion_check` - Uses metrics for evaluation
- `project_auto_summary` - Incorporates in summaries
- User directly - Manual metrics request

### Calls:
- Logging functions - Records metrics snapshots
- Database queries - Extracts raw data

---

## Database Updates

### Tables Modified:

**project.db**:
```sql
-- Log metrics snapshot
INSERT INTO notes (content, note_type, source, directive_name, severity)
VALUES (?, 'metrics', 'directive', 'project_metrics', 'info');
```

### Tables Queried:

```sql
-- completion_path, milestones, tasks, items, subtasks
-- For completion percentages

-- functions
-- For FP compliance scoring

-- notes
-- For directive success rates and historical trends
```

---

## Roadblocks and Resolutions

### Roadblock 1: missing_task_data
**Issue**: Tasks or items table empty, cannot calculate metrics
**Resolution**: Requery project.db and retry, report "No data" if truly empty

### Roadblock 2: stale_metrics
**Issue**: Metrics calculated long ago, no longer accurate
**Resolution**: Recalculate from base tables, don't use cached values

### Roadblock 3: calculation_error
**Issue**: Division by zero or invalid data
**Resolution**: Handle edge cases (0 tasks, 0 items), return N/A for invalid metrics

---

## Intent Keywords

- "progress"
- "metrics"
- "statistics"
- "completion percentage"
- "velocity"
- "health report"

**Confidence Threshold**: 0.7

---

## Related Directives

- `project_completion_check` - Parent directive, uses metrics for completion evaluation
- `aifp_status` - Includes metrics in status reports
- `project_performance_summary` - Extends metrics with directive performance
- `project_auto_summary` - Uses metrics in automated summaries

---

## Metric Definitions

### Completion Percentage
- **Formula**: (Completed / Total) * 100
- **Levels**: Items, Tasks, Milestones, Stages
- **Weighted Score**: Emphasizes granular progress (items weighted 40%)

### Compliance Score
- **Formula**: (Pure Functions / Total Functions) * 100
- **Target**: > 90% for strict FP projects
- **Threshold**: < 80% triggers refactoring recommendations

### Velocity
- **Formula**: Items Completed / Time Period
- **Default Period**: 7 days (rolling window)
- **Uses**: Estimate completion dates, detect acceleration/deceleration

### Success Rate
- **Formula**: (Successful Executions / Total Executions) * 100
- **Threshold**: < 80% indicates problematic directive
- **Source**: notes table, directive execution logs

---

## Notes

- **Log metrics transparently** - Record in notes for audit trail
- **Calculate weighted progress** - Items carry more weight (40%)
- **Track directive reliability** - Identify failing directives
- **Detect bottlenecks early** - Flag stale tasks automatically
- **Estimate completion dates** - Use velocity for projections
- **Periodic reporting** - Regular health checks maintain visibility
- **Historical tracking** - Log snapshots for trend analysis
- **Visual indicators** - Use progress bars and symbols for clarity
