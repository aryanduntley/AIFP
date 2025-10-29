# Directive: user_directive_monitor

**Type**: User System
**Level**: N/A (Continuous operation)
**Parent Directive**: `user_directive_activate`
**Priority**: High

---

## Purpose

Continuously monitor active user directives, track execution statistics, handle errors, and manage log rotation. This directive runs **automatically and continuously** after directives are activated.

**Responsibilities**:
1. Track each directive execution (success/failure)
2. Log executions to file (JSON Lines format)
3. Log errors with stack traces
4. Update execution statistics in database
5. Detect and alert on error patterns
6. Rotate logs based on size/time
7. Maintain system health

**Critical**: This is a **passive monitoring** directive - it tracks what happens, it doesn't control execution.

---

## When to Apply

This directive applies **automatically**:
- Runs continuously after `user_directive_activate` completes
- Monitors all active directives simultaneously
- Triggered by directive execution events
- User can query: "directive status" / "show directive logs"

**Never explicitly called by user** - it's background infrastructure.

---

## Workflow

### Trunk: Continuous Monitoring Loop

#### Step 1: Initialize Monitoring System

1. **On first activation** (when project.user_directives_status becomes 'active'):
   ```python
   # Set up monitoring infrastructure
   monitoring_system = DirectiveMonitor()

   # Register all active directives
   active_directives = query_active_directives()
   for directive in active_directives:
       monitoring_system.register(directive)

   # Start monitoring loop
   monitoring_system.start()
   ```

2. **Set up event hooks**:
   ```python
   # Hook into directive execution events
   @on_directive_execution
   def handle_execution(directive_id, result, duration_ms):
       log_execution(directive_id, result, duration_ms)
       update_statistics(directive_id, result)

   @on_directive_error
   def handle_error(directive_id, error, stack_trace):
       log_error(directive_id, error, stack_trace)
       update_error_stats(directive_id, error)
       check_error_threshold(directive_id)
   ```

#### Step 2: Track Executions (on each execution)

1. **When directive executes successfully**:
   ```python
   # Log to execution file (JSON Lines)
   execution_log = {
       "timestamp": datetime.utcnow().isoformat(),
       "directive_id": directive_id,
       "directive_name": directive_name,
       "status": "success",
       "duration_ms": duration_ms,
       "trigger_type": trigger_type,
       "result": result_summary
   }

   append_to_log(
       ".aifp-project/logs/executions/current.log",
       json.dumps(execution_log)
   )
   ```

2. **Update database statistics**:
   ```sql
   UPDATE directive_executions
   SET total_executions = total_executions + 1,
       success_count = success_count + 1,
       last_execution_time = CURRENT_TIMESTAMP,
       last_execution_status = 'success',
       avg_execution_time_ms = (
           (avg_execution_time_ms * (total_executions - 1) + ?) / total_executions
       )
   WHERE directive_id = ?;
   ```

3. **Calculate next execution** (for time-based):
   ```sql
   UPDATE directive_executions
   SET next_scheduled_time = ?
   WHERE directive_id = ? AND trigger_type = 'time';
   ```

#### Step 3: Handle Errors (on execution failure)

1. **When directive execution fails**:
   ```python
   # Log to error file (JSON Lines)
   error_log = {
       "timestamp": datetime.utcnow().isoformat(),
       "directive_id": directive_id,
       "directive_name": directive_name,
       "error_type": type(error).__name__,
       "error_message": str(error),
       "stack_trace": traceback.format_exc(),
       "context": {
           "trigger_data": trigger_data,
           "action_attempted": action_name
       }
   }

   append_to_log(
       ".aifp-project/logs/errors/current_errors.log",
       json.dumps(error_log)
   )
   ```

2. **Update error statistics**:
   ```sql
   UPDATE directive_executions
   SET total_executions = total_executions + 1,
       error_count = error_count + 1,
       last_execution_time = CURRENT_TIMESTAMP,
       last_execution_status = 'error',
       last_error_time = CURRENT_TIMESTAMP,
       last_error_type = ?,
       last_error_message = ?
   WHERE directive_id = ?;
   ```

3. **Check error threshold**:
   ```python
   error_rate = error_count / total_executions

   if error_rate > 0.5 and total_executions > 10:
       # More than 50% failures
       alert_user(f"High error rate for {directive_name}")
       suggest_deactivation(directive_id)
   ```

#### Step 4: Log Rotation

1. **Check rotation conditions**:
   ```python
   # Daily rotation for execution logs
   if current_date != log_date:
       rotate_log(
           ".aifp-project/logs/executions/current.log",
           f".aifp-project/logs/executions/{log_date}.log"
       )

   # Size-based rotation for error logs
   if get_file_size("errors/current_errors.log") > 10 * 1024 * 1024:  # 10MB
       rotate_log(
           ".aifp-project/logs/errors/current_errors.log",
           f".aifp-project/logs/errors/{timestamp}_errors.log"
       )
   ```

2. **Clean up old logs**:
   ```python
   # Delete execution logs older than 30 days
   cleanup_old_logs(
       ".aifp-project/logs/executions/",
       retention_days=30
   )

   # Delete error logs older than 90 days
   cleanup_old_logs(
       ".aifp-project/logs/errors/",
       retention_days=90
   )
   ```

#### Step 5: Health Monitoring

1. **Check directive health**:
   ```python
   for directive in active_directives:
       # Check if scheduler job still exists
       if directive.trigger_type == 'time':
           job = scheduler.get_job(f"directive_{directive.id}")
           if not job:
               alert_user(f"Scheduler job missing for {directive.name}")

       # Check if background service still running
       if directive.trigger_type == 'condition':
           if not process_exists(directive.process_id):
               alert_user(f"Background service stopped for {directive.name}")
   ```

2. **Report to user on query**:
   ```
   User: "directive status"

   AI: [Calls this directive to generate report]

   📊 User Directive Status

   Active Directives: 3

   🟢 turn_off_lights_5pm
      Status: Active
      Next execution: Today at 5:00 PM EST
      Total executions: 24
      Success rate: 100%
      Last execution: Yesterday at 5:00 PM (success)

   🟢 monitor_stove
      Status: Active
      Total executions: 1440
      Success rate: 100%
      Last execution: 2 minutes ago (success)

   🔴 scale_ec2_high_cpu
      Status: Active (errors detected)
      Total executions: 288
      Success rate: 85.4% ⚠️
      Last execution: 5 minutes ago (error: connection timeout)
      Errors: 42 (last 24 hours)

   Logs: .aifp-project/logs/
   ```

---

### Branches

#### Branch 1: Normal Execution
- **Condition**: Directive executes successfully
- **Action**: Log, update stats, calculate next run

#### Branch 2: Error During Execution
- **Condition**: Directive execution fails
- **Action**: Log error, update error stats, check threshold, possibly alert

#### Branch 3: High Error Rate
- **Condition**: Error rate > 50% with >10 executions
- **Action**:
  1. Alert user
  2. Suggest deactivation or investigation
  3. Mark directive status as 'degraded'

#### Branch 4: Service Health Issue
- **Condition**: Scheduler job missing or process died
- **Action**:
  1. Alert user immediately
  2. Attempt recovery if configured
  3. Update status to 'error'

#### Branch 5: Log Rotation Triggered
- **Condition**: Date change or size threshold
- **Action**: Rotate logs, archive old logs, clean up expired logs

---

### Fallback

If monitoring system fails:
1. Log monitoring failure
2. Attempt restart
3. Alert user if critical
4. Directives continue executing (monitoring is separate)

---

## Examples

### ✅ Example 1: Successful Execution Tracking

**Execution Log** (`.aifp-project/logs/executions/2025-10-28.log`):
```json
{"timestamp": "2025-10-28T17:00:00.123Z", "directive_id": 1, "directive_name": "turn_off_lights_5pm", "status": "success", "duration_ms": 234, "trigger_type": "time", "result": "lights_off"}
{"timestamp": "2025-10-28T17:01:00.456Z", "directive_id": 2, "directive_name": "monitor_stove", "status": "success", "duration_ms": 12, "trigger_type": "condition", "result": "stove_off_no_action"}
{"timestamp": "2025-10-28T17:05:00.789Z", "directive_id": 3, "directive_name": "scale_ec2_high_cpu", "status": "success", "duration_ms": 1203, "trigger_type": "condition", "result": "cpu_normal_no_scaling"}
```

**Database Update**:
```sql
-- turn_off_lights_5pm stats
total_executions: 24 → 25
success_count: 24 → 25
last_execution_time: updated
avg_execution_time_ms: recalculated
```

---

### ⚠️ Example 2: Error Tracking

**Error Log** (`.aifp-project/logs/errors/2025-10-28_errors.log`):
```json
{"timestamp": "2025-10-28T17:00:05.123Z", "directive_id": 1, "directive_name": "turn_off_lights_5pm", "error_type": "ConnectionError", "error_message": "Failed to connect to Home Assistant API at http://homeassistant.local:8123", "stack_trace": "Traceback (most recent call last):\n  File ...", "context": {"trigger_data": {"time": "17:00"}, "action_attempted": "turn_off_lights"}}
```

**Database Update**:
```sql
-- turn_off_lights_5pm error stats
total_executions: 24 → 25
error_count: 0 → 1
last_error_time: updated
last_error_type: "ConnectionError"
last_error_message: "Failed to connect..."
```

**Alert to User**:
```
⚠️  Directive Error: turn_off_lights_5pm

Error: Failed to connect to Home Assistant API
Time: 5:00 PM EST
This is the 1st error out of 25 total executions (4% error rate)

Possible causes:
- Home Assistant server offline
- Network connectivity issue
- API endpoint changed

Would you like to:
a) Check Home Assistant status
b) View full error log
c) Deactivate directive temporarily
d) Ignore (monitor for pattern)
```

---

### 🔴 Example 3: High Error Rate Alert

**Scenario**: 15 consecutive errors

```
🚨 ALERT: High Error Rate for 'scale_ec2_high_cpu'

Status: 15 errors in last 15 executions (100% error rate)
Error: "NoCredentialsError: Unable to locate AWS credentials"

This directive is effectively non-functional.

Recommended action: Deactivate and fix configuration

Would you like me to:
a) Deactivate directive now
b) Show error logs for investigation
c) Help reconfigure AWS credentials
d) Continue monitoring (not recommended)
```

---

## Edge Cases

### 1. **Log File Write Failure**
- **Scenario**: Disk full, permissions issue
- **Handling**:
  - Log to stderr as fallback
  - Alert user about logging failure
  - Continue monitoring (don't crash)

### 2. **Database Connection Lost**
- **Scenario**: project.db locked or corrupted
- **Handling**:
  - Buffer stats in memory
  - Retry database update
  - Write to file if DB unavailable

### 3. **Monitoring Process Crashed**
- **Scenario**: Monitoring system itself fails
- **Handling**:
  - Directives continue executing
  - Attempt auto-restart monitoring
  - Alert user if monitoring down >5 minutes

### 4. **Clock Skew**
- **Scenario**: System time changed during execution
- **Handling**:
  - Use UTC timestamps
  - Detect time anomalies
  - Log warning if detected

### 5. **Rapid Error Spam**
- **Scenario**: Directive failing every second
- **Handling**:
  - Rate-limit error alerts
  - Auto-suggest deactivation
  - Don't spam user with alerts

### 6. **Log Rotation During Write**
- **Scenario**: Rotation happens while writing
- **Handling**:
  - Use file locks
  - Complete write before rotation
  - Ensure atomic operations

---

## Related Directives

### Pipeline Position
```
user_directive_activate
   ↓
user_directive_monitor (YOU ARE HERE - runs continuously)
```

### Triggered By
- **user_directive_activate**: Starts monitoring after activation
- **Directive executions**: Every execution event

### Triggers
- **user_directive_deactivate**: If high error rate, may suggest deactivation
- **user_directive_status**: Provides data for status reports

### Works With
- **All active directives**: Monitors their executions
- **project_notes_log**: Logs significant events

---

## Helper Functions Used

### Logging
- `append_to_log(log_file: str, content: str) -> bool`
  - Append JSON line to log file
  - Thread-safe file writes

- `rotate_log(current_path: str, archive_path: str) -> bool`
  - Move current log to archive
  - Create new current log

- `cleanup_old_logs(log_dir: str, retention_days: int) -> int`
  - Delete logs older than retention period
  - Returns count of deleted files

### Statistics
- `update_execution_stats(directive_id: int, success: bool, duration_ms: int) -> bool`
  - Update directive_executions table
  - Calculate averages

- `calculate_error_rate(directive_id: int) -> float`
  - Return error_count / total_executions

### Health Monitoring
- `check_scheduler_job_exists(job_id: str) -> bool`
  - Verify APScheduler job still registered

- `process_exists(pid: int) -> bool`
  - Check if background process running

### Alerting
- `alert_user(message: str, severity: str) -> bool`
  - Send alert to user
  - Severity: 'info', 'warning', 'error', 'critical'

---

## Database Operations

### Tables Read
```sql
-- Get all active directives
SELECT id, name, trigger_type, process_id
FROM user_directives
WHERE status = 'active';

-- Get current stats
SELECT total_executions, success_count, error_count
FROM directive_executions
WHERE directive_id = ?;
```

### Tables Updated

#### directive_executions
```sql
-- On successful execution
UPDATE directive_executions
SET total_executions = total_executions + 1,
    success_count = success_count + 1,
    last_execution_time = CURRENT_TIMESTAMP,
    last_execution_status = 'success',
    avg_execution_time_ms = (
        (avg_execution_time_ms * (total_executions - 1) + ?) / total_executions
    ),
    next_scheduled_time = ?  -- For time-based
WHERE directive_id = ?;

-- On error
UPDATE directive_executions
SET total_executions = total_executions + 1,
    error_count = error_count + 1,
    last_execution_time = CURRENT_TIMESTAMP,
    last_execution_status = 'error',
    last_error_time = CURRENT_TIMESTAMP,
    last_error_type = ?,
    last_error_message = ?
WHERE directive_id = ?;
```

#### user_directives (if health issue detected)
```sql
UPDATE user_directives
SET status = 'degraded'  -- or 'error'
WHERE id = ? AND error_rate > threshold;
```

---

## Testing

### Test 1: Track Successful Execution
```
Directive executes successfully
Expected: Execution logged to file, stats updated
Verify: Log file contains entry, total_executions incremented
```

### Test 2: Track Error
```
Directive execution fails
Expected: Error logged with stack trace, error stats updated
Verify: Error log contains entry, error_count incremented
```

### Test 3: High Error Rate Alert
```
15 consecutive errors
Expected: Alert sent to user, deactivation suggested
Verify: User sees alert with recommended actions
```

### Test 4: Log Rotation
```
Date changes at midnight
Expected: Execution log rotated, new log created
Verify: Yesterday's log archived, current.log reset
```

### Test 5: Health Check Detects Dead Process
```
Background service process killed externally
Expected: Monitoring detects, alerts user
Verify: Status shows 'error', user notified
```

---

## Common Mistakes

### ❌ Mistake 1: Blocking Directive Execution
**Wrong**: Monitoring blocks or delays directive execution
**Right**: Monitoring is async, never blocks execution

### ❌ Mistake 2: Not Rotating Logs
**Wrong**: Let log files grow indefinitely
**Right**: Rotate daily/by size, clean up old logs

### ❌ Mistake 3: Spamming Alerts
**Wrong**: Alert on every single error
**Right**: Rate-limit alerts, detect patterns

### ❌ Mistake 4: Database-Only Logging
**Wrong**: Store all execution data in database
**Right**: Use file-based logging, database for stats only

### ❌ Mistake 5: Ignoring Monitoring Failures
**Wrong**: If monitoring crashes, ignore it
**Right**: Auto-restart monitoring, alert if persistent failure

---

## References

- [Previous: user_directive_activate](./user_directive_activate.md)
- [Next: user_directive_update](./user_directive_update.md)
- [Blueprint: User Directives](../../blueprints/blueprint_user_directives.md)
- [Helper Functions Reference](../helper-functions-reference.md#monitoring-helpers)

---

## Notes

**Passive Monitoring**: This directive observes and tracks - it doesn't control execution.

**File-Based Logging**: Critical for performance. Database stores aggregated stats only.

**Continuous Operation**: Runs as long as any directive is active.

**Log Retention**: 30 days for executions, 90 days for errors (configurable).
