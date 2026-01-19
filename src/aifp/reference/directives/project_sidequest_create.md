# Directive: project_sidequest_create

**Type**: Project
**Level**: 3 (Task Management)
**Parent Directive**: project_task_decomposition
**Priority**: HIGH - Exploratory work tracking

---

## Purpose

The `project_sidequest_create` directive handles atomic creation of new sidequests in `project.db`. This directive serves as the **sidequest constructor**, providing a focused, validated interface for inserting new exploratory deviation records.

Sidequests are **exploratory interruptions** - fixes, pivots, or modifications that pause tasks when:
- User notices something that needs fixing
- User wants to explore a different direction
- An unrelated interruption requires attention
- Exploratory work doesn't fit the main roadmap

Key responsibilities:
- **Create sidequest record** - Insert into `sidequests` table
- **Link to paused task** - Optional reference to interrupted task
- **Set low priority** - Default priority lower than tasks (exploratory)
- **Link to project** - Associate with project, not milestone
- **Create initial items** - Set up work items for sidequest
- **Pause task if linked** - Mark parent task as paused
- **Validate inputs** - Ensure required fields present
- **Return sidequest ID** - Enable immediate linking to items

This is the **atomic sidequest creator** - called by `project_task_decomposition` when exploratory or interruption work is needed.

---

## When to Apply

This directive applies when:
- **Exploratory work** - User wants to try something new
- **Interruption handling** - Something needs immediate attention
- **Bug fixes during task** - Found issue while working on task
- **Direction pivot** - User wants to explore different approach
- **Unrelated work** - Work doesn't fit current milestone
- **Called by other directives**:
  - `project_task_decomposition` - Primary caller for sidequest creation
  - `project_user_referral` - User explicitly requests sidequest
  - User directly - Manual sidequest creation

---

## Workflow

### Trunk: validate_inputs

Ensures all required fields are present and valid.

**Steps**:
1. **Validate sidequest name** - Non-empty, descriptive
2. **Validate project** - Project exists and is active
3. **Validate paused_task** - If provided, task exists
4. **Validate priority** - Appropriate for exploratory work

### Branches

**Branch 1: If linked_to_task**
- **Then**: `create_with_task_link`
- **Details**: Sidequest pauses specific task
  - Validate task exists and is active
  - Create sidequest record
  - Set `paused_task_id` reference
  - Mark task as `is_paused = 1`
  - Set sidequest priority (default: low)
  - Log task pause in notes
  - Create initial items for sidequest
  - Return sidequest ID
- **Result**: Sidequest created, task paused

**Branch 2: If exploratory_work**
- **Then**: `create_standalone`
- **Details**: Exploratory sidequest not linked to task
  - Create sidequest record
  - Link to project (not milestone)
  - Set `paused_task_id = NULL`
  - Set low priority (exploratory)
  - Add note explaining purpose
  - Create initial items
  - Return sidequest ID
- **Result**: Standalone sidequest created

**Branch 3: If bug_fix**
- **Then**: `create_fix_sidequest`
- **Details**: Sidequest for bug fix
  - Create sidequest record
  - Link to task if bug found during task
  - Higher priority than normal sidequest
  - Add bug description to notes
  - Create fix items
  - Return sidequest ID
- **Result**: Bug fix sidequest created

**Branch 4: If pivot_exploration**
- **Then**: `create_pivot_sidequest`
- **Details**: Sidequest for trying different approach
  - Create sidequest record
  - Link to original task
  - Mark as pivot exploration
  - Low priority (don't block main work)
  - Document pivot reason
  - Create exploration items
  - Return sidequest ID
- **Result**: Pivot sidequest created

**Fallback**: `prompt_user`
- **Details**: Insufficient information
  - Ask user for sidequest purpose
  - Clarify if task should be paused
  - Get priority guidance
  - Log clarification request
- **Result**: User provides details

---

## Examples

### ✅ Compliant Usage

**Create Sidequest Linked to Task (Compliant):**

```python
def create_task_linked_sidequest(
    name: str,
    description: str,
    paused_task_id: int
) -> Result[int, str]:
    """Create sidequest that pauses specific task.

    Args:
        name: Sidequest name
        description: What needs to be done
        paused_task_id: Task being paused

    Returns:
        Ok with sidequest ID or Err if creation failed
    """
    return pipe(
        lambda: validate_task_exists(paused_task_id),
        lambda _: validate_task_active(paused_task_id),
        lambda _: insert_sidequest(
            name=name,
            description=description,
            project_id=get_current_project_id(),
            paused_task_id=paused_task_id,
            priority="low",
            status="pending"
        ),
        lambda sidequest_id: mark_task_paused(paused_task_id),
        lambda _: log_sidequest_creation(sidequest_id, paused_task_id),
        lambda _: create_initial_items(sidequest_id),
        lambda _: Ok(sidequest_id)
    ).or_else(lambda err: Err(f"Sidequest creation failed: {err}"))

# ✅ Validates task exists
# ✅ Pauses parent task
# ✅ Creates sidequest
# ✅ Logs operation
# ✅ Sets up items
```

**Why Compliant**:
- Complete validation
- Task pause handling
- Proper database updates
- Audit trail maintained

---

**Create Exploratory Sidequest (Compliant):**

```python
def create_exploratory_sidequest(
    name: str,
    description: str,
    exploration_reason: str
) -> Result[int, str]:
    """Create standalone exploratory sidequest.

    Args:
        name: Sidequest name
        description: What to explore
        exploration_reason: Why exploring

    Returns:
        Ok with sidequest ID or Err if creation failed
    """
    return pipe(
        lambda: validate_project_active(),
        lambda _: insert_sidequest(
            name=name,
            description=description,
            project_id=get_current_project_id(),
            paused_task_id=None,  # Not linked to task
            priority="low",
            status="pending"
        ),
        lambda sidequest_id: add_exploration_note(
            sidequest_id,
            exploration_reason
        ),
        lambda _: create_exploration_items(sidequest_id),
        lambda _: Ok(sidequest_id)
    ).or_else(lambda err: Err(f"Exploratory sidequest failed: {err}"))

# ✅ Standalone sidequest
# ✅ Low priority
# ✅ Documents exploration reason
# ✅ No task interruption
```

**Why Compliant**:
- Standalone exploratory work
- Proper priority setting
- Documentation of purpose
- Clean separation from tasks

---

**Create Bug Fix Sidequest (Compliant):**

```python
def create_bug_fix_sidequest(
    bug_description: str,
    found_during_task_id: Optional[int]
) -> Result[int, str]:
    """Create sidequest for bug fix.

    Args:
        bug_description: Description of bug
        found_during_task_id: Task where bug was found (optional)

    Returns:
        Ok with sidequest ID or Err if creation failed
    """
    priority = "medium"  # Bug fixes higher priority

    return pipe(
        lambda: validate_project_active(),
        lambda _: insert_sidequest(
            name=f"Fix: {bug_description[:50]}",
            description=bug_description,
            project_id=get_current_project_id(),
            paused_task_id=found_during_task_id,
            priority=priority,
            status="pending"
        ),
        lambda sidequest_id: add_bug_note(sidequest_id, bug_description),
        lambda _: create_fix_items(sidequest_id),
        lambda _: maybe_pause_task(found_during_task_id),
        lambda _: Ok(sidequest_id)
    ).or_else(lambda err: Err(f"Bug fix sidequest failed: {err}"))

# ✅ Medium priority for bugs
# ✅ Links to task if applicable
# ✅ Documents bug details
# ✅ Conditional task pause
```

**Why Compliant**:
- Appropriate priority for bugs
- Optional task linking
- Bug documentation
- Conditional behavior

---

### ❌ Non-Compliant Code

**Create Sidequest Without Pausing Task (Violation):**

```python
# ❌ VIOLATION: Sidequest references task but doesn't pause it
def bad_sidequest_create(name, task_id):
    execute_sql(
        f"INSERT INTO sidequests (name, paused_task_id) VALUES ('{name}', {task_id})"
    )
    print("Sidequest created!")

# Problem:
# - Task not marked as paused
# - No validation
# - No audit trail
# - Task continues running (inconsistent state)
```

**Why Non-Compliant**:
- Task not paused despite reference
- No validation
- Inconsistent state
- No logging

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Proper task pause handling
def create_sidequest_safe(
    name: str,
    task_id: int
) -> Result[int, str]:
    """Create sidequest with proper task pause.

    Args:
        name: Sidequest name
        task_id: Task to pause

    Returns:
        Ok with sidequest ID or Err if failed
    """
    return pipe(
        lambda: validate_task_exists(task_id),
        lambda _: insert_sidequest(name, task_id),
        lambda sidequest_id: mark_task_paused(task_id),
        lambda _: log_task_pause(task_id, sidequest_id),
        lambda _: Ok(sidequest_id)
    ).or_else(lambda err: Err(f"Failed: {err}"))

# Task properly paused
# Validation included
# Audit trail
```

---

**High Priority Sidequest (Violation):**

```python
# ❌ VIOLATION: Sidequest with high priority (should use subtask)
def create_urgent_sidequest(name):
    execute_sql(
        f"INSERT INTO sidequests (name, priority) VALUES ('{name}', 'high')"
    )

# Problem:
# - Sidequests should be low priority
# - High priority work should be subtask
# - Misusing sidequest concept
# - Wrong tool for urgent work
```

**Why Non-Compliant**:
- Wrong priority for sidequest
- Should use subtask instead
- Misuse of sidequest pattern
- Confuses work types

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Use subtask for high priority work
def create_urgent_work(
    name: str,
    parent_task_id: int
) -> Result[int, str]:
    """Create high-priority subtask, not sidequest.

    Args:
        name: Work description
        parent_task_id: Parent task

    Returns:
        Ok with subtask ID or Err if failed
    """
    # High priority work should be subtask
    return create_subtask(
        name=name,
        parent_task_id=parent_task_id,
        priority="high"
    )

# ✅ Correct work type
# ✅ Appropriate priority
# ✅ Proper pattern usage
```

---

## Edge Cases

### Edge Case 1: Sidequest While Subtask Active

**Issue**: User requests sidequest while subtask is in progress

**Handling**:
```python
def check_active_work_before_sidequest() -> Result[None, str]:
    """Check for active subtasks before creating sidequest.

    Returns:
        Ok if safe to create, Err if subtask active
    """
    active_subtasks = query_active_subtasks()

    if len(active_subtasks) > 0:
        return Err(
            f"Active subtask in progress. Complete/discard subtask "
            f"'{active_subtasks[0].name}' before creating sidequest."
        )

    return Ok(None)

# Check for active higher-priority work
```

**Directive Action**: Prompt user to handle active subtask first.

---

### Edge Case 2: Multiple Sidequests

**Issue**: Multiple sidequests created, which takes priority?

**Handling**:
```python
def get_highest_priority_sidequest() -> Optional[Sidequest]:
    """Get highest priority open sidequest.

    Returns:
        Highest priority sidequest or None
    """
    # Sidequests checked by: priority (medium > low), then created_at
    return query_one("""
        # Use project query helper: get_from_project_where('sidequests', {})
        WHERE status = 'pending' OR status = 'in_progress'
        ORDER BY
            CASE priority
                WHEN 'medium' THEN 1
                WHEN 'low' THEN 2
            END,
            created_at ASC
        LIMIT 1
    """)

# Priority order: medium (bugs) before low (exploration)
```

**Directive Action**: Process sidequests by priority, then creation order.

---

### Edge Case 3: Sidequest Completion

**Issue**: What happens when sidequest completes?

**Handling**:
```python
def complete_sidequest(sidequest_id: int) -> Result[None, str]:
    """Complete sidequest and resume paused task.

    Args:
        sidequest_id: Sidequest to complete

    Returns:
        Ok if successful, Err if failed
    """
    return pipe(
        lambda: get_sidequest(sidequest_id),
        lambda sq: mark_sidequest_complete(sq.id),
        lambda sq: resume_paused_task_if_exists(sq.paused_task_id),
        lambda _: log_sidequest_completion(sidequest_id),
        lambda _: Ok(None)
    )

# Resume task when sidequest completes
```

**Directive Action**: Resume paused task when sidequest completes.

---

## Related Directives

- **Depends On**:
  - `project_task_decomposition` - Determines when sidequest needed
- **Triggers**:
  - `project_item_create` - Create items for sidequest
  - `project_task_update` - Pause parent task
- **Called By**:
  - `project_task_decomposition` - Primary caller
  - `project_user_referral` - User requests sidequest
  - User directly - Manual creation
- **Escalates To**:
  - `project_user_referral` - If validation fails

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`sidequests`**: Inserts new sidequest record
- **`tasks`**: Sets `is_paused = 1` if task linked
- **`items`**: Creates initial work items for sidequest
- **`notes`**: Logs sidequest creation with `note_type = 'sidequest'`

---

## Priority Hierarchy

**AI Work Priority Order**:
1. **Sidequests** (highest - interruptions/fixes)
2. **Subtasks** (high - critical breakdowns)
3. **Tasks** (normal - planned work)

**Sidequest Priority Levels**:
- **Medium**: Bug fixes, critical issues
- **Low**: Exploratory work, pivots, investigations

---

## Testing

How to verify this directive is working:

1. **Create sidequest linked to task**
   ```python
   sidequest_id = create_task_linked_sidequest(
       "Fix type errors",
       "Clean up type annotations",
       task_id=5
   )
   # Verify task 5 is marked as paused
   ```

2. **Check task paused**
   **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

3. **Verify sidequest priority**
   **Use helper functions** for database operations. Query available helpers for the appropriate database.

4. **Check priority order**
   ```python
   # AI should work on sidequest before task
   status = get_project_status()
   assert status.current_focus.type == "sidequest"
   ```

---

## Common Mistakes

- ❌ **High priority sidequests** - Use subtasks for urgent work
- ❌ **Not pausing task** - Must pause task if sidequest references it
- ❌ **No exploration reason** - Document why exploring
- ❌ **Creating sidequest when subtask active** - Complete subtask first
- ❌ **Forgetting to resume task** - Resume task when sidequest completes

---

## Roadblocks and Resolutions

### Roadblock 1: task_already_paused
**Issue**: Task already paused by another sidequest
**Resolution**: Prompt user - complete existing sidequest or create standalone sidequest

### Roadblock 2: subtask_active
**Issue**: Subtask in progress (higher priority than sidequest)
**Resolution**: Prompt user to complete/discard subtask before creating sidequest

### Roadblock 3: unclear_purpose
**Issue**: Sidequest purpose unclear
**Resolution**: Prompt user for exploration reason, determine if really needs sidequest

### Roadblock 4: should_be_subtask
**Issue**: Work described is high priority (should be subtask, not sidequest)
**Resolution**: Suggest creating subtask instead with higher priority

---

## Sidequest vs Task vs Subtask

**When to use Sidequest**:
- ✅ Exploratory work not in roadmap
- ✅ Bug fixes found during task
- ✅ Trying different approach (pivot)
- ✅ Interruptions or unrelated work
- ✅ Low priority investigations

**When to use Subtask**:
- ✅ High priority work breakdown
- ✅ Critical to complete current task
- ✅ Blocking progress on parent task
- ✅ Must pause parent task

**When to use Task**:
- ✅ Planned work in roadmap
- ✅ Aligned to milestone
- ✅ Part of completion path
- ✅ Normal priority work

---

## References

None
---

*Part of AIFP v1.0 - Project directive for sidequest creation and exploratory work tracking*
