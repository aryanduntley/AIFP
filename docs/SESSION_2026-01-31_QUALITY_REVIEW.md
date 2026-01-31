# Session Summary: Quality Review & State Database Implementation

**Date**: 2026-01-31
**Scope**: Quality review of recent implementations + state database architecture

---

## Overview

This session started as a quality review of the DIRECTIVE_ADDITIONS and WATCHDOG implementation plans, then expanded into state database design and MCP server architecture corrections.

---

## 1. Quality Review Findings & Fixes

### 1.1 Connection Leaks in Delete Functions

**Files**: `src/aifp/helpers/project/functions_2.py`, `src/aifp/helpers/project/types_1.py`

**Problem**: `delete_function` and `delete_type` had `conn.close()` inside the `try` block on the happy path, with `finally: pass`. If an exception occurred between `_create_deletion_note` and `conn.close()`, the connection would leak.

**Fix**: Moved `conn.close()` into `finally` block, matching the pattern already used correctly in `delete_interaction` in `interactions.py`.

### 1.2 sys.path.insert Fragility

**Files**: `functions_2.py`, `types_1.py`, `interactions.py`

**Problem**: Three files used `sys.path.insert(0, ...)` to import from parent directories — fragile and inconsistent with `_common.py` which uses proper relative imports.

**Fix**: Converted to relative imports:
```python
# Before
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_return_statements

# After
from ..utils import get_return_statements
```

**Note**: 22 other files in `helpers/` have the same `sys.path.insert` pattern. Broader cleanup is a separate effort.

### 1.3 Python Builtin Shadowing in Interactions

**Files**: `src/aifp/helpers/project/interactions.py`, `docs/helpers/json/helpers-project-4.json`

**Problem**: `add_interaction` used `type` as a parameter name, `update_interaction` and `delete_interaction` used `id` — both shadow Python builtins.

**Fix**: Renamed in both Python code and JSON helper definitions:
- `type` → `interaction_type` (in `add_interaction`)
- `id` → `interaction_id` (in `update_interaction` and `delete_interaction`)

---

## 2. State Database Architecture

### 2.1 Decision: Two Separate State Databases

There are two distinct state database concerns:

1. **Per-project state DB** (`<source-dir>/.state/runtime.db`) — Created during `project_discovery` for user projects that need FP-compliant mutable state. AI creates it via helper, then writes language-appropriate `state_operations` file for the project to use. The MCP server never connects to this.

2. **MCP server state DB** (`src/aifp/database/mcp_runtime.db`) — The MCP server's own global mutable state. Lives alongside `aifp_core.db`. All MCP server code can import operations from `aifp.database.state_operations`.

Both use the same schema (variables key-value table with type tracking).

### 2.2 Per-Project State Database

**Decision**: State DB creation is a helper (not internal to init), called during `project_discovery` when `source_directory` is confirmed. Init doesn't know the source directory yet — discovery is where infrastructure gets mapped.

**Files created**:
- `src/aifp/database/initialization/state_db.sql` — SQL schema (variables table, update trigger, schema_version)
- `src/aifp/helpers/project/state_db.py` — `create_state_database(source_directory)` helper

**Files modified**:
- `src/aifp/reference/directives/project_discovery.md` — Added steps 5-6 to Branch 3 (Map Infrastructure)
- `docs/directives-json/directives-project.json` — Added state DB steps to `map_infrastructure` branch
- `docs/helpers/json/helpers-project-9.json` — Added `create_state_database` helper definition (#113)

**Files deleted**:
- `src/aifp/templates/state_db/runtime.db` — Binary SQLite DB removed from templates. Databases are created from SQL at runtime, not shipped as binaries.

**How it works**:
1. During `project_discovery` Branch 3 (Map Infrastructure), once `source_directory` is confirmed
2. AI calls `create_state_database(source_directory)`
3. Helper creates `<source-dir>/.state/` directory and `runtime.db` from SQL schema
4. Return statement tells AI to create language-appropriate `state_operations` file using template at `src/aifp/templates/state_db/state_operations.py`
5. Database sits idle unless/until AI determines the project needs mutable global state

**Key principle**: The helper only creates. It doesn't manage, connect, or operate on the database. The `state_operations` template file is what AI adapts for the project's language to provide CRUD access.

### 2.3 MCP Server State Database

**Decision**: `mcp_runtime.db` already had connection infrastructure (`_open_mcp_runtime_connection`, `get_mcp_runtime_db_path`) but no schema or operations. Applied the same schema and created a state operations module.

**Files created**:
- `src/aifp/database/mcp_runtime.db` — Empty database with state_db.sql schema applied
- `src/aifp/database/state_operations.py` — `set_var`, `get_var`, `delete_var`, `increment_var`, `list_vars`

**Usage**: Any MCP server code can import:
```python
from aifp.database.state_operations import set_var, get_var, delete_var
```

**No separate SQL schema file needed** for this database. It was created once with the schema applied directly. During dev, SQL can be used directly against it.

### 2.4 What Was Removed from connection.py

**Decision**: The MCP server has no business connecting to per-project state databases. That's the user project's concern.

**Removed from `connection.py`**:
- `STATE_DIR_NAME` constant
- `STATE_DB_NAME` constant
- `get_state_db_path(source_directory)` function
- `get_state_dir(source_directory)` function
- `_open_state_connection(source_directory)` function
- `runtime.db` line from module docstring

**Removed from `helpers/utils.py`**: Corresponding re-exports and `__all__` entries.

The `state_db.py` helper computes these paths internally — it doesn't need them in the global connection layer.

### 2.5 Updated Orchestrator References

**File**: `docs/helpers/json/helpers-orchestrators.json`

- Updated `aifp_init` return statement: now references `create_state_database()` helper instead of "templates/state_db/ files"
- Updated implementation note: now lists correct locations (SQL schema, template, helper) instead of stale reference to `templates/state_db/runtime.db`

---

## 3. Global Database Access Summary (Post-Changes)

### Connection Layer (`aifp.database.connection`)

| Function | Database | Scope |
|----------|----------|-------|
| `_open_core_connection()` | aifp_core.db | Global, read-only |
| `_open_project_connection(project_root)` | project.db | Per-project, mutable |
| `_open_preferences_connection(project_root)` | user_preferences.db | Per-project, mutable |
| `_open_directives_connection(project_root)` | user_directives.db | Per-project, optional |
| `_open_mcp_runtime_connection()` | mcp_runtime.db | Global, mutable |

### State Operations (`aifp.database.state_operations`)

| Function | Purpose |
|----------|---------|
| `set_var(name, value, type)` | Store variable |
| `get_var(name)` | Retrieve variable |
| `delete_var(name)` | Delete variable |
| `increment_var(name, amount)` | Increment numeric variable |
| `list_vars(type)` | List all variables |

All operate on `mcp_runtime.db`. Globally importable by all MCP server code.

### Per-Project State (NOT in MCP server)

Created by `create_state_database()` helper during `project_discovery`. AI writes language-specific `state_operations` file for the project. MCP server never connects to it.

---

## 4. Complete File Change List

### New Files
- `src/aifp/database/initialization/state_db.sql` — State DB schema
- `src/aifp/database/state_operations.py` — MCP server state variable operations
- `src/aifp/database/mcp_runtime.db` — MCP server state database (with schema)
- `src/aifp/helpers/project/state_db.py` — `create_state_database` helper

### Deleted Files
- `src/aifp/templates/state_db/runtime.db` — Binary template removed

### Modified Files
- `src/aifp/database/connection.py` — Removed project state DB code, updated docstring
- `src/aifp/helpers/utils.py` — Removed state DB re-exports
- `src/aifp/helpers/project/functions_2.py` — Connection leak fix, relative imports
- `src/aifp/helpers/project/types_1.py` — Connection leak fix, relative imports
- `src/aifp/helpers/project/interactions.py` — Relative imports, builtin shadowing fix
- `src/aifp/reference/directives/project_discovery.md` — State DB creation steps
- `src/aifp/templates/state_db/README.md` — Updated to reflect new structure
- `docs/directives-json/directives-project.json` — State DB steps in map_infrastructure
- `docs/helpers/json/helpers-project-4.json` — Renamed interaction params
- `docs/helpers/json/helpers-project-9.json` — Added create_state_database helper
- `docs/helpers/json/helpers-orchestrators.json` — Updated stale state DB references

---

## 5. Key Decisions Log

| Decision | Rationale |
|----------|-----------|
| State DB creation is a helper, not internal to init | Init doesn't know source_directory yet — discovery is where it's confirmed |
| State DB creation lives in project_discovery Branch 3 | Infrastructure mapping is the natural point where source_directory is confirmed |
| MCP server does NOT connect to project state DBs | Separation of concerns — project state is the project's business |
| No SQL schema file for mcp_runtime.db | One-time creation, dev can use SQL directly |
| Binary runtime.db removed from templates | Databases should be created from SQL at runtime, not shipped as binaries |
| state_operations.py template stays as template | Language-dependent — AI adapts it per project |
| mcp_runtime.db uses same schema as project state DBs | Same key-value variable store pattern works for both |

---

*Generated at end of session 2026-01-31*
