# Directive: project_performance_summary

**Type**: Project
**Level**: 4 (State Management)
**Parent Directive**: project_metrics
**Priority**: LOW - Directive audit and reliability tracking

---

## Purpose

The `project_performance_summary` directive summarizes recent directive outcomes, including successes, retries, and failures, and stores summaries in notes for audit. This directive serves as the **directive reliability monitor**, keeping a rolling summary of directive performance for reliability tracking and system health.

Key responsibilities:
- **Summarize directive outcomes** - Track success/failure rates
- **Analyze failure patterns** - Identify common errors
- **Track retry behavior** - Monitor retry attempts and outcomes
- **Generate audit reports** - Periodic performance summaries
- **Detect reliability trends** - Track improvement or degradation
- **Log transparently** - Record in notes for accountability

This is the **directive auditor** - ensures directive system reliability and transparency.

---

## When to Apply

This directive applies when:
- **Periodic audit** - Scheduled performance review (daily, weekly)
- **After directive failures** - Analyze patterns when errors occur
- **System health check** - Verify directive system functioning properly
- **Performance review** - User requests directive statistics
- **Called by other directives**:
  - `project_metrics` - Includes directive performance in metrics
  - `project_error_handling` - Uses performance data to identify problematic directives
  - `aifp_status` - May include directive health in status reports
  - User directly - Manual audit request

---

## Workflow

### Trunk: summarize_recent_runs

Analyzes recent directive execution logs from the notes table.

**Steps**:
1. **Define time window** - Last 7 days by default (configurable)
2. **Query execution logs** - Extract directive execution records from notes
3. **Classify outcomes** - Success, failure, warning, retry
4. **Calculate statistics** - Success rates, failure counts, retry patterns
5. **Identify patterns** - Common errors, problematic directives
6. **Generate summary** - Format human-readable report
7. **Log summary** - Store in notes for historical tracking

### Branches

**Branch 1: If error_logs_present**
- **Then**: `analyze_failures`
- **Details**: Deep dive into failure patterns
  - Group errors by directive
  - Extract error messages and patterns
  - Identify most common failures
  - Calculate failure impact (blocking vs non-blocking)
  - Suggest resolutions or improvements
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Failure analysis with common patterns identified

**Branch 2: If recent_successes**
- **Then**: `record_success_rate`
- **Details**: Calculate and track success rates
  - Count successful executions per directive
  - Calculate success percentage
  - Compare to historical baseline
  - Identify improving/degrading directives
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Success rates calculated, ranked by reliability

**Branch 3: If retry_pattern_analysis**
- **Then**: `analyze_retry_behavior`
- **Details**: Track retry attempts and outcomes
  - Identify directives requiring multiple retries
  - Calculate average retries per directive
  - Determine retry success rates
  - Flag directives with excessive retries
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Retry patterns analyzed, excessive retry directives flagged

**Branch 4: If historical_comparison**
- **Then**: `compare_to_baseline`
- **Details**: Compare current performance to historical average
  - Query performance from previous period (7-14 days ago)
  - Calculate delta in success rates
  - Identify improving directives (↗) and degrading directives (↘)
  - Flag significant changes (>10% delta)
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Historical comparison with trends identified

**Branch 5: If top_performers_analysis**
- **Then**: `identify_top_performers`
- **Details**: Highlight most reliable directives
  - Rank directives by success rate
  - Consider execution volume (min threshold)
  - List top 5 most reliable directives
  - Provide positive reinforcement
- **Result**: Top performers identified and celebrated

**Branch 6: If problematic_directives_flagged**
- **Then**: `flag_for_review`
- **Details**: Identify directives needing attention
  - Success rate < 80%
  - Excessive retries (>3 average per execution)
  - Frequent failures (>5 in period)
  - Recent degradation (>10% drop)
  - Suggest investigating directive .md files
- **Result**: Problem directives flagged with recommendations

**Branch 7: If generate_audit_report**
- **Then**: `format_performance_summary`
- **Details**: Create comprehensive performance report
  - Executive summary (overall health)
  - Top performers (most reliable)
  - Problem areas (needs attention)
  - Retry analysis (excessive retries)
  - Historical trends (improving/degrading)
  - Recommendations (specific actions)
- **Report Format**:
  ```
  Directive Performance Summary
  ═════════════════════════════

  Period: Last 7 days (Oct 20-27)

  ## Executive Summary

  Overall Health: 92% average success rate ✓
  Total Executions: 284 across 23 directives
  Failures: 18 (6%)
  Warnings: 5 (2%)

  Status: Healthy (>90% success rate)

  ## Top Performers (Success Rate > 95%)

  1. project_file_write:    100% (42/42)  🏆
  2. project_task_update:    98% (58/59)
  3. project_task_create:    97% (35/36)
  4. project_blueprint_read: 96% (24/25)
  5. aifp_status:            95% (20/21)

  ## Needs Attention (Success Rate < 85%)

  1. fp_compliance_check:     76% (19/25)  ⚠️
     - Common Error: "Cannot parse function signature"
     - Retry Rate: 24% (6 retries)
     - Recommendation: Review parsing logic in fp_compliance_check.md

  2. project_dependency_sync: 82% (18/22)  ⚠️
     - Common Error: "Unresolved dependency"
     - Retry Rate: 18% (4 retries)
     - Recommendation: Improve dependency resolution algorithm

  ## Retry Analysis

  Directives with >3 retries:
  - fp_compliance_check: 6 retries (3 successful, 3 exhausted)
  - project_dependency_sync: 4 retries (4 successful)

  Average retries per execution: 0.8

  ## Historical Trends

  Improving (↗):
  - project_file_write: 95% → 100% (+5%)
  - project_task_update: 92% → 98% (+6%)

  Degrading (↘):
  - fp_compliance_check: 88% → 76% (-12%)  ⚠️ ALERT

  Stable (→):
  - Most directives within ±5%

  ## Recommendations

  1. HIGH: Investigate fp_compliance_check parsing failures
     - Action: Review recent code changes
     - Expected Impact: +15% success rate

  2. MEDIUM: Optimize project_dependency_sync resolution logic
     - Action: Add better error messages for common cases
     - Expected Impact: +10% success rate, reduce retries

  3. LOW: Continue monitoring project_file_write consistency
     - Action: Maintain current implementation
     - Note: Perfect track record
  ```
- **Result**: Comprehensive audit report generated

**Branch 8: If write_summary_to_notes**
- **Then**: `log_performance_snapshot`
- **Details**: Store summary in notes for historical tracking
  - Record key metrics (overall success rate, top/bottom performers)
  - Enable trend analysis over multiple periods
  - Support long-term reliability tracking
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Performance snapshot logged

**Fallback**: `write_summary_to_notes`
- Log basic summary even if detailed analysis fails
- Ensure audit trail maintained

### Error Handling

**on_failure**: `prompt_user`
- If summary generation fails: Log error, report issue
- Common issues: Notes table empty, query errors, date calculation issues

---

## Examples

### Example 1: Weekly Performance Report

**Context**: Scheduled weekly audit

**AI Execution**:
1. Queries last 7 days of directive executions:
   - Total: 284 executions across 23 directives
   - Successes: 261 (92%)
   - Failures: 18 (6%)
   - Warnings: 5 (2%)
2. Calculates per-directive success rates
3. Identifies top performers:
   - project_file_write: 100%
   - project_task_update: 98%
4. Identifies problem directives:
   - fp_compliance_check: 76%
   - project_dependency_sync: 82%
5. Analyzes trends:
   - fp_compliance_check degraded from 88% → 76%
6. Generates comprehensive report (see Branch 7 example)
7. Logs summary to notes

### Example 2: Failure Pattern Analysis

**Context**: Multiple fp_compliance_check failures detected

**AI Execution**:
1. Queries failures for fp_compliance_check:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
2. Results:
   - "Cannot parse function signature: missing return type" (6 occurrences)
   - "Type annotation required but missing" (2 occurrences)
   - "Syntax error in parameter list" (1 occurrence)
3. Identifies pattern: Most failures are parsing-related
4. Calculates impact:
   - 9 total failures out of 25 executions = 36% failure rate
   - 6 retries triggered, 3 successful
5. Reports:
   ```
   fp_compliance_check Failure Analysis
   ════════════════════════════════════

   Failure Rate: 36% (9/25 executions)

   Common Errors:
   1. "Cannot parse function signature" - 6 occurrences (67%)
      - Cause: Missing return type annotations
      - Resolution: Improve parser to handle optional returns

   2. "Type annotation required" - 2 occurrences (22%)
      - Cause: Dynamic type inference not supported
      - Resolution: Require explicit types

   3. "Syntax error in parameter list" - 1 occurrence (11%)
      - Cause: Complex parameter patterns
      - Resolution: Enhance pattern matching

   Recommendation: Review fp_compliance_check.md parsing logic
   Expected Impact: +20% success rate
   ```

### Example 3: Retry Behavior Analysis

**Context**: Identify directives requiring excessive retries

**AI Execution**:
1. Queries retry patterns:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
2. Analyzes results:
   - fp_compliance_check: 6 retries (3 successful, 3 exhausted)
   - project_dependency_sync: 4 retries (all successful)
   - project_file_write: 1 retry (successful)
3. Calculates retry rates:
   - fp_compliance_check: 24% of executions require retry
   - project_dependency_sync: 18% require retry
4. Reports:
   ```
   Retry Behavior Analysis
   ═══════════════════════

   Directives with Excessive Retries (>3):

   1. fp_compliance_check: 6 retries
      - Success after retry: 50% (3/6)
      - Issue: Parsing failures often persist
      - Recommendation: Fix root cause, don't rely on retries

   2. project_dependency_sync: 4 retries
      - Success after retry: 100% (4/4)
      - Issue: Transient database locks
      - Status: Acceptable (retry strategy working)

   Overall: 0.8 retries per execution (acceptable threshold: <1.0)
   ```

### Example 4: Historical Trend Detection

**Context**: Compare current to previous week

**AI Execution**:
1. Calculates current week success rates (see Example 1)
2. Calculates previous week (8-14 days ago):
   - fp_compliance_check: 88%
   - project_file_write: 95%
3. Compares:
   - fp_compliance_check: 88% → 76% = -12% (DEGRADING ↘)
   - project_file_write: 95% → 100% = +5% (IMPROVING ↗)
4. Flags significant change:
   - fp_compliance_check dropped >10%, requires investigation
5. Reports:
   ```
   Historical Trend Alert
   ══════════════════════

   ⚠️ Significant Degradation Detected

   Directive: fp_compliance_check
   Current Period: 76% (Oct 20-27)
   Previous Period: 88% (Oct 13-20)
   Delta: -12% ↘

   This represents a significant performance drop.

   Possible Causes:
   - Recent code changes to compliance logic
   - Increased complexity in parsed code
   - New edge cases not handled

   Recommendation: Urgent review of recent changes
   ```

### Example 5: Top Performers Report

**Context**: Highlight most reliable directives

**AI Execution**:
1. Queries all directives with >10 executions
2. Ranks by success rate:
   - project_file_write: 100% (42/42)
   - project_task_update: 98% (58/59)
   - project_task_create: 97% (35/36)
3. Reports:
   ```
   Top Performing Directives 🏆
   ═══════════════════════════

   1. project_file_write: 100% (42/42)
      - Perfect record this period
      - 0 failures, 0 retries
      - Consistent execution

   2. project_task_update: 98% (58/59)
      - 1 minor failure (database lock, resolved on retry)
      - High volume, excellent reliability

   3. project_task_create: 97% (35/36)
      - 1 failure (user cancellation, expected)
      - Robust task creation logic

   These directives demonstrate excellent stability.
   Continue current implementation.
   ```

---

## Integration with Other Directives

### Called By:
- `project_metrics` - Includes directive performance in metrics
- `project_error_handling` - Uses performance data to identify issues
- `aifp_status` - May include directive health
- User directly - Manual audit request

### Calls:
- Logging functions - Records performance snapshots
- Database queries - Extracts execution logs from notes

---

## Database Updates

### Tables Modified:

**project.db**:
**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Tables Queried:

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Roadblocks and Resolutions

### Roadblock 1: missing_logs
**Issue**: Notes table empty or insufficient data
**Resolution**: Query notes table for directive references, return "Insufficient data" if < 10 executions

### Roadblock 2: date_calculation_error
**Issue**: Incorrect time window for queries
**Resolution**: Validate date parameters, default to 7 days if invalid

### Roadblock 3: ambiguous_success_classification
**Issue**: Unclear if note represents success or failure
**Resolution**: Use explicit note_type values (success, error, failure, info)

---

## Intent Keywords

- "summary"
- "audit"
- "performance"
- "directive reliability"
- "execution logs"
- "failure analysis"

**Confidence Threshold**: 0.6

---

## Related Directives

- `project_metrics` - Parent directive, includes performance in overall metrics
- `project_error_handling` - Uses performance data to identify problematic directives
- `aifp_status` - May include directive health in status reports
- `project_notes_log` - Logs that this directive analyzes

---

## Performance Thresholds

### Success Rate Thresholds
- **Excellent**: >95% - No action needed
- **Good**: 90-95% - Monitor
- **Fair**: 80-90% - Review recommended
- **Poor**: <80% - Urgent investigation

### Retry Thresholds
- **Acceptable**: <1.0 retries per execution
- **Warning**: 1.0-2.0 retries per execution
- **Excessive**: >2.0 retries per execution

### Trend Thresholds
- **Significant Improvement**: >10% increase
- **Stable**: ±5% change
- **Significant Degradation**: >10% decrease

---

## Audit Frequency

### Recommended Schedule
- **Daily**: Automated summary for critical systems
- **Weekly**: Standard audit frequency (default)
- **Monthly**: Long-term trend analysis

### Trigger-Based Audits
- After >5 failures in 1 hour
- When success rate drops below 85%
- When retry rate exceeds 2.0

---

## Notes

- **Query notes table** - Source of truth for directive execution logs
- **Log performance snapshots** - Enable historical trend analysis
- **Identify patterns** - Common errors, failure clusters
- **Track reliability** - Success rates, retry behavior
- **Compare to baseline** - Detect degradation early
- **Celebrate success** - Highlight top performers
- **Flag problems** - Alert on poor performance (<80%)
- **Actionable recommendations** - Specific next steps for improvement
- **Transparent audit** - All summaries logged in notes
