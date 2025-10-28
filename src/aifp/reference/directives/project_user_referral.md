# Directive: project_user_referral

**Type**: Project
**Level**: 4 (State Management)
**Parent Directive**: project_error_handling
**Priority**: HIGH - Standard fallback for uncertain operations

---

## Purpose

The `project_user_referral` directive handles situations where AI confidence is low or workflows fail, routing decisions to the user for guidance. This directive serves as the **human-in-the-loop gateway**, ensuring ambiguous operations never proceed without explicit user confirmation.

Key responsibilities:
- **Detect low confidence** - Identify when AI is uncertain
- **Present options clearly** - Show alternatives with context
- **Request clarification** - Ask specific, actionable questions
- **Log all referrals** - Record user decisions for learning
- **Preserve context** - Include directive name, issue, attempted solution
- **Enable learning** - Build knowledge base from user clarifications

This is the **uncertainty handler** - ensures AI never guesses when stakes are high.

---

## When to Apply

This directive applies when:
- **Confidence < threshold** - AI uncertainty exceeds acceptable level
- **Workflow failure** - Directive cannot proceed without input
- **Ambiguous request** - User intent unclear
- **Multiple valid options** - Choice requires domain knowledge
- **Risky operation** - User confirmation required for safety
- **Called by other directives**:
  - All project directives - Fallback for low confidence
  - `project_error_handling` - Escalates unresolved issues
  - User directly - Manual clarification requests

---

## Workflow

### Trunk: check_confidence

Evaluates AI confidence and determines if user referral is needed.

**Steps**:
1. **Assess confidence level** - Numeric score 0.0-1.0
2. **Check directive threshold** - Each directive has confidence threshold
3. **Determine referral need** - confidence < threshold → Refer to user
4. **Prepare clarification** - Format question with context
5. **Log referral** - Record in notes table

### Branches

**Branch 1: If low_confidence**
- **Then**: `prompt_user`
- **Details**: AI confidence too low to proceed autonomously
  - Present situation clearly
  - Show what AI attempted
  - List viable options
  - Ask specific question
  - Wait for user response
- **Prompt Format**:
  ```
  ⚠️  Uncertain Operation

  Directive: [directive_name]
  Confidence: [score] (threshold: [threshold])

  Situation: [description]

  AI Analysis: [what AI thinks]

  Options:
  1. [Option A - description]
  2. [Option B - description]
  3. [Option C - description]
  4. Other (specify)

  What should I do?
  ```
- **Result**: User provides clarification, AI proceeds with confidence

**Branch 2: If workflow_failure**
- **Then**: `escalate_to_md`
- **Details**: Directive workflow cannot continue
  - Show workflow state
  - Indicate failure point
  - Reference detailed .md documentation
  - Prompt for manual intervention
- **Prompt Format**:
  ```
  ❌ Workflow Failure

  Directive: [directive_name]
  Step: [failed_step]

  Attempted: [what was tried]
  Result: [failure reason]

  See detailed guidance:
  → src/aifp/reference/directives/[directive_name].md

  Options:
  1. Retry with modifications
  2. Skip this step
  3. Abort operation

  Choose action:
  ```
- **Result**: User reviews documentation, provides instructions

**Branch 3: If ambiguous_request**
- **Then**: `clarify_intent`
- **Details**: User request has multiple interpretations
  - Show possible interpretations
  - Ask which is correct
  - Provide examples
  - Log chosen interpretation
- **Prompt Format**:
  ```
  ❓ Ambiguous Request

  Your request: "[user_request]"

  Possible interpretations:
  1. [Interpretation A - example]
  2. [Interpretation B - example]
  3. [Interpretation C - example]

  Which did you mean?
  ```
- **Result**: User clarifies, AI proceeds with correct interpretation

**Branch 4: If multiple_valid_options**
- **Then**: `present_trade_offs`
- **Details**: Several valid approaches, choice requires domain knowledge
  - Show each option with pros/cons
  - Explain trade-offs
  - Ask user to choose
  - Log decision rationale
- **Prompt Format**:
  ```
  🔀 Multiple Valid Approaches

  Context: [situation]

  Option A: [name]
  Pros: [benefits]
  Cons: [drawbacks]

  Option B: [name]
  Pros: [benefits]
  Cons: [drawbacks]

  Recommendation: [AI suggestion with reasoning]

  Your choice:
  ```
- **Result**: User chooses, AI understands preference for future

**Branch 5: If risky_operation**
- **Then**: `require_confirmation`
- **Details**: Operation has significant consequences
  - Explain risk clearly
  - Show what will be affected
  - Require explicit "yes" to proceed
  - Log confirmation
- **Prompt Format**:
  ```
  ⚠️  Confirmation Required

  Operation: [risky_operation]

  This will:
  - [Impact 1]
  - [Impact 2]
  - [Impact 3]

  ⚠️  This cannot be easily undone

  Type "yes" to confirm or "no" to cancel:
  ```
- **Result**: User confirms or cancels

**Branch 6: If referral_logged**
- **Then**: `log_note`
- **Details**: Record referral in notes table
  - Include directive, issue, confidence score
  - Include user's decision
  - Enable future learning
- **SQL**:
  ```sql
  INSERT INTO notes (
    content,
    note_type,
    reference_table,
    reference_id,
    source,
    directive_name,
    severity
  ) VALUES (
    'User referral: [directive] - [issue]. Confidence: [score]. Decision: [user_choice]',
    'user_referral',
    'directives',
    ?,
    'user',
    'project_user_referral',
    'info'
  );
  ```
- **Result**: Referral logged for learning

**Branch 7: If user_provides_guidance**
- **Then**: `apply_guidance_and_proceed`
- **Details**: User clarified, AI can now proceed
  - Apply user's decision
  - Update confidence (now 1.0)
  - Continue with directive execution
  - Log successful resolution
- **Result**: Operation proceeds with clarity

**Branch 8: If user_cancels**
- **Then**: `abort_operation`
- **Details**: User chooses not to proceed
  - Rollback any partial changes
  - Log cancellation
  - Return to safe state
- **SQL**:
  ```sql
  -- Rollback transaction
  ROLLBACK;

  -- Log cancellation
  INSERT INTO notes (content, note_type, source, directive_name)
  VALUES ('Operation cancelled by user: [directive] - [operation]', 'cancellation', 'user', 'project_user_referral');
  ```
- **Result**: Operation safely aborted

**Branch 9: If pattern_for_learning**
- **Then**: `extract_learning`
- **Details**: User's decision reveals preference or pattern
  - Analyze decision context
  - Extract rule or preference
  - Suggest adding to user_preferences
  - Log learning opportunity
- **Prompt**:
  ```
  I notice you chose [option] for [context].

  Should I remember this preference?
  - "Always choose [option] for [context_pattern]"

  Add to preferences? (y/n)
  ```
- **Result**: Preference learned if confirmed

**Fallback**: `prompt_user_with_full_context`
- Present everything AI knows
- Ask for any guidance
- Log for manual review

### Error Handling

**on_failure**: `log_and_halt`
- If referral itself fails: Log critical error, halt
- Preserve all context for debugging
- Common issues: Cannot reach user, logging failure

---

## Examples

### Example 1: Low Confidence - Task Categorization

**Context**: User says "Do the database thing"

**AI Execution**:
1. Analyzes request: Multiple interpretations possible
2. Confidence: 0.3 (< threshold 0.5)
3. Prompts user:
   ```
   ❓ Ambiguous Request

   Your request: "Do the database thing"

   Possible interpretations:
   1. Create database schema (new task)
   2. Update existing database (maintenance)
   3. Query database for information (data retrieval)
   4. Sync database with code (project_dependency_sync)

   Which did you mean?
   ```
4. User clarifies: "4 - Sync database"
5. Logs:
   ```sql
   INSERT INTO notes (content, note_type, source, directive_name)
   VALUES ('User clarified: "database thing" = project_dependency_sync', 'clarification', 'user', 'project_user_referral');
   ```
6. Proceeds with `project_dependency_sync`

### Example 2: Workflow Failure - Cannot Create File

**Context**: `project_file_write` fails due to invalid path

**AI Execution**:
1. Attempts to write to `/nonexistent/path/file.py`
2. Fails: Directory doesn't exist
3. Checks roadblock: No automatic resolution
4. Escalates:
   ```
   ❌ Workflow Failure

   Directive: project_file_write
   Step: write_file

   Attempted: Write to /nonexistent/path/file.py
   Result: Directory does not exist

   Options:
   1. Create directory and retry
   2. Choose different path
   3. Abort file creation

   Choose action:
   ```
5. User chooses: "1" (Create directory)
6. AI creates directory:
   ```bash
   mkdir -p /nonexistent/path/
   ```
7. Retries file write: Success
8. Logs resolution

### Example 3: Multiple Valid Options - Delete Strategy

**Context**: Deleting file with dependencies

**AI Execution**:
1. User requests: "Delete src/old_module.py"
2. Checks dependencies: 3 other files depend on it
3. Multiple valid strategies exist
4. Prompts:
   ```
   🔀 Multiple Valid Approaches

   Context: src/old_module.py has 3 dependencies

   Option A: Soft Delete
   Pros: Preserves history, allows rollback
   Cons: Database still contains records

   Option B: Hard Delete
   Pros: Complete removal, clean database
   Cons: Cannot undo, may break dependencies

   Recommendation: Soft Delete (safer, reversible)

   Your choice:
   ```
5. User chooses: "A" (Soft delete)
6. Executes soft delete
7. Logs preference:
   ```
   User prefers soft delete for files with dependencies
   ```

### Example 4: Risky Operation - Delete Milestone

**Context**: User wants to delete milestone with 15 completed tasks

**AI Execution**:
1. Analyzes impact: 15 tasks, 42 items, 8 files linked
2. High-risk operation → Require confirmation
3. Prompts:
   ```
   ⚠️  Confirmation Required

   Operation: Delete milestone "Core Development"

   This will affect:
   - 15 tasks (all completed)
   - 42 items
   - 8 files (will be unlinked from milestone)

   ⚠️  This will remove history and cannot be easily undone

   Alternative: Archive milestone instead of delete?

   Type "yes" to delete, "archive" to archive, or "no" to cancel:
   ```
4. User responds: "archive"
5. Archives milestone instead (safer)
6. Logs decision

### Example 5: Ambiguous Function Intent

**Context**: Function name unclear

**AI Execution**:
1. Parsing `src/utils.py`:
   ```python
   def process(data):
       # Complex logic
       return result
   ```
2. Function name "process" is generic, confidence low (0.4)
3. Prompts:
   ```
   ❓ Unclear Function Purpose

   Function: process (in src/utils.py)

   The name "process" is generic. What does this function do?
   (This helps with documentation and dependency tracking)

   Examples:
   - "Process payment transactions"
   - "Process user input data"
   - "Process image files"

   Function purpose:
   ```
4. User provides: "Process and validate user registration data"
5. Updates function metadata:
   ```sql
   UPDATE functions
   SET purpose = 'Process and validate user registration data'
   WHERE name = 'process' AND file_id = ?;
   ```
6. Logs clarification

### Example 6: Learning from Pattern

**Context**: User consistently chooses specific theme for auth files

**AI Execution**:
1. User assigns theme "Security" to `src/auth/login.py`
2. AI checks history: Last 3 auth files also assigned "Security"
3. Detects pattern
4. Prompts:
   ```
   I notice you consistently assign theme "Security" to files in src/auth/.

   Should I remember this preference?
   - "Always suggest 'Security' theme for files in src/auth/"

   Add to preferences? (y/n)
   ```
5. User: "y"
6. Adds preference:
   ```sql
   INSERT INTO directive_preferences (directive_name, preference_key, preference_value)
   VALUES ('project_theme_flow_mapping', 'auth_path_theme', 'Security');
   ```
7. Future auth files automatically suggested "Security" theme

---

## Integration with Other Directives

### Called By:
- All project directives - Fallback for low confidence
- `project_error_handling` - Escalates unresolved issues
- User directly - Manual clarification

### Calls:
- Logging functions - Records all referrals
- User preference system - Learns from decisions

---

## Referral Logging

### Notes Table Format:

```sql
INSERT INTO notes (
  content,
  note_type,
  reference_table,
  reference_id,
  source,
  directive_name,
  severity
) VALUES (
  'User referral: [directive] - [issue]. Confidence: [score]. User decision: [choice]. Rationale: [reasoning]',
  'user_referral',
  'directives',
  [directive_id],
  'user',
  'project_user_referral',
  'info'
);
```

---

## Roadblocks and Resolutions

### Roadblock 1: unresolved_issue
**Issue**: AI cannot determine correct action
**Resolution**: Prompt user and record clarification in notes for learning

### Roadblock 2: low_confidence_path
**Issue**: Confidence below directive threshold
**Resolution**: Escalate to user confirmation before proceeding

### Roadblock 3: user_unavailable
**Issue**: Need user input but user not present
**Resolution**: Queue referral, pause operation, resume when user returns

### Roadblock 4: recursive_ambiguity
**Issue**: User's clarification is also ambiguous
**Resolution**: Provide more specific options, simplify question

---

## Intent Keywords

- "clarify"
- "user input"
- "confirmation"
- "resolve"
- "uncertain"
- "ambiguous"

**Confidence Threshold**: 0.5

---

## Related Directives

- `project_error_handling` - Escalates errors to referral
- All project directives - Use referral as fallback
- `user_preferences_learn` - Learns from referral patterns

---

## Confidence Thresholds by Directive

| Directive | Threshold | Rationale |
|-----------|-----------|-----------|
| project_task_create | 0.7 | Tasks are foundational, need clarity |
| project_file_write | 0.8 | File creation is permanent, high stakes |
| project_file_delete | 0.9 | Deletion is risky, requires high confidence |
| project_task_decomposition | 0.5 | Decomposition can be iterative, lower threshold |
| project_theme_flow_mapping | 0.5 | Can be corrected later, lower stakes |

---

## Prompt Design Principles

**Clear Context**:
- Always include directive name
- Show what AI attempted
- Explain why uncertain

**Actionable Options**:
- Provide specific choices
- Include "Other" option
- Show examples when helpful

**Risk Communication**:
- Clearly state consequences
- Use warning symbols for risky operations
- Offer safer alternatives

**Learning Opportunity**:
- Ask if preference should be remembered
- Extract patterns from decisions
- Build knowledge base

---

## User Response Handling

### Expected Responses:

| User Input | Interpretation | Action |
|------------|----------------|--------|
| "1", "Option 1" | Select option 1 | Apply chosen option |
| "yes", "y", "confirm" | Confirm | Proceed with operation |
| "no", "n", "cancel" | Cancel | Abort operation |
| "skip" | Skip this step | Continue without |
| "retry" | Try again | Re-execute with same params |
| Free text | Custom guidance | Parse and apply |

### Invalid Responses:

If user response unclear:
1. Repeat prompt with clarification
2. Show examples of valid responses
3. Max 2 repetitions before logging issue

---

## Notes

- **Never guess** - Always ask when uncertain
- **Preserve context** - Include full situation in prompt
- **Learn from referrals** - Build knowledge base
- **Log everything** - Audit trail for decisions
- **Clear communication** - User-friendly prompts
- **Offer alternatives** - Present multiple options
- **Explain risks** - Communicate consequences clearly
- **Enable learning** - Extract preferences from patterns
- **Graceful degradation** - Handle user unavailability
- **Respect user time** - Only refer when necessary
