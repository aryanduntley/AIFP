# AIFP Helper Functions - Complete Implementation Plan

**Total Helpers**: 220 across 15 JSON files (updated 2026-01-28: removed get_status_tree, get_project_context from orchestrators)
**Target**: 600-900 lines per Python file (prefer ~600)
**Estimated**: ~30-50 lines per helper → ~12-20 helpers per file

---

## 🚨 CRITICAL: Functional Programming Requirements 🚨

**ALL helper functions MUST be strictly coded in pure functional programming (FP) style.**

### Non-Negotiable FP Rules

1. **Pure Functions Only**
   - Same inputs → Same outputs (deterministic)
   - NO side effects in function logic
   - NO global state access or modification
   - NO hidden dependencies

2. **Immutable Data Structures**
   - Use `@dataclass(frozen=True)` for ALL data structures
   - NO mutable lists/dicts in return values (use tuples/frozensets)
   - NO in-place modifications
   - Create new instances instead of mutating

3. **Explicit Error Handling**
   - Use Result types: `Result[T, Error]`
   - NO try/except in pure logic
   - NO exceptions for control flow
   - Return errors as data

4. **NO Object-Oriented Programming**
   - NO classes (except frozen dataclasses for data)
   - NO inheritance
   - NO instance methods (static methods only)
   - NO stateful objects

5. **Database Operations as Effects**
   - Database reads/writes are effects (side effects)
   - Isolate in separate effect functions
   - Pure logic functions call effect functions
   - Effect functions clearly named (e.g., `_execute_query`, `_write_to_db`)

6. **Type Hints Required**
   - ALL parameters must have type hints
   - ALL return types must be specified
   - Use `Optional[T]`, `List[T]`, `Dict[K, V]`, etc.
   - Use type aliases for complex types

7. **Global Constants - Extensive Use Encouraged**
   - ✅ **Read-only global constants ENCOURAGED** (use `Final` in Python, `const` in JS/TS)
   - Configuration: `DATABASE_URL`, `MAX_RETRIES`, `TIMEOUT`, `API_KEYS`
   - Lookup tables: `VALID_STATUSES = frozenset(['pending', 'completed'])`
   - Paths: `PROJECT_DB_DIR`, `STATE_DB_PATH`, `BACKUP_DIR`
   - Business rules: `MAX_CART_ITEMS`, `PAYMENT_TIMEOUT`, `RATE_LIMIT`
   - ❌ **Mutable global variables strongly discouraged** (cause race conditions, testing issues)

8. **Runtime State Management**
   - ⚠️ Avoid mutable global variables
   - ✅ **For runtime mutable state, use state database pattern:**
     - Create lightweight SQLite database (e.g., `state.db`, `runtime.db`)
     - Use for: sessions, rate limits, progress tracking, job queues, temp caches, metrics
     - State mutations isolated in effect functions (explicit, traceable)
     - Thread-safe (SQLite handles concurrent access)
     - Maintains FP compliance (all state access explicit via function parameters)
   - See `docs/GLOBAL_STATE_AND_DRY_UPDATES.md` for detailed pattern

9. **Explicit Parameters**
   - ALL parameters explicit in function signature
   - NO hidden dependencies
   - NO closure over mutable state
   - Configuration passed as parameters (or read from global constants)

10. **Composition Over Abstraction**
    - Small, focused functions
    - Compose complex behavior from simple functions
    - Function pipelines over method chains
    - Higher-order functions when appropriate

### Example: FP-Compliant Helper

```python
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

@dataclass(frozen=True)
class FileRecord:
    id: int
    name: str
    path: str
    language: str
    checksum: str
    is_reserved: bool

@dataclass(frozen=True)
class Result:
    success: bool
    data: Optional[FileRecord] = None
    error: Optional[str] = None

# Pure function - deterministic, no side effects
def validate_file_name(name: str, file_id: int) -> Result:
    """Validate file name contains _id_{file_id} pattern."""
    expected_pattern = f"_id_{file_id}"

    if expected_pattern not in name:
        return Result(
            success=False,
            error=f"File name must contain {expected_pattern}"
        )

    return Result(success=True)

# Effect function - performs database I/O
def _get_file_from_db(conn, file_id: int) -> Optional[FileRecord]:
    """Database effect - fetch file by ID."""
    cursor = conn.execute("SELECT * FROM files WHERE id=?", (file_id,))
    row = cursor.fetchone()

    if row is None:
        return None

    return FileRecord(
        id=row[0],
        name=row[1],
        path=row[2],
        language=row[3],
        checksum=row[4],
        is_reserved=bool(row[5])
    )

# Pure orchestration - combines pure logic with effects
def get_file_by_id(db_path: str, file_id: int) -> Result:
    """Get file by ID with validation."""
    # Effect: open connection
    conn = _open_connection(db_path)

    # Effect: query database
    file_record = _get_file_from_db(conn, file_id)

    # Effect: close connection
    conn.close()

    # Pure logic: process result
    if file_record is None:
        return Result(success=False, error="File not found")

    return Result(success=True, data=file_record)
```

### Anti-Patterns to AVOID

❌ **Mutable state:**
```python
# BAD - mutating list
results = []
for item in items:
    results.append(process(item))
```

✅ **Immutable alternative:**
```python
# GOOD - immutable tuple
results = tuple(process(item) for item in items)
```

❌ **Exceptions for control flow:**
```python
# BAD - using exceptions
try:
    result = db.query(...)
except NotFound:
    return {"error": "not found"}
```

✅ **Result types:**
```python
# GOOD - explicit Result type
result = query_db(...)
if not result.success:
    return Result(success=False, error="not found")
```

❌ **Mutable global state:**
```python
# BAD - mutable global variable
total_files = 0  # Mutable global

def count_file():
    global total_files
    total_files += 1  # Mutation
    return total_files
```

✅ **Read-only global constants (ENCOURAGED):**
```python
from typing import Final

# GOOD - read-only constants
MAX_RETRIES: Final[int] = 3
PROJECT_DB_PATH: Final[str] = ".aifp-project/project.db"

def retry_operation(operation, max_retries: int = MAX_RETRIES):
    # Uses constant - still deterministic
    for attempt in range(max_retries):
        if operation().success: return result
    return Err("Max retries exceeded")
```

✅ **State database for runtime mutable state:**
```python
from typing import Final
import sqlite3

STATE_DB_PATH: Final[str] = ".state/runtime.db"  # Read-only constant

def track_progress(job_id: str, progress: int) -> Result[None, str]:
    """Effect: Explicit state mutation via database."""
    conn = sqlite3.connect(STATE_DB_PATH)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO jobs VALUES (?, ?, CURRENT_TIMESTAMP)",
            (job_id, progress)
        )
        conn.commit()
        return Ok(None)
    except Exception as e:
        return Err(str(e))
    finally:
        conn.close()
```

✅ **Explicit parameters:**
```python
# GOOD - connection passed explicitly
def get_file(conn, file_id: int):
    return conn.execute(...)
```

### Why This Matters

- **Referential Transparency**: Functions can be replaced with their return values
- **Testability**: Pure functions are trivial to test (no mocks needed)
- **Parallelization**: Pure functions can run in parallel safely
- **Reasoning**: Code behavior is local and predictable
- **AIFP Philosophy**: FP is the foundation of the entire paradigm

**If you're not sure if your code is FP-compliant, it probably isn't. When in doubt, ask.**

---

## File Structure

All helpers will be implemented in `src/aifp/helpers/` with the following categorized structure:

```
src/aifp/helpers/
├── global/
│   └── database_info.py (1 helper)
├── core/
│   ├── validation.py (1 helper)
│   ├── schema.py (6 helpers)
│   ├── directives_1.py (15 helpers)
│   ├── directives_2.py (9 helpers)
│   └── flows.py (5 helpers)
├── orchestrators/
│   ├── entry_points.py (2 helpers)
│   ├── status.py (3 helpers)
│   ├── state.py (3 helpers)
│   └── query.py (4 helpers)
├── project/
│   ├── validation.py (1 helper)
│   ├── schema.py (4 helpers)
│   ├── crud.py (7 helpers)
│   ├── metadata.py (6 helpers)
│   ├── files_1.py (6 helpers)
│   ├── files_2.py (4 helpers)
│   ├── functions_1.py (5 helpers)
│   ├── functions_2.py (5 helpers)
│   ├── types_1.py (6 helpers)
│   ├── types_2.py (3 helpers)
│   ├── interactions.py (5 helpers)
│   ├── themes_flows_1.py (11 helpers)
│   ├── themes_flows_2.py (14 helpers)
│   ├── tasks.py (15 helpers)
│   ├── subtasks_sidequests.py (14 helpers)
│   └── items_notes.py (10 helpers)
├── git/
│   └── operations.py (11 helpers)
├── user_preferences/
│   ├── validation.py (1 helper)
│   ├── schema.py (4 helpers)
│   ├── crud.py (6 helpers)
│   └── management.py (12 helpers)
└── user_directives/
    ├── validation.py (1 helper)
    ├── schema.py (4 helpers)
    ├── crud.py (8 helpers)
    └── management.py (7 helpers)
```

**Total Files**: 32 Python files
**Average**: ~7 helpers per file

---

## Complete Implementation Checklist

### Phase 1: Global & Core (49 helpers)

#### Global Database Operations (1 helper)
- [x] **global/database_info.py** - `helpers-index.json`
  - [x] get_databases

#### Core Database Operations (38 helpers) ✅ COMPLETE
- [x] **core/validation.py** - `helpers-core.json` ✅
  - [x] core_allowed_check_constraints

- [x] **core/schema.py** - `helpers-core.json` ✅
  - [x] get_core_tables
  - [x] get_core_fields
  - [x] get_core_schema
  - [x] get_from_core
  - [x] get_from_core_where
  - [x] query_core

- [x] **core/directives_1.py** - `helpers-core.json` ✅
  - [x] get_directive_by_name
  - [x] get_all_directives
  - [x] search_directives
  - [x] find_directive_by_intent
  - [x] find_directives_by_intent_keyword
  - [x] get_directives_with_intent_keywords
  - [x] add_directive_intent_keyword
  - [x] remove_directive_intent_keyword
  - [x] get_directive_keywords
  - [x] get_all_directive_keywords
  - [x] get_all_intent_keywords_with_counts
  - [x] get_directives_by_category
  - [x] get_directives_by_type
  - [x] get_fp_directive_index
  - [x] get_all_directive_names

- [x] **core/directives_2.py** - `helpers-core.json` ✅
  - [x] get_helper_by_name
  - [x] get_helpers_by_database
  - [x] get_helpers_are_tool
  - [x] get_helpers_not_tool_not_sub
  - [x] get_helpers_are_sub
  - [x] get_helpers_for_directive
  - [x] get_directives_for_helper
  - [x] get_category_by_name
  - [x] get_categories

- [x] **core/flows.py** - `helpers-core.json` ✅ (refactored 2026-01-27)
  - [x] get_flows_from_directive (NEW - replaces get_next_directives_from_status)
  - [x] get_flows_to_directive (NEW)
  - [x] get_completion_loop_target
  - [x] get_directive_flows
  - [x] get_wildcard_flows (NEW - replaces search_fp_references + get_contextual_utilities)

---

### Phase 2: Orchestrators (10 helpers) ✅

- [x] **orchestrators/entry_points.py** - `helpers-orchestrators.json` ✅
  - [x] aifp_run
  - [x] aifp_init
  - [x] aifp_status

- [x] **orchestrators/status.py** - `helpers-orchestrators.json` ✅
  - [x] get_project_status (sub-helper, includes tree logic formerly in get_status_tree)
  - [x] get_task_context

- [x] **orchestrators/state.py** - `helpers-orchestrators.json` ✅
  - [x] get_current_progress
  - [x] update_project_state
  - [x] batch_update_progress

- [x] **orchestrators/query.py** - `helpers-orchestrators.json` ✅
  - [x] query_project_state
  - [x] get_files_by_flow_context

---

### Phase 3: Project Database (118 helpers)

#### Schema, CRUD, & Metadata (21 helpers)
- [x] **project/validation.py** - `helpers-project-1.json` (1 helper) ✅
  - [x] project_allowed_check_constraints

- [x] **project/schema.py** - `helpers-project-1.json` (4 helpers) ✅
  - [x] get_project_tables
  - [x] get_project_fields
  - [x] get_project_schema
  - [x] get_project_json_parameters

- [x] **project/crud.py** - `helpers-project-1.json` (7 helpers) ✅
  - [x] get_from_project
  - [x] get_from_project_where
  - [x] query_project
  - [x] add_project_entry
  - [x] update_project_entry
  - [x] delete_project_entry
  - [x] delete_reserved

- [x] **project/metadata.py** - `helpers-project-1.json` (22 total, 10 coded, 2 removed) ✅
  - [x] create_project
  - [x] get_project
  - [x] update_project
  - [x] blueprint_has_changed
  - [x] get_infrastructure_by_type
  - [x] get_all_infrastructure
  - [x] get_source_directory
  - [x] update_source_directory (now includes failsafe insert if not exists)
  - [x] get_project_root
  - [x] update_project_root (with failsafe insert if not exists)
  - ~~add_source_directory~~ (REMOVED - SQL creates entry, update_source_directory has failsafe)
  - ~~initialize_state_database~~ (REMOVED - now part of aifp_init implementation)

#### Files (10 helpers)
- [x] **project/files_1.py** - `helpers-project-2.json` (6 helpers) ✅
  - [x] reserve_file
  - [x] reserve_files
  - [x] finalize_file
  - [x] finalize_files
  - [x] get_file_by_name
  - [x] get_file_by_path

- [x] **project/files_2.py** - `helpers-project-2.json` (4 helpers) ✅
  - [x] update_file
  - [x] file_has_changed
  - [x] update_file_timestamp (sub-helper)
  - [x] delete_file

#### Functions (10 helpers)
- [x] **project/functions_1.py** - `helpers-project-3.json` (5 helpers) ✅
  - [x] reserve_function
  - [x] reserve_functions
  - [x] finalize_function
  - [x] finalize_functions
  - [x] get_function_by_name

- [x] **project/functions_2.py** - `helpers-project-3.json` (5 helpers) ✅
  - [x] get_functions_by_file
  - [x] update_function
  - [x] update_functions_for_file
  - [x] update_function_file_location
  - [x] delete_function

#### Types & Interactions (13 helpers)
- [x] **project/types_1.py** - `helpers-project-4.json` (6 helpers) ✅
  - [x] reserve_type
  - [x] reserve_types
  - [x] finalize_type
  - [x] finalize_types
  - [x] update_type
  - [x] delete_type

- [x] **project/types_2.py** - `helpers-project-4.json` (3 helpers) ✅
  - [x] add_types_functions
  - [x] update_type_function_role
  - [x] delete_type_function

- [x] **project/interactions.py** - `helpers-project-4.json` (4 helpers) ✅
  - [x] add_interaction
  - [x] add_interactions
  - [x] update_interaction
  - [x] delete_interaction

#### Themes & Flows (25 helpers)
- [x] **project/themes_flows_1.py** - `helpers-project-5.json` (11 helpers) ✅
  - [x] get_theme_by_name
  - [x] get_flow_by_name
  - [x] get_all_themes
  - [x] get_all_flows
  - [x] add_theme
  - [x] update_theme
  - [x] delete_theme
  - [x] add_flow
  - [x] get_file_ids_from_flows
  - [x] update_flow
  - [x] delete_flow

- [x] **project/themes_flows_2.py** - `helpers-project-6.json` (14 helpers) ✅
  - [x] get_flows_for_theme
  - [x] get_themes_for_flow
  - [x] get_files_by_flow
  - [x] get_flows_for_file
  - [x] add_completion_path
  - [x] get_all_completion_paths
  - [x] get_next_completion_path
  - [x] get_completion_paths_by_status
  - [x] get_incomplete_completion_paths
  - [x] update_completion_path
  - [x] delete_completion_path
  - [x] reorder_completion_path
  - [x] reorder_all_completion_paths
  - [x] swap_completion_paths_order

#### Tasks (15 helpers)
- [x] **project/tasks.py** - `helpers-project-7.json` (15 helpers) ✅
  - [x] add_milestone
  - [x] get_milestones_by_path
  - [x] get_milestones_by_status
  - [x] get_incomplete_milestones
  - [x] update_milestone
  - [x] delete_milestone
  - [x] add_task
  - [x] get_incomplete_tasks_by_milestone
  - [x] get_incomplete_tasks
  - [x] get_tasks_by_milestone
  - [x] get_tasks_comprehensive
  - [x] get_task_flows
  - [x] get_task_files
  - [x] update_task
  - [x] delete_task

#### Subtasks & Sidequests (14 helpers)
- [x] **project/subtasks_sidequests.py** - `helpers-project-8.json` (14 helpers) ✅
  - [x] add_subtask
  - [x] get_incomplete_subtasks
  - [x] get_incomplete_subtasks_by_task
  - [x] get_subtasks_by_task
  - [x] get_subtasks_comprehensive
  - [x] update_subtask
  - [x] delete_subtask
  - [x] add_sidequest
  - [x] get_incomplete_sidequests
  - [x] get_sidequests_comprehensive
  - [x] get_sidequest_flows
  - [x] get_sidequest_files
  - [x] update_sidequest
  - [x] delete_sidequest

#### Items & Notes (10 helpers)
- [x] **project/items_notes.py** - `helpers-project-9.json` (10 helpers) ✅
  - [x] get_items_for_task
  - [x] get_items_for_subtask
  - [x] get_items_for_sidequest
  - [x] get_incomplete_items
  - [x] delete_item
  - [x] add_note
  - [x] get_notes_comprehensive
  - [x] search_notes
  - [x] update_note
  - [x] delete_note

---

### Phase 4: Git Operations (11 helpers) ✅ COMPLETE

- [x] **git/operations.py** - `helpers-git.json` ✅
  - [x] get_current_commit_hash
  - [x] get_current_branch
  - [x] get_git_status
  - [x] detect_external_changes
  - [x] create_user_branch
  - [x] get_user_name_for_branch (sub-helper)
  - [x] list_active_branches
  - [x] detect_conflicts_before_merge
  - [x] execute_merge (renamed from merge_with_fp_intelligence)
  - [x] sync_git_state
  - [x] project_update_git_status (sub-helper)

---

### Phase 5: User Preferences (23 helpers) ✅ COMPLETE

- [x] **user_preferences/validation.py** - `helpers-settings.json` (1 helper) ✅
  - [x] user_preferences_allowed_check_constraints

- [x] **user_preferences/schema.py** - `helpers-settings.json` (4 helpers) ✅
  - [x] get_settings_tables
  - [x] get_settings_fields
  - [x] get_settings_schema
  - [x] get_settings_json_parameters

- [x] **user_preferences/crud.py** - `helpers-settings.json` (6 helpers) ✅
  - [x] get_from_settings
  - [x] get_from_settings_where
  - [x] query_settings
  - [x] add_settings_entry
  - [x] update_settings_entry
  - [x] delete_settings_entry

- [x] **user_preferences/management.py** - `helpers-settings.json` (12 helpers) ✅
  - [x] load_directive_preferences
  - [x] add_directive_preference
  - [x] update_directive_preference
  - [x] get_user_setting
  - [x] add_user_setting
  - [x] update_user_setting
  - [x] get_user_settings
  - [x] get_tracking_settings
  - [x] toggle_tracking_feature
  - [x] add_tracking_note
  - [x] get_tracking_notes
  - [x] search_tracking_notes

**Refactored 2026-01-27**:
- Removed: `apply_preferences_to_context` (redundant - load via `load_directive_preferences`, apply is AI work)
- Removed: `update_user_preferences` (confused orchestrator - AI coordinates CRUD directly)
- Added: `update_directive_preference` (update existing preference in directive_preferences)
- Added: `add_user_setting` (add new setting to user_settings)
- Added: `update_user_setting` (update existing setting in user_settings)

**Implemented 2026-01-27**: All 23 helpers across 4 files.

---

### Phase 6: User Directives (19 helpers) — Refactored 2026-01-28

> **Refactored:** Removed 6 orchestrator helpers that contained deep logic (parse_directive_file,
> validate_directive_config, generate_handler_code, deploy_background_service, get_user_directive_status,
> monitor_directive_execution). These operations are AI's responsibility guided by directive workflows.
> Replaced with 5 CRUD-oriented helpers. Removed validate_user_directive (AI handles validation
> via user_directive_validate directive workflow). See helpers-user-custom.json metadata.changes for details.

- [x] **user_directives/validation.py** - `helpers-user-custom.json` (1 helper)
  - [x] user_directives_allowed_check_constraints

- [x] **user_directives/schema.py** - `helpers-user-custom.json` (4 helpers)
  - [x] get_user_custom_tables
  - [x] get_user_custom_fields
  - [x] get_user_custom_schema
  - [x] get_user_custom_json_parameters

- [x] **user_directives/crud.py** - `helpers-user-custom.json` (8 helpers)
  - [x] get_from_user_custom
  - [x] get_from_user_custom_where
  - [x] query_user_custom
  - [x] add_user_custom_entry
  - [x] update_user_custom_entry
  - [x] delete_user_custom_entry
  - [x] get_active_user_directives
  - [x] search_user_directives

- [x] **user_directives/management.py** - `helpers-user-custom.json` (6 helpers)
  - [x] get_user_directive_by_name
  - [x] activate_user_directive
  - [x] deactivate_user_directive
  - [x] add_user_directive_note
  - [x] get_user_directive_notes
  - [x] search_user_directive_notes

---

## Implementation Priority Order

**Based on dependencies and immediate need:**

1. ✅ **START HERE: Project Files** (`project/files_1.py`, `project/files_2.py`)
   - Most fundamental operation (reserve/finalize pattern)
   - No dependencies on other helpers
   - Critical for all code generation directives

2. **Project Functions** (`project/functions_1.py`, `project/functions_2.py`)
   - Depends on: files (for file_id references, update_file_timestamp)
   - Same reserve/finalize pattern as files

3. **Project Types & Interactions** (`project/types_1.py`, `project/types_2.py`, `project/interactions.py`)
   - Depends on: files, functions
   - More complex relationships

4. **Project Schema & CRUD** (`project/validation.py`, `project/schema.py`, `project/crud.py`, `project/metadata.py`)
   - Generic operations used by many other helpers
   - Blueprint management

5. **Project Themes & Flows** (`project/themes_flows_1.py`, `project/themes_flows_2.py`)
   - Organizational structures
   - Completion path management

6. **Project Tasks** (`project/tasks.py`, `project/subtasks_sidequests.py`, `project/items_notes.py`)
   - Work hierarchy management
   - Depends on: completion paths

7. **Core Helpers** (all core/ files)
   - Directive and helper queries
   - Used by orchestrators

8. **Git Operations** (`git/operations.py`)
   - Version control integration
   - Used by various project directives

9. **User Preferences** (all user_preferences/ files)
   - Settings management
   - Used by preference directives

10. **User Directives** (all user_directives/ files)
    - Custom automation system
    - Use Case 2 only

11. **Orchestrators** (all orchestrators/ files) - **DO LAST**
    - Depends on ALL other helpers
    - Calls many helpers to aggregate data

12. **Global** (`global/database_info.py`)
    - Simple database metadata query
    - Minimal dependencies

---

## Implementation Guidelines

### Critical Workflow: Read JSON → Code → Update JSON

**BEFORE coding each helper:**

1. **Read the helper's JSON entry** in the corresponding file (e.g., `docs/helpers/json/helpers-project-2.json`)
2. **Check the `implementation_notes` field** - Contains critical guidance:
   - SQL queries to use
   - Return value formats
   - Error logic and validation rules
   - Expected behavior patterns
   - Edge cases to handle
3. **Check the `error_handling` field** - Specific error scenarios
4. **Check the `return_statements` field** - Expected return formats
5. **Check the `used_by_directives` field** - Context for how directives use this helper

**Example JSON entry to review:**
```json
{
  "name": "reserve_file",
  "file_path": "TODO_helpers/project/module.py",
  "parameters": [...],
  "purpose": "Reserve file ID for naming before creation",
  "implementation_notes": [
    "Returns {success: true, id: reserved_id, is_reserved: true}",
    "SQL: INSERT INTO files (name, path, language, is_reserved) VALUES (?, ?, ?, 1) RETURNING id",
    "Filename pattern: {name}_id_{id}.{extension} (e.g., calculator_id_42.py)"
  ],
  "error_handling": "Return error if path already exists",
  ...
}
```

**AFTER coding each helper (CRITICAL):**

Update the `file_path` field in the JSON file with the actual implementation path:

**Current format** (placeholder):
```json
"file_path": "TODO_helpers/project/module.py"
```

**New format** (relative to src/aifp):
```json
"file_path": "helpers/project/files_1.py"
```

**Example patterns**:
```json
"file_path": "helpers/orchestrators/entry_points.py"
"file_path": "helpers/core/validation.py"
"file_path": "helpers/project/functions_2.py"
```

**⚠️ IMPORTANT**: The `file_path` update serves as our completion tracker. **ONLY update the file_path AFTER the function is fully coded and tested.** We will use these field modifications to verify all 218 helpers have been implemented.

### Functional Programming Requirements

All helpers MUST be FP-compliant:
- ✅ Pure functions only (no side effects in logic)
- ✅ Immutable data structures (frozen dataclasses)
- ✅ Explicit error handling (Result types, not exceptions)
- ✅ No OOP (except frozen dataclasses for data)
- ✅ Database operations isolated in effect functions
- ✅ All parameters explicit (no hidden state)
- ✅ Type hints on all parameters and returns
- ✅ Deterministic (same inputs → same outputs)
- ✅ **DRY (Don't Repeat Yourself) - Extract common utilities to shared modules**

### Code Reusability and DRY Principle

**CRITICAL**: Helper files are NOT required to be self-contained. Extract common utilities at the **appropriate scope level**.

**Why DRY Matters at Scale**:
- At scale (hundreds/thousands of files), duplication causes massive overhead:
  - **Token generation**: Duplicating 50 lines × 1,000 files = 50,000 wasted lines
  - **Database bloat**: Same function stored 1,000 times with different file_ids
  - **Maintenance burden**: Logic change requires updating 1,000 files instead of 1
  - **Context window waste**: Every file carries boilerplate instead of unique logic
  - **Memory/cache overhead**: AI loads duplicated code repeatedly
- **Database provides context**: AI queries database for function metadata, not file contents
  - Database has function signatures, purposes, relationships
  - No need to read actual files for context
  - So no "readability penalty" from imports

**The Right DRY Philosophy**:

✅ **Extract when** (GOOD DRY):
- Code is **IDENTICAL** across 2+ files
- Function has **single responsibility**
- Use cases are **truly the same**
- No conditionals or parameters needed to handle variations

❌ **Don't extract when** (FORCED DRY - avoid this):
- Code is **similar but not identical**
- Would require adding parameters/conditionals to handle variations
- Use cases are **actually different** (even if they look similar)
- Would create "god functions" that try to do everything

**Examples**:
```python
# ✅ GOOD DRY - Extract this (identical everywhere)
def _open_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ❌ FORCED DRY - Don't do this (forced reuse with many parameters)
def update_entity(conn, table, entity_id, field_name, new_value,
                  validate=True, cascade=False, log_change=True, ...):
    # 200 lines of conditionals trying to handle every case
    # This becomes unmaintainable

# ✅ GOOD DRY - Make separate focused functions instead
def update_file(conn, file_id, name, path): ...
def update_function(conn, func_id, name, purpose): ...
def update_type(conn, type_id, name, variants): ...
```

**Scope Levels for Common Utilities**:

1. **Global Level** (`src/aifp/helpers/_common.py` or `src/aifp/_common.py`)
   - Utilities used across ALL helper categories (project, core, git, user_preferences, user_directives)
   - Examples: Database connection, generic Result types, validation utilities
   - Extract if used in multiple categories

2. **Category Level** (`src/aifp/helpers/project/_common.py`)
   - Utilities used across multiple files within ONE category
   - Examples: Category-specific entity checks, domain-specific query builders
   - Extract if used in 2+ files within same category

3. **File Level** (keep in the file)
   - Utilities used only in ONE file
   - Examples: File-specific data transformations, unique business logic
   - Keep local if truly file-specific

**Decision Rules**:
- Function appears in 2+ files AND is identical → **Extract immediately**
- Function is similar but needs variations → **Make separate functions** (don't force extraction)
- Function is truly generic and focused → **Extract proactively** to appropriate scope
- Function is domain-specific to one file → **Keep local**

**Directory Structure Example**:
```
src/aifp/
├── _common.py                    # GLOBAL utilities (all helpers use)
└── helpers/
    ├── _common.py                # Helpers-wide utilities (if needed)
    ├── project/
    │   ├── _common.py            # Project category utilities
    │   ├── files_1.py            # Imports from project/_common AND global
    │   ├── files_2.py
    │   └── ...
    ├── core/
    │   ├── _common.py            # Core category utilities
    │   └── ...
    └── user_preferences/
        ├── _common.py            # User preferences category utilities
        └── ...
```

**This is project-wide standard behavior** for all AIFP projects unless user explicitly overrides.
```

### Return Statements - AI Guidance System

**CRITICAL: All helper functions MUST return `return_statements` for successful operations.**

Return statements are forward-thinking guidance for the AI, providing next steps and context after a helper executes. They are stored in the `aifp_core.db` database and are subject to change, so they must NEVER be hardcoded into helper functions.

#### Return Statement Rules

1. **Success Only**: Return statements are ONLY included when `success=True`
   - If `error` is returned, DO NOT include return_statements
   - Return statements are for forward-thinking guidance, not error handling

2. **Database-Driven**: Return statements are stored in `helper_functions.return_statements` (JSON array)
   - Never hardcode return statements in helper code
   - Always fetch from core database at runtime
   - Allows return statements to evolve without code changes

3. **Global Helper Function**: Use `get_return_statements(helper_name)` to fetch
   - This function queries `aifp_core.db` for the helper's return_statements
   - Returns empty tuple if helper not found or no statements defined
   - Implemented as a global utility in `src/aifp/helpers/utils.py`

#### Implementation Pattern

```python
# Import from utils (path setup handled in each helper file)
from utils import get_return_statements

def some_helper(db_path: str, param: str) -> SomeResult:
    """Helper function that includes return statements."""

    # Perform operation
    result = _perform_operation(db_path, param)

    # If error, return WITHOUT return_statements
    if not result.success:
        return SomeResult(
            success=False,
            error=result.error
        )

    # Success - fetch return statements from core database
    return_statements = get_return_statements("some_helper")

    return SomeResult(
        success=True,
        data=result.data,
        return_statements=return_statements  # Add AI guidance
    )
```

#### Return Statement Examples

From `helpers-project-2.json`:
- `reserve_file`: `["Use returned ID for file naming: {name}_id_{id}.{ext}"]`
- `finalize_file`: `["Verify flows are added in file_flows table"]`
- `update_file`: `["Ensure name or path changes are updated throughout codebase", "If name changed, verify _id_xxx suffix is retained"]`

#### Data Structure Update

All Result dataclasses should include optional `return_statements` field:

```python
@dataclass(frozen=True)
class SomeResult:
    success: bool
    data: Optional[SomeData] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps
```

#### Global Utility Function Location

Create `src/aifp/helpers/utils.py` with:
```python
def get_return_statements(helper_name: str) -> Tuple[str, ...]:
    """
    Fetch return statements for a helper from core database.

    Args:
        helper_name: Name of the helper function

    Returns:
        Tuple of return statement strings (empty if not found)
    """
    # Query aifp_core.db for return_statements
    # Parse JSON array and return as tuple
```

### Implementation Notes

Each helper JSON entry includes critical guidance:
- **implementation_notes**: Detailed SQL, logic, return formats
- **error_handling**: Specific error scenarios and returns
- **return_statements**: Forward-thinking AI guidance (fetch from database, don't hardcode)
- **used_by_directives**: Context for usage patterns and dependencies

**Review these fields carefully during implementation.**

### Code Organization Per File

Each Python file should:
1. Import dependencies at top (frozen dataclasses, Result types, **shared utilities from _common.py**)
2. Define data structures (frozen dataclasses for return types)
3. Implement helpers in logical order
4. Include comprehensive docstrings
5. Handle errors with Result types
6. Keep files between 600-900 lines
7. **Extract common functions to `_common.py` - avoid duplication across files**

---

## Progress Tracking

**Current Status**: ALL HELPERS COMPLETE! - 220 of 220 helpers completed (100%)

**Completed Modules** (32 of 32 files):

**Core Database (5 files, 36 helpers)** ✅:
- ✅ `core/validation.py` - 1 helper
- ✅ `core/schema.py` - 6 helpers
- ✅ `core/directives_1.py` - 15 helpers
- ✅ `core/directives_2.py` - 9 helpers
- ✅ `core/flows.py` - 5 helpers (refactored: simple queries, no deep logic)

**Project Database (16 files, 119 helpers)** ✅:
- ✅ `project/validation.py` - 1 helper
- ✅ `project/schema.py` - 4 helpers
- ✅ `project/crud.py` - 7 helpers
- ✅ `project/metadata.py` - 10 helpers (2 removed: add_source_directory, initialize_state_database)
- ✅ `project/files_1.py` - 6 helpers
- ✅ `project/files_2.py` - 4 helpers
- ✅ `project/functions_1.py` - 5 helpers
- ✅ `project/functions_2.py` - 5 helpers
- ✅ `project/types_1.py` - 6 helpers
- ✅ `project/types_2.py` - 3 helpers
- ✅ `project/interactions.py` - 4 helpers
- ✅ `project/themes_flows_1.py` - 11 helpers
- ✅ `project/themes_flows_2.py` - 14 helpers
- ✅ `project/tasks.py` - 15 helpers
- ✅ `project/subtasks_sidequests.py` - 14 helpers
- ✅ `project/items_notes.py` - 10 helpers

**Git Operations (1 file, 11 helpers)** ✅:
- ✅ `git/operations.py` - 11 helpers

**User Preferences (3 files, 23 helpers)** ✅:
- ✅ `user_preferences/settings.py` - helpers
- ✅ `user_preferences/management.py` - helpers
- ✅ `user_preferences/tracking.py` - helpers

**User Directives (2 files, 20 helpers)** ✅:
- ✅ `user_directives/directives.py` - helpers
- ✅ `user_directives/management.py` - helpers

**Global (1 file, 1 helper)** ✅:
- ✅ `global/global_helpers.py` - 1 helper

**Orchestrators (4 files + _common.py, 10 helpers)** ✅:
- ✅ `orchestrators/_common.py` - shared constants, connection helpers, lookup tables
- ✅ `orchestrators/entry_points.py` - 3 helpers (aifp_run, aifp_init, aifp_status)
- ✅ `orchestrators/status.py` - 2 helpers (get_project_status, get_task_context)
- ✅ `orchestrators/state.py` - 3 helpers (get_current_progress, update_project_state, batch_update_progress)
- ✅ `orchestrators/query.py` - 2 helpers (query_project_state, get_files_by_flow_context)

**Completed Milestones**:
- ✅ **ALL CORE DATABASE HELPERS COMPLETE** (36 helpers after refactor)
- ✅ **ALL PROJECT DATABASE HELPERS COMPLETE** (119 coded; 2 removed: add_source_directory, initialize_state_database)
- ✅ **ALL GIT HELPERS COMPLETE** (11 helpers)
- ✅ **ALL USER PREFERENCES HELPERS COMPLETE** (23 helpers)
- ✅ **ALL USER DIRECTIVES HELPERS COMPLETE** (20 helpers)
- ✅ **ALL GLOBAL HELPERS COMPLETE** (1 helper)
- ✅ **ALL ORCHESTRATOR HELPERS COMPLETE** (10 helpers across 4 files + _common.py)

Use checkboxes above to track implementation progress as each helper is completed and tested.

**Estimated Effort**:
- 32 files × ~700 lines avg = ~22,400 lines of FP-compliant Python code
- ~218 helpers × 10-15 min avg = 36-55 hours of pure coding
- Plus testing, documentation, integration = ~100-120 hours total

---

## Quick Reference: Complete Helper List

For detailed helper specifications, see: `docs/COMPLETE_HELPERS_LIST.md`

**Summary by Category**:
- Global: 1 helper
- Core: 36 helpers (refactored 2026-01-27)
- Orchestrators: 10 helpers
- Project: 114 helpers
- Git: 11 helpers
- User Preferences: 23 helpers
- User Directives: 20 helpers

**TOTAL: 220 helpers**

---

## Next Steps

1. ✅ Implementation plan complete with all 218 helpers listed
2. ✅ Complete helper list generated in `COMPLETE_HELPERS_LIST.md`
3. ✅ **COMPLETED: Files module** (`project/files_1.py` and `project/files_2.py`)
4. ✅ **COMPLETED: Functions module** (`project/functions_1.py` and `project/functions_2.py`)
5. ✅ **COMPLETED: Types & Interactions** (`project/types_1.py`, `project/types_2.py`, `project/interactions.py`)
6. ✅ **COMPLETED: Themes & Flows Part 1** (`project/themes_flows_1.py` - 11 helpers)
7. ✅ **COMPLETED: Themes & Flows Part 2** (`project/themes_flows_2.py` - 14 helpers)
8. ⏳ Update JSON file_path fields as we progress (ongoing)
8. ⏳ Write comprehensive tests for each helper
9. ⏳ Integration testing with MCP server

---

**Generated**: 2026-01-11
**Last Updated**: 2026-01-28
**Status**: ALL COMPLETE! - 220/220 helpers (100%)
**Next**: Testing, integration, MCP tool registration

---

## Recent Updates (2026-01-28)

### Orchestrators Complete (10 helpers) — ALL 220 HELPERS DONE

**Implemented Files**:
- `orchestrators/_common.py` — Shared constants, connection helpers, lookup tables (ACTION_STATUS_MAP, JOIN_MAPPINGS, VALID_QUERY_ENTITIES, etc.)
- `orchestrators/entry_points.py` — 3 helpers: `aifp_init`, `aifp_status`, `aifp_run`
- `orchestrators/status.py` — 2 helpers: `get_project_status` (with tree), `get_task_context`
- `orchestrators/state.py` — 3 helpers: `get_current_progress`, `update_project_state`, `batch_update_progress`
- `orchestrators/query.py` — 2 helpers: `query_project_state`, `get_files_by_flow_context` (validate_initialization removed — AI responsibility)

**Prerequisites completed before coding**:
1. ✅ Updated `helpers-orchestrators.json` — removed `get_status_tree` + `get_project_context`, fixed `target_database` values (`multi_db` for cross-DB, `project` for single-DB)
2. ✅ Updated `aifp_core.sql` CHECK constraint — `orchestrator` → `multi_db`, `system` → `no_db`
3. ✅ Updated `validation.py` tuple to match
4. ✅ Updated this plan — counts, checklists
5. ✅ Updated directive MDs — `aifp_status.md`, `aifp_run.md`
6. ✅ Updated `README.md` — removed `get_project_context` from available_helpers
7. ✅ Created `ProjectBlueprint_template.md` — used by `aifp_init` step 5
8. ✅ Verified git helpers — all `"project"`, no `"system"` values
9. ✅ Created `__init__.py` for orchestrators package

**Design decisions**:
- `get_status_tree` folded into `get_project_status` (single-pass flat counts + nested tree)
- `get_project_context` removed (redundant with `get_from_project`, `get_all_infrastructure`, `get_project_status`)
- `aifp_run` discovers project_root by walking up from cwd looking for `.aifp-project/`
- `aifp_init` does full shutil.rmtree cleanup if any step fails past directory creation
- `query_project_state` sanitizes field names + parameterizes all values (SQL injection prevention)
- Cross-module calls in `entry_points.py` use `_safe` wrappers that return empty results on failure

**Progress**: 220/220 helpers — **100% COMPLETE**

---

## Recent Updates (2026-01-27)

### Git Operations Complete (11 helpers)

**Implemented**: `src/aifp/helpers/git/operations.py`

All 11 git helpers implemented:
- `get_current_commit_hash` - git rev-parse HEAD
- `get_current_branch` - git branch --show-current
- `get_git_status` - comprehensive status (branch, hash, files, ahead/behind)
- `detect_external_changes` - compare stored hash with current HEAD
- `create_user_branch` - aifp-{user}-{number} convention
- `get_user_name_for_branch` - detect from git config/env/system
- `list_active_branches` - query work_branches table
- `detect_conflicts_before_merge` - dry-run merge analysis
- `execute_merge` - execute merge, return result (renamed from merge_with_fp_intelligence)
- `sync_git_state` - update project.last_known_git_hash
- `project_update_git_status` - sub-helper for hash/timestamp update

**Design fixes applied**:
- Renamed `merge_with_fp_intelligence` to `execute_merge` (no auto-resolution)
- `detect_conflicts_before_merge` returns raw data (no confidence scores)
- All helpers follow principle: retrieve data, AI decides

**Progress**: 166/222 helpers (74.8%)

---

### Core Flows Refactored (38 → 36 helpers)

**Problem**: Flow helpers had embedded "deep logic" that evaluated conditions internally.
This violated the design principle: MCP server retrieves data, AI handles logic/decisions.

**Removed** (5 helpers with deep logic):
- `get_next_directives_from_status` - evaluated conditions internally
- `get_matching_next_directives` - filtered by evaluated conditions
- `get_conditional_work_paths` - evaluated conditions internally
- `search_fp_references` - specialized wildcard query
- `get_contextual_utilities` - specialized wildcard query

**Added** (3 simple query helpers):
- `get_flows_from_directive(from_directive)` - all flows originating from directive
- `get_flows_to_directive(to_directive)` - all flows leading to directive
- `get_wildcard_flows(flow_type?)` - flows from `*` (available from any context)

**Kept unchanged**:
- `get_completion_loop_target` - simple lookup (already clean)
- `get_directive_flows` - generic filter query (already clean)

**Impact**:
- Core helpers: 38 → 36
- Total helpers: 224 → 222
- Code reduced from 718 lines to 348 lines

**Files updated**:
- `docs/helpers/json/helpers-core.json` - JSON definitions
- `src/aifp/helpers/core/flows.py` - Implementation
- `docs/HELPER_IMPLEMENTATION_PLAN.md` - This file

---

### Core Database Helpers Complete (36 helpers)

**Implemented Files**:
- `core/_common.py` - Core-specific utilities, record types (DirectiveRecord, HelperRecord, FlowRecord, etc.)
- `core/validation.py` - 1 helper (CHECK constraint parsing)
- `core/schema.py` - 6 helpers (schema introspection, generic queries)
- `core/directives_1.py` - 15 helpers (directive queries, search, intent keywords)
- `core/directives_2.py` - 9 helpers (helper queries, category operations)
- `core/flows.py` - 7 helpers (flow navigation, wildcard handling)

**DRY Hierarchy Established**:
```
utils.py (global)                    <- Database-agnostic shared code
├── Database path resolution for all 4 databases
├── Generic connection management (_open_connection)
├── Return statements fetching
├── Schema introspection utilities
└── Row conversion utilities

{category}/_common.py                <- Category-specific shared code
├── project/_common.py               <- Project entity checks, validation constants
└── core/_common.py                  <- DirectiveRecord, HelperRecord, FlowRecord, etc.

{category}/{file}.py                 <- Individual helpers
└── Import from _common.py which re-exports from utils.py
```

**Global Utils Updated** (`src/aifp/helpers/utils.py`):
- Added `get_project_db_path(project_root)` - path to project.db
- Added `get_user_preferences_db_path(project_root)` - path to user_preferences.db
- Added `get_user_directives_db_path(project_root)` - path to user_directives.db
- Moved `_open_connection()` from project/_common.py to utils.py (DRY)
- Added schema introspection utilities for all database operations

**Flow Helpers Design Note**:
- `get_next_directives_from_status`, `get_matching_next_directives`, `get_conditional_work_paths` take optional `project_root` parameter
- AI passes project root (which it knows), helper constructs path and queries project.db internally
- Conditions evaluated against project status without AI needing to pass status objects
- If `project_root` not provided, conditions not evaluated (all flows returned)

**JSON Updated**:
- `docs/helpers/json/helpers-core.json` - All 38 `file_path` entries updated to actual paths

**Progress Impact**:
- Total: 224 helpers
- Coded: 157 helpers (Core: 38 + Project: 119)
- Percentage: 70.1% complete

---

## Recent Updates (2026-01-19)

### Project Root Helpers Added and add_source_directory Removed

**Changes**:
- ❌ Removed `add_source_directory` - Redundant since SQL creates entry and update has failsafe
- ✅ Added `get_project_root` - Get project root from infrastructure table
- ✅ Added `update_project_root` - Update project root (with failsafe insert if not exists)
- ✅ Updated `update_source_directory` - Added failsafe insert if entry doesn't exist
- ✅ Updated `aifp_init` implementation notes - Call update_project_root() after SQL to populate value

**Rationale**:
- Both `project_root` and `source_directory` need get/update helpers for symmetry
- Add functions are unnecessary - SQL creates entries, update functions have failsafe insert
- This provides safety while reducing API surface (fewer functions = clearer intent)

**Progress Impact**:
- Total: 224 helpers (was 223, -1 add_source_directory, +2 project_root helpers)
- Coded: 119 helpers (was 118, -1 add_source_directory, +2 project_root helpers)
- Percentage: 53.1% (was 52.9%)

---

### Infrastructure Helpers Verification and State DB Removal

**Verification Results**:
- ✅ `get_source_directory` - VERIFIED: Fully implemented (lines 700-737 in metadata.py)
- ✅ `add_source_directory` - VERIFIED: Fully implemented (lines 740-786 in metadata.py)
- ✅ `update_source_directory` - VERIFIED: Fully implemented (lines 789-837 in metadata.py)
- ✅ `get_all_infrastructure` - COMPLETED: Implemented (lines 662-698 in metadata.py)
- ❌ `initialize_state_database` - REMOVED: State DB initialization moved to aifp_init orchestrator

**State Database Helper Removal**:
- **Rationale**: State DB initialization is part of aifp_init's setup work, just like directory creation and database initialization. No separate helper needed.
- **Action**: Removed from helpers-project-1.json and moved to aifp_init's implementation_notes
- **Impact**: Total helper count reduced from 224 to 223

**Helper Count Correction**:
- 3 helpers were already coded but marked as pending (get_source_directory, add_source_directory, update_source_directory)
- 1 helper removed (initialize_state_database → now part of aifp_init)
- Net change: +3 coded, -1 total = 117 of 223 complete

**Progress Impact**:
- **FINAL**: 118 of 223 helpers complete (52.9%)
- **metadata.py**: 9 of 9 helpers coded (was incorrectly showing 5 of 10, then 8 of 9)
- **Schema, CRUD & Metadata module**: 21 of 21 helpers COMPLETE (was incorrectly showing 17 of 21)
- **Phase 3 (Project Database)**: 118 of 118 helpers COMPLETE! 🎉

---

## Recent Updates (2026-01-15)

### Methodology Updates

**Global State Management Clarified**:
- Read-only global constants now **extensively encouraged** (was "exception")
- Added state database pattern for runtime mutable state (FP-compliant)
- Updated FP rules #7-9 to reflect new patterns
- See `docs/GLOBAL_STATE_AND_DRY_UPDATES.md` for full details

**Documentation Updates**:
- System prompt condensed (34 lines = 5% reduction, ~850 tokens saved)
- Added MD file references for deeper FP pattern context
- Updated directive JSONs (`fp_state_elimination`, `fp_no_oop`) to match MD changes
- All three layers aligned: system prompt, directive MDs, directive JSONs

**Key Changes**:
- Rule #7: "No Hidden State" → "Global Constants - Extensive Use Encouraged"
- Rule #8: Added "Runtime State Management" (state database pattern)
- Rule #9: "Explicit Parameters" (clarified can use global constants)
- Anti-patterns: Added positive examples for constants and state database

**Implementation Impact**:
- Helpers can freely use `Final` constants for config, paths, business rules
- For runtime state (sessions, rate limits, job tracking), suggest state database pattern
- Extract common utilities aggressively (DRY principle already covered)

**Related Documentation**:
- `docs/GLOBAL_STATE_AND_DRY_UPDATES.md` - Comprehensive changes
- `docs/SYSTEM_PROMPT_CONDENSING.md` - Example optimization
- `docs/DIRECTIVE_JSON_UPDATES_2026-01-15.md` - JSON alignment
