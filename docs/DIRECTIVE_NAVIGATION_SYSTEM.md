# Directive Navigation System: Status-Driven Decision Tree

**Version**: 1.0
**Last Updated**: 2025-01-15
**Status**: Design Document

---

## Table of Contents

1. [Overview](#overview)
2. [The Problem We're Solving](#the-problem-were-solving)
3. [Core Architecture](#core-architecture)
4. [The Hub Pattern: aifp_status](#the-hub-pattern-aifp_status)
5. [The directive_flow Table](#the-directive_flow-table)
6. [Decision Tree Flow](#decision-tree-flow)
7. [Helper Functions](#helper-functions)
8. [Loop-Back Pattern](#loop-back-pattern)
9. [Comparison: directive_flow vs directives_interactions](#comparison-directive_flow-vs-directives_interactions)
10. [Implementation Plan](#implementation-plan)
11. [Examples](#examples)

---

## Overview

The Directive Navigation System provides AI with a **state-driven decision tree** for project management workflows. Instead of requiring AI to infer "what comes next?" from relationship data, the system explicitly maps possible next steps based on current project state.

### Key Principles

1. **Status as Hub**: Every workflow cycle starts with `aifp_status`, which provides comprehensive state
2. **Many-to-Many Branching**: Any directive can have multiple valid next steps
3. **State-Driven Decisions**: Next steps are determined by evaluating current state conditions
4. **Loop-Back Architecture**: All directives return to status after completion
5. **Zero Inference**: AI receives explicit list of possible next directives with conditions

---

## The Problem We're Solving

### The Cognitive Load Problem

Without explicit navigation, AI must:

1. **Infer sequences** from relationship data
2. **Guess priorities** when multiple relationships exist
3. **Mentally construct** the "next step" from abstract relationship types
4. **Remember context** about where it is in the workflow
5. **Determine** if a relationship means "next step," "dependency," or "exception"

This creates:
- Inconsistent workflow execution
- Difficulty determining "where am I?"
- Ambiguity about valid next steps
- Risk of choosing wrong directive
- Cognitive overhead for AI

### What We Need Instead

**Clear answers to:**
- "What are my options from here?"
- "Which conditions determine which path?"
- "What's the canonical next step?"
- "Where do I go after completing this action?"

**Without requiring AI to:**
- Construct workflows mentally
- Infer meaning from relationship types
- Guess at sequences
- Remember implicit rules

---

## Core Architecture

### The Three Components

```
┌─────────────────────────────────────────────────────────────┐
│                     1. aifp_status                          │
│           (Comprehensive State Orchestrator)                │
│  - Queries all project state                                │
│  - Returns structured status object                         │
│  - Suggests next directives based on state                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   2. directive_flow                         │
│              (State-to-Directive Mapping)                   │
│  - Maps states to possible next directives                  │
│  - Defines conditions for each transition                   │
│  - Provides priorities and descriptions                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   3. Helper Functions                       │
│            (Query and Evaluation Layer)                     │
│  - Query possible next directives                           │
│  - Evaluate conditions against current state                │
│  - Return filtered, prioritized options                     │
└─────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

**1. Status as Single Source of Truth**
- One function (`aifp_status`) gathers ALL relevant state
- Reduces queries: AI calls status once, gets everything
- Consistency: Same state representation every time
- Cacheable: Status can be memoized within a session

**2. Declarative Flow Mapping**
- Flow definitions are data, not code
- Easy to visualize and modify
- Can be queried, analyzed, validated
- Future-proof: Can generate flow diagrams automatically

**3. Separation of Concerns**
- **Status**: Knows about project state
- **Flow**: Knows about valid transitions
- **Helpers**: Knows how to query and filter
- **AI**: Focuses on decision-making with filtered options

---

## The Hub Pattern: aifp_status

### Why Status is Central

In project management, **you can't know what to do next without knowing where you are**. The hub pattern makes status checking **explicit and comprehensive** rather than scattered across multiple queries.

### What aifp_status Returns

```json
{
  "project": {
    "initialized": true | false,
    "name": "string",
    "status": "planning" | "in_progress" | "completed",
    "blueprint_path": "string",
    "blueprint_needs_sync": true | false
  },

  "user_custom": {
    "exists": true | false
  },

  "infrastructure": [
    {"type": "language|package|tool", "value": "string"}
  ],

  "completion_path": {
    "current": {
      "id": number,
      "name": "string",
      "status": "pending|in_progress|completed",
      "order_index": number,
      "all_milestones_complete": true | false
    },
    "next_pending": {
      "id": number,
      "name": "string"
    } | null
  },

  "milestone": {
    "current": {
      "id": number,
      "name": "string",
      "status": "pending|in_progress|completed",
      "all_tasks_complete": true | false,
      "has_tasks": true | false
    } | null,
    "has_incomplete": true | false
  },

  "task": {
    "current": {
      "id": number,
      "name": "string",
      "status": "pending|in_progress|completed",
      "priority": "low|medium|high|critical",
      "all_items_complete": true | false,
      "has_items": true | false
    } | null,
    "has_incomplete_items": true | false,
    "next_pending": {
      "id": number,
      "name": "string"
    } | null
  },

  "items": {
    "current": {
      "id": number,
      "content": "string",
      "status": "pending|in_progress|completed",
      "for_table": "tasks|subtasks|sidequests"
    } | null,
    "next_pending": {
      "id": number,
      "content": "string"
    } | null
  },

  "context": {
    "recent_completed": [
      {
        "id": number,
        "content": "string",
        "completed_at": "ISO timestamp",
        "for_table": "tasks|subtasks|sidequests"
      }
    ],
    "files_in_scope": [
      {
        "id": number,
        "name": "string",
        "path": "string",
        "language": "string"
      }
    ]
  },

  "suggested_next_directives": [
    {
      "directive": "string",
      "reason": "string",
      "priority": number,
      "condition_matches": true
    }
  ]
}
```

### Why This Structure?

**Hierarchical Organization**
- Mirrors the project structure (path → milestone → task → item)
- Shows "where am I?" at each level
- Includes completion flags for decision-making

**Context for Decisions**
- Recent completed items show progress
- Files in scope show current work area
- Infrastructure shows technical constraints

**Suggested Next Directives**
- Pre-computed suggestions reduce AI overhead
- Includes reasoning for transparency
- AI can accept suggestions or explore alternatives

### What aifp_status Queries Internally

```python
def aifp_status():
    # 1. Project metadata
    project = get_project()

    # 2. Blueprint sync check
    blueprint_changed = blueprint_has_changed()

    # 3. User custom directives existence
    user_custom_exists = check_user_directives_db_exists()

    # 4. Infrastructure
    infrastructure = get_from_project_where("infrastructure", {}, None, None)

    # 5. Current completion path
    current_path = get_from_project_where(
        "completion_path",
        {"status": "in_progress"},
        1,
        "order_index ASC"
    )

    # 6. Check if all milestones complete for current path
    if current_path:
        milestones = get_milestones_by_path(current_path['id'])
        all_complete = all(m['status'] == 'completed' for m in milestones)

    # 7. Current milestone
    current_milestone = get_from_project_where(
        "milestones",
        {"status": "in_progress"},
        1,
        None
    )

    # 8. Check if milestone has tasks
    if current_milestone:
        tasks = get_tasks_by_milestone(current_milestone['id'])
        all_tasks_complete = all(t['status'] == 'completed' for t in tasks)

    # 9. Current task
    current_task = get_from_project_where(
        "tasks",
        {"status": "in_progress"},
        1,
        "priority DESC, created_at ASC"
    )

    # 10. Current and next task items
    if current_task:
        current_item = get_from_project_where(
            "items",
            {"for_id": current_task['id'], "for_table": "tasks", "status": "in_progress"},
            1,
            None
        )
        next_item = get_from_project_where(
            "items",
            {"for_id": current_task['id'], "for_table": "tasks", "status": "pending"},
            1,
            "created_at ASC"
        )

    # 11. Recent completed items for context
    recent_completed = get_from_project_where(
        "items",
        {"status": "completed"},
        5,
        "updated_at DESC"
    )

    # 12. Files related to current task
    if current_task:
        flow_ids = get_task_flows(current_task['id'])
        file_ids = get_file_ids_from_flows(flow_ids)
        files = get_from_project("files", file_ids)

    # 13. Next pending entities
    next_milestone = get_from_project_where("milestones", {"status": "pending"}, 1, "created_at ASC")
    next_task = get_from_project_where("tasks", {"status": "pending"}, 1, "priority DESC, created_at ASC")

    # 14. Build status object
    status = {
        "project": {...},
        "completion_path": {...},
        "milestone": {...},
        "task": {...},
        "items": {...},
        "context": {...}
    }

    # 15. Generate suggested next directives
    status["suggested_next_directives"] = generate_suggestions(status)

    return status
```

### Why This Level of Detail?

**Completeness**: AI has everything needed to decide without additional queries

**Performance**: One comprehensive query is faster than many small queries

**Consistency**: Same state view throughout decision process

**Debuggability**: Can log full status for troubleshooting

**Self-Documenting**: Status object itself explains current state

---

## The directive_flow Table

### Schema

```sql
CREATE TABLE IF NOT EXISTS directive_flow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_directive TEXT NOT NULL,
    to_directive TEXT NOT NULL,

    -- Flow classification
    flow_type TEXT CHECK (flow_type IN (
        'status_branch',    -- Branch from status based on state
        'completion_loop',  -- Return to status after completing action
        'conditional',      -- Conditional next step during work
        'error'            -- Error handling path
    )) NOT NULL DEFAULT 'conditional',

    -- Condition for this transition
    condition_key TEXT,              -- e.g., "project.initialized", "task.has_items"
    condition_value TEXT,            -- e.g., "false", "true", "exists"
    condition_description TEXT,      -- Human readable: "if project not initialized"

    priority INTEGER DEFAULT 0,      -- Higher = preferred when multiple match
    description TEXT,                -- Why this transition exists

    FOREIGN KEY (from_directive) REFERENCES directives(name),
    FOREIGN KEY (to_directive) REFERENCES directives(name)
);

CREATE INDEX idx_directive_flow_from ON directive_flow(from_directive);
CREATE INDEX idx_directive_flow_type ON directive_flow(flow_type);
```

### Why This Design?

**1. from_directive / to_directive**
- **What**: Simple edge representation (A → B)
- **Why**: Dead simple to query "what comes after X?"
- **Many-to-Many**: Multiple rows with same `from_directive` = branching

**2. flow_type**
- **What**: Categorizes the type of transition
- **Why**: Different types have different semantics
  - `status_branch`: Primary decision point from status
  - `completion_loop`: Always return to status
  - `conditional`: Context-dependent work transitions
  - `error`: Exception handling

**3. condition_key / condition_value**
- **What**: JSONPath-like key and expected value
- **Why**:
  - Allows programmatic condition evaluation
  - Can be queried and filtered
  - Self-documenting (key shows what's being checked)

**4. condition_description**
- **What**: Human-readable condition explanation
- **Why**:
  - AI can read and understand intent
  - Documentation embedded in data
  - Helps during manual review

**5. priority**
- **What**: Integer for sorting when multiple conditions match
- **Why**:
  - Handles ambiguous states
  - Provides canonical "preferred" path
  - AI can still choose lower priority if justified

### Flow Type Semantics

**status_branch**
```sql
-- From status to next directive based on project state
('aifp_status', 'project_init', 'status_branch', 'project.initialized', 'false', ...)
```
- Used exclusively from `aifp_status`
- Represents primary decision points
- Conditions evaluated against status object
- Multiple branches possible

**completion_loop**
```sql
-- Return to status after completing work
('project_file_write', 'aifp_status', 'completion_loop', NULL, NULL, ...)
```
- Used from work directives back to status
- Usually no conditions (always loop back)
- Closes the loop for continuous workflow
- Ensures state is re-evaluated after changes

**conditional**
```sql
-- Context-dependent work transitions
('task_item_work', 'project_file_write', 'conditional', 'item.requires', 'file_creation', ...)
```
- Used during actual work execution
- Depends on current work context
- May have multiple options
- AI chooses based on task requirements

**error**
```sql
-- Exception handling paths
('project_file_write', 'fp_error_recovery', 'error', NULL, NULL, ...)
```
- Fallback when directive fails
- Error recovery paths
- Escalation routes

---

## Decision Tree Flow

### The Complete Cycle

```
┌──────────────┐
│   aifp_run   │ Entry point
└──────┬───────┘
       ↓
┌──────────────────────────────────────────────────────────┐
│                     aifp_status                          │
│  1. Query comprehensive project state                    │
│  2. Evaluate completion path / milestone / task state    │
│  3. Check for pending work items                         │
│  4. Get context (recent completed, files in scope)       │
│  5. Generate suggested next directives                   │
└──────┬───────────────────────────────────────────────────┘
       ↓
       ↓ Query directive_flow for status_branch flows
       ↓
┌──────────────────────────────────────────────────────────┐
│              Possible Next Directives                    │
│                                                          │
│  Based on state conditions:                              │
│                                                          │
│  IF project.initialized = false                          │
│    → project_init (priority: 100)                        │
│                                                          │
│  IF completion_path.current.all_milestones_complete      │
│    → completion_path_complete (priority: 100)            │
│                                                          │
│  IF milestone.current.all_tasks_complete                 │
│    → milestone_complete (priority: 85)                   │
│                                                          │
│  IF task.current.all_items_complete                      │
│    → task_complete (priority: 70)                        │
│                                                          │
│  IF items.current exists AND status = in_progress        │
│    → task_item_work (priority: 45)                       │
│                                                          │
│  IF task.has_items = false                               │
│    → task_item_create (priority: 50)                     │
│                                                          │
│  ... (multiple branches possible)                        │
└──────┬───────────────────────────────────────────────────┘
       ↓
       ↓ AI evaluates conditions, context, and chooses
       ↓
┌──────────────────────────────────────────────────────────┐
│              Execute Chosen Directive                    │
│                                                          │
│  Example: task_item_work                                 │
│    ↓                                                     │
│    Query conditional flows                               │
│    ↓                                                     │
│    IF item requires file creation                        │
│      → project_file_write                                │
│    IF item requires function creation                    │
│      → project_function_create                           │
│    ↓                                                     │
│    Execute chosen work directive                         │
└──────┬───────────────────────────────────────────────────┘
       ↓
       ↓ Work completed
       ↓
┌──────────────────────────────────────────────────────────┐
│               Completion Loop Back                       │
│                                                          │
│  Query directive_flow for completion_loop                │
│    → Always returns to aifp_status                       │
│                                                          │
│  Why loop back?                                          │
│  - State has changed (file created, item completed)      │
│  - Need fresh status to determine next step              │
│  - Ensures consistent decision-making                    │
└──────┬───────────────────────────────────────────────────┘
       ↓
       └─────→ Back to aifp_status (cycle repeats)
```

### Why This Pattern?

**1. Always Fresh State**
- Looping through status ensures decisions are based on current state
- Prevents stale state bugs
- No need to manually track "where am I?"

**2. Consistent Decision Point**
- All major decisions go through same logic
- Status evaluation is uniform
- Easier to debug and trace

**3. Clear Completion Semantics**
- Work directives don't need to know "what's next?"
- They just do their job and loop back
- Separation of concerns: work vs. navigation

**4. Handles State Changes**
- After completing item, task might be done
- After completing task, milestone might be done
- Status re-evaluation catches these transitions

**5. Prevents Runaway Loops**
- Can add loop counter in status
- Can detect no-progress cycles
- Easy to add safeguards

---

## Helper Functions

### Core Navigation Helpers

#### `aifp_status()`

**Purpose**: Orchestrator that gathers comprehensive project state and suggests next directives

**Returns**: Complete status object (see structure above)

**Classification**: is_tool=true, is_sub_helper=false

**Internally Calls**:
- `get_project()`
- `blueprint_has_changed()`
- `get_from_project_where()` (multiple times)
- `get_milestones_by_path()`
- `get_tasks_by_milestone()`
- `get_task_flows()`
- `get_file_ids_from_flows()`
- `generate_next_directive_suggestions()` (internal)

**Why This Function?**
- Single call gives complete picture
- Reduces query overhead
- Standardizes state representation
- Can be memoized/cached

---

#### `get_next_directives_from_status(from_directive, status_object)`

**Purpose**: Get all possible next directives with condition evaluation

**Parameters**:
- `from_directive` (String) - Usually 'aifp_status'
- `status_object` (Object) - Status returned from aifp_status()

**Returns**: Array of objects:
```json
[
  {
    "to_directive": "string",
    "flow_type": "status_branch|conditional|...",
    "condition_key": "string",
    "condition_value": "string",
    "condition_description": "string",
    "priority": number,
    "matches": true | false,
    "description": "string"
  }
]
```

**Logic**:
```python
def get_next_directives_from_status(from_directive, status_object):
    # 1. Query all flows from this directive
    flows = query_db("""
        SELECT to_directive, flow_type, condition_key, condition_value,
               condition_description, priority, description
        FROM directive_flow
        WHERE from_directive = ?
        ORDER BY priority DESC
    """, [from_directive])

    # 2. Evaluate each condition
    results = []
    for flow in flows:
        matches = evaluate_condition(
            flow['condition_key'],
            flow['condition_value'],
            status_object
        )

        results.append({
            **flow,
            'matches': matches
        })

    return results
```

**Why This Function?**
- Evaluates conditions against actual state
- Returns both matching and non-matching (for transparency)
- Sorted by priority
- AI can see why each option does/doesn't apply

**Classification**: is_tool=true, is_sub_helper=false

---

#### `get_matching_next_directives(from_directive, status_object)`

**Purpose**: Get ONLY the directives whose conditions match current state

**Parameters**: Same as above

**Returns**: Filtered array with only `matches: true`

**Logic**:
```python
def get_matching_next_directives(from_directive, status_object):
    all_directives = get_next_directives_from_status(from_directive, status_object)
    return [d for d in all_directives if d['matches']]
```

**Why This Function?**
- Convenience wrapper for most common use case
- AI gets only valid options
- Simpler decision-making

**Classification**: is_tool=true, is_sub_helper=false

---

#### `get_completion_loop_target(from_directive)`

**Purpose**: Get where to loop back after completing directive

**Parameters**: `from_directive` (String)

**Returns**: Single directive name (usually 'aifp_status')

**SQL**:
```sql
SELECT to_directive
FROM directive_flow
WHERE from_directive = ? AND flow_type = 'completion_loop'
LIMIT 1;
```

**Why This Function?**
- Work directives need to know where to return
- Explicit loop-back destination
- Enables automatic return to status

**Classification**: is_tool=true, is_sub_helper=false

---

#### `get_conditional_work_paths(from_directive, work_context)`

**Purpose**: Get conditional next steps during work execution

**Parameters**:
- `from_directive` (String) - e.g., 'task_item_work'
- `work_context` (Object) - Current item/task context

**Returns**: Array of conditional work directives

**SQL**:
```sql
SELECT to_directive, condition_description, priority
FROM directive_flow
WHERE from_directive = ? AND flow_type = 'conditional'
ORDER BY priority DESC;
```

**Why This Function?**
- Work items have different requirements
- Need conditional branching during execution
- AI chooses based on what work needs to be done

**Classification**: is_tool=true, is_sub_helper=false

---

#### `evaluate_condition(condition_key, condition_value, status_object)`

**Purpose**: Evaluate a single condition against status object (internal helper)

**Parameters**:
- `condition_key` (String) - JSONPath-like key: "project.initialized"
- `condition_value` (String) - Expected value: "false"
- `status_object` (Object) - Status from aifp_status()

**Returns**: Boolean (condition matches or not)

**Logic**:
```python
def evaluate_condition(condition_key, condition_value, status_object):
    if not condition_key:
        return True  # No condition = always matches

    # Parse key path: "project.initialized" → ["project", "initialized"]
    keys = condition_key.split('.')

    # Navigate status object
    value = status_object
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return False  # Key path doesn't exist

    # Compare value
    if condition_value == 'exists':
        return value is not None
    elif condition_value == 'true':
        return value is True
    elif condition_value == 'false':
        return value is False
    else:
        return str(value) == condition_value
```

**Why This Function?**
- Programmatic condition evaluation
- Consistent logic across all flows
- Handles different value types

**Classification**: is_tool=false, is_sub_helper=true

---

### Helper Function Integration

These functions get added to **docs/helpers/helpers-consolidated-core.md** in a new section:

```markdown
### Directive Navigation (Status-Driven Decision Tree)

**`aifp_status()`**
- **Purpose**: Get comprehensive project state and suggest next directives
- **Returns**: Complete status object with suggestions
- **Classification**: is_tool=true, is_sub_helper=false

**`get_next_directives_from_status(from_directive, status_object)`**
- **Purpose**: Get all possible next directives with condition matching
- **Parameters**: from_directive, status_object
- **Returns**: Array of {to_directive, matches, priority, ...}
- **Classification**: is_tool=true, is_sub_helper=false

**`get_matching_next_directives(from_directive, status_object)`**
- **Purpose**: Get only directives whose conditions match current state
- **Parameters**: from_directive, status_object
- **Returns**: Filtered array with only valid options
- **Classification**: is_tool=true, is_sub_helper=false

**`get_completion_loop_target(from_directive)`**
- **Purpose**: Get where to loop back after completing directive
- **Parameters**: from_directive
- **Returns**: Single directive name (usually 'aifp_status')
- **Classification**: is_tool=true, is_sub_helper=false

**`get_conditional_work_paths(from_directive, work_context)`**
- **Purpose**: Get conditional next steps during work execution
- **Parameters**: from_directive, work_context
- **Returns**: Array of conditional work directives
- **Classification**: is_tool=true, is_sub_helper=false
```

---

## Loop-Back Pattern

### Why Everything Loops to Status

**Traditional Approach (Linear):**
```
init → read_blueprint → extract_themes → extract_flows → create_tasks → [stuck: what now?]
```

**Problem**: After creating tasks, AI must figure out "what's next?" by inferring from context.

**Status-Driven Approach (Loop):**
```
status → init → status → read_blueprint → status → extract_themes → status → ...
```

**Benefit**: After each action, status re-evaluates and provides fresh options.

### The Loop Back Rule

**Every work directive has a completion_loop flow back to aifp_status:**

```sql
INSERT INTO directive_flow (from_directive, to_directive, flow_type, description)
VALUES
  ('project_init', 'aifp_status', 'completion_loop', 'Re-evaluate after initialization'),
  ('project_file_write', 'aifp_status', 'completion_loop', 'Re-evaluate after file write'),
  ('task_complete', 'aifp_status', 'completion_loop', 'Re-evaluate after task completion'),
  ('milestone_complete', 'aifp_status', 'completion_loop', 'Re-evaluate after milestone completion');
```

### Advantages

**1. State Synchronization**
- Status always reflects latest changes
- No risk of acting on stale state
- Decisions based on current reality

**2. Simplifies Work Directives**
- They don't need to know "what comes next?"
- Focus on doing their job well
- Clean separation of concerns

**3. Handles Cascading Completions**
- Complete item → re-check → task might be done
- Complete task → re-check → milestone might be done
- Complete milestone → re-check → path might be done

**4. Error Recovery**
- If work fails, loop back shows updated state
- Status can suggest recovery directives
- No special error handling needed in most cases

**5. Debuggability**
- Can log status at each loop iteration
- Easy to see state progression
- Trace decisions through status snapshots

### Loop Control

To prevent infinite loops:

**1. Track Loop Count**
```python
status['meta'] = {
    'loop_count': 0,
    'last_directive': None,
    'no_progress_count': 0
}
```

**2. Detect No-Progress Loops**
```python
if status['meta']['last_directive'] == chosen_directive:
    status['meta']['no_progress_count'] += 1
    if status['meta']['no_progress_count'] > 3:
        # Escalate or prompt user
        return suggest_directive('project_status_review')
```

**3. Max Loop Protection**
```python
if status['meta']['loop_count'] > 100:
    # Safety limit
    raise Exception("Max loop iterations reached")
```

---

## Comparison: directive_flow vs directives_interactions

### Schema Comparison

**directives_interactions (existing):**
```sql
CREATE TABLE IF NOT EXISTS directives_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_directive_id INTEGER NOT NULL,
    target_directive_id INTEGER NOT NULL,
    interaction_type TEXT CHECK (interaction_type IN (
        'triggers',
        'depends_on',
        'escalates_to',
        'validates_with',
        'orchestrates'
    )) NOT NULL,
    condition_description TEXT,
    priority INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT 1,
    notes TEXT,
    UNIQUE(source_directive_id, target_directive_id, interaction_type),
    FOREIGN KEY (source_directive_id) REFERENCES directives(id),
    FOREIGN KEY (target_directive_id) REFERENCES directives(id)
);
```

**directive_flow (proposed):**
```sql
CREATE TABLE IF NOT EXISTS directive_flow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_directive TEXT NOT NULL,
    to_directive TEXT NOT NULL,
    flow_type TEXT CHECK (flow_type IN (
        'status_branch',
        'completion_loop',
        'conditional',
        'error'
    )) NOT NULL DEFAULT 'conditional',
    condition_key TEXT,
    condition_value TEXT,
    condition_description TEXT,
    priority INTEGER DEFAULT 0,
    description TEXT,
    FOREIGN KEY (from_directive) REFERENCES directives(name),
    FOREIGN KEY (to_directive) REFERENCES directives(name)
);
```

### Semantic Comparison

| Aspect | directives_interactions | directive_flow |
|--------|------------------------|----------------|
| **Purpose** | Describe relationships between directives | Define executable workflow transitions |
| **Semantic** | "X has relationship to Y" | "From X, go to Y" |
| **Ambiguity** | High: "triggers" could mean many things | Low: "next step is Y" is explicit |
| **Executability** | Requires interpretation | Directly queryable for "what's next" |
| **Condition Handling** | Free text description | Structured key/value for evaluation |
| **Flow Types** | Relationship types mix concerns | Clear separation: branch, loop, conditional, error |
| **Query Complexity** | Must infer meaning from interaction_type | Direct: "show me next options" |
| **AI Cognitive Load** | High: must interpret relationships | Low: get explicit list of options |

### Detailed Analysis

#### directives_interactions Limitations

**1. Semantic Ambiguity**

```sql
-- What does "triggers" mean?
source: 'project_init', target: 'blueprint_read', type: 'triggers'

-- Is this:
- "After project_init, ALWAYS do blueprint_read"?
- "project_init CAN trigger blueprint_read"?
- "project_init SOMETIMES triggers blueprint_read"?
```

AI must guess the semantics.

**2. No Clear "Next Step" Semantics**

```sql
-- Multiple interactions from same source
source: 'aifp_status', target: 'project_init', type: 'triggers'
source: 'aifp_status', target: 'task_start', type: 'triggers'
source: 'aifp_status', target: 'milestone_create', type: 'triggers'

-- Question: Which one is the NEXT step?
-- Answer: Unclear. AI must infer from context.
```

**3. Condition Evaluation Difficult**

```sql
condition_description: "if project not initialized"
```

- Free text, not programmatically evaluable
- AI must parse and interpret
- No standardized condition checking
- Prone to misinterpretation

**4. Mixed Concerns**

```sql
-- These are fundamentally different concepts:
type: 'triggers'       -- Sequential: A then B
type: 'depends_on'     -- Prerequisite: B needs A first
type: 'escalates_to'   -- Error handling: A fails, go to B
type: 'validates_with' -- Composition: A uses B
type: 'orchestrates'   -- Hierarchy: A manages B
```

Mixing navigation, dependencies, and orchestration in one table creates confusion.

**5. No Loop-Back Pattern**

- No explicit "return to status" concept
- Work directives don't know where to go after completion
- Must be hardcoded in directive logic

#### directive_flow Advantages

**1. Execution Clarity**

```sql
-- Explicit: "From aifp_status, if project.initialized=false, go to project_init"
from: 'aifp_status', to: 'project_init', type: 'status_branch',
condition_key: 'project.initialized', condition_value: 'false'
```

No interpretation needed. Direct instruction.

**2. Structured Conditions**

```sql
condition_key: 'project.initialized'
condition_value: 'false'
```

- Programmatically evaluable
- Can be queried and filtered
- Consistent evaluation logic
- No parsing required

**3. Clear Flow Types**

```sql
-- Different tables or at least clear semantic separation:
type: 'status_branch'    -- From status, choose next based on state
type: 'completion_loop'  -- Work done, return to status
type: 'conditional'      -- During work, choose action based on context
type: 'error'           -- Fallback path
```

Each type has clear, distinct meaning.

**4. Built-in Loop Pattern**

```sql
-- Explicit loop back to status
from: 'project_file_write', to: 'aifp_status', type: 'completion_loop'
```

Every work directive knows to return to status.

**5. Priority Handling**

```sql
-- When multiple conditions match, priority determines preference
priority: 100  -- High priority (do this first)
priority: 50   -- Lower priority (do if higher not applicable)
```

Clear disambiguation when multiple paths are valid.

### Are They Complementary or Redundant?

#### Argument for Complementary

**directives_interactions** could represent:
- **Logical relationships**: "A depends on B being executed first"
- **Validation chains**: "A must be validated by B"
- **Orchestration hierarchy**: "A orchestrates B, C, D"

**directive_flow** represents:
- **Executable workflow**: "From A, the next step is B"
- **Decision trees**: "From status, go to X if condition Y"
- **Loop patterns**: "After completing A, return to status"

**Complementary Use Case:**
- Use `directives_interactions` for documentation and relationship visualization
- Use `directive_flow` for actual execution and AI navigation

#### Argument for Redundancy

**Everything `directives_interactions` does can be done with `directive_flow`:**

**Dependencies:**
```sql
-- Instead of: source: A, target: B, type: 'depends_on'
-- Use: from: B, to: A, type: 'prerequisite', condition: 'A not completed'
```

**Validation:**
```sql
-- Instead of: source: A, target: B, type: 'validates_with'
-- Use: from: A, to: B, type: 'conditional', condition: 'validation_required'
```

**Orchestration:**
```sql
-- Instead of: source: A, target: [B,C,D], type: 'orchestrates'
-- Use: from: A, to: B, type: 'conditional'
--      from: A, to: C, type: 'conditional'
--      from: A, to: D, type: 'conditional'
```

**Escalation:**
```sql
-- Instead of: source: A, target: B, type: 'escalates_to'
-- Use: from: A, to: B, type: 'error'
```

### Recommendation: Remove directives_interactions

**Why Remove It:**

1. **Semantic Confusion**: Having two tables with overlapping purposes creates ambiguity
2. **Maintenance Burden**: Two systems to keep in sync
3. **AI Overhead**: AI must check both tables and reconcile differences
4. **Redundancy**: `directive_flow` can express everything `interactions` can, but more clearly
5. **Execution Focus**: We need executable workflows, not abstract relationships
6. **Simplicity**: One clear system is better than two overlapping ones

**Migration Path:**

1. **Audit existing `directives_interactions` data**
   - Identify what relationships are actually being used
   - Map each interaction to appropriate `directive_flow` entry

2. **Convert to `directive_flow` format**
   ```sql
   -- Example conversion
   -- OLD: source: project_init, target: blueprint_read, type: triggers
   -- NEW:
   INSERT INTO directive_flow (from_directive, to_directive, flow_type, priority)
   VALUES ('project_init', 'aifp_status', 'completion_loop', 100);

   INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value)
   VALUES ('aifp_status', 'blueprint_read', 'status_branch', 'project.initialized', 'true');
   ```

3. **Deprecate `directives_interactions` table**
   - Mark as deprecated in schema
   - Stop using in directives
   - Remove after migration complete

4. **Update helper functions**
   - Remove any helpers that query `directives_interactions`
   - Migrate to new `directive_flow` helpers

**What We Lose:**
- Some documentation value (relationships between directives)
- Historical relationship data (if it exists)

**What We Gain:**
- Clear, executable workflow system
- Reduced cognitive load for AI
- Simpler codebase
- One source of truth for directive navigation
- Better debugging and visualization

**Alternative: Keep for Documentation Only**

If there's value in preserving logical relationships separate from execution:

1. **Rename to `directive_relationships`** (clarify it's not for execution)
2. **Add documentation**: "This table documents logical relationships. For execution flow, use `directive_flow`"
3. **Never query it for execution decisions**
4. **Use it only for:**
   - Generating relationship diagrams
   - Documentation
   - Understanding directive architecture

But honestly, if it's never queried for execution, why keep it in the database? Could be documented in markdown instead.

### Final Verdict

**Remove `directives_interactions` table.**

- Merge any valuable data into `directive_flow`
- Use `directive_flow` as single source of truth
- Document directive relationships in markdown if needed for human reference
- Simplify the system

---

## Implementation Status

### Phase 1: Schema and Helpers ✅ COMPLETED

**1.1. Add directive_flow table to core database** ✅
- **File**: `src/aifp/database/schemas/aifp_core.sql`
- **Version**: Updated from 1.7 to 1.8
- **Changes**:
  - Removed `directives_interactions` table (lines 71-103)
  - Added `directive_flow` table with flow_type, conditions, and priority
  - Added indexes: `idx_directive_flow_from`, `idx_directive_flow_type`
  - Added reference comment pointing to this documentation

**1.2. Implement aifp_status helper** ✅
- **File**: `docs/helpers/helpers-consolidated-orchestrators.md`
- **Location**: Layer 3: Specific Project Analysis Orchestrators
- **Classification**: `target_database='orchestrator'`
- **Status**: Fully documented with complete return structure
- **Note**: Moved to orchestrators (not core) because it queries multiple databases

**1.3. Implement navigation helpers** ✅
- **File**: `docs/helpers/helpers-consolidated-core.md`
- **Removed old helpers**:
  - `get_directive_interactions()`
  - `get_interactions_for_directive()`
  - `get_interactions_for_directive_as_target()`
- **Added new navigation helpers**:
  - `get_next_directives_from_status()` - Query flows with condition evaluation
  - `get_matching_next_directives()` - Return only matching flows
  - `get_completion_loop_target()` - Get loop-back destination
  - `get_conditional_work_paths()` - Get conditional work branches
- **Internal helper**: `evaluate_condition()` (documented in DIRECTIVE_NAVIGATION_SYSTEM.md)

### Phase 2: Map Project Management Flows ⚠️ PENDING

**Status**: Schema ready, awaiting directive flow data

**Blockers**:
- Need to create `directive-flow.json` with project management flows
- Need to update `sync-directives.py` to load new format
- Current `directives-interactions.json` uses old schema (needs migration)

**Next Steps**:
1. Design directive-flow.json format
2. Map project management directives to flows
3. Update sync script to load new format

---

## Reference: Planned Implementation (Not Yet Completed)

The sections below show the planned directive flow mappings. These will be implemented once directive-flow.json is created and sync-directives.py is updated.

### Phase 2: Map Project Management Flows (REFERENCE)

**2.1. Map initialization flows**
```sql
-- Entry point
INSERT INTO directive_flow (from_directive, to_directive, flow_type, priority, description)
VALUES ('aifp_run', 'aifp_status', 'status_branch', 100, 'Always start with status check');

-- Initialization branch
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'project_init', 'status_branch', 'project.initialized', 'false', 'Project not initialized', 100);

INSERT INTO directive_flow (from_directive, to_directive, flow_type, description)
VALUES ('project_init', 'aifp_status', 'completion_loop', 'Re-evaluate after initialization');

-- Blueprint sync
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'blueprint_read', 'status_branch', 'project.blueprint_needs_sync', 'true', 'Blueprint changed', 90);

INSERT INTO directive_flow (from_directive, to_directive, flow_type, description)
VALUES ('blueprint_read', 'aifp_status', 'completion_loop', 'Re-evaluate after blueprint read');
```

**2.2. Map completion path flows**
```sql
-- Completion path complete
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'completion_path_complete', 'status_branch', 'completion_path.current.all_milestones_complete', 'true', 'All milestones in current path complete', 100);

INSERT INTO directive_flow (from_directive, to_directive, flow_type, description)
VALUES ('completion_path_complete', 'aifp_status', 'completion_loop', 'Re-evaluate after path completion');

-- Start next completion path
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'completion_path_start_next', 'status_branch', 'completion_path.next_pending', 'exists', 'Move to next completion path', 90);

INSERT INTO directive_flow (from_directive, to_directive, flow_type, description)
VALUES ('completion_path_start_next', 'aifp_status', 'completion_loop', 'Re-evaluate after starting new path');
```

**2.3. Map milestone flows**
```sql
-- Milestone complete
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'milestone_complete', 'status_branch', 'milestone.current.all_tasks_complete', 'true', 'All tasks in milestone complete', 85);

INSERT INTO directive_flow (from_directive, to_directive, flow_type, description)
VALUES ('milestone_complete', 'aifp_status', 'completion_loop', 'Re-evaluate after milestone completion');

-- Start next milestone
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'milestone_start_next', 'status_branch', 'milestone.has_incomplete', 'false', 'No incomplete milestones, start next', 80);

-- Create first task for milestone
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'task_create', 'status_branch', 'milestone.current.has_tasks', 'false', 'Milestone has no tasks', 75);
```

**2.4. Map task flows**
```sql
-- Task complete
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'task_complete', 'status_branch', 'task.current.all_items_complete', 'true', 'All items in task complete', 70);

INSERT INTO directive_flow (from_directive, to_directive, flow_type, description)
VALUES ('task_complete', 'aifp_status', 'completion_loop', 'Re-evaluate after task completion');

-- Start next task
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'task_start', 'status_branch', 'task.next_pending', 'exists', 'Start next pending task', 65);

-- Create new task
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'task_create', 'status_branch', 'task.next_pending', 'none', 'No pending tasks, create new', 60);
```

**2.5. Map task item flows**
```sql
-- Item complete
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'item_complete', 'status_branch', 'items.current.status', 'completed', 'Mark current item complete', 55);

INSERT INTO directive_flow (from_directive, to_directive, flow_type, description)
VALUES ('item_complete', 'aifp_status', 'completion_loop', 'Re-evaluate after item completion');

-- Create task items
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'item_create', 'status_branch', 'task.has_items', 'false', 'Task has no items - create them', 50);

-- Work on item
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_key, condition_value, condition_description, priority)
VALUES ('aifp_status', 'task_item_work', 'status_branch', 'items.current', 'exists', 'Work on current task item', 45);
```

**2.6. Map work directive flows**
```sql
-- From task_item_work, conditional on what work is needed
INSERT INTO directive_flow (from_directive, to_directive, flow_type, condition_description, priority)
VALUES
  ('task_item_work', 'project_file_write', 'conditional', 'Item requires file creation', 100),
  ('task_item_work', 'project_file_update', 'conditional', 'Item requires file update', 90),
  ('task_item_work', 'project_function_create', 'conditional', 'Item requires function creation', 85),
  ('task_item_work', 'project_function_update', 'conditional', 'Item requires function update', 80),
  ('task_item_work', 'project_type_create', 'conditional', 'Item requires type definition', 75),
  ('task_item_work', 'git_commit', 'conditional', 'Ready to commit changes', 60);

-- Loop backs for work directives
INSERT INTO directive_flow (from_directive, to_directive, flow_type, description)
VALUES
  ('project_file_write', 'aifp_status', 'completion_loop', 'Re-evaluate after file write'),
  ('project_file_update', 'aifp_status', 'completion_loop', 'Re-evaluate after file update'),
  ('project_function_create', 'aifp_status', 'completion_loop', 'Re-evaluate after function creation'),
  ('project_function_update', 'aifp_status', 'completion_loop', 'Re-evaluate after function update'),
  ('project_type_create', 'aifp_status', 'completion_loop', 'Re-evaluate after type creation'),
  ('git_commit', 'aifp_status', 'completion_loop', 'Re-evaluate after commit');
```

### Phase 3: Update Directives (REFERENCE)

**3.1. Update aifp_run**
- Change to call `aifp_status` first
- Use returned status to show user current state
- Call `get_matching_next_directives()` to show options
- Execute chosen directive

**3.2. Update work directives**
- Remove hardcoded "next step" logic
- Add call to `get_completion_loop_target()` at end
- Return to target (usually aifp_status)

**3.3. Add condition evaluation to directives**
- Directives can query `get_conditional_work_paths()` for branching
- Use status object for context-aware decisions

### Phase 4: Test and Iterate (REFERENCE)

**4.1. Test initialization flow**
- Start new project
- Verify status → init → status → blueprint → status cycle

**4.2. Test work flow**
- Create task with items
- Verify status → work → status loop
- Check condition matching

**4.3. Test completion flow**
- Complete all items in task
- Verify automatic task completion detection
- Check milestone/path cascade

**4.4. Test error cases**
- Missing data
- Invalid states
- Infinite loop protection

### Phase 5: Deprecate directives_interactions ✅ PARTIALLY COMPLETED

**5.1. Audit existing interactions data** ⚠️ PENDING
- Review document created: `docs/DIRECTIVES_INTERACTIONS_REVIEW.md`
- Old data still exists in `directives-interactions.json`
- Needs migration to new format

**5.2. Remove table** ✅ COMPLETED
- Removed from `src/aifp/database/schemas/aifp_core.sql` (v1.8)
- Replaced with `directive_flow` table

**5.3. Update schema documentation** ✅ COMPLETED
- Schema updated with directive_flow
- Reference comment points to this documentation

**5.4. Remove helper functions** ✅ COMPLETED
- `get_directive_interactions()` - REMOVED
- `get_interactions_for_directive()` - REMOVED
- `get_interactions_for_directive_as_target()` - REMOVED
- Removed from helpers-consolidated-core.md

**5.5. Remaining cleanup** ⚠️ PENDING
- See `docs/DIRECTIVES_INTERACTIONS_REVIEW.md` for detailed checklist
- Key files needing updates:
  - `sync-directives.py` (8 locations)
  - `aifp_help.md` (2 references)
  - Create new `directive-flow.json` format

---

## Examples

### Example 1: New Project Initialization

**User runs: `aifp_run`**

**Step 1: Check Status**
```python
status = aifp_status()
# Returns:
{
  "project": {
    "initialized": false,
    "name": null,
    "status": null
  },
  "suggested_next_directives": [
    {
      "directive": "project_init",
      "reason": "Project not initialized",
      "priority": 100
    }
  ]
}
```

**Step 2: Query Next Directives**
```python
options = get_matching_next_directives('aifp_status', status)
# Returns:
[
  {
    "to_directive": "project_init",
    "condition_key": "project.initialized",
    "condition_value": "false",
    "matches": true,
    "priority": 100
  }
]
```

**Step 3: AI Chooses**
- Only one option matches
- Execute `project_init`

**Step 4: Complete and Loop**
```python
# project_init completes
loop_target = get_completion_loop_target('project_init')
# Returns: 'aifp_status'

# Return to status
status = aifp_status()
# Now returns:
{
  "project": {
    "initialized": true,
    "name": "MyProject",
    "status": "planning"
  },
  "suggested_next_directives": [
    {
      "directive": "blueprint_read",
      "reason": "Blueprint needs reading",
      "priority": 90
    }
  ]
}
```

**Step 5: Continue Cycle**
- Status now shows different state
- New next directives suggested
- Cycle continues

---

### Example 2: Working on Task Item

**Current State:**
- Project initialized
- Milestone in progress
- Task in progress
- Current item: "Create User model with ID naming"

**Step 1: Status Shows Work Available**
```python
status = aifp_status()
# Returns:
{
  "project": {"initialized": true, "status": "in_progress"},
  "milestone": {
    "current": {"id": 5, "name": "Core Features", "status": "in_progress"}
  },
  "task": {
    "current": {"id": 12, "name": "Implement authentication", "status": "in_progress"}
  },
  "items": {
    "current": {
      "id": 45,
      "content": "Create User model with ID naming",
      "status": "in_progress"
    }
  },
  "context": {
    "files_in_scope": [
      {"id": 5, "name": "auth-ID_5.py", "path": "src/auth-ID_5.py"}
    ]
  },
  "suggested_next_directives": [
    {
      "directive": "task_item_work",
      "reason": "Current task has in-progress item",
      "priority": 45
    }
  ]
}
```

**Step 2: Work on Item**
```python
# AI chooses task_item_work
# Inside task_item_work, query conditional paths
work_options = get_conditional_work_paths('task_item_work', current_item_context)
# Returns:
[
  {"to_directive": "project_file_write", "condition": "Item requires file creation", "priority": 100},
  {"to_directive": "project_type_create", "condition": "Item requires type definition", "priority": 75}
]

# AI determines: Need to create User type
# Execute project_type_create
```

**Step 3: Complete Type Creation**
```python
# project_type_create completes
loop_target = get_completion_loop_target('project_type_create')
# Returns: 'aifp_status'

# Back to status
status = aifp_status()
# Item still in progress, but now context updated with new type
```

**Step 4: Continue Work**
```python
# Status suggests task_item_work again
# This time, create functions that use the type
# Execute project_function_create
# Loop back to status
# Repeat until item complete
```

**Step 5: Item Completion Detected**
```python
# After final function created, item marked complete
status = aifp_status()
# Returns:
{
  "items": {
    "current": null,  # No in-progress item
    "next_pending": {
      "id": 46,
      "content": "Create authentication functions"
    }
  },
  "suggested_next_directives": [
    {
      "directive": "task_item_work",
      "reason": "Next pending item available",
      "priority": 45
    }
  ]
}
```

---

### Example 3: Task Completion Cascade

**Current State:**
- Last item in task completed
- All items complete

**Step 1: Status Detects Completion**
```python
status = aifp_status()
# Returns:
{
  "task": {
    "current": {
      "id": 12,
      "name": "Implement authentication",
      "all_items_complete": true
    }
  },
  "suggested_next_directives": [
    {
      "directive": "task_complete",
      "reason": "All task items complete",
      "priority": 70
    }
  ]
}
```

**Step 2: Complete Task**
```python
# Execute task_complete
# Marks task status as 'completed'
# Loops back to status
```

**Step 3: Check Milestone**
```python
status = aifp_status()
# Now checks: were there other tasks in milestone?
# Returns:
{
  "milestone": {
    "current": {
      "id": 5,
      "name": "Core Features",
      "all_tasks_complete": false  # Other tasks exist
    }
  },
  "task": {
    "next_pending": {
      "id": 13,
      "name": "Add logging"
    }
  },
  "suggested_next_directives": [
    {
      "directive": "task_start",
      "reason": "Next pending task available",
      "priority": 65
    }
  ]
}
```

**Step 4: OR Milestone Complete**
```python
# If that was the last task:
status = aifp_status()
# Returns:
{
  "milestone": {
    "current": {
      "id": 5,
      "name": "Core Features",
      "all_tasks_complete": true
    }
  },
  "suggested_next_directives": [
    {
      "directive": "milestone_complete",
      "reason": "All milestone tasks complete",
      "priority": 85
    }
  ]
}
```

**Step 5: Cascade Continues**
- Complete milestone → check completion path
- Complete path → start next path
- Status always shows what's next

---

## Conclusion

The Status-Driven Decision Tree architecture provides:

1. **Explicit Navigation**: No inference needed for "what's next?"
2. **State-Driven Decisions**: Choices based on actual project state
3. **Many-to-Many Branching**: Multiple valid paths from any point
4. **Loop-Back Pattern**: Consistent return to status after work
5. **Low Cognitive Load**: AI queries for options, gets filtered list
6. **Maintainable**: Flow data is declarative and queryable
7. **Debuggable**: Can trace decisions through status snapshots
8. **Extensible**: Easy to add new flows and conditions

By removing `directives_interactions` and using `directive_flow` as the single navigation system, we eliminate ambiguity and provide clear, executable workflow guidance for AI.

The hub pattern (status as central orchestrator) ensures that decisions are always based on current reality, and the loop-back pattern prevents stale state issues while simplifying work directive implementation.

This architecture directly addresses the original problem: AI no longer needs to "guess" what comes next. It simply queries the flow table, evaluates conditions, and chooses from valid options.
