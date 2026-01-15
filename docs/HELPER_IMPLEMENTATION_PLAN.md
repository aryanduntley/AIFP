# AIFP Helper Functions - Complete Implementation Plan

**Total Helpers**: 218 across 15 JSON files
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

7. **No Hidden State**
   - ALL parameters explicit in function signature
   - NO module-level variables (except constants)
   - NO closure over mutable state
   - Configuration passed as parameters

8. **Composition Over Abstraction**
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

❌ **Hidden dependencies:**
```python
# BAD - global connection
conn = sqlite3.connect(DB_PATH)

def get_file(file_id):
    return conn.execute(...)  # uses global
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
│   ├── directives_2.py (10 helpers)
│   └── flows.py (6 helpers)
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
│   ├── crud.py (8 helpers)
│   └── management.py (9 helpers)
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
- [ ] **global/database_info.py** - `helpers-index.json`
  - [ ] get_databases

#### Core Database Operations (38 helpers)
- [ ] **core/validation.py** - `helpers-core.json`
  - [ ] core_allowed_check_constraints

- [ ] **core/schema.py** - `helpers-core.json`
  - [ ] get_core_tables
  - [ ] get_core_fields
  - [ ] get_core_schema
  - [ ] get_from_core
  - [ ] get_from_core_where
  - [ ] query_core

- [ ] **core/directives_1.py** - `helpers-core.json`
  - [ ] get_directive_by_name
  - [ ] get_all_directives
  - [ ] search_directives
  - [ ] find_directive_by_intent
  - [ ] find_directives_by_intent_keyword
  - [ ] get_directives_with_intent_keywords
  - [ ] add_directive_intent_keyword
  - [ ] remove_directive_intent_keyword
  - [ ] get_directive_keywords
  - [ ] get_all_directive_keywords
  - [ ] get_all_intent_keywords_with_counts
  - [ ] get_directives_by_category
  - [ ] get_directives_by_type
  - [ ] get_fp_directive_index
  - [ ] get_all_directive_names

- [ ] **core/directives_2.py** - `helpers-core.json`
  - [ ] get_helper_by_name
  - [ ] get_helpers_by_database
  - [ ] get_helpers_are_tool
  - [ ] get_helpers_not_tool_not_sub
  - [ ] get_helpers_are_sub
  - [ ] get_helpers_for_directive
  - [ ] get_directives_for_helper
  - [ ] get_category_by_name
  - [ ] get_categories
  - [ ] get_directive_flows

- [ ] **core/flows.py** - `helpers-core.json`
  - [ ] get_next_directives_from_status
  - [ ] get_matching_next_directives
  - [ ] get_completion_loop_target
  - [ ] get_conditional_work_paths
  - [ ] search_fp_references
  - [ ] get_contextual_utilities

---

### Phase 2: Orchestrators (12 helpers)

- [ ] **orchestrators/entry_points.py** - `helpers-orchestrators.json`
  - [ ] aifp_run
  - [ ] aifp_status

- [ ] **orchestrators/status.py** - `helpers-orchestrators.json`
  - [ ] get_project_status (sub-helper)
  - [ ] get_status_tree (sub-helper)
  - [ ] get_work_context

- [ ] **orchestrators/state.py** - `helpers-orchestrators.json`
  - [ ] get_current_progress
  - [ ] update_project_state
  - [ ] batch_update_progress

- [ ] **orchestrators/query.py** - `helpers-orchestrators.json`
  - [ ] query_project_state
  - [ ] validate_initialization
  - [ ] get_project_context
  - [ ] get_files_by_flow_context

---

### Phase 3: Project Database (114 helpers)

#### Schema, CRUD, & Metadata (17 helpers)
- [ ] **project/validation.py** - `helpers-project-1.json` (1 helper)
  - [ ] project_allowed_check_constraints

- [ ] **project/schema.py** - `helpers-project-1.json` (4 helpers)
  - [ ] get_project_tables
  - [ ] get_project_fields
  - [ ] get_project_schema
  - [ ] get_project_json_parameters

- [ ] **project/crud.py** - `helpers-project-1.json` (7 helpers)
  - [ ] get_from_project
  - [ ] get_from_project_where
  - [ ] query_project
  - [ ] add_project_entry
  - [ ] update_project_entry
  - [ ] delete_project_entry
  - [ ] delete_reserved

- [ ] **project/metadata.py** - `helpers-project-1.json` (5 helpers)
  - [ ] create_project
  - [ ] get_project
  - [ ] update_project
  - [ ] blueprint_has_changed
  - [ ] get_infrastructure_by_type

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
- [ ] **project/tasks.py** - `helpers-project-7.json` (15 helpers)
  - [ ] add_milestone
  - [ ] get_milestones_by_path
  - [ ] get_milestones_by_status
  - [ ] get_incomplete_milestones
  - [ ] update_milestone
  - [ ] delete_milestone
  - [ ] add_task
  - [ ] get_incomplete_tasks_by_milestone
  - [ ] get_incomplete_tasks
  - [ ] get_tasks_by_milestone
  - [ ] get_tasks_comprehensive
  - [ ] get_task_flows
  - [ ] get_task_files
  - [ ] update_task
  - [ ] delete_task

#### Subtasks & Sidequests (14 helpers)
- [ ] **project/subtasks_sidequests.py** - `helpers-project-8.json` (14 helpers)
  - [ ] add_subtask
  - [ ] get_incomplete_subtasks
  - [ ] get_incomplete_subtasks_by_task
  - [ ] get_subtasks_by_task
  - [ ] get_subtasks_comprehensive
  - [ ] update_subtask
  - [ ] delete_subtask
  - [ ] add_sidequest
  - [ ] get_incomplete_sidequests
  - [ ] get_sidequests_comprehensive
  - [ ] get_sidequest_flows
  - [ ] get_sidequest_files
  - [ ] update_sidequest
  - [ ] delete_sidequest

#### Items & Notes (10 helpers)
- [ ] **project/items_notes.py** - `helpers-project-9.json` (10 helpers)
  - [ ] get_items_for_task
  - [ ] get_items_for_subtask
  - [ ] get_items_for_sidequest
  - [ ] get_incomplete_items
  - [ ] delete_item
  - [ ] add_note
  - [ ] get_notes_comprehensive
  - [ ] search_notes
  - [ ] update_note
  - [ ] delete_note

---

### Phase 4: Git Operations (11 helpers)

- [ ] **git/operations.py** - `helpers-git.json`
  - [ ] get_current_commit_hash
  - [ ] get_current_branch
  - [ ] get_git_status
  - [ ] detect_external_changes
  - [ ] create_user_branch
  - [ ] get_user_name_for_branch (sub-helper)
  - [ ] list_active_branches
  - [ ] detect_conflicts_before_merge
  - [ ] merge_with_fp_intelligence
  - [ ] sync_git_state
  - [ ] project_update_git_status (sub-helper)

---

### Phase 5: User Preferences (22 helpers)

- [ ] **user_preferences/validation.py** - `helpers-settings.json` (1 helper)
  - [ ] user_preferences_allowed_check_constraints

- [ ] **user_preferences/schema.py** - `helpers-settings.json` (4 helpers)
  - [ ] get_settings_tables
  - [ ] get_settings_fields
  - [ ] get_settings_schema
  - [ ] get_settings_json_parameters

- [ ] **user_preferences/crud.py** - `helpers-settings.json` (8 helpers)
  - [ ] get_from_settings
  - [ ] get_from_settings_where
  - [ ] query_settings
  - [ ] add_settings_entry
  - [ ] update_settings_entry
  - [ ] delete_settings_entry
  - [ ] get_all_tracking_features
  - [ ] get_tracking_status

- [ ] **user_preferences/management.py** - `helpers-settings.json` (9 helpers)
  - [ ] get_user_settings
  - [ ] update_user_setting
  - [ ] get_directive_preferences
  - [ ] update_directive_preference
  - [ ] get_tracking_settings
  - [ ] update_tracking_setting
  - [ ] add_tracking_note
  - [ ] get_tracking_notes
  - [ ] search_tracking_notes

---

### Phase 6: User Directives (20 helpers)

- [ ] **user_directives/validation.py** - `helpers-user-custom.json` (1 helper)
  - [ ] user_directives_allowed_check_constraints

- [ ] **user_directives/schema.py** - `helpers-user-custom.json` (4 helpers)
  - [ ] get_user_custom_tables
  - [ ] get_user_custom_fields
  - [ ] get_user_custom_schema
  - [ ] get_user_custom_json_parameters

- [ ] **user_directives/crud.py** - `helpers-user-custom.json` (8 helpers)
  - [ ] get_from_user_custom
  - [ ] get_from_user_custom_where
  - [ ] query_user_custom
  - [ ] add_user_custom_entry
  - [ ] update_user_custom_entry
  - [ ] delete_user_custom_entry
  - [ ] get_active_user_directives
  - [ ] search_user_directives

- [ ] **user_directives/management.py** - `helpers-user-custom.json` (7 helpers)
  - [ ] get_user_directive_by_name
  - [ ] validate_user_directive
  - [ ] activate_user_directive
  - [ ] deactivate_user_directive
  - [ ] add_user_directive_note
  - [ ] get_user_directive_notes
  - [ ] search_user_directive_notes

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

**Current Status**: Phase 3 in progress - 58 of 218 helpers completed (26.6%)

**Completed Modules** (9 of 32 files):
- ✅ `project/files_1.py` - 6 helpers
- ✅ `project/files_2.py` - 4 helpers
- ✅ `project/functions_1.py` - 5 helpers
- ✅ `project/functions_2.py` - 5 helpers
- ✅ `project/types_1.py` - 6 helpers
- ✅ `project/types_2.py` - 3 helpers
- ✅ `project/interactions.py` - 4 helpers
- ✅ `project/themes_flows_1.py` - 11 helpers
- ✅ `project/themes_flows_2.py` - 14 helpers

**Completed Milestones**:
- ✅ Files module (10 helpers)
- ✅ Functions module (10 helpers)
- ✅ Types & Interactions module (13 helpers)
- ✅ Themes & Flows module (25 helpers)

**Next Up**:
- ⏳ `project/tasks.py` - 15 helpers (task management)
- ⏳ `project/subtasks_sidequests.py` - 14 helpers (subtasks and sidequests)

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
- Core: 38 helpers
- Orchestrators: 12 helpers
- Project: 114 helpers
- Git: 11 helpers
- User Preferences: 22 helpers
- User Directives: 20 helpers

**TOTAL: 218 helpers**

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
**Last Updated**: 2026-01-15
**Status**: Phase 3 in progress - 58/218 helpers complete (26.6%)
**Next**: Implement `src/aifp/helpers/project/tasks.py` (15 helpers)
