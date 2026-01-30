# Implementation Plan: New Directives & System Prompt Update

**Date**: 2026-01-30
**Scope**: 4 new directives + system prompt lifecycle flow addition
**Dependencies**: Watchdog implementation (pending, accounted for in aifp_end design)

### Progress Summary

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Directive JSON Definitions | ✅ COMPLETE |
| 2 | Helper JSON Definitions | ✅ COMPLETE |
| 3 | Directive Flow Updates | ✅ COMPLETE |
| 4 | Directive MD Documentation | ✅ COMPLETE |
| 5 | System Prompt Update | ✅ COMPLETE |
| 6 | Helper Implementation (Code) | ✅ COMPLETE |
| 7 | Watchdog Consideration | ✅ COMPLETE |

**Overall**: 7/7 phases complete. All directive additions implemented.

---

## Table of Contents

1. [Problem Analysis](#1-problem-analysis)
2. [Solution Design](#2-solution-design)
3. [Directive Specifications](#3-directive-specifications)
4. [System Prompt Update](#4-system-prompt-update)
5. [Directive Flow Updates](#5-directive-flow-updates)
6. [Plan of Action](#6-plan-of-action)

---

## 1. Problem Analysis

### 1.1 Post-Init Gap (Project Discovery)

**Problem**: After `project_init` completes (Phase 1 mechanical setup + Phase 2 metadata detection), there is no structured directive guiding AI through the collaborative process of:
- Filling out the project blueprint in detail with the user
- Mapping infrastructure thoroughly
- Creating a well-considered completion path (not just a default placeholder)
- Breaking the completion path into meaningful milestones
- Establishing initial themes and flows

**Current behavior**: Phase 2 of `project_init` tells AI to "detect and prompt metadata" and creates a default completion path (`Project Setup & Core Development`). The flow then goes to `aifp_status` → `project_task_decomposition` if no tasks exist. This skips the critical conversation where AI and user map out the project shape together.

**Impact**: AI jumps from "project created" to "let's make tasks" without a structured understanding of what the project actually needs. The completion path, milestones, themes, and flows are either default placeholders or ad-hoc.

### 1.2 Progression State Machine (Project Progression)

**Problem**: The milestone → task → items incremental workflow is implicit across multiple directives (`project_task_decomposition`, `project_task_complete`, `project_milestone_complete`) and the system prompt hints at it, but no single directive codifies:
- One task (with items) created at a time per milestone
- On task completion → create next task for that milestone
- On milestone completion → open next milestone → create first task
- When themes/flows evolve → re-evaluate completion path and milestones
- Completion path progression as a formal state machine

**Current behavior**: `project_task_complete` flows to `project_milestone_complete` if all tasks are done, and `project_milestone_complete` loops back to `aifp_status`. But nothing says "now create the next task" or "now open the next milestone." AI must infer this from status data.

**Impact**: Risk of AI creating all tasks upfront (bulk decomposition) rather than the incremental one-task-at-a-time approach. No formal trigger for evolution review when themes/flows change.

### 1.3 Pre-Existing Codebase Cataloging (Project Catalog)

**Problem**: `project_init` Phase 2 has a single branch (`catalog_existing_fp_code`) with minimal guidance: "AI must scan all existing files and functions, then catalog them into project.db." For a large pre-existing codebase, this is a substantial operation requiring:
- Scanning every source file
- Identifying every function with parameters, return types, purity levels
- Mapping file-to-file and function-to-function interactions
- Inferring themes and flows from existing code organization
- Ensuring all data is correctly entered into the database

**Current behavior**: One-line instruction buried in `project_init`. No structured workflow, no guidance on order of operations, no handling of edge cases (large codebases, mixed patterns, partial FP compliance).

**Impact**: AI may skip or rush cataloging, resulting in incomplete database state from day one.

### 1.4 No Session End (aifp_end)

**Problem**: There is no concept of graceful session termination. Sessions just stop when the user closes the chat. Since MCP servers have no hook into session close events, there is no opportunity to:
- Verify all work is tracked in the database
- Ensure FP compliance of all code written during the session
- Update notes, completion path, milestones, task progress
- Close/stop the watchdog process
- Inform user that data state is consistent and safe to end

**Current behavior**: The workflow loops indefinitely (`aifp_status` → work → `aifp_status`). If AI wrote code but didn't update the database (edge case: context window filled, user stopped mid-workflow), the database is stale.

**Impact**: Risk of data drift between actual project state and database state. The watchdog (pending implementation) will catch some of this during sessions, but `aifp_end` provides the final comprehensive sweep.

---

## 2. Solution Design

### 2.1 project_discovery (New Directive)

**Type**: project, Level 1
**Parent**: project_init
**When triggered**: Immediately after `project_init` completes successfully (both phases)
**Purpose**: Structured conversational workflow for AI to collaborate with user on defining the full project shape

**Key design decisions**:
- Sits between `project_init` completion and first `project_task_decomposition`
- Flow: `project_init` → `project_discovery` → `aifp_status` (which then routes to task work)
- Replaces the current `project_init` → `aifp_status` → `project_task_decomposition` gap
- Handles both new empty projects and pre-existing FP projects (delegates to `project_catalog` for the latter)
- Outputs: populated blueprint, completion path with stages, milestones, initial themes and flows, infrastructure details

### 2.2 project_progression (New Directive)

**Type**: project, Level 2
**Parent**: aifp_status
**When triggered**: After any task/milestone completion event, or when themes/flows evolve
**Purpose**: Reference + orchestration directive that codifies the incremental progression state machine

**Key design decisions**:
- Acts as a **reference directive** (AI consults it for progression rules) AND an **orchestration point** (status routes through it after completions)
- Formalizes: task completion → next task creation, milestone completion → next milestone opening
- Includes evolution trigger: when `project_evolution` updates themes/flows, `project_progression` reviews completion path
- Does NOT replace existing completion directives — it augments them with "what comes next" logic
- The system prompt will include a brief lifecycle summary that points to this directive

### 2.3 project_catalog (New Directive)

**Type**: project, Level 1
**Parent**: project_discovery
**When triggered**: During `project_discovery` when pre-existing FP codebase detected
**Purpose**: Comprehensive cataloging of all existing code into project.db

**Key design decisions**:
- Called BY `project_discovery` (not by `project_init` directly — init detects existing code, discovery decides to catalog)
- Removes the `catalog_existing_fp_code` branch from `project_init` Phase 2 (replaced by this directive)
- Requires database and init setup to already be complete (depends on Phase 1)
- Structured workflow: scan files → identify functions → map interactions → infer themes → populate database
- Handles edge cases: large codebases (batch processing), partial FP compliance (flag impure functions), mixed file types

### 2.4 aifp_end (New Directive + Helper)

**Type**: project, Level 0 (same level as aifp_run — session lifecycle)
**Parent**: none (user-initiated)
**When triggered**: User explicitly requests session end, or AI detects session is ending
**Purpose**: Graceful session termination with comprehensive data audit

**Key design decisions**:
- Counterpart to `aifp_run(is_new_session=true)` — bookend pattern
- Helper: `aifp_end` orchestrator (similar to `aifp_run` — entry point helper)
- Directive: `aifp_end` directive workflow
- Watchdog integration: stops watchdog process, reads final reminders before clearing
- Audit steps: review all files written, verify DB entries, check FP compliance, update notes
- Output: session summary report to user confirming all is caught up
- Does NOT block user from closing chat without calling it — it's a best practice, not mandatory
- If watchdog is not yet implemented: skip watchdog steps gracefully (check for PID file existence)

---

## 3. Directive Specifications

### 3.1 project_discovery

```
Name: project_discovery
Type: project
Level: 1
Parent: project_init
Category: initialization
Description: Guided project discovery workflow. After init creates base files and
  databases, AI collaborates with user to define the full project shape: detailed
  blueprint, infrastructure mapping, completion path with stages, milestones,
  initial themes and flows. For pre-existing FP codebases, delegates to
  project_catalog before proceeding.

Workflow (trunk → branches):
  trunk: assess_project_state
  branches:
    1. if: pre_existing_fp_code_detected
       then: delegate_to_project_catalog
       details: Call project_catalog directive to scan and register all existing
         code before proceeding with discovery conversation

    2. if: catalog_complete_or_empty_project
       then: discuss_project_blueprint
       details:
         - Review current blueprint (template or partially filled from init Phase 2)
         - Discuss with user: project purpose, goals, scope, constraints
         - Fill out blueprint sections collaboratively
         - Update ProjectBlueprint.md via project_blueprint_update

    3. if: blueprint_populated
       then: map_infrastructure
       details:
         - Confirm/refine infrastructure entries from init Phase 2 detection
         - Discuss: language choices, build tools, testing strategy, deployment
         - Update infrastructure table with confirmed values
         - Discuss coding conventions, file organization patterns

    4. if: infrastructure_mapped
       then: define_themes_and_flows
       details:
         - Discuss project organization with user
         - Identify themes (logical groupings of functionality)
         - Identify flows (cross-cutting workflows/processes)
         - Create initial theme and flow entries in database
         - Update blueprint section 3

    5. if: themes_flows_defined
       then: create_completion_path
       details:
         - Discuss project stages with user (what are the major phases?)
         - Replace default completion path with user-informed path
         - Each stage should have clear entry/exit criteria
         - Update completion_path table

    6. if: completion_path_created
       then: create_milestones
       details:
         - For each stage in completion path, discuss milestones with user
         - Create milestone entries with descriptions and acceptance criteria
         - Do NOT create tasks yet — that happens during progression
         - Update milestones table

    7. if: milestones_created
       then: finalize_discovery
       details:
         - Backup blueprint
         - Log discovery completion in notes
         - Present summary to user: "Project shape defined. Ready to begin work."
         - Flow to aifp_status for first task creation via progression

Helpers used:
  - project_blueprint_update (update blueprint)
  - update_infrastructure_entry (infrastructure values)
  - create_theme, create_flow (themes/flows)
  - create_completion_path, create_milestone (project roadmap)
  - project_notes_log (log discovery decisions)

Related directives:
  - project_init (predecessor — must complete before discovery)
  - project_catalog (called during discovery for pre-existing codebases)
  - project_progression (successor — handles first task creation after discovery)
```

### 3.2 project_progression

```
Name: project_progression
Type: project
Level: 2
Parent: aifp_status
Category: task_management
Description: Codifies the incremental milestone/task/items state machine.
  Determines what to create next after completions. Ensures tasks are created
  one at a time per milestone, not in bulk. Triggers completion path review
  when themes or flows evolve.

Workflow (trunk → branches):
  trunk: assess_progression_state
  branches:
    1. if: milestone_just_completed
       then: open_next_milestone
       details:
         - Identify next milestone in completion path (by order_index)
         - Set its status to in_progress
         - Create FIRST task for that milestone (with items)
         - Do NOT create remaining tasks — they are created incrementally
         - If no next milestone: check if completion path stage is done
         - If stage done and more stages exist: open next stage's first milestone
         - If all stages done: route to project_completion_check

    2. if: task_just_completed
       then: create_next_task
       details:
         - Review milestone scope and remaining work
         - Determine what the next task should be based on:
           - Milestone description and acceptance criteria
           - What was just completed (context)
           - Current themes and flows
         - Create ONE new task with items for the active milestone
         - If milestone work is fully covered: do NOT create more tasks
           (milestone_complete will handle closure)

    3. if: themes_or_flows_evolved
       then: review_completion_path
       details:
         - project_evolution has updated themes/flows
         - Review current completion path against new project shape
         - Assess: do milestones still make sense?
         - Assess: does completion path need new stages?
         - If changes needed:
           - Add/modify milestones
           - Potentially add completion path stages
           - Update blueprint via project_blueprint_update
           - Log evolution impact in notes
         - If no changes needed: log "evolution reviewed, no path changes"

    4. if: no_active_tasks_in_milestone
       then: create_first_task
       details:
         - Active milestone has no tasks yet (fresh milestone opening)
         - Discuss with user or infer from milestone description
         - Create first task with items

    5. if: discovery_just_completed
       then: create_first_milestone_task
       details:
         - project_discovery just finished, first milestone is open
         - Create the very first task for the project
         - This is the entry point from discovery into active work

    fallback: route_to_status
    details: No progression action needed, return to aifp_status

Helpers used:
  - create_task, create_item (task creation)
  - update_milestone_status (milestone state changes)
  - get_project_status (assess current state)
  - project_notes_log (log progression decisions)

Related directives:
  - project_task_complete (triggers progression: task done → next task)
  - project_milestone_complete (triggers progression: milestone done → next milestone)
  - project_evolution (triggers progression: evolution → path review)
  - project_discovery (predecessor for first-time progression)
  - project_completion_check (successor when all stages done)
```

### 3.3 project_catalog

```
Name: project_catalog
Type: project
Level: 1
Parent: project_discovery
Category: initialization
Description: Comprehensive cataloging of an existing FP-compliant codebase into
  project.db. Scans all source files, identifies functions with metadata, maps
  interactions, and infers organizational structure. Called by project_discovery
  when pre-existing code is detected.

Workflow (trunk → branches):
  trunk: prepare_catalog_scan
  branches:
    1. if: source_directory_set
       then: scan_all_source_files
       details:
         - Read source_directory from infrastructure table
         - Recursively scan for source files (respect language-appropriate extensions)
         - Exclude: build artifacts, dependencies, generated files, .aifp-project/
         - Use same exclusion patterns as watchdog config (consistency)
         - Build file inventory: path, size, last_modified, extension

    2. if: files_scanned
       then: register_files_in_database
       details:
         - For each source file, create entry in files table
         - Use reserve → finalize pattern (get IDs, embed in names)
         - Set file metadata: path, purpose (infer from filename/location), theme (infer)
         - Batch processing for large codebases (process N files per batch)

    3. if: files_registered
       then: scan_functions_per_file
       details:
         - For each registered file, parse function definitions
         - Use language-appropriate patterns (same as watchdog function patterns)
         - For each function identify:
           - Name, parameters, return type (if typed)
           - Purity assessment (pure / has side effects / uncertain)
           - Purpose (infer from name and docstring if present)
         - Register functions in database with reserve → finalize pattern
         - Flag impure functions for user review (reminder, not blocker)

    4. if: functions_registered
       then: map_interactions
       details:
         - For each function, identify:
           - Which other functions it calls (within project)
           - Which files it imports from
           - External library dependencies
         - Create interaction entries in database
         - Build dependency graph

    5. if: interactions_mapped
       then: infer_themes_and_flows
       details:
         - Analyze file/directory structure for logical groupings → suggest themes
         - Analyze call patterns for cross-cutting workflows → suggest flows
         - Present inferred themes/flows to user for confirmation
         - These feed into project_discovery's theme/flow definition step

    6. if: catalog_complete
       then: report_catalog_summary
       details:
         - Report: files registered, functions registered, interactions mapped
         - Report: purity assessment summary (N pure, N impure, N uncertain)
         - Report: suggested themes and flows
         - Log completion in notes
         - Return to project_discovery flow

Edge cases:
  - Large codebase (>100 files): Process in batches, report progress
  - Mixed purity: Flag impure functions, do not abort
  - No functions in file: Register file only (config files, data files)
  - Unrecognized language: Use generic function patterns, warn user

Helpers used:
  - reserve_file, finalize_file (file registration)
  - reserve_function, finalize_function (function registration)
  - create_interaction (interaction mapping)
  - create_theme, create_flow (inferred organization)
  - project_notes_log (catalog progress)

Related directives:
  - project_discovery (parent — calls catalog when existing code detected)
  - project_init (predecessor — must complete before catalog)
  - project_progression (successor — after discovery completes)
```

### 3.4 aifp_end

```
Name: aifp_end
Type: project
Level: 0
Parent: none (user-initiated session lifecycle)
Category: session_management
Description: Graceful session termination. Comprehensive audit of all work done
  during the session, ensuring database state is consistent and up to date.
  Closes watchdog if running. Counterpart to aifp_run(is_new_session=true).

Workflow (trunk → branches):
  trunk: begin_session_audit
  branches:
    1. if: watchdog_running
       then: stop_watchdog_read_final_reminders
       details:
         - Read .aifp-project/watchdog/watchdog.pid
         - If PID exists and process alive: read final reminders.json
         - Process any outstanding reminders (unregistered files, missing functions)
         - Kill watchdog process
         - NOTE: If watchdog not implemented yet, skip gracefully
           (check PID file existence)

    2. if: session_has_file_writes
       then: verify_all_files_tracked
       details:
         - Review files written/modified during session
         - Cross-reference with files table in project.db
         - If any file missing from DB: register it
         - If any file has stale updated_at: correct it
         - Report discrepancies found and fixed

    3. if: session_has_code_changes
       then: verify_all_functions_tracked
       details:
         - For each file modified during session, scan for functions
         - Cross-reference with functions table in project.db
         - If any function missing from DB: register it
         - If any DB function missing from file: flag for review
         - Report discrepancies found and fixed

    4. if: code_verified
       then: check_fp_compliance
       details:
         - Quick FP scan of all code written during session
         - Check for: mutations, OOP patterns, unWrapped externals,
           missing Result types
         - Report violations (do not auto-fix — inform user)
         - Log compliance status in notes

    5. if: compliance_checked
       then: review_project_management_state
       details:
         - Check task/item progress: any items worked on but not updated?
         - Check notes: any important discussion points not logged?
         - Check completion path: does current progress match task state?
         - Check themes/flows: any new patterns that should be captured?
         - Check infrastructure: any changes to tools/dependencies?
         - Update anything that's stale

    6. if: state_reviewed
       then: generate_session_summary
       details:
         - Compile session summary:
           - Files created/modified
           - Functions added/modified
           - Tasks completed/progressed
           - Milestones progressed
           - Discrepancies found and fixed
           - FP compliance status
           - Outstanding items for next session
         - Log session summary in notes (source=directive, directive_name=aifp_end)

    7. if: summary_generated
       then: present_to_user
       details:
         - Display session summary to user
         - Confirm: "All project data is up to date. Safe to end session."
         - If outstanding issues: list them with severity
         - If clean: "Clean session end. No outstanding issues."

Helper: aifp_end (orchestrator)
  - File: helpers/orchestrators/entry_points.py
  - Parameters: project_root (string, required)
  - Purpose: Session termination orchestrator. Reads watchdog state, audits
    file/function tracking, checks FP compliance, reviews project management
    state, generates session summary.
  - Returns: {
      success: bool,
      watchdog_stopped: bool | null (null if not implemented),
      files_audited: int,
      functions_audited: int,
      discrepancies_found: int,
      discrepancies_fixed: int,
      fp_violations: [],
      session_summary: {
        files_created: int,
        files_modified: int,
        functions_added: int,
        tasks_completed: int,
        milestones_progressed: int,
        outstanding_items: []
      }
    }
  - is_tool: true
  - is_sub_helper: false
  - target_database: multi_db
  - used_by_directives: [{directive_name: "aifp_end"}]

Related directives:
  - aifp_run (counterpart — session start vs session end)
  - aifp_status (uses similar state gathering)
```

---

## 4. System Prompt Update

Add a new section after `=== ENTRY POINT: AUTOMATIC STARTUP BEHAVIOR ===` and before `=== FUNCTIONAL PROGRAMMING: YOUR MANDATORY CODING STYLE ===`:

```
=== PROJECT LIFECYCLE FLOW ===

After initialization, projects follow this lifecycle:

  init → discovery → [progression loop] → completion → end

1. **project_init**: Creates databases, templates, base files (Phase 1 mechanical + Phase 2 metadata detection)

2. **project_discovery**: AI collaborates with user to define the full project shape:
   - Populate project blueprint (purpose, goals, scope)
   - Map infrastructure (language, tools, conventions)
   - Define themes and flows (organizational structure)
   - Create completion path with stages and milestones
   - If pre-existing FP code: catalog via project_catalog first

3. **project_progression** (loop): Incremental work advancement:
   - ONE task (with items) created at a time per milestone
   - Task complete → create next task for milestone
   - Milestone complete → open next milestone → create first task
   - Themes/flows evolve → review completion path and milestones
   - Repeat until all stages complete

4. **project_completion_check** → **project_archive**: Validate and archive

5. **aifp_end**: Graceful session close — audit work, verify DB state, stop watchdog, confirm safe to end

**Key principle**: Tasks are created incrementally as work progresses, NOT all at once. Each completion triggers the next creation. Themes and flows evolve over time and may trigger completion path changes.
```

This is concise (~20 lines) and gives AI the mental model without duplicating directive detail.

---

## 5. Directive Flow Updates

### 5.1 Changes to `directive_flow_project.json`

**Remove** (replaced by project_discovery routing):
- None removed, but the `aifp_status → project_task_decomposition` flow (line 114-123) gets a modified condition (see below)

**Add new flows**:

```json
// project_init → project_discovery (NEW: init completes, go to discovery)
{
  "from_directive": "project_init",
  "to_directive": "project_discovery",
  "flow_type": "canonical",
  "condition_key": "initialization_successful",
  "condition_value": "true",
  "condition_description": "Initialization complete, proceed to project discovery",
  "priority": 100,
  "description": "After successful init, guide user through project discovery",
  "flow_category": "project"
}

// project_discovery → project_catalog (NEW: existing code needs cataloging)
{
  "from_directive": "project_discovery",
  "to_directive": "project_catalog",
  "flow_type": "conditional",
  "condition_key": "pre_existing_fp_code_detected",
  "condition_value": "true",
  "condition_description": "Existing FP-compliant codebase needs cataloging",
  "priority": 100,
  "description": "Catalog existing code before proceeding with discovery",
  "flow_category": "project"
}

// project_catalog → project_discovery (NEW: catalog done, resume discovery)
{
  "from_directive": "project_catalog",
  "to_directive": "project_discovery",
  "flow_type": "completion_loop",
  "condition_key": null,
  "condition_value": null,
  "condition_description": "Cataloging complete, resume discovery workflow",
  "priority": 100,
  "description": "Existing code cataloged, continue project discovery",
  "flow_category": "project"
}

// project_discovery → aifp_status (NEW: discovery complete)
{
  "from_directive": "project_discovery",
  "to_directive": "aifp_status",
  "flow_type": "completion_loop",
  "condition_key": "discovery_complete",
  "condition_value": "true",
  "condition_description": "Project shape fully defined, milestones created",
  "priority": 100,
  "description": "Discovery complete, status will route to progression for first task",
  "flow_category": "project"
}

// aifp_status → project_progression (NEW: after completions or no active tasks)
{
  "from_directive": "aifp_status",
  "to_directive": "project_progression",
  "flow_type": "conditional",
  "condition_key": "progression_action_needed",
  "condition_value": "true",
  "condition_description": "Task/milestone just completed, or active milestone has no tasks, or discovery just completed",
  "priority": 85,
  "description": "Determine next work item via progression state machine",
  "flow_category": "project"
}

// project_progression → aifp_status (NEW: progression action taken)
{
  "from_directive": "project_progression",
  "to_directive": "aifp_status",
  "flow_type": "completion_loop",
  "condition_key": null,
  "condition_value": null,
  "condition_description": "Next task created or milestone opened",
  "priority": 100,
  "description": "Progression action complete, return to status for work",
  "flow_category": "project"
}

// project_evolution → project_progression (NEW: evolution triggers path review)
{
  "from_directive": "project_evolution",
  "to_directive": "project_progression",
  "flow_type": "conditional",
  "condition_key": "themes_or_flows_changed",
  "condition_value": "true",
  "condition_description": "Themes or flows evolved, review completion path",
  "priority": 90,
  "description": "Evolution may require completion path adjustments",
  "flow_category": "project"
}

// aifp_status → aifp_end (NEW: user requests session end)
{
  "from_directive": "aifp_status",
  "to_directive": "aifp_end",
  "flow_type": "conditional",
  "condition_key": "user_requests_session_end",
  "condition_value": "true",
  "condition_description": "User explicitly requests to end the session",
  "priority": 100,
  "description": "Graceful session termination with comprehensive audit",
  "flow_category": "project"
}

// aifp_end → (terminal) (NEW: session ends, no loop back)
// Note: aifp_end is terminal — it does not loop back to aifp_status.
// The session is over after aifp_end completes.
```

### 5.2 Modify Existing Flows

**Change**: `project_init → aifp_status` completion loop (lines 92-101)
- **Before**: `project_init` → `aifp_status` (on success)
- **After**: `project_init` → `project_discovery` (on success)
- Keep the error handler flow (`project_init` → `aifp_status` on OOP detected)

**Change**: `aifp_status → project_task_decomposition` (lines 114-123)
- **Before**: condition is `has_incomplete_tasks = false` (no tasks exist)
- **After**: condition should also check that discovery is complete. If discovery hasn't been done yet, status should route to `project_discovery` instead. Add condition: `discovery_complete = true AND has_incomplete_tasks = false`
- Alternatively: `project_progression` now handles first task creation after discovery, so this flow may become less critical (progression handles the "no tasks" case for active milestones)

### 5.3 Flow Summary (Post-Change)

```
SESSION START:
  aifp_run(is_new_session=true) → aifp_status → git_detect_external_changes

INITIALIZATION (new project):
  aifp_status → project_init → project_discovery → aifp_status
  (with project_catalog called during discovery if existing code)

WORK LOOP:
  aifp_status → project_progression → aifp_status → project_file_write → ...
  (progression creates tasks incrementally, status routes to work)

COMPLETION EVENTS:
  project_task_complete → aifp_status → project_progression (creates next task)
  project_milestone_complete → aifp_status → project_progression (opens next milestone)

EVOLUTION:
  project_evolution → project_progression (reviews path) → aifp_status

SESSION END:
  aifp_status → aifp_end (terminal)
```

---

## 6. Plan of Action

### Phase 1: Directive JSON Definitions ✅ COMPLETE

| Task | File | Status |
|------|------|--------|
| 1.1 | `docs/directives-json/directives-project.json` | ✅ Added `project_discovery` directive definition |
| 1.2 | `docs/directives-json/directives-project.json` | ✅ Added `project_progression` directive definition |
| 1.3 | `docs/directives-json/directives-project.json` | ✅ Added `project_catalog` directive definition |
| 1.4 | `docs/directives-json/directives-project.json` | ✅ Added `aifp_end` directive definition |
| 1.5 | `docs/directives-json/directives-project.json` | ✅ Modified `project_init` — removed `catalog_existing_fp_code` branch, updated completion flow to route to `project_discovery` |

### Phase 2: Helper JSON Definitions ✅ COMPLETE

| Task | File | Status |
|------|------|--------|
| 2.1 | `docs/helpers/json/helpers-orchestrators.json` | ✅ Added `aifp_end` helper definition (JSON spec only) |

Note: `project_discovery`, `project_progression`, and `project_catalog` are directive-driven workflows that use existing helpers (create_task, create_milestone, reserve_file, etc.). They do not need new dedicated helpers — they compose existing ones. `aifp_end` needs a new orchestrator helper because it's an entry point (like `aifp_run` and `aifp_init`).

**⚠️ PENDING**: `aifp_end` Python implementation in `src/aifp/helpers/orchestrators/entry_points.py` is tracked in Phase 6, task 6.1. The JSON definition includes `"implementation_status": "NOT_IMPLEMENTED"` to flag this.

### Phase 3: Directive Flow Updates ✅ COMPLETE

| Task | File | Status |
|------|------|--------|
| 3.1 | `docs/directives-json/directive_flow_project.json` | ✅ Added 8 new flow entries (discovery↔catalog, discovery→status, status↔progression, evolution→progression, status→end, status→discovery) |
| 3.2 | `docs/directives-json/directive_flow_project.json` | ✅ Modified `project_init → aifp_status` to `project_init → project_discovery` (canonical flow) |
| 3.3 | `docs/directives-json/directive_flow_project.json` | ✅ Modified `aifp_status → project_task_decomposition` — lowered priority to 70, added note that progression handles normal flow |
| 3.4 | `docs/directives-json/directive_flow_project.json` | ✅ Updated metadata: version 1.3.0, total_flows 95, added coverage entries and v1.3.0 changelog notes |

### Phase 4: Directive MD Documentation ✅ COMPLETE

| Task | File | Status |
|------|------|--------|
| 4.1 | `src/aifp/reference/directives/project_discovery.md` | ✅ Created |
| 4.2 | `src/aifp/reference/directives/project_progression.md` | ✅ Created |
| 4.3 | `src/aifp/reference/directives/project_catalog.md` | ✅ Created |
| 4.4 | `src/aifp/reference/directives/aifp_end.md` | ✅ Created |
| 4.5 | `src/aifp/reference/directives/project_init.md` | ✅ Updated — removed catalog branch, added discovery routing |

### Phase 5: System Prompt Update ✅ COMPLETE

| Task | File | Status |
|------|------|--------|
| 5.1 | `sys-prompt/aifp_system_prompt.txt` | ✅ Added `=== PROJECT LIFECYCLE FLOW ===` section |
| 5.2 | `sys-prompt/aifp_system_prompt.txt` | ✅ Added `aifp_end` to session-essential helpers list |
| 5.3 | `sys-prompt/aifp_system_prompt.txt` | ✅ Added behavioral rule #7 "Session End Best Practice", renumbered existing rules |

### Phase 6: Helper Implementation (Code) ✅ COMPLETE

| Task | File | Status |
|------|------|--------|
| 6.1 | `src/aifp/helpers/orchestrators/entry_points.py` | ✅ Implemented `aifp_end` helper + `_stop_watchdog` with TODO for watchdog integration |

Note: No code changes needed for the three directive-only additions (discovery, progression, catalog). They are AI behavioral directives that compose existing helpers. The `aifp_end` helper is the only new code.

### Phase 7: Watchdog Consideration ✅ COMPLETE

| Task | File | Status |
|------|------|--------|
| 7.1 | `src/aifp/helpers/orchestrators/entry_points.py` | ✅ `_stop_watchdog()` stubbed with TODO — ready for watchdog integration |
| 7.2 | `docs/WATCHDOG_IMPLEMENTATION_PLAN.md` | ✅ Added "Integration Notes" section with `aifp_end` shutdown requirements |

The `aifp_end` helper should be written with watchdog integration points stubbed: check for PID file existence, if found attempt stop, if not found skip gracefully. This ensures `aifp_end` works both before and after watchdog implementation.

### Execution Order

1. **Phase 1** (directive JSON) — must come first, defines the specifications
2. **Phase 2** (helper JSON) — depends on directive specs being finalized
3. **Phase 3** (directive flows) — depends on directive names being finalized
4. **Phase 4** (MD docs) — can parallel with Phase 3
5. **Phase 5** (system prompt) — depends on directive names and flow being finalized
6. **Phase 6** (code) — depends on helper JSON spec being finalized
7. **Phase 7** (watchdog notes) — independent, can happen anytime

---

## Notes

- **Watchdog**: Not yet implemented but accounted for in `aifp_end` design. The helper will check for watchdog PID file and gracefully skip if not present. When watchdog is built, `aifp_end` gains automatic integration.
- **project_task_decomposition**: Still exists and is still useful for ad-hoc task creation requests from users. `project_progression` handles the incremental "what's next" flow; `project_task_decomposition` handles "user explicitly asks to break down work."
- **Backward compatibility**: Existing projects without discovery/progression will work fine — `aifp_status` still routes based on project state. These new directives enhance the flow but don't break existing state machines.
- **Directive flow JSON version**: Should be bumped to 1.3.0 after all flow changes.
