# Directive: project_auto_summary

**Type**: Project
**Level**: 4 (Metrics & Reporting)
**Parent Directive**: project_metrics
**Priority**: MEDIUM - Context awareness

---

## Purpose

The `project_auto_summary` directive generates human-readable summaries of project purpose, progress, and open tasks, stored in notes or output to the terminal. This directive provides **automated status reporting**, giving both AI and users quick, comprehensive overviews of project state.

Auto-summary provides **context awareness**, enabling:
- **Quick Status Overview**: Project state at a glance
- **Progress Tracking**: Completion percentages and milestones
- **Open Work Identification**: What needs attention now
- **Historical Context**: Recent accomplishments and changes
- **AI Context Loading**: Help AI understand project quickly

This directive acts as a **project narrator** providing concise, actionable project summaries.

---

## When to Apply

This directive applies when:
- **Session start** - Provide context when AI starts working
- **User requests status** - Generate current state summary
- **After major changes** - Summarize impact of changes
- **Periodic reporting** - Scheduled status updates
- **Context loss** - Help AI regain project understanding
- **Called by other directives**:
  - `aifp_status` - Includes summary in status report
  - `project_evolution` - Summarize after pivot
  - `project_completion_check` - Summary of completion state
  - Works with `project_metrics` - Includes metrics in summary

---

## Workflow

### Trunk: gather_project_context

Collects all necessary information for summary.

**Steps**:
1. **Query project metadata** - Name, purpose, version
2. **Query completion state** - Milestones, tasks, progress
3. **Query recent activity** - Recent changes and completions
4. **Route to appropriate branch** - Based on available data

### Branches

**Branch 1: If active_tasks_found**
- **Then**: `summarize_by_path`
- **Details**: Generate summary focused on active work
  - Get current focus (sidequest > subtask > task)
  - List open items with priority
  - Show recent completions
  - Calculate completion percentage
  - Estimate remaining work
  - Include project goals
  - Format for readability
  - Store in notes
  - Output to terminal
- **Result**: Active work summary generated

**Branch 2: If completed_milestones**
- **Then**: `log_completion_summary`
- **Details**: Summarize completed work
  - List completed milestones
  - Show milestone completion dates
  - Count completed tasks
  - Highlight achievements
  - Show remaining milestones
  - Calculate overall progress
  - Format for readability
  - Store in notes
- **Result**: Completion summary generated

**Branch 3: If project_idle**
- **Then**: `idle_summary`
- **Details**: Summary for idle project
  - Show project purpose
  - Show completion state
  - Suggest next actions
  - List potential next milestones
  - Show last activity date
  - Format for readability
  - Store in notes
- **Result**: Idle state summary

**Branch 4: If recent_evolution**
- **Then**: `evolution_summary`
- **Details**: Summarize project changes
  - Show previous vs current state
  - List major changes
  - Show version progression
  - Impact on completion path
  - New goals or architecture
  - Format for readability
  - Store in notes
- **Result**: Evolution summary

**Fallback**: `prompt_user`
- **Details**: Insufficient data for summary
  - Ask user for additional context
  - Suggest project initialization
  - Log issue in notes
- **Result**: User provides context

---

## Examples

### ✅ Compliant Usage

**Generate Active Work Summary (Compliant):**

```python
def generate_active_work_summary() -> Result[str, str]:
    """Generate summary focused on current active work.

    Returns:
        Ok with formatted summary or Err if generation failed
    """
    return pipe(
        get_project_metadata,
        lambda metadata: get_current_focus(),
        lambda focus: get_open_items(focus),
        lambda items: get_recent_completions(),
        lambda completions: calculate_progress(),
        lambda progress: format_active_summary(
            metadata, focus, items, completions, progress
        ),
        lambda summary: store_summary(summary, "active_work"),
        lambda summary: Ok(summary)
    ).or_else(lambda err: Err(f"Summary generation failed: {err}"))

# ✅ Complete data gathering
# ✅ Pure pipeline
# ✅ Formatted output
# ✅ Persisted
```

**Why Compliant**:
- Complete context
- Functional pipeline
- Proper formatting
- Stored for reference

---

**Format Summary for Display (Compliant):**

```python
def format_active_summary(
    metadata: dict,
    focus: Focus,
    items: list[WorkItem],
    completions: list[Completion],
    progress: Progress
) -> str:
    """Format active work summary for display.

    Args:
        metadata: Project metadata
        focus: Current focus (task/subtask/sidequest)
        items: Open work items
        completions: Recent completions
        progress: Completion progress

    Returns:
        Formatted summary string
    """
    summary_lines = [
        f"# Project: {metadata['name']} (v{metadata['version']})",
        f"",
        f"## Purpose",
        f"{metadata['purpose']}",
        f"",
        f"## Current Focus",
        f"{focus.type}: {focus.name}",
        f"Status: {focus.status}",
        f"Priority: {focus.priority}",
        f"",
        f"## Open Items ({len(items)})",
    ]

    # Add open items
    for item in items[:5]:  # Top 5
        summary_lines.append(f"- [ ] {item.name} (Priority: {item.priority})")

    summary_lines.extend([
        f"",
        f"## Recent Completions ({len(completions)})",
    ])

    # Add recent completions
    for completion in completions[:3]:  # Last 3
        summary_lines.append(f"- [x] {completion.name} ({completion.completed_at})")

    summary_lines.extend([
        f"",
        f"## Progress",
        f"Overall: {progress.percentage}%",
        f"Milestones: {progress.completed_milestones}/{progress.total_milestones}",
        f"Tasks: {progress.completed_tasks}/{progress.total_tasks}",
        f"",
        f"---",
        f"Generated: {timestamp()}"
    ])

    return "\n".join(summary_lines)

# ✅ Pure function
# ✅ Clear structure
# ✅ Readable format
# ✅ Complete information
```

**Why Compliant**:
- Pure function
- Clear formatting
- Readable output
- Complete summary

---

**Store Summary for Reference (Compliant):**

```python
def store_summary(summary: str, summary_type: str) -> str:
    """Store summary in notes for future reference.

    Args:
        summary: Formatted summary text
        summary_type: Type of summary (active_work, completion, etc.)

    Returns:
        Same summary text
    """
    insert_note(
        content=summary,
        note_type="auto_summary",
        source="directive",
        severity="info",
        metadata={
            "summary_type": summary_type,
            "generated_at": timestamp()
        }
    )

    return summary

# ✅ Persists summary
# ✅ Typed appropriately
# ✅ Includes metadata
# ✅ Returns unchanged
```

**Why Compliant**:
- Proper persistence
- Metadata included
- Returns input (pure)
- Audit trail

---

### ❌ Non-Compliant Code

**Generate Summary Without Context (Violation):**

```python
# ❌ VIOLATION: Summary without project context
def quick_summary():
    summary = "Project Status: Working"
    print(summary)

# Problem:
# - No project metadata
# - No actual status information
# - Not helpful
# - No persistence
# - Useless summary
```

**Why Non-Compliant**:
- No real information
- Not helpful
- No context
- Not stored

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Complete contextual summary
def generate_complete_summary() -> Result[str, str]:
    """Generate complete project summary with context.

    Returns:
        Ok with detailed summary or Err if failed
    """
    return pipe(
        load_project_context,
        lambda ctx: gather_progress_data(ctx),
        lambda data: format_detailed_summary(data),
        lambda summary: store_and_display(summary),
        lambda summary: Ok(summary)
    ).or_else(lambda err: Err(f"Summary failed: {err}"))

# Complete context
# Detailed information
# Proper formatting
# Stored and displayed
```

---

**Mutating Data During Summary (Violation):**

```python
# ❌ VIOLATION: Mutating project data during summary
def bad_summary(project_data):
    # Mutating data while summarizing
    project_data["last_summarized"] = datetime.now()
    project_data["summary_count"] += 1

    return f"Summary: {project_data['name']}"

# Problem:
# - Mutates input data
# - Side effect during read operation
# - Not pure
# - Summary shouldn't modify state
```

**Why Non-Compliant**:
- Mutates input
- Side effects
- Not pure
- Violates FP principles

**Refactored (Compliant):**

```python
# ✅ REFACTORED: Pure summary generation
def generate_pure_summary(project_data: dict) -> tuple[str, dict]:
    """Generate summary without mutating input.

    Args:
        project_data: Project metadata

    Returns:
        Tuple of (summary, updated_metadata)
    """
    summary = format_summary(project_data)

    updated_metadata = {
        **project_data,
        "last_summarized": timestamp(),
        "summary_count": project_data.get("summary_count", 0) + 1
    }

    return (summary, updated_metadata)

# ✅ Pure function
# ✅ No mutation
# ✅ Returns new state
# ✅ Original unchanged
```

---

## Edge Cases

### Edge Case 1: No Active Tasks

**Issue**: Project has no open tasks

**Handling**:
```python
def handle_idle_project() -> Result[str, str]:
    """Generate summary for project with no active tasks.

    Returns:
        Ok with idle project summary or Err if failed
    """
    return pipe(
        get_project_metadata,
        lambda meta: get_last_activity_date(),
        lambda last_activity: suggest_next_actions(),
        lambda suggestions: format_idle_summary(
            meta, last_activity, suggestions
        ),
        lambda summary: Ok(summary)
    )

# Handle idle state appropriately
```

**Directive Action**: Provide idle project summary with suggestions.

---

### Edge Case 2: New Project

**Issue**: Project just initialized, no history

**Handling**:
```python
def handle_new_project() -> Result[str, str]:
    """Generate summary for newly initialized project.

    Returns:
        Ok with new project summary or Err if failed
    """
    return pipe(
        get_project_metadata,
        lambda meta: get_project_goals(meta),
        lambda goals: get_initial_milestones(),
        lambda milestones: format_new_project_summary(
            meta, goals, milestones
        ),
        lambda summary: Ok(summary)
    )

# Show project setup and initial roadmap
```

**Directive Action**: Focus summary on goals and initial roadmap.

---

## Related Directives

- **Depends On**:
  - `project_metrics` - Uses metrics in summary
  - `project_blueprint_read` - Reads project context
- **Triggers**:
  - None
- **Called By**:
  - `aifp_status` - Includes summary in status
  - `project_evolution` - After major changes
  - `project_completion_check` - Completion summaries
- **Escalates To**:
  - `project_user_referral` - If summary generation fails

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive queries the following tables:

- **`project`**: Project metadata
- **`milestones`**: Milestone status
- **`tasks`**: Task status
- **`subtasks`**: Subtask status
- **`sidequests`**: Sidequest status
- **`notes`**: Recent activity

This directive updates:

- **`notes`**: Stores summary with `note_type = 'auto_summary'`

---

## Testing

How to verify this directive is working:

1. **Generate summary**
   ```python
   summary = generate_active_work_summary()
   assert summary.is_ok()
   assert len(summary.unwrap()) > 0
   ```

2. **Check summary stored**
   ```sql
   SELECT content, created_at
   FROM notes
   WHERE note_type = 'auto_summary'
   ORDER BY created_at DESC
   LIMIT 1;
   ```

3. **Verify summary content**
   ```python
   # Should include project name, progress, open tasks
   assert "Project:" in summary
   assert "Progress:" in summary
   ```

---

## Common Mistakes

- ❌ **Summary without context** - Include project metadata
- ❌ **No progress information** - Show completion percentages
- ❌ **Not storing summary** - Persist for future reference
- ❌ **Mutating data during summary** - Pure functions only
- ❌ **Unreadable format** - Use clear, structured format

---

## Roadblocks and Resolutions

### Roadblock 1: summary_generation_failed
**Issue**: Cannot generate summary due to missing data
**Resolution**: Retry summary with fallback data sources or prompt user for context

### Roadblock 2: no_active_work
**Issue**: Project has no open tasks or milestones
**Resolution**: Generate idle project summary with suggestions for next actions

### Roadblock 3: insufficient_context
**Issue**: Project data incomplete for meaningful summary
**Resolution**: Use available data and note limitations in summary

### Roadblock 4: new_project_no_history
**Issue**: Newly initialized project with no activity
**Resolution**: Focus summary on goals, milestones, and initial roadmap

---

## References

None
---

*Part of AIFP v1.0 - Project directive for automated status summaries*
