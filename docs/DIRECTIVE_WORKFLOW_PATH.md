# AIFP Directive Workflow Path

**Date**: 2025-12-17
**Purpose**: Comprehensive documentation of AIFP directive flow patterns
**Status**: Phase 1 - Core workflow mapping

---

## Overview

This document maps the **complete AIFP directive workflow paths** covering:
- **Use Case 1**: Regular software development (building applications)
- **Use Case 2**: User directive automation (AI builds infrastructure to execute user directives)
- **User preferences integration** (checked before every directive execution)
- **Git integration** (standard workflow component, not conditional)
- **FP directives** (reference consultation, not execution flow)
- **Complete project management** (all project directives and when they're used)

The workflow follows a **state-driven, loop-back pattern** where all completion directives return to `aifp_status` to re-evaluate state and determine next actions.

**Key Principles**:
1. **Status-first**: Always check current state before action
2. **Preferences-first**: Load user preferences before executing directives
3. **Git-aware**: Sync git state on boot and after file operations
4. **Two use cases**: Different workflows for software development vs. automation infrastructure
5. **FP baseline**: All code FP-compliant; consult FP directives for clarification
6. **Loop-back pattern**: All state changes → aifp_status → re-evaluate

---

## Core Architecture Pattern

```
┌───────────────────────────────────────────────────────────────────┐
│                   COMPLETE WORKFLOW PATTERN                        │
│                                                                    │
│  Entry → Status → Preferences Check → Git Sync →                  │
│  Detect Use Case → [Work/Decisions] → State Change →              │
│  Completion → LOOP BACK to Status → Re-evaluate → Next            │
│                                                                    │
│  Key Integrations:                                                │
│  - User Preferences: Loaded before every directive execution      │
│  - Git Management: Sync state on boot + after file operations     │
│  - Use Case Detection: user_directives_status determines path     │
│  - FP Baseline: Always FP-compliant; consult FP directives if needed │
│                                                                    │
│  All paths eventually loop back to aifp_status for                │
│  state re-evaluation and next-step determination                  │
└───────────────────────────────────────────────────────────────────┘
```

## Two Distinct Use Cases

### Use Case 1: Regular Software Development
**User is building**: Web apps, libraries, CLI tools, data processors, etc.
**AIFP role**: Enforce FP compliance, manage project lifecycle, track progress
**Project structure**: User writes code, AIFP tracks in project.db
**Workflow**: Standard project management (tasks, milestones, completion)

### Use Case 2: User Directive Automation
**User wants**: Home automation, cloud infrastructure management, custom workflows
**AIFP role**: Parse user directives → **Build entire automation infrastructure**
**Project structure**:
- User writes directive files (directives/lights.yaml)
- **AI generates entire codebase** (src/, tests/, etc.)
- project.db tracks generated code
- user_directives.db tracks directive state
**Workflow**:
1. Parse user directives → Create user_directives.db
2. Generate infrastructure to execute directives
3. AI self-manages project until infrastructure complete
4. Once complete: Project exists to support user directive execution
5. Modifications only when needed to better support directives

**Detection**: Query `project.user_directives_status`:
- `NULL` = Use Case 1 (regular development)
- `'in_progress'`, `'active'`, `'disabled'` = Use Case 2 (automation)

---

## Entry Point: aifp_run

**Directive**: `aifp_run`
**Purpose**: Gateway orchestrator with conditional status fetching
**File**: `docs/directives-json/directives-project.json:3`

### Flow

```
aifp_run(user_request, get_status)
  ├─ IF get_status=true:
  │    └─ Call aifp_status → Return comprehensive state + suggestions
  │
  └─ IF get_status=false (default):
       └─ Return common starting points + directive_flow guidance
```

### When Called

**get_status=true**:
- First interaction of session
- After major state changes (init, milestone complete, multiple tasks done)
- User asks for status explicitly
- AI uncertain of current state

**get_status=false** (default):
- Continuation work within session
- AI has cached status
- Normal operations (file writes, task updates, etc.)

### Next Steps

From `aifp_run`, AI should:
1. Call `aifp_status` (if get_status=true) OR use cached status
2. Use `get_next_directives_from_status()` to determine appropriate directive
3. Execute work directive
4. Loop back to status after state changes

---

## User Preferences Integration

**Critical**: User preferences MUST be loaded before executing any directive that can be customized.

**Directive**: `user_preferences_sync`
**File**: `docs/directives-json/directives-user-pref.json:3`

### Workflow

```
BEFORE executing any customizable directive:
  ↓
user_preferences_sync(directive_name)
  ├─ Query user_preferences.db:
  │    SELECT * FROM directive_preferences
  │    WHERE directive_name = ? AND active = 1
  ├─ Load all active preferences for directive
  ├─ Apply preferences to execution context
  └─ Return modified context
  ↓
Execute directive with user preferences applied
```

### Which Directives Check Preferences

**Project directives** (most common):
- `project_file_write` - code style, docstrings, max function length, naming conventions
- `project_task_create` - task granularity, default priorities
- `project_task_decomposition` - how detailed to break down tasks
- `project_compliance_check` - auto-fix violations vs. report only

**User system directives**:
- `user_directive_validate` - validation strictness
- `user_directive_implement` - code generation preferences

### Preference Examples

```json
{
  "directive_name": "project_file_write",
  "preference_key": "always_add_docstrings",
  "preference_value": "true",
  "active": 1
}

{
  "directive_name": "project_task_decomposition",
  "preference_key": "task_granularity",
  "preference_value": "medium",
  "active": 1
}
```

### Integration Pattern

```
User requests work
  ↓
aifp_run → aifp_status (get state)
  ↓
Determine appropriate directive (e.g., project_file_write)
  ↓
BEFORE executing project_file_write:
  └─ user_preferences_sync("project_file_write")
       └─ Load preferences → Apply to context
  ↓
Execute project_file_write with preferences applied
  ↓
Code generated follows user's style preferences
```

**User Preference Directives** (7 total):
- `user_preferences_sync` - Load before directive execution
- `user_preferences_update` - Update preferences from user requests
- `user_preferences_learn` - Learn from corrections (opt-in)
- `user_preferences_export` - Export to JSON
- `user_preferences_import` - Import from JSON
- `project_notes_log` - Logging with directive context
- `tracking_toggle` - Enable/disable tracking features

---

## Git Integration (Standard Workflow)

**Critical**: Git is NOT optional. It's integrated into standard workflow for version control and external change detection.

### Git on Session Start

```
aifp_status called (session start)
  ↓
ALWAYS: git_detect_external_changes
  ├─ Compare project.last_known_git_hash with current HEAD
  ├─ IF different:
  │    ├─ Alert: "Code changed outside AIFP"
  │    ├─ Show: git diff between hashes
  │    ├─ Prompt: Review changes? Sync database?
  │    └─ Call git_sync_state to update hash
  └─ ELSE: Continue normally
```

### Git on File Write

```
project_file_write
  ↓
Write file to disk
  ↓
Update project.db (files, functions, interactions)
  ↓
ALWAYS: git_sync_state
  └─ Update project.last_known_git_hash = current HEAD
```

### Git Collaboration Workflow

```
Multi-user or multi-AI work:
  ↓
git_create_branch(user_name)
  └─ Creates: aifp-{user}-{number}
  ↓
[Work on branch]
  ↓
Ready to merge:
  ↓
git_detect_conflicts(source_branch, target_branch)
  ├─ FP-powered conflict analysis:
  │    ├─ Compare purity levels
  │    ├─ Check test results
  │    ├─ Analyze dependencies
  │    └─ Calculate confidence score
  ├─ IF confidence > 0.8:
  │    └─ Auto-resolve conflict (prefer higher purity + passing tests)
  └─ ELSE:
       └─ Prompt user for manual resolution
  ↓
git_merge_branch(source, target, resolution_strategy)
  ├─ Apply resolution
  ├─ Update merge_history table
  ├─ Run tests
  └─ Update project.last_known_git_hash
```

**Git Directives** (6 total):
- `git_init` - Initialize git integration
- `git_detect_external_changes` - Detect changes made outside AIFP (session start)
- `git_create_branch` - Create work branches (format: aifp-{user}-{number})
- `git_detect_conflicts` - FP-powered conflict analysis
- `git_merge_branch` - Merge with AI-assisted resolution
- `git_sync_state` - Update last_known_git_hash (after file writes)

---

## Status Orchestrator: aifp_status

**Directive**: `aifp_status`
**Purpose**: Comprehensive state analysis and next-step guidance
**File**: `docs/directives-json/directives-project.json:1644`

### Workflow

```
aifp_status
  ├─ Determine project state:
  │    ├─ Check .aifp-project/ folder exists
  │    ├─ Check .git/.aifp/ backup exists
  │    └─ Check project initialized
  │
  ├─ IF project not initialized:
  │    └─ Branch: Suggest initialization path
  │
  ├─ IF project initialized:
  │    ├─ Sync git state on boot (detect external changes)
  │    ├─ Read ProjectBlueprint.md
  │    ├─ Load infrastructure context
  │    ├─ Check user_directives_status (NULL=Use Case 1, active=Use Case 2)
  │    ├─ Build priority status tree:
  │    │    └─ Sidequests (highest priority) → Subtasks → Tasks
  │    ├─ Get historical context (previous completed items)
  │    ├─ Check for ambiguities (unclear next steps)
  │    └─ Generate comprehensive status report
  │
  └─ Return:
       ├─ Project state summary
       ├─ Current work item (task/subtask/sidequest if any)
       ├─ Completion path progress
       ├─ Milestone progress
       ├─ Priority work queue
       ├─ Ambiguities/roadblocks
       └─ Next-step suggestions
```

### Status Object Structure

The status object returned includes:
- **project_initialized**: boolean
- **git_backup_exists**: boolean
- **project_metadata**: {name, purpose, goals, status}
- **infrastructure**: {language, build_tool, packages}
- **user_directives_status**: NULL | 'in_progress' | 'active' | 'disabled'
- **completion_path**: {current_stage, stages_completed, stages_remaining}
- **current_milestone**: {id, name, progress, tasks_complete, tasks_total}
- **priority_work_queue**: [sidequests, subtasks, tasks] ordered by priority
- **current_work_item**: {type, id, name, description, status} OR null
- **historical_context**: [last_N_completed_items]
- **ambiguities**: [list of unclear decisions]
- **next_step_suggestions**: [directive_names]

---

## State-Based Branching

Based on the status object, the workflow branches to different paths:

### Branch 1: Uninitialized Project

**State**: `project_initialized = false`

```
aifp_status (returns: not initialized)
  ↓
IF git_backup_exists:
  ↓
  Prompt: Restore from .git/.aifp/ OR Initialize new?
  ├─ User chooses restore:
  │    └─ Copy .git/.aifp/ → .aifp-project/
  │         └─ aifp_status (verify restoration)
  │
  └─ User chooses new init:
       └─ project_init

ELSE (no backup):
  ↓
  Suggest: project_init
  ↓
  User confirms:
  └─ project_init
```

**Directives Involved**:
- `aifp_status` - Detects uninitialized state
- `project_init` - Initializes new AIFP project

**Next**: After initialization → LOOP BACK to `aifp_status`

---

### Branch 2: Initialized, No Tasks

**State**: `project_initialized = true`, `has_incomplete_items = false`

```
aifp_status (returns: initialized, no tasks)
  ↓
Suggest: Create initial tasks
  ↓
IF user confirms:
  └─ project_task_decomposition
       ├─ Reads ProjectBlueprint.md
       ├─ Identifies themes/flows
       ├─ Creates completion_path stages
       ├─ Creates milestones per stage
       ├─ Creates initial tasks per milestone
       ├─ Auto-creates items per task
       └─ Updates database
  ↓
LOOP BACK to aifp_status (verify tasks created)
```

**Directives Involved**:
- `aifp_status` - Detects no tasks
- `project_task_decomposition` - Creates task hierarchy

**Next**: After task creation → LOOP BACK to `aifp_status` → Active work branch

---

### Branch 3: Active Work (Has Incomplete Items)

**State**: `project_initialized = true`, `has_incomplete_items = true`

```
aifp_status (returns: current work item)
  ↓
Priority order: Sidequest > Subtask > Task
  ↓
Get highest priority incomplete item:
  ├─ IF sidequest exists: Focus on sidequest
  ├─ ELIF subtask exists: Focus on subtask
  └─ ELSE: Focus on task
  ↓
Display:
  ├─ Current item details
  ├─ Related flows
  ├─ Related files
  ├─ Historical context (previous items)
  └─ Next-step guidance
  ↓
User/AI performs work:
  ├─ project_file_write (creates/modifies code)
  ├─ project_task_update (updates progress)
  ├─ project_item_create (adds new items)
  └─ [other work directives]
  ↓
Work complete:
  └─ [Completion directives based on item type]
       ├─ Item complete → Mark item done → Continue task
       ├─ Task complete → project_task_complete
       ├─ Subtask complete → project_subtask_complete
       └─ Sidequest complete → project_sidequest_complete
  ↓
LOOP BACK to aifp_status (re-evaluate state)
```

**Work Directives** (examples):
- `project_file_write` - Create/modify code files
- `project_task_update` - Update task progress
- `project_item_create` - Add new task items
- `project_subtask_create` - Create subtasks
- `project_sidequest_create` - Create sidequests
- `project_reserve_finalize` - Reserve file/function IDs
- `project_update_db` - Sync database state

**Completion Flow**: See "Completion Hierarchy" section below

---

### Branch 4: Milestone Complete

**State**: All tasks in milestone marked complete

```
project_task_complete
  ↓
Check milestone status:
  └─ Query: SELECT COUNT(*) FROM tasks WHERE milestone_id = ? AND status != 'completed'
  ↓
IF all tasks complete:
  ↓
  project_milestone_complete
    ├─ Mark milestone complete
    ├─ Check completion_path status
    ├─ Review next milestone (if any)
    ├─ Log milestone completion
    └─ Prompt user for next steps
  ↓
LOOP BACK to aifp_status (show next milestone or completion_path progress)
```

**Directives Involved**:
- `project_task_complete` - Detects milestone completion condition
- `project_milestone_complete` - Handles milestone completion

---

### Branch 5: All Work Complete

**State**: All milestones complete, all tasks done

```
aifp_status (returns: no incomplete items, all milestones done)
  ↓
Suggest: Check for project completion
  ↓
IF user confirms:
  └─ project_completion_check
       ├─ Check completion_path stages (all done?)
       ├─ Check milestones (all done?)
       ├─ Check tasks (all done?)
       ├─ Verify no pending items
       ├─ Check for drift (goals vs actual)
       └─ Generate completion report
  ↓
IF all criteria met:
  ├─ Mark project status = 'complete'
  ├─ Suggest: project_archive
  └─ LOOP BACK to aifp_status (show completed state)
  ↓
ELSE (criteria not met):
  ├─ Report gaps/issues
  ├─ Suggest corrections (create tasks, adjust milestones, etc.)
  └─ LOOP BACK to aifp_status
```

**Directives Involved**:
- `aifp_status` - Detects all work complete
- `project_completion_check` - Validates completion criteria
- `project_archive` - Archives completed project

---

## Use Case 2: User Directive Automation (Complete Workflow)

**Critical Difference**: In Use Case 2, **AI builds the entire project infrastructure** to execute user directives.

### Detection

```
aifp_status
  ↓
Query: SELECT user_directives_status FROM project.project
  ├─ IF NULL: Use Case 1 (regular development)
  └─ IF NOT NULL: Use Case 2 (automation infrastructure)
```

### Complete Workflow

#### Phase 1: Parse & Setup (Initialization)

```
User provides directive files (directives/lights.yaml, directives/thermostat.json, etc.)
  ↓
project_init (detects directive files)
  ↓
user_directive_parse(directive_file_path)
  ├─ Parse YAML/JSON/TXT format
  ├─ Extract: triggers, conditions, actions, schedules
  ├─ Generate directive_id (hash of content)
  ├─ Create user_directives.db:
  │    ├─ CREATE TABLE directives (id, name, config, status, ...)
  │    ├─ CREATE TABLE triggers (directive_id, type, conditions, ...)
  │    ├─ CREATE TABLE actions (directive_id, type, target, ...)
  │    └─ CREATE TABLE execution_logs (directive_id, timestamp, ...)
  └─ INSERT parsed directives
  ↓
user_directive_validate(directive_id)
  ├─ Interactive Q&A with user:
  │    "For 'turn on lights', which lights?"
  │    "What time range for 'morning routine'?"
  │    "API credentials for HomeAssistant?"
  ├─ Validate trigger types (time, event, webhook, state change)
  ├─ Validate action targets (devices, APIs, databases)
  ├─ Check for conflicts (overlapping triggers, contradictory actions)
  └─ UPDATE directives SET validation_status = 'validated'
  ↓
Update project.user_directives_status = 'in_progress'
  ↓
LOOP BACK to aifp_status (now in Use Case 2 mode)
```

#### Phase 2: Generate Infrastructure (AI Self-Manages)

```
aifp_status (detects user_directives_status = 'in_progress')
  ↓
Suggest: Generate infrastructure for directives
  ↓
user_directive_implement(directive_id)
  ├─ AI analyzes directive requirements:
  │    ├─ What APIs needed? (HomeAssistant, AWS, MQTT, etc.)
  │    ├─ What data structures? (state, history, schedules)
  │    ├─ What runtime? (event loop, cron, webhook server)
  │    └─ What error handling? (retries, fallbacks, alerts)
  │
  ├─ AI generates complete codebase:
  │    ├─ src/
  │    │    ├─ main.py (entry point, event loop)
  │    │    ├─ triggers/ (trigger handlers)
  │    │    ├─ actions/ (action executors)
  │    │    ├─ integrations/ (API clients)
  │    │    └─ utils/ (helpers)
  │    ├─ tests/
  │    ├─ config/
  │    └─ docs/
  │
  ├─ For EACH file to create:
  │    └─ project_file_write(file_path, content)
  │         ├─ AI writes FP-compliant code
  │         ├─ Consult FP directives if needed
  │         ├─ Update project.db (files, functions, interactions)
  │         └─ git_sync_state (update hash)
  │
  ├─ AI creates tasks to track implementation:
  │    └─ project_task_decomposition
  │         ├─ Create milestone: "Core Infrastructure"
  │         ├─ Create tasks: "Trigger system", "Action system", "API integration"
  │         └─ AI completes tasks as it generates code
  │
  ├─ AI self-manages until infrastructure complete:
  │    └─ LOOP: project_file_write → project_task_complete → aifp_status
  │              → determine next file → project_file_write → ...
  │
  └─ When all infrastructure complete:
       └─ UPDATE directives SET implementation_status = 'complete'
```

#### Phase 3: Approval & Activation

```
AI completes infrastructure generation
  ↓
user_directive_approve(directive_id)
  ├─ Present to user:
  │    ├─ Generated code overview
  │    ├─ File structure
  │    ├─ Test results
  │    └─ How directives will execute
  ├─ User tests implementation (manual testing)
  ├─ IF user approves:
  │    └─ UPDATE directives SET approval_status = 'approved'
  └─ ELSE:
       ├─ User provides feedback
       ├─ AI modifies code (project_file_write)
       └─ Repeat approval process
  ↓
user_directive_activate(directive_id)
  ├─ Deploy directive for real-time execution:
  │    ├─ Start event loop / cron / webhook server
  │    ├─ Register triggers with external systems
  │    ├─ Begin monitoring state
  │    └─ UPDATE directives SET status = 'active'
  └─ Log activation timestamp
  ↓
Update project.user_directives_status = 'active'
  ↓
LOOP BACK to aifp_status (infrastructure active, monitoring mode)
```

#### Phase 4: Monitoring & Maintenance (Ongoing)

```
Project infrastructure now exists solely to support directive execution
  ↓
user_directive_monitor()
  ├─ Track execution logs
  ├─ Monitor errors / failures
  ├─ Check trigger hit rates
  ├─ Analyze action success rates
  └─ Alert on anomalies
  ↓
IF directive file updated by user:
  ↓
  user_directive_parse (re-parse)
    ↓
  user_directive_validate (re-validate changes)
    ↓
  user_directive_update(directive_id)
    ├─ Generate code diffs
    ├─ Apply necessary changes (project_file_write)
    ├─ Run tests
    └─ Re-approve → Re-activate
  ↓
IF infrastructure needs improvement to better support directives:
  ↓
  AI creates tasks (project_task_create)
    ↓
  AI implements improvements (project_file_write)
    ↓
  AI completes tasks (project_task_complete)
    ↓
  LOOP BACK to aifp_status
```

### Key Differences from Use Case 1

| Aspect | Use Case 1 | Use Case 2 |
|--------|-----------|-----------|
| **Code author** | User writes code | AI generates all code |
| **Project purpose** | User's application | Infrastructure for user directives |
| **Task source** | User defines tasks | AI creates tasks to track generation |
| **Completion** | User's app feature-complete | Directive infrastructure complete |
| **Ongoing work** | User continues building | AI only modifies when directives change |
| **Database** | project.db only | project.db + user_directives.db |

**User Directive System Directives** (9 total):
- `user_directive_parse` - Parse directive files → create user_directives.db
- `user_directive_validate` - Interactive Q&A validation
- `user_directive_implement` - **AI generates entire codebase**
- `user_directive_approve` - User approval workflow
- `user_directive_activate` - Deploy for execution
- `user_directive_monitor` - Track execution & errors
- `user_directive_update` - Handle directive file changes
- `user_directive_deactivate` - Stop execution
- `user_directive_status` - Report system status

---

## FP Directives: Reference Consultation Flow

**Critical**: FP directives are **NOT executed step-by-step**. They are **reference documentation** consulted when clarification needed.

### FP Baseline (Always Active)

**All code MUST be FP-compliant**. Non-negotiable requirements:
- ✅ Pure functions (no side effects, same input → same output)
- ✅ Immutable data structures (no reassignment, no mutations)
- ✅ No OOP (no classes, no inheritance, no objects)
- ✅ Explicit dependencies (all inputs as parameters)
- ✅ Explicit error handling (Result types, Try monads, no exceptions)

**AI does NOT need to consult FP directives for baseline compliance**. FP is the default coding style.

### When to Consult FP Directives

AI should query FP directives when:

1. **Implementation details unclear**:
   - "How do I implement currying in Python?"
   - "What's the FP way to handle optional values?"
   - Query: `search_directives(keyword="currying", type="fp")`

2. **Complex FP patterns needed**:
   - "How do I compose monads?"
   - "What's the FP approach to lazy evaluation?"
   - Query: `search_directives(keyword="monadic composition", type="fp")`

3. **OOP library wrapping**:
   - "How do I wrap Django ORM in FP style?"
   - "How do I use React (OOP) in FP project?"
   - Query: `get_directive("fp_wrapper_generation")`

4. **FP compliance validation**:
   - "Is this function pure?"
   - "Does this violate immutability?"
   - Query: `get_directive("fp_purity")`, `get_directive("fp_side_effect_detection")`

5. **Optimization techniques**:
   - "How can I optimize this recursive function?"
   - "Should I memoize this?"
   - Query: `get_directive("fp_tail_recursion")`, `get_directive("fp_memoization")`

### FP Directive Categories

**FP Core** (29 directives) - Fundamental FP principles:
- `fp_purity` - Pure function requirements
- `fp_immutability` - Immutable data structures
- `fp_side_effect_detection` - Detect side effects
- `fp_no_oop` - No classes/inheritance
- `fp_type_safety` - Type annotations
- `fp_currying` - Function currying
- `fp_pattern_matching` - Pattern matching
- `fp_tail_recursion` - Tail call optimization
- [21 more core directives...]

**FP Auxiliary** (36 directives) - Advanced FP techniques:
- `fp_optionals` - Option/Maybe types
- `fp_result_types` - Result types (Ok/Err)
- `fp_try_monad` - Try monad for error handling
- `fp_wrapper_generation` - Wrap OOP libraries
- `fp_memoization` - Function memoization
- `fp_lazy_evaluation` - Lazy computation
- `fp_monadic_composition` - Monad composition
- [29 more auxiliary directives...]

### Directive Flow for FP References

```
AI writing code (default: FP-compliant)
  ↓
IF implementation detail unclear:
  ↓
  search_directives(keyword="...", type="fp")
    └─ Returns: List of relevant FP directives
  ↓
  get_directive_content(directive_name)
    └─ Returns: Full MD documentation
  ↓
  Read guidance
  ↓
  Apply to code
  ↓
  Continue coding
```

**No loop-back to aifp_status for FP consultations** - they're inline references.

---

## Complete Project Management Directive List

**All Project Directives** (38 total)

### Entry & Status (3)
- `aifp_run` - Entry point orchestrator
- `aifp_status` - Comprehensive status analysis
- `aifp_help` - Directive help/documentation

### Initialization (3)
- `project_init` - Initialize AIFP project
- `project_blueprint_read` - Read ProjectBlueprint.md
- `project_blueprint_update` - Update ProjectBlueprint.md

### Task Management (10)
- `project_task_decomposition` - Create task hierarchy from blueprint
- `project_task_create` - Create new task
- `project_task_update` - Update task progress
- `project_task_complete` - Mark task complete (auto-detect milestone)
- `project_subtask_create` - Create subtask (task decomposition)
- `project_subtask_complete` - Mark subtask complete
- `project_sidequest_create` - Create sidequest (unexpected work)
- `project_sidequest_complete` - Mark sidequest complete
- `project_item_create` - Create task items (smallest unit)
- `project_milestone_complete` - Mark milestone complete

### File & Code Management (5)
- `project_file_write` - Create/modify code files + DB sync
- `project_file_read` - Read file with context
- `project_file_delete` - Delete file + DB cleanup
- `project_add_path` - Add file to tracking
- `project_reserve_finalize` - Reserve file/function IDs

### Database & State (2)
- `project_update_db` - Sync database state
- `project_evolution` - Track project evolution

### Analysis & Validation (7)
- `project_completion_check` - Validate completion criteria
- `project_compliance_check` - FP compliance validation
- `project_error_handling` - Error handling guidance
- `project_metrics` - Project metrics analysis
- `project_performance_summary` - Performance analysis
- `project_dependency_map` - Dependency visualization
- `project_theme_flow_mapping` - Theme/flow mapping

### Maintenance (5)
- `project_dependency_sync` - Sync dependencies
- `project_integrity_check` - Data integrity validation
- `project_auto_resume` - Auto-resume work
- `project_auto_summary` - Auto-generate summaries
- `project_user_referral` - User decision needed

### Archival (3)
- `project_archive` - Archive completed project
- `project_backup_restore` - Backup/restore operations
- `project_refactor_path` - Path refactoring

---

## Completion Hierarchy (Loop-Back Pattern)

**Critical Pattern**: ALL completion directives loop back to `aifp_status` to re-evaluate state.

### Hierarchy Levels

```
Item (lowest level)
  ↓ (when all items done)
Task
  ↓ (when all tasks done)
Milestone
  ↓ (when all milestones done)
Completion Path Stage
  ↓ (when all stages done)
Project Complete
```

### Completion Flow Details

#### 1. Task Completion

**Directive**: `project_task_complete`
**File**: `docs/directives-json/directives-project.json:2486`

```
project_task_complete(task_id)
  ├─ Validate task eligible for completion
  ├─ Mark task status = 'completed'
  ├─ Mark all task items = 'completed' (auto-complete items)
  ├─ Log completion timestamp
  ├─ Check milestone status:
  │    └─ Query incomplete tasks in milestone
  │         ├─ IF all tasks complete:
  │         │    └─ Call project_milestone_complete
  │         └─ ELSE:
  │              └─ Review next steps with user
  ↓
LOOP BACK to aifp_status
  ├─ Show completion_path progress
  ├─ Show milestone progress
  ├─ Query pending tasks in milestone
  ├─ Offer options:
  │    ├─ Continue with next task
  │    ├─ Create new task
  │    ├─ Pivot to different milestone
  │    └─ Review completion path
  └─ Set next task status = 'in_progress' OR call project_task_create
```

**Key Feature**: Automatic milestone completion detection

#### 2. Subtask Completion

**Directive**: `project_subtask_complete`
**File**: `docs/directives-json/directives-project.json:2593`

```
project_subtask_complete(subtask_id)
  ├─ Mark subtask status = 'completed'
  ├─ Mark all subtask items = 'completed'
  ├─ Log completion timestamp
  ├─ Check parent task status
  ├─ Resume parent task work
  ↓
LOOP BACK to aifp_status
  └─ Show parent task context
```

#### 3. Sidequest Completion

**Directive**: `project_sidequest_complete`
**File**: `docs/directives-json/directives-project.json:2673`

```
project_sidequest_complete(sidequest_id)
  ├─ Mark sidequest status = 'completed'
  ├─ Mark all sidequest items = 'completed'
  ├─ Log completion timestamp
  ├─ Log lessons learned
  ├─ Resume original work context
  ↓
LOOP BACK to aifp_status
  └─ Show original task/subtask context
```

#### 4. Milestone Completion

**Directive**: `project_milestone_complete`
**File**: `docs/directives-json/directives-project.json:2767`

```
project_milestone_complete(milestone_id)
  ├─ Mark milestone status = 'completed'
  ├─ Log completion timestamp
  ├─ Check completion_path stage status
  ├─ Identify next milestone (if any)
  ├─ Prompt user for next steps:
  │    ├─ Start next milestone
  │    ├─ Create new milestone
  │    └─ Review completion path
  ↓
LOOP BACK to aifp_status
  └─ Show completion_path progress + next milestone
```

---

## Conditional Paths

### Git Integration Points

Git directives integrate at key workflow points:

```
Session Start:
  aifp_status
    └─ git_detect_external_changes (sync git state)

File Write:
  project_file_write
    └─ git_sync_state (update last_known_git_hash)

Branch Work:
  git_create_branch (user/AI work branches)
  ↓
  [work directives]
  ↓
  git_detect_conflicts
  ↓
  git_merge_branch (FP-powered resolution)
```

**Git Directives**:
- `git_init` - Initialize Git integration
- `git_detect_external_changes` - Detect changes made outside AIFP
- `git_create_branch` - Create work branches (aifp-{user}-{number})
- `git_detect_conflicts` - Analyze conflicts using FP purity
- `git_merge_branch` - Merge with AI-assisted resolution
- `git_sync_state` - Update last_known_git_hash

### User Directive Automation (Use Case 2)

When `user_directives_status != NULL`:

```
aifp_status (detects user_directives_status = 'active')
  ↓
User requests directive work:
  ↓
user_directive_parse (parse YAML/JSON/TXT)
  ↓
user_directive_validate (Q&A validation)
  ↓
user_directive_implement (generate FP code in src/)
  ├─ Uses project_file_write to create implementation
  ├─ Uses project_task_create to track implementation tasks
  └─ Updates user_directives.db
  ↓
user_directive_approve (user tests implementation)
  ↓
user_directive_activate (deploy to real-time execution)
  ↓
user_directive_monitor (track execution stats)
  ↓
LOOP BACK to aifp_status
```

**User Directive System Directives**:
- `user_directive_parse` - Parse directive files
- `user_directive_validate` - Interactive validation
- `user_directive_implement` - Generate implementation code
- `user_directive_approve` - User approval workflow
- `user_directive_activate` - Deploy for execution
- `user_directive_monitor` - Track execution and errors
- `user_directive_update` - Handle directive file changes
- `user_directive_deactivate` - Stop execution
- `user_directive_status` - Report directive system status

---

## Directive Flow Navigation

### Using directive_flow Table

AI should query the `directive_flow` table to determine next steps based on current state:

**Core Helpers**:
- `get_next_directives_from_status(current_directive, state_object)` - Get possible next directives
- `get_conditional_work_paths(state_object)` - Get work paths based on conditions
- `get_completion_loop_target(completion_directive_name)` - Get loop-back target (always aifp_status)

**Example Query Flow**:
```
AI has status object cached
  ↓
User: "Add authentication"
  ↓
AI: get_next_directives_from_status("aifp_status", status_object)
  ↓
Returns:
  IF no incomplete items:
    - project_task_decomposition
    - project_task_create
  IF has incomplete items AND work related to request:
    - project_file_write
    - project_task_update
  ↓
AI selects: project_file_write (has related task)
  ↓
AI writes auth code, updates database
  ↓
AI: get_completion_loop_target("project_file_write")
  ↓
Returns: aifp_status (loop back)
```

---

## State Transition Summary

```
┌─────────────────────────────────────────────────────────────┐
│                   STATE TRANSITIONS                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Uninitialized → project_init → Initialized (no tasks)      │
│                                                              │
│  Initialized (no tasks) → project_task_decomposition →      │
│                            Active Work                       │
│                                                              │
│  Active Work → [work directives] → Item/Task/Milestone      │
│                                     Complete                 │
│                                                              │
│  Item/Task/Milestone Complete → project_*_complete →        │
│                                  LOOP BACK to aifp_status    │
│                                                              │
│  All Work Complete → project_completion_check →             │
│                      Complete OR Create More Work           │
│                                                              │
│  Complete → project_archive → Archived                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Flow Type Classifications

### 1. status_branch
**Definition**: Flow from aifp_status to next directive based on state
**Priority**: 100 (always highest)
**Example**: `aifp_status → project_init` (if not initialized)

### 2. completion_loop
**Definition**: Flow from completion directive back to aifp_status
**Priority**: 100 (mandatory loop-back)
**Example**: `project_task_complete → aifp_status`

### 3. conditional
**Definition**: Flow based on specific conditions
**Priority**: 80-90 (varies by importance)
**Example**: `aifp_status → project_task_decomposition` (if no tasks)

### 4. canonical
**Definition**: Standard workflow sequence
**Priority**: 70-80
**Example**: `project_init → project_blueprint_read`

### 5. error_handler
**Definition**: Flow to handle errors or roadblocks
**Priority**: 60-70
**Example**: `project_file_write → project_error_handling` (on failure)

---

## Next Steps for Mapping

With this comprehensive workflow path documented, the next phase is:

**Phase 1 Continuation**:
1. ✅ Comprehensive workflow documented (this file)
2. ⏳ Create `directive_flow.json` with 20-30 core flows
3. ⏳ Map completion loop-backs (all completion directives → aifp_status)
4. ⏳ Map conditional branches (state-based routing)

**Phase 2**: Map individual directives with helper usage

**Reference**: `docs/DIRECTIVE_HELPER_MAPPING_IMPLEMENTATION_PLAN.md`

---

## Validation Checklist

- [x] Entry point documented (aifp_run)
- [x] Status orchestrator documented (aifp_status)
- [x] All branches based on state documented
- [x] Loop-back pattern explained
- [x] Completion hierarchy detailed
- [x] Conditional paths documented
- [x] Git integration points identified
- [x] User directive automation flow documented
- [x] State transitions summarized
- [x] Flow type classifications defined

---

**Document Status**: ✅ Complete - Ready for directive_flow.json creation

**Created**: 2025-12-17
**Next**: Create directive_flow.json with core flows
