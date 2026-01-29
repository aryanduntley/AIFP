# Orchestrator Implementation Plan

**Status**: COMPLETE — All 10 helpers implemented across 4 files + _common.py
**Date**: 2026-01-28
**Scope**: 10 helpers across 4 files (reduced from 13; validate_initialization removed — AI responsibility)

---

## Key Principle

Orchestrators are **data aggregation** helpers — they query multiple tables and assemble structured data for AI to act on. They do NOT make decisions, analyze, recommend, or execute workflows. The **directives** tell AI what to do; the orchestrators give AI the data it needs to follow those directives.

Return statements are critical for orchestrators because they chain into AI-driven workflows.

---

## Decisions Made (Session 2026-01-28)

### REMOVED: `get_status_tree` (was in status.py)
- **Reason**: Redundant with `get_project_status`. Both query the same work hierarchy tables; `get_status_tree` just nests the data differently. Fold tree-building logic into `get_project_status` so it returns both flat counts AND nested tree in one pass.
- **Impact**: `aifp_status` no longer calls `get_status_tree` separately — it gets tree data from `get_project_status`.
- **Files referencing `get_status_tree` that need updating**:
  - `docs/helpers/json/helpers-orchestrators.json` — remove helper entry + remove from aifp_status used_by
  - `docs/HELPER_IMPLEMENTATION_PLAN.md` — remove from Phase 2 orchestrators checklist
  - `src/aifp/reference/directives/aifp_status.md` — remove references (2 occurrences: line ~206 "Calls" section and line ~524 helper functions section)
  - Other docs files (deprecated/reference, low priority): `docs/helpers/project-helpers-analysis-recommendations.md`, `docs/helpers/REGISTRY_VS_CONSOLIDATED_COMPARISON.md`, `docs/COMPLETE/helpers/helper-functions-reference.md`, `docs/PHASE_8_HELPER_MAPPING_STRATEGY.md`, `docs/helpers/USED_BY_DIRECTIVES_CHECKLIST.md`

### REMOVED: `get_project_context` (was in query.py)
- **Reason**: Every type is redundant with existing capabilities:
  - `type='blueprint'` → AI can read files directly, no helper needed
  - `type='metadata'` → `get_from_project([1])` on project table (existing CRUD helper)
  - `type='status'` → `get_project_status` / `aifp_status` (existing orchestrators)
  - `type='infrastructure'` → `get_all_infrastructure()` (existing project helper)
- **Impact**: `aifp_help` directive referenced this; it should use existing helpers directly instead.
- **Files referencing `get_project_context` that need updating**:
  - `docs/helpers/json/helpers-orchestrators.json` — remove helper entry
  - `docs/HELPER_IMPLEMENTATION_PLAN.md` — remove from Phase 2 orchestrators checklist
  - `README.md` — remove from available_helpers list (line ~324)
  - `src/aifp/reference/directives/aifp_run.md` — remove from available_helpers list (2 occurrences)
  - Other docs files (deprecated/reference, low priority): `docs/helpers/project-helpers-analysis-recommendations.md`, `docs/helpers/REGISTRY_VS_CONSOLIDATED_COMPARISON.md`, `docs/COMPLETE/helpers/helper-functions-reference.md`, `docs/PHASE_8_HELPER_MAPPING_STRATEGY.md`, `docs/blueprints/blueprint_mcp.md`, `docs/GUIDES-WORKFLOW-ANALYSIS.md`, `docs/IMPLEMENTATION-PLAN-DIRECTIVE-MD-FILES.md`, `docs/helpers/USED_BY_DIRECTIVES_CHECKLIST.md`

### RENAMED: `target_database` field values in schema and JSON
- **Current values**: `'orchestrator'` and `'system'`
- **Problem**: AI on fresh context may think `orchestrator` is a database file. `system` is vague.
- **New values**: `'multi_db'` and `'no_db'`
- **Full CHECK constraint becomes**:
  ```sql
  target_database TEXT CHECK (target_database IN (
      'core',              -- aifp_core.db (directives, helpers, directive_flow)
      'project',           -- project.db (single-database CRUD operations)
      'user_preferences',  -- user_preferences.db (settings and preferences)
      'user_directives',   -- user_directives.db (user-defined automation)
      'multi_db',          -- Multi-database operations (orchestrators that coordinate across databases)
      'no_db'              -- Non-database operations (git, filesystem, validation utilities)
  )) NOT NULL
  ```
- **Files that need updating**:
  - `src/aifp/database/schemas/aifp_core.sql` — lines 137-144: change CHECK constraint
  - `src/aifp/helpers/core/validation.py` — line 77: change validation tuple from `('core', 'project', 'user_preferences', 'user_directives', 'orchestrator', 'system')` to `('core', 'project', 'user_preferences', 'user_directives', 'multi_db', 'no_db')`
  - `docs/helpers/json/helpers-orchestrators.json` — all entries: change `"target_database": "orchestrator"` to correct value per helper (see classification below)
  - `docs/helpers/json/helpers-git.json` — if any use `"system"`, change to `"no_db"` (need to verify)
  - Any JSON files in `docs/helpers/json/` using `"orchestrator"` or `"system"` as target_database values

### target_database Classification for Each Orchestrator Helper

| Helper | Databases actually used | target_database value |
|--------|------------------------|----------------------|
| `aifp_init` | project.db + user_preferences.db (creates both) | `multi_db` |
| `aifp_run` | project.db + user_preferences.db + core.db | `multi_db` |
| `aifp_status` | project.db + user_preferences.db + user_directives.db | `multi_db` |
| `validate_initialization` | project.db + user_preferences.db (checks both) | `multi_db` |
| `get_project_status` | project.db only | `project` |
| `get_task_context` | project.db only | `project` |
| `get_current_progress` | project.db only | `project` |
| `update_project_state` | project.db only | `project` |
| `batch_update_progress` | project.db only | `project` |
| `query_project_state` | project.db only | `project` |
| `get_files_by_flow_context` | project.db only | `project` |

---

## File Organization (Updated)

| File | Helpers | Purpose |
|------|---------|---------|
| `entry_points.py` | `aifp_init`, `aifp_run`, `aifp_status` | Top-level entry points called directly by directives |
| `status.py` | `get_project_status`, `get_task_context` | Project state retrieval (tree logic folded into get_project_status) |
| `state.py` | `get_current_progress`, `update_project_state`, `batch_update_progress` | Flexible state queries and updates |
| `query.py` | `query_project_state`, `get_files_by_flow_context` | Advanced queries (validate_initialization removed — AI responsibility) |

---

## Helper-by-Helper Analysis

### 1. `aifp_init` (entry_points.py) — target_database: `multi_db`

**Called by**: `project_init` directive (Phase 1: Mechanical Setup)

**What it does**: Atomically creates directories, databases with schemas, and template files. Pure mechanical operations — no intelligence.

**What it does NOT do**: OOP scanning, language detection, user prompting, infrastructure population, state DB creation — all of that is Phase 2, handled by AI following the `project_init` directive.

**IMPORTANT**: The `project_init` **directive** (not this helper) tells AI to check for existing state first:
- If `.aifp-project/` exists → call `aifp_status` instead (already initialized)
- If existing code detected → scan for OOP patterns → abort if OOP detected with message telling user AIFP is FP-only and to uninstall MCP server
- If existing FP code → proceed with init, then AI logs existing files/functions into project.db
- If empty project → proceed with clean init

This helper only handles the mechanical Phase 1. AI handles all pre-flight checks BEFORE calling this helper.

**Steps**:
1. Validate project_root exists and is a directory
2. Check if `.aifp-project/project.db` already exists → error if yes
3. Create `.aifp-project/` directory
4. Create `.aifp-project/backups/` directory
5. Copy `ProjectBlueprint_template.md` → `.aifp-project/ProjectBlueprint.md`
6. Create `project.db`: execute `schemas/project.sql`, then `initialization/standard_infrastructure.sql`, then update project_root value
7. Create `user_preferences.db`: execute `schemas/user_preferences.sql`, then INSERT default tracking_settings (all 5 features, all disabled)
8. Create `.aifp-project/.gitkeep`
9. Call `validate_initialization()` to verify everything
10. Return result

**Parameters**: `project_root: str`

**Returns**:
```python
@dataclass(frozen=True)
class InitResult:
    success: bool
    project_root: str = ""
    aifp_dir: str = ""
    files_created: Tuple[str, ...] = ()
    tables_created_project: Tuple[str, ...] = ()
    tables_created_preferences: Tuple[str, ...] = ()
    infrastructure_entries: int = 0
    error: Optional[str] = None
    failed_step: Optional[int] = None
    cleanup_performed: bool = False
    return_statements: Tuple[str, ...] = ()
```

**Return statements** (critical for chaining):
- "Phase 1 complete. AI must now execute Phase 2: scan for OOP patterns (if existing code), detect infrastructure (language, build tool, source directory), and prompt user for project name/purpose/goals."
- "Empty infrastructure entries created: project_root (populated), source_directory, primary_language, build_tool, package_manager, test_framework, runtime_version, main_branch. AI must detect and populate these values."
- "ProjectBlueprint.md is a template with placeholders. AI must populate with real project data after user interaction."
- "After source_directory is populated: AI must create state database at {source_dir}/.state/ using templates/state_db/ files."
- "After all population complete: create initial completion_path, prompt for Use Case 2 (user directives), initialize git if needed, backup blueprint."

**Error handling**: If any step fails after directory creation, delete `.aifp-project/` entirely (shutil.rmtree). Return error with failed_step number.

**Dependencies**:
- `validate_initialization` (called at step 9)
- Schema SQL files (read from `src/aifp/database/schemas/`)
- Infrastructure SQL (read from `src/aifp/database/initialization/`)
- Blueprint template (read from `src/aifp/templates/`)

**Missing prerequisite**: `ProjectBlueprint_template.md` does not exist yet in `src/aifp/templates/`. Must be created before aifp_init can be coded. Template should have placeholder sections matching the AIFP project blueprint structure (Project Overview, Technical Blueprint, Themes & Flows, Completion Path).

---

### 2. `aifp_run` (entry_points.py) — target_database: `multi_db`

**Called by**: `aifp_run` directive (every interaction)

**What it does**: Returns static guidance to AI. For new sessions, bundles startup data (status + settings + directive index). For continuation, returns lightweight guidance.

**What it does NOT do**: Parse user intent, execute directives, make decisions.

**Parameters**: `project_root: str`, `is_new_session: bool = False`

**Logic**:
- If `is_new_session=True`:
  - Call `aifp_status(project_root, type="summary")`
  - Call `get_user_settings(db_path)` (from user_preferences helpers)
  - Query core DB for FP directive names grouped by category
  - Query core DB for all directive names
  - Call `get_all_infrastructure(db_path)` (from project helpers)
  - Bundle all data + static guidance
- If `is_new_session=False`:
  - Return lightweight guidance object with common starting points

**Returns**:
```python
@dataclass(frozen=True)
class RunResult:
    success: bool
    is_new_session: bool = False
    status: Optional[Dict] = None           # aifp_status result (new session only)
    user_settings: Tuple[Dict, ...] = ()    # user settings (new session only)
    fp_directive_index: Dict[str, Tuple[str, ...]] = None  # category -> names (new session only)
    all_directive_names: Tuple[str, ...] = ()  # all directive names (new session only)
    infrastructure: Tuple[Dict, ...] = ()   # infrastructure entries (new session only)
    guidance: Dict[str, Any] = None         # static guidance (always)
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()
```

**Return statements**:
- "If user_setting project_continue_on_start=true and is_new_session=true: automatically continue project work with bundled context."
- "When autostart enabled: load pending tasks from status, present with priority order, proactively suggest next steps."

**Dependencies**: `aifp_status`, user_preferences helpers (`get_user_settings`), project helpers (`get_all_infrastructure`), core helpers (`get_fp_directive_index`, `get_all_directive_names`)

**Note**: This helper calls other helpers internally. Uses existing helpers from core, project, and user_preferences modules.

---

### 3. `aifp_status` (entry_points.py) — target_database: `multi_db`

**Called by**: `aifp_status` directive, `aifp_run` (for session bundles)

**What it does**: Retrieves comprehensive project state from multiple sources. Assembles structured status data for AI to interpret.

**What it does NOT do**: Analyze status, recommend actions, make decisions.

**Parameters**: `project_root: str`, `type: str = "summary"` (quick/summary/detailed)

**Logic**:
1. Check if `.aifp-project/` exists → if not, return `{initialized: false}`
2. Call `validate_initialization(project_root)` for structural health check
3. Call `get_project_status(project_root, type)` for work hierarchy data (now includes tree)
4. Read project metadata from project table
5. Read infrastructure from infrastructure table
6. Check `project.user_directives_status` for Use Case determination
7. If Use Case 2 + active: query user_directives.db for active directive counts
8. Read recent notes (limit 5, severity warning/error)
9. Get git state from work_branches table

**Returns**:
```python
@dataclass(frozen=True)
class StatusResult:
    success: bool
    initialized: bool = False
    project_metadata: Optional[Dict] = None
    infrastructure: Tuple[Dict, ...] = ()
    work_hierarchy: Optional[Dict] = None        # from get_project_status (includes counts + tree)
    user_directives_status: Optional[str] = None  # NULL, in_progress, active, disabled
    active_directive_count: int = 0
    recent_warnings: Tuple[Dict, ...] = ()
    git_state: Optional[Dict] = None
    validation: Optional[Dict] = None            # from validate_initialization
    type: str = "summary"
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()
```

**Return statements**:
- "AI should interpret status data and determine next directive to execute based on project state."
- "If not initialized: AI should prompt user to run project_init."
- "If validation has errors: AI should address structural issues before continuing work."
- "Priority order for current focus: sidequests → subtasks → tasks."

**Dependencies**: `validate_initialization`, `get_project_status`, project helpers, user_preferences helpers, optionally user_directives helpers

---

### 4. `get_project_status` (status.py) — target_database: `project`

**Called by**: `aifp_status`, also available as direct AI tool for in-session use

**What it does**: Queries work hierarchy tables (completion_path, milestones, tasks, subtasks, sidequests, items) and returns counts + relevant records + nested tree structure based on detail level.

**Note**: Tree-building logic (formerly `get_status_tree`) is now folded into this helper. Single pass over the data, returns both flat counts and nested tree.

**Parameters**: `project_root: str`, `type: str = "summary"`

**Logic by type**:
- **quick**: Counts only (pending/in_progress/completed per table) + current in_progress item
- **summary**: Incomplete items + last 5 completed items per level + counts + tree
- **detailed**: All items including full completed history + complete tree

**Returns**:
```python
@dataclass(frozen=True)
class ProjectStatusResult:
    success: bool
    counts: Optional[Dict] = None          # {completion_paths: {total, pending, in_progress, completed}, milestones: {...}, ...}
    completion_paths: Tuple[Dict, ...] = ()
    milestones: Tuple[Dict, ...] = ()
    tasks: Tuple[Dict, ...] = ()
    subtasks: Tuple[Dict, ...] = ()
    sidequests: Tuple[Dict, ...] = ()
    blocked_items: Tuple[Dict, ...] = ()
    tree: Optional[Dict] = None            # nested: {completion_paths: [{milestones: [{tasks: [{subtasks: [...]}]}]}], sidequests: [...]}
    error: Optional[str] = None
```

**No return statements** (data-only helper, called by aifp_status which has its own return statements)

---

### 5. `get_task_context` (status.py) — target_database: `project`

**Called by**: `project_auto_resume` directive

**What it does**: Gets full context for a specific work item (task/subtask/sidequest) including associated flows, files, functions, and optionally interactions and history notes. This is a deep dive on ONE work item, unlike `get_project_status` which is a broad overview.

**Parameters**: `project_root: str`, `task_type: str`, `task_id: int`, `include_interactions: bool = False`, `include_history: bool = False`

**Logic**:
1. Query the work item by type + id (tasks/subtasks/sidequests table)
2. Get associated items from items table
3. Get flows linked to the work item's parent or direct associations
4. Get files from file_flows for those flows
5. Get functions for those files
6. If include_interactions: get interactions for those functions
7. If include_history: get notes for this work item

**Returns**:
```python
@dataclass(frozen=True)
class WorkContextResult:
    success: bool
    work_item: Optional[Dict] = None
    items: Tuple[Dict, ...] = ()
    flows: Tuple[Dict, ...] = ()
    files: Tuple[Dict, ...] = ()
    functions: Tuple[Dict, ...] = ()
    interactions: Tuple[Dict, ...] = ()  # if requested
    notes: Tuple[Dict, ...] = ()         # if requested
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()
```

**Return statements**:
- "Work context loaded. AI should review items to determine where to resume."
- "If work item is blocked: check blocked_by field and resolve blockers first."

---

### 6. `get_current_progress` (state.py) — target_database: `project`

**Called by**: Generic tool — flexible status query entry point

**What it does**: Single entry point for scoped project status queries. Replaces 5-10 separate helper calls.

**Parameters**: `project_root: str`, `scope: str = None`, `detail_level: str = "standard"`, `filters: Dict = None`

**Scope values**: "tasks", "milestones", "completion_paths", "files", "functions", "flows", "themes", "infrastructure", "all"

**Logic**: Routes to appropriate table queries based on scope, applies filters, returns at requested detail level.

**Returns**: `QueryResult` with rows from the appropriate scope.

**No return statements** (utility query)

---

### 7. `update_project_state` (state.py) — target_database: `project`

**Called by**: Generic tool — simplified state transition interface

**What it does**: Performs common state transitions on project entities (start_task, complete_task, pause_task, etc.) with optional auto-note creation.

**Parameters**: `project_root: str`, `action: str`, `target_type: str`, `target_id: int`, `data: Dict = None`, `create_note: bool = False`

**Actions**: start_task, complete_task, pause_task, resume_task, block_task, unblock_task, start_subtask, complete_subtask, etc.

**Logic**: Maps action to appropriate field updates (status, timestamps), executes UPDATE, optionally creates note.

**Returns**:
```python
@dataclass(frozen=True)
class StateUpdateResult:
    success: bool
    updated_entity: Optional[Dict] = None
    note_created: bool = False
    note_id: Optional[int] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()
```

**Return statements**:
- "State updated. If task completed: check if all tasks in milestone are complete, consider marking milestone complete."
- "If task blocked: create sidequest to resolve blocker, then unblock and resume."

---

### 8. `batch_update_progress` (state.py) — target_database: `project`

**Called by**: Post-code-generation bulk updates

**What it does**: Atomically updates multiple project items. Used after AI generates code (multiple files/functions at once).

**Parameters**: `project_root: str`, `updates: List[Dict]`, `transaction: bool = True`, `continue_on_error: bool = False`

**Each update**: `{target_type: str, target_id: int, action: str, data: Dict}`

**Logic**: Iterates updates, calls `update_project_state` for each. If transaction=True, wraps in DB transaction.

**Returns**:
```python
@dataclass(frozen=True)
class BatchUpdateResult:
    success: bool
    updated_count: int = 0
    failed_count: int = 0
    results: Tuple[Dict, ...] = ()  # per-update results
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()
```

**Return statements**:
- "Batch update complete. Review any failures and retry individually if needed."

---

### 9. `query_project_state` (query.py) — target_database: `project`

**Called by**: Generic tool — flexible SQL-like query interface

**What it does**: Provides structured query interface without raw SQL. Supports filtering, joins, sorting, pagination.

**Parameters**: `project_root: str`, `entity: str`, `filters: Dict = None`, `joins: List[str] = None`, `sort: str = None`, `limit: int = None`, `offset: int = None`

**Filter operators**: eq, ne, gt, lt, gte, lte, in, like

**Joins**: Predefined join mappings (e.g., entity="tasks" + joins=["milestones"] → LEFT JOIN milestones ON tasks.milestone_id = milestones.id)

**Returns**: `QueryResult` with rows

**No return statements** (utility query)

---

### 10. `validate_initialization` (query.py) — target_database: `multi_db`

**Called by**: `aifp_init` (step 9), `aifp_status` (health check)

**What it does**: Validates that project initialization is structurally complete and correct.

**Parameters**: `project_root: str`

**Checks**:
1. `.aifp-project/` directory exists
2. `project.db` exists and has expected tables (20 tables)
3. `user_preferences.db` exists and has expected tables (7 tables)
4. `ProjectBlueprint.md` exists
5. `backups/` directory exists
6. Infrastructure table has 8 entries
7. Schema versions are correct

**Returns**:
```python
@dataclass(frozen=True)
class ValidationResult:
    success: bool
    valid: bool = False
    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    checked_components: Optional[Dict] = None  # {directories: bool, project_db: bool, ...}
    error: Optional[str] = None
```

**No return statements** (validation utility)

---

### 11. `get_files_by_flow_context` (query.py) — target_database: `project`

**Called by**: `project_dependency_map` directive

**What it does**: Gets all files for a flow with functions embedded in each file.

**Parameters**: `project_root: str`, `flow_id: int`

**Logic**:
1. Query `file_flows` for flow_id → get file_ids
2. Query `files` for those file_ids
3. For each file: query `functions` WHERE file_id = file.id
4. Embed functions array in each file dict

**Returns**: `QueryResult` with file dicts containing embedded `functions` arrays.

**No return statements** (data retrieval)

---

## Implementation Order

Based on dependency chain:

1. **`validate_initialization`** — No dependencies, needed by aifp_init and aifp_status
2. **`get_project_status`** — No orchestrator dependencies, queries project.db directly (now includes tree logic)
3. **`get_files_by_flow_context`** — No orchestrator dependencies, queries project.db directly
4. **`get_task_context`** — No orchestrator dependencies, queries project.db directly
5. **`get_current_progress`** — No orchestrator dependencies, routes to table queries
6. **`query_project_state`** — No orchestrator dependencies, flexible query interface
7. **`update_project_state`** — No orchestrator dependencies, state transition updates
8. **`batch_update_progress`** — Depends on `update_project_state`
9. **`aifp_init`** — Depends on `validate_initialization`
10. **`aifp_status`** — Depends on `validate_initialization`, `get_project_status`
11. **`aifp_run`** — Depends on `aifp_status` + helpers from other modules

---

## Prerequisites Before Coding

### 1. ✅ Update orchestrator JSON (`docs/helpers/json/helpers-orchestrators.json`)
- ✅ Remove `get_status_tree` entry entirely
- ✅ Remove `get_project_context` entry entirely
- ✅ Update `aifp_status` to remove `get_status_tree` from implementation_notes
- ✅ Change `target_database` values per classification table above
- ✅ Update metadata count to 11
- ✅ Fill in implementation_notes and return_statements
- ✅ Added project_root parameter to helpers missing it
- ✅ Updated file_path values to match planned file organization

### 2. ✅ Update aifp_core.sql schema
- ✅ Changed CHECK constraint: `'orchestrator'` → `'multi_db'`, `'system'` → `'no_db'`
- File: `src/aifp/database/schemas/aifp_core.sql` lines 137-144

### 3. ✅ Update validation.py
- ✅ Changed validation tuple: `'orchestrator'` → `'multi_db'`, `'system'` → `'no_db'`
- File: `src/aifp/helpers/core/validation.py` line 77

### 4. ✅ Update HELPER_IMPLEMENTATION_PLAN.md
- ✅ Removed `get_status_tree` and `get_project_context` from Phase 2 orchestrators checklist
- ✅ Updated orchestrator count from 13 to 11
- ✅ Updated total helper count from 223 to 221
- ✅ Updated progress percentages

### 5. ✅ Update directive MD files
- ✅ `src/aifp/reference/directives/aifp_status.md` — replaced `get_status_tree` and `get_project_context` with `get_project_status`
- ✅ `src/aifp/reference/directives/aifp_run.md` — removed `get_project_context` from available_helpers, replaced with `get_project_status`

### 6. ✅ Update README.md
- ✅ Removed `get_project_context` from available_helpers list

### 7. ✅ Create `ProjectBlueprint_template.md`
- ✅ Created at `src/aifp/templates/ProjectBlueprint_template.md`
- ✅ All 9 sections match production blueprint structure
- ✅ HTML comment block explains this is a template requiring AI population
- ✅ All placeholder values marked with [BRACKETS]
- Used by `aifp_init` step 5 (copy to `.aifp-project/ProjectBlueprint.md`)

### 8. ✅ Create `_common.py` for orchestrators module
- ✅ Created at `src/aifp/helpers/orchestrators/_common.py`
- ✅ Shared imports, constants, connection helpers, lookup tables
- ✅ All orchestrator files import from _common only (DRY hierarchy)

### 9. ✅ Verify git helpers target_database
- ✅ Checked `docs/helpers/json/helpers-git.json` — all entries use `"project"`, no `"system"` values found

---

## Updated Helper Counts

**Before decisions**: 13 orchestrator helpers (12 in JSON + validate_initialization in code)
**After decisions**: 11 orchestrator helpers

**Total project helper count**: 223 → 221 (removed get_status_tree, get_project_context)
**Already implemented**: 210 (user_directives 19 + global 1 from this session)
**Remaining**: 11 orchestrators

---

## Notes

- `aifp_init` is the most complex helper. It does file I/O, schema execution, and multi-database setup. Must be atomic with rollback.
- `aifp_run` and `aifp_status` call helpers from other modules (core, project, user_preferences). They import from sibling packages.
- Return statements on entry_points are critical — they drive AI's next actions after calling these helpers.
- `get_current_progress`, `update_project_state`, `batch_update_progress`, `query_project_state` have no `used_by_directives` — they're generic AI tools. Still worth implementing as they simplify common operations.
- The `orchestrator` value in `user_directive_implement.md` (function_type field) is UNRELATED to the `target_database` rename. That refers to a user directive's main orchestrator function type (`trigger`/`action`/`condition`/`orchestrator`). No change needed there.
- `get_project_status` is used both by `aifp_status` (broad session init) and directly by AI in-session for more targeted status checks. Different use cases justify keeping both.
