# Directive: project_notes_log

**Type**: Project
**Level**: 3
**Parent Directive**: None
**Priority**: HIGH - Core context management

---

## Purpose

The `project_notes_log` directive **logs important clarifications, reasoning, and directive execution context** to the `project.db notes table`, enabling AI assistants to maintain persistent memory across sessions. This directive is **not for logging** (which is opt-in in user_preferences.db), but rather for recording **critical decisions, clarifications, and context** that inform future AI behavior.

This directive is **essential for AI memory** because:
- **Session continuity**: Notes persist across AI sessions, restoring context
- **Decision traceability**: Records why specific choices were made
- **Clarification storage**: Saves user confirmations and intent
- **Roadblock documentation**: Tracks issues requiring future resolution
- **Directive attribution**: Optional `directive_name` field links notes to directive execution

The notes table stores:
1. **Clarifications** - User-confirmed intent or decisions
2. **Pivots** - Project goal or direction changes
3. **Research** - AI-documented findings or analysis
4. **Roadblocks** - Issues blocking progress or requiring future work

**Key distinction**: This is **NOT for debugging/logging** (that's opt-in via tracking_toggle). Notes are for **important context only**.

**Severity levels**:
- `info`: Normal clarifications and decisions
- `warning`: Important changes or pivots
- `error`: Roadblocks or critical issues

**Source tracking**:
- `user`: User explicitly stated note content
- `ai`: AI generated note from analysis
- `directive`: Note created during directive execution

**Optional directive_name field**:
- Only populated when note relates to specific directive execution
- Example: `project_file_write` notes FP compliance refactoring decision
- Provides traceability for directive-specific context

---

## When to Apply

This directive applies when:
- **Important clarification needed** - User confirms intent or decision
- **Project pivot occurs** - Goals or direction change
- **Roadblock encountered** - Issue blocks progress
- **Research findings** - AI documents analysis results
- **Directive makes decision** - Directive records reasoning for future reference
- **Ambiguity resolved** - User clarifies previously unclear requirement

**Not for**:
- ❌ Verbose debugging logs (use user_preferences.db tracking instead)
- ❌ Routine operations (only important context)
- ❌ Every directive execution (only when context is valuable)

---

## Workflow

### Trunk: determine_note_context

Identifies the note's purpose, content, and metadata.

**Steps**:
1. **Parse request** - What needs to be logged?
2. **Classify note type** - Clarification, pivot, research, or roadblock?
3. **Determine severity** - Info, warning, or error?
4. **Route to logging** - Insert into notes table

### Branches

**Branch 1: If clarification_note**
- **Then**: `log_clarification`
- **Details**: Record user-confirmed decision or intent
  - Note type: `'clarification'`
  - Typical severity: `'info'`
  - Examples:
    - "User confirmed: Use pure Python, no NumPy"
    - "User wants all functions to be pure (no side effects)"
    - "User clarified: Matrix operations should use immutable data structures"
  - SQL:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
  - Best practices:
    - Always quote exact user statement when possible
    - Link to relevant entity via reference_table/reference_id
    - Source = 'user' when user explicitly stated
- **Result**: Clarification stored for future sessions

**Branch 2: If pivot_note**
- **Then**: `log_pivot`
- **Details**: Record significant project direction change
  - Note type: `'pivot'`
  - Typical severity: `'warning'`
  - Examples:
    - "Pivoting from CLI tool to web API"
    - "User changed goal: Optimize for memory instead of speed"
    - "Abandoning OOP approach, switching to pure FP"
  - SQL:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
  - Update project version:
    **Use helper functions** for database operations. Query available helpers for the appropriate database.
  - Pivots are **high-severity** because they invalidate previous assumptions
- **Result**: Pivot documented, project version incremented

**Branch 3: If research_note**
- **Then**: `log_research`
- **Details**: Document AI analysis or findings
  - Note type: `'research'`
  - Typical severity: `'info'`
  - Examples:
    - "Function refactored for purity: eliminated mutation in calculate_total"
    - "Analyzed codebase: 15 functions are pure, 3 have side effects"
    - "Dependency analysis: matrix operations do not depend on I/O"
  - SQL:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
  - Use directive_name when note relates to specific directive execution
  - Reference specific entity (function, file, task) when relevant
- **Result**: Research findings stored for future reference

**Branch 4: If roadblock_note**
- **Then**: `log_roadblock`
- **Details**: Document issue blocking progress
  - Note type: `'roadblock'`
  - Typical severity: `'error'`
  - Examples:
    - "Cannot write to /protected/ - needs elevated permissions"
    - "External library 'numpy' conflicts with pure FP requirement"
    - "User ambiguity: Unclear whether to use Result or Option type"
  - SQL:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
  - Roadblocks should include:
    - What is blocked?
    - Why is it blocked?
    - What's needed to unblock?
  - High-priority for user review
- **Result**: Roadblock logged, flagged as error severity

**Branch 5: If directive_context_note**
- **Then**: `log_with_directive_name`
- **Details**: Record directive-specific decision or reasoning
  - Use when directive makes important decision
  - Populate directive_name field
  - Examples:
    - `project_file_write`: "FP compliance check required refactoring function X"
    - `project_task_decomposition`: "User request ambiguous - created subtask for clarification"
    - `git_merge_branch`: "Auto-resolved conflict using FP purity analysis (confidence 0.9)"
  - SQL:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
  - Provides traceability: Why did this directive make this choice?
- **Result**: Directive reasoning documented with attribution

**Branch 6: If reference_entity**
- **Then**: `link_to_entity`
- **Details**: Link note to specific project entity
  - Valid reference_tables:
    - `'project'` - Project-wide notes
    - `'files'` - File-specific notes
    - `'functions'` - Function-specific notes
    - `'tasks'` - Task-specific notes
    - `'milestones'` - Milestone-specific notes
    - `'themes'` - Theme-specific notes
    - `'flows'` - Flow-specific notes
  - Query to get entity ID:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
  - Insert with reference:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
  - Enables querying notes by entity
- **Result**: Note linked to specific entity

**Fallback**: `prompt_user`
- **Details**: Unable to determine note context
  - Clarify with user:
    ```
    What would you like to log?

    Note types:
    1. Clarification - Confirm intent or decision
    2. Pivot - Project direction change
    3. Research - Document findings
    4. Roadblock - Issue blocking progress

    Your choice (1-4): _
    ```
  - Get note content from user
  - Determine severity and references
- **Result**: User clarifies what to log

---

## Examples

### ✅ Compliant Usage

**Logging User Clarification:**
```python
# User: "I want to use pure Python, no external dependencies"
# AI calls: project_notes_log()

# Workflow:
# 1. determine_note_context:
#    - Type: clarification
#    - Content: User's exact statement
#    - Source: user
#    - Severity: info
#
# 2. log_clarification:
INSERT INTO notes (
  content,
  note_type,
  reference_table,
  reference_id,
  source,
  severity
) VALUES (
  'User confirmed: Use pure Python, no external dependencies',
  'clarification',
  'project',
  1,
  'user',
  'info'
)

# Result:
# ✅ User intent recorded
# ✅ Future sessions will respect this clarification
# ✅ No directive_name (not directive-specific)
```

---

**Logging Project Pivot:**
```python
# AI detected major direction change
# User pivoting from CLI to web API

# Workflow:
# 1. determine_note_context:
#    - Type: pivot
#    - Severity: warning (high importance)
#
# 2. log_pivot:
INSERT INTO notes (
  content,
  note_type,
  reference_table,
  reference_id,
  source,
  severity
) VALUES (
  'Pivoting from CLI tool to web API. Infrastructure will change.',
  'pivot',
  'project',
  1,
  'ai',
  'warning'
)

# Update project version (major change)
UPDATE project
SET version = version + 1,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 1

# Result:
# ✅ Pivot documented
# ✅ Project version incremented
# ✅ Severity = warning (alerts future sessions)
```

---

**Logging Research Findings:**
```python
# AI analyzed function and documented findings
# After refactoring calculate_total for purity

# Workflow:
# 1. determine_note_context:
#    - Type: research
#    - Reference: functions table, ID 42
#    - Source: directive (project_file_write)
#
# 2. log_research:
INSERT INTO notes (
  content,
  note_type,
  reference_table,
  reference_id,
  source,
  directive_name,
  severity
) VALUES (
  'Function refactored for purity: eliminated in-place mutation. Now returns new data structure.',
  'research',
  'functions',
  42,  -- calculate_total function ID
  'directive',
  'project_file_write',  -- Directive that did refactoring
  'info'
)

# Result:
# ✅ Refactoring decision documented
# ✅ Linked to specific function
# ✅ Directive attribution included
# ✅ Future sessions know why function changed
```

---

**Logging Roadblock:**
```python
# AI encountered permission issue
# Cannot write to protected directory

# Workflow:
# 1. determine_note_context:
#    - Type: roadblock
#    - Severity: error (blocks progress)
#    - Reference: files table, ID 5
#
# 2. log_roadblock:
INSERT INTO notes (
  content,
  note_type,
  reference_table,
  reference_id,
  source,
  directive_name,
  severity
) VALUES (
  'Cannot write to /protected/config.py - needs elevated permissions. User must chmod or run as sudo.',
  'roadblock',
  'files',
  5,
  'directive',
  'project_file_write',
  'error'
)

# Result:
# ✅ Roadblock documented
# ✅ Severity = error (high priority)
# ✅ User can review and resolve
# ✅ Next session will know about this issue
```

---

**Logging Directive Decision:**
```python
# project_task_decomposition encountered ambiguity
# Created subtask for clarification

# Workflow:
# 1. determine_note_context:
#    - Type: clarification
#    - Source: directive
#    - Directive_name: project_task_decomposition
#
# 2. log_with_directive_name:
INSERT INTO notes (
  content,
  note_type,
  reference_table,
  reference_id,
  source,
  directive_name,
  severity
) VALUES (
  'User request ambiguous: "optimize performance" could mean speed or memory. Created subtask for user to clarify.',
  'clarification',
  'tasks',
  15,  -- parent task ID
  'directive',
  'project_task_decomposition',
  'info'
)

# Result:
# ✅ Ambiguity documented
# ✅ Directive attribution clear
# ✅ Future sessions know why subtask exists
```

---

### ❌ Non-Compliant Usage

**Logging Verbose Debug Info:**
```python
# ❌ Using notes for logging/debugging
INSERT INTO notes (content, note_type, source, severity)
VALUES ('Function called with args: [1, 2, 3]', 'research', 'ai', 'info')

# Why Non-Compliant:
# - This is debugging/logging, not important context
# - Should use user_preferences.db tracking (opt-in)
# - Notes are for critical decisions only
```

**Corrected:**
```python
# ✅ Use tracking (opt-in) for debugging
# Only log if ai_interaction_log or helper_function_logging enabled
if tracking_enabled('helper_function_logging'):
    log_to_user_preferences_db('Function called with args: [1, 2, 3]')
# Notes table not used for routine logging
```

---

**Missing directive_name When Relevant:**
```python
# ❌ Directive makes decision but doesn't attribute it
INSERT INTO notes (content, note_type, source, severity)
VALUES (
  'FP compliance check required refactoring',
  'research',
  'directive',  # Source says directive, but which one?
  'info'
)
# directive_name is NULL - loses traceability!
```

**Corrected:**
```python
# ✅ Include directive_name for attribution
INSERT INTO notes (content, note_type, source, directive_name, severity)
VALUES (
  'FP compliance check required refactoring function X',
  'research',
  'directive',
  'project_file_write',  # Now we know which directive
  'info'
)
```

---

**Not Linking to Entity:**
```python
# ❌ Note about function but no reference
INSERT INTO notes (content, note_type, source, severity)
VALUES ('Function calculate_total optimized', 'research', 'ai', 'info')
# Which function? No reference_table/reference_id
```

**Corrected:**
```python
# ✅ Link to specific function
# Use project query helper to find function by name
functions = get_from_project_where('functions', {'name': 'calculate_total'})
function_id = functions[0]['id'] if functions else None
INSERT INTO notes (content, note_type, reference_table, reference_id, source, severity)
VALUES (
  'Function calculate_total optimized for performance',
  'research',
  'functions',
  function_id,  # Now linked to specific function
  'ai',
  'info'
)
```

---

## Edge Cases

### Edge Case 1: Note for Non-Existent Entity

**Issue**: Trying to reference entity that doesn't exist

**Handling**:
```python
# Validate entity exists before inserting
# Use project query helper
functions = get_from_project_where('functions', {'name': function_name})
function_id = functions[0]['id'] if functions else None

if not function_id:
    # Entity doesn't exist - log without reference or create entity first
    INSERT INTO notes (content, note_type, source, severity)
    VALUES (
      f'Note about {function_name} (function not yet in database)',
      'research',
      'ai',
      'info'
    )
    # Or create function entry first, then reference it
```

**Directive Action**: Validate references before logging.

---

### Edge Case 2: Duplicate Notes

**Issue**: Same note logged multiple times

**Handling**:
```python
# Use project query helper to check for duplicates
# Note: For time-based queries, get all matching notes and filter
all_notes = get_from_project_where('notes', {'content': note_content})
# Filter for recent notes (last 5 minutes)
from datetime import datetime, timedelta
recent_cutoff = datetime.now() - timedelta(minutes=5)
recent_duplicate = [n for n in all_notes if datetime.fromisoformat(n['created_at']) > recent_cutoff]

if recent_duplicate:
    # Don't insert duplicate
    return {"skipped": True, "reason": "Duplicate note"}
else:
    # Use project CRUD helper to add note
    # add_note(...)
```

**Directive Action**: Prevent duplicate notes within short time window.

---

### Edge Case 3: Extremely Long Note Content

**Issue**: Note content exceeds reasonable length

**Handling**:
```python
MAX_NOTE_LENGTH = 2000  # characters

if len(note_content) > MAX_NOTE_LENGTH:
    # Truncate and add indicator
    truncated_content = note_content[:MAX_NOTE_LENGTH] + "... [truncated]"
    INSERT INTO notes (content, note_type, source, severity)
    VALUES (truncated_content, note_type, source, severity)
else:
    INSERT INTO notes (content, note_type, source, severity)
    VALUES (note_content, note_type, source, severity)
```

**Directive Action**: Truncate long notes, keep database performant.

---

## Related Directives

- **Called By**:
  - `project_file_write` - Logs FP compliance decisions and refactoring reasoning
  - `project_task_decomposition` - Logs ambiguity clarifications
  - `project_blueprint_update` - Logs blueprint changes
  - User requests - "Remember that I want X"
- **Calls**:
  - Database helpers for notes table operations
- **Related**:
  - `user_preferences_sync` - Both provide context, but notes are project-wide
  - `tracking_toggle` - Tracking is opt-in logging, notes are important context

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following table:

- **`notes`**: INSERT clarifications, pivots, research, and roadblocks

**No data deletion**: Notes are append-only (never deleted, only queried).

**Indexes used**:
- `idx_notes_directive` - Query by directive_name
- `idx_notes_severity` - Query by severity (error roadblocks)
- `idx_notes_source` - Query by source (user vs ai vs directive)
- `idx_notes_reference` - Query by entity reference

---

## Testing

How to verify this directive is working:

1. **Log clarification** → Note inserted with correct type
   ```python
   project_notes_log(
     content="User confirmed: pure Python only",
     note_type="clarification",
     source="user"
   )

   # Use project query helper
   result = get_from_project_where('notes', {'note_type': 'clarification'})
   assert len(result) > 0
   assert result[0]['content'] == "User confirmed: pure Python only"
   ```

2. **Log with directive_name** → Attribution included
   ```python
   project_notes_log(
     content="FP compliance check refactored function X",
     note_type="research",
     source="directive",
     directive_name="project_file_write"
   )

   # Use project query helper
   result = get_from_project_where('notes', {'directive_name': 'project_file_write'})
   assert len(result) > 0
   ```

3. **Log roadblock** → Severity = error
   ```python
   project_notes_log(
     content="Cannot write to /protected/",
     note_type="roadblock",
     severity="error"
   )

   # Use project query helper
   result = get_from_project_where('notes', {'severity': 'error'})
   assert len(result) > 0
   assert result[0]['note_type'] == 'roadblock'
   ```

4. **Link to entity** → Reference set correctly
   ```python
   function_id = 42
   project_notes_log(
     content="Function optimized",
     note_type="research",
     reference_table="functions",
     reference_id=function_id
   )

   # Use project query helper
   result = get_from_project_where('notes', {'reference_table': 'functions', 'reference_id': 42})
   assert len(result) > 0
   ```

---

## Common Mistakes

- ❌ **Using notes for logging** - Use user_preferences.db tracking instead
- ❌ **Missing directive_name** - Include when directive makes decision
- ❌ **Not linking to entities** - Use reference_table/reference_id
- ❌ **Logging routine operations** - Only important context
- ❌ **Duplicate notes** - Check for recent duplicates first

---

## Roadblocks and Resolutions

### Roadblock 1: entity_not_found
**Issue**: Reference entity doesn't exist in database
**Resolution**: Validate entity exists before inserting note, or log without reference

### Roadblock 2: duplicate_note
**Issue**: Same note content logged multiple times
**Resolution**: Check for duplicates in recent time window, skip if duplicate

### Roadblock 3: note_too_long
**Issue**: Note content exceeds reasonable length
**Resolution**: Truncate content with indicator, keep database performant

---

## References

None

---

## Implementation Notes

**Use Helpers, Not Direct SQL**:
- All database operations use project CRUD/query helpers
- Examples show conceptual operations - actual implementation uses helpers
- For time-based queries: query all matching records, then filter in code
- Never use direct SQL queries or conn.execute in directives

---

*Part of AIFP v1.0 - Core context management directive for persistent AI memory*
