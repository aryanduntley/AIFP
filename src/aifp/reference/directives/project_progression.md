# project_progression - Project Progression Directive

**Type**: Project Management
**Level**: 2
**Parent**: `aifp_status`
**Category**: Task Management

---

## Purpose

`project_progression` codifies the incremental milestone/task/items state machine. It determines what work to create next after task or milestone completions, ensuring tasks are created one at a time rather than in bulk.

**What it does**:
- Creates the first task after discovery completes
- Creates the next task after a task completes
- Opens the next milestone after a milestone completes
- Reviews completion path when themes or flows evolve
- Routes to `project_completion_check` when all stages are done

**Key principle**: **ONE task (with items) created at a time per milestone.** Each completion event triggers the next creation. Tasks are never batch-created.

**Use this directive when**:
- `project_discovery` just completed (first task creation)
- A task just completed (next task creation)
- A milestone just completed (next milestone opening)
- `project_evolution` updated themes or flows (completion path review)
- An active milestone has no tasks (gap detected by `aifp_status`)

**DO NOT use when**:
- User explicitly requests ad-hoc task decomposition (use `project_task_decomposition`)
- Project is not yet initialized or discovery not complete
- No milestones exist (route to `project_discovery` first)

---

## When to Use

### Automatic Trigger

`aifp_status` routes here when `progression_action_needed = true`:
- Task or milestone just completed
- Active milestone has no tasks
- Discovery just completed

`project_evolution` routes here when `themes_or_flows_changed = true`.

### Manual Trigger

Keywords: "next task", "what's next", "continue work", "next milestone", "progress", "advance"

---

## Workflow

### Trunk: `assess_progression_state`

Determine which progression action is needed by reading current project state:
- Is there a recently completed task? → Branch 2
- Is there a recently completed milestone? → Branch 3
- Did discovery just complete? → Branch 1
- Does the active milestone have no tasks? → Branch 4
- Did themes/flows just evolve? → Branch 5

---

### Branch 1: Create First Milestone Task (after discovery)

**Condition**: `project_discovery` just completed. First milestone is `in_progress` but has no tasks.

**Steps**:
1. Identify the first milestone (first `in_progress` milestone of first stage)
2. Review milestone description and acceptance criteria
3. Discuss with user or infer: what is the first concrete task for this milestone?
4. Create **ONE** task with items via `project_task_create` and `project_item_create` helpers
5. This is the entry point from discovery into active development work

**Note**: Only one task created. Subsequent tasks created after this one completes.

---

### Branch 2: Evaluate and Create Next Task (after task completion)

**Condition**: A task just completed within the active milestone.

**Steps**:
1. Review active milestone scope, description, and acceptance criteria
2. Review what was just completed (context from the completed task and its items)
3. Review current themes and flows for organizational context
4. Assess: is there more work needed for this milestone?
5. **If yes**: Create **ONE** new task with items for the active milestone
6. **If no** (milestone work is fully covered): Do NOT create more tasks. The existing completion events (`project_task_complete` → `project_milestone_complete`) handle milestone closure.
7. Log progression decision in notes

**Key principle**: Create ONE task at a time. Never batch-create all remaining tasks for a milestone. The AI should think about what the next logical piece of work is, not plan out every remaining task.

---

### Branch 3: Open Next Milestone (after milestone completion)

**Condition**: All tasks in a milestone are complete. `project_milestone_complete` has marked the milestone done.

**Steps**:
1. Identify next milestone in current completion path stage (by `order_index`)
2. **If next milestone exists in current stage**:
   - Set its status to `in_progress` via `update_milestone_status` helper
   - Create **first** task (with items) for the newly opened milestone
3. **If no more milestones in current stage**:
   - Check if more stages exist in completion path
   - If next stage exists: set first milestone of next stage to `in_progress`, create first task
4. **If no more stages**:
   - Route to `project_completion_check` (project may be complete)
5. Log milestone transition in notes

**Helpers**: `update_milestone_status`, `create_task`, `create_item`

---

### Branch 4: Create First Task for Milestone (gap fill)

**Condition**: An active milestone has zero tasks. This can happen when:
- A milestone was just opened but progression didn't fire
- Tasks were cleared or deleted
- Manual milestone activation

**Steps**:
1. Review milestone description and acceptance criteria
2. Discuss with user or infer first task
3. Create ONE task with items

---

### Branch 5: Review Completion Path (after evolution)

**Condition**: `project_evolution` has updated themes or flows. The completion path may need adjustment.

**Steps**:
1. Review current completion path stages against the new project shape
2. Assess: do existing milestones still make sense with evolved themes/flows?
3. Assess: does the completion path need new stages or modified stages?
4. **If changes needed**:
   - Add or modify milestones as appropriate
   - Potentially add completion path stages
   - Update blueprint via `project_blueprint_update`
   - Log evolution impact in notes
5. **If no changes needed**:
   - Log: "Evolution reviewed, no completion path changes required"

**Note**: This is a **thoughtful review**, not automatic restructuring. AI should consider whether changes are actually necessary before making them. Not every theme/flow change requires path adjustments.

---

### Fallback: Route to Status

No progression action needed at this time. Return to `aifp_status`.

---

## Interactions with Other Directives

### Called By

- **`aifp_status`** — Routes here when progression action is needed (priority 85)
- **`project_evolution`** — Routes here when themes/flows changed (priority 90)

### Calls

- **Helpers**: `create_task`, `create_item`, `update_milestone_status`, `get_project_status`, `project_notes_log`, `project_blueprint_update`

### Flows To

- **`aifp_status`** — After progression action is taken
- **`project_completion_check`** — When all stages are exhausted

### Related

- **`project_task_complete`** — Triggers progression (task done → next task)
- **`project_milestone_complete`** — Triggers progression (milestone done → next milestone)
- **`project_task_decomposition`** — Separate directive for explicit user-requested decomposition (not replaced by progression)
- **`project_discovery`** — Predecessor for first-time progression

---

## The Incremental State Machine

```
discovery completes
  → progression creates FIRST task for first milestone
    → user works on task
      → task completes
        → progression creates NEXT task for milestone
          → ... repeat until milestone covered ...
            → milestone completes
              → progression opens NEXT milestone, creates first task
                → ... repeat until stage covered ...
                  → stage completes
                    → progression opens next stage's first milestone
                      → ... repeat until all stages done ...
                        → route to project_completion_check
```

At any point, `project_evolution` can trigger a path review:
```
themes/flows evolve
  → progression reviews completion path
    → adjusts milestones/stages if needed
      → continues normal flow
```

---

## Edge Cases

### Case 1: Unclear Next Task

**Response**: Ask user what they want to work on next within the current milestone scope. Do not guess. Present the milestone's acceptance criteria and ask what's the next logical step.

### Case 2: Milestone Scope Exhausted but Criteria Not Met

The milestone's acceptance criteria haven't been met, but AI can't identify more tasks.

**Response**: Review milestone acceptance criteria with user. Either:
- Add tasks to meet the criteria
- Revise the criteria (via `project_evolution`)

### Case 3: Evolution Invalidates Milestones

Theme/flow changes make existing milestones irrelevant.

**Response**: Discuss with user: update existing milestones or create new ones? Never silently restructure the project's roadmap.

### Case 4: No Milestones Exist

**Response**: Route to `project_discovery` to define milestones. Progression requires milestones to operate.

### Case 5: All Stages Complete Unexpectedly

**Response**: Route to `project_completion_check`. If completion check fails (gaps found), create missing work via new milestones.

---

## Database Operations

**Read Operations**:
- Completion path table (stages, order)
- Milestones table (status, order_index, acceptance criteria)
- Tasks table (active tasks, recently completed)
- Items table (task items)
- Themes/flows tables (for context)

**Write Operations**:
- Tasks table (new task creation)
- Items table (new item creation)
- Milestones table (status updates)
- Completion path table (stage updates, if evolution triggers changes)
- Notes table (progression decisions)

---

## FP Compliance

**Purity**: ⚠️ Effect function — writes to database
**Immutability**: ✅ State read from DB, decisions made from immutable snapshots
**Side Effects**: ⚠️ Explicit — all DB writes via helpers

---

## Best Practices

1. **One task at a time** — Never batch-create tasks for a milestone
2. **Context-aware creation** — Use the just-completed task as context for the next one
3. **Respect acceptance criteria** — Milestones are done when criteria are met, not when tasks run out
4. **Ask when uncertain** — If AI can't determine the next task, ask the user
5. **Log decisions** — Every progression decision should be noted for audit trail
6. **Evolution review is thoughtful** — Don't restructure the path on every minor change

---

## Version History

- **v1.0** (2026-01-30): Initial creation — formalizes the incremental milestone/task state machine

---

## Notes

- `project_task_decomposition` still exists for explicit user-requested decomposition
- Progression handles the "what's next" flow; decomposition handles "break this down"
- The state machine is driven by completion events routed through `aifp_status`
- Themes and flows evolving is a trigger for review, not automatic restructuring
