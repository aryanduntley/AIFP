# Directive: project_refactor_path

**Type**: Project
**Level**: 3 (Task Management)
**Parent Directive**: project_evolution
**Priority**: MEDIUM - Roadmap clarity

---

## Purpose

The `project_refactor_path` directive allows restructuring of `completion_path` sequences for clarity, merging or reordering tasks while maintaining linkage integrity. This directive provides **roadmap reorganization**, ensuring the completion path accurately reflects project progress and structure.

Path refactoring provides **roadmap clarity**, enabling:
- **Milestone Merging**: Combine duplicate or overlapping milestones
- **Task Reordering**: Adjust task sequence for better flow
- **Path Cleanup**: Remove obsolete or completed paths
- **Hierarchy Adjustment**: Fix misaligned task relationships
- **Linkage Preservation**: Maintain database integrity during restructuring

This directive acts as a **roadmap organizer** ensuring completion paths stay clean and accurate.

---

## When to Apply

This directive applies when:
- **Duplicate milestones** - Multiple milestones serving same purpose
- **Path misalignment** - Tasks in wrong order or wrong milestone
- **Roadmap evolution** - Project structure changed
- **Cleanup needed** - Obsolete paths cluttering roadmap
- **Called by other directives**:
  - `project_evolution` - Refactor after major project changes
  - `project_completion_check` - Fix misaligned completion paths
  - `project_user_referral` - User requests roadmap cleanup
  - Works with `project_theme_flow_mapping` - Align paths with themes

---

## Workflow

### Trunk: analyze_completion_path

Examines current completion path structure for issues.

**Steps**:
1. **Load completion path** - Get all milestones and tasks
2. **Detect issues** - Find duplicates, misalignments, gaps
3. **Analyze relationships** - Check task linkages
4. **Route to appropriate branch** - Based on issue type

### Branches

**Branch 1: If duplicate_milestone**
- **Then**: `merge_entries`
- **Details**: Combine duplicate milestones
  - Identify duplicate milestones
  - Merge tasks from both milestones
  - Preserve all task linkages
  - Update task.milestone_id references
  - Keep most descriptive name
  - Update order indices
  - Remove duplicate milestone
  - Log merge in notes
- **Result**: Milestones merged successfully

**Branch 2: If order_misaligned**
- **Then**: `reorder_path`
- **Details**: Fix task/milestone ordering
  - Identify correct order
  - Update order_index for milestones
  - Update task sequence within milestones
  - Preserve dependencies
  - Check for circular dependencies
  - Update database order indices
  - Log reordering in notes
- **Result**: Path reordered correctly

**Branch 3: If obsolete_path**
- **Then**: `archive_or_remove`
- **Details**: Handle obsolete completion paths
  - Mark path as obsolete
  - Move completed tasks to archive
  - Update active path references
  - Preserve for historical record
  - Log archival in notes
- **Result**: Obsolete path archived

**Branch 4: If misaligned_tasks**
- **Then**: `reassign_tasks`
- **Details**: Move tasks to correct milestone
  - Identify correct milestone
  - Update task.milestone_id
  - Preserve task order within new milestone
  - Update subtask linkages
  - Log reassignment in notes
- **Result**: Tasks correctly aligned

**Branch 5: If gaps_detected**
- **Then**: `fill_or_prompt`
- **Details**: Handle gaps in completion path
  - Identify missing milestones
  - Suggest milestone creation
  - Prompt user for clarification
  - Log gaps in notes
- **Result**: Gaps identified for user

**Fallback**: `log_changes`
- **Details**: Record analysis results
  - Log current path structure
  - Note any issues found
  - Recommend actions
- **Result**: Analysis logged

---

## Examples

### ✅ Compliant Usage

**Merge Duplicate Milestones (Compliant):**

```python
def merge_duplicate_milestones(
    milestone1_id: int,
    milestone2_id: int
) -> Result[int, str]:
    """Merge two duplicate milestones into one.

    Args:
        milestone1_id: First milestone ID
        milestone2_id: Second milestone ID (will be removed)

    Returns:
        Ok with merged milestone ID or Err if merge failed
    """
    return pipe(
        lambda: validate_milestones_exist(milestone1_id, milestone2_id),
        lambda _: get_tasks_for_milestone(milestone2_id),
        lambda tasks: reassign_tasks_to_milestone(tasks, milestone1_id),
        lambda _: merge_milestone_metadata(milestone1_id, milestone2_id),
        lambda _: archive_milestone(milestone2_id),
        lambda _: log_milestone_merge(milestone1_id, milestone2_id),
        lambda _: Ok(milestone1_id)
    ).or_else(lambda err: Err(f"Merge failed: {err}"))

# ✅ Validates milestones exist
# ✅ Preserves all tasks
# ✅ Updates references
# ✅ Archives old milestone
# ✅ Logs operation
```

**Why Compliant**:
- Complete validation
- All tasks preserved
- References updated
- Audit trail maintained

---

**Reorder Completion Path (Compliant):**

```python
def reorder_completion_path(
    new_order: list[tuple[int, int]]
) -> Result[None, str]:
    """Reorder milestones in completion path.

    Args:
        new_order: List of (milestone_id, new_order_index) tuples

    Returns:
        Ok if reordering successful, Err if failed
    """
    # Validate no circular dependencies
    dependency_check = validate_no_circular_deps(new_order)
    if dependency_check.is_err():
        return Err("Cannot reorder: circular dependencies detected")

    # Update order indices
    return pipe(
        lambda: begin_transaction(),
        lambda _: update_milestone_order_indices(new_order),
        lambda _: verify_path_integrity(),
        lambda _: commit_transaction(),
        lambda _: log_reordering(new_order),
        lambda _: Ok(None)
    ).or_else(lambda err: rollback_and_error(err))

# ✅ Dependency validation
# ✅ Transaction for atomicity
# ✅ Integrity verification
# ✅ Rollback on error
```

**Why Compliant**:
- Dependency checking
- Atomic transaction
- Integrity verification
- Error handling with rollback

---

**Reassign Tasks to Correct Milestone (Compliant):**

```python
def reassign_tasks_to_milestone(
    task_ids: list[int],
    new_milestone_id: int
) -> Result[None, str]:
    """Move tasks to correct milestone.

    Args:
        task_ids: List of task IDs to reassign
        new_milestone_id: Target milestone ID

    Returns:
        Ok if reassignment successful, Err if failed
    """
    return pipe(
        lambda: validate_milestone_exists(new_milestone_id),
        lambda _: validate_tasks_exist(task_ids),
        lambda _: map(
            lambda task_id: update_task_milestone(task_id, new_milestone_id),
            task_ids
        ),
        lambda results: check_all_success(results),
        lambda _: update_milestone_task_count(new_milestone_id),
        lambda _: log_task_reassignment(task_ids, new_milestone_id),
        lambda _: Ok(None)
    ).or_else(lambda err: Err(f"Reassignment failed: {err}"))

# ✅ Validation before changes
# ✅ All tasks processed
# ✅ Update milestone metadata
# ✅ Complete audit trail
```

**Why Compliant**:
- Complete validation
- Batch processing
- Metadata updates
- Proper logging

---

### ❌ Non-Compliant Code

**Merge Without Preserving Tasks (Violation):**

```python
# ❌ VIOLATION: Delete milestone without moving tasks
def quick_merge(milestone1_id, milestone2_id):
    execute_sql(f"DELETE FROM milestones WHERE id = {milestone2_id}")
    print("Merged!")

# Problem:
# - Tasks linked to milestone2_id now orphaned
# - Foreign key constraints violated
# - Data loss
# - No audit trail
```

**Why Non-Compliant**:
- Orphans tasks
- Violates referential integrity
- Data loss
- No logging

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Safe merge with task preservation
def safe_merge_milestones(
    milestone1_id: int,
    milestone2_id: int
) -> Result[None, str]:
    """Safely merge milestones preserving all tasks.

    Args:
        milestone1_id: Target milestone
        milestone2_id: Source milestone (will be archived)

    Returns:
        Ok if merge successful, Err if failed
    """
    # Get all tasks from milestone2
    tasks = get_tasks_for_milestone(milestone2_id)

    if tasks.is_err():
        return Err("Cannot get tasks for source milestone")

    # Reassign all tasks to milestone1
    return pipe(
        lambda: reassign_tasks(tasks.unwrap(), milestone1_id),
        lambda _: verify_no_orphaned_tasks(milestone2_id),
        lambda _: archive_milestone(milestone2_id),
        lambda _: log_merge(milestone1_id, milestone2_id),
        lambda _: Ok(None)
    )

# Tasks preserved
# Verification step
# Safe archival
```

---

**Reorder Without Dependency Check (Violation):**

```python
# ❌ VIOLATION: Reorder without checking dependencies
def reorder_milestones(new_order):
    for milestone_id, order_index in new_order:
        execute_sql(
            f"UPDATE milestones SET order_index = {order_index} WHERE id = {milestone_id}"
        )

# Problem:
# - No dependency validation
# - Could create circular dependencies
# - No transaction (partial update on failure)
# - No integrity check
```

**Why Non-Compliant**:
- No dependency checking
- Not atomic
- No integrity verification
- No error handling

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Safe reordering with validation
def safe_reorder_milestones(
    new_order: list[tuple[int, int]]
) -> Result[None, str]:
    """Safely reorder milestones with dependency validation.

    Args:
        new_order: List of (milestone_id, order_index) tuples

    Returns:
        Ok if reordering successful, Err if failed
    """
    # Check for circular dependencies first
    if has_circular_deps(new_order):
        return Err("Circular dependency detected")

    # Use transaction for atomicity
    with database_transaction() as txn:
        result = pipe(
            lambda: validate_all_milestones_exist(new_order),
            lambda _: apply_new_order(new_order),
            lambda _: verify_path_integrity(),
            lambda _: Ok(None)
        )

        if result.is_err():
            txn.rollback()
            return result
        else:
            txn.commit()
            log_reordering(new_order)
            return result

# Dependency validation
# Atomic transaction
# Integrity check
# Proper error handling
```

---

## Edge Cases

### Edge Case 1: Circular Dependencies

**Issue**: Reordering creates circular dependencies

**Handling**:
```python
def detect_circular_dependencies(
    new_order: list[tuple[int, int]]
) -> Result[None, str]:
    """Check for circular dependencies in new order.

    Args:
        new_order: Proposed new milestone order

    Returns:
        Ok if no circular deps, Err if circular dependency found
    """
    # Build dependency graph
    graph = build_dependency_graph(new_order)

    # Use depth-first search to detect cycles
    if has_cycle(graph):
        return Err("Circular dependency detected in new order")

    return Ok(None)

# Detect circular dependencies before applying
```

**Directive Action**: Validate dependency graph before reordering.

---

### Edge Case 2: Milestone with Active Tasks

**Issue**: Trying to archive milestone with in_progress tasks

**Handling**:
```python
def safe_archive_milestone(milestone_id: int) -> Result[None, str]:
    """Archive milestone only if no active tasks.

    Args:
        milestone_id: Milestone to archive

    Returns:
        Ok if archived, Err if active tasks exist
    """
    active_tasks = get_active_tasks_for_milestone(milestone_id)

    if len(active_tasks) > 0:
        return Err(
            f"Cannot archive: {len(active_tasks)} active tasks remaining"
        )

    return archive_milestone(milestone_id)

# Check for active tasks before archival
```

**Directive Action**: Prevent archival of milestones with active work.

---

## Related Directives

- **Depends On**:
  - `project_integrity_check` - Verify integrity after refactoring
- **Triggers**:
  - `project_evolution` - Update ProjectBlueprint after refactoring
  - `project_integrity_check` - Verify path integrity
- **Called By**:
  - `project_evolution` - Refactor after major changes
  - `project_completion_check` - Fix path misalignment
  - `project_user_referral` - User requests cleanup
- **Escalates To**:
  - `project_user_referral` - If path conflict requires user decision

---

## Helper Functions Used

- `get_completion_path() -> list[Milestone]` - Get all milestones
- `merge_milestones(id1: int, id2: int) -> Result[int, str]` - Merge two milestones
- `reorder_milestones(order: list[tuple]) -> Result[None, str]` - Update order
- `reassign_tasks(tasks: list[int], milestone_id: int) -> Result[None, str]` - Move tasks
- `validate_no_circular_deps(order: list) -> Result[None, str]` - Check dependencies
- `archive_milestone(milestone_id: int) -> Result[None, str]` - Archive milestone
- `verify_path_integrity() -> Result[None, str]` - Check integrity
- `log_path_refactoring(details: dict)` - Record changes

---

## Database Operations

This directive updates the following tables:

- **`milestones`**: Updates `order_index`, archives obsolete milestones
- **`tasks`**: Updates `milestone_id` when reassigning tasks
- **`notes`**: Logs refactoring operations with `note_type = 'path_refactoring'`

---

## Testing

How to verify this directive is working:

1. **Check milestone order**
   ```sql
   SELECT id, name, order_index
   FROM milestones
   WHERE completion_path_id = ?
   ORDER BY order_index;
   ```

2. **Verify no orphaned tasks**
   ```sql
   SELECT t.id, t.name
   FROM tasks t
   LEFT JOIN milestones m ON t.milestone_id = m.id
   WHERE m.id IS NULL;
   ```

3. **Check refactoring logs**
   ```sql
   SELECT content, created_at
   FROM notes
   WHERE note_type = 'path_refactoring'
   ORDER BY created_at DESC;
   ```

---

## Common Mistakes

- ❌ **Delete milestone without moving tasks** - Always reassign tasks first
- ❌ **Reorder without dependency check** - Validate dependencies
- ❌ **No transaction** - Use atomic operations
- ❌ **Archive active milestone** - Check for active tasks first
- ❌ **No integrity verification** - Always verify after refactoring

---

## Roadblocks and Resolutions

### Roadblock 1: path_conflict
**Issue**: Multiple valid reordering options
**Resolution**: Prompt user for reorder approval, show implications of each option

### Roadblock 2: circular_dependency
**Issue**: Proposed reordering creates circular dependencies
**Resolution**: Reject reordering, suggest alternative ordering

### Roadblock 3: active_tasks_in_milestone
**Issue**: Cannot archive milestone with active tasks
**Resolution**: Complete or reassign active tasks before archival

### Roadblock 4: foreign_key_violation
**Issue**: Task references would be orphaned
**Resolution**: Reassign or archive tasks before milestone removal

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#project-refactor-path)
- [Blueprint: Project Directives](../../../docs/blueprints/blueprint_project_directives.md#archival-refactor)
- [JSON Definition](../../../docs/directives-json/directives-project.json)

---

*Part of AIFP v1.0 - Project directive for completion path refactoring*
