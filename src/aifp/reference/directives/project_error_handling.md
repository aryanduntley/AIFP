# Directive: project_error_handling

**Type**: Project
**Level**: 4 (State Management)
**Parent Directive**: None (standalone utility directive)
**Priority**: HIGH - Universal error recovery for all directives

---

## Purpose

The `project_error_handling` directive monitors directive execution for failures and applies recovery strategies. This directive serves as the **universal error handler**, providing consistent error management across all project-level directives with transparency through logging.

Key responsibilities:
- **Monitor directive execution** - Catch failures during execution
- **Apply known resolutions** - Use stored roadblock solutions from directives
- **Log all errors** - Record in notes table for transparency and learning
- **Escalate unknown issues** - Route to user for guidance
- **Preserve context** - Include directive name, parameters, error details
- **Enable retry logic** - Support automatic and manual retries

This is the **directive safety net** - ensures graceful failure handling across the system.

---

## When to Apply

This directive applies when:
- **Directive execution fails** - Any project directive encounters error
- **Known roadblock detected** - Error matches stored resolution pattern
- **Unknown error occurs** - Error not in roadblock catalog
- **Retry needed** - Previous attempt failed, retry requested
- **Called by other directives**:
  - All project directives - Implicit error handling
  - User directly - Manual error investigation

---

## Workflow

### Trunk: check_roadblocks

Identifies error type and determines appropriate resolution.

**Steps**:
1. **Capture error context** - Directive name, parameters, error message, stack trace
2. **Query roadblock catalog** - Check if error matches known pattern
3. **Apply resolution** - Execute known fix or escalate to user
4. **Log error** - Record in notes table with full context
5. **Return result** - Success, retry, or user intervention needed

### Branches

**Branch 1: If known_issue**
- **Then**: `apply_resolution`
- **Details**: Error matches roadblock in directive definition
  - Look up roadblock resolution from directive JSON
  - Apply stored solution automatically
  - Log resolution attempt
  - Return result (success or retry needed)
- **Example Roadblocks**:
  ```json
  {
    "issue": "db_creation_failed",
    "resolution": "Check file permissions or re-run as admin"
  },
  {
    "issue": "checksum_mismatch",
    "resolution": "Run project_update_db to sync metadata"
  }
  ```
- **Log**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Known error resolved automatically or with guidance

**Branch 2: If unknown_issue**
- **Then**: `prompt_user`
- **Details**: Error doesn't match any known roadblock
  - Present full error context to user
  - Include directive name, parameters, error message
  - Ask: "How should I resolve this?"
  - Log user's resolution for future learning
  - Optionally add to roadblock catalog
- **Prompt Format**:
  ```
  ❌ Unknown error in directive: [directive_name]

  Error: [error_message]

  Context:
  - Parameters: [params]
  - Stack trace: [trace]

  This error is not in the roadblock catalog.

  How should I resolve this?
  ```
- **Result**: User provides resolution strategy

**Branch 3: If resolution_applied**
- **Then**: `log_note`
- **Details**: Record resolution in notes table
  - Include directive name, error type, resolution
  - Severity: info/warning/error
  - Source: directive
  - Enable future analysis and learning
- **SQL**:
  **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: Error logged for audit trail

**Branch 4: If resolution_failed**
- **Then**: `escalate_to_md`
- **Details**: Resolution attempt unsuccessful
  - Check if directive has detailed .md file
  - Present .md file guidance to user
  - Prompt for manual intervention
  - Log escalation
- **Example**:
  ```
  Resolution failed for: project_file_write

  Attempted: Check file permissions
  Result: Still failing

  See detailed guidance: src/aifp/reference/directives/project_file_write.md

  Manual intervention required.
  ```
- **Result**: User reviews detailed documentation

**Branch 5: If retry_requested**
- **Then**: `retry_with_backoff`
- **Details**: Attempt operation again after delay
  - Apply exponential backoff (1s, 2s, 4s, ...)
  - Max retries: 3 (configurable per directive)
  - Log each retry attempt
  - Return final result
- **Logic**:
  ```python
  for attempt in range(1, max_retries + 1):
      try:
          result = execute_directive(...)
          log_success()
          return result
      except Exception as e:
          if attempt < max_retries:
              wait_time = 2 ** (attempt - 1)
              log_retry(attempt, wait_time)
              sleep(wait_time)
          else:
              log_failure()
              escalate_to_user(e)
  ```
- **Result**: Retry succeeded or max attempts exceeded

**Branch 6: If database_error**
- **Then**: `handle_db_specific_errors`
- **Details**: Database-specific error handling
  - Lock timeout: Retry with backoff
  - Constraint violation: Analyze and suggest fix
  - Connection error: Reconnect and retry
  - Corruption: Restore from backup
- **Common DB Errors**:
  - `SQLITE_BUSY`: Database locked, retry
  - `SQLITE_CONSTRAINT`: Foreign key or unique constraint, validate data
  - `SQLITE_CANTOPEN`: Cannot open database, check permissions
  - `SQLITE_CORRUPT`: Database corrupted, restore backup
- **Result**: DB-specific resolution applied

**Branch 7: If parse_error**
- **Then**: `handle_parse_errors`
- **Details**: File parsing failure
  - Syntax error: Report to user, skip file
  - Encoding error: Try different encoding
  - Format error: Check file type
  - Log parsing context
- **Result**: Parse error handled gracefully

**Branch 8: If permission_error**
- **Then**: `handle_permission_errors`
- **Details**: File or directory permission issue
  - Check file permissions: `ls -la`
  - Check directory permissions
  - Suggest: `chmod` or run as appropriate user
  - Log permission error
- **Result**: User informed of permission fix

**Branch 9: If workflow_failure**
- **Then**: `prompt_user_and_halt`
- **Details**: Directive workflow cannot continue
  - Present failure point
  - Show workflow state
  - Ask: "Continue, retry, or abort?"
  - Log halt
- **Result**: User decides next action

**Fallback**: `prompt_user_and_log`
- Present complete error context
- Ask for guidance
- Log everything for future learning

### Error Handling

**on_failure**: `log_and_halt`
- If error handling itself fails: Log critical error, halt execution
- Preserve all context for debugging
- Common issues: Logging failure, database unavailable

---

## Examples

### Example 1: Known Issue - Database Lock

**Error**: `SQLITE_BUSY: database is locked`
**Directive**: `project_task_create`

**AI Execution**:
1. Catches error during task creation
2. Checks roadblock catalog:
   ```json
   {
     "issue": "database_lock",
     "resolution": "Retry after brief delay (max 2 attempts)"
   }
   ```
3. Applies retry with backoff:
   - Attempt 1: Wait 1s, retry
   - Attempt 2: Wait 2s, retry
   - Success: Task created
4. Logs resolution:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Returns success to user

### Example 2: Known Issue - Checksum Mismatch

**Error**: File checksum doesn't match database
**Directive**: `project_file_read`

**AI Execution**:
1. Detects checksum mismatch
2. Checks roadblock catalog:
   ```json
   {
     "issue": "checksum_mismatch",
     "resolution": "Run project_update_db to sync metadata"
   }
   ```
3. Suggests resolution to user:
   ```
   ⚠️  File modified outside AIFP

   File: src/auth.py
   DB checksum: sha256:abc123...
   Current: sha256:xyz789...

   Resolution: Run project_update_db to sync metadata
   ```
4. User runs: `project_update_db`
5. Logs:
   ```
   Checksum mismatch resolved: src/auth.py synced
   ```

### Example 3: Unknown Error - Custom Exception

**Error**: `CustomValidationError: Invalid matrix dimensions`
**Directive**: `project_file_write`

**AI Execution**:
1. Catches exception not in roadblock catalog
2. Prompts user:
   ```
   ❌ Unknown error in directive: project_file_write

   Error: CustomValidationError: Invalid matrix dimensions

   Context:
   - File: src/matrix.py
   - Function: multiply_matrices
   - Parameters: a=3x3, b=2x2

   This error is not in the roadblock catalog.

   Options:
   1. Fix and retry
   2. Skip this operation
   3. Add to roadblock catalog
   ```
3. User chooses: "1" (Fix and retry)
4. User fixes: Change b to 3x2
5. Retries successfully
6. Prompts: "Add this error to roadblock catalog for future?"
7. User: "Yes"
8. Logs:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Example 4: Retry with Exponential Backoff

**Error**: Network timeout (external API call)
**Directive**: `user_directive_activate` (home automation API)

**AI Execution**:
1. API call times out
2. Checks retry policy: Max 3 attempts
3. Retry sequence:
   - Attempt 1: Fail (timeout)
   - Wait 1s
   - Attempt 2: Fail (timeout)
   - Wait 2s
   - Attempt 3: Success
4. Logs:
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
5. Returns success

### Example 6: Permission Error

**Error**: `PermissionError: Cannot write to /project/src/`
**Directive**: `project_file_write`

**AI Execution**:
1. Catches permission error
2. Checks roadblock catalog:
   ```json
   {
     "issue": "permission_denied",
     "resolution": "Check file permissions, suggest chmod or run as appropriate user"
   }
   ```
3. Diagnoses:
   ```bash
   ls -la /project/src/
   # drwxr-xr-x user group /project/src/
   # → Directory is read-only for current user
   ```
4. Prompts user:
   ```
   ❌ Permission error

   Cannot write to: /project/src/

   Current permissions: drwxr-xr-x (read-only)

   Solutions:
   1. Run: chmod u+w /project/src/
   2. Run AI as user with write permissions
   3. Change project directory

   Choose solution:
   ```
5. User applies fix
6. Retries successfully

---

## Integration with Other Directives

### Called By:
- All project directives - Implicit error handling
- User directly - Manual error investigation

### Calls:
- `project_user_referral` - Escalates to user when uncertain
- Directive-specific .md files - Provides detailed guidance

---

## Error Logging Format

### Notes Table Entry:

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

### Severity Levels:

| Severity | Description | Example |
|----------|-------------|---------|
| info | Resolved automatically | Database lock resolved with retry |
| warning | Required intervention but resolved | Checksum mismatch, user synced |
| error | Failed to resolve, user intervention | Unknown error, manual fix needed |

---

## Roadblocks and Resolutions

### Roadblock 1: generic_error
**Issue**: Non-specific error without clear cause
**Resolution**: Prompt user and record in notes for future pattern matching

### Roadblock 2: workflow_failure
**Issue**: Directive workflow cannot continue
**Resolution**: Escalate to associated .md file for detailed guidance

### Roadblock 3: logging_failure
**Issue**: Cannot write to notes table
**Resolution**: Print to stderr, attempt to write to fallback log file

### Roadblock 4: recursive_error
**Issue**: Error handling itself fails
**Resolution**: Log critical error, halt execution, preserve context

---

## Intent Keywords

- "error"
- "failure"
- "roadblock"
- "issue"
- "exception"
- "handle error"

**Confidence Threshold**: 0.5

---

## Related Directives

- `project_user_referral` - Escalates uncertain issues to user
- All project directives - Rely on error handling

---

## Retry Configuration

### Per-Directive Retry Policies:

| Directive | Max Retries | Backoff | Conditions |
|-----------|-------------|---------|------------|
| project_task_create | 2 | Exponential | DB lock only |
| project_file_write | 3 | Exponential | Permission, lock |
| project_update_db | 2 | Exponential | DB lock only |
| user_directive_activate | 3 | Exponential | Network timeout |

### Backoff Formula:
```python
wait_time = min(2 ** (attempt - 1), max_wait)
# attempt=1 → 1s
# attempt=2 → 2s
# attempt=3 → 4s
# max_wait = 10s (cap)
```

---

## Error Context Preservation

When error occurs, preserve:
- **Directive name** - Which directive failed
- **Parameters** - Input values
- **Error message** - Exception text
- **Stack trace** - Full traceback
- **Timestamp** - When error occurred
- **User context** - Who was using AI
- **Project state** - Current project version, status

---

## Notes

- **Log everything** - Errors, resolutions, outcomes
- **Learn from errors** - Build roadblock catalog over time
- **Preserve context** - Full error details for debugging
- **Graceful degradation** - Continue when possible
- **User escalation** - Don't guess, ask when uncertain
- **Retry judiciously** - Not all errors should retry
- **Transactional safety** - Rollback on failure
- **Clear messaging** - User-friendly error explanations
