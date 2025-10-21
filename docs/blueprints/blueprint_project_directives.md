# Project Directives Blueprint

## Overview

Project directives manage the **lifecycle, organization, and completion** of AIFP-compliant projects. They orchestrate high-level workflows, coordinate database updates, and ensure project goals are achieved through a **finite completion path**.

### Core Philosophy

- **Level-Based Hierarchy**: Directives organized from orchestration (Level 0) to validation (Level 4)
- **Database-Driven**: All state persists in `project.db` for instant AI context retrieval
- **Completion-Oriented**: Every project has a **finite roadmap** to prevent endless development
- **FP Integration**: Project directives **call FP directives** for code compliance enforcement

---

## Directive Structure

### Format

Project directives exist in **three representations**:

1. **Compressed JSON** (`directives-project.json`) - Minimal, fast parsing for AI
2. **Detailed JSON** (individual directive files) - Complete workflow specifications
3. **Markdown** (escalation only) - Human-readable explanations for complex cases

### Standard Fields

```json
{
  "name": "project_init",
  "type": "project",
  "level": 0,
  "category": {
    "name": "initialization",
    "description": "Sets up project structure and databases"
  },
  "description": "Initialize AIFP project structure with databases and completion path",
  "workflow": {
    "trunk": "check_existing_project",
    "branches": [
      {"if": "project_exists", "then": "load_existing_state"},
      {"if": "new_project", "then": "create_aifp_structure"},
      {"if": "low_confidence", "then": "prompt_user", "details": {"clarify": "Project initialization unclear"}},
      {"fallback": "prompt_user", "details": {"log_note": true}}
    ],
    "error_handling": {"on_failure": "prompt_user"}
  },
  "roadblocks_json": [
    {"issue": "missing_permissions", "resolution": "Escalate to user for directory access"},
    {"issue": "conflicting_structure", "resolution": "Prompt user to confirm overwrite or merge"}
  ],
  "intent_keywords_json": ["init", "initialize", "setup", "new project"],
  "confidence_threshold": 0.8,
  "notes": "Links to project_structure_definition and database_init. First directive in chain.",
  "related_directives": {
    "project": ["project_structure_definition", "project_db_init"],
    "fp": []
  }
}
```

---

## Directive Levels

### Level 0: Root Orchestration
**Directives**: `project_init`, `project_run`

**Purpose**: High-level entry points that route user intent to appropriate workflows.

**Characteristics**:
- Parse natural language intent
- Route to specific directives based on keywords and context
- Initialize core systems (databases, file structure)
- Coordinate cross-directive workflows

**Example Flow**:
```
User: "Set up AIFP for my calculator project"
  → project_init
    → project_structure_definition
    → project_db_init
    → project_themes_init
    → project_completion_path_setup
```

### Level 1: High-Level Coordination
**Directives**: `project_task_decomposition`, `project_themes_flows_init`, `project_completion_path_setup`

**Purpose**: Break down goals into actionable structures and coordinate major workflows.

**Characteristics**:
- Decompose high-level goals into hierarchical tasks
- Create themes and flows for code organization
- Establish finite completion roadmap
- Link to multiple Level 2 directives

### Level 2: Operational Execution
**Directives**: `project_file_write`, `project_file_read`, `project_update_db`, `project_task_update`

**Purpose**: Execute concrete operations on files, databases, and project state.

**Characteristics**:
- Perform file I/O operations
- Update database tables
- Modify task/subtask/sidequest status
- Call FP directives for code compliance

**Cross-Directive Calls**:
- `project_file_write` → calls `fp_purity`, `fp_immutability` before writing
- `project_update_db` → updates `functions`, `interactions`, `types` tables

### Level 3: State Management
**Directives**: `project_compliance_check`, `project_evolution`, `project_metadata_sync`

**Purpose**: Maintain consistency between code, database, and organizational state.

**Characteristics**:
- Validate AIFP compliance across project
- Handle project pivots and goal changes
- Sync metadata between files and database
- Generate compliance reports

### Level 4: Validation & Completion
**Directives**: `project_completion_check`, `project_archival`

**Purpose**: Verify project completion and archive final state.

**Characteristics**:
- Validate all completion criteria met
- Check test coverage and documentation
- Archive project state to completion log
- Prevent post-completion modifications

---

## Workflow Patterns

### Branch Logic

All directives follow a **trunk → branches → fallback** pattern:

```json
"workflow": {
  "trunk": "primary_analysis_step",
  "branches": [
    {"if": "condition_met", "then": "action_to_take"},
    {"if": "alternative_condition", "then": "alternative_action"},
    {"if": "low_confidence", "then": "prompt_user", "details": {"clarify": "What AI is uncertain about"}},
    {"fallback": "prompt_user", "details": {"log_note": true}}
  ],
  "error_handling": {"on_failure": "prompt_user"}
}
```

**Key Patterns**:
- **low_confidence branch**: Always present when AI uncertainty is possible
- **fallback**: Catches all unhandled cases → prompts user
- **error_handling**: Defines behavior when directive execution fails
- **update_db branch**: Present when database updates are required

### Roadblocks

Common issues and their resolutions:

```json
"roadblocks_json": [
  {"issue": "database_locked", "resolution": "Retry with exponential backoff, max 3 attempts"},
  {"issue": "file_write_failed", "resolution": "Check permissions, prompt user if insufficient"},
  {"issue": "task_dependency_cycle", "resolution": "Break cycle by removing weakest dependency link"},
  {"issue": "theme_overlap_ambiguous", "resolution": "Escalate to project_themes_flows_init for restructuring"}
]
```

**Resolution Strategies**:
- **Automatic**: Retry, backoff, self-correction
- **Escalation**: Call another directive for specialized handling
- **User Prompt**: Request clarification or permission

---

## Database Integration

### Tables Used by Project Directives

| Directive | Tables Updated | Purpose |
|-----------|----------------|---------|
| `project_init` | `project`, `completion_path`, `milestones`, `infrastructure` | Initialize project structure with ProjectBlueprint.md |
| `aifp_status` | None (read-only) | Read project state for context-aware continuation |
| `project_task_decomposition` | `tasks`, `subtasks`, `items` | Break down work into actionable units |
| `project_file_write` | `files`, `functions`, `interactions` | Track written code and relationships |
| `project_theme_flow_mapping` | `themes`, `flows`, `flow_themes` | Link files to themes/flows, trigger blueprint updates |
| `project_update_db` | All tables | Generic database update handler |
| `project_evolution` | `project` (version, blueprint_checksum), `infrastructure`, `themes`, `flows` | Handle pivots and update ProjectBlueprint.md |
| `project_blueprint_update` | `project` (blueprint_checksum) | Update ProjectBlueprint.md sections |
| `project_compliance_check` | `functions` (read), `notes` (write) | Validate AIFP compliance |
| `project_completion_check` | `completion_path`, `milestones`, `tasks` | Verify completion criteria |

### Update Patterns

**Transactional Updates**:
```python
# project_file_write workflow
1. Begin transaction
2. Insert/update `files` table
3. Insert/update `functions` table
4. Insert `interactions` for dependencies
5. Call fp_purity, fp_immutability
6. If all pass → commit; else → rollback
```

**Cascading Updates**:
```python
# project_task_update workflow
1. Update task status
2. Check if all subtasks completed
3. If yes → auto-complete parent task
4. If milestone tasks all done → mark milestone complete
5. Update completion_path progress
```

---

## Intent Detection

### Confidence Thresholds

| Threshold | Meaning | Action |
|-----------|---------|--------|
| 0.9+ | Very High Confidence | Execute automatically |
| 0.7-0.9 | High Confidence | Execute with logging |
| 0.5-0.7 | Medium Confidence | Prompt user for confirmation |
| <0.5 | Low Confidence | Always prompt user |

### Intent Keywords

Each directive has **intent keywords** for routing:

```json
"intent_keywords_json": ["init", "initialize", "setup", "new project", "start"]
```

**`project_run` (master router)** matches user input against all directive keywords and routes accordingly.

---

## Cross-Directive Relationships

### Project → FP Links

Project directives **call FP directives** to enforce code standards:

- `project_file_write` → `fp_purity`, `fp_immutability`, `fp_side_effect_detection`
- `project_compliance_check` → All relevant FP directives for validation
- `project_task_decomposition` → `fp_function_decomposition` for implementation planning

### Project → Project Links

Hierarchical directive chaining:

```
aifp_run (L0)
  → aifp_status (L1)
    → project_blueprint_read (L2)
  → project_task_decomposition (L1)
    → aifp_status (L1) [for context before decomposing]
  → project_evolution (L4)
    → project_blueprint_update (L2)
  → project_theme_flow_mapping (L3)
    → project_evolution (L4) [when themes/flows change]
```

**New Cross-Directive Calls (Added)**:
- `aifp_run` → `aifp_status` (on continuation requests: "continue", "status", "resume")
- `project_task_decomposition` → `aifp_status` (check context before creating tasks)
- `project_theme_flow_mapping` → `project_evolution` (trigger blueprint update when themes/flows change)
- `aifp_status` → `project_blueprint_read` (read ProjectBlueprint.md for status context)
- `project_evolution` → `project_blueprint_update` (update blueprint sections on project-wide changes)

### Escalation to Markdown

When JSON workflow is insufficient (complex edge cases, ambiguous user intent), escalate to `.md` files for detailed human-readable instructions.

---

## Directive List

### Level 0 - Root Orchestration
- `aifp_run`: Gateway entry point for AIFP system, returns guidance and routes to appropriate directives

### Level 1 - Initialization & Status
- `project_init`: Initialize project structure with ProjectBlueprint.md creation and database setup
- `aifp_status`: Retrieve comprehensive project status with priority-based context (sidequests → subtasks → tasks)
- `project_task_decomposition`: Break goals into tasks → subtasks → items (calls aifp_status first for context)

### Level 2 - Operations & Helpers
- `project_add_path`: Create or update completion_path, milestones, and tasks
- `project_file_write`: Write code files with FP compliance
- `project_blueprint_read`: Read and parse ProjectBlueprint.md into structured data (helper)
- `project_blueprint_update`: Update specific sections of ProjectBlueprint.md (helper)

### Level 3 - Coordination
- `project_update_db`: Parse code and sync metadata with project.db
- `project_theme_flow_mapping`: Link files to themes/flows, triggers blueprint updates
- `project_dependency_sync`: Reconcile code dependencies with database records
- `project_auto_resume`: Resume interrupted tasks or workflows

### Level 4 - Validation & Evolution
- `project_compliance_check`: Validate AIFP compliance
- `project_evolution`: Handle project pivots, goal changes, and ProjectBlueprint.md updates
- `project_completion_check`: Verify completion criteria
- `project_error_handling`: Monitor directive execution failures
- `project_user_referral`: Delegate unresolved issues to user
- `project_metrics`: Track quantitative project progress
- `project_archival`: Archive completed project state

**Note**: See `docs/directives-json/directives-project.json` for complete directive specifications (25 total project directives).

---

## Notes Table Usage

The `notes` table is used extensively for:

1. **Clarifications**: When AI needs to remember context for future decisions
2. **Pivots**: When project goals change (logged by `project_evolution`)
3. **Roadblocks**: When directive encounters issue requiring future resolution
4. **Research**: When AI documents findings during code analysis

**Format**:
```sql
INSERT INTO notes (content, note_type, reference_table, reference_id)
VALUES
  ('User confirmed matrix multiplication is primary goal', 'clarification', 'project', 1),
  ('Pivoting from NumPy to pure Python implementation', 'pivot', 'project', 1),
  ('File permission issue on /protected/dir - needs user intervention', 'roadblock', 'files', 42);
```

---

## Completion Path

### Philosophy

Every AIFP project has a **finite completion path** to prevent endless development. This is tracked in the `completion_path` → `milestones` → `tasks` → `subtasks`/`items` hierarchy.

### Completion Criteria

**Milestone-Level**:
- All tasks under milestone are `completed`
- All subtasks resolved
- All sidequests merged back or abandoned

**Project-Level**:
- All milestones in completion path are `completed`
- Compliance check passes (`project_compliance_check`)
- Documentation complete
- Test coverage meets threshold

### Post-Completion

Once `project_completion_check` passes:
- Project marked as `completed` in `project` table
- `project_archival` logs final state
- Further modifications require explicit user consent and version increment

---

## Best Practices

1. **Always use low_confidence branches** for ambiguous scenarios
2. **Log to notes table** for future AI context retrieval
3. **Link directives explicitly** in `related_directives` field
4. **Use roadblocks for known issues** with clear resolution paths
5. **Keep compressed JSON minimal** (~50-100 chars per directive)
6. **Escalate to markdown only when necessary** (complex edge cases)
7. **Update database transactionally** to prevent inconsistent state
8. **Validate foreign keys** before insertions
9. **Use cascading deletes appropriately** (internal hierarchies only)
10. **Always check confidence thresholds** before auto-executing

---

## Example: project_file_write Workflow

```json
{
  "name": "project_file_write",
  "type": "project",
  "level": 2,
  "workflow": {
    "trunk": "validate_file_path_and_content",
    "branches": [
      {"if": "path_valid_and_content_ready", "then": "call_fp_directives_for_compliance"},
      {"if": "fp_compliance_passed", "then": "write_file_to_disk"},
      {"if": "file_written", "then": "update_database_tables"},
      {"if": "database_updated", "then": "mark_complete"},
      {"if": "fp_compliance_failed", "then": "refactor_code_and_retry"},
      {"if": "low_confidence", "then": "prompt_user", "details": {"clarify": "File write operation uncertain"}},
      {"fallback": "prompt_user", "details": {"log_note": true}}
    ],
    "error_handling": {"on_failure": "prompt_user"}
  },
  "related_directives": {
    "fp": ["fp_purity", "fp_immutability", "fp_side_effect_detection"],
    "project": ["project_update_db", "project_metadata_sync"]
  }
}
```

**Execution Flow**:
1. Validate file path exists and content is well-formed
2. Call `fp_purity`, `fp_immutability`, `fp_side_effect_detection`
3. If all FP directives pass → write file
4. Update `files`, `functions`, `interactions` tables
5. Call `project_metadata_sync` to ensure consistency
6. Return success/failure to caller

---

## Summary

Project directives are the **orchestration layer** of AIFP, managing:
- Project lifecycle from init to completion
- Task decomposition and tracking
- Database persistence and consistency
- Cross-directive coordination
- Finite completion enforcement

They work in tandem with **FP directives** (code standards) and **database schemas** (state persistence) to create a cohesive, AI-friendly development environment.
